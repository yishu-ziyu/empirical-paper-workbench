from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.agent_task_queue_service import (
    agent_task_queue_state_path,
    build_agent_task_queue_response,
    build_agent_task_queue_summary,
    dispatch_review_required_blocker,
    load_saved_agent_task_queue,
    normalize_agent_task_queue,
)
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


VALID_DISPATCH_REVIEW_ACTIONS = {"approve", "reject", "needs_revision"}


class AgentTaskDispatchReviewError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def review_project_agent_task_dispatch(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    task_id: str,
    action: str,
    note: str = "",
) -> dict[str, Any]:
    if action not in VALID_DISPATCH_REVIEW_ACTIONS:
        raise AgentTaskDispatchReviewError(
            "invalid_dispatch_review_action",
            f"Unsupported dispatch review action: {action}.",
        )
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = normalize_agent_task_queue(load_required_queue(project_root))
    task = find_agent_task(queue, task_id)
    timestamp = utc_now()
    require_internal_skill_execution_packet_before_dispatch(task, action)
    apply_dispatch_review(task, action, note, timestamp)
    queue["summary"] = build_agent_task_queue_summary(queue.get("tasks", []))
    queue["updated_at"] = timestamp
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    return build_agent_task_queue_response(project, queue)


def load_required_queue(project_root: Path) -> dict[str, Any]:
    queue = load_saved_agent_task_queue(project_root)
    if not queue:
        raise AgentTaskDispatchReviewError(
            "agent_task_queue_required",
            "Agent Task Queue must exist before dispatch review.",
        )
    return queue


def find_agent_task(queue: dict[str, Any], task_id: str) -> dict[str, Any]:
    for task in queue.get("tasks", []):
        if isinstance(task, dict) and task.get("id") == task_id:
            return task
    raise AgentTaskDispatchReviewError(
        "agent_task_not_found",
        f"Agent task {task_id} does not exist.",
    )


def require_internal_skill_execution_packet_before_dispatch(task: dict[str, Any], action: str) -> None:
    if action != "approve" or not has_internal_skill_binding(task):
        return
    packet = task.get("internal_skill_execution_packet")
    if isinstance(packet, dict) and packet.get("status") == "draft_execution_packet_ready":
        return
    raise AgentTaskDispatchReviewError(
        "internal_skill_execution_packet_required",
        "Internal skill task must generate a reviewable execution packet before dispatch approval.",
    )


def has_internal_skill_binding(task: dict[str, Any]) -> bool:
    bindings = task.get("internal_skill_bindings")
    return isinstance(bindings, list) and any(isinstance(binding, dict) for binding in bindings)


def apply_dispatch_review(task: dict[str, Any], action: str, note: str, timestamp: str) -> None:
    review = {
        "status": "reviewed",
        "action": action,
        "reviewer": "human",
        "note": note,
        "reviewed_at": timestamp,
        "evidence_level": "local_file",
    }
    task["dispatch_review"] = review
    task["can_execute"] = False
    if action == "approve":
        task["status"] = "reviewed_for_dispatch"
        task["next_action"] = "select_execution_backend"
        task["blockers"] = []
        task["dispatch_readiness"] = {
            "status": "reviewed_for_dispatch",
            "blockers": [],
        }
    elif action == "reject":
        blocker = {
            "code": "dispatch_rejected",
            "label": "派工已阻断",
            "description": note or "人工拒绝了这个子 Agent 任务。",
        }
        task["status"] = "blocked"
        task["next_action"] = "revise_dispatch_task"
        task["blockers"] = [blocker]
        task["dispatch_readiness"] = {
            "status": "blocked",
            "blockers": [blocker],
        }
    else:
        blocker = {
            "code": "dispatch_needs_revision",
            "label": "派工需要修改",
            "description": note or "人工要求先修改这个子 Agent 任务。",
        }
        task["status"] = "needs_revision"
        task["next_action"] = "revise_dispatch_task"
        task["blockers"] = [blocker]
        task["dispatch_readiness"] = {
            "status": "blocked",
            "blockers": [blocker],
        }
    task.setdefault("audit_log", []).append(
        {
            "event": "dispatch_review_recorded",
            "actor": "human",
            "timestamp": timestamp,
            "action": action,
            "note": note,
            "previous_dispatch_blocker": dispatch_review_required_blocker()["code"],
        }
    )

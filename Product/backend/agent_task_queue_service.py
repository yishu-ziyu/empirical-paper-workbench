from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.supervisor_plan_service import load_saved_supervisor_plan


AGENT_TASK_QUEUE_PATH = Path("state/product/agent_task_queue.json")


class AgentTaskQueueBlockedError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def agent_task_queue_state_path(project_root: Path) -> Path:
    return project_root / AGENT_TASK_QUEUE_PATH


def get_project_agent_task_queue(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    queue = load_saved_agent_task_queue(project_root)
    if not queue:
        queue = build_empty_agent_task_queue(project_root)
    return build_agent_task_queue_response(project, queue)


def create_project_agent_task_queue(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    plan = load_saved_supervisor_plan(project_root)
    require_approved_supervisor_plan(plan)
    dispatch_items = normalize_list(plan.get("subagent_dispatch"))
    if not dispatch_items:
        raise AgentTaskQueueBlockedError(
            "subagent_dispatch_required",
            "Approved SupervisorPlan must include subagent_dispatch before creating Agent Task Queue.",
        )

    timestamp = utc_now()
    queue = build_agent_task_queue(plan, dispatch_items, timestamp)
    path = agent_task_queue_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    return build_agent_task_queue_response(project, queue)


def load_saved_agent_task_queue(project_root: Path) -> dict[str, Any] | None:
    path = agent_task_queue_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_empty_agent_task_queue(project_root: Path) -> dict[str, Any]:
    plan = load_saved_supervisor_plan(project_root)
    blockers = agent_task_queue_blockers(plan)
    can_create = not blockers and bool(normalize_list(plan.get("subagent_dispatch") if plan else []))
    return {
        "id": "agent_task_queue",
        "version": 0,
        "status": "ready_to_create" if can_create else "empty",
        "exists": agent_task_queue_state_path(project_root).exists(),
        "can_create": can_create,
        "evidence_level": "local_file",
        "source_supervisor_plan": compact_supervisor_plan_source(plan),
        "summary": {
            "total_tasks": 0,
            "queued_count": 0,
            "blocked_count": len(blockers),
            "owner_agents": [],
        },
        "tasks": [],
        "blockers": blockers,
        "ui_contract": build_queue_ui_contract(),
        "next_action": {
            "id": "create_agent_task_queue" if can_create else "approve_supervisor_plan",
            "label": "创建 Agent 任务队列" if can_create else "先批准 SupervisorPlan",
        },
        "path": AGENT_TASK_QUEUE_PATH.as_posix(),
    }


def require_approved_supervisor_plan(plan: dict[str, Any] | None) -> None:
    if not plan:
        raise AgentTaskQueueBlockedError(
            "supervisor_plan_required",
            "Approved SupervisorPlan is required before creating Agent Task Queue.",
        )
    if plan.get("status") != "approved" or plan.get("can_dispatch") is not True:
        raise AgentTaskQueueBlockedError(
            "supervisor_plan_not_approved",
            "SupervisorPlan must be approved and can_dispatch=true before creating Agent Task Queue.",
        )


def agent_task_queue_blockers(plan: dict[str, Any] | None) -> list[dict[str, str]]:
    if not plan:
        return [
            {
                "code": "supervisor_plan_required",
                "label": "缺少 SupervisorPlan",
                "description": "先由本地 Codex Supervisor 生成可审阅计划。",
            }
        ]
    if plan.get("status") != "approved" or plan.get("can_dispatch") is not True:
        return [
            {
                "code": "supervisor_plan_not_approved",
                "label": "SupervisorPlan 尚未批准",
                "description": "只有人工批准后的计划才能创建任务队列。",
            }
        ]
    if not normalize_list(plan.get("subagent_dispatch")):
        return [
            {
                "code": "subagent_dispatch_required",
                "label": "缺少子 Agent 分工",
                "description": "Approved SupervisorPlan 必须包含 subagent_dispatch。",
            }
        ]
    return []


def build_agent_task_queue(plan: dict[str, Any], dispatch_items: list[Any], timestamp: str) -> dict[str, Any]:
    tasks = [
        build_agent_task(index, dispatch, plan, timestamp)
        for index, dispatch in enumerate(dispatch_items, start=1)
    ]
    return {
        "id": "agent_task_queue",
        "version": 1,
        "status": "ready_for_dispatch",
        "exists": True,
        "can_create": False,
        "evidence_level": "local_file",
        "source_supervisor_plan": compact_supervisor_plan_source(plan),
        "summary": build_agent_task_queue_summary(tasks),
        "tasks": tasks,
        "blockers": [],
        "ui_contract": build_queue_ui_contract(),
        "next_action": {
            "id": "dispatch_agent_tasks",
            "label": "检查后进入真实 Agent 执行队列",
        },
        "path": AGENT_TASK_QUEUE_PATH.as_posix(),
        "updated_at": timestamp,
    }


def build_agent_task(index: int, dispatch: Any, plan: dict[str, Any], timestamp: str) -> dict[str, Any]:
    dispatch_item = dispatch if isinstance(dispatch, dict) else {"task": str(dispatch)}
    owner_agent = str(dispatch_item.get("agent_id") or dispatch_item.get("role") or f"agent_{index:02d}")
    role = str(dispatch_item.get("role") or owner_agent)
    title = str(dispatch_item.get("task") or dispatch_item.get("title") or dispatch_item.get("goal") or f"Agent task {index}")
    return {
        "id": f"agent_task_{index:02d}",
        "source_dispatch_id": dispatch_item.get("agent_id") or "",
        "owner_agent": owner_agent,
        "role": role,
        "title": title,
        "summary": str(dispatch_item.get("summary") or title),
        "status": "queued",
        "can_execute": False,
        "next_action": "dispatch_review_required",
        "dispatch_readiness": {
            "status": "blocked",
            "blockers": [dispatch_review_required_blocker()],
        },
        "dispatch_review": {
            "status": "pending",
            "evidence_level": "local_file",
        },
        "input_evidence": build_task_input_evidence(plan),
        "output_requirements": build_output_requirements(plan, dispatch_item),
        "blockers": [],
        "risk_flags": normalize_list(plan.get("risks")),
        "audit_log": [
            {
                "event": "task_created_from_supervisor_plan",
                "actor": "product_workbench",
                "timestamp": timestamp,
                "source_supervisor_plan_version": plan.get("version", 0),
            }
        ],
    }


def build_task_input_evidence(plan: dict[str, Any]) -> dict[str, Any]:
    input_evidence = plan.get("input_evidence") if isinstance(plan.get("input_evidence"), dict) else {}
    return {
        "supervisor_plan": {
            "path": "state/product/supervisor_plan.json",
            "version": plan.get("version", 0),
            "evidence_level": plan.get("evidence_level", "local_execution"),
        },
        "research_question": plan.get("input_research_question") or {},
        "state_paths": input_evidence,
    }


def build_output_requirements(plan: dict[str, Any], dispatch_item: dict[str, Any]) -> list[dict[str, Any]]:
    explicit_outputs = normalize_list(dispatch_item.get("output_requirements"))
    if explicit_outputs:
        return [item if isinstance(item, dict) else {"requirement": str(item)} for item in explicit_outputs]
    requirements = normalize_list(plan.get("evidence_requirements"))
    return [
        item if isinstance(item, dict) else {"requirement": str(item)}
        for item in requirements
    ]


def compact_supervisor_plan_source(plan: dict[str, Any] | None) -> dict[str, Any]:
    if not plan:
        return {
            "exists": False,
            "path": "state/product/supervisor_plan.json",
        }
    return {
        "exists": True,
        "id": plan.get("id", "supervisor_plan"),
        "version": int(plan.get("version", 0)),
        "status": plan.get("status", "unknown"),
        "can_dispatch": bool(plan.get("can_dispatch")),
        "path": plan.get("path") or "state/product/supervisor_plan.json",
        "objective": plan.get("objective", ""),
        "research_question": (plan.get("input_research_question") or {}).get("question", ""),
    }


def build_queue_ui_contract() -> dict[str, Any]:
    return {
        "summary_first": True,
        "details_collapsed_by_default": True,
        "primary_object": "agent_task",
        "hidden_by_default": [
            "input_evidence",
            "output_requirements",
            "risk_flags",
            "audit_log",
        ],
    }


def build_agent_task_queue_response(project: dict[str, Any], queue: dict[str, Any]) -> dict[str, Any]:
    queue = normalize_agent_task_queue(queue)
    return {
        "_meta": {
            "evidence_level": queue.get("evidence_level", "local_file"),
            "service": "agent_task_queue_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "agent_task_queue": queue,
    }


def normalize_agent_task_queue(queue: dict[str, Any]) -> dict[str, Any]:
    tasks = normalize_list(queue.get("tasks"))
    if tasks:
        for task in tasks:
            if isinstance(task, dict):
                ensure_task_dispatch_audit_fields(task)
        queue["summary"] = build_agent_task_queue_summary(tasks)
    return queue


def ensure_task_dispatch_audit_fields(task: dict[str, Any]) -> None:
    status = str(task.get("status") or "queued")
    task.setdefault("can_execute", False)
    if status == "reviewed_for_dispatch":
        task.setdefault("next_action", "select_execution_backend")
        task.setdefault("dispatch_readiness", {"status": "reviewed_for_dispatch", "blockers": []})
    elif status == "blocked":
        task.setdefault("next_action", "revise_dispatch_task")
        task.setdefault(
            "dispatch_readiness",
            {
                "status": "blocked",
                "blockers": task.get("blockers") or [dispatch_review_required_blocker()],
            },
        )
    else:
        task.setdefault("next_action", "dispatch_review_required")
        task.setdefault(
            "dispatch_readiness",
            {
                "status": "blocked",
                "blockers": [dispatch_review_required_blocker()],
            },
        )
    task.setdefault(
        "dispatch_review",
        {
            "status": "pending",
            "evidence_level": "local_file",
        },
    )


def build_agent_task_queue_summary(tasks: list[Any]) -> dict[str, Any]:
    task_dicts = [task for task in tasks if isinstance(task, dict)]
    return {
        "total_tasks": len(task_dicts),
        "queued_count": len([task for task in task_dicts if task.get("status") == "queued"]),
        "blocked_count": len([task for task in task_dicts if task.get("blockers")]),
        "dispatch_reviewed_count": len(
            [task for task in task_dicts if task.get("status") == "reviewed_for_dispatch"]
        ),
        "needs_revision_count": len([task for task in task_dicts if task.get("status") == "needs_revision"]),
        "owner_agents": unique_preserve_order([str(task.get("owner_agent", "")) for task in task_dicts]),
    }


def dispatch_review_required_blocker() -> dict[str, str]:
    return {
        "code": "dispatch_review_required",
        "label": "等待人工派工审阅",
        "description": "队列草案不能直接执行，必须先确认这个子 Agent 任务是否应该派发。",
    }


def normalize_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result

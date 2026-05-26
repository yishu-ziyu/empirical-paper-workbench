from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute


PROTECTED_FORMAL_STATE = [
    "state/product/research_question.json",
    "state/product/variable_roles.json",
    "state/product/variable_role_set.json",
    "state/product/design_spec.json",
    "state/product/run_plan.json",
    "state/product/supervisor_plan.json",
    "state/product/agent_task_queue.json",
]

DEFAULT_VERIFICATION_EVIDENCE = [
    "updated_section_or_diagnostic_artifact",
    "reviewer_scorecard_task_cleared",
    "export_gate_recomputed",
    "human_review_decision_recorded",
]


def snapshot_formal_state(project_root: Path) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for relative_path in PROTECTED_FORMAL_STATE:
        path = project_root / relative_path
        if path.exists():
            content = path.read_bytes()
            snapshot[relative_path] = {
                "exists": True,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
            }
        else:
            snapshot[relative_path] = {"exists": False, "sha256": None, "bytes": 0}
    return snapshot


def diff_formal_state(
    before: dict[str, dict[str, Any]],
    after: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    changed = [
        path
        for path in sorted(set(before) | set(after))
        if before.get(path) != after.get(path)
    ]
    return {
        "protected_paths": PROTECTED_FORMAL_STATE,
        "changed": bool(changed),
        "changed_paths": changed,
    }


def build_paper_revision_round(
    project_root: Path,
    expansion_plan: dict[str, Any],
    expansion_plan_path: Path,
    *,
    supervisor_context: dict[str, Any] | None = None,
    supervisor_context_path: Path | None = None,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    tasks = normalize_revision_items(project_root, expansion_plan, expansion_plan_path)
    packets = build_agent_packets(tasks)
    schedule = build_agent_team_schedule(expansion_plan, tasks)
    before = formal_state_before or snapshot_formal_state(project_root)
    after = snapshot_formal_state(project_root)

    return {
        "schema_version": "p4.paper_revision_round.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "round_id": build_round_id(expansion_plan, tasks),
        "profile": expansion_plan.get("profile", "general_working_paper"),
        "status": "ready_for_human_review",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "write_boundary": (
            "本轮只生成草案层 revision round、Agent packets 和验收清单；"
            "正式层 state/product、正式论文和 canonical 方法库必须人工确认后写回。"
        ),
        "source_expansion_plan": relative_or_absolute(expansion_plan_path, project_root),
        "source_supervisor_context": (
            relative_or_absolute(supervisor_context_path, project_root)
            if supervisor_context_path is not None
            else None
        ),
        "source_contexts": build_source_contexts(project_root, expansion_plan, supervisor_context),
        "revision_items": tasks,
        "agent_packets": packets,
        "agent_team_schedule": schedule,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": {
            "id": "review_revision_round",
            "label": "人工审阅本轮修订任务",
            "description": "确认每个 Agent packet 的输入、输出和验收证据后，再进入 P4-H/P5 的真实任务执行。",
        },
    }


def write_paper_revision_round(path: Path, revision_round: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(revision_round, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_revision_review_markdown(revision_round: dict[str, Any]) -> str:
    lines = [
        "# 审稿式修订轮次",
        "",
        f"- Round: `{revision_round['round_id']}`",
        f"- Profile: `{revision_round.get('profile')}`",
        "- 正式层写回：关闭",
        "- 当前状态：等待人工审阅",
        "",
        "## Agent Team 调用节奏",
        "",
    ]
    schedule = revision_round.get("agent_team_schedule", {})
    for key in ["call_when", "called_agents", "recall_when", "next_call_when", "boundary"]:
        lines.append(f"- {key}: {schedule.get(key)}")
    lines.extend(["", "## Agent Packets", ""])

    for packet in revision_round.get("agent_packets", []):
        lines.extend(
            [
                f"### {packet['agent']}",
                "",
                f"- 任务数：{packet['task_count']}",
                f"- 草案输出目录：`{packet['draft_output_dir']}`",
                "",
            ]
        )
        for task in packet.get("tasks", []):
            lines.extend(
                [
                    f"#### {task['id']}",
                    "",
                    f"- 来源：{task.get('source')}",
                    f"- 来源产物：`{task.get('source_artifact')}`",
                    f"- 动作：{task.get('action_item')}",
                    f"- 状态：{task.get('status')}",
                    f"- 输入：{', '.join(str(item) for item in task.get('inputs', [])) or '无'}",
                    f"- 草案产物：`{task.get('draft_output_path')}`",
                    "- 验收证据：",
                ]
            )
            for evidence in task.get("verification_evidence_required", []):
                lines.append(f"  - {evidence}")
            lines.append("")

    lines.extend(
        [
            "## 正式层保护",
            "",
            f"- changed: `{revision_round.get('formal_state_guard', {}).get('changed')}`",
            "- protected paths:",
        ]
    )
    for path in revision_round.get("formal_state_guard", {}).get("protected_paths", []):
        lines.append(f"  - `{path}`")
    return "\n".join(lines).rstrip() + "\n"


def write_revision_review_markdown(path: Path, revision_round: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_revision_review_markdown(revision_round), encoding="utf-8")
    return path


def normalize_revision_items(
    project_root: Path,
    expansion_plan: dict[str, Any],
    expansion_plan_path: Path,
) -> list[dict[str, Any]]:
    source_plan = relative_or_absolute(expansion_plan_path, project_root)
    items: list[dict[str, Any]] = []
    for order, task in enumerate(expansion_plan.get("agent_task_queue", []), start=1):
        task_id = str(task.get("id") or f"revision_task_{order}")
        source = str(task.get("source") or "paper_expansion_plan")
        source_artifact = str(task.get("source_artifact") or source_plan)
        verification = task.get("verification", {}).get("required_before_completion")
        evidence = list(verification or DEFAULT_VERIFICATION_EVIDENCE)
        action_item = task.get("action") or task.get("recommended_action") or task.get("reason") or task_id
        agent = str(task.get("agent") or infer_agent(task_id))
        items.append(
            {
                "order": order,
                "id": task_id,
                "agent": agent,
                "source": source,
                "source_artifact": source_artifact,
                "reason": task.get("reason") or action_item,
                "action_item": action_item,
                "inputs": task.get("inputs", []),
                "draft_output_path": build_draft_output_path(agent, task_id),
                "verification_evidence_required": evidence,
                "requires_human_confirmation": True,
                "can_write_product_state": False,
                "status": "queued_for_revision",
            }
        )
    return items


def build_agent_packets(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in tasks:
        grouped[task["agent"]].append(task)

    packets = []
    for agent in sorted(grouped):
        agent_tasks = sorted(grouped[agent], key=lambda item: item["order"])
        packets.append(
            {
                "agent": agent,
                "task_count": len(agent_tasks),
                "draft_output_dir": f"Reviews/agent_packets/{slugify(agent)}",
                "source_inputs": sorted(
                    {
                        str(input_item)
                        for task in agent_tasks
                        for input_item in task.get("inputs", [])
                    }
                ),
                "handoff_prompt": build_agent_handoff_prompt(agent, agent_tasks),
                "tasks": agent_tasks,
            }
        )
    return packets


def build_agent_team_schedule(
    expansion_plan: dict[str, Any],
    tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    called_agents = set(expansion_plan.get("agent_team_schedule", {}).get("called_agents", []))
    called_agents.update(task.get("agent") for task in tasks if task.get("agent"))
    called_agents.update(["ReviewerAgent", "VerifierAgent", "MethodAgent"])
    return {
        "call_when": "before_revision_round_build",
        "called_agents": sorted(called_agents),
        "upstream_call_when": expansion_plan.get("agent_team_schedule", {}).get("call_when"),
        "upstream_recall_when": expansion_plan.get("agent_team_schedule", {}).get("recall_when"),
        "recall_when": "after_revision_round_manifest_written",
        "next_call_when": "before_revision_task_execution_or_formal_writeback",
        "integration_owner": "MainAgent",
        "boundary": (
            "生成 revision round 前调用 ReviewerAgent/VerifierAgent/MethodAgent 复核任务、证据和正式层边界；"
            "round manifest 和 review doc 写出后收回；执行任务或正式层写回前再次调用，确认验收证据已补齐。"
        ),
    }


def build_source_contexts(
    project_root: Path,
    expansion_plan: dict[str, Any],
    supervisor_context: dict[str, Any] | None,
) -> list[str]:
    contexts = {"Results/json/paper_expansion_plan.json"}
    if supervisor_context:
        contexts.update(str(source) for source in supervisor_context.get("context_sources", []))
    source_manifest = expansion_plan.get("source_export_manifest")
    if source_manifest:
        contexts.add(str(source_manifest))
    return sorted(contexts)


def build_round_id(expansion_plan: dict[str, Any], tasks: list[dict[str, Any]]) -> str:
    seed = "|".join([str(expansion_plan.get("profile", ""))] + [task["id"] for task in tasks])
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]
    return f"paper_revision_round_{digest}"


def build_draft_output_path(agent: str, task_id: str) -> str:
    return f"Reviews/agent_packets/{slugify(agent)}/{slugify(task_id)}.md"


def build_agent_handoff_prompt(agent: str, tasks: list[dict[str, Any]]) -> str:
    task_lines = "\n".join(
        f"- {task['id']}: {task['action_item']} | evidence={', '.join(task['verification_evidence_required'])}"
        for task in tasks
    )
    return (
        f"你是 {agent}。只处理下列草案层修订任务，不写正式 state/product，不覆盖正式论文。\n"
        "每个任务必须输出草案产物、证据说明和验收记录，等待人工确认后再进入正式层。\n"
        f"{task_lines}"
    )


def infer_agent(task_id: str) -> str:
    if any(marker in task_id for marker in ["literature", "bibliography", "citation", "contribution"]):
        return "LiteratureAgent"
    if any(marker in task_id for marker in ["method", "iv", "bartik", "rdd", "did", "psm", "dml", "identification"]):
        return "MethodAgent"
    if any(marker in task_id for marker in ["data", "sample", "variable", "missing"]):
        return "DataAgent"
    if any(marker in task_id for marker in ["review", "scorecard", "revision"]):
        return "ReviewerAgent"
    if any(marker in task_id for marker in ["export", "pdf", "manifest"]):
        return "VerifierAgent"
    return "ManuscriptAgent"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "item"

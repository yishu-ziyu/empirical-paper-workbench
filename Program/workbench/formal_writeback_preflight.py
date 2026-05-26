from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


WRITEBACK_CATEGORIES = [
    {
        "category": "sections",
        "label": "章节扩写",
        "agents": {"ManuscriptAgent"},
        "fallback_paths": ["Manuscripts/generated/paper_package_draft.md"],
        "approval_question": "是否把扩写后的章节结构纳入正式 paper package？",
    },
    {
        "category": "citations",
        "label": "引用与文献",
        "agents": {"LiteratureAgent"},
        "fallback_paths": [
            "Data/literature/processed/verified_bibliography.csv",
            "Data/literature/processed/contribution_matrix.md",
        ],
        "approval_question": "是否接受当前文献清单、贡献矩阵和引用边界？",
    },
    {
        "category": "method_narrative",
        "label": "方法叙述",
        "agents": {"MethodAgent"},
        "fallback_paths": [
            "Results/json/method_gate_report.json",
            "Results/json/method_diagnostics_report.json",
        ],
        "approval_question": "是否把方法门诊断和识别边界写入正式方法章节？",
    },
    {
        "category": "result_tables",
        "label": "结果表与样本说明",
        "agents": {"ExecutionAgent", "DataAgent"},
        "fallback_paths": [
            "Results/json/method_execution_result.json",
            "Results/json/project_snapshot.json",
        ],
        "approval_question": "是否把当前结果表、样本口径和数据诊断纳入正式结果章节？",
    },
    {
        "category": "reproducibility",
        "label": "复现说明",
        "agents": {"ReviewerAgent", "VerifierAgent", "ExportAgent"},
        "fallback_paths": [
            "Results/json/reviewer_scorecard_report.json",
            "Submissions/cfps_robot_pdf_export_manifest.json",
            "Results/json/paper_quality_report.json",
        ],
        "approval_question": "是否进入 P5 正式包并生成复现交付材料？",
    },
]


def build_formal_writeback_preflight(
    project_root: Path,
    gate_recompute: dict[str, Any],
    gate_recompute_path: Path,
    preview_path: Path,
    *,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    before = formal_state_before or snapshot_formal_state(project_root)
    blocking_reasons = build_blocking_reasons(gate_recompute)
    ready = not blocking_reasons
    writeback_scope = build_writeback_scope(project_root, gate_recompute) if ready else []
    after = snapshot_formal_state(project_root)

    return {
        "schema_version": "p4.formal_writeback_preflight.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_gate_recompute": relative_or_absolute(gate_recompute_path, project_root),
        "status": "ready_for_human_approval" if ready else "blocked_by_gate_recompute",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "requires_human_approval": True,
        "blocking_reasons": blocking_reasons,
        "source_status_counts": gate_recompute.get("status_counts", {}),
        "writeback_scope": writeback_scope,
        "preview_path": relative_or_absolute(preview_path, project_root),
        "approval_contract": build_approval_contract(ready),
        "agent_team_schedule": build_agent_team_schedule(writeback_scope),
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(ready, blocking_reasons),
    }


def build_blocking_reasons(gate_recompute: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if gate_recompute.get("status") != "ready_for_formal_writeback_preflight":
        reasons.append("gate_recompute_not_ready")
    task_results = gate_recompute.get("task_results", [])
    if any(task.get("status") != "cleared" for task in task_results):
        reasons.append("uncleared_revision_tasks")
    if gate_recompute.get("next_action", {}).get("id") != "formal_writeback_preflight":
        reasons.append("next_action_not_formal_writeback_preflight")
    return reasons


def build_writeback_scope(project_root: Path, gate_recompute: dict[str, Any]) -> list[dict[str, Any]]:
    tasks_by_agent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in gate_recompute.get("task_results", []):
        if task.get("status") == "cleared":
            tasks_by_agent[str(task.get("agent") or "")].append(task)

    scope: list[dict[str, Any]] = []
    for order, spec in enumerate(WRITEBACK_CATEGORIES, start=1):
        tasks = [
            task
            for agent in spec["agents"]
            for task in tasks_by_agent.get(agent, [])
        ]
        evidence_refs = collect_category_evidence(project_root, spec["fallback_paths"], tasks)
        scope.append(
            {
                "order": order,
                "category": spec["category"],
                "label": spec["label"],
                "approval_question": spec["approval_question"],
                "task_ids": [task.get("task_id") for task in tasks if task.get("task_id")],
                "evidence_refs": evidence_refs,
                "approval_status": "pending_human_approval",
                "requires_human_confirmation": True,
                "can_write_product_state": False,
            }
        )
    return scope


def collect_category_evidence(
    project_root: Path,
    fallback_paths: list[str],
    tasks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    evidence: list[dict[str, Any]] = []
    for task in tasks:
        for item in task.get("evidence_items", []):
            path = item.get("path") if isinstance(item, dict) else None
            if path:
                append_evidence_ref(project_root, evidence, seen, path, source="revision_task")
        packet_path = task.get("evidence_packet_path")
        if packet_path:
            append_evidence_ref(project_root, evidence, seen, packet_path, source="agent_packet")
    for path in fallback_paths:
        append_evidence_ref(project_root, evidence, seen, path, source="canonical_artifact")
    return evidence


def append_evidence_ref(
    project_root: Path,
    evidence: list[dict[str, Any]],
    seen: set[str],
    path_value: str,
    *,
    source: str,
) -> None:
    if path_value in seen:
        return
    seen.add(path_value)
    path = Path(path_value)
    resolved = path if path.is_absolute() else project_root / path
    evidence.append(
        {
            "path": path_value,
            "source": source,
            "exists": resolved.exists(),
            "evidence_level": "local_file" if resolved.exists() else "planned_artifact",
        }
    )


def build_approval_contract(ready: bool) -> dict[str, Any]:
    return {
        "required_before_p5": [
            "human_approval_record",
            "writeback_scope_reviewed",
            "formal_state_guard_confirmed",
        ],
        "approval_path": "state/product/writeback_approvals.json",
        "docx_preflight_path": "state/product/docx_export_preflight.json",
        "ready_for_approval": ready,
        "canonical_write_policy": (
            "本节点只生成草案层预览；人工批准后，P5 才能写正式 paper package、docx preflight 和 export manifest。"
        ),
    }


def build_agent_team_schedule(writeback_scope: list[dict[str, Any]]) -> dict[str, Any]:
    called_agents = ["ReviewerAgent", "VerifierAgent"]
    for item in writeback_scope:
        if item["category"] == "sections":
            called_agents.append("ManuscriptAgent")
        elif item["category"] == "citations":
            called_agents.append("LiteratureAgent")
        elif item["category"] == "method_narrative":
            called_agents.append("MethodAgent")
        elif item["category"] == "result_tables":
            called_agents.append("ExecutionAgent")
        elif item["category"] == "reproducibility":
            called_agents.append("ExportAgent")
    return {
        "call_when": "before_formal_writeback_preflight",
        "called_agents": sorted(set(called_agents), key=called_agents.index),
        "recall_when": "after_formal_writeback_preflight_written",
        "next_call_when": "after_human_approval_before_p5_formal_package",
        "integration_owner": "MainAgent",
        "boundary": "Agent Team 只复核写回范围、证据和风险；正式写回由 P5 在人工批准后执行。",
    }


def build_next_action(ready: bool, blocking_reasons: list[str]) -> dict[str, Any]:
    if ready:
        return {
            "id": "human_approve_formal_package",
            "label": "人工批准正式包写回",
            "description": "审阅 formal writeback preview 后，决定是否进入 P5 正式 paper package。",
        }
    return {
        "id": "rerun_revision_gate_recompute",
        "label": "回到质量门复核",
        "description": "先处理 gate recompute 阻塞项，再重新生成正式写回预检。",
        "blocking_reasons": blocking_reasons,
    }


def write_formal_writeback_preflight_outputs(
    report_path: Path,
    review_path: Path,
    preview_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(build_review_markdown(report), encoding="utf-8")
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.write_text(build_preview_markdown(report), encoding="utf-8")
    return report_path, review_path, preview_path


def build_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P4-J 正式写回预检",
        "",
        f"- Source gate recompute: `{report.get('source_gate_recompute')}`",
        f"- Status: `{report.get('status')}`",
        "- 正式层写回：关闭",
        "- 人工批准：必需",
        "",
        "## 写回范围",
        "",
    ]
    if not report.get("writeback_scope"):
        lines.append("- 当前 gate recompute 尚未满足正式写回预检条件。")
    for item in report.get("writeback_scope", []):
        lines.extend(
            [
                f"### {item.get('label')}",
                "",
                f"- Category: `{item.get('category')}`",
                f"- Approval status: `{item.get('approval_status')}`",
                f"- Task ids: {', '.join(item.get('task_ids', [])) or 'none'}",
                "- Evidence refs:",
            ]
        )
        for evidence in item.get("evidence_refs", []):
            lines.append(f"  - `{evidence.get('path')}` ({evidence.get('evidence_level')})")
        lines.append("")

    lines.extend(["## Agent Team 调用节奏", ""])
    schedule = report.get("agent_team_schedule", {})
    for key in ["call_when", "called_agents", "recall_when", "next_call_when", "boundary"]:
        lines.append(f"- {key}: {schedule.get(key)}")

    lines.extend(
        [
            "",
            "## 正式层保护",
            "",
            f"- changed: `{report.get('formal_state_guard', {}).get('changed')}`",
            "- protected paths:",
        ]
    )
    for path in report.get("formal_state_guard", {}).get("protected_paths", []):
        lines.append(f"  - `{path}`")
    return "\n".join(lines).rstrip() + "\n"


def build_preview_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Formal Writeback Preview",
        "",
        "这份预览只用于人工审阅，不写入正式层。",
        "",
    ]
    if report.get("status") != "ready_for_human_approval":
        lines.extend(["## 当前不能进入正式写回", ""])
        for reason in report.get("blocking_reasons", []):
            lines.append(f"- {reason}")
        return "\n".join(lines).rstrip() + "\n"

    for item in report.get("writeback_scope", []):
        lines.extend(
            [
                f"## {item.get('label')}",
                "",
                f"- 审批问题：{item.get('approval_question')}",
                f"- 当前状态：{item.get('approval_status')}",
                "- 证据：",
            ]
        )
        for evidence in item.get("evidence_refs", []):
            lines.append(f"  - `{evidence.get('path')}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

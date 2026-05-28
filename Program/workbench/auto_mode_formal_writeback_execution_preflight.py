from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_writeback_execution_preflight.v1"
DEFAULT_APPROVAL_PATH = Path("Results/json/auto_mode_formal_writeback_approval.json")
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_writeback_execution_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_writeback_execution_preflight.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_writeback_execution_preflight(
    formal_writeback_approval: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    approval_reasons = build_approval_blocking_reasons(formal_writeback_approval)
    scope_reasons = build_scope_blocking_reasons(formal_writeback_approval)
    boundary_reasons = build_boundary_blocking_reasons(formal_writeback_approval)
    blocking_reasons = boundary_reasons + approval_reasons + scope_reasons
    status = build_status(boundary_reasons, approval_reasons, scope_reasons)
    ready = status == "ready_for_formal_writeback_execution_review"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": formal_writeback_approval.get("topic", ""),
        "source_paths": {
            "formal_writeback_approval": source_paths.get("formal_writeback_approval", str(DEFAULT_APPROVAL_PATH)),
        },
        "status": status,
        "can_request_formal_writeback_execution": ready,
        "requires_explicit_execute_command": True,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_approval": build_source_approval(formal_writeback_approval),
        "execution_plan": build_execution_plan(formal_writeback_approval) if ready else [],
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_approval_blocking_reasons(formal_writeback_approval: dict[str, Any]) -> list[str]:
    reasons = []
    if formal_writeback_approval.get("schema_version") != "p7.auto_mode_formal_writeback_approval.v1":
        reasons.append("formal_writeback_approval_missing_or_invalid_schema")
    effective = (
        formal_writeback_approval.get("status") == "approved_for_formal_writeback_execution_preflight"
        and formal_writeback_approval.get("approved") is True
        and formal_writeback_approval.get("formal_writeback_allowed") is True
        and formal_writeback_approval.get("can_enter_formal_writeback_execution_preflight") is True
    )
    if not effective:
        reasons.append("formal_writeback_approval_not_effective")
    approval = formal_writeback_approval.get("approval", {})
    if approval.get("decision") != "approve":
        reasons.append("formal_writeback_approval_decision_not_approve")
    if approval.get("metadata_complete") is not True:
        reasons.append("formal_writeback_approval_metadata_incomplete")
    return reasons


def build_scope_blocking_reasons(formal_writeback_approval: dict[str, Any]) -> list[str]:
    approved_scope = formal_writeback_approval.get("approved_scope", [])
    if not approved_scope:
        return ["approved_scope_missing"]
    reasons = []
    for item in approved_scope:
        category = item.get("category", "unknown")
        if item.get("approval_status") != "approved_for_formal_writeback_execution_preflight":
            reasons.append(f"approved_scope_not_ready:{category}")
        if item.get("requires_execution_preflight") is not True:
            reasons.append(f"approved_scope_missing_execution_preflight_requirement:{category}")
        if item.get("this_command_wrote_formal_state") is True:
            reasons.append(f"approved_scope_already_wrote_formal_state:{category}")
    return reasons


def build_boundary_blocking_reasons(formal_writeback_approval: dict[str, Any]) -> list[str]:
    reasons = []
    if formal_writeback_approval.get("this_command_wrote_formal_state") is True:
        reasons.append("approval_ledger_already_wrote_formal_state")
    if formal_writeback_approval.get("can_write_product_state") is True:
        reasons.append("approval_ledger_allows_product_state_write")
    for flag, value in formal_writeback_approval.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"approval_ledger_boundary_violation:{flag}")
    return reasons


def build_status(
    boundary_reasons: list[str],
    approval_reasons: list[str],
    scope_reasons: list[str],
) -> str:
    if boundary_reasons:
        return "blocked_by_approval_boundary_violation"
    if approval_reasons:
        return "blocked_by_formal_writeback_approval"
    if scope_reasons:
        return "blocked_by_formal_writeback_scope"
    return "ready_for_formal_writeback_execution_review"


def build_source_approval(formal_writeback_approval: dict[str, Any]) -> dict[str, Any]:
    approval = formal_writeback_approval.get("approval", {})
    return {
        "schema_version": formal_writeback_approval.get("schema_version", ""),
        "status": formal_writeback_approval.get("status", ""),
        "approved": formal_writeback_approval.get("approved") is True,
        "formal_writeback_allowed": formal_writeback_approval.get("formal_writeback_allowed") is True,
        "can_enter_formal_writeback_execution_preflight": formal_writeback_approval.get(
            "can_enter_formal_writeback_execution_preflight"
        )
        is True,
        "this_command_wrote_formal_state": formal_writeback_approval.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": formal_writeback_approval.get("can_write_product_state") is True,
        "approved_scope_count": len(formal_writeback_approval.get("approved_scope", [])),
        "blocking_reasons": formal_writeback_approval.get("blocking_reasons", []),
        "decision": approval.get("decision", ""),
        "reviewer": approval.get("reviewer", ""),
        "metadata_complete": approval.get("metadata_complete") is True,
    }


def build_execution_plan(formal_writeback_approval: dict[str, Any]) -> list[dict[str, Any]]:
    plan = []
    for item in formal_writeback_approval.get("approved_scope", []):
        category = item.get("category", "")
        plan.append(
            {
                "category": category,
                "label": item.get("label", ""),
                "evidence_refs": item.get("evidence_refs", []),
                "execution_status": "pending_explicit_execute_command",
                "requires_explicit_execute_command": True,
                "executed_by_this_command": False,
                "writeback_target_group": build_writeback_target_group(category),
                "next_gates": item.get("next_gates", []),
            }
        )
    return plan


def build_writeback_target_group(category: str) -> str:
    target_groups = {
        "manuscript": "formal_manuscript_sources",
        "bibliography": "formal_bibliography_sources",
        "method_review": "method_review_records",
        "statistical_results": "statistical_result_records",
        "reproducibility": "reproducibility_records",
        "package_artifacts": "formal_package_records",
    }
    return target_groups.get(category, "unclassified_formal_writeback_target")


def build_boundary_flags() -> dict[str, bool]:
    return {
        "modified_formal_manuscript": False,
        "modified_formal_bibliography": False,
        "modified_project_bibliography": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "modified_product_state": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "reran_models": False,
        "modified_statistical_execution_artifacts": False,
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "ready_for_formal_writeback_execution_review":
        return {
            "id": "run_explicit_formal_writeback_execute_command",
            "label": "Run explicit formal writeback execute command",
            "description": "Execution preflight is ready; a separate command must perform and audit any formal writeback.",
        }
    if status == "blocked_by_approval_boundary_violation":
        return {
            "id": "repair_approval_boundary_violation",
            "label": "Repair approval boundary violation",
            "description": "The approval ledger indicates a write boundary violation and cannot feed execution.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_formal_writeback_scope":
        return {
            "id": "repair_formal_writeback_scope",
            "label": "Repair formal writeback scope",
            "description": "The approval ledger must include approved scope before execution can be requested.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "obtain_effective_formal_writeback_approval",
        "label": "Obtain effective formal writeback approval",
        "description": "The execution preflight cannot proceed until the P7-K approval ledger is effective.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_writeback_execution_preflight_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_PREFLIGHT_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Formal Writeback Execution Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 可请求正式写回执行：{str(report['can_request_formal_writeback_execution']).lower()}",
        f"- 需要单独执行命令：{str(report['requires_explicit_execute_command']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Execution Plan"])
    if report["execution_plan"]:
        for item in report["execution_plan"]:
            lines.append(f"- `{item['category']}`: {item['execution_status']}")
    else:
        lines.append("- 无；等待生效审批。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"

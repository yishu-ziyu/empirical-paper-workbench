from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_writeback_approval.v1"
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_promotion_preflight.json")
DEFAULT_APPROVAL_PATH = Path("Results/json/auto_mode_formal_writeback_approval.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_writeback_approval.md")
VALID_DECISIONS = {"approve", "defer", "revise", "reject"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_writeback_approval(
    formal_promotion_preflight: dict[str, Any],
    decision: str = "defer",
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(formal_promotion_preflight)
    approval_reasons = build_approval_blocking_reasons(decision, reviewer, note)
    blocking_reasons = preflight_reasons + approval_reasons
    status = build_status(decision, preflight_reasons, approval_reasons)
    approved = status == "approved_for_formal_writeback_execution_preflight"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": formal_promotion_preflight.get("topic", ""),
        "source_paths": {
            "formal_promotion_preflight": source_paths.get(
                "formal_promotion_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "status": status,
        "approved": approved,
        "formal_writeback_allowed": approved,
        "can_enter_formal_writeback_execution_preflight": approved,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_preflight": build_source_preflight(formal_promotion_preflight),
        "approval": build_approval(decision, reviewer, note, approved),
        "approved_scope": build_approved_scope(formal_promotion_preflight) if approved else [],
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_preflight_blocking_reasons(formal_promotion_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if formal_promotion_preflight.get("schema_version") != "p7.auto_mode_formal_promotion_preflight.v1":
        reasons.append("formal_promotion_preflight_missing_or_invalid_schema")
    if formal_promotion_preflight.get("status") != "ready_for_formal_writeback_approval":
        reasons.append("formal_promotion_preflight_not_ready")
    if formal_promotion_preflight.get("can_request_formal_writeback_approval") is not True:
        reasons.append("formal_promotion_preflight_cannot_request_approval")
    if formal_promotion_preflight.get("requires_separate_formal_writeback_approval") is not True:
        reasons.append("formal_promotion_preflight_missing_separate_approval_requirement")
    if formal_promotion_preflight.get("formal_writeback_allowed") is True:
        reasons.append("formal_promotion_preflight_already_allows_writeback")
    if formal_promotion_preflight.get("can_write_product_state") is True:
        reasons.append("formal_promotion_preflight_allows_product_state_write")
    if not formal_promotion_preflight.get("promotion_scope"):
        reasons.append("formal_promotion_scope_missing")
    for flag, value in formal_promotion_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"formal_promotion_preflight_boundary_violation:{flag}")
    return reasons


def build_approval_blocking_reasons(decision: str, reviewer: str, note: str) -> list[str]:
    if decision not in VALID_DECISIONS:
        return ["formal_writeback_decision_invalid"]
    if decision != "approve":
        return []
    reasons = []
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("approval_note_required")
    return reasons


def build_status(decision: str, preflight_reasons: list[str], approval_reasons: list[str]) -> str:
    if preflight_reasons:
        return "blocked_by_formal_promotion_preflight"
    if "formal_writeback_decision_invalid" in approval_reasons:
        return "blocked_by_formal_writeback_approval_decision"
    if decision == "approve" and approval_reasons:
        return "blocked_by_formal_writeback_approval_metadata"
    if decision == "approve":
        return "approved_for_formal_writeback_execution_preflight"
    if decision == "revise":
        return "formal_writeback_needs_revision"
    if decision == "reject":
        return "formal_writeback_rejected"
    return "waiting_for_human_formal_writeback_approval"


def build_source_preflight(formal_promotion_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": formal_promotion_preflight.get("schema_version", ""),
        "status": formal_promotion_preflight.get("status", ""),
        "can_request_formal_writeback_approval": formal_promotion_preflight.get(
            "can_request_formal_writeback_approval"
        )
        is True,
        "requires_separate_formal_writeback_approval": formal_promotion_preflight.get(
            "requires_separate_formal_writeback_approval"
        )
        is True,
        "formal_writeback_allowed": formal_promotion_preflight.get("formal_writeback_allowed") is True,
        "can_write_product_state": formal_promotion_preflight.get("can_write_product_state") is True,
        "promotion_scope_count": len(formal_promotion_preflight.get("promotion_scope", [])),
        "blocking_reasons": formal_promotion_preflight.get("blocking_reasons", []),
    }


def build_approval(decision: str, reviewer: str, note: str, approved: bool) -> dict[str, Any]:
    return {
        "decision": decision,
        "reviewer": reviewer,
        "note": note,
        "approved": approved,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_approved_scope(formal_promotion_preflight: dict[str, Any]) -> list[dict[str, Any]]:
    approved_scope = []
    for item in formal_promotion_preflight.get("promotion_scope", []):
        approved_scope.append(
            {
                "category": item.get("category", ""),
                "label": item.get("label", ""),
                "evidence_refs": item.get("evidence_refs", []),
                "approval_status": "approved_for_formal_writeback_execution_preflight",
                "requires_execution_preflight": True,
                "this_command_wrote_formal_state": False,
                "next_gates": item.get("next_gates", []),
            }
        )
    return approved_scope


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
    if status == "approved_for_formal_writeback_execution_preflight":
        return {
            "id": "run_formal_writeback_execution_preflight",
            "label": "Run formal writeback execution preflight",
            "description": "Formal writeback approval is recorded; a separate execution preflight must still protect formal state writes.",
        }
    if status == "blocked_by_formal_promotion_preflight":
        return {
            "id": "resolve_formal_promotion_preflight_blockers",
            "label": "Resolve formal promotion preflight blockers",
            "description": "The approval ledger cannot become effective until P7-J is ready.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_formal_writeback_approval_metadata":
        return {
            "id": "record_reviewer_and_approval_note",
            "label": "Record reviewer and approval note",
            "description": "Approval requires a traceable reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "formal_writeback_needs_revision":
        return {
            "id": "revise_paper_package_before_writeback",
            "label": "Revise paper package before writeback",
            "description": "The human decision requested revision before formal writeback.",
        }
    if status == "formal_writeback_rejected":
        return {
            "id": "stop_formal_writeback",
            "label": "Stop formal writeback",
            "description": "The human decision rejected formal writeback for this package.",
        }
    if status == "blocked_by_formal_writeback_approval_decision":
        return {
            "id": "choose_valid_formal_writeback_decision",
            "label": "Choose a valid formal writeback decision",
            "description": "Decision must be approve, defer, revise, or reject.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "obtain_human_formal_writeback_approval",
        "label": "Wait for formal writeback approval",
        "description": "Formal writeback remains disabled until a human records approve with reviewer and note.",
    }


def write_auto_mode_formal_writeback_approval_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_APPROVAL_PATH,
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
        "# Auto Mode Formal Writeback Approval",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 决策：`{report['approval']['decision']}`",
        f"- 审批生效：{str(report['approved']).lower()}",
        f"- 允许后续正式写回执行预检：{str(report['can_enter_formal_writeback_execution_preflight']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Approved Scope"])
    if report["approved_scope"]:
        for item in report["approved_scope"]:
            lines.append(f"- `{item['category']}`: {item['approval_status']}")
    else:
        lines.append("- 无；等待可生效审批。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"

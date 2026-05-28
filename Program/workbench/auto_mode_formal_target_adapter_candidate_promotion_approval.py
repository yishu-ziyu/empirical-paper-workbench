from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_approval.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_target_adapter_candidate_promotion_preflight.json")
DEFAULT_APPROVAL_PATH = Path("Results/json/auto_mode_formal_target_adapter_candidate_promotion_approval.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_candidate_promotion_approval.md")
VALID_DECISIONS = {"approve", "defer", "revise", "reject"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_candidate_promotion_approval(
    candidate_promotion_preflight: dict[str, Any],
    decision: str = "defer",
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(candidate_promotion_preflight)
    approval_reasons = build_approval_blocking_reasons(decision, reviewer, note)
    blocking_reasons = preflight_reasons + approval_reasons
    status = build_status(decision, preflight_reasons, approval_reasons)
    approved = status == "approved_for_verified_candidate_promotion_execution_preflight"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": candidate_promotion_preflight.get("topic", ""),
        "source_paths": {
            "candidate_promotion_preflight": source_paths.get(
                "candidate_promotion_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "status": status,
        "approved": approved,
        "verified_candidate_promotion_allowed": approved,
        "can_enter_verified_candidate_promotion_execution_preflight": approved,
        "candidate_targets_promoted": False,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_preflight": build_source_preflight(candidate_promotion_preflight),
        "approval": build_approval(decision, reviewer, note, approved),
        "approved_promotion_plan": build_approved_promotion_plan(candidate_promotion_preflight) if approved else [],
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_preflight_blocking_reasons(candidate_promotion_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if candidate_promotion_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("candidate_promotion_preflight_missing_or_invalid_schema")
    if candidate_promotion_preflight.get("status") != "ready_for_verified_candidate_promotion_review":
        reasons.append("candidate_promotion_preflight_not_ready")
    if candidate_promotion_preflight.get("can_request_verified_candidate_promotion_approval") is not True:
        reasons.append("candidate_promotion_preflight_cannot_request_approval")
    if candidate_promotion_preflight.get("requires_separate_promotion_approval") is not True:
        reasons.append("candidate_promotion_preflight_missing_separate_approval_requirement")
    if candidate_promotion_preflight.get("requires_explicit_promotion_execute_command") is not True:
        reasons.append("candidate_promotion_preflight_missing_explicit_execute_requirement")
    if candidate_promotion_preflight.get("candidate_targets_promoted") is True:
        reasons.append("candidate_promotion_preflight_already_promoted_candidates")
    if candidate_promotion_preflight.get("formal_target_adapters_executed") is True:
        reasons.append("candidate_promotion_preflight_already_executed_target_adapters")
    if candidate_promotion_preflight.get("formal_writeback_executed") is True:
        reasons.append("candidate_promotion_preflight_already_executed_formal_writeback")
    if candidate_promotion_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("candidate_promotion_preflight_already_wrote_formal_state")
    if candidate_promotion_preflight.get("can_write_product_state") is True:
        reasons.append("candidate_promotion_preflight_allows_product_state_write")
    if candidate_promotion_preflight.get("blocking_reasons"):
        reasons.append("candidate_promotion_preflight_has_blocking_reasons")
    if not candidate_promotion_preflight.get("promotion_plan"):
        reasons.append("candidate_promotion_plan_missing")
    for flag, value in candidate_promotion_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"candidate_promotion_preflight_boundary_violation:{flag}")
    return reasons


def build_approval_blocking_reasons(decision: str, reviewer: str, note: str) -> list[str]:
    if decision not in VALID_DECISIONS:
        return ["candidate_promotion_decision_invalid"]
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
        return "blocked_by_candidate_promotion_preflight"
    if "candidate_promotion_decision_invalid" in approval_reasons:
        return "blocked_by_candidate_promotion_approval_decision"
    if decision == "approve" and approval_reasons:
        return "blocked_by_candidate_promotion_approval_metadata"
    if decision == "approve":
        return "approved_for_verified_candidate_promotion_execution_preflight"
    if decision == "revise":
        return "verified_candidate_promotion_needs_revision"
    if decision == "reject":
        return "verified_candidate_promotion_rejected"
    return "waiting_for_human_verified_candidate_promotion_approval"


def build_source_preflight(candidate_promotion_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": candidate_promotion_preflight.get("schema_version", ""),
        "status": candidate_promotion_preflight.get("status", ""),
        "can_request_verified_candidate_promotion_approval": candidate_promotion_preflight.get(
            "can_request_verified_candidate_promotion_approval"
        )
        is True,
        "requires_separate_promotion_approval": candidate_promotion_preflight.get(
            "requires_separate_promotion_approval"
        )
        is True,
        "requires_explicit_promotion_execute_command": candidate_promotion_preflight.get(
            "requires_explicit_promotion_execute_command"
        )
        is True,
        "candidate_targets_promoted": candidate_promotion_preflight.get("candidate_targets_promoted") is True,
        "formal_writeback_executed": candidate_promotion_preflight.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": candidate_promotion_preflight.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": candidate_promotion_preflight.get("can_write_product_state") is True,
        "promotion_plan_count": len(candidate_promotion_preflight.get("promotion_plan", [])),
        "blocking_reasons": candidate_promotion_preflight.get("blocking_reasons", []),
    }


def build_approval(decision: str, reviewer: str, note: str, approved: bool) -> dict[str, Any]:
    return {
        "decision": decision,
        "reviewer": reviewer,
        "note": note,
        "approved": approved,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_approved_promotion_plan(candidate_promotion_preflight: dict[str, Any]) -> list[dict[str, Any]]:
    approved_plan = []
    for item in candidate_promotion_preflight.get("promotion_plan", []):
        approved_plan.append(
            {
                "promotion_id": item.get("promotion_id", ""),
                "operation_id": item.get("operation_id", ""),
                "writeback_target_group": item.get("writeback_target_group", ""),
                "candidate_path": item.get("candidate_path", ""),
                "candidate_bytes": item.get("candidate_bytes"),
                "candidate_sha256": item.get("candidate_sha256", ""),
                "formal_target_path": item.get("formal_target_path", ""),
                "approval_status": "approved_for_verified_candidate_promotion_execution_preflight",
                "requires_explicit_promotion_execute_command": True,
                "promoted_by_this_command": False,
                "this_command_wrote_formal_state": False,
            }
        )
    return approved_plan


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
        "executed_target_adapters": False,
        "wrote_formal_state": False,
        "created_or_repaired_candidate_targets": False,
        "promoted_candidate_targets": False,
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "approved_for_verified_candidate_promotion_execution_preflight":
        return {
            "id": "run_verified_candidate_promotion_execution_preflight",
            "label": "Run verified candidate promotion execution preflight",
            "description": "Candidate promotion approval is recorded; a later execution preflight must still guard target writes.",
        }
    if status == "blocked_by_candidate_promotion_preflight":
        return {
            "id": "resolve_candidate_promotion_preflight_blockers",
            "label": "Resolve candidate promotion preflight blockers",
            "description": "The approval ledger cannot become effective until P7-S is ready.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_candidate_promotion_approval_metadata":
        return {
            "id": "record_candidate_promotion_reviewer_and_note",
            "label": "Record reviewer and approval note",
            "description": "Candidate promotion approval requires a traceable reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "verified_candidate_promotion_needs_revision":
        return {
            "id": "revise_verified_candidate_promotion_inputs",
            "label": "Revise verified candidate promotion inputs",
            "description": "The human decision requested revision before candidate promotion.",
        }
    if status == "verified_candidate_promotion_rejected":
        return {
            "id": "stop_verified_candidate_promotion",
            "label": "Stop verified candidate promotion",
            "description": "The human decision rejected candidate promotion for this package.",
        }
    if status == "blocked_by_candidate_promotion_approval_decision":
        return {
            "id": "choose_valid_candidate_promotion_decision",
            "label": "Choose a valid candidate promotion decision",
            "description": "Decision must be approve, defer, revise, or reject.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "obtain_human_verified_candidate_promotion_approval",
        "label": "Wait for verified candidate promotion approval",
        "description": "Candidate promotion remains disabled until a human records approve with reviewer and note.",
    }


def write_auto_mode_formal_target_adapter_candidate_promotion_approval_outputs(
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
        "# Auto Mode Formal Target Adapter Candidate Promotion Approval",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 决策：`{report['approval']['decision']}`",
        f"- 审批生效：{str(report['approved']).lower()}",
        f"- 允许后续 candidate promotion execution preflight：{str(report['can_enter_verified_candidate_promotion_execution_preflight']).lower()}",
        f"- 已提升 candidate targets：{str(report['candidate_targets_promoted']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Approved Promotion Plan"])
    if report["approved_promotion_plan"]:
        for item in report["approved_promotion_plan"]:
            lines.append(f"- `{item['promotion_id']}`: {item['approval_status']}")
    else:
        lines.append("- 无；等待可生效审批。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"

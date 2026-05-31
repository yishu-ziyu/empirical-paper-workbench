from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.v1"
)
ENTRY_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_package_routed_next_gate_entry_preflight.v1"
ENTRY_SUCCESS_STATUS = "next_gate_routed_next_gate_entry_preflight_entered"
PREFLIGHT_SUCCESS_STATUS = "ready_for_routed_next_gate_entry_review"
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry.json"
)
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json")
DEFAULT_PREFLIGHT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md")
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.md"
)

GATE_ENTRY_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "allowed_actions": {"continue_formal_package_export_acceptance_cycle"},
        "next_command": "auto_mode_formal_package_export_acceptance_router",
        "entry_kind": "continue_export_acceptance_cycle",
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "allowed_actions": {"finalize_formal_package_delivery_review"},
        "next_command": "auto_mode_formal_package_delivery_completion_gate",
        "entry_kind": "delivery_completion",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
    project_root: Path,
    routed_next_gate_entry_preflight_entry: dict[str, Any],
    routed_next_gate_entry_preflight: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    entry_reasons = build_entry_blocking_reasons(routed_next_gate_entry_preflight_entry)
    preflight_reasons = (
        build_preflight_review_blocking_reasons(routed_next_gate_entry_preflight)
        if not entry_reasons
        else []
    )
    boundary_reasons = (
        build_boundary_blocking_reasons(
            routed_next_gate_entry_preflight_entry,
            routed_next_gate_entry_preflight,
        )
        if not entry_reasons and not preflight_reasons
        else []
    )
    contract_reasons = (
        build_contract_blocking_reasons(
            routed_next_gate_entry_preflight_entry,
            routed_next_gate_entry_preflight,
        )
        if not entry_reasons and not preflight_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(entry_reasons + preflight_reasons + boundary_reasons + contract_reasons)
    status = build_status(entry_reasons, preflight_reasons, boundary_reasons, contract_reasons)
    ready = status == "routed_next_gate_entry_preflight_entry_result_review_ready"
    plan = routed_next_gate_entry_preflight.get("next_gate_entry_plan", []) if ready else []
    route_type = routed_next_gate_entry_preflight.get("verified_route_type", "") if ready else ""
    routed_next_gate = routed_next_gate_entry_preflight.get("routed_next_gate", "") if ready else ""

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": routed_next_gate_entry_preflight_entry.get(
            "topic",
            routed_next_gate_entry_preflight.get("topic", ""),
        ),
        "source_paths": {
            "routed_next_gate_entry_preflight_entry": source_paths.get(
                "routed_next_gate_entry_preflight_entry",
                str(DEFAULT_ENTRY_PATH),
            ),
            "routed_next_gate_entry_preflight": source_paths.get(
                "routed_next_gate_entry_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "source_status": routed_next_gate_entry_preflight_entry.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "routed_next_gate_entry_preflight_status": (
            routed_next_gate_entry_preflight.get("status", "") if ready else ""
        ),
        "routed_next_gate_entry_preflight_entry_result_reviewed": ready,
        "can_continue_to_explicit_routed_next_gate_entry": ready,
        "can_request_routed_next_gate_entry": (
            routed_next_gate_entry_preflight.get("can_request_routed_next_gate_entry") is True
            if ready
            else False
        ),
        "requires_explicit_next_gate_entry_command": (
            routed_next_gate_entry_preflight.get("requires_explicit_next_gate_entry_command") is True
            if ready
            else False
        ),
        "next_gate_entry_plan_count": len(plan),
        "next_gate_entry_plan": plan,
        "explicit_routed_next_gate_entry_input_records": (
            build_explicit_routed_next_gate_entry_input_records(routed_next_gate_entry_preflight)
            if ready
            else []
        ),
        "explicit_routed_next_gate_entry_executed": False,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "next_gate_command_executed": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_preflight_entry": build_source_preflight_entry_summary(
            routed_next_gate_entry_preflight_entry
        ),
        "source_preflight": build_source_preflight_summary(routed_next_gate_entry_preflight),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type, routed_next_gate),
    }


def build_entry_blocking_reasons(routed_next_gate_entry_preflight_entry: dict[str, Any]) -> list[str]:
    reasons = []
    if routed_next_gate_entry_preflight_entry.get("schema_version") != ENTRY_SCHEMA_VERSION:
        reasons.append("routed_next_gate_entry_preflight_entry_missing_or_invalid_schema")
    if routed_next_gate_entry_preflight_entry.get("status") != ENTRY_SUCCESS_STATUS:
        reasons.append("routed_next_gate_entry_preflight_entry_not_entered")
    if routed_next_gate_entry_preflight_entry.get("can_enter_routed_next_gate_entry_preflight") is not True:
        reasons.append("routed_next_gate_entry_preflight_entry_did_not_allow_preflight")
    if (
        routed_next_gate_entry_preflight_entry.get("routed_next_gate_entry_preflight_entry_command_executed")
        is not True
    ):
        reasons.append("routed_next_gate_entry_preflight_entry_command_not_executed")
    if (
        routed_next_gate_entry_preflight_entry.get("this_command_ran_routed_next_gate_entry_preflight")
        is not True
    ):
        reasons.append("preflight_entry_did_not_run_routed_next_gate_entry_preflight")
    if routed_next_gate_entry_preflight_entry.get("routed_next_gate_entry_preflight_returncode") != 0:
        reasons.append("routed_next_gate_entry_preflight_returncode_not_zero")
    if routed_next_gate_entry_preflight_entry.get("routed_next_gate_entry_preflight_status") != (
        PREFLIGHT_SUCCESS_STATUS
    ):
        reasons.append("routed_next_gate_entry_preflight_status_not_ready")
    if routed_next_gate_entry_preflight_entry.get("can_request_routed_next_gate_entry") is not True:
        reasons.append("preflight_entry_cannot_request_routed_next_gate_entry")
    if routed_next_gate_entry_preflight_entry.get("requires_explicit_next_gate_entry_command") is not True:
        reasons.append("preflight_entry_missing_explicit_next_gate_entry_requirement")
    if not routed_next_gate_entry_preflight_entry.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if not routed_next_gate_entry_preflight_entry.get("routed_next_gate"):
        reasons.append("routed_next_gate_missing")
    if not routed_next_gate_entry_preflight_entry.get("next_gate_entry_plan"):
        reasons.append("preflight_entry_next_gate_entry_plan_missing")
    for field in [
        "routed_next_gate_entry_preflight_report_path",
        "routed_next_gate_entry_preflight_review_path",
        "routed_next_gate_entry_preflight_status",
    ]:
        if not routed_next_gate_entry_preflight_entry.get(field):
            reasons.append(f"{field}_missing")
    if routed_next_gate_entry_preflight_entry.get("blocking_reasons"):
        reasons.append("source_preflight_entry_has_blocking_reasons")
    return dedupe(reasons)


def build_preflight_review_blocking_reasons(routed_next_gate_entry_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if routed_next_gate_entry_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("routed_next_gate_entry_preflight_missing_or_invalid_schema")
    if routed_next_gate_entry_preflight.get("status") != PREFLIGHT_SUCCESS_STATUS:
        reasons.append("routed_next_gate_entry_preflight_not_ready")
    if routed_next_gate_entry_preflight.get("can_request_routed_next_gate_entry") is not True:
        reasons.append("routed_next_gate_entry_preflight_cannot_request_entry")
    if routed_next_gate_entry_preflight.get("requires_explicit_next_gate_entry_command") is not True:
        reasons.append("routed_next_gate_entry_preflight_missing_explicit_command_requirement")
    if not routed_next_gate_entry_preflight.get("verified_route_type"):
        reasons.append("routed_next_gate_entry_preflight_verified_route_type_missing")
    if not routed_next_gate_entry_preflight.get("routed_next_gate"):
        reasons.append("routed_next_gate_entry_preflight_routed_next_gate_missing")
    if routed_next_gate_entry_preflight.get("blocking_reasons"):
        reasons.append("source_preflight_has_blocking_reasons")
    if not routed_next_gate_entry_preflight.get("next_gate_entry_plan"):
        reasons.append("routed_next_gate_entry_plan_missing")
    return dedupe(reasons)


def build_boundary_blocking_reasons(
    routed_next_gate_entry_preflight_entry: dict[str, Any],
    routed_next_gate_entry_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    entry_fields = {
        "next_gate_entered": "routed_next_gate_entry_preflight_entry_entered_next_gate",
        "this_command_entered_next_gate": "routed_next_gate_entry_preflight_entry_entered_next_gate",
        "export_or_acceptance_executed": "routed_next_gate_entry_preflight_entry_executed_export_or_acceptance",
        "rendered_pdf": "routed_next_gate_entry_preflight_entry_rendered_pdf",
        "rendered_docx": "routed_next_gate_entry_preflight_entry_rendered_docx",
        "package_manifest_generated": "routed_next_gate_entry_preflight_entry_generated_package_manifest",
        "manual_acceptance_performed": "routed_next_gate_entry_preflight_entry_performed_manual_acceptance",
        "formal_writeback_executed": "routed_next_gate_entry_preflight_entry_executed_formal_writeback",
        "this_command_wrote_formal_state": "routed_next_gate_entry_preflight_entry_wrote_formal_state",
        "can_write_product_state": "routed_next_gate_entry_preflight_entry_allows_product_state_write",
    }
    preflight_fields = {
        "next_gate_entered": "routed_next_gate_entry_preflight_entered_next_gate",
        "this_command_entered_next_gate": "routed_next_gate_entry_preflight_entered_next_gate",
        "export_or_acceptance_executed": "routed_next_gate_entry_preflight_executed_export_or_acceptance",
        "formal_writeback_executed": "routed_next_gate_entry_preflight_executed_formal_writeback",
        "this_command_wrote_formal_state": "routed_next_gate_entry_preflight_wrote_formal_state",
        "can_write_product_state": "routed_next_gate_entry_preflight_allows_product_state_write",
    }
    for field, reason in entry_fields.items():
        if routed_next_gate_entry_preflight_entry.get(field) is True:
            reasons.append(reason)
    for field, reason in preflight_fields.items():
        if routed_next_gate_entry_preflight.get(field) is True:
            reasons.append(reason)
    for flag, value in routed_next_gate_entry_preflight_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"routed_next_gate_entry_preflight_entry_boundary_violation:{flag}")
    for flag, value in routed_next_gate_entry_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"routed_next_gate_entry_preflight_boundary_violation:{flag}")
    return dedupe(reasons)


def build_contract_blocking_reasons(
    routed_next_gate_entry_preflight_entry: dict[str, Any],
    routed_next_gate_entry_preflight: dict[str, Any],
) -> list[str]:
    route_type = routed_next_gate_entry_preflight_entry.get("verified_route_type", "unknown")
    result = routed_next_gate_entry_preflight_entry.get("routed_next_gate_entry_preflight_result", {})
    summary = result.get("routed_next_gate_entry_preflight_report_summary", {})
    reasons = []
    if routed_next_gate_entry_preflight_entry.get("routed_next_gate_entry_preflight_report_path") != str(
        DEFAULT_PREFLIGHT_PATH
    ):
        reasons.append(f"routed_next_gate_entry_preflight_report_path_mismatch:{route_type}")
    if routed_next_gate_entry_preflight_entry.get("routed_next_gate_entry_preflight_review_path") != str(
        DEFAULT_PREFLIGHT_REVIEW_PATH
    ):
        reasons.append(f"routed_next_gate_entry_preflight_review_path_mismatch:{route_type}")
    if result.get("report_path") != str(DEFAULT_PREFLIGHT_PATH):
        reasons.append(f"routed_next_gate_entry_preflight_result_report_path_mismatch:{route_type}")
    if result.get("review_path") != str(DEFAULT_PREFLIGHT_REVIEW_PATH):
        reasons.append(f"routed_next_gate_entry_preflight_result_review_path_mismatch:{route_type}")
    if result.get("returncode") != routed_next_gate_entry_preflight_entry.get(
        "routed_next_gate_entry_preflight_returncode"
    ):
        reasons.append(f"routed_next_gate_entry_preflight_result_returncode_mismatch:{route_type}")
    if result.get("status") != routed_next_gate_entry_preflight.get("status"):
        reasons.append(f"routed_next_gate_entry_preflight_result_status_mismatch:{route_type}")
    if routed_next_gate_entry_preflight_entry.get("routed_next_gate_entry_preflight_status") != (
        routed_next_gate_entry_preflight.get("status")
    ):
        reasons.append(f"routed_next_gate_entry_preflight_status_mismatch:{route_type}")
    for field in [
        "verified_route_type",
        "routed_next_gate",
        "can_request_routed_next_gate_entry",
        "requires_explicit_next_gate_entry_command",
        "next_gate_entry_plan",
    ]:
        if routed_next_gate_entry_preflight_entry.get(field) != routed_next_gate_entry_preflight.get(field):
            reasons.append(f"routed_next_gate_entry_preflight_{field}_mismatch:{route_type}")
    if summary.get("schema_version") != routed_next_gate_entry_preflight.get("schema_version"):
        reasons.append(f"routed_next_gate_entry_preflight_summary_schema_mismatch:{route_type}")
    if summary.get("status") != routed_next_gate_entry_preflight.get("status"):
        reasons.append(f"routed_next_gate_entry_preflight_summary_status_mismatch:{route_type}")
    if summary.get("verified_route_type") != routed_next_gate_entry_preflight.get("verified_route_type"):
        reasons.append(f"routed_next_gate_entry_preflight_summary_route_mismatch:{route_type}")
    if summary.get("routed_next_gate") != routed_next_gate_entry_preflight.get("routed_next_gate"):
        reasons.append(f"routed_next_gate_entry_preflight_summary_routed_next_gate_mismatch:{route_type}")
    if summary.get("can_request_routed_next_gate_entry") != (
        routed_next_gate_entry_preflight.get("can_request_routed_next_gate_entry") is True
    ):
        reasons.append(f"routed_next_gate_entry_preflight_summary_can_request_mismatch:{route_type}")
    if summary.get("next_gate_entry_plan_count") != len(
        routed_next_gate_entry_preflight.get("next_gate_entry_plan", []) or []
    ):
        reasons.append(f"routed_next_gate_entry_preflight_summary_plan_count_mismatch:{route_type}")
    if summary.get("blocking_reasons", []) != routed_next_gate_entry_preflight.get("blocking_reasons", []):
        reasons.append(f"routed_next_gate_entry_preflight_summary_blockers_mismatch:{route_type}")
    reasons.extend(build_entry_plan_contract_blocking_reasons(routed_next_gate_entry_preflight))
    return dedupe(reasons)


def build_entry_plan_contract_blocking_reasons(
    routed_next_gate_entry_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    plan = routed_next_gate_entry_preflight.get("next_gate_entry_plan", [])
    if len(plan) != 1:
        return ["routed_next_gate_entry_plan_not_single"]
    item = plan[0]
    route_type = item.get("verified_route_type", "unknown")
    routed_next_gate = routed_next_gate_entry_preflight.get("routed_next_gate", "")
    contract = GATE_ENTRY_CONTRACTS.get(routed_next_gate)
    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{routed_next_gate}")
    else:
        if route_type not in contract["allowed_route_types"]:
            reasons.append(f"routed_next_gate_entry_route_type_not_allowed:{route_type}")
        if item.get("next_gate_action") not in contract["allowed_actions"]:
            reasons.append(f"routed_next_gate_entry_action_not_allowed:{routed_next_gate}")
        if item.get("next_command") != contract["next_command"]:
            reasons.append(f"routed_next_gate_entry_next_command_mismatch:{route_type}")
        if item.get("entry_kind") != contract["entry_kind"]:
            reasons.append(f"routed_next_gate_entry_kind_mismatch:{route_type}")
    if item.get("gate_id") != routed_next_gate:
        reasons.append(f"routed_next_gate_entry_gate_mismatch:{routed_next_gate}")
    if route_type != routed_next_gate_entry_preflight.get("verified_route_type", ""):
        reasons.append(f"routed_next_gate_entry_route_type_mismatch:{route_type}")
    if item.get("entry_id") != f"routed_next_gate_entry::{routed_next_gate}::{route_type}":
        reasons.append(f"routed_next_gate_entry_id_mismatch:{route_type}")
    if not item.get("source_route_id"):
        reasons.append(f"routed_next_gate_entry_source_route_missing:{route_type}")
    if not item.get("next_command"):
        reasons.append(f"routed_next_gate_entry_next_command_missing:{route_type}")
    if item.get("entry_status") != "pending_explicit_next_gate_entry_command":
        reasons.append(f"routed_next_gate_entry_not_pending:{route_type}")
    if item.get("requires_explicit_next_gate_entry_command") is not True:
        reasons.append(f"routed_next_gate_entry_missing_explicit_command_requirement:{route_type}")
    if item.get("will_enter_next_gate_by_this_command") is True:
        reasons.append(f"routed_next_gate_entry_marked_enter_by_this_command:{route_type}")
    if item.get("will_execute_export_or_acceptance_by_this_command") is True:
        reasons.append(f"routed_next_gate_entry_marked_export_or_acceptance:{route_type}")
    if item.get("will_write_product_state_by_this_command") is True:
        reasons.append(f"routed_next_gate_entry_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_status(
    entry_reasons: list[str],
    preflight_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if entry_reasons:
        return "blocked_by_routed_next_gate_entry_preflight_entry"
    if preflight_reasons:
        return "blocked_by_routed_next_gate_entry_preflight_review"
    if boundary_reasons:
        return "blocked_by_routed_next_gate_entry_preflight_entry_result_boundary"
    if contract_reasons:
        return "blocked_by_routed_next_gate_entry_preflight_entry_result_contract"
    return "routed_next_gate_entry_preflight_entry_result_review_ready"


def build_explicit_routed_next_gate_entry_input_records(
    routed_next_gate_entry_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = routed_next_gate_entry_preflight["verified_route_type"]
    routed_next_gate = routed_next_gate_entry_preflight["routed_next_gate"]
    entry_plan = routed_next_gate_entry_preflight["next_gate_entry_plan"]
    return [
        {
            "record_id": f"explicit_routed_next_gate_entry_input::{routed_next_gate}::{route_type}",
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "routed_next_gate_entry_preflight_status": PREFLIGHT_SUCCESS_STATUS,
            "routed_next_gate_entry_preflight_report_path": str(DEFAULT_PREFLIGHT_PATH),
            "routed_next_gate_entry_preflight_review_path": str(DEFAULT_PREFLIGHT_REVIEW_PATH),
            "next_gate_entry_plan_count": len(entry_plan),
            "entry_ids": [item.get("entry_id", "") for item in entry_plan],
            "review_status": "routed_next_gate_entry_preflight_accepted_for_explicit_entry_gate",
            "can_continue_to_explicit_routed_next_gate_entry": True,
        }
    ]


def build_source_preflight_entry_summary(routed_next_gate_entry_preflight_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": routed_next_gate_entry_preflight_entry.get("schema_version", ""),
        "status": routed_next_gate_entry_preflight_entry.get("status", ""),
        "verified_route_type": routed_next_gate_entry_preflight_entry.get("verified_route_type", ""),
        "routed_next_gate": routed_next_gate_entry_preflight_entry.get("routed_next_gate", ""),
        "can_enter_routed_next_gate_entry_preflight": routed_next_gate_entry_preflight_entry.get(
            "can_enter_routed_next_gate_entry_preflight"
        )
        is True,
        "routed_next_gate_entry_preflight_entry_command_executed": routed_next_gate_entry_preflight_entry.get(
            "routed_next_gate_entry_preflight_entry_command_executed"
        )
        is True,
        "this_command_ran_routed_next_gate_entry_preflight": routed_next_gate_entry_preflight_entry.get(
            "this_command_ran_routed_next_gate_entry_preflight"
        )
        is True,
        "routed_next_gate_entry_preflight_status": routed_next_gate_entry_preflight_entry.get(
            "routed_next_gate_entry_preflight_status",
            "",
        ),
        "can_request_routed_next_gate_entry": routed_next_gate_entry_preflight_entry.get(
            "can_request_routed_next_gate_entry"
        )
        is True,
        "next_gate_entry_plan_count": len(
            routed_next_gate_entry_preflight_entry.get("next_gate_entry_plan", []) or []
        ),
        "blocking_reasons": routed_next_gate_entry_preflight_entry.get("blocking_reasons", []),
        "boundary_flags": routed_next_gate_entry_preflight_entry.get("boundary_flags", {}),
    }


def build_source_preflight_summary(routed_next_gate_entry_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": routed_next_gate_entry_preflight.get("schema_version", ""),
        "status": routed_next_gate_entry_preflight.get("status", ""),
        "verified_route_type": routed_next_gate_entry_preflight.get("verified_route_type", ""),
        "routed_next_gate": routed_next_gate_entry_preflight.get("routed_next_gate", ""),
        "can_request_routed_next_gate_entry": routed_next_gate_entry_preflight.get(
            "can_request_routed_next_gate_entry"
        )
        is True,
        "requires_explicit_next_gate_entry_command": routed_next_gate_entry_preflight.get(
            "requires_explicit_next_gate_entry_command"
        )
        is True,
        "next_gate_entry_plan_count": len(
            routed_next_gate_entry_preflight.get("next_gate_entry_plan", []) or []
        ),
        "blocking_reasons": routed_next_gate_entry_preflight.get("blocking_reasons", []),
        "boundary_flags": routed_next_gate_entry_preflight.get("boundary_flags", {}),
    }


def build_boundary_flags() -> dict[str, bool]:
    return {
        "modified_formal_manuscript": False,
        "modified_formal_bibliography": False,
        "modified_project_bibliography": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "modified_product_state": False,
        "reran_models": False,
        "modified_statistical_execution_artifacts": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "generated_package_manifest": False,
        "performed_manual_acceptance": False,
        "entered_next_gate": False,
        "ran_next_gate_command": False,
        "wrote_formal_state": False,
        "executed_selected_route": False,
        "exported_or_accepted_formal_package": False,
        "ran_routed_next_gate_entry_preflight": False,
        "entered_explicit_routed_next_gate_entry": False,
    }


def build_next_action(
    status: str,
    blocking_reasons: list[str],
    route_type: str,
    routed_next_gate: str,
) -> dict[str, Any]:
    if status == "routed_next_gate_entry_preflight_entry_result_review_ready":
        return {
            "id": "run_explicit_routed_next_gate_entry_gate",
            "label": "Run explicit routed next-gate entry gate",
            "description": f"The `{route_type}` route may continue to explicit entry for `{routed_next_gate}`.",
        }
    if status == "blocked_by_routed_next_gate_entry_preflight_review":
        return {
            "id": "repair_routed_next_gate_entry_preflight_output",
            "label": "Repair routed next-gate entry preflight output",
            "description": "The existing preflight output must be ready before explicit entry review.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_preflight_entry_result_boundary":
        return {
            "id": "resolve_routed_next_gate_entry_preflight_entry_result_boundary",
            "label": "Resolve routed next-gate entry preflight entry result boundary",
            "description": "P7-BA cannot consume inputs that already entered gates or wrote formal/product state.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_preflight_entry_result_contract":
        return {
            "id": "repair_routed_next_gate_entry_preflight_entry_result_contract",
            "label": "Repair routed next-gate entry preflight entry result contract",
            "description": "P7-AZ entry and the existing preflight output must agree before explicit entry.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_routed_next_gate_entry_preflight_entry_blockers",
        "label": "Resolve P7-AZ blockers",
        "description": "P7-AZ must prove that routed next-gate entry preflight ran successfully.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_RESULT_REVIEW_PATH,
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
        "# Auto Mode Formal Package Next Gate Routed Next Gate Entry Preflight Entry Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- preflight status：`{report['routed_next_gate_entry_preflight_status']}`",
        "- 已审阅 preflight entry result："
        f"{str(report['routed_next_gate_entry_preflight_entry_result_reviewed']).lower()}",
        "- 可继续 explicit routed next gate entry："
        f"{str(report['can_continue_to_explicit_routed_next_gate_entry']).lower()}",
        f"- 可请求进入 routed next gate：{str(report['can_request_routed_next_gate_entry']).lower()}",
        "- 需要 explicit next gate entry command："
        f"{str(report['requires_explicit_next_gate_entry_command']).lower()}",
        f"- next gate entry plan 数：{report['next_gate_entry_plan_count']}",
        "- explicit entry input records："
        f"{len(report['explicit_routed_next_gate_entry_input_records'])}",
        "- 已执行 explicit routed next gate entry："
        f"{str(report['explicit_routed_next_gate_entry_executed']).lower()}",
        f"- 本命令进入下一关：{str(report['this_command_entered_next_gate']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["explicit_routed_next_gate_entry_input_records"]:
        lines.extend(["", "## Explicit Routed Next Gate Entry Input Records"])
        for record in report["explicit_routed_next_gate_entry_input_records"]:
            lines.append(f"- `{record['record_id']}`")
            lines.append(f"- status：`{record['review_status']}`")
            lines.append(f"- entry ids：{', '.join(record['entry_ids'])}")
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

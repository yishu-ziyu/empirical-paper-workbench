from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_review.v1"
)
EXECUTE_GATE_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_gate.v1"
)
SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_selected_route_execution_preflight.v1"
)
DEFAULT_EXECUTE_GATE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_gate.json"
)
DEFAULT_SELECTED_ROUTE_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
)
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_review.md"
)

EXPORT_SUCCESS_STATUS = "manifested_routed_next_gate_result_continuation_executed"
TERMINAL_SUCCESS_STATUS = "manifested_routed_next_gate_terminal_continuation_recorded"
READY_STATUS = "manifested_routed_next_gate_result_continuation_execute_result_review_ready"
SELECTED_ROUTE_READY_STATUS = "ready_for_selected_formal_package_route_execution_review"
TERMINAL_READY_STATUS = "terminal_delivery_completion_ready_for_product_review"

CONTINUATION_RESULT_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "continuation_report_path": str(DEFAULT_SELECTED_ROUTE_PREFLIGHT_PATH),
        "continuation_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
        "success_status": SELECTED_ROUTE_READY_STATUS,
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "continuation_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
        "continuation_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
        "success_status": TERMINAL_READY_STATUS,
    },
}

SELECTED_ROUTE_EXECUTION_CONTRACTS = {
    "pdf_export": {
        "routed_action": "formal_pdf_export_preflight",
        "next_command": "formal_pdf_export_execute",
        "planned_outputs": ["Submissions/formal_package/paper.pdf"],
    },
    "docx_export": {
        "routed_action": "formal_docx_export_preflight",
        "next_command": "formal_docx_export_execute",
        "planned_outputs": ["Submissions/formal_package/paper.docx"],
    },
    "package_manifest": {
        "routed_action": "formal_submission_package_manifest_preflight",
        "next_command": "formal_submission_package_manifest_execute",
        "planned_outputs": ["Submissions/formal_package/manifest.json"],
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
    project_root: Path,
    continuation_execute_gate: dict[str, Any],
    selected_route_execution_preflight: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    execute_reasons = build_execute_gate_blocking_reasons(continuation_execute_gate)
    contract_reasons = (
        build_execute_result_contract_blocking_reasons(continuation_execute_gate)
        if not execute_reasons
        else []
    )
    boundary_reasons = (
        build_boundary_blocking_reasons(
            continuation_execute_gate,
            selected_route_execution_preflight,
        )
        if not execute_reasons and not contract_reasons
        else []
    )
    output_reasons = (
        build_continuation_output_blocking_reasons(
            continuation_execute_gate,
            selected_route_execution_preflight,
        )
        if not execute_reasons and not contract_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(
        execute_reasons + contract_reasons + boundary_reasons + output_reasons
    )
    status = build_status(execute_reasons, contract_reasons, boundary_reasons, output_reasons)
    ready = status == READY_STATUS
    is_terminal = continuation_execute_gate.get("status") == TERMINAL_SUCCESS_STATUS and ready
    is_export = continuation_execute_gate.get("status") == EXPORT_SUCCESS_STATUS and ready
    route_type = continuation_execute_gate.get("verified_route_type", "") if ready else ""
    routed_next_gate = continuation_execute_gate.get("routed_next_gate", "") if ready else ""
    continuation_status = continuation_execute_gate.get("continuation_status", "") if ready else ""

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": continuation_execute_gate.get(
            "topic",
            selected_route_execution_preflight.get("topic", ""),
        ),
        "source_paths": {
            "manifested_routed_next_gate_command_result_continuation_execute_gate": (
                source_paths.get(
                    "manifested_routed_next_gate_command_result_continuation_execute_gate",
                    str(DEFAULT_EXECUTE_GATE_PATH),
                )
            ),
            "selected_route_execution_preflight": source_paths.get(
                "selected_route_execution_preflight",
                continuation_execute_gate.get("continuation_report_path", ""),
            ),
        },
        "source_status": continuation_execute_gate.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "continuation_status": continuation_status,
        "selected_route_preflight_status": (
            selected_route_execution_preflight.get("status", "") if is_export else ""
        ),
        "terminal_status": continuation_status if is_terminal else "",
        "continuation_execute_result_reviewed": ready,
        "can_continue_after_manifested_routed_next_gate_result_continuation": ready,
        "continuation_executed": (
            continuation_execute_gate.get("continuation_executed") is True if is_export else False
        ),
        "terminal_continuation_recorded": (
            continuation_execute_gate.get("terminal_continuation_recorded") is True
            if is_terminal
            else False
        ),
        "this_command_ran_continuation": False,
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "selected_route_execution_preflight_records": (
            build_selected_route_execution_preflight_records(
                continuation_execute_gate,
                selected_route_execution_preflight,
            )
            if is_export
            else []
        ),
        "terminal_continuation_records": (
            build_terminal_continuation_records(continuation_execute_gate) if is_terminal else []
        ),
        "blocking_reasons": blocking_reasons,
        "source_execute_gate": build_source_execute_gate_summary(continuation_execute_gate),
        "source_selected_route_preflight": build_source_selected_route_preflight_summary(
            selected_route_execution_preflight
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type, is_terminal),
    }


def build_execute_gate_blocking_reasons(
    continuation_execute_gate: dict[str, Any],
) -> list[str]:
    reasons = []
    if continuation_execute_gate.get("schema_version") != EXECUTE_GATE_SCHEMA_VERSION:
        reasons.append(
            "manifested_routed_next_gate_result_continuation_execute_gate_missing_or_invalid_schema"
        )
    status = continuation_execute_gate.get("status", "")
    if status not in {EXPORT_SUCCESS_STATUS, TERMINAL_SUCCESS_STATUS}:
        reasons.append("manifested_routed_next_gate_result_continuation_execute_gate_not_completed")
    if not continuation_execute_gate.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if not continuation_execute_gate.get("routed_next_gate"):
        reasons.append("routed_next_gate_missing")
    if not continuation_execute_gate.get("continuation_status"):
        reasons.append("continuation_status_missing")
    if continuation_execute_gate.get("blocking_reasons"):
        reasons.append("source_execute_gate_has_blocking_reasons")

    if status == EXPORT_SUCCESS_STATUS:
        if continuation_execute_gate.get("continuation_executed") is not True:
            reasons.append("continuation_not_executed")
        if continuation_execute_gate.get("this_command_ran_continuation") is not True:
            reasons.append("source_execute_gate_did_not_run_continuation")
        if continuation_execute_gate.get("continuation_returncode") != 0:
            reasons.append("continuation_returncode_not_zero")
        if not continuation_execute_gate.get("continuation_command"):
            reasons.append("continuation_command_missing")
        if not continuation_execute_gate.get("continuation_report_path"):
            reasons.append("continuation_report_path_missing")
        if not continuation_execute_gate.get("continuation_review_path"):
            reasons.append("continuation_review_path_missing")
    return dedupe(reasons)


def build_execute_result_contract_blocking_reasons(
    continuation_execute_gate: dict[str, Any],
) -> list[str]:
    status = continuation_execute_gate.get("status", "")
    route_type = continuation_execute_gate.get("verified_route_type", "unknown")
    routed_next_gate = continuation_execute_gate.get("routed_next_gate", "")
    contract = CONTINUATION_RESULT_CONTRACTS.get(routed_next_gate)
    reasons = []
    if contract is None:
        return [f"routed_next_gate_unknown:{routed_next_gate}"]
    if route_type not in contract["allowed_route_types"]:
        reasons.append(f"continuation_route_type_not_allowed:{route_type}")

    if status == TERMINAL_SUCCESS_STATUS:
        if continuation_execute_gate.get("completion_terminal") is not True:
            reasons.append("terminal_continuation_completion_terminal_missing")
        if continuation_execute_gate.get("terminal_continuation_recorded") is not True:
            reasons.append("terminal_continuation_not_recorded")
        if continuation_execute_gate.get("this_command_recorded_terminal_continuation") is not True:
            reasons.append("terminal_continuation_not_recorded_by_source")
        if continuation_execute_gate.get("continuation_executed") is True:
            reasons.append("terminal_continuation_marked_executed")
        if continuation_execute_gate.get("this_command_ran_continuation") is True:
            reasons.append("terminal_continuation_ran_external_continuation")
        if continuation_execute_gate.get("continuation_command"):
            reasons.append("terminal_continuation_has_external_command")
        if continuation_execute_gate.get("continuation_returncode") is not None:
            reasons.append("terminal_continuation_has_returncode")
        if continuation_execute_gate.get("continuation_status") != TERMINAL_READY_STATUS:
            reasons.append("terminal_continuation_status_mismatch")
    elif status == EXPORT_SUCCESS_STATUS:
        if continuation_execute_gate.get("completion_terminal") is True:
            reasons.append(f"export_continuation_marked_terminal:{route_type}")
        if continuation_execute_gate.get("terminal_continuation_recorded") is True:
            reasons.append(f"export_continuation_has_terminal_record:{route_type}")
    return dedupe(reasons)


def build_boundary_blocking_reasons(
    continuation_execute_gate: dict[str, Any],
    selected_route_execution_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    for field, reason in [
        ("selected_route_executed", "execute_gate_selected_route_executed"),
        ("export_or_acceptance_executed", "execute_gate_export_or_acceptance_executed"),
        ("formal_writeback_executed", "execute_gate_formal_writeback"),
        ("this_command_wrote_formal_state", "execute_gate_wrote_formal_state"),
        ("can_write_product_state", "execute_gate_allows_product_state_write"),
    ]:
        if continuation_execute_gate.get(field) is True:
            reasons.append(reason)
    for flag, value in continuation_execute_gate.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"execute_gate_boundary_violation:{flag}")

    if continuation_execute_gate.get("status") == EXPORT_SUCCESS_STATUS:
        route_type = continuation_execute_gate.get("verified_route_type", "unknown")
        for field, reason in [
            ("selected_route_executed", "selected_route_preflight_already_executed"),
            ("export_or_acceptance_executed", "selected_route_preflight_export_or_acceptance_executed"),
            ("rendered_pdf", "selected_route_preflight_rendered_pdf"),
            ("rendered_docx", "selected_route_preflight_rendered_docx"),
            ("package_manifest_generated", "selected_route_preflight_generated_package_manifest"),
            ("manual_acceptance_performed", "selected_route_preflight_performed_manual_acceptance"),
            ("formal_writeback_executed", "selected_route_preflight_formal_writeback"),
            ("this_command_wrote_formal_state", "selected_route_preflight_wrote_formal_state"),
            ("can_write_product_state", "selected_route_preflight_allows_product_state_write"),
        ]:
            if selected_route_execution_preflight.get(field) is True:
                reasons.append(f"{reason}:{route_type}")
        for flag, value in selected_route_execution_preflight.get("boundary_flags", {}).items():
            if value is True:
                reasons.append(f"selected_route_preflight_boundary_violation:{flag}")
    return dedupe(reasons)


def build_continuation_output_blocking_reasons(
    continuation_execute_gate: dict[str, Any],
    selected_route_execution_preflight: dict[str, Any],
) -> list[str]:
    if continuation_execute_gate.get("status") == TERMINAL_SUCCESS_STATUS:
        return []

    route_type = continuation_execute_gate.get("verified_route_type", "unknown")
    routed_next_gate = continuation_execute_gate.get("routed_next_gate", "")
    contract = CONTINUATION_RESULT_CONTRACTS.get(routed_next_gate, {})
    route_contract = SELECTED_ROUTE_EXECUTION_CONTRACTS.get(route_type, {})
    reasons = []
    expected_report_path = contract.get("continuation_report_path", "")
    expected_review_path = contract.get("continuation_review_path", "")
    expected_status = contract.get("success_status", "")

    if continuation_execute_gate.get("continuation_report_path") != expected_report_path:
        reasons.append(f"continuation_report_path_mismatch:{route_type}")
    if continuation_execute_gate.get("continuation_review_path") != expected_review_path:
        reasons.append(f"continuation_review_path_mismatch:{route_type}")
    if continuation_execute_gate.get("continuation_status") != expected_status:
        reasons.append(f"continuation_status_mismatch:{route_type}")

    result = continuation_execute_gate.get("continuation_result", {})
    if result.get("returncode") not in (None, 0):
        reasons.append(f"continuation_result_returncode_not_zero:{route_type}")
    if result.get("status") and result.get("status") != continuation_execute_gate.get("continuation_status"):
        reasons.append(f"continuation_result_status_mismatch:{route_type}")
    if result.get("report_path") and result.get("report_path") != expected_report_path:
        reasons.append(f"continuation_result_report_path_mismatch:{route_type}")
    if result.get("review_path") and result.get("review_path") != expected_review_path:
        reasons.append(f"continuation_result_review_path_mismatch:{route_type}")

    summary = result.get("continuation_report_summary", {})
    if summary.get("schema_version") and summary.get("schema_version") != SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION:
        reasons.append(f"continuation_summary_schema_mismatch:{route_type}")
    if summary.get("status") and summary.get("status") != expected_status:
        reasons.append(f"continuation_summary_status_mismatch:{route_type}")
    if summary.get("can_request_selected_route_execution") is False:
        reasons.append(f"continuation_summary_cannot_request_selected_route_execution:{route_type}")
    if summary.get("selected_route_execution_plan_count") not in (None, 1):
        reasons.append(f"continuation_summary_selected_route_plan_count_mismatch:{route_type}")
    if summary.get("blocking_reasons"):
        reasons.append(f"continuation_summary_has_blocking_reasons:{route_type}")

    reasons.extend(
        build_selected_route_preflight_output_blocking_reasons(
            selected_route_execution_preflight,
            route_type,
            expected_status,
            route_contract,
        )
    )
    return dedupe(reasons)


def build_selected_route_preflight_output_blocking_reasons(
    selected_route_execution_preflight: dict[str, Any],
    route_type: str,
    expected_status: str,
    route_contract: dict[str, Any],
) -> list[str]:
    reasons = []
    if selected_route_execution_preflight.get("schema_version") != SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION:
        reasons.append(f"selected_route_preflight_missing_or_invalid_schema:{route_type}")
    if selected_route_execution_preflight.get("status") != expected_status:
        reasons.append(f"selected_route_preflight_status_not_ready:{route_type}")
    if selected_route_execution_preflight.get("can_request_selected_route_execution") is not True:
        reasons.append(f"selected_route_preflight_cannot_request_execution:{route_type}")
    if selected_route_execution_preflight.get("requires_explicit_route_execute_command") is not True:
        reasons.append(f"selected_route_preflight_missing_explicit_route_command:{route_type}")
    if selected_route_execution_preflight.get("blocking_reasons"):
        reasons.append(f"selected_route_preflight_has_blocking_reasons:{route_type}")

    plan = selected_route_execution_preflight.get("selected_route_execution_plan", [])
    if not isinstance(plan, list) or len(plan) != 1:
        reasons.append(f"selected_route_execution_plan_not_single:{route_type}")
    elif route_contract:
        item = plan[0]
        if item.get("route_type") != route_type:
            reasons.append(f"selected_route_plan_route_type_mismatch:{route_type}")
        if item.get("routed_action") != route_contract["routed_action"]:
            reasons.append(f"selected_route_plan_routed_action_mismatch:{route_type}")
        if item.get("next_command") != route_contract["next_command"]:
            reasons.append(f"selected_route_plan_next_command_mismatch:{route_type}")
        if item.get("planned_outputs") != route_contract["planned_outputs"]:
            reasons.append(f"selected_route_plan_outputs_mismatch:{route_type}")
        if item.get("execution_status") != "pending_explicit_route_execute_command":
            reasons.append(f"selected_route_plan_not_pending:{route_type}")
        if item.get("requires_explicit_route_execute_command") is not True:
            reasons.append(f"selected_route_plan_missing_explicit_command:{route_type}")
        if item.get("will_execute_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_execute:{route_type}")
        if item.get("will_render_pdf_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_render_pdf:{route_type}")
        if item.get("will_render_docx_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_render_docx:{route_type}")
        if item.get("will_generate_manifest_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_generate_manifest:{route_type}")
        if item.get("will_perform_manual_acceptance_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_manual_acceptance:{route_type}")
        if item.get("will_write_product_state_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_status(
    execute_reasons: list[str],
    contract_reasons: list[str],
    boundary_reasons: list[str],
    output_reasons: list[str],
) -> str:
    if execute_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_gate"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_contract"
    if boundary_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_boundary"
    if output_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_output"
    return READY_STATUS


def build_selected_route_execution_preflight_records(
    continuation_execute_gate: dict[str, Any],
    selected_route_execution_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = continuation_execute_gate.get("verified_route_type", "")
    routed_next_gate = continuation_execute_gate.get("routed_next_gate", "")
    plan_item = selected_route_execution_preflight.get("selected_route_execution_plan", [{}])[0]
    return [
        {
            "record_id": f"manifested_routed_continuation_result::{routed_next_gate}::{route_type}",
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "continuation_status": continuation_execute_gate.get("continuation_status", ""),
            "selected_route_preflight_status": selected_route_execution_preflight.get("status", ""),
            "selected_route_preflight_schema_version": selected_route_execution_preflight.get(
                "schema_version",
                "",
            ),
            "selected_route_preflight_report_path": continuation_execute_gate.get(
                "continuation_report_path",
                "",
            ),
            "selected_route_preflight_review_path": continuation_execute_gate.get(
                "continuation_review_path",
                "",
            ),
            "routed_action": plan_item.get("routed_action", ""),
            "next_command": plan_item.get("next_command", ""),
            "planned_outputs": plan_item.get("planned_outputs", []),
            "review_status": "selected_route_preflight_accepted_for_explicit_route_execution",
            "can_continue_to_selected_route_execution": True,
        }
    ]


def build_terminal_continuation_records(
    continuation_execute_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = continuation_execute_gate.get("verified_route_type", "")
    routed_next_gate = continuation_execute_gate.get("routed_next_gate", "")
    return [
        {
            "record_id": f"manifested_routed_terminal_continuation::{routed_next_gate}::{route_type}",
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "terminal_status": continuation_execute_gate.get("continuation_status", ""),
            "terminal_report_path": continuation_execute_gate.get("continuation_report_path", ""),
            "terminal_review_path": continuation_execute_gate.get("continuation_review_path", ""),
            "next_command": "product_review_preparation",
            "review_status": "terminal_continuation_accepted_for_product_review_preparation",
            "can_continue_to_product_review_preparation": True,
        }
    ]


def build_source_execute_gate_summary(
    continuation_execute_gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": continuation_execute_gate.get("schema_version", ""),
        "status": continuation_execute_gate.get("status", ""),
        "verified_route_type": continuation_execute_gate.get("verified_route_type", ""),
        "routed_next_gate": continuation_execute_gate.get("routed_next_gate", ""),
        "completion_terminal": continuation_execute_gate.get("completion_terminal") is True,
        "continuation_executed": continuation_execute_gate.get("continuation_executed") is True,
        "this_command_ran_continuation": (
            continuation_execute_gate.get("this_command_ran_continuation") is True
        ),
        "terminal_continuation_recorded": (
            continuation_execute_gate.get("terminal_continuation_recorded") is True
        ),
        "continuation_report_path": continuation_execute_gate.get("continuation_report_path", ""),
        "continuation_review_path": continuation_execute_gate.get("continuation_review_path", ""),
        "continuation_returncode": continuation_execute_gate.get("continuation_returncode"),
        "continuation_status": continuation_execute_gate.get("continuation_status", ""),
        "source_blocking_reasons": continuation_execute_gate.get("blocking_reasons", []),
        "boundary_flags": continuation_execute_gate.get("boundary_flags", {}),
    }


def build_source_selected_route_preflight_summary(
    selected_route_execution_preflight: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execution_preflight.get("schema_version", ""),
        "status": selected_route_execution_preflight.get("status", ""),
        "can_request_selected_route_execution": (
            selected_route_execution_preflight.get("can_request_selected_route_execution") is True
        ),
        "requires_explicit_route_execute_command": (
            selected_route_execution_preflight.get("requires_explicit_route_execute_command") is True
        ),
        "selected_route_execution_plan_count": len(
            selected_route_execution_preflight.get("selected_route_execution_plan", []) or []
        ),
        "selected_route_executed": selected_route_execution_preflight.get("selected_route_executed") is True,
        "export_or_acceptance_executed": (
            selected_route_execution_preflight.get("export_or_acceptance_executed") is True
        ),
        "blocking_reasons": selected_route_execution_preflight.get("blocking_reasons", []),
        "boundary_flags": selected_route_execution_preflight.get("boundary_flags", {}),
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
        "reviewed_manifested_routed_next_gate_result_continuation_execute_result": False,
    }


def build_next_action(
    status: str,
    blocking_reasons: list[str],
    route_type: str,
    is_terminal: bool,
) -> dict[str, Any]:
    if status == READY_STATUS and is_terminal:
        return {
            "id": "prepare_product_review_from_terminal_continuation",
            "label": "Prepare product review",
            "description": "Terminal continuation is accepted; product-state writeback remains separate.",
        }
    if status == READY_STATUS:
        next_command = SELECTED_ROUTE_EXECUTION_CONTRACTS.get(route_type, {}).get(
            "next_command",
            "selected_route_execute",
        )
        return {
            "id": next_command,
            "label": "Run explicit selected route execute command",
            "description": f"The `{route_type}` selected route preflight is accepted for explicit route execution.",
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_execute_gate":
        return {
            "id": "resolve_p7_bg_execute_gate_blockers",
            "label": "Resolve P7-BG execute gate blockers",
            "description": "P7-BG must complete or record continuation before result review can continue.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_contract":
        return {
            "id": "repair_manifested_routed_continuation_result_contract",
            "label": "Repair continuation result contract",
            "description": "The continuation route or terminal record does not match contract.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_boundary":
        return {
            "id": "remove_formal_action_from_continuation_result_review",
            "label": "Remove formal action from review input",
            "description": "P7-BH can only review results; execution and writeback belong to later explicit nodes.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "repair_manifested_routed_continuation_output",
        "label": "Repair continuation output",
        "description": "The selected-route preflight output must be ready and clean before continuing.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- continuation 状态：`{report['continuation_status']}`",
        f"- selected route preflight 状态：`{report['selected_route_preflight_status']}`",
        f"- terminal 状态：`{report['terminal_status']}`",
        "- 已审阅 continuation 执行结果："
        f"{str(report['continuation_execute_result_reviewed']).lower()}",
        "- 可继续 after manifested routed continuation："
        f"{str(report['can_continue_after_manifested_routed_next_gate_result_continuation']).lower()}",
        "- selected route preflight records："
        f"{len(report['selected_route_execution_preflight_records'])}",
        f"- terminal continuation records：{len(report['terminal_continuation_records'])}",
        f"- source 已运行 continuation：{str(report['continuation_executed']).lower()}",
        f"- source 已记录 terminal continuation：{str(report['terminal_continuation_recorded']).lower()}",
        f"- 本命令运行 continuation：{str(report['this_command_ran_continuation']).lower()}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if report["selected_route_execution_preflight_records"]:
        lines.extend(["", "## Selected Route Preflight Records"])
        for record in report["selected_route_execution_preflight_records"]:
            lines.append(
                "- "
                f"`{record['record_id']}`: {record['review_status']} "
                f"-> `{record['next_command']}`"
            )
    if report["terminal_continuation_records"]:
        lines.extend(["", "## Terminal Continuation Records"])
        for record in report["terminal_continuation_records"]:
            lines.append(
                "- "
                f"`{record['record_id']}`: {record['review_status']} "
                f"-> `{record['next_command']}`"
            )
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

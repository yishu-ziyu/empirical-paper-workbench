from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.auto_mode_formal_package_routed_next_gate_entry_preflight import (
    build_auto_mode_formal_package_routed_next_gate_entry_preflight,
)


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.v1"
ENTRY_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry.v1"
ROUTER_SCHEMA_VERSION = "p7.auto_mode_formal_package_verified_route_next_gate_router.v1"
ENTRY_SUCCESS_STATUS = "next_gate_verified_route_next_gate_router_entered"
ROUTER_SUCCESS_STATUS = "verified_route_next_gate_route_recorded"
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry.json"
)
DEFAULT_ROUTER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_next_gate_router.json")
DEFAULT_ROUTER_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_verified_route_next_gate_router.md")
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review.md"
)
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
    project_root: Path,
    verified_route_next_gate_router_entry: dict[str, Any],
    verified_route_next_gate_router: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    entry_reasons = build_entry_blocking_reasons(verified_route_next_gate_router_entry)
    router_reasons = (
        build_router_blocking_reasons(verified_route_next_gate_router)
        if not entry_reasons
        else []
    )
    contract_reasons = (
        build_entry_router_contract_blocking_reasons(
            verified_route_next_gate_router_entry,
            verified_route_next_gate_router,
        )
        if not entry_reasons and not router_reasons
        else []
    )
    boundary_reasons = (
        build_boundary_blocking_reasons(verified_route_next_gate_router)
        if not entry_reasons and not router_reasons and not contract_reasons
        else []
    )
    preflight_reasons = (
        build_preflight_probe_blocking_reasons(verified_route_next_gate_router)
        if not entry_reasons and not router_reasons and not contract_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(
        entry_reasons + router_reasons + contract_reasons + boundary_reasons + preflight_reasons
    )
    status = build_status(
        entry_reasons,
        router_reasons,
        contract_reasons,
        boundary_reasons,
        preflight_reasons,
    )
    ready = status == "verified_route_next_gate_router_entry_result_review_ready"
    route_type = verified_route_next_gate_router.get("verified_route_type", "") if ready else ""
    records = verified_route_next_gate_router.get("route_completion_records", []) if ready else []
    routed_next_gate = verified_route_next_gate_router.get("routed_next_gate", "") if ready else ""
    next_gate_route = verified_route_next_gate_router.get("next_gate_route", {}) if ready else {}

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": verified_route_next_gate_router_entry.get(
            "topic",
            verified_route_next_gate_router.get("topic", ""),
        ),
        "source_paths": {
            "verified_route_next_gate_router_entry": source_paths.get(
                "verified_route_next_gate_router_entry",
                str(DEFAULT_ENTRY_PATH),
            ),
            "verified_route_next_gate_router": source_paths.get(
                "verified_route_next_gate_router",
                str(DEFAULT_ROUTER_PATH),
            ),
        },
        "source_status": verified_route_next_gate_router_entry.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "verified_route_next_gate_router_status": (
            verified_route_next_gate_router.get("status", "") if ready else ""
        ),
        "verified_route_next_gate_router_entry_result_reviewed": ready,
        "can_continue_to_routed_next_gate_entry_preflight": ready,
        "next_gate_route_recorded": (
            verified_route_next_gate_router.get("next_gate_route_recorded") is True if ready else False
        ),
        "can_enter_routed_next_gate": (
            verified_route_next_gate_router.get("can_enter_routed_next_gate") is True if ready else False
        ),
        "routed_next_gate": routed_next_gate,
        "next_gate_route": next_gate_route,
        "route_completion_record_count": len(records),
        "route_completion_records": records,
        "routed_next_gate_entry_preflight_input_records": (
            build_routed_next_gate_entry_preflight_input_records(verified_route_next_gate_router)
            if ready
            else []
        ),
        "routed_next_gate_entry_preflight_executed": False,
        "this_command_ran_routed_next_gate_entry_preflight": False,
        "entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_router_entry": build_source_entry_summary(verified_route_next_gate_router_entry),
        "source_router": build_source_router_summary(verified_route_next_gate_router),
        "routed_next_gate_entry_preflight_probe": build_preflight_probe_summary(
            verified_route_next_gate_router
        )
        if not entry_reasons and not router_reasons and not contract_reasons
        else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type, routed_next_gate),
    }


def build_entry_blocking_reasons(verified_route_next_gate_router_entry: dict[str, Any]) -> list[str]:
    reasons = []
    route_type = verified_route_next_gate_router_entry.get("verified_route_type", "unknown")
    if verified_route_next_gate_router_entry.get("schema_version") != ENTRY_SCHEMA_VERSION:
        reasons.append("verified_route_next_gate_router_entry_missing_or_invalid_schema")
    if verified_route_next_gate_router_entry.get("status") != ENTRY_SUCCESS_STATUS:
        reasons.append("verified_route_next_gate_router_entry_not_entered")
    if verified_route_next_gate_router_entry.get("can_enter_verified_route_next_gate_router") is not True:
        reasons.append("router_entry_did_not_allow_verified_route_next_gate_router")
    if (
        verified_route_next_gate_router_entry.get("verified_route_next_gate_router_entry_command_executed")
        is not True
    ):
        reasons.append("verified_route_next_gate_router_entry_command_not_executed")
    if verified_route_next_gate_router_entry.get("this_command_ran_verified_route_next_gate_router") is not True:
        reasons.append("router_entry_did_not_run_verified_route_next_gate_router")
    if verified_route_next_gate_router_entry.get("verified_route_next_gate_router_returncode") != 0:
        reasons.append("verified_route_next_gate_router_returncode_not_zero")
    if verified_route_next_gate_router_entry.get("verified_route_next_gate_router_status") != ROUTER_SUCCESS_STATUS:
        reasons.append("verified_route_next_gate_router_status_not_recorded")
    if verified_route_next_gate_router_entry.get("next_gate_route_recorded") is not True:
        reasons.append("router_entry_next_gate_route_not_recorded")
    if verified_route_next_gate_router_entry.get("can_enter_routed_next_gate") is not True:
        reasons.append("router_entry_cannot_enter_routed_next_gate")
    if not verified_route_next_gate_router_entry.get("routed_next_gate"):
        reasons.append("router_entry_routed_next_gate_missing")
    if not verified_route_next_gate_router_entry.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if route_type not in VALID_ROUTE_TYPES and route_type != "unknown":
        reasons.append(f"verified_route_type_unknown:{route_type}")
    if verified_route_next_gate_router_entry.get("route_completion_record_count", 0) <= 0:
        reasons.append("route_completion_record_count_missing")
    if not verified_route_next_gate_router_entry.get("route_completion_records"):
        reasons.append("route_completion_records_missing")
    for field in [
        "verified_route_next_gate_router_report_path",
        "verified_route_next_gate_router_review_path",
        "verified_route_next_gate_router_status",
    ]:
        if not verified_route_next_gate_router_entry.get(field):
            reasons.append(f"{field}_missing")
    for field in [
        "entered_next_gate",
        "export_or_acceptance_executed",
        "rendered_pdf",
        "rendered_docx",
        "package_manifest_generated",
        "manual_acceptance_performed",
        "formal_writeback_executed",
        "this_command_wrote_formal_state",
        "can_write_product_state",
    ]:
        if verified_route_next_gate_router_entry.get(field) is True:
            reasons.append(f"router_entry_{field}")
    if verified_route_next_gate_router_entry.get("blocking_reasons"):
        reasons.append("source_router_entry_has_blocking_reasons")
    for flag, value in verified_route_next_gate_router_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"router_entry_boundary_violation:{flag}")
    return dedupe(reasons)


def build_router_blocking_reasons(verified_route_next_gate_router: dict[str, Any]) -> list[str]:
    reasons = []
    if verified_route_next_gate_router.get("schema_version") != ROUTER_SCHEMA_VERSION:
        reasons.append("verified_route_next_gate_router_missing_or_invalid_schema")
    if verified_route_next_gate_router.get("status") != ROUTER_SUCCESS_STATUS:
        reasons.append("verified_route_next_gate_router_not_route_recorded")
    if verified_route_next_gate_router.get("next_gate_route_recorded") is not True:
        reasons.append("verified_route_next_gate_router_route_not_recorded")
    if verified_route_next_gate_router.get("can_enter_routed_next_gate") is not True:
        reasons.append("verified_route_next_gate_router_cannot_enter_routed_next_gate")
    if not verified_route_next_gate_router.get("routed_next_gate"):
        reasons.append("verified_route_next_gate_router_routed_next_gate_missing")
    if not verified_route_next_gate_router.get("verified_route_type"):
        reasons.append("verified_route_next_gate_router_verified_route_type_missing")
    if verified_route_next_gate_router.get("blocking_reasons"):
        reasons.append("source_router_has_blocking_reasons")
    return dedupe(reasons)


def build_entry_router_contract_blocking_reasons(
    verified_route_next_gate_router_entry: dict[str, Any],
    verified_route_next_gate_router: dict[str, Any],
) -> list[str]:
    route_type = verified_route_next_gate_router_entry.get("verified_route_type", "unknown")
    entry_result = verified_route_next_gate_router_entry.get("verified_route_next_gate_router_result", {})
    summary = entry_result.get("verified_route_next_gate_router_report_summary", {})
    reasons = []
    if verified_route_next_gate_router_entry.get("verified_route_next_gate_router_report_path") != str(
        DEFAULT_ROUTER_PATH
    ):
        reasons.append(f"verified_route_next_gate_router_report_path_mismatch:{route_type}")
    if verified_route_next_gate_router_entry.get("verified_route_next_gate_router_review_path") != str(
        DEFAULT_ROUTER_REVIEW_PATH
    ):
        reasons.append(f"verified_route_next_gate_router_review_path_mismatch:{route_type}")
    if entry_result.get("report_path") != str(DEFAULT_ROUTER_PATH):
        reasons.append(f"verified_route_next_gate_router_result_report_path_mismatch:{route_type}")
    if entry_result.get("review_path") != str(DEFAULT_ROUTER_REVIEW_PATH):
        reasons.append(f"verified_route_next_gate_router_result_review_path_mismatch:{route_type}")
    if entry_result.get("returncode") != verified_route_next_gate_router_entry.get(
        "verified_route_next_gate_router_returncode"
    ):
        reasons.append(f"verified_route_next_gate_router_result_returncode_mismatch:{route_type}")
    if entry_result.get("status") != verified_route_next_gate_router.get("status"):
        reasons.append(f"verified_route_next_gate_router_result_status_mismatch:{route_type}")
    if verified_route_next_gate_router_entry.get("verified_route_next_gate_router_status") != (
        verified_route_next_gate_router.get("status")
    ):
        reasons.append(f"verified_route_next_gate_router_status_mismatch:{route_type}")
    for field in ["verified_route_type", "next_gate_route_recorded", "can_enter_routed_next_gate", "routed_next_gate"]:
        if verified_route_next_gate_router_entry.get(field) != verified_route_next_gate_router.get(field):
            reasons.append(f"verified_route_next_gate_router_{field}_mismatch:{route_type}")
    if verified_route_next_gate_router_entry.get("route_completion_record_count") != len(
        verified_route_next_gate_router.get("route_completion_records", []) or []
    ):
        reasons.append(f"route_completion_record_count_mismatch:{route_type}")
    if verified_route_next_gate_router_entry.get("route_completion_records") != (
        verified_route_next_gate_router.get("route_completion_records", []) or []
    ):
        reasons.append(f"route_completion_records_mismatch:{route_type}")
    if summary.get("schema_version") != verified_route_next_gate_router.get("schema_version"):
        reasons.append(f"verified_route_next_gate_router_summary_schema_mismatch:{route_type}")
    if summary.get("status") != verified_route_next_gate_router.get("status"):
        reasons.append(f"verified_route_next_gate_router_summary_status_mismatch:{route_type}")
    if summary.get("verified_route_type") != verified_route_next_gate_router.get("verified_route_type"):
        reasons.append(f"verified_route_next_gate_router_summary_route_mismatch:{route_type}")
    if summary.get("next_gate_route_recorded") != (
        verified_route_next_gate_router.get("next_gate_route_recorded") is True
    ):
        reasons.append(f"verified_route_next_gate_router_summary_recorded_mismatch:{route_type}")
    if summary.get("can_enter_routed_next_gate") != (
        verified_route_next_gate_router.get("can_enter_routed_next_gate") is True
    ):
        reasons.append(f"verified_route_next_gate_router_summary_can_enter_mismatch:{route_type}")
    if summary.get("routed_next_gate") != verified_route_next_gate_router.get("routed_next_gate"):
        reasons.append(f"verified_route_next_gate_router_summary_routed_next_gate_mismatch:{route_type}")
    if summary.get("blocking_reasons", []) != verified_route_next_gate_router.get("blocking_reasons", []):
        reasons.append(f"verified_route_next_gate_router_summary_blockers_mismatch:{route_type}")
    return dedupe(reasons)


def build_boundary_blocking_reasons(verified_route_next_gate_router: dict[str, Any]) -> list[str]:
    reasons = []
    if verified_route_next_gate_router.get("this_command_entered_next_gate") is True:
        reasons.append("verified_route_next_gate_router_entered_next_gate")
    if verified_route_next_gate_router.get("export_or_acceptance_executed") is True:
        reasons.append("verified_route_next_gate_router_executed_export_or_acceptance")
    if verified_route_next_gate_router.get("formal_writeback_executed") is True:
        reasons.append("verified_route_next_gate_router_formal_writeback_executed")
    if verified_route_next_gate_router.get("this_command_wrote_formal_state") is True:
        reasons.append("verified_route_next_gate_router_wrote_formal_state")
    if verified_route_next_gate_router.get("can_write_product_state") is True:
        reasons.append("verified_route_next_gate_router_allows_product_state_write")
    for flag, value in verified_route_next_gate_router.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"verified_route_next_gate_router_boundary_violation:{flag}")
    return dedupe(reasons)


def build_preflight_probe_blocking_reasons(verified_route_next_gate_router: dict[str, Any]) -> list[str]:
    probe = build_auto_mode_formal_package_routed_next_gate_entry_preflight(verified_route_next_gate_router)
    if probe.get("status") == "ready_for_routed_next_gate_entry_review":
        return []
    reasons = list(probe.get("blocking_reasons", []))
    reasons.append(f"routed_next_gate_entry_preflight_probe_status:{probe.get('status', 'missing')}")
    return dedupe(reasons)


def build_status(
    entry_reasons: list[str],
    router_reasons: list[str],
    contract_reasons: list[str],
    boundary_reasons: list[str],
    preflight_reasons: list[str],
) -> str:
    if entry_reasons:
        return "blocked_by_verified_route_next_gate_router_entry"
    if router_reasons:
        return "blocked_by_verified_route_next_gate_router_review"
    if contract_reasons:
        return "blocked_by_verified_route_next_gate_router_entry_result_contract"
    if boundary_reasons:
        return "blocked_by_verified_route_next_gate_router_entry_result_boundary"
    if preflight_reasons:
        return "blocked_by_routed_next_gate_entry_preflight_probe"
    return "verified_route_next_gate_router_entry_result_review_ready"


def build_routed_next_gate_entry_preflight_input_records(
    verified_route_next_gate_router: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = verified_route_next_gate_router.get("verified_route_type", "")
    routed_next_gate = verified_route_next_gate_router.get("routed_next_gate", "")
    route = verified_route_next_gate_router.get("next_gate_route", {})
    return [
        {
            "record_id": f"routed_next_gate_entry_preflight_input::{routed_next_gate}::{route_type}",
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "verified_route_next_gate_router_status": verified_route_next_gate_router.get("status", ""),
            "verified_route_next_gate_router_report_path": str(DEFAULT_ROUTER_PATH),
            "verified_route_next_gate_router_review_path": str(DEFAULT_ROUTER_REVIEW_PATH),
            "next_gate_route_id": route.get("route_id", ""),
            "next_gate_action": route.get("next_gate_action", ""),
            "route_completion_record_count": len(
                verified_route_next_gate_router.get("route_completion_records", []) or []
            ),
            "review_status": "verified_route_next_gate_router_entry_accepted_for_routed_next_gate_entry_preflight",
            "can_continue_to_routed_next_gate_entry_preflight": True,
        }
    ]


def build_source_entry_summary(verified_route_next_gate_router_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": verified_route_next_gate_router_entry.get("schema_version", ""),
        "status": verified_route_next_gate_router_entry.get("status", ""),
        "verified_route_type": verified_route_next_gate_router_entry.get("verified_route_type", ""),
        "verified_route_next_gate_router_status": verified_route_next_gate_router_entry.get(
            "verified_route_next_gate_router_status",
            "",
        ),
        "next_gate_route_recorded": verified_route_next_gate_router_entry.get("next_gate_route_recorded") is True,
        "can_enter_routed_next_gate": verified_route_next_gate_router_entry.get(
            "can_enter_routed_next_gate"
        )
        is True,
        "routed_next_gate": verified_route_next_gate_router_entry.get("routed_next_gate", ""),
        "source_blocking_reasons": verified_route_next_gate_router_entry.get("blocking_reasons", []),
        "boundary_flags": verified_route_next_gate_router_entry.get("boundary_flags", {}),
    }


def build_source_router_summary(verified_route_next_gate_router: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": verified_route_next_gate_router.get("schema_version", ""),
        "status": verified_route_next_gate_router.get("status", ""),
        "verified_route_type": verified_route_next_gate_router.get("verified_route_type", ""),
        "next_gate_route_recorded": verified_route_next_gate_router.get("next_gate_route_recorded") is True,
        "can_enter_routed_next_gate": verified_route_next_gate_router.get("can_enter_routed_next_gate")
        is True,
        "routed_next_gate": verified_route_next_gate_router.get("routed_next_gate", ""),
        "next_gate_route": verified_route_next_gate_router.get("next_gate_route", {}),
        "this_command_entered_next_gate": verified_route_next_gate_router.get(
            "this_command_entered_next_gate"
        )
        is True,
        "export_or_acceptance_executed": verified_route_next_gate_router.get(
            "export_or_acceptance_executed"
        )
        is True,
        "formal_writeback_executed": verified_route_next_gate_router.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": verified_route_next_gate_router.get(
            "this_command_wrote_formal_state"
        )
        is True,
        "can_write_product_state": verified_route_next_gate_router.get("can_write_product_state") is True,
        "source_blocking_reasons": verified_route_next_gate_router.get("blocking_reasons", []),
        "boundary_flags": verified_route_next_gate_router.get("boundary_flags", {}),
    }


def build_preflight_probe_summary(verified_route_next_gate_router: dict[str, Any]) -> dict[str, Any]:
    probe = build_auto_mode_formal_package_routed_next_gate_entry_preflight(verified_route_next_gate_router)
    return {
        "schema_version": probe.get("schema_version", ""),
        "status": probe.get("status", ""),
        "can_request_routed_next_gate_entry": probe.get("can_request_routed_next_gate_entry") is True,
        "routed_next_gate": probe.get("routed_next_gate", ""),
        "next_gate_entry_plan_count": len(probe.get("next_gate_entry_plan", []) or []),
        "blocking_reasons": probe.get("blocking_reasons", []),
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
        "recorded_verified_route_next_gate_router": False,
        "ran_routed_next_gate_entry_preflight": False,
    }


def build_next_action(
    status: str,
    blocking_reasons: list[str],
    route_type: str,
    routed_next_gate: str,
) -> dict[str, Any]:
    if status == "verified_route_next_gate_router_entry_result_review_ready":
        return {
            "id": "run_routed_next_gate_entry_preflight",
            "label": "Run routed next-gate entry preflight",
            "description": f"The `{route_type}` completion can continue to `{routed_next_gate}` preflight.",
        }
    if status == "blocked_by_verified_route_next_gate_router_entry":
        return {
            "id": "resolve_verified_route_next_gate_router_entry_blockers",
            "label": "Resolve P7-AX blockers",
            "description": "P7-AX must enter the verified route next-gate router before result review can continue.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_next_gate_router_entry_result_contract":
        return {
            "id": "repair_verified_route_next_gate_router_entry_result_contract",
            "label": "Repair router entry result contract",
            "description": "P7-AX and the verified route next-gate router output must agree.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_next_gate_router_review":
        return {
            "id": "resolve_verified_route_next_gate_router_output_blockers",
            "label": "Resolve verified route next-gate router output blockers",
            "description": "The router output must record one routed next gate.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_preflight_probe":
        return {
            "id": "repair_routed_next_gate_entry_preflight_contract",
            "label": "Repair routed next-gate entry preflight contract",
            "description": "The routed next gate must satisfy the existing preflight contract.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_verified_route_next_gate_router_boundary_violation",
        "label": "Resolve router result review boundary violation",
        "description": "P7-AY is read-only and cannot consume inputs with later-stage side effects.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Verified Route Next-Gate Router Entry Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- router status：`{report['verified_route_next_gate_router_status']}`",
        "- router entry result reviewed："
        f"{str(report['verified_route_next_gate_router_entry_result_reviewed']).lower()}",
        "- 可继续到 routed next gate entry preflight："
        f"{str(report['can_continue_to_routed_next_gate_entry_preflight']).lower()}",
        f"- next gate route recorded：{str(report['next_gate_route_recorded']).lower()}",
        f"- 可进入 routed next gate：{str(report['can_enter_routed_next_gate']).lower()}",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- route completion record 数：{report['route_completion_record_count']}",
        "- preflight input record 数："
        f"{len(report['routed_next_gate_entry_preflight_input_records'])}",
        "- routed next gate entry preflight 已执行："
        f"{str(report['routed_next_gate_entry_preflight_executed']).lower()}",
        "- 本命令运行 routed next gate entry preflight："
        f"{str(report['this_command_ran_routed_next_gate_entry_preflight']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["routed_next_gate_entry_preflight_input_records"]:
        lines.extend(["", "## Routed Next Gate Entry Preflight Input Records"])
        for record in report["routed_next_gate_entry_preflight_input_records"]:
            lines.append(f"- `{record['record_id']}` -> `{record['routed_next_gate']}`")
            lines.append(f"- action：`{record['next_gate_action']}`")
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

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.auto_mode_formal_package_routed_next_gate_entry_execute import (
    DEFAULT_ENTRY_MANIFEST_PATH,
    DEFAULT_EXECUTE_PATH,
    DEFAULT_REVIEW_PATH as DEFAULT_EXECUTE_REVIEW_PATH,
    build_auto_mode_formal_package_routed_next_gate_entry_execute,
    write_auto_mode_formal_package_routed_next_gate_entry_execute_outputs,
)


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.v1"
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.v1"
)
RESULT_REVIEW_READY_STATUS = "routed_next_gate_entry_preflight_entry_result_review_ready"
PREFLIGHT_SUCCESS_STATUS = "ready_for_routed_next_gate_entry_review"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review.json"
)
DEFAULT_GATE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.json"
)
DEFAULT_GATE_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.md"
)
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json")
DEFAULT_PREFLIGHT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md")
VALID_MODES = {"execute"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
    project_root: Path,
    routed_next_gate_entry_preflight_entry_result_review: dict[str, Any],
    *,
    mode: str = "execute",
    confirm_entry: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    execute_report_path: Path = DEFAULT_EXECUTE_PATH,
    execute_review_path: Path = DEFAULT_EXECUTE_REVIEW_PATH,
    entry_manifest_path: Path = DEFAULT_ENTRY_MANIFEST_PATH,
) -> tuple[dict[str, Any], int]:
    report = build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
        routed_next_gate_entry_preflight_entry_result_review,
        mode=mode,
        confirm_entry=confirm_entry,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        execute_report_path=execute_report_path,
        execute_review_path=execute_review_path,
        entry_manifest_path=entry_manifest_path,
    )
    if report["status"] != "ready_to_execute_explicit_routed_next_gate_entry":
        return report, 0

    preflight = build_preflight_from_result_review(routed_next_gate_entry_preflight_entry_result_review)
    execute_report = build_auto_mode_formal_package_routed_next_gate_entry_execute(
        preflight,
        mode="execute",
        confirm_entry=True,
        reviewer=reviewer,
        note=note,
        entry_manifest_path=entry_manifest_path,
        source_paths={
            "routed_next_gate_entry_preflight": str(DEFAULT_PREFLIGHT_PATH),
        },
    )
    execute_path, review_path, manifest_path = write_auto_mode_formal_package_routed_next_gate_entry_execute_outputs(
        project_root,
        execute_report,
        execute_report_path,
        execute_review_path,
        entry_manifest_path,
    )
    report["explicit_routed_next_gate_entry_gate_executed"] = True
    report["explicit_routed_next_gate_entry_execute_status"] = execute_report["status"]
    report["explicit_routed_next_gate_entry_execute_report_path"] = str(execute_report_path)
    report["explicit_routed_next_gate_entry_execute_review_path"] = str(execute_review_path)
    report["explicit_routed_next_gate_entry_execute_written_paths"] = {
        "report": str(execute_path.relative_to(project_root)),
        "review": str(review_path.relative_to(project_root)),
        "manifest": str(manifest_path.relative_to(project_root)) if manifest_path is not None else "",
    }
    report["routed_next_gate_entry_manifest_recorded"] = (
        execute_report.get("routed_next_gate_entry_manifest_recorded") is True
    )
    report["routed_next_gate_entry_manifest_path"] = execute_report.get("routed_next_gate_entry_manifest_path", "")
    report["explicit_routed_next_gate_entry_operations"] = execute_report.get(
        "routed_next_gate_entry_operations",
        [],
    )
    report["next_gate_entered"] = execute_report.get("next_gate_entered") is True
    report["this_command_entered_next_gate"] = execute_report.get("this_command_entered_next_gate") is True
    report["next_gate_command_executed"] = execute_report.get("next_gate_command_executed") is True
    report["export_or_acceptance_executed"] = execute_report.get("export_or_acceptance_executed") is True
    report["formal_writeback_executed"] = execute_report.get("formal_writeback_executed") is True
    report["this_command_wrote_formal_state"] = execute_report.get("this_command_wrote_formal_state") is True
    report["can_write_product_state"] = execute_report.get("can_write_product_state") is True
    if execute_report["status"] == "routed_next_gate_entry_manifest_recorded":
        report["status"] = "explicit_routed_next_gate_entry_manifest_recorded"
        report["next_action"] = build_next_action(report["status"], [])
        return report, 0

    report["status"] = "blocked_by_explicit_routed_next_gate_entry_execute"
    report["blocking_reasons"] = dedupe(
        [f"explicit_routed_next_gate_entry_execute_status:{execute_report['status']}"]
        + execute_report.get("blocking_reasons", [])
    )
    report["next_action"] = build_next_action(report["status"], report["blocking_reasons"])
    return report, 2


def build_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
    routed_next_gate_entry_preflight_entry_result_review: dict[str, Any],
    *,
    mode: str = "execute",
    confirm_entry: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    execute_report_path: Path = DEFAULT_EXECUTE_PATH,
    execute_review_path: Path = DEFAULT_EXECUTE_REVIEW_PATH,
    entry_manifest_path: Path = DEFAULT_ENTRY_MANIFEST_PATH,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    result_review_reasons = build_result_review_blocking_reasons(
        routed_next_gate_entry_preflight_entry_result_review
    )
    boundary_reasons = (
        build_boundary_blocking_reasons(routed_next_gate_entry_preflight_entry_result_review)
        if not result_review_reasons
        else []
    )
    contract_reasons = (
        build_input_record_contract_blocking_reasons(
            routed_next_gate_entry_preflight_entry_result_review
        )
        if not result_review_reasons and not boundary_reasons
        else []
    )
    request_reasons = (
        build_request_blocking_reasons(mode, confirm_entry, reviewer, note)
        if not result_review_reasons and not boundary_reasons and not contract_reasons
        else []
    )
    blocking_reasons = dedupe(result_review_reasons + boundary_reasons + contract_reasons + request_reasons)
    status = build_status(result_review_reasons, boundary_reasons, contract_reasons, request_reasons)
    ready = status == "ready_to_execute_explicit_routed_next_gate_entry"
    route_type = routed_next_gate_entry_preflight_entry_result_review.get("verified_route_type", "") if ready else ""
    routed_next_gate = routed_next_gate_entry_preflight_entry_result_review.get("routed_next_gate", "") if ready else ""

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": routed_next_gate_entry_preflight_entry_result_review.get("topic", ""),
        "source_paths": {
            "routed_next_gate_entry_preflight_entry_result_review": source_paths.get(
                "routed_next_gate_entry_preflight_entry_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": routed_next_gate_entry_preflight_entry_result_review.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_entry": confirm_entry,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "can_execute_explicit_routed_next_gate_entry": ready,
        "explicit_routed_next_gate_entry_gate_executed": False,
        "explicit_routed_next_gate_entry_execute_status": "",
        "explicit_routed_next_gate_entry_execute_report_path": str(execute_report_path) if ready else "",
        "explicit_routed_next_gate_entry_execute_review_path": str(execute_review_path) if ready else "",
        "explicit_routed_next_gate_entry_execute_written_paths": {},
        "routed_next_gate_entry_manifest_recorded": False,
        "routed_next_gate_entry_manifest_path": str(entry_manifest_path) if ready else "",
        "explicit_routed_next_gate_entry_operations": build_planned_operations(
            routed_next_gate_entry_preflight_entry_result_review
        )
        if ready
        else [],
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
        "entry_request": build_entry_request(mode, confirm_entry, reviewer, note),
        "source_result_review": build_source_result_review_summary(
            routed_next_gate_entry_preflight_entry_result_review
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_result_review_blocking_reasons(
    routed_next_gate_entry_preflight_entry_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    if routed_next_gate_entry_preflight_entry_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("routed_next_gate_entry_preflight_entry_result_review_missing_or_invalid_schema")
    if routed_next_gate_entry_preflight_entry_result_review.get("status") != RESULT_REVIEW_READY_STATUS:
        reasons.append("routed_next_gate_entry_preflight_entry_result_review_not_ready")
    if (
        routed_next_gate_entry_preflight_entry_result_review.get(
            "routed_next_gate_entry_preflight_entry_result_reviewed"
        )
        is not True
    ):
        reasons.append("routed_next_gate_entry_preflight_entry_result_not_reviewed")
    if (
        routed_next_gate_entry_preflight_entry_result_review.get(
            "can_continue_to_explicit_routed_next_gate_entry"
        )
        is not True
    ):
        reasons.append("result_review_cannot_continue_to_explicit_routed_next_gate_entry")
    if routed_next_gate_entry_preflight_entry_result_review.get("can_request_routed_next_gate_entry") is not True:
        reasons.append("result_review_cannot_request_routed_next_gate_entry")
    if (
        routed_next_gate_entry_preflight_entry_result_review.get("requires_explicit_next_gate_entry_command")
        is not True
    ):
        reasons.append("result_review_missing_explicit_next_gate_entry_requirement")
    if routed_next_gate_entry_preflight_entry_result_review.get("routed_next_gate_entry_preflight_status") != (
        PREFLIGHT_SUCCESS_STATUS
    ):
        reasons.append("result_review_preflight_status_not_ready")
    if not routed_next_gate_entry_preflight_entry_result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if not routed_next_gate_entry_preflight_entry_result_review.get("routed_next_gate"):
        reasons.append("routed_next_gate_missing")
    if not routed_next_gate_entry_preflight_entry_result_review.get("next_gate_entry_plan"):
        reasons.append("next_gate_entry_plan_missing")
    if routed_next_gate_entry_preflight_entry_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(
    routed_next_gate_entry_preflight_entry_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    field_reasons = {
        "explicit_routed_next_gate_entry_executed": "result_review_already_executed_explicit_routed_next_gate_entry",
        "next_gate_entered": "result_review_entered_next_gate",
        "this_command_entered_next_gate": "result_review_entered_next_gate",
        "next_gate_command_executed": "result_review_ran_next_gate_command",
        "export_or_acceptance_executed": "result_review_executed_export_or_acceptance",
        "rendered_pdf": "result_review_rendered_pdf",
        "rendered_docx": "result_review_rendered_docx",
        "package_manifest_generated": "result_review_generated_package_manifest",
        "manual_acceptance_performed": "result_review_performed_manual_acceptance",
        "formal_writeback_executed": "result_review_executed_formal_writeback",
        "this_command_wrote_formal_state": "result_review_wrote_formal_state",
        "can_write_product_state": "result_review_allows_product_state_write",
    }
    for field, reason in field_reasons.items():
        if routed_next_gate_entry_preflight_entry_result_review.get(field) is True:
            reasons.append(reason)
    for flag, value in routed_next_gate_entry_preflight_entry_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_input_record_contract_blocking_reasons(
    routed_next_gate_entry_preflight_entry_result_review: dict[str, Any],
) -> list[str]:
    records = routed_next_gate_entry_preflight_entry_result_review.get(
        "explicit_routed_next_gate_entry_input_records",
        [],
    )
    if not records:
        return ["explicit_routed_next_gate_entry_input_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["explicit_routed_next_gate_entry_input_record_not_single"]
    record = records[0]
    if not isinstance(record, dict):
        return ["explicit_routed_next_gate_entry_input_record_not_object"]

    route_type = routed_next_gate_entry_preflight_entry_result_review.get("verified_route_type", "unknown")
    routed_next_gate = routed_next_gate_entry_preflight_entry_result_review.get("routed_next_gate", "")
    plan = routed_next_gate_entry_preflight_entry_result_review.get("next_gate_entry_plan", []) or []
    entry_ids = [item.get("entry_id", "") for item in plan]
    reasons = []
    if record.get("record_id") != f"explicit_routed_next_gate_entry_input::{routed_next_gate}::{route_type}":
        reasons.append(f"explicit_routed_next_gate_entry_input_record_id_mismatch:{route_type}")
    if record.get("verified_route_type") != route_type:
        reasons.append(f"explicit_routed_next_gate_entry_input_record_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != routed_next_gate:
        reasons.append(f"explicit_routed_next_gate_entry_input_record_gate_mismatch:{route_type}")
    if record.get("routed_next_gate_entry_preflight_status") != PREFLIGHT_SUCCESS_STATUS:
        reasons.append(f"routed_next_gate_entry_preflight_status_mismatch:{route_type}")
    if record.get("routed_next_gate_entry_preflight_report_path") != str(DEFAULT_PREFLIGHT_PATH):
        reasons.append(f"routed_next_gate_entry_preflight_report_path_mismatch:{route_type}")
    if record.get("routed_next_gate_entry_preflight_review_path") != str(DEFAULT_PREFLIGHT_REVIEW_PATH):
        reasons.append(f"routed_next_gate_entry_preflight_review_path_mismatch:{route_type}")
    if record.get("next_gate_entry_plan_count") != len(plan):
        reasons.append(f"explicit_routed_next_gate_entry_input_record_plan_count_mismatch:{route_type}")
    if record.get("entry_ids") != entry_ids:
        reasons.append(f"explicit_routed_next_gate_entry_input_record_entry_ids_mismatch:{route_type}")
    if record.get("review_status") != "routed_next_gate_entry_preflight_accepted_for_explicit_entry_gate":
        reasons.append(f"explicit_routed_next_gate_entry_input_record_review_status_mismatch:{route_type}")
    if record.get("can_continue_to_explicit_routed_next_gate_entry") is not True:
        reasons.append(f"explicit_routed_next_gate_entry_input_record_cannot_continue:{route_type}")
    return dedupe(reasons)


def build_request_blocking_reasons(
    mode: str,
    confirm_entry: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["explicit_routed_next_gate_entry_mode_invalid"]
    reasons = []
    if not confirm_entry:
        reasons.append("confirm_entry_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("entry_note_required")
    return reasons


def build_status(
    result_review_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if result_review_reasons:
        return "blocked_by_routed_next_gate_entry_preflight_entry_result_review"
    if boundary_reasons:
        return "blocked_by_explicit_routed_next_gate_entry_boundary"
    if contract_reasons:
        return "blocked_by_explicit_routed_next_gate_entry_input_contract"
    if "explicit_routed_next_gate_entry_mode_invalid" in request_reasons:
        return "blocked_by_explicit_routed_next_gate_entry_mode"
    if "confirm_entry_required" in request_reasons:
        return "blocked_by_missing_explicit_routed_next_gate_entry_confirmation"
    if request_reasons:
        return "blocked_by_explicit_routed_next_gate_entry_metadata"
    return "ready_to_execute_explicit_routed_next_gate_entry"


def build_preflight_from_result_review(
    routed_next_gate_entry_preflight_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "p7.auto_mode_formal_package_routed_next_gate_entry_preflight.v1",
        "generated_at": routed_next_gate_entry_preflight_entry_result_review.get("generated_at", utc_now()),
        "topic": routed_next_gate_entry_preflight_entry_result_review.get("topic", ""),
        "source_status": routed_next_gate_entry_preflight_entry_result_review.get("status", ""),
        "status": PREFLIGHT_SUCCESS_STATUS,
        "verified_route_type": routed_next_gate_entry_preflight_entry_result_review.get("verified_route_type", ""),
        "routed_next_gate": routed_next_gate_entry_preflight_entry_result_review.get("routed_next_gate", ""),
        "can_request_routed_next_gate_entry": True,
        "requires_explicit_next_gate_entry_command": True,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": [],
        "source_router": {},
        "next_gate_entry_plan": routed_next_gate_entry_preflight_entry_result_review.get(
            "next_gate_entry_plan",
            [],
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": {"id": "explicit_routed_next_gate_entry_gate"},
    }


def build_planned_operations(
    routed_next_gate_entry_preflight_entry_result_review: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = []
    for item in routed_next_gate_entry_preflight_entry_result_review.get("next_gate_entry_plan", []) or []:
        route_type = item.get("verified_route_type", "")
        gate_id = item.get("gate_id", "")
        operations.append(
            {
                "operation_id": f"explicit_routed_next_gate_entry_gate::{gate_id}::{route_type}",
                "entry_id": item.get("entry_id", ""),
                "verified_route_type": route_type,
                "gate_id": gate_id,
                "next_command": item.get("next_command", ""),
                "operation_status": "pending_execute_component_call",
                "will_enter_next_gate": False,
                "will_run_next_gate_command": False,
                "will_execute_export_or_acceptance": False,
                "will_write_product_state": False,
            }
        )
    return operations


def build_entry_request(mode: str, confirm_entry: bool, reviewer: str, note: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_entry": confirm_entry,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_source_result_review_summary(
    routed_next_gate_entry_preflight_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": routed_next_gate_entry_preflight_entry_result_review.get("schema_version", ""),
        "status": routed_next_gate_entry_preflight_entry_result_review.get("status", ""),
        "verified_route_type": routed_next_gate_entry_preflight_entry_result_review.get("verified_route_type", ""),
        "routed_next_gate": routed_next_gate_entry_preflight_entry_result_review.get("routed_next_gate", ""),
        "can_continue_to_explicit_routed_next_gate_entry": routed_next_gate_entry_preflight_entry_result_review.get(
            "can_continue_to_explicit_routed_next_gate_entry"
        )
        is True,
        "explicit_input_record_count": len(
            routed_next_gate_entry_preflight_entry_result_review.get(
                "explicit_routed_next_gate_entry_input_records",
                [],
            )
            or []
        ),
        "next_gate_entry_plan_count": len(
            routed_next_gate_entry_preflight_entry_result_review.get("next_gate_entry_plan", []) or []
        ),
        "blocking_reasons": routed_next_gate_entry_preflight_entry_result_review.get("blocking_reasons", []),
        "boundary_flags": routed_next_gate_entry_preflight_entry_result_review.get("boundary_flags", {}),
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
        "entered_explicit_routed_next_gate_entry": False,
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "explicit_routed_next_gate_entry_manifest_recorded":
        return {
            "id": "run_manifested_routed_next_gate",
            "label": "Run manifested routed next gate",
            "description": "The entry manifest is recorded; a later node may run the routed next-gate command.",
        }
    if status == "ready_to_execute_explicit_routed_next_gate_entry":
        return {
            "id": "call_routed_next_gate_entry_execute",
            "label": "Call routed next-gate entry execute",
            "description": "P7-BB may call the existing execute component to record an entry manifest.",
        }
    if status == "blocked_by_missing_explicit_routed_next_gate_entry_confirmation":
        return {
            "id": "rerun_with_confirm_entry",
            "label": "Rerun with explicit entry confirmation",
            "description": "P7-BB requires --confirm-entry before invoking execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_explicit_routed_next_gate_entry_metadata":
        return {
            "id": "record_entry_reviewer_and_note",
            "label": "Record entry reviewer and note",
            "description": "P7-BB requires reviewer and note before invoking execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_explicit_routed_next_gate_entry_input_contract":
        return {
            "id": "repair_explicit_routed_next_gate_entry_input_record",
            "label": "Repair explicit routed next-gate entry input record",
            "description": "P7-BA must provide one accepted input record matching its entry plan.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_explicit_routed_next_gate_entry_boundary":
        return {
            "id": "resolve_explicit_routed_next_gate_entry_boundary",
            "label": "Resolve explicit routed next-gate entry boundary",
            "description": "P7-BB cannot consume result reviews that already crossed formal boundaries.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_routed_next_gate_entry_preflight_entry_result_review_blockers",
        "label": "Resolve P7-BA blockers",
        "description": "P7-BA must accept the preflight result before P7-BB can invoke execute.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_GATE_PATH,
    review_path: Path = DEFAULT_GATE_REVIEW_PATH,
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
        "# Auto Mode Formal Package Next Gate Explicit Routed Next Gate Entry Gate",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        "- explicit entry gate 已执行："
        f"{str(report['explicit_routed_next_gate_entry_gate_executed']).lower()}",
        f"- execute status：`{report['explicit_routed_next_gate_entry_execute_status']}`",
        f"- entry manifest 已记录：{str(report['routed_next_gate_entry_manifest_recorded']).lower()}",
        f"- explicit operations：{len(report['explicit_routed_next_gate_entry_operations'])}",
        f"- 已进入下一关：{str(report['next_gate_entered']).lower()}",
        f"- 已运行下一关命令：{str(report['next_gate_command_executed']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Explicit Routed Next Gate Entry Operations"])
    if report["explicit_routed_next_gate_entry_operations"]:
        for operation in report["explicit_routed_next_gate_entry_operations"]:
            lines.append(f"- `{operation['operation_id']}`: {operation['operation_status']}")
            lines.append(f"- next command：`{operation['next_command']}`")
    else:
        lines.append("- 无；等待 P7-BA ready 和显式确认。")
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

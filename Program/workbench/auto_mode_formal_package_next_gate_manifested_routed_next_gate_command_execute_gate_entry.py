from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.auto_mode_formal_package_manifested_routed_next_gate_command_execute import (
    DEFAULT_EXECUTE_PATH as DEFAULT_MANIFESTED_COMMAND_EXECUTE_PATH,
    DEFAULT_REVIEW_PATH as DEFAULT_MANIFESTED_COMMAND_EXECUTE_REVIEW_PATH,
    run_auto_mode_formal_package_manifested_routed_next_gate_command_execute,
    write_auto_mode_formal_package_manifested_routed_next_gate_command_execute_outputs,
)


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.v1"
)
RUN_PREFLIGHT_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.v1"
)
RUN_PREFLIGHT_READY_STATUS = "ready_for_manifested_routed_next_gate_run_preflight"
LEGACY_COMMAND_PREFLIGHT_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_manifested_routed_next_gate_command_preflight.v1"
)
LEGACY_COMMAND_PREFLIGHT_READY_STATUS = "ready_for_manifested_routed_next_gate_command_review"
DEFAULT_RUN_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.json"
)
DEFAULT_GATE_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.json"
)
DEFAULT_GATE_ENTRY_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.md"
)


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
    project_root: Path,
    manifested_routed_next_gate_run_preflight: dict[str, Any],
    *,
    confirm_command_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
    manifested_command_execute_report_path: Path = DEFAULT_MANIFESTED_COMMAND_EXECUTE_PATH,
    manifested_command_execute_review_path: Path = DEFAULT_MANIFESTED_COMMAND_EXECUTE_REVIEW_PATH,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
        manifested_routed_next_gate_run_preflight,
        confirm_command_execute=confirm_command_execute,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        repo_root=repo_root,
        manifested_command_execute_report_path=manifested_command_execute_report_path,
        manifested_command_execute_review_path=manifested_command_execute_review_path,
    )
    if report["status"] != "ready_to_execute_manifested_routed_next_gate_command":
        return report, 0

    legacy_preflight = build_legacy_manifested_command_preflight(manifested_routed_next_gate_run_preflight)
    execute_report, execute_exit_code = run_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
        project_root,
        legacy_preflight,
        mode="execute",
        confirm_command_execute=True,
        reviewer=reviewer,
        note=note,
        source_paths={
            "manifested_routed_next_gate_command_preflight": source_paths.get(
                "manifested_routed_next_gate_run_preflight",
                str(DEFAULT_RUN_PREFLIGHT_PATH),
            )
            if source_paths
            else str(DEFAULT_RUN_PREFLIGHT_PATH),
        },
        repo_root=repo_root,
    )
    execute_path, execute_review_path = write_auto_mode_formal_package_manifested_routed_next_gate_command_execute_outputs(
        project_root,
        execute_report,
        manifested_command_execute_report_path,
        manifested_command_execute_review_path,
    )

    report["command_execute_gate_entry_executed"] = True
    report["manifested_command_execute_status"] = execute_report["status"]
    report["manifested_command_execute_report_path"] = str(manifested_command_execute_report_path)
    report["manifested_command_execute_review_path"] = str(manifested_command_execute_review_path)
    report["manifested_command_execute_written_paths"] = {
        "report": str(execute_path.relative_to(project_root)),
        "review": str(execute_review_path.relative_to(project_root)),
    }
    report["delegated_command"] = execute_report.get("delegated_command", [])
    report["delegated_report_path"] = execute_report.get("delegated_report_path", "")
    report["delegated_review_path"] = execute_report.get("delegated_review_path", "")
    report["delegated_returncode"] = execute_report.get("delegated_returncode")
    report["delegated_status"] = execute_report.get("delegated_status", "")
    report["delegated_result"] = execute_report.get("delegated_result", {})
    report["next_gate_command_executed"] = execute_report.get("next_gate_command_executed") is True
    report["this_command_ran_next_gate_command"] = execute_report.get("this_command_ran_next_gate_command") is True
    report["next_gate_entered"] = execute_report.get("next_gate_entered") is True
    report["this_command_entered_next_gate"] = execute_report.get("this_command_entered_next_gate") is True
    report["export_or_acceptance_executed"] = execute_report.get("export_or_acceptance_executed") is True
    report["formal_writeback_executed"] = execute_report.get("formal_writeback_executed") is True
    report["this_command_wrote_formal_state"] = execute_report.get("this_command_wrote_formal_state") is True
    report["can_write_product_state"] = execute_report.get("can_write_product_state") is True
    if execute_report["status"] == "manifested_next_gate_command_executed" and execute_exit_code == 0:
        report["status"] = "manifested_routed_next_gate_command_execute_gate_entry_executed"
        report["blocking_reasons"] = []
        report["next_action"] = build_next_action(report["status"], [], report["verified_route_type"])
        return report, 0

    report["status"] = "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_delegation"
    report["blocking_reasons"] = dedupe(
        [f"manifested_command_execute_status:{execute_report['status']}"]
        + execute_report.get("blocking_reasons", [])
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
    *,
    confirm_command_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
    manifested_command_execute_report_path: Path = DEFAULT_MANIFESTED_COMMAND_EXECUTE_PATH,
    manifested_command_execute_review_path: Path = DEFAULT_MANIFESTED_COMMAND_EXECUTE_REVIEW_PATH,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    preflight_reasons = build_run_preflight_blocking_reasons(manifested_routed_next_gate_run_preflight)
    boundary_reasons = (
        build_boundary_blocking_reasons(manifested_routed_next_gate_run_preflight)
        if not preflight_reasons
        else []
    )
    input_contract_reasons = (
        build_run_input_contract_blocking_reasons(manifested_routed_next_gate_run_preflight)
        if not preflight_reasons and not boundary_reasons
        else []
    )
    command_reasons = (
        build_command_unavailable_reasons(manifested_routed_next_gate_run_preflight, repo_root)
        if not preflight_reasons and not boundary_reasons and not input_contract_reasons
        else []
    )
    request_reasons = (
        build_request_blocking_reasons(confirm_command_execute, reviewer, note)
        if not preflight_reasons and not boundary_reasons and not input_contract_reasons and not command_reasons
        else []
    )
    blocking_reasons = dedupe(
        preflight_reasons + boundary_reasons + input_contract_reasons + command_reasons + request_reasons
    )
    status = build_status(
        preflight_reasons,
        boundary_reasons,
        input_contract_reasons,
        command_reasons,
        request_reasons,
    )
    ready = status == "ready_to_execute_manifested_routed_next_gate_command"
    route_type = manifested_routed_next_gate_run_preflight.get("verified_route_type", "") if ready else ""
    routed_next_gate = manifested_routed_next_gate_run_preflight.get("routed_next_gate", "") if ready else ""
    delegated_command = (
        build_preview_delegated_command(manifested_routed_next_gate_run_preflight)
        if ready
        else []
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": manifested_routed_next_gate_run_preflight.get("topic", ""),
        "source_paths": {
            "manifested_routed_next_gate_run_preflight": source_paths.get(
                "manifested_routed_next_gate_run_preflight",
                str(DEFAULT_RUN_PREFLIGHT_PATH),
            ),
        },
        "source_status": manifested_routed_next_gate_run_preflight.get("status", ""),
        "status": status,
        "confirm_command_execute": confirm_command_execute,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "can_execute_manifested_routed_next_gate_command": ready,
        "requires_explicit_next_gate_command_execute": ready,
        "command_execute_gate_entry_executed": False,
        "manifested_command_execute_status": "",
        "manifested_command_execute_report_path": str(manifested_command_execute_report_path) if ready else "",
        "manifested_command_execute_review_path": str(manifested_command_execute_review_path) if ready else "",
        "manifested_command_execute_written_paths": {},
        "delegated_command": delegated_command,
        "delegated_report_path": "",
        "delegated_review_path": "",
        "delegated_returncode": None,
        "delegated_status": "",
        "delegated_result": {},
        "next_gate_command_executed": False,
        "this_command_ran_next_gate_command": False,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_run_preflight": build_source_run_preflight_summary(
            manifested_routed_next_gate_run_preflight
        ),
        "command_execute_request": build_command_execute_request(
            confirm_command_execute,
            reviewer,
            note,
        ),
        "run_input_record": extract_run_input_record(manifested_routed_next_gate_run_preflight)
        if ready
        else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_run_preflight_blocking_reasons(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    if manifested_routed_next_gate_run_preflight.get("schema_version") != RUN_PREFLIGHT_SCHEMA_VERSION:
        reasons.append("manifested_routed_next_gate_run_preflight_missing_or_invalid_schema")
    if manifested_routed_next_gate_run_preflight.get("status") != RUN_PREFLIGHT_READY_STATUS:
        reasons.append("manifested_routed_next_gate_run_preflight_not_ready")
    if (
        manifested_routed_next_gate_run_preflight.get("manifested_routed_next_gate_run_preflight_reviewed")
        is not True
    ):
        reasons.append("manifested_routed_next_gate_run_preflight_not_reviewed")
    if (
        manifested_routed_next_gate_run_preflight.get("can_request_manifested_next_gate_command_execution")
        is not True
    ):
        reasons.append("manifested_routed_next_gate_run_preflight_cannot_request_execution")
    if manifested_routed_next_gate_run_preflight.get("requires_explicit_next_gate_command_execute") is not True:
        reasons.append("manifested_routed_next_gate_run_preflight_missing_explicit_command_requirement")
    if not manifested_routed_next_gate_run_preflight.get("verified_route_type"):
        reasons.append("manifested_routed_next_gate_run_preflight_verified_route_type_missing")
    if not manifested_routed_next_gate_run_preflight.get("routed_next_gate"):
        reasons.append("manifested_routed_next_gate_run_preflight_routed_next_gate_missing")
    if not manifested_routed_next_gate_run_preflight.get("next_gate_command_call_plan"):
        reasons.append("next_gate_command_call_plan_missing")
    if manifested_routed_next_gate_run_preflight.get("blocking_reasons"):
        reasons.append("source_run_preflight_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    field_reasons = {
        "next_gate_command_executed": "manifested_routed_next_gate_run_preflight_already_executed_command",
        "this_command_ran_next_gate_command": "manifested_routed_next_gate_run_preflight_ran_command",
        "next_gate_entered": "manifested_routed_next_gate_run_preflight_already_entered_next_gate",
        "this_command_entered_next_gate": "manifested_routed_next_gate_run_preflight_already_entered_next_gate",
        "export_or_acceptance_executed": "manifested_routed_next_gate_run_preflight_executed_export_or_acceptance",
        "formal_writeback_executed": "manifested_routed_next_gate_run_preflight_executed_formal_writeback",
        "this_command_wrote_formal_state": "manifested_routed_next_gate_run_preflight_wrote_formal_state",
        "can_write_product_state": "manifested_routed_next_gate_run_preflight_allows_product_state_write",
    }
    for field, reason in field_reasons.items():
        if manifested_routed_next_gate_run_preflight.get(field) is True:
            reasons.append(reason)
    for flag, value in manifested_routed_next_gate_run_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"manifested_routed_next_gate_run_preflight_boundary_violation:{flag}")
    return dedupe(reasons)


def build_run_input_contract_blocking_reasons(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
) -> list[str]:
    plan = manifested_routed_next_gate_run_preflight.get("next_gate_command_call_plan", [])
    records = manifested_routed_next_gate_run_preflight.get("manifested_routed_next_gate_run_input_records", [])
    if not isinstance(plan, list) or len(plan) != 1:
        return ["next_gate_command_call_plan_not_single"]
    if not records:
        return ["manifested_routed_next_gate_run_input_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["manifested_routed_next_gate_run_input_record_not_single"]

    item = plan[0]
    record = records[0]
    route_type = manifested_routed_next_gate_run_preflight.get("verified_route_type", "unknown")
    gate_id = manifested_routed_next_gate_run_preflight.get("routed_next_gate", "")
    reasons = []
    if record.get("record_id") != f"manifested_routed_next_gate_run_input::{gate_id}::{route_type}":
        reasons.append(f"manifested_routed_next_gate_run_input_record_id_mismatch:{route_type}")
    if record.get("verified_route_type") != route_type:
        reasons.append(f"manifested_routed_next_gate_run_input_record_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != gate_id:
        reasons.append(f"manifested_routed_next_gate_run_input_record_gate_mismatch:{route_type}")
    if record.get("manifested_command_preflight_status") != LEGACY_COMMAND_PREFLIGHT_READY_STATUS:
        reasons.append(f"manifested_routed_next_gate_run_input_record_preflight_status_mismatch:{route_type}")
    for field in ["command_plan_id", "source_operation_id", "source_entry_id", "next_command", "command_path", "command_kind"]:
        if record.get(field) != item.get(field):
            reasons.append(f"manifested_routed_next_gate_run_input_record_{field}_mismatch:{route_type}")
    if record.get("requires_explicit_next_gate_command_execute") is not True:
        reasons.append(f"manifested_routed_next_gate_run_input_record_missing_explicit_requirement:{route_type}")
    if record.get("review_status") != "manifested_routed_next_gate_run_preflight_ready_for_command_execute_gate":
        reasons.append(f"manifested_routed_next_gate_run_input_record_review_status_mismatch:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    item = extract_command_plan(manifested_routed_next_gate_run_preflight)
    command_path = item.get("command_path", "")
    if command_path and not (repo_root / command_path).exists():
        return [f"next_gate_command_file_missing:{command_path}"]
    return []


def build_request_blocking_reasons(
    confirm_command_execute: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    reasons = []
    if not confirm_command_execute:
        reasons.append("confirm_command_execute_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("command_execute_note_required")
    return reasons


def build_status(
    preflight_reasons: list[str],
    boundary_reasons: list[str],
    input_contract_reasons: list[str],
    command_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if preflight_reasons:
        return "blocked_by_manifested_routed_next_gate_run_preflight"
    if boundary_reasons:
        return "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_boundary"
    if input_contract_reasons:
        return "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_input_contract"
    if command_reasons:
        return "blocked_by_manifested_routed_next_gate_command_unavailable"
    if "confirm_command_execute_required" in request_reasons:
        return "blocked_by_missing_manifested_routed_next_gate_command_execute_confirmation"
    if request_reasons:
        return "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_metadata"
    return "ready_to_execute_manifested_routed_next_gate_command"


def build_legacy_manifested_command_preflight(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": LEGACY_COMMAND_PREFLIGHT_SCHEMA_VERSION,
        "generated_at": manifested_routed_next_gate_run_preflight.get("generated_at", utc_now()),
        "topic": manifested_routed_next_gate_run_preflight.get("topic", ""),
        "source_paths": manifested_routed_next_gate_run_preflight.get("source_paths", {}),
        "source_status": "manifested",
        "status": LEGACY_COMMAND_PREFLIGHT_READY_STATUS,
        "verified_route_type": manifested_routed_next_gate_run_preflight.get("verified_route_type", ""),
        "routed_next_gate": manifested_routed_next_gate_run_preflight.get("routed_next_gate", ""),
        "can_request_manifested_next_gate_command_execution": True,
        "requires_explicit_next_gate_command_execute": True,
        "next_gate_command_executed": False,
        "this_command_ran_next_gate_command": False,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": [],
        "next_gate_command_call_plan": manifested_routed_next_gate_run_preflight.get(
            "next_gate_command_call_plan",
            [],
        ),
        "boundary_flags": build_boundary_flags(),
    }


def build_preview_delegated_command(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
) -> list[str]:
    item = extract_command_plan(manifested_routed_next_gate_run_preflight)
    command_path = item.get("command_path", "")
    args = list(item.get("command_args", []))
    return ["python3", command_path] + [str(arg) for arg in args]


def extract_command_plan(manifested_routed_next_gate_run_preflight: dict[str, Any]) -> dict[str, Any]:
    plan = manifested_routed_next_gate_run_preflight.get("next_gate_command_call_plan", [])
    if isinstance(plan, list) and len(plan) == 1:
        return plan[0]
    return {}


def extract_run_input_record(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
) -> dict[str, Any]:
    records = manifested_routed_next_gate_run_preflight.get("manifested_routed_next_gate_run_input_records", [])
    if isinstance(records, list) and len(records) == 1:
        return records[0]
    return {}


def build_source_run_preflight_summary(
    manifested_routed_next_gate_run_preflight: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": manifested_routed_next_gate_run_preflight.get("schema_version", ""),
        "status": manifested_routed_next_gate_run_preflight.get("status", ""),
        "verified_route_type": manifested_routed_next_gate_run_preflight.get("verified_route_type", ""),
        "routed_next_gate": manifested_routed_next_gate_run_preflight.get("routed_next_gate", ""),
        "manifested_routed_next_gate_run_preflight_reviewed": manifested_routed_next_gate_run_preflight.get(
            "manifested_routed_next_gate_run_preflight_reviewed"
        )
        is True,
        "can_request_manifested_next_gate_command_execution": manifested_routed_next_gate_run_preflight.get(
            "can_request_manifested_next_gate_command_execution"
        )
        is True,
        "requires_explicit_next_gate_command_execute": manifested_routed_next_gate_run_preflight.get(
            "requires_explicit_next_gate_command_execute"
        )
        is True,
        "command_plan_count": len(
            manifested_routed_next_gate_run_preflight.get("next_gate_command_call_plan", []) or []
        ),
        "run_input_record_count": len(
            manifested_routed_next_gate_run_preflight.get(
                "manifested_routed_next_gate_run_input_records",
                [],
            )
            or []
        ),
        "blocking_reasons": manifested_routed_next_gate_run_preflight.get("blocking_reasons", []),
        "boundary_flags": manifested_routed_next_gate_run_preflight.get("boundary_flags", {}),
    }


def build_command_execute_request(
    confirm_command_execute: bool,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    return {
        "confirm_command_execute": confirm_command_execute,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
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
        "ran_manifested_routed_next_gate_command": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "ready_to_execute_manifested_routed_next_gate_command":
        return {
            "id": "delegate_manifested_routed_next_gate_command_execute",
            "label": "Delegate manifested routed next-gate command execute",
            "description": "P7-BD may call the existing command execute component now that confirmation is present.",
        }
    if status == "manifested_routed_next_gate_command_execute_gate_entry_executed":
        return {
            "id": "review_manifested_routed_next_gate_command_execute_result",
            "label": "Review manifested routed next-gate command execute result",
            "description": f"The `{route_type}` command executed; review the delegated result before continuing.",
        }
    if status == "blocked_by_missing_manifested_routed_next_gate_command_execute_confirmation":
        return {
            "id": "rerun_with_confirm_command_execute",
            "label": "Rerun with explicit command execution confirmation",
            "description": "P7-BD requires --confirm-command-execute before delegation.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_metadata":
        return {
            "id": "record_command_execute_reviewer_and_note",
            "label": "Record command execution reviewer and note",
            "description": "P7-BD requires reviewer and note before delegation.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_input_contract":
        return {
            "id": "repair_manifested_routed_next_gate_run_input_record",
            "label": "Repair P7-BC run input record",
            "description": "P7-BC must expose one input record matching its command plan.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_boundary":
        return {
            "id": "resolve_manifested_routed_next_gate_command_execute_boundary",
            "label": "Resolve command execute gate boundary",
            "description": "P7-BD cannot consume a run preflight that already crossed execution boundaries.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_unavailable":
        return {
            "id": "restore_manifested_routed_next_gate_command",
            "label": "Restore delegated next-gate command",
            "description": "The command file referenced by P7-BC is missing.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_delegation":
        return {
            "id": "repair_delegated_command_execution",
            "label": "Repair delegated command execution",
            "description": "P7-BD delegated to the existing execute component, but it did not complete successfully.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_manifested_routed_next_gate_run_preflight_blockers",
        "label": "Resolve P7-BC blockers",
        "description": "P7-BC must be ready before P7-BD can execute the routed next-gate command.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_GATE_ENTRY_PATH,
    review_path: Path = DEFAULT_GATE_ENTRY_REVIEW_PATH,
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Execute Gate Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        "- command execute gate entry 已执行："
        f"{str(report['command_execute_gate_entry_executed']).lower()}",
        f"- manifested command execute status：`{report['manifested_command_execute_status']}`",
        f"- delegated command 数：{len(report['delegated_command'])}",
        f"- 已运行下一关命令：{str(report['next_gate_command_executed']).lower()}",
        f"- 本命令运行下一关命令：{str(report['this_command_ran_next_gate_command']).lower()}",
        f"- 已进入下一关：{str(report['next_gate_entered']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["delegated_command"]:
        lines.extend(["", "## Delegated Command"])
        lines.append(f"- `{' '.join(report['delegated_command'])}`")
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

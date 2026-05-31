from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry import (
    run_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_outputs,
)


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry_execute_gate.v1"
)
GATE_ENTRY_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry.v1"
)
SOURCE_READY_STATUS = "ready_for_manifested_routed_downstream_execute_result_continuation_gate_entry"
EXPORT_DRY_RUN_STATUS = (
    "manifested_routed_downstream_execute_result_continuation_artifact_executor_entry_dry_run_ready"
)
MANUAL_DRY_RUN_STATUS = (
    "manifested_routed_downstream_execute_result_continuation_product_review_packet_preparation_dry_run_ready"
)
EXPORT_READY_TO_ENTER_STATUS = (
    "ready_to_enter_manifested_routed_downstream_execute_result_continuation_artifact_executor_entry"
)
EXPORT_ENTERED_STATUS = (
    "manifested_routed_downstream_execute_result_continuation_artifact_executor_entry_entered"
)
MANUAL_RECORDED_STATUS = (
    "manifested_routed_downstream_execute_result_continuation_product_review_packet_preparation_recorded"
)
DEFAULT_GATE_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry.json"
)
DEFAULT_EXECUTE_GATE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry_execute_gate.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry_execute_gate.md"
)
ARTIFACT_ENTRY_REPORT_PATH = (
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
)
ARTIFACT_ENTRY_REVIEW_PATH = (
    "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.md"
)
ARTIFACT_ENTRY_COMMAND_PATH = (
    "Program/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.py"
)
VALID_MODES = {"dry-run", "execute"}
EXPORT_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
    project_root: Path,
    gate_entry: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_downstream_execute_result_continuation: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
        project_root,
        gate_entry,
        mode=mode,
        confirm_downstream_execute_result_continuation=confirm_downstream_execute_result_continuation,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != EXPORT_READY_TO_ENTER_STATUS:
        return report, 0 if report["status"] in {EXPORT_DRY_RUN_STATUS, MANUAL_DRY_RUN_STATUS, MANUAL_RECORDED_STATUS} else 2

    route_entry_report, route_entry_exit_code = (
        run_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
            project_root,
            build_route_specific_artifact_executor_entry_source(gate_entry, report["continuation_input_record"]),
            mode="execute",
            confirm_artifact_executor_entry=True,
            reviewer=reviewer,
            note=note,
            source_paths={
                "next_gate_selected_route_execute_result_review": (
                    "derived_from_p7_bm_downstream_execute_result_continuation_gate_entry"
                ),
            },
            repo_root=repo_root,
        )
    )
    route_entry_report_path, route_entry_review_path = (
        write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_outputs(
            project_root,
            route_entry_report,
            Path(report["route_specific_artifact_executor_entry_report_path"]),
            Path(report["route_specific_artifact_executor_entry_review_path"]),
        )
    )

    report["continuation_execute_command_executed"] = True
    report["this_command_ran_continuation_command"] = True
    report["route_specific_artifact_executor_entry_returncode"] = route_entry_exit_code
    report["route_specific_artifact_executor_entry_status"] = route_entry_report.get("status", "")
    report["route_specific_artifact_executor_entry_result"] = {
        "returncode": route_entry_exit_code,
        "status": route_entry_report.get("status", ""),
        "report_path": str(route_entry_report_path.relative_to(project_root)),
        "review_path": str(route_entry_review_path.relative_to(project_root)),
    }
    if route_entry_exit_code == 0 and route_entry_report.get("status") == "next_gate_route_specific_artifact_executor_entered":
        report["status"] = EXPORT_ENTERED_STATUS
        report["blocking_reasons"] = []
        report["route_specific_artifact_executor_entry_entered"] = True
        copy_route_entry_flags(report, route_entry_report)
        report["next_action"] = build_next_action(report["status"], [], report["continuation_kind"])
        return report, 0

    report["status"] = "blocked_by_downstream_execute_result_continuation_artifact_executor_entry_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            "route_specific_artifact_executor_entry_failed",
            f"route_specific_artifact_executor_entry_status:{route_entry_report.get('status', 'missing')}",
        ]
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["continuation_kind"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
    project_root: Path,
    gate_entry: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_downstream_execute_result_continuation: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    source_reasons = build_source_blocking_reasons(gate_entry)
    boundary_reasons = build_boundary_blocking_reasons(gate_entry) if not source_reasons else []
    contract_reasons = (
        build_continuation_input_contract_blocking_reasons(gate_entry)
        if not source_reasons and not boundary_reasons
        else []
    )
    record = extract_continuation_input_record(gate_entry)
    unavailable_reasons = (
        build_command_unavailable_reasons(record, repo_root)
        if not source_reasons and not boundary_reasons and not contract_reasons
        else []
    )
    request_reasons = build_request_blocking_reasons(
        mode,
        confirm_downstream_execute_result_continuation,
        reviewer,
        note,
    )
    status = build_status(
        gate_entry.get("continuation_kind", ""),
        mode,
        source_reasons,
        boundary_reasons,
        contract_reasons,
        unavailable_reasons,
        request_reasons,
    )
    can_execute = not source_reasons and not boundary_reasons and not contract_reasons and not unavailable_reasons
    continuation_kind = gate_entry.get("continuation_kind", "") if can_execute else ""
    command = (
        build_continuation_execute_command(project_root, record)
        if status in {EXPORT_DRY_RUN_STATUS, EXPORT_READY_TO_ENTER_STATUS}
        else []
    )
    product_review_records = (
        [build_product_review_packet_preparation_record(record, reviewer, note)]
        if status == MANUAL_RECORDED_STATUS
        else []
    )
    blocking_reasons = dedupe(source_reasons + boundary_reasons + contract_reasons + unavailable_reasons + request_reasons)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": gate_entry.get("topic", ""),
        "source_paths": {
            "manifested_routed_downstream_execute_result_continuation_gate_entry": source_paths.get(
                "manifested_routed_downstream_execute_result_continuation_gate_entry",
                str(DEFAULT_GATE_ENTRY_PATH),
            ),
        },
        "source_status": gate_entry.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_downstream_execute_result_continuation": confirm_downstream_execute_result_continuation,
        "verified_route_type": gate_entry.get("verified_route_type", "") if can_execute else "",
        "routed_next_gate": gate_entry.get("routed_next_gate", "") if can_execute else "",
        "downstream_kind": gate_entry.get("downstream_kind", "") if can_execute else "",
        "continuation_kind": continuation_kind,
        "can_execute_downstream_execute_result_continuation_with_confirmation": can_execute,
        "requires_explicit_continuation_command": record.get("requires_explicit_continuation_command") is True
        if can_execute
        else False,
        "continuation_execute_command": command,
        "continuation_execute_command_executed": False,
        "this_command_ran_continuation_command": False,
        "route_specific_artifact_executor_entry_entered": False,
        "route_specific_artifact_executor_entry_report_path": record.get("next_report_path", "") if can_execute else "",
        "route_specific_artifact_executor_entry_review_path": record.get("next_review_path", "") if can_execute else "",
        "route_specific_artifact_executor_entry_returncode": None,
        "route_specific_artifact_executor_entry_status": "",
        "route_specific_artifact_executor_entry_result": {},
        "product_review_packet_preparation_recorded": status == MANUAL_RECORDED_STATUS,
        "product_review_packet_preparation_records": product_review_records,
        "route_specific_artifact_executed": False,
        "route_specific_command_executed": False,
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_gate_entry": build_source_gate_entry_summary(gate_entry),
        "continuation_input_record": record if can_execute else {},
        "execute_request": build_execute_request(
            mode,
            confirm_downstream_execute_result_continuation,
            reviewer,
            note,
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, continuation_kind),
    }


def build_source_blocking_reasons(gate_entry: dict[str, Any]) -> list[str]:
    reasons = []
    if gate_entry.get("schema_version") != GATE_ENTRY_SCHEMA_VERSION:
        reasons.append("manifested_routed_downstream_execute_result_continuation_gate_entry_missing_or_invalid_schema")
    if gate_entry.get("status") != SOURCE_READY_STATUS:
        reasons.append("manifested_routed_downstream_execute_result_continuation_gate_entry_not_ready")
    if gate_entry.get("downstream_execute_result_continuation_gate_entry_recorded") is not True:
        reasons.append("manifested_routed_downstream_execute_result_continuation_gate_entry_not_recorded")
    if gate_entry.get("can_request_downstream_execute_result_continuation") is not True:
        reasons.append("manifested_routed_downstream_execute_result_continuation_gate_entry_cannot_request_continuation")
    if not gate_entry.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if gate_entry.get("continuation_kind") not in {
        "route_specific_artifact_executor_continuation",
        "product_review_packet_continuation",
    }:
        reasons.append("continuation_kind_missing_or_unknown")
    if gate_entry.get("blocking_reasons"):
        reasons.append("source_downstream_execute_result_continuation_gate_entry_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(gate_entry: dict[str, Any]) -> list[str]:
    reasons = []
    if gate_entry.get("this_command_ran_continuation_command") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_ran_continuation_command")
    if gate_entry.get("route_specific_artifact_executed") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_executed_route_specific_artifact")
    if gate_entry.get("selected_route_executed") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_selected_route_executed")
    if gate_entry.get("export_or_acceptance_executed") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_executed_export_or_acceptance")
    if gate_entry.get("rendered_pdf") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_rendered_pdf")
    if gate_entry.get("rendered_docx") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_rendered_docx")
    if gate_entry.get("package_manifest_generated") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_generated_package_manifest")
    if gate_entry.get("manual_acceptance_performed") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_performed_manual_acceptance")
    if gate_entry.get("formal_writeback_executed") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_formal_writeback")
    if gate_entry.get("this_command_wrote_formal_state") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_wrote_formal_state")
    if gate_entry.get("can_write_product_state") is True:
        reasons.append("downstream_execute_result_continuation_gate_entry_allows_product_state_write")
    for flag, value in gate_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"downstream_execute_result_continuation_gate_entry_boundary_violation:{flag}")
    return dedupe(reasons)


def build_continuation_input_contract_blocking_reasons(gate_entry: dict[str, Any]) -> list[str]:
    records = gate_entry.get("continuation_input_records", [])
    if not isinstance(records, list) or not records:
        return ["continuation_input_record_missing"]
    if len(records) != 1:
        return ["continuation_input_record_not_single"]
    record = records[0]
    if gate_entry.get("continuation_kind") == "route_specific_artifact_executor_continuation":
        return build_export_continuation_record_blocking_reasons(gate_entry, record)
    if gate_entry.get("continuation_kind") == "product_review_packet_continuation":
        return build_manual_continuation_record_blocking_reasons(gate_entry, record)
    return ["continuation_kind_unknown"]


def build_export_continuation_record_blocking_reasons(
    gate_entry: dict[str, Any],
    record: dict[str, Any],
) -> list[str]:
    route_type = gate_entry.get("verified_route_type", "")
    reasons = []
    if route_type not in EXPORT_ROUTE_TYPES:
        reasons.append(f"route_specific_artifact_executor_continuation_route_type_not_allowed:{route_type}")
    if record.get("record_id") != (
        "manifested_routed_downstream_execute_result_continuation::"
        f"route_specific_artifact_executor::{route_type}"
    ):
        reasons.append(f"continuation_input_record_id_mismatch:{route_type}")
    if record.get("verified_route_type") != route_type:
        reasons.append(f"continuation_input_record_route_type_mismatch:{route_type}")
    if record.get("continuation_kind") != "route_specific_artifact_executor_continuation":
        reasons.append(f"continuation_input_record_kind_mismatch:{route_type}")
    if record.get("review_status") != "route_specific_artifact_executor_input_accepted_for_continuation":
        reasons.append(f"route_specific_artifact_executor_continuation_record_not_accepted:{route_type}")
    if record.get("can_continue_to_route_specific_artifact_executor_entry") is not True:
        reasons.append(f"route_specific_artifact_executor_continuation_record_cannot_continue:{route_type}")
    if record.get("command_path") != ARTIFACT_ENTRY_COMMAND_PATH:
        reasons.append(f"route_specific_artifact_executor_continuation_command_path_mismatch:{route_type}")
    if record.get("next_report_path") != ARTIFACT_ENTRY_REPORT_PATH:
        reasons.append(f"route_specific_artifact_executor_continuation_report_path_mismatch:{route_type}")
    if record.get("next_review_path") != ARTIFACT_ENTRY_REVIEW_PATH:
        reasons.append(f"route_specific_artifact_executor_continuation_review_path_mismatch:{route_type}")
    for field in [
        "selected_route_execute_report_path",
        "selected_route_execute_manifest_path",
        "operation_id",
        "route_execution_id",
        "routed_action",
        "route_specific_next_command",
        "planned_outputs",
    ]:
        if not record.get(field):
            reasons.append(f"route_specific_artifact_executor_continuation_{field}_missing:{route_type}")
    return dedupe(reasons)


def build_manual_continuation_record_blocking_reasons(
    gate_entry: dict[str, Any],
    record: dict[str, Any],
) -> list[str]:
    route_type = gate_entry.get("verified_route_type", "")
    reasons = []
    if route_type != "manual_acceptance":
        reasons.append(f"product_review_packet_continuation_route_type_not_allowed:{route_type}")
    if record.get("record_id") != (
        "manifested_routed_downstream_execute_result_continuation::"
        "product_review_packet::manual_acceptance"
    ):
        reasons.append("product_review_packet_continuation_record_id_mismatch")
    if record.get("verified_route_type") != "manual_acceptance":
        reasons.append(f"product_review_packet_continuation_route_type_mismatch:{route_type}")
    if record.get("continuation_kind") != "product_review_packet_continuation":
        reasons.append(f"product_review_packet_continuation_record_kind_mismatch:{route_type}")
    if record.get("review_status") != "product_review_preparation_result_accepted_for_product_review_packet_continuation":
        reasons.append(f"product_review_packet_continuation_record_not_accepted:{route_type}")
    if record.get("can_continue_to_product_review_packet") is not True:
        reasons.append(f"product_review_packet_continuation_record_cannot_continue:{route_type}")
    if record.get("command_path") != "":
        reasons.append(f"product_review_packet_continuation_command_path_mismatch:{route_type}")
    if record.get("terminal_status") != "terminal_delivery_completion_ready_for_product_review":
        reasons.append(f"product_review_packet_continuation_terminal_status_mismatch:{route_type}")
    if record.get("terminal_completion") is not True:
        reasons.append(f"product_review_packet_continuation_terminal_completion_missing:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(record: dict[str, Any], repo_root: Path) -> list[str]:
    command_path = record.get("command_path", "")
    if not command_path:
        return []
    if not (repo_root / command_path).exists():
        return [f"downstream_execute_result_continuation_command_file_missing:{command_path}"]
    return []


def build_request_blocking_reasons(
    mode: str,
    confirm_downstream_execute_result_continuation: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["downstream_execute_result_continuation_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_downstream_execute_result_continuation:
        reasons.append("confirm_downstream_execute_result_continuation_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("downstream_execute_result_continuation_note_required")
    return reasons


def build_status(
    continuation_kind: str,
    mode: str,
    source_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if source_reasons:
        return "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry"
    if boundary_reasons:
        return "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry_boundary"
    if contract_reasons:
        return "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry_contract"
    if unavailable_reasons:
        return "blocked_by_downstream_execute_result_continuation_command_unavailable"
    if "downstream_execute_result_continuation_mode_invalid" in request_reasons:
        return "blocked_by_downstream_execute_result_continuation_execute_mode"
    if mode == "dry-run" and continuation_kind == "route_specific_artifact_executor_continuation":
        return EXPORT_DRY_RUN_STATUS
    if mode == "dry-run":
        return MANUAL_DRY_RUN_STATUS
    if "confirm_downstream_execute_result_continuation_required" in request_reasons:
        return "blocked_by_missing_downstream_execute_result_continuation_execute_confirmation"
    if request_reasons:
        return "blocked_by_downstream_execute_result_continuation_execute_metadata"
    if continuation_kind == "route_specific_artifact_executor_continuation":
        return EXPORT_READY_TO_ENTER_STATUS
    return MANUAL_RECORDED_STATUS


def extract_continuation_input_record(gate_entry: dict[str, Any]) -> dict[str, Any]:
    records = gate_entry.get("continuation_input_records", [])
    if isinstance(records, list) and len(records) == 1 and isinstance(records[0], dict):
        return records[0]
    return {}


def build_continuation_execute_command(project_root: Path, record: dict[str, Any]) -> list[str]:
    return [
        "python3",
        record.get("command_path", ARTIFACT_ENTRY_COMMAND_PATH),
        "--project-root",
        str(project_root),
        "--next-gate-selected-route-execute-result-review",
        "derived_from_p7_bm_downstream_execute_result_continuation_gate_entry",
        "--mode",
        "execute",
        "--confirm-artifact-executor-entry",
        "--output-entry",
        record.get("next_report_path", ARTIFACT_ENTRY_REPORT_PATH),
        "--output-review",
        record.get("next_review_path", ARTIFACT_ENTRY_REVIEW_PATH),
    ]


def build_route_specific_artifact_executor_entry_source(
    gate_entry: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    route_type = record.get("verified_route_type", "")
    return {
        "schema_version": "p7.auto_mode_formal_package_next_gate_selected_route_execute_result_review.v1",
        "generated_at": utc_now(),
        "topic": gate_entry.get("topic", ""),
        "source_status": "derived_from_manifested_routed_downstream_execute_result_continuation_gate_entry",
        "status": "next_gate_selected_route_execute_result_review_ready",
        "verified_route_type": route_type,
        "selected_route_execute_status": "selected_route_execute_manifest_recorded",
        "selected_route_execute_result_reviewed": True,
        "can_continue_to_route_specific_artifact_executor": True,
        "selected_route_execute_command_executed": True,
        "this_command_ran_selected_route_execute_command": False,
        "selected_route_execute_manifest_recorded": True,
        "route_specific_artifact_executed": False,
        "route_specific_command_executed": False,
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "route_specific_artifact_executor_input_records": [
            {
                "record_id": f"selected_route_execute_result::{route_type}",
                "verified_route_type": route_type,
                "selected_route_execute_status": "selected_route_execute_manifest_recorded",
                "selected_route_execute_report_path": record.get("selected_route_execute_report_path", ""),
                "selected_route_execute_manifest_path": record.get("selected_route_execute_manifest_path", ""),
                "operation_id": record.get("operation_id", ""),
                "route_execution_id": record.get("route_execution_id", ""),
                "routed_action": record.get("routed_action", ""),
                "next_command": record.get("route_specific_next_command", ""),
                "planned_outputs": record.get("planned_outputs", []),
                "review_status": "selected_route_execute_manifest_accepted_for_route_specific_artifact_executor",
                "can_continue_to_route_specific_artifact_executor": True,
            }
        ],
        "blocking_reasons": [],
        "boundary_flags": build_boundary_flags(),
    }


def copy_route_entry_flags(report: dict[str, Any], route_entry_report: dict[str, Any]) -> None:
    for field in [
        "route_specific_command_executed",
        "route_specific_artifact_executed",
        "selected_route_executed",
        "export_or_acceptance_executed",
        "rendered_pdf",
        "rendered_docx",
        "package_manifest_generated",
        "manual_acceptance_performed",
        "formal_writeback_executed",
        "this_command_wrote_formal_state",
        "can_write_product_state",
    ]:
        report[field] = route_entry_report.get(field) is True


def build_product_review_packet_preparation_record(
    record: dict[str, Any],
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    return {
        "record_id": "product_review_packet_preparation::manual_acceptance",
        "verified_route_type": "manual_acceptance",
        "continuation_kind": "product_review_packet_continuation",
        "next_report_path": record.get("next_report_path", ""),
        "next_review_path": record.get("next_review_path", ""),
        "source_product_review_preparation_report_path": record.get(
            "source_product_review_preparation_report_path",
            "",
        ),
        "source_product_review_preparation_review_path": record.get(
            "source_product_review_preparation_review_path",
            "",
        ),
        "terminal_status": record.get("terminal_status", ""),
        "terminal_completion": record.get("terminal_completion") is True,
        "reviewer": reviewer,
        "note": note,
        "preparation_status": "product_review_packet_preparation_recorded",
    }


def build_source_gate_entry_summary(gate_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": gate_entry.get("schema_version", ""),
        "status": gate_entry.get("status", ""),
        "verified_route_type": gate_entry.get("verified_route_type", ""),
        "continuation_kind": gate_entry.get("continuation_kind", ""),
        "downstream_execute_result_continuation_gate_entry_recorded": (
            gate_entry.get("downstream_execute_result_continuation_gate_entry_recorded") is True
        ),
        "can_request_downstream_execute_result_continuation": (
            gate_entry.get("can_request_downstream_execute_result_continuation") is True
        ),
        "continuation_input_records_count": len(gate_entry.get("continuation_input_records", []) or []),
        "source_blocking_reasons": gate_entry.get("blocking_reasons", []),
        "boundary_flags": gate_entry.get("boundary_flags", {}),
    }


def build_execute_request(
    mode: str,
    confirm_downstream_execute_result_continuation: bool,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_downstream_execute_result_continuation": confirm_downstream_execute_result_continuation,
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
    }


def build_next_action(status: str, blocking_reasons: list[str], continuation_kind: str) -> dict[str, Any]:
    if status == EXPORT_DRY_RUN_STATUS:
        return {
            "id": "rerun_with_confirm_downstream_execute_result_continuation",
            "label": "Confirm artifact executor entry continuation",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note to enter the route-specific artifact executor entry.",
        }
    if status == MANUAL_DRY_RUN_STATUS:
        return {
            "id": "rerun_with_confirm_product_review_packet_preparation",
            "label": "Confirm product-review packet preparation",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note to record product-review packet preparation.",
        }
    if status == EXPORT_READY_TO_ENTER_STATUS:
        return {
            "id": "enter_route_specific_artifact_executor_entry",
            "label": "Enter route-specific artifact executor entry",
            "description": "The route-specific artifact executor entry dry-run command is ready to run.",
        }
    if status == EXPORT_ENTERED_STATUS:
        return {
            "id": "review_route_specific_artifact_executor_entry",
            "label": "Review route-specific artifact executor entry",
            "description": "P7-BM entered the route-specific artifact executor entry dry-run.",
        }
    if status == MANUAL_RECORDED_STATUS:
        return {
            "id": "prepare_product_review_packet",
            "label": "Prepare product-review packet",
            "description": "P7-BM recorded product-review packet preparation for the manual terminal branch.",
        }
    if status == "blocked_by_missing_downstream_execute_result_continuation_execute_confirmation":
        return {
            "id": "rerun_with_explicit_downstream_execute_result_continuation_confirmation",
            "label": "Rerun with explicit continuation confirmation",
            "description": "Execute mode requires --confirm-downstream-execute-result-continuation.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_downstream_execute_result_continuation_execute_metadata":
        return {
            "id": "record_downstream_execute_result_continuation_reviewer_and_note",
            "label": "Record reviewer and note",
            "description": "Execute mode requires reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry_contract":
        return {
            "id": "repair_downstream_execute_result_continuation_execute_contract",
            "label": "Repair continuation execute contract",
            "description": "P7-BL must expose exactly one accepted continuation input record.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry_boundary":
        return {
            "id": "repair_downstream_execute_result_continuation_execute_boundary",
            "label": "Repair continuation boundary",
            "description": "P7-BL must remain an entry record without formal execution side effects.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_downstream_execute_result_continuation_artifact_executor_entry_failure":
        return {
            "id": "repair_artifact_executor_entry_inputs",
            "label": "Repair artifact executor entry inputs",
            "description": "The route-specific artifact executor entry did not reach its dry-run entered state.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_downstream_execute_result_continuation_command_unavailable":
        return {
            "id": "restore_downstream_execute_result_continuation_command",
            "label": "Restore continuation command",
            "description": "The command file named by the continuation record is unavailable.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_p7_bl_continuation_gate_entry_blockers",
        "label": "Resolve P7-BL blockers",
        "description": f"P7-BL must be ready before P7-BM can execute {continuation_kind or 'the continuation'}.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTE_GATE_PATH,
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
        "# Auto Mode Formal Package Manifested Routed Downstream Execute Result Continuation Gate Entry Execute Gate",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- continuation kind：`{report['continuation_kind']}`",
        "- 可确认执行 downstream execute result continuation："
        f"{str(report['can_execute_downstream_execute_result_continuation_with_confirmation']).lower()}",
        "- 需要显式 continuation command："
        f"{str(report['requires_explicit_continuation_command']).lower()}",
        f"- continuation execute command 数：{len(report['continuation_execute_command'])}",
        "- 已运行 continuation execute command："
        f"{str(report['continuation_execute_command_executed']).lower()}",
        "- 本命令运行 continuation command："
        f"{str(report['this_command_ran_continuation_command']).lower()}",
        "- 已进入 route-specific artifact executor entry："
        f"{str(report['route_specific_artifact_executor_entry_entered']).lower()}",
        "- product-review packet preparation 已记录："
        f"{str(report['product_review_packet_preparation_recorded']).lower()}",
        f"- product-review preparation records：{len(report['product_review_packet_preparation_records'])}",
        f"- 已执行 route-specific artifact：{str(report['route_specific_artifact_executed']).lower()}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 已渲染 PDF：{str(report['rendered_pdf']).lower()}",
        f"- 已渲染 DOCX：{str(report['rendered_docx']).lower()}",
        f"- 已生成 package manifest：{str(report['package_manifest_generated']).lower()}",
        f"- 已执行人工验收：{str(report['manual_acceptance_performed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["continuation_execute_command"]:
        lines.extend(["", "## Continuation Execute Command"])
        lines.append("```text")
        lines.append(" ".join(report["continuation_execute_command"]))
        lines.append("```")
    if report["product_review_packet_preparation_records"]:
        lines.extend(["", "## Product Review Packet Preparation"])
        for record in report["product_review_packet_preparation_records"]:
            lines.append(f"- `{record['record_id']}`: {record['preparation_status']}")
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

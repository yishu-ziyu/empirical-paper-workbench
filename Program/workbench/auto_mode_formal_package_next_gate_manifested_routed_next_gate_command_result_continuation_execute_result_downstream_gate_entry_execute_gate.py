from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate.v1"
)
GATE_ENTRY_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry.v1"
)
GATE_ENTRY_READY_STATUS = (
    "ready_for_manifested_routed_next_gate_result_continuation_execute_downstream_gate_entry"
)
DEFAULT_GATE_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry.json"
)
DEFAULT_EXECUTE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate.md"
)
SELECTED_ROUTE_EXECUTE_COMMAND_PATH = "Program/auto_mode_formal_package_selected_route_execute.py"
SELECTED_ROUTE_EXECUTE_REPORT_PATH = "Results/json/auto_mode_formal_package_selected_route_execute.json"
SELECTED_ROUTE_EXECUTE_REVIEW_PATH = "Reviews/auto_mode_formal_package_selected_route_execute.md"
SELECTED_ROUTE_EXECUTE_MANIFEST_PATH = (
    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
)
VALID_MODES = {"dry-run", "execute"}
EXPORT_ROUTES = {"pdf_export", "docx_export", "package_manifest"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
    project_root: Path,
    downstream_gate_entry: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_downstream_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
        project_root,
        downstream_gate_entry,
        mode=mode,
        confirm_downstream_execute=confirm_downstream_execute,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_execute_manifested_routed_next_gate_downstream":
        return (
            report,
            0
            if report["status"]
            in {
                "manifested_routed_next_gate_downstream_execute_dry_run_ready",
                "manifested_routed_next_gate_downstream_product_review_preparation_dry_run_ready",
            }
            else 2,
        )
    if report["downstream_kind"] == "product_review_preparation":
        report["status"] = (
            "manifested_routed_next_gate_downstream_product_review_preparation_recorded"
        )
        report["product_review_preparation_recorded"] = True
        report["blocking_reasons"] = []
        report["next_action"] = build_next_action(report["status"], [], report["downstream_kind"])
        return report, 0

    result = subprocess.run(
        report["downstream_execute_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    selected_route_execute_report = load_json_or_empty(
        project_root / SELECTED_ROUTE_EXECUTE_REPORT_PATH
    )
    selected_route_execute_status = selected_route_execute_report.get("status", "")
    report["downstream_execute_command_executed"] = True
    report["this_command_ran_downstream_command"] = True
    report["downstream_execute_returncode"] = result.returncode
    report["downstream_execute_status"] = selected_route_execute_status
    report["downstream_execute_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": selected_route_execute_status,
        "report_path": SELECTED_ROUTE_EXECUTE_REPORT_PATH,
        "review_path": SELECTED_ROUTE_EXECUTE_REVIEW_PATH,
        "manifest_path": SELECTED_ROUTE_EXECUTE_MANIFEST_PATH,
        "selected_route_execute_report_summary": build_selected_route_execute_report_summary(
            selected_route_execute_report
        ),
    }
    if (
        result.returncode == 0
        and selected_route_execute_status == "selected_route_execute_manifest_recorded"
    ):
        report["status"] = (
            "manifested_routed_next_gate_downstream_selected_route_execute_command_executed"
        )
        report["selected_route_execute_manifest_recorded"] = (
            selected_route_execute_report.get("selected_route_execute_manifest_recorded") is True
        )
        report["selected_route_executed"] = (
            selected_route_execute_report.get("selected_route_executed") is True
        )
        report["export_or_acceptance_executed"] = (
            selected_route_execute_report.get("export_or_acceptance_executed") is True
        )
        report["blocking_reasons"] = []
        report["next_action"] = build_next_action(report["status"], [], report["downstream_kind"])
        return report, 0

    report["status"] = "blocked_by_manifested_routed_next_gate_downstream_execute_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"downstream_execute_command_failed:{report['verified_route_type']}",
            f"selected_route_execute_status:{selected_route_execute_status or 'missing'}",
        ]
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["downstream_kind"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate(
    project_root: Path,
    downstream_gate_entry: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_downstream_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    gate_reasons = build_gate_entry_blocking_reasons(downstream_gate_entry)
    contract_reasons = (
        build_downstream_input_contract_blocking_reasons(downstream_gate_entry)
        if not gate_reasons
        else []
    )
    unavailable_reasons = (
        build_command_unavailable_reasons(downstream_gate_entry, repo_root)
        if not gate_reasons and not contract_reasons
        else []
    )
    request_reasons = build_request_blocking_reasons(
        mode,
        confirm_downstream_execute,
        reviewer,
        note,
    )
    status = build_status(
        mode,
        gate_reasons,
        contract_reasons,
        unavailable_reasons,
        request_reasons,
        downstream_gate_entry,
    )
    can_execute = not gate_reasons and not contract_reasons and not unavailable_reasons
    record = extract_downstream_record(downstream_gate_entry)
    downstream_kind = record.get("downstream_kind", "") if can_execute else ""
    command = (
        build_selected_route_execute_command(project_root, record, mode, reviewer, note)
        if can_execute and downstream_kind == "selected_route_execution"
        else []
    )
    blocking_reasons = dedupe(
        gate_reasons + contract_reasons + unavailable_reasons + request_reasons
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": downstream_gate_entry.get("topic", ""),
        "source_paths": {
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry": (
                source_paths.get(
                    "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry",
                    str(DEFAULT_GATE_ENTRY_PATH),
                )
            ),
        },
        "source_status": downstream_gate_entry.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_downstream_execute": confirm_downstream_execute,
        "verified_route_type": record.get("verified_route_type", "") if can_execute else "",
        "routed_next_gate": record.get("routed_next_gate", "") if can_execute else "",
        "downstream_kind": downstream_kind,
        "downstream_status": record.get("downstream_status", "") if can_execute else "",
        "can_execute_downstream_with_confirmation": can_execute,
        "requires_explicit_downstream_command": (
            record.get("requires_explicit_downstream_command") is True if can_execute else False
        ),
        "downstream_execute_command": (
            command
            if status
            in {
                "manifested_routed_next_gate_downstream_execute_dry_run_ready",
                "ready_to_execute_manifested_routed_next_gate_downstream",
            }
            else []
        ),
        "downstream_execute_command_executed": False,
        "this_command_ran_downstream_command": False,
        "downstream_execute_returncode": None,
        "downstream_execute_status": "",
        "downstream_execute_result": {},
        "selected_route_execute_manifest_recorded": False,
        "product_review_preparation_recorded": False,
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
        "source_downstream_gate_entry": build_source_gate_entry_summary(downstream_gate_entry),
        "downstream_execute_request": build_downstream_execute_request(
            mode,
            confirm_downstream_execute,
            reviewer,
            note,
        ),
        "downstream_input_record": record if can_execute else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, downstream_kind),
    }


def build_gate_entry_blocking_reasons(downstream_gate_entry: dict[str, Any]) -> list[str]:
    reasons = []
    if downstream_gate_entry.get("schema_version") != GATE_ENTRY_SCHEMA_VERSION:
        reasons.append(
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_missing_or_invalid_schema"
        )
    if downstream_gate_entry.get("status") != GATE_ENTRY_READY_STATUS:
        reasons.append(
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_not_ready"
        )
    if downstream_gate_entry.get("downstream_gate_entry_recorded") is not True:
        reasons.append("manifested_routed_next_gate_downstream_gate_entry_not_recorded")
    if (
        downstream_gate_entry.get(
            "can_request_manifested_routed_next_gate_result_continuation_downstream"
        )
        is not True
    ):
        reasons.append(
            "manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry_cannot_request_downstream"
        )
    if downstream_gate_entry.get("blocking_reasons"):
        reasons.append("source_downstream_gate_entry_has_blocking_reasons")
    if downstream_gate_entry.get("downstream_command_executed") is True:
        reasons.append("source_downstream_gate_entry_already_executed_downstream_command")
    if downstream_gate_entry.get("this_command_ran_downstream_command") is True:
        reasons.append("source_downstream_gate_entry_ran_downstream_command")
    if downstream_gate_entry.get("selected_route_executed") is True:
        reasons.append("source_downstream_gate_entry_selected_route_executed")
    if downstream_gate_entry.get("export_or_acceptance_executed") is True:
        reasons.append("source_downstream_gate_entry_export_or_acceptance_executed")
    if downstream_gate_entry.get("formal_writeback_executed") is True:
        reasons.append("source_downstream_gate_entry_formal_writeback_executed")
    if downstream_gate_entry.get("this_command_wrote_formal_state") is True:
        reasons.append("source_downstream_gate_entry_wrote_formal_state")
    if downstream_gate_entry.get("can_write_product_state") is True:
        reasons.append("source_downstream_gate_entry_allows_product_state_write")
    for flag, value in downstream_gate_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"source_downstream_gate_entry_boundary_violation:{flag}")
    return dedupe(reasons)


def build_downstream_input_contract_blocking_reasons(
    downstream_gate_entry: dict[str, Any],
) -> list[str]:
    records = downstream_gate_entry.get("downstream_input_records", []) or []
    if not records:
        return ["downstream_input_record_missing"]
    if len(records) != 1:
        return ["downstream_input_record_not_single"]

    record = records[0]
    route_type = downstream_gate_entry.get("verified_route_type", "")
    routed_next_gate = downstream_gate_entry.get("routed_next_gate", "")
    expected_kind = downstream_gate_entry.get("downstream_kind", "")
    reasons = []
    if record.get("verified_route_type") != route_type:
        reasons.append(f"downstream_record_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != routed_next_gate:
        reasons.append(f"downstream_record_gate_mismatch:{routed_next_gate}")
    if record.get("downstream_kind") != expected_kind:
        reasons.append(f"downstream_record_kind_mismatch:{expected_kind}")
    if record.get("downstream_status") != downstream_gate_entry.get("downstream_status", ""):
        reasons.append(f"downstream_record_status_mismatch:{route_type}")
    if record.get("will_run_downstream_command_by_this_command") is True:
        reasons.append(f"downstream_record_marked_run_by_source:{route_type}")
    if record.get("will_execute_selected_route_by_this_command") is True:
        reasons.append(f"downstream_record_marked_selected_route_execution:{route_type}")
    if record.get("will_execute_export_or_acceptance_by_this_command") is True:
        reasons.append(f"downstream_record_marked_export_or_acceptance:{route_type}")
    if record.get("will_write_product_state_by_this_command") is True:
        reasons.append(f"downstream_record_marked_product_state_write:{route_type}")
    for key in ["source_report_path", "source_review_path", "next_report_path", "next_review_path"]:
        path = record.get(key, "")
        if not is_safe_relative_path(path):
            reasons.append(f"downstream_record_{key}_unsafe:{path}")

    if expected_kind == "selected_route_execution":
        reasons.extend(build_selected_route_record_reasons(record, route_type, routed_next_gate))
    elif expected_kind == "product_review_preparation":
        reasons.extend(build_product_review_record_reasons(record, route_type, routed_next_gate))
    else:
        reasons.append(f"downstream_kind_unknown:{expected_kind}")
    return dedupe(reasons)


def build_selected_route_record_reasons(
    record: dict[str, Any],
    route_type: str,
    routed_next_gate: str,
) -> list[str]:
    reasons = []
    if route_type not in EXPORT_ROUTES:
        reasons.append(f"downstream_selected_route_type_not_export:{route_type}")
    if routed_next_gate != "formal_package_export_acceptance_router":
        reasons.append(f"downstream_selected_route_gate_mismatch:{routed_next_gate}")
    if record.get("requires_explicit_downstream_command") is not True:
        reasons.append(f"downstream_selected_route_missing_explicit_command:{route_type}")
    if record.get("terminal_completion") is True:
        reasons.append(f"downstream_selected_route_marked_terminal:{route_type}")
    if record.get("source_report_path") != (
        "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
    ):
        reasons.append(f"downstream_selected_route_source_report_mismatch:{route_type}")
    if not record.get("route_specific_next_command"):
        reasons.append(f"downstream_selected_route_next_command_missing:{route_type}")
    if not record.get("planned_outputs"):
        reasons.append(f"downstream_selected_route_outputs_missing:{route_type}")
    return reasons


def build_product_review_record_reasons(
    record: dict[str, Any],
    route_type: str,
    routed_next_gate: str,
) -> list[str]:
    reasons = []
    if route_type != "manual_acceptance":
        reasons.append(f"downstream_product_review_route_type_mismatch:{route_type}")
    if routed_next_gate != "formal_package_delivery_completion_gate":
        reasons.append(f"downstream_product_review_gate_mismatch:{routed_next_gate}")
    if record.get("requires_explicit_downstream_command") is True:
        reasons.append("downstream_product_review_unexpected_explicit_command")
    if record.get("terminal_completion") is not True:
        reasons.append("downstream_product_review_not_terminal")
    if record.get("command_path"):
        reasons.append("downstream_product_review_command_path_not_empty")
    if record.get("terminal_status") != "terminal_delivery_completion_ready_for_product_review":
        reasons.append(f"downstream_product_review_terminal_status_mismatch:{route_type}")
    return reasons


def build_command_unavailable_reasons(
    downstream_gate_entry: dict[str, Any],
    repo_root: Path,
) -> list[str]:
    record = extract_downstream_record(downstream_gate_entry)
    if record.get("downstream_kind") != "selected_route_execution":
        return []
    command_path = repo_root / SELECTED_ROUTE_EXECUTE_COMMAND_PATH
    if not command_path.exists():
        return [f"selected_route_execute_command_file_missing:{SELECTED_ROUTE_EXECUTE_COMMAND_PATH}"]
    return []


def build_request_blocking_reasons(
    mode: str,
    confirm_downstream_execute: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["downstream_execute_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_downstream_execute:
        reasons.append("confirm_downstream_execute_required")
    if not reviewer.strip():
        reasons.append("downstream_execute_reviewer_required")
    if not note.strip():
        reasons.append("downstream_execute_note_required")
    return reasons


def build_status(
    mode: str,
    gate_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
    request_reasons: list[str],
    downstream_gate_entry: dict[str, Any],
) -> str:
    if gate_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_gate_entry"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_downstream_execute_contract"
    if unavailable_reasons:
        return "blocked_by_manifested_routed_next_gate_downstream_command_unavailable"
    if "downstream_execute_mode_invalid" in request_reasons:
        return "blocked_by_downstream_execute_mode"
    if mode == "dry-run":
        if downstream_gate_entry.get("downstream_kind") == "product_review_preparation":
            return (
                "manifested_routed_next_gate_downstream_product_review_preparation_dry_run_ready"
            )
        return "manifested_routed_next_gate_downstream_execute_dry_run_ready"
    if "confirm_downstream_execute_required" in request_reasons:
        return "blocked_by_missing_downstream_execute_confirmation"
    if request_reasons:
        return "blocked_by_downstream_execute_metadata"
    return "ready_to_execute_manifested_routed_next_gate_downstream"


def build_selected_route_execute_command(
    project_root: Path,
    record: dict[str, Any],
    mode: str,
    reviewer: str,
    note: str,
) -> list[str]:
    command = [
        "python3",
        SELECTED_ROUTE_EXECUTE_COMMAND_PATH,
        "--project-root",
        str(project_root),
        "--selected-route-preflight",
        record.get("source_report_path", ""),
        "--mode",
        mode,
        "--output-execute",
        SELECTED_ROUTE_EXECUTE_REPORT_PATH,
        "--output-review",
        SELECTED_ROUTE_EXECUTE_REVIEW_PATH,
        "--execute-manifest",
        SELECTED_ROUTE_EXECUTE_MANIFEST_PATH,
    ]
    if mode == "execute":
        command.extend(["--confirm-execute", "--reviewer", reviewer, "--note", note])
    return command


def extract_downstream_record(downstream_gate_entry: dict[str, Any]) -> dict[str, Any]:
    records = downstream_gate_entry.get("downstream_input_records", []) or []
    if len(records) != 1:
        return {}
    return records[0]


def build_source_gate_entry_summary(downstream_gate_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": downstream_gate_entry.get("schema_version", ""),
        "status": downstream_gate_entry.get("status", ""),
        "verified_route_type": downstream_gate_entry.get("verified_route_type", ""),
        "routed_next_gate": downstream_gate_entry.get("routed_next_gate", ""),
        "downstream_kind": downstream_gate_entry.get("downstream_kind", ""),
        "downstream_gate_entry_recorded": (
            downstream_gate_entry.get("downstream_gate_entry_recorded") is True
        ),
        "can_request_manifested_routed_next_gate_result_continuation_downstream": (
            downstream_gate_entry.get(
                "can_request_manifested_routed_next_gate_result_continuation_downstream"
            )
            is True
        ),
        "downstream_input_records_count": len(
            downstream_gate_entry.get("downstream_input_records", []) or []
        ),
        "source_blocking_reasons": downstream_gate_entry.get("blocking_reasons", []),
    }


def build_downstream_execute_request(
    mode: str,
    confirm_downstream_execute: bool,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_downstream_execute": confirm_downstream_execute,
        "reviewer": reviewer,
        "note": note,
    }


def build_selected_route_execute_report_summary(selected_route_execute_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execute_report.get("schema_version", ""),
        "status": selected_route_execute_report.get("status", ""),
        "selected_route_execute_manifest_recorded": (
            selected_route_execute_report.get("selected_route_execute_manifest_recorded")
            is True
        ),
        "selected_route_execute_operations_count": len(
            selected_route_execute_report.get("selected_route_execute_operations", []) or []
        ),
        "blocking_reasons": selected_route_execute_report.get("blocking_reasons", []),
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
        "entered_continuation_execute_result_downstream_gate_execute_gate": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], downstream_kind: str) -> dict[str, Any]:
    if status == "manifested_routed_next_gate_downstream_execute_dry_run_ready":
        return {
            "id": "rerun_with_confirm_downstream_execute",
            "label": "Confirm downstream execute",
            "description": "Downstream selected-route execute is ready for explicit confirmation.",
        }
    if status == "manifested_routed_next_gate_downstream_product_review_preparation_dry_run_ready":
        return {
            "id": "rerun_with_confirm_product_review_preparation",
            "label": "Confirm product review preparation",
            "description": "Terminal downstream input is ready for product-review preparation.",
        }
    if status == "ready_to_execute_manifested_routed_next_gate_downstream":
        return {
            "id": "execute_manifested_routed_next_gate_downstream",
            "label": "Execute downstream",
            "description": f"Execute or record downstream action for {downstream_kind}.",
        }
    if status == "manifested_routed_next_gate_downstream_selected_route_execute_command_executed":
        return {
            "id": "review_downstream_selected_route_execute_result",
            "label": "Review downstream selected route execute",
            "description": "Selected-route execute result is ready for downstream review.",
        }
    if status == "manifested_routed_next_gate_downstream_product_review_preparation_recorded":
        return {
            "id": "prepare_product_review_packet",
            "label": "Prepare product review packet",
            "description": "Product-review preparation record is ready for downstream review.",
        }
    if status == "blocked_by_missing_downstream_execute_confirmation":
        return {
            "id": "rerun_with_confirm_downstream_execute",
            "label": "Confirm downstream execute",
            "description": "Execution mode requires explicit confirmation.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_downstream_execute_metadata":
        return {
            "id": "record_downstream_execute_metadata",
            "label": "Record reviewer and note",
            "description": "Execution mode requires reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_downstream_execute_failure":
        return {
            "id": "repair_downstream_execute_result",
            "label": "Repair downstream execute result",
            "description": "Downstream selected-route execute did not complete cleanly.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_downstream_execute_contract":
        return {
            "id": "repair_p7_bi_downstream_input_record",
            "label": "Repair P7-BI downstream input",
            "description": "P7-BI must expose exactly one clean downstream input record.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_p7_bi_downstream_gate_entry_blockers",
        "label": "Resolve P7-BI blockers",
        "description": "P7-BI must be ready before P7-BJ can execute or record downstream action.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTE_PATH,
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Downstream Gate Entry Execute Gate",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- mode：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- downstream kind：`{report['downstream_kind']}`",
        "- 可确认执行 downstream："
        f"{str(report['can_execute_downstream_with_confirmation']).lower()}",
        "- 需要显式 downstream command："
        f"{str(report['requires_explicit_downstream_command']).lower()}",
        f"- downstream execute command 数：{len(report['downstream_execute_command'])}",
        "- downstream command 已执行："
        f"{str(report['downstream_execute_command_executed']).lower()}",
        "- 本命令运行 downstream command："
        f"{str(report['this_command_ran_downstream_command']).lower()}",
        f"- downstream execute returncode：{report['downstream_execute_returncode']}",
        f"- downstream execute status：`{report['downstream_execute_status']}`",
        "- selected route execute manifest 已记录："
        f"{str(report['selected_route_execute_manifest_recorded']).lower()}",
        "- product review preparation 已记录："
        f"{str(report['product_review_preparation_recorded']).lower()}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["downstream_execute_command"]:
        lines.extend(["", "## Downstream Execute Command"])
        lines.append(f"- `{' '.join(report['downstream_execute_command'])}`")
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def is_safe_relative_path(value: str) -> bool:
    if not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


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

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_selected_route_execute.v1"
RESULT_REVIEW_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_workflow_continuation_result_review.v1"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json"
)
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_next_gate_selected_route_execute.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_next_gate_selected_route_execute.md")
DEFAULT_SELECTED_ROUTE_EXECUTE_REPORT_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execute.json")
DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_selected_route_execute.md")
DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH = Path(
    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
)
SELECTED_ROUTE_EXECUTE_COMMAND_PATH = "Program/auto_mode_formal_package_selected_route_execute.py"
SELECTED_ROUTE_PREFLIGHT_REPORT_PATH = (
    "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
)
SELECTED_ROUTE_PREFLIGHT_REVIEW_PATH = "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md"
VALID_MODES = {"dry-run", "execute"}

SELECTED_ROUTE_EXECUTE_CONTRACTS = {
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


def run_auto_mode_formal_package_next_gate_selected_route_execute(
    project_root: Path,
    next_gate_workflow_continuation_result_review: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_selected_route_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_selected_route_execute(
        project_root,
        next_gate_workflow_continuation_result_review,
        mode=mode,
        confirm_selected_route_execute=confirm_selected_route_execute,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_execute_next_gate_selected_route":
        return (
            report,
            0 if report["status"] == "next_gate_selected_route_execute_dry_run_ready" else 2,
        )

    result = subprocess.run(
        report["selected_route_execute_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    selected_route_execute_report = load_json_or_empty(
        project_root / report["selected_route_execute_report_path"]
    )
    selected_route_execute_status = selected_route_execute_report.get("status", "")
    report["selected_route_execute_command_executed"] = True
    report["this_command_ran_selected_route_execute_command"] = True
    report["selected_route_execute_returncode"] = result.returncode
    report["selected_route_execute_status"] = selected_route_execute_status
    report["selected_route_execute_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": selected_route_execute_status,
        "report_path": report["selected_route_execute_report_path"],
        "review_path": report["selected_route_execute_review_path"],
        "manifest_path": report["selected_route_execute_manifest_path"],
        "selected_route_execute_report_summary": build_selected_route_execute_report_summary(
            selected_route_execute_report
        ),
    }
    if result.returncode == 0 and selected_route_execute_status == "selected_route_execute_manifest_recorded":
        report["status"] = "next_gate_selected_route_execute_command_executed"
        report["blocking_reasons"] = []
        report["selected_route_execute_manifest_recorded"] = (
            selected_route_execute_report.get("selected_route_execute_manifest_recorded") is True
        )
        report["selected_route_executed"] = selected_route_execute_report.get("selected_route_executed") is True
        report["export_or_acceptance_executed"] = (
            selected_route_execute_report.get("export_or_acceptance_executed") is True
        )
        report["rendered_pdf"] = selected_route_execute_report.get("rendered_pdf") is True
        report["rendered_docx"] = selected_route_execute_report.get("rendered_docx") is True
        report["package_manifest_generated"] = (
            selected_route_execute_report.get("package_manifest_generated") is True
        )
        report["manual_acceptance_performed"] = (
            selected_route_execute_report.get("manual_acceptance_performed") is True
        )
        report["next_action"] = build_next_action(report["status"], [], report["verified_route_type"])
        return report, 0

    report["status"] = "blocked_by_next_gate_selected_route_execute_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"selected_route_execute_command_failed:{report['verified_route_type']}",
            f"selected_route_execute_status:{selected_route_execute_status or 'missing'}",
        ]
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_selected_route_execute(
    project_root: Path,
    next_gate_workflow_continuation_result_review: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_selected_route_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    result_review_reasons = build_result_review_blocking_reasons(
        next_gate_workflow_continuation_result_review
    )
    contract_reasons = (
        build_selected_route_execute_contract_blocking_reasons(
            next_gate_workflow_continuation_result_review
        )
        if not result_review_reasons
        else []
    )
    unavailable_reasons = (
        build_command_unavailable_reasons(repo_root)
        if not result_review_reasons and not contract_reasons
        else []
    )
    request_reasons = build_request_blocking_reasons(
        mode,
        confirm_selected_route_execute,
        reviewer,
        note,
    )
    status = build_status(mode, result_review_reasons, contract_reasons, unavailable_reasons, request_reasons)
    record = extract_selected_route_preflight_record(next_gate_workflow_continuation_result_review)
    can_execute = not result_review_reasons and not contract_reasons and not unavailable_reasons
    route_type = record.get("verified_route_type", "") if can_execute else ""
    routed_next_gate = record.get("routed_next_gate", "") if can_execute else ""
    selected_route_execute_command = (
        build_selected_route_execute_command(project_root, record, mode, reviewer, note)
        if status
        in {
            "next_gate_selected_route_execute_dry_run_ready",
            "ready_to_execute_next_gate_selected_route",
        }
        else []
    )
    blocking_reasons = dedupe(
        result_review_reasons + contract_reasons + unavailable_reasons + request_reasons
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": next_gate_workflow_continuation_result_review.get("topic", ""),
        "source_paths": {
            "next_gate_workflow_continuation_result_review": source_paths.get(
                "next_gate_workflow_continuation_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": next_gate_workflow_continuation_result_review.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_selected_route_execute": confirm_selected_route_execute,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "can_execute_selected_route_with_confirmation": can_execute,
        "requires_explicit_selected_route_execute_command": can_execute,
        "selected_route_execute_command": selected_route_execute_command,
        "selected_route_execute_command_executed": False,
        "this_command_ran_selected_route_execute_command": False,
        "selected_route_execute_report_path": str(DEFAULT_SELECTED_ROUTE_EXECUTE_REPORT_PATH) if can_execute else "",
        "selected_route_execute_review_path": str(DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH) if can_execute else "",
        "selected_route_execute_manifest_path": str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH)
        if can_execute
        else "",
        "selected_route_execute_returncode": None,
        "selected_route_execute_status": "",
        "selected_route_execute_result": {},
        "selected_route_execute_manifest_recorded": False,
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
        "source_result_review": build_source_result_review_summary(
            next_gate_workflow_continuation_result_review
        ),
        "selected_route_preflight_record": record if can_execute else {},
        "selected_route_execute_request": build_selected_route_execute_request(
            mode,
            confirm_selected_route_execute,
            reviewer,
            note,
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_result_review_blocking_reasons(
    next_gate_workflow_continuation_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    if next_gate_workflow_continuation_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("workflow_continuation_result_review_missing_or_invalid_schema")
    if (
        next_gate_workflow_continuation_result_review.get("status")
        != "next_gate_workflow_continuation_result_review_ready"
    ):
        reasons.append("workflow_continuation_result_review_not_ready")
    if next_gate_workflow_continuation_result_review.get("workflow_continuation_result_reviewed") is not True:
        reasons.append("workflow_continuation_result_not_reviewed")
    if next_gate_workflow_continuation_result_review.get("can_continue_to_selected_route_execution") is not True:
        reasons.append("workflow_continuation_result_cannot_continue_to_selected_route_execution")
    if next_gate_workflow_continuation_result_review.get("workflow_continuation_executed") is not True:
        reasons.append("workflow_continuation_not_executed")
    if next_gate_workflow_continuation_result_review.get("selected_route_executed") is True:
        reasons.append("workflow_continuation_result_review_selected_route_executed")
    if next_gate_workflow_continuation_result_review.get("export_or_acceptance_executed") is True:
        reasons.append("workflow_continuation_result_review_exported_or_accepted")
    if next_gate_workflow_continuation_result_review.get("rendered_pdf") is True:
        reasons.append("workflow_continuation_result_review_rendered_pdf")
    if next_gate_workflow_continuation_result_review.get("rendered_docx") is True:
        reasons.append("workflow_continuation_result_review_rendered_docx")
    if next_gate_workflow_continuation_result_review.get("package_manifest_generated") is True:
        reasons.append("workflow_continuation_result_review_generated_package_manifest")
    if next_gate_workflow_continuation_result_review.get("manual_acceptance_performed") is True:
        reasons.append("workflow_continuation_result_review_performed_manual_acceptance")
    if next_gate_workflow_continuation_result_review.get("formal_writeback_executed") is True:
        reasons.append("workflow_continuation_result_review_formal_writeback")
    if next_gate_workflow_continuation_result_review.get("this_command_wrote_formal_state") is True:
        reasons.append("workflow_continuation_result_review_wrote_formal_state")
    if next_gate_workflow_continuation_result_review.get("can_write_product_state") is True:
        reasons.append("workflow_continuation_result_review_allows_product_state_write")
    if next_gate_workflow_continuation_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    for flag, value in next_gate_workflow_continuation_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"workflow_continuation_result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_selected_route_execute_contract_blocking_reasons(
    next_gate_workflow_continuation_result_review: dict[str, Any],
) -> list[str]:
    records = next_gate_workflow_continuation_result_review.get(
        "selected_route_execution_preflight_records",
        [],
    )
    if not records:
        return ["selected_route_preflight_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["selected_route_preflight_record_not_single"]

    record = records[0]
    route_type = record.get("verified_route_type", "unknown")
    contract = SELECTED_ROUTE_EXECUTE_CONTRACTS.get(route_type)
    reasons = []
    if contract is None:
        reasons.append(f"selected_route_type_unknown:{route_type}")
    else:
        if record.get("routed_action") != contract["routed_action"]:
            reasons.append(f"selected_route_routed_action_mismatch:{route_type}")
        if record.get("next_command") != contract["next_command"]:
            reasons.append(f"selected_route_next_command_mismatch:{route_type}")
        if record.get("planned_outputs") != contract["planned_outputs"]:
            reasons.append(f"selected_route_planned_outputs_mismatch:{route_type}")

    if route_type != next_gate_workflow_continuation_result_review.get("verified_route_type", ""):
        reasons.append(f"selected_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != next_gate_workflow_continuation_result_review.get("routed_next_gate", ""):
        reasons.append(f"selected_route_gate_mismatch:{route_type}")
    if record.get("record_id") != f"workflow_continuation_result::{record.get('routed_next_gate', '')}::{route_type}":
        reasons.append(f"selected_route_preflight_record_id_mismatch:{route_type}")
    if record.get("selected_route_preflight_report_path") != SELECTED_ROUTE_PREFLIGHT_REPORT_PATH:
        reasons.append(f"selected_route_preflight_report_path_mismatch:{route_type}")
    if record.get("selected_route_preflight_review_path") != SELECTED_ROUTE_PREFLIGHT_REVIEW_PATH:
        reasons.append(f"selected_route_preflight_review_path_mismatch:{route_type}")
    if (
        record.get("selected_route_preflight_status")
        != "ready_for_selected_formal_package_route_execution_review"
    ):
        reasons.append(f"selected_route_preflight_status_mismatch:{route_type}")
    if (
        record.get("selected_route_preflight_schema_version")
        != "p7.auto_mode_formal_package_selected_route_execution_preflight.v1"
    ):
        reasons.append(f"selected_route_preflight_schema_mismatch:{route_type}")
    if record.get("review_status") != "selected_route_preflight_accepted_for_explicit_route_execution":
        reasons.append(f"selected_route_preflight_review_status_mismatch:{route_type}")
    if record.get("can_continue_to_selected_route_execution") is not True:
        reasons.append(f"selected_route_preflight_record_cannot_continue:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(repo_root: Path) -> list[str]:
    if not (repo_root / SELECTED_ROUTE_EXECUTE_COMMAND_PATH).exists():
        return [f"selected_route_execute_command_file_missing:{SELECTED_ROUTE_EXECUTE_COMMAND_PATH}"]
    return []


def build_request_blocking_reasons(
    mode: str,
    confirm_selected_route_execute: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["next_gate_selected_route_execute_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_selected_route_execute:
        reasons.append("confirm_selected_route_execute_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("selected_route_execute_note_required")
    return reasons


def build_status(
    mode: str,
    result_review_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if result_review_reasons:
        return "blocked_by_workflow_continuation_result_review"
    if contract_reasons:
        return "blocked_by_next_gate_selected_route_execute_contract"
    if unavailable_reasons:
        return "blocked_by_next_gate_selected_route_command_unavailable"
    if "next_gate_selected_route_execute_mode_invalid" in request_reasons:
        return "blocked_by_next_gate_selected_route_execute_mode"
    if mode == "dry-run":
        return "next_gate_selected_route_execute_dry_run_ready"
    if "confirm_selected_route_execute_required" in request_reasons:
        return "blocked_by_missing_next_gate_selected_route_execute_confirmation"
    if request_reasons:
        return "blocked_by_next_gate_selected_route_execute_metadata"
    return "ready_to_execute_next_gate_selected_route"


def extract_selected_route_preflight_record(
    next_gate_workflow_continuation_result_review: dict[str, Any],
) -> dict[str, Any]:
    records = next_gate_workflow_continuation_result_review.get(
        "selected_route_execution_preflight_records",
        [],
    )
    if isinstance(records, list) and len(records) == 1:
        return records[0]
    return {}


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
        record.get("selected_route_preflight_report_path", ""),
        "--mode",
        mode,
        "--output-execute",
        str(DEFAULT_SELECTED_ROUTE_EXECUTE_REPORT_PATH),
        "--output-review",
        str(DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH),
        "--execute-manifest",
        str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH),
    ]
    if mode == "execute":
        command.extend(["--confirm-execute", "--reviewer", reviewer, "--note", note])
    return command


def build_source_result_review_summary(
    next_gate_workflow_continuation_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": next_gate_workflow_continuation_result_review.get("schema_version", ""),
        "status": next_gate_workflow_continuation_result_review.get("status", ""),
        "verified_route_type": next_gate_workflow_continuation_result_review.get("verified_route_type", ""),
        "routed_next_gate": next_gate_workflow_continuation_result_review.get("routed_next_gate", ""),
        "workflow_continuation_result_reviewed": (
            next_gate_workflow_continuation_result_review.get("workflow_continuation_result_reviewed")
            is True
        ),
        "can_continue_to_selected_route_execution": (
            next_gate_workflow_continuation_result_review.get("can_continue_to_selected_route_execution")
            is True
        ),
        "workflow_continuation_executed": (
            next_gate_workflow_continuation_result_review.get("workflow_continuation_executed") is True
        ),
        "selected_route_execution_preflight_records_count": len(
            next_gate_workflow_continuation_result_review.get(
                "selected_route_execution_preflight_records",
                [],
            )
        ),
        "source_blocking_reasons": next_gate_workflow_continuation_result_review.get("blocking_reasons", []),
        "boundary_flags": next_gate_workflow_continuation_result_review.get("boundary_flags", {}),
    }


def build_selected_route_execute_request(
    mode: str,
    confirm_selected_route_execute: bool,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_selected_route_execute": confirm_selected_route_execute,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_selected_route_execute_report_summary(
    selected_route_execute_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execute_report.get("schema_version", ""),
        "status": selected_route_execute_report.get("status", ""),
        "selected_route_execute_manifest_recorded": (
            selected_route_execute_report.get("selected_route_execute_manifest_recorded") is True
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
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "next_gate_selected_route_execute_dry_run_ready":
        return {
            "id": "rerun_with_confirm_selected_route_execute",
            "label": "Confirm selected route execute",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note to run the selected route execute gate.",
        }
    if status == "ready_to_execute_next_gate_selected_route":
        return {
            "id": "execute_next_gate_selected_route",
            "label": "Execute next-gate selected route",
            "description": "The selected route execute command is ready to run.",
        }
    if status == "next_gate_selected_route_execute_command_executed":
        return {
            "id": "review_selected_route_execute_manifest",
            "label": "Review selected route execute manifest",
            "description": f"The `{route_type}` selected route execute command ran and recorded its manifest.",
        }
    if status == "blocked_by_missing_next_gate_selected_route_execute_confirmation":
        return {
            "id": "rerun_with_confirm_selected_route_execute",
            "label": "Rerun with explicit selected route execute confirmation",
            "description": "Execute mode requires --confirm-selected-route-execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_selected_route_execute_metadata":
        return {
            "id": "record_selected_route_execute_reviewer_and_note",
            "label": "Record selected route execute reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_selected_route_command_unavailable":
        return {
            "id": "implement_or_restore_selected_route_execute_command",
            "label": "Implement selected route execute command",
            "description": "The planned selected route execute command file is missing.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_selected_route_execute_failure":
        return {
            "id": "repair_selected_route_execute_command_inputs",
            "label": "Repair selected route execute command inputs",
            "description": "The selected route execute command ran but did not record a manifest.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_selected_route_execute_contract":
        return {
            "id": "repair_selected_route_execute_contract",
            "label": "Repair selected route execute contract",
            "description": "P7-AM must expose exactly one clean selected route preflight record.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_workflow_continuation_result_review_blockers",
        "label": "Resolve P7-AM blockers",
        "description": "P7-AM must be ready before P7-AN can run selected route execute.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_selected_route_execute_outputs(
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
        "# Auto Mode Formal Package Next Gate Selected Route Execute",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        "- 可确认执行 selected route："
        f"{str(report['can_execute_selected_route_with_confirmation']).lower()}",
        f"- selected route execute command 数：{len(report['selected_route_execute_command'])}",
        "- 已运行 selected route execute command："
        f"{str(report['selected_route_execute_command_executed']).lower()}",
        "- 本命令运行 selected route execute command："
        f"{str(report['this_command_ran_selected_route_execute_command']).lower()}",
        f"- selected route execute returncode：{report['selected_route_execute_returncode']}",
        f"- selected route execute status：`{report['selected_route_execute_status']}`",
        "- selected route execute manifest 已记录："
        f"{str(report['selected_route_execute_manifest_recorded']).lower()}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 已渲染 PDF：{str(report['rendered_pdf']).lower()}",
        f"- 已渲染 DOCX：{str(report['rendered_docx']).lower()}",
        f"- 已生成 package manifest：{str(report['package_manifest_generated']).lower()}",
        f"- 已执行人工验收：{str(report['manual_acceptance_performed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["selected_route_execute_command"]:
        lines.extend(["", "## Selected Route Execute Command"])
        lines.append(f"- `{' '.join(report['selected_route_execute_command'])}`")
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

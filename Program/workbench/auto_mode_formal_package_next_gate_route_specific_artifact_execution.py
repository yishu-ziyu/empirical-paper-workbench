from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution.v1"
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.v1"
)
RESULT_REVIEW_READY_STATUS = "route_specific_artifact_executor_entry_result_review_ready"
ARTIFACT_EXECUTOR_SUCCESS_STATUS = "route_specific_artifact_executed"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.json"
)
DEFAULT_EXECUTION_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_execution.md")
DEFAULT_SELECTED_ROUTE_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execute.json")
DEFAULT_EXECUTE_MANIFEST_PATH = Path(
    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
)
DEFAULT_ARTIFACT_EXECUTOR_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_executor.json")
DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_executor.md")
ARTIFACT_EXECUTOR_COMMAND_PATH = "Program/auto_mode_formal_package_route_specific_artifact_executor.py"
VALID_MODES = {"dry-run", "execute"}
VALID_MANUAL_DECISIONS = {"accept", "defer", "needs_revision", "reject"}
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}
ROUTE_DELEGATED_PATHS = {
    "pdf_export": {
        "report": "Results/json/formal_pdf_final_writeback.json",
        "review": "Reviews/formal_pdf_final_writeback.md",
    },
    "docx_export": {
        "report": "Results/json/formal_docx_export.json",
        "review": "Reviews/formal_docx_export.md",
    },
    "package_manifest": {
        "report": "Results/json/formal_submission_package_manifest.json",
        "review": "Reviews/formal_submission_package_acceptance.md",
    },
    "manual_acceptance": {
        "report": "Results/json/formal_submission_package_manual_acceptance.json",
        "review": "Reviews/formal_submission_package_manual_acceptance.md",
    },
}
EXECUTION_BOUNDARY_FIELDS = [
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
]


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
    project_root: Path,
    route_specific_artifact_executor_entry_result_review: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_artifact_execution: bool = False,
    reviewer: str = "",
    note: str = "",
    manual_decision: str = "defer",
    manual_actor: str = "",
    manual_note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
        project_root,
        route_specific_artifact_executor_entry_result_review,
        mode=mode,
        confirm_artifact_execution=confirm_artifact_execution,
        reviewer=reviewer,
        note=note,
        manual_decision=manual_decision,
        manual_actor=manual_actor,
        manual_note=manual_note,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_execute_route_specific_artifact":
        return report, 0 if report["status"] == "route_specific_artifact_execution_dry_run_ready" else 2

    result = subprocess.run(
        report["route_specific_artifact_execution_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    artifact_executor_report = load_json_or_empty(
        project_root / report["route_specific_artifact_executor_report_path"]
    )
    artifact_executor_status = artifact_executor_report.get("status", "")
    report["route_specific_artifact_execution_command_executed"] = True
    report["this_command_ran_route_specific_artifact_executor"] = True
    report["route_specific_artifact_executor_returncode"] = result.returncode
    report["route_specific_artifact_executor_status"] = artifact_executor_status
    report["route_specific_artifact_executor_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": artifact_executor_status,
        "report_path": report["route_specific_artifact_executor_report_path"],
        "review_path": report["route_specific_artifact_executor_review_path"],
        "route_specific_artifact_executor_report_summary": build_artifact_executor_report_summary(
            artifact_executor_report
        ),
    }
    if result.returncode == 0 and artifact_executor_status == ARTIFACT_EXECUTOR_SUCCESS_STATUS:
        mark_successful_artifact_execution(report, artifact_executor_report)
        return report, 0

    report["status"] = "blocked_by_route_specific_artifact_execution_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"route_specific_artifact_execution_command_failed:{report['verified_route_type']}",
            f"route_specific_artifact_executor_status:{artifact_executor_status or 'missing'}",
        ]
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
    project_root: Path,
    route_specific_artifact_executor_entry_result_review: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_artifact_execution: bool = False,
    reviewer: str = "",
    note: str = "",
    manual_decision: str = "defer",
    manual_actor: str = "",
    manual_note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    result_review_reasons = build_result_review_blocking_reasons(
        route_specific_artifact_executor_entry_result_review
    )
    contract_reasons = (
        build_artifact_execution_record_contract_blocking_reasons(
            route_specific_artifact_executor_entry_result_review
        )
        if not result_review_reasons
        else []
    )
    unavailable_reasons = (
        build_command_unavailable_reasons(repo_root)
        if not result_review_reasons and not contract_reasons
        else []
    )
    request_reasons = build_request_blocking_reasons(mode, confirm_artifact_execution, reviewer, note, manual_decision)
    status = build_status(mode, result_review_reasons, contract_reasons, unavailable_reasons, request_reasons)
    record = extract_artifact_execution_record(route_specific_artifact_executor_entry_result_review)
    can_execute = not result_review_reasons and not contract_reasons and not unavailable_reasons
    route_type = route_specific_artifact_executor_entry_result_review.get("verified_route_type", "") if can_execute else ""
    command = (
        build_artifact_execution_command(
            project_root,
            mode,
            reviewer=reviewer,
            note=note,
            manual_decision=manual_decision,
            manual_actor=manual_actor,
            manual_note=manual_note,
        )
        if status in {"route_specific_artifact_execution_dry_run_ready", "ready_to_execute_route_specific_artifact"}
        else []
    )
    blocking_reasons = dedupe(result_review_reasons + contract_reasons + unavailable_reasons + request_reasons)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": route_specific_artifact_executor_entry_result_review.get("topic", ""),
        "source_paths": {
            "route_specific_artifact_executor_entry_result_review": source_paths.get(
                "route_specific_artifact_executor_entry_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": route_specific_artifact_executor_entry_result_review.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_artifact_execution": confirm_artifact_execution,
        "verified_route_type": route_type,
        "can_execute_route_specific_artifact_with_confirmation": can_execute,
        "requires_explicit_route_specific_artifact_execution_command": can_execute,
        "route_specific_artifact_execution_command": command,
        "route_specific_artifact_execution_command_executed": False,
        "this_command_ran_route_specific_artifact_executor": False,
        "route_specific_artifact_executor_report_path": str(DEFAULT_ARTIFACT_EXECUTOR_PATH) if can_execute else "",
        "route_specific_artifact_executor_review_path": str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH)
        if can_execute
        else "",
        "route_specific_artifact_executor_returncode": None,
        "route_specific_artifact_executor_status": "",
        "route_specific_artifact_executor_result": {},
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
        "source_result_review": build_source_result_review_summary(
            route_specific_artifact_executor_entry_result_review
        ),
        "route_specific_artifact_execution_record": record if can_execute else {},
        "artifact_execution_request": build_artifact_execution_request(
            mode,
            confirm_artifact_execution,
            reviewer,
            note,
            manual_decision,
            manual_actor,
            manual_note,
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_result_review_blocking_reasons(
    route_specific_artifact_executor_entry_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    if route_specific_artifact_executor_entry_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("route_specific_artifact_executor_entry_result_review_missing_or_invalid_schema")
    if route_specific_artifact_executor_entry_result_review.get("status") != RESULT_REVIEW_READY_STATUS:
        reasons.append("route_specific_artifact_executor_entry_result_review_not_ready")
    if route_specific_artifact_executor_entry_result_review.get("artifact_executor_entry_result_reviewed") is not True:
        reasons.append("artifact_executor_entry_result_not_reviewed")
    if (
        route_specific_artifact_executor_entry_result_review.get(
            "can_continue_to_route_specific_artifact_execution"
        )
        is not True
    ):
        reasons.append("result_review_cannot_continue_to_route_specific_artifact_execution")
    for field in EXECUTION_BOUNDARY_FIELDS:
        if route_specific_artifact_executor_entry_result_review.get(field) is True:
            reasons.append(f"result_review_{field}")
    if route_specific_artifact_executor_entry_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    for flag, value in route_specific_artifact_executor_entry_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_artifact_execution_record_contract_blocking_reasons(
    route_specific_artifact_executor_entry_result_review: dict[str, Any],
) -> list[str]:
    records = route_specific_artifact_executor_entry_result_review.get(
        "route_specific_artifact_execution_records",
        [],
    )
    if not records:
        return ["route_specific_artifact_execution_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["route_specific_artifact_execution_record_not_single"]

    record = records[0]
    route_type = route_specific_artifact_executor_entry_result_review.get("verified_route_type", "unknown")
    delegated_paths = ROUTE_DELEGATED_PATHS.get(route_type, {"report": "", "review": ""})
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"route_specific_artifact_execution_route_type_unknown:{route_type}")
    if record.get("route_type") != route_type:
        reasons.append(f"route_specific_artifact_execution_record_route_type_mismatch:{route_type}")
    if record.get("record_id") != f"artifact_executor_dry_run::{route_type}":
        reasons.append(f"route_specific_artifact_execution_record_id_mismatch:{route_type}")
    if record.get("artifact_executor_report_path") != str(DEFAULT_ARTIFACT_EXECUTOR_PATH):
        reasons.append(f"artifact_executor_report_path_mismatch:{route_type}")
    if record.get("artifact_executor_review_path") != str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH):
        reasons.append(f"artifact_executor_review_path_mismatch:{route_type}")
    if record.get("delegated_report_path") != delegated_paths["report"]:
        reasons.append(f"delegated_report_path_mismatch:{route_type}")
    if record.get("delegated_review_path") != delegated_paths["review"]:
        reasons.append(f"delegated_review_path_mismatch:{route_type}")
    if not record.get("route_specific_command"):
        reasons.append(f"route_specific_command_missing:{route_type}")
    if record.get("review_status") != "artifact_executor_dry_run_accepted_for_explicit_artifact_execution":
        reasons.append(f"route_specific_artifact_execution_record_review_status_mismatch:{route_type}")
    if record.get("can_continue_to_route_specific_artifact_execution") is not True:
        reasons.append(f"route_specific_artifact_execution_record_cannot_continue:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(repo_root: Path) -> list[str]:
    if not (repo_root / ARTIFACT_EXECUTOR_COMMAND_PATH).exists():
        return [f"route_specific_artifact_executor_command_file_missing:{ARTIFACT_EXECUTOR_COMMAND_PATH}"]
    return []


def build_request_blocking_reasons(
    mode: str,
    confirm_artifact_execution: bool,
    reviewer: str,
    note: str,
    manual_decision: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["route_specific_artifact_execution_mode_invalid"]
    if manual_decision not in VALID_MANUAL_DECISIONS:
        return [f"manual_decision_invalid:{manual_decision}"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_artifact_execution:
        reasons.append("confirm_artifact_execution_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("artifact_execution_note_required")
    return reasons


def build_status(
    mode: str,
    result_review_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if result_review_reasons:
        return "blocked_by_route_specific_artifact_execution_result_review"
    if contract_reasons:
        return "blocked_by_route_specific_artifact_execution_contract"
    if unavailable_reasons:
        return "blocked_by_route_specific_artifact_executor_command_unavailable"
    if "route_specific_artifact_execution_mode_invalid" in request_reasons:
        return "blocked_by_route_specific_artifact_execution_mode"
    if any(reason.startswith("manual_decision_invalid") for reason in request_reasons):
        return "blocked_by_route_specific_artifact_execution_metadata"
    if mode == "dry-run":
        return "route_specific_artifact_execution_dry_run_ready"
    if "confirm_artifact_execution_required" in request_reasons:
        return "blocked_by_missing_route_specific_artifact_execution_confirmation"
    if request_reasons:
        return "blocked_by_route_specific_artifact_execution_metadata"
    return "ready_to_execute_route_specific_artifact"


def extract_artifact_execution_record(
    route_specific_artifact_executor_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    records = route_specific_artifact_executor_entry_result_review.get(
        "route_specific_artifact_execution_records",
        [],
    )
    if isinstance(records, list) and len(records) == 1:
        return records[0]
    return {}


def build_artifact_execution_command(
    project_root: Path,
    mode: str,
    *,
    reviewer: str,
    note: str,
    manual_decision: str,
    manual_actor: str,
    manual_note: str,
) -> list[str]:
    command = [
        "python3",
        ARTIFACT_EXECUTOR_COMMAND_PATH,
        "--project-root",
        str(project_root),
        "--selected-route-execute",
        str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH),
        "--execute-manifest",
        str(DEFAULT_EXECUTE_MANIFEST_PATH),
        "--mode",
        "execute",
        "--confirm-artifact-execution",
        "--reviewer",
        reviewer,
        "--note",
        note,
        "--manual-decision",
        manual_decision,
        "--output-executor",
        str(DEFAULT_ARTIFACT_EXECUTOR_PATH),
        "--output-review",
        str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH),
    ]
    if manual_actor.strip():
        command.extend(["--manual-actor", manual_actor])
    if manual_note.strip():
        command.extend(["--manual-note", manual_note])
    return command


def build_source_result_review_summary(
    route_specific_artifact_executor_entry_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_executor_entry_result_review.get("schema_version", ""),
        "status": route_specific_artifact_executor_entry_result_review.get("status", ""),
        "verified_route_type": route_specific_artifact_executor_entry_result_review.get("verified_route_type", ""),
        "artifact_executor_entry_result_reviewed": (
            route_specific_artifact_executor_entry_result_review.get("artifact_executor_entry_result_reviewed")
            is True
        ),
        "can_continue_to_route_specific_artifact_execution": (
            route_specific_artifact_executor_entry_result_review.get(
                "can_continue_to_route_specific_artifact_execution"
            )
            is True
        ),
        "route_specific_artifact_execution_records_count": len(
            route_specific_artifact_executor_entry_result_review.get(
                "route_specific_artifact_execution_records",
                [],
            )
        ),
        "blocking_reasons": route_specific_artifact_executor_entry_result_review.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_executor_entry_result_review.get("boundary_flags", {}),
    }


def build_artifact_execution_request(
    mode: str,
    confirm_artifact_execution: bool,
    reviewer: str,
    note: str,
    manual_decision: str,
    manual_actor: str,
    manual_note: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_artifact_execution": confirm_artifact_execution,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
        "manual_decision": manual_decision,
        "manual_actor": manual_actor,
        "manual_note": manual_note,
    }


def build_artifact_executor_report_summary(artifact_executor_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": artifact_executor_report.get("schema_version", ""),
        "status": artifact_executor_report.get("status", ""),
        "mode": artifact_executor_report.get("mode", ""),
        "route_type": artifact_executor_report.get("route_type", ""),
        "route_specific_artifact_executed": (
            artifact_executor_report.get("route_specific_artifact_executed") is True
        ),
        "route_specific_command_executed": artifact_executor_report.get("route_specific_command_executed") is True,
        "delegated_status": artifact_executor_report.get("delegated_status", ""),
        "blocking_reasons": artifact_executor_report.get("blocking_reasons", []),
    }


def mark_successful_artifact_execution(
    report: dict[str, Any],
    artifact_executor_report: dict[str, Any],
) -> None:
    report["status"] = "next_gate_route_specific_artifact_executed"
    report["blocking_reasons"] = []
    report["route_specific_artifact_executed"] = artifact_executor_report.get("route_specific_artifact_executed") is True
    report["route_specific_command_executed"] = artifact_executor_report.get("route_specific_command_executed") is True
    report["selected_route_executed"] = artifact_executor_report.get("selected_route_executed") is True
    report["export_or_acceptance_executed"] = artifact_executor_report.get("export_or_acceptance_executed") is True
    report["rendered_pdf"] = artifact_executor_report.get("rendered_pdf") is True
    report["rendered_docx"] = artifact_executor_report.get("rendered_docx") is True
    report["package_manifest_generated"] = artifact_executor_report.get("package_manifest_generated") is True
    report["manual_acceptance_performed"] = artifact_executor_report.get("manual_acceptance_performed") is True
    report["formal_writeback_executed"] = artifact_executor_report.get("formal_writeback_executed") is True
    report["this_command_wrote_formal_state"] = artifact_executor_report.get("this_command_wrote_formal_state") is True
    report["can_write_product_state"] = artifact_executor_report.get("can_write_product_state") is True
    report["next_action"] = build_next_action(report["status"], [], report["verified_route_type"])


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
    if status == "route_specific_artifact_execution_dry_run_ready":
        return {
            "id": "rerun_with_confirm_artifact_execution",
            "label": "Confirm route-specific artifact execution",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note to execute the route-specific artifact.",
        }
    if status == "ready_to_execute_route_specific_artifact":
        return {
            "id": "execute_route_specific_artifact",
            "label": "Execute route-specific artifact",
            "description": "The route-specific artifact executor command is ready to run.",
        }
    if status == "next_gate_route_specific_artifact_executed":
        return {
            "id": "review_route_specific_artifact_execution",
            "label": "Review route-specific artifact execution",
            "description": f"The `{route_type}` route-specific artifact has executed; review the output report.",
        }
    if status == "blocked_by_route_specific_artifact_execution_contract":
        return {
            "id": "repair_route_specific_artifact_execution_record",
            "label": "Repair route-specific artifact execution record",
            "description": "P7-AQ must expose exactly one clean artifact execution record.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_executor_command_unavailable":
        return {
            "id": "restore_route_specific_artifact_executor_command",
            "label": "Restore route-specific artifact executor command",
            "description": "The artifact executor command file is missing.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_missing_route_specific_artifact_execution_confirmation":
        return {
            "id": "rerun_with_confirm_artifact_execution",
            "label": "Rerun with explicit artifact execution confirmation",
            "description": "Execute mode requires --confirm-artifact-execution.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_execution_metadata":
        return {
            "id": "record_artifact_execution_reviewer_and_note",
            "label": "Record artifact execution reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_execution_failure":
        return {
            "id": "repair_route_specific_artifact_execution_inputs",
            "label": "Repair route-specific artifact execution inputs",
            "description": "The artifact executor command ran but did not complete route-specific artifact execution.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_route_specific_artifact_executor_entry_result_review_blockers",
        "label": "Resolve P7-AQ blockers",
        "description": "P7-AQ must approve the artifact executor dry-run before P7-AR can execute artifacts.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_route_specific_artifact_execution_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTION_PATH,
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
        "# Auto Mode Formal Package Next Gate Route-Specific Artifact Execution",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        "- 可确认执行 route-specific artifact："
        f"{str(report['can_execute_route_specific_artifact_with_confirmation']).lower()}",
        "- artifact execution command 数："
        f"{len(report['route_specific_artifact_execution_command'])}",
        "- 已运行 artifact execution command："
        f"{str(report['route_specific_artifact_execution_command_executed']).lower()}",
        "- 本命令运行 artifact executor："
        f"{str(report['this_command_ran_route_specific_artifact_executor']).lower()}",
        f"- artifact executor returncode：{report['route_specific_artifact_executor_returncode']}",
        f"- artifact executor status：`{report['route_specific_artifact_executor_status']}`",
        f"- 已执行 route-specific command：{str(report['route_specific_command_executed']).lower()}",
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
    if report["route_specific_artifact_execution_command"]:
        lines.extend(["", "## Route-Specific Artifact Execution Command", ""])
        lines.append("```bash")
        lines.append(" ".join(str(item) for item in report["route_specific_artifact_execution_command"]))
        lines.append("```")
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

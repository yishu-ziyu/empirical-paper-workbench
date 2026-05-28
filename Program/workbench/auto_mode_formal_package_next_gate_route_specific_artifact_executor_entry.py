from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.v1"
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_selected_route_execute_result_review.v1"
)
ARTIFACT_EXECUTOR_DRY_RUN_STATUS = "route_specific_artifact_executor_dry_run_ready"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_selected_route_execute_result_review.json"
)
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.md")
DEFAULT_ARTIFACT_EXECUTOR_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_executor.json")
DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_executor.md")
DEFAULT_SELECTED_ROUTE_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execute.json")
DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH = Path(
    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
)
ARTIFACT_EXECUTOR_COMMAND_PATH = "Program/auto_mode_formal_package_route_specific_artifact_executor.py"
VALID_MODES = {"dry-run", "execute"}

ROUTE_CONTRACTS = {
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
    "manual_acceptance": {
        "routed_action": "formal_submission_package_manual_acceptance_preflight",
        "next_command": "formal_submission_package_manual_acceptance_execute",
        "planned_outputs": ["Submissions/formal_package/manual_acceptance.json"],
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
    project_root: Path,
    next_gate_selected_route_execute_result_review: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_artifact_executor_entry: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
        project_root,
        next_gate_selected_route_execute_result_review,
        mode=mode,
        confirm_artifact_executor_entry=confirm_artifact_executor_entry,
        reviewer=reviewer,
        note=note,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_enter_route_specific_artifact_executor":
        return (
            report,
            0
            if report["status"] == "next_gate_route_specific_artifact_executor_entry_dry_run_ready"
            else 2,
        )

    result = subprocess.run(
        report["route_specific_artifact_executor_entry_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    executor_report = load_json_or_empty(project_root / report["route_specific_artifact_executor_report_path"])
    executor_status = executor_report.get("status", "")
    report["route_specific_artifact_executor_entry_command_executed"] = True
    report["this_command_ran_route_specific_artifact_executor"] = True
    report["route_specific_artifact_executor_returncode"] = result.returncode
    report["route_specific_artifact_executor_status"] = executor_status
    report["route_specific_artifact_executor_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": executor_status,
        "report_path": report["route_specific_artifact_executor_report_path"],
        "review_path": report["route_specific_artifact_executor_review_path"],
        "route_specific_artifact_executor_report_summary": build_artifact_executor_report_summary(
            executor_report
        ),
    }
    if result.returncode == 0 and executor_status == ARTIFACT_EXECUTOR_DRY_RUN_STATUS:
        report["status"] = "next_gate_route_specific_artifact_executor_entered"
        report["blocking_reasons"] = []
        report["route_specific_artifact_executor_entered"] = True
        report["route_specific_command_executed"] = executor_report.get("route_specific_command_executed") is True
        report["route_specific_artifact_executed"] = (
            executor_report.get("route_specific_artifact_executed") is True
        )
        report["selected_route_executed"] = executor_report.get("selected_route_executed") is True
        report["export_or_acceptance_executed"] = (
            executor_report.get("export_or_acceptance_executed") is True
        )
        report["rendered_pdf"] = executor_report.get("rendered_pdf") is True
        report["rendered_docx"] = executor_report.get("rendered_docx") is True
        report["package_manifest_generated"] = executor_report.get("package_manifest_generated") is True
        report["manual_acceptance_performed"] = (
            executor_report.get("manual_acceptance_performed") is True
        )
        report["formal_writeback_executed"] = executor_report.get("formal_writeback_executed") is True
        report["this_command_wrote_formal_state"] = executor_report.get("this_command_wrote_formal_state") is True
        report["can_write_product_state"] = executor_report.get("can_write_product_state") is True
        report["next_action"] = build_next_action(
            report["status"],
            [],
            report["verified_route_type"],
        )
        return report, 0

    report["status"] = "blocked_by_route_specific_artifact_executor_entry_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"route_specific_artifact_executor_entry_command_failed:{report['verified_route_type']}",
            f"route_specific_artifact_executor_status:{executor_status or 'missing'}",
        ]
    )
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
    project_root: Path,
    next_gate_selected_route_execute_result_review: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_artifact_executor_entry: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    result_review_reasons = build_result_review_blocking_reasons(
        next_gate_selected_route_execute_result_review
    )
    contract_reasons = (
        build_artifact_executor_input_contract_blocking_reasons(
            next_gate_selected_route_execute_result_review
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
        confirm_artifact_executor_entry,
        reviewer,
        note,
    )
    status = build_status(
        mode,
        result_review_reasons,
        contract_reasons,
        unavailable_reasons,
        request_reasons,
    )
    record = extract_artifact_executor_input_record(next_gate_selected_route_execute_result_review)
    can_enter = not result_review_reasons and not contract_reasons and not unavailable_reasons
    route_type = record.get("verified_route_type", "") if can_enter else ""
    command = (
        build_artifact_executor_entry_command(project_root, record)
        if status
        in {
            "next_gate_route_specific_artifact_executor_entry_dry_run_ready",
            "ready_to_enter_route_specific_artifact_executor",
        }
        else []
    )
    blocking_reasons = dedupe(
        result_review_reasons + contract_reasons + unavailable_reasons + request_reasons
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": next_gate_selected_route_execute_result_review.get("topic", ""),
        "source_paths": {
            "next_gate_selected_route_execute_result_review": source_paths.get(
                "next_gate_selected_route_execute_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": next_gate_selected_route_execute_result_review.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_artifact_executor_entry": confirm_artifact_executor_entry,
        "verified_route_type": route_type,
        "can_enter_route_specific_artifact_executor_with_confirmation": can_enter,
        "requires_explicit_artifact_executor_entry_command": can_enter,
        "route_specific_artifact_executor_entry_command": command,
        "route_specific_artifact_executor_entry_command_executed": False,
        "this_command_ran_route_specific_artifact_executor": False,
        "route_specific_artifact_executor_entered": False,
        "route_specific_artifact_executor_report_path": str(DEFAULT_ARTIFACT_EXECUTOR_PATH) if can_enter else "",
        "route_specific_artifact_executor_review_path": str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH) if can_enter else "",
        "route_specific_artifact_executor_returncode": None,
        "route_specific_artifact_executor_status": "",
        "route_specific_artifact_executor_result": {},
        "route_specific_command_executed": False,
        "route_specific_artifact_executed": False,
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
            next_gate_selected_route_execute_result_review
        ),
        "artifact_executor_input_record": record if can_enter else {},
        "artifact_executor_entry_request": build_artifact_executor_entry_request(
            mode,
            confirm_artifact_executor_entry,
            reviewer,
            note,
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_result_review_blocking_reasons(
    next_gate_selected_route_execute_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    if next_gate_selected_route_execute_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("next_gate_selected_route_execute_result_review_missing_or_invalid_schema")
    if (
        next_gate_selected_route_execute_result_review.get("status")
        != "next_gate_selected_route_execute_result_review_ready"
    ):
        reasons.append("next_gate_selected_route_execute_result_review_not_ready")
    if next_gate_selected_route_execute_result_review.get("selected_route_execute_result_reviewed") is not True:
        reasons.append("selected_route_execute_result_not_reviewed")
    if (
        next_gate_selected_route_execute_result_review.get(
            "can_continue_to_route_specific_artifact_executor"
        )
        is not True
    ):
        reasons.append("result_review_cannot_continue_to_route_specific_artifact_executor")
    if next_gate_selected_route_execute_result_review.get("selected_route_execute_manifest_recorded") is not True:
        reasons.append("selected_route_execute_manifest_not_recorded")
    for field in [
        "route_specific_artifact_executed",
        "route_specific_command_executed",
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
        if next_gate_selected_route_execute_result_review.get(field) is True:
            reasons.append(f"result_review_{field}")
    if next_gate_selected_route_execute_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    for flag, value in next_gate_selected_route_execute_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_artifact_executor_input_contract_blocking_reasons(
    next_gate_selected_route_execute_result_review: dict[str, Any],
) -> list[str]:
    records = next_gate_selected_route_execute_result_review.get(
        "route_specific_artifact_executor_input_records",
        [],
    )
    if not records:
        return ["artifact_executor_input_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["artifact_executor_input_record_not_single"]

    record = records[0]
    route_type = record.get("verified_route_type", "unknown")
    contract = ROUTE_CONTRACTS.get(route_type)
    reasons = []
    if contract is None:
        reasons.append(f"artifact_executor_route_type_unknown:{route_type}")
    else:
        if record.get("routed_action") != contract["routed_action"]:
            reasons.append(f"artifact_executor_routed_action_mismatch:{route_type}")
        if record.get("next_command") != contract["next_command"]:
            reasons.append(f"artifact_executor_next_command_mismatch:{route_type}")
        if record.get("planned_outputs") != contract["planned_outputs"]:
            reasons.append(f"artifact_executor_planned_outputs_mismatch:{route_type}")

    if route_type != next_gate_selected_route_execute_result_review.get("verified_route_type", ""):
        reasons.append(f"artifact_executor_route_type_mismatch:{route_type}")
    if record.get("record_id") != f"selected_route_execute_result::{route_type}":
        reasons.append(f"artifact_executor_record_id_mismatch:{route_type}")
    if record.get("selected_route_execute_status") != "selected_route_execute_manifest_recorded":
        reasons.append(f"artifact_executor_selected_route_execute_status_mismatch:{route_type}")
    if record.get("selected_route_execute_report_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH):
        reasons.append(f"artifact_executor_report_path_mismatch:{route_type}")
    if record.get("selected_route_execute_manifest_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH):
        reasons.append(f"artifact_executor_manifest_path_mismatch:{route_type}")
    if (
        record.get("review_status")
        != "selected_route_execute_manifest_accepted_for_route_specific_artifact_executor"
    ):
        reasons.append(f"artifact_executor_review_status_mismatch:{route_type}")
    if record.get("can_continue_to_route_specific_artifact_executor") is not True:
        reasons.append(f"artifact_executor_record_cannot_continue:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(repo_root: Path) -> list[str]:
    if not (repo_root / ARTIFACT_EXECUTOR_COMMAND_PATH).exists():
        return [
            f"route_specific_artifact_executor_command_file_missing:{ARTIFACT_EXECUTOR_COMMAND_PATH}"
        ]
    return []


def build_request_blocking_reasons(
    mode: str,
    confirm_artifact_executor_entry: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["route_specific_artifact_executor_entry_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_artifact_executor_entry:
        reasons.append("confirm_artifact_executor_entry_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("artifact_executor_entry_note_required")
    return reasons


def build_status(
    mode: str,
    result_review_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if result_review_reasons:
        return "blocked_by_next_gate_selected_route_execute_result_review"
    if contract_reasons:
        return "blocked_by_route_specific_artifact_executor_entry_contract"
    if unavailable_reasons:
        return "blocked_by_route_specific_artifact_executor_command_unavailable"
    if "route_specific_artifact_executor_entry_mode_invalid" in request_reasons:
        return "blocked_by_route_specific_artifact_executor_entry_mode"
    if mode == "dry-run":
        return "next_gate_route_specific_artifact_executor_entry_dry_run_ready"
    if "confirm_artifact_executor_entry_required" in request_reasons:
        return "blocked_by_missing_route_specific_artifact_executor_entry_confirmation"
    if request_reasons:
        return "blocked_by_route_specific_artifact_executor_entry_metadata"
    return "ready_to_enter_route_specific_artifact_executor"


def extract_artifact_executor_input_record(
    next_gate_selected_route_execute_result_review: dict[str, Any],
) -> dict[str, Any]:
    records = next_gate_selected_route_execute_result_review.get(
        "route_specific_artifact_executor_input_records",
        [],
    )
    if isinstance(records, list) and len(records) == 1:
        return records[0]
    return {}


def build_artifact_executor_entry_command(project_root: Path, record: dict[str, Any]) -> list[str]:
    return [
        "python3",
        ARTIFACT_EXECUTOR_COMMAND_PATH,
        "--project-root",
        str(project_root),
        "--selected-route-execute",
        record.get("selected_route_execute_report_path", ""),
        "--execute-manifest",
        record.get("selected_route_execute_manifest_path", ""),
        "--mode",
        "dry-run",
        "--output-executor",
        str(DEFAULT_ARTIFACT_EXECUTOR_PATH),
        "--output-review",
        str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH),
    ]


def build_source_result_review_summary(
    next_gate_selected_route_execute_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": next_gate_selected_route_execute_result_review.get("schema_version", ""),
        "status": next_gate_selected_route_execute_result_review.get("status", ""),
        "verified_route_type": next_gate_selected_route_execute_result_review.get("verified_route_type", ""),
        "selected_route_execute_result_reviewed": (
            next_gate_selected_route_execute_result_review.get("selected_route_execute_result_reviewed")
            is True
        ),
        "can_continue_to_route_specific_artifact_executor": (
            next_gate_selected_route_execute_result_review.get(
                "can_continue_to_route_specific_artifact_executor"
            )
            is True
        ),
        "route_specific_artifact_executor_input_records_count": len(
            next_gate_selected_route_execute_result_review.get(
                "route_specific_artifact_executor_input_records",
                [],
            )
        ),
        "source_blocking_reasons": next_gate_selected_route_execute_result_review.get("blocking_reasons", []),
        "boundary_flags": next_gate_selected_route_execute_result_review.get("boundary_flags", {}),
    }


def build_artifact_executor_entry_request(
    mode: str,
    confirm_artifact_executor_entry: bool,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_artifact_executor_entry": confirm_artifact_executor_entry,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_artifact_executor_report_summary(executor_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": executor_report.get("schema_version", ""),
        "status": executor_report.get("status", ""),
        "route_type": executor_report.get("route_type", ""),
        "route_specific_command_executed": executor_report.get("route_specific_command_executed") is True,
        "route_specific_artifact_executed": executor_report.get("route_specific_artifact_executed") is True,
        "blocking_reasons": executor_report.get("blocking_reasons", []),
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
    if status == "next_gate_route_specific_artifact_executor_entry_dry_run_ready":
        return {
            "id": "rerun_with_confirm_artifact_executor_entry",
            "label": "Confirm artifact executor entry",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note to enter the artifact executor dry-run.",
        }
    if status == "ready_to_enter_route_specific_artifact_executor":
        return {
            "id": "enter_route_specific_artifact_executor",
            "label": "Enter route-specific artifact executor",
            "description": "The route-specific artifact executor dry-run command is ready to run.",
        }
    if status == "next_gate_route_specific_artifact_executor_entered":
        return {
            "id": "review_route_specific_artifact_executor_dry_run",
            "label": "Review route-specific artifact executor dry-run",
            "description": f"The `{route_type}` artifact executor dry-run has been entered.",
        }
    if status == "blocked_by_missing_route_specific_artifact_executor_entry_confirmation":
        return {
            "id": "rerun_with_confirm_artifact_executor_entry",
            "label": "Rerun with explicit artifact executor entry confirmation",
            "description": "Execute mode requires --confirm-artifact-executor-entry.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_executor_entry_metadata":
        return {
            "id": "record_artifact_executor_entry_reviewer_and_note",
            "label": "Record artifact executor entry reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_executor_entry_contract":
        return {
            "id": "repair_artifact_executor_entry_contract",
            "label": "Repair artifact executor entry contract",
            "description": "P7-AO must expose exactly one clean route-specific artifact executor input record.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_executor_command_unavailable":
        return {
            "id": "implement_or_restore_artifact_executor_command",
            "label": "Implement artifact executor command",
            "description": "The planned route-specific artifact executor command file is missing.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_executor_entry_failure":
        return {
            "id": "repair_artifact_executor_entry_inputs",
            "label": "Repair artifact executor entry inputs",
            "description": "The artifact executor dry-run command did not return a dry-run-ready report.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_selected_route_execute_result_review_blockers",
        "label": "Resolve P7-AO blockers",
        "description": "P7-AO must be ready before P7-AP can enter the route-specific artifact executor.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_ENTRY_PATH,
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
        "# Auto Mode Formal Package Next Gate Route-Specific Artifact Executor Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        "- 可确认进入 artifact executor："
        f"{str(report['can_enter_route_specific_artifact_executor_with_confirmation']).lower()}",
        f"- artifact executor entry command 数：{len(report['route_specific_artifact_executor_entry_command'])}",
        "- 已运行 artifact executor entry command："
        f"{str(report['route_specific_artifact_executor_entry_command_executed']).lower()}",
        "- 本命令运行 artifact executor："
        f"{str(report['this_command_ran_route_specific_artifact_executor']).lower()}",
        "- 已进入 artifact executor："
        f"{str(report['route_specific_artifact_executor_entered']).lower()}",
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
    if report["route_specific_artifact_executor_entry_command"]:
        lines.extend(["", "## Route-Specific Artifact Executor Entry Command"])
        lines.append(f"- `{' '.join(report['route_specific_artifact_executor_entry_command'])}`")
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

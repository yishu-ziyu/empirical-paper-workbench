from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_route_specific_artifact_executor.v1"
SELECTED_ROUTE_EXECUTE_SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execute.v1"
EXECUTE_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execute_manifest.v1"
DEFAULT_SELECTED_ROUTE_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execute.json")
DEFAULT_EXECUTE_MANIFEST_PATH = Path(
    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
)
DEFAULT_EXECUTOR_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_executor.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_executor.md")
VALID_MODES = {"dry-run", "execute"}
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}
SUCCESS_STATUSES = {
    "pdf_export": {"final_pdf_written", "final_pdf_already_written"},
    "docx_export": {"docx_exported"},
    "package_manifest": {"formal_submission_package_ready"},
    "manual_acceptance": {
        "formal_submission_package_accepted",
        "pending_human_manual_acceptance",
        "formal_submission_package_needs_revision",
        "formal_submission_package_rejected",
    },
}
VALID_MANUAL_DECISIONS = {"accept", "defer", "needs_revision", "reject"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_route_specific_artifact_executor(
    project_root: Path,
    selected_route_execute: dict[str, Any],
    selected_route_execute_manifest: dict[str, Any],
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
    report = build_auto_mode_formal_package_route_specific_artifact_executor(
        project_root,
        selected_route_execute,
        selected_route_execute_manifest,
        mode=mode,
        confirm_artifact_execution=confirm_artifact_execution,
        reviewer=reviewer,
        note=note,
        manual_decision=manual_decision,
        manual_actor=manual_actor,
        manual_note=manual_note,
        source_paths=source_paths,
    )
    if report["status"] != "ready_to_execute_route_specific_artifact":
        return report, 0 if report["status"] == "route_specific_artifact_executor_dry_run_ready" else 2

    result = subprocess.run(
        report["route_specific_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    delegated_report = load_json_or_empty(project_root / report["delegated_report_path"])
    delegated_status = delegated_report.get("status", "")
    route_type = report["route_type"]
    succeeded = result.returncode == 0 and delegated_status in SUCCESS_STATUSES[route_type]
    report["route_specific_command_executed"] = True
    report["delegated_returncode"] = result.returncode
    report["delegated_status"] = delegated_status
    report["route_specific_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": delegated_status,
        "report_path": report["delegated_report_path"],
        "review_path": report["delegated_review_path"],
    }
    if succeeded:
        mark_successful_route_execution(report, delegated_report)
        return report, 0

    report["status"] = "blocked_by_route_specific_artifact_command"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"route_specific_command_failed:{route_type}",
            f"delegated_status:{delegated_status or 'missing'}",
        ]
    )
    report["next_action"] = build_next_action(report["status"], report["blocking_reasons"], route_type)
    return report, 2


def build_auto_mode_formal_package_route_specific_artifact_executor(
    project_root: Path,
    selected_route_execute: dict[str, Any],
    selected_route_execute_manifest: dict[str, Any],
    *,
    mode: str = "dry-run",
    confirm_artifact_execution: bool = False,
    reviewer: str = "",
    note: str = "",
    manual_decision: str = "defer",
    manual_actor: str = "",
    manual_note: str = "",
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    execute_reasons = build_selected_route_execute_blocking_reasons(selected_route_execute)
    manifest_reasons = (
        build_execute_manifest_blocking_reasons(selected_route_execute_manifest) if not execute_reasons else []
    )
    contract_reasons = (
        build_route_operation_contract_blocking_reasons(selected_route_execute_manifest)
        if not execute_reasons and not manifest_reasons
        else []
    )
    request_reasons = build_request_blocking_reasons(mode, confirm_artifact_execution, reviewer, note, manual_decision)
    route_type = extract_route_type(selected_route_execute_manifest) if not contract_reasons else ""
    status = build_status(mode, execute_reasons, manifest_reasons, contract_reasons, request_reasons)
    command = (
        build_route_specific_command(
            project_root,
            route_type,
            reviewer=reviewer,
            note=note,
            manual_decision=manual_decision,
            manual_actor=manual_actor,
            manual_note=manual_note,
        )
        if status in {"route_specific_artifact_executor_dry_run_ready", "ready_to_execute_route_specific_artifact"}
        else []
    )
    delegated_paths = build_delegated_paths(route_type)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": selected_route_execute.get("topic", selected_route_execute_manifest.get("topic", "")),
        "source_paths": {
            "selected_route_execute": source_paths.get(
                "selected_route_execute",
                str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH),
            ),
            "selected_route_execute_manifest": source_paths.get(
                "selected_route_execute_manifest",
                str(DEFAULT_EXECUTE_MANIFEST_PATH),
            ),
        },
        "status": status,
        "mode": mode,
        "confirm_artifact_execution": confirm_artifact_execution,
        "can_execute_route_specific_artifact_with_confirmation": not execute_reasons
        and not manifest_reasons
        and not contract_reasons,
        "route_type": route_type,
        "route_specific_artifact_executed": False,
        "route_specific_command_executed": False,
        "route_specific_command": command,
        "delegated_report_path": delegated_paths["report"],
        "delegated_review_path": delegated_paths["review"],
        "delegated_returncode": None,
        "delegated_status": "",
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": execute_reasons + manifest_reasons + contract_reasons + request_reasons,
        "source_execute": build_source_execute(selected_route_execute),
        "source_manifest": build_source_manifest(selected_route_execute_manifest),
        "artifact_execution_request": build_artifact_execution_request(
            mode,
            confirm_artifact_execution,
            reviewer,
            note,
            manual_decision,
            manual_actor,
            manual_note,
        ),
        "selected_route_operation": extract_route_operation(selected_route_execute_manifest)
        if not contract_reasons and not manifest_reasons
        else {},
        "route_specific_result": {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, execute_reasons + manifest_reasons + contract_reasons + request_reasons, route_type),
    }


def build_selected_route_execute_blocking_reasons(selected_route_execute: dict[str, Any]) -> list[str]:
    reasons = []
    if selected_route_execute.get("schema_version") != SELECTED_ROUTE_EXECUTE_SCHEMA_VERSION:
        reasons.append("selected_route_execute_missing_or_invalid_schema")
    if selected_route_execute.get("status") != "selected_route_execute_manifest_recorded":
        reasons.append("selected_route_execute_not_manifest_recorded")
    if selected_route_execute.get("selected_route_execute_manifest_recorded") is not True:
        reasons.append("selected_route_execute_manifest_not_recorded")
    if selected_route_execute.get("can_execute_selected_route_with_confirmation") is not True:
        reasons.append("selected_route_execute_cannot_execute_with_confirmation")
    if selected_route_execute.get("selected_route_executed") is True:
        reasons.append("selected_route_execute_already_executed")
    if selected_route_execute.get("export_or_acceptance_executed") is True:
        reasons.append("selected_route_execute_already_exported_or_accepted")
    if selected_route_execute.get("rendered_pdf") is True:
        reasons.append("selected_route_execute_already_rendered_pdf")
    if selected_route_execute.get("rendered_docx") is True:
        reasons.append("selected_route_execute_already_rendered_docx")
    if selected_route_execute.get("package_manifest_generated") is True:
        reasons.append("selected_route_execute_already_generated_package_manifest")
    if selected_route_execute.get("manual_acceptance_performed") is True:
        reasons.append("selected_route_execute_already_performed_manual_acceptance")
    if selected_route_execute.get("this_command_wrote_formal_state") is True:
        reasons.append("selected_route_execute_wrote_formal_state")
    if selected_route_execute.get("can_write_product_state") is True:
        reasons.append("selected_route_execute_allows_product_state_write")
    for flag, value in selected_route_execute.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"selected_route_execute_boundary_violation:{flag}")
    return dedupe(reasons)


def build_execute_manifest_blocking_reasons(selected_route_execute_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    if selected_route_execute_manifest.get("schema_version") != EXECUTE_MANIFEST_SCHEMA_VERSION:
        reasons.append("selected_route_execute_manifest_missing_or_invalid_schema")
    if selected_route_execute_manifest.get("selected_route_executed") is True:
        reasons.append("selected_route_execute_manifest_already_executed")
    if selected_route_execute_manifest.get("export_or_acceptance_executed") is True:
        reasons.append("selected_route_execute_manifest_already_exported_or_accepted")
    if selected_route_execute_manifest.get("rendered_pdf") is True:
        reasons.append("selected_route_execute_manifest_rendered_pdf")
    if selected_route_execute_manifest.get("rendered_docx") is True:
        reasons.append("selected_route_execute_manifest_rendered_docx")
    if selected_route_execute_manifest.get("package_manifest_generated") is True:
        reasons.append("selected_route_execute_manifest_generated_package_manifest")
    if selected_route_execute_manifest.get("manual_acceptance_performed") is True:
        reasons.append("selected_route_execute_manifest_performed_manual_acceptance")
    if selected_route_execute_manifest.get("this_command_wrote_formal_state") is True:
        reasons.append("selected_route_execute_manifest_wrote_formal_state")
    if selected_route_execute_manifest.get("can_write_product_state") is True:
        reasons.append("selected_route_execute_manifest_allows_product_state_write")
    for flag, value in selected_route_execute_manifest.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"selected_route_execute_manifest_boundary_violation:{flag}")
    return dedupe(reasons)


def build_route_operation_contract_blocking_reasons(selected_route_execute_manifest: dict[str, Any]) -> list[str]:
    operations = selected_route_execute_manifest.get("selected_route_execute_operations", [])
    if len(operations) != 1:
        return ["selected_route_execute_operations_not_single"]
    operation = operations[0]
    route_type = operation.get("route_type", "unknown")
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"route_type_unknown:{route_type}")
    if not operation.get("operation_id"):
        reasons.append(f"route_operation_id_missing:{route_type}")
    if not operation.get("route_execution_id"):
        reasons.append(f"route_execution_id_missing:{route_type}")
    if not operation.get("routed_action"):
        reasons.append(f"route_routed_action_missing:{route_type}")
    if not operation.get("next_command"):
        reasons.append(f"route_next_command_missing:{route_type}")
    if not operation.get("planned_outputs"):
        reasons.append(f"route_operation_planned_outputs_missing:{route_type}")
    if operation.get("operation_status") != "planned_not_executed":
        reasons.append(f"route_operation_not_planned:{route_type}")
    if operation.get("will_execute_selected_route") is True:
        reasons.append(f"route_operation_marked_execute_by_this_command:{route_type}")
    if operation.get("will_render_pdf") is True:
        reasons.append(f"route_operation_marked_render_pdf:{route_type}")
    if operation.get("will_render_docx") is True:
        reasons.append(f"route_operation_marked_render_docx:{route_type}")
    if operation.get("will_generate_package_manifest") is True:
        reasons.append(f"route_operation_marked_generate_manifest:{route_type}")
    if operation.get("will_perform_manual_acceptance") is True:
        reasons.append(f"route_operation_marked_manual_acceptance:{route_type}")
    if operation.get("will_write_product_state") is True:
        reasons.append(f"route_operation_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_request_blocking_reasons(
    mode: str,
    confirm_artifact_execution: bool,
    reviewer: str,
    note: str,
    manual_decision: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["artifact_execution_mode_invalid"]
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
    execute_reasons: list[str],
    manifest_reasons: list[str],
    contract_reasons: list[str],
    request_reasons: list[str],
) -> str:
    if execute_reasons:
        return "blocked_by_selected_route_execute"
    if manifest_reasons:
        return "blocked_by_selected_route_execute_manifest"
    if contract_reasons:
        return "blocked_by_route_specific_artifact_contract"
    if "artifact_execution_mode_invalid" in request_reasons:
        return "blocked_by_artifact_execution_mode"
    if any(reason.startswith("manual_decision_invalid") for reason in request_reasons):
        return "blocked_by_artifact_execution_metadata"
    if mode == "dry-run":
        return "route_specific_artifact_executor_dry_run_ready"
    if "confirm_artifact_execution_required" in request_reasons:
        return "blocked_by_missing_artifact_execution_confirmation"
    if request_reasons:
        return "blocked_by_artifact_execution_metadata"
    return "ready_to_execute_route_specific_artifact"


def build_route_specific_command(
    project_root: Path,
    route_type: str,
    *,
    reviewer: str,
    note: str,
    manual_decision: str,
    manual_actor: str,
    manual_note: str,
) -> list[str]:
    common = ["python3"]
    if route_type == "pdf_export":
        return common + [
            "Program/formal_pdf_final_writeback.py",
            "--project-root",
            str(project_root),
            "--output-report",
            "Results/json/formal_pdf_final_writeback.json",
            "--output-review",
            "Reviews/formal_pdf_final_writeback.md",
            "--output-pdf",
            "Submissions/formal_package/paper.pdf",
        ]
    if route_type == "docx_export":
        return common + [
            "Program/formal_docx_export.py",
            "--project-root",
            str(project_root),
            "--preflight-report",
            "Results/json/formal_docx_export_preflight.json",
            "--output-report",
            "Results/json/formal_docx_export.json",
            "--output-review",
            "Reviews/formal_docx_export.md",
            "--output-docx",
            "Submissions/formal_package/paper.docx",
            "--log-path",
            "Results/logs/formal_docx_export.log",
        ]
    if route_type == "package_manifest":
        return common + [
            "Program/formal_submission_package_manifest.py",
            "--project-root",
            str(project_root),
            "--output-report",
            "Results/json/formal_submission_package_manifest.json",
            "--output-review",
            "Reviews/formal_submission_package_acceptance.md",
            "--package-manifest",
            "Submissions/formal_package/manifest.json",
        ]
    if route_type == "manual_acceptance":
        return common + [
            "Program/formal_submission_package_manual_acceptance.py",
            "--project-root",
            str(project_root),
            "--summary",
            "state/product/formal_submission_package_summary.json",
            "--decision",
            manual_decision,
            "--actor",
            manual_actor.strip() or reviewer,
            "--note",
            manual_note.strip() or note,
            "--output-report",
            "Results/json/formal_submission_package_manual_acceptance.json",
            "--output-state",
            "state/product/formal_submission_package_manual_acceptance.json",
            "--output-review",
            "Reviews/formal_submission_package_manual_acceptance.md",
        ]
    return []


def mark_successful_route_execution(report: dict[str, Any], delegated_report: dict[str, Any]) -> None:
    route_type = report["route_type"]
    report["status"] = "route_specific_artifact_executed"
    report["route_specific_artifact_executed"] = True
    report["selected_route_executed"] = True
    report["export_or_acceptance_executed"] = True
    report["rendered_pdf"] = route_type == "pdf_export"
    report["rendered_docx"] = route_type == "docx_export"
    report["package_manifest_generated"] = route_type == "package_manifest"
    report["manual_acceptance_performed"] = route_type == "manual_acceptance"
    report["formal_writeback_executed"] = False
    report["this_command_wrote_formal_state"] = False
    report["can_write_product_state"] = route_type == "manual_acceptance"
    report["blocking_reasons"] = []
    report["route_specific_result"]["delegated_report_summary"] = build_delegated_report_summary(delegated_report)
    report["next_action"] = build_next_action(report["status"], [], route_type)


def build_delegated_report_summary(delegated_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": delegated_report.get("schema_version", ""),
        "status": delegated_report.get("status", ""),
        "blocking_reasons": delegated_report.get("blocking_reasons", []),
    }


def build_source_execute(selected_route_execute: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execute.get("schema_version", ""),
        "status": selected_route_execute.get("status", ""),
        "selected_route_execute_manifest_recorded": selected_route_execute.get(
            "selected_route_execute_manifest_recorded"
        )
        is True,
        "can_execute_selected_route_with_confirmation": selected_route_execute.get(
            "can_execute_selected_route_with_confirmation"
        )
        is True,
        "selected_route_execute_operations_count": len(selected_route_execute.get("selected_route_execute_operations", [])),
        "blocking_reasons": selected_route_execute.get("blocking_reasons", []),
    }


def build_source_manifest(selected_route_execute_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execute_manifest.get("schema_version", ""),
        "selected_route_execute_operations_count": len(
            selected_route_execute_manifest.get("selected_route_execute_operations", [])
        ),
        "selected_route_executed": selected_route_execute_manifest.get("selected_route_executed") is True,
        "export_or_acceptance_executed": selected_route_execute_manifest.get("export_or_acceptance_executed") is True,
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


def build_delegated_paths(route_type: str) -> dict[str, str]:
    return {
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
    }.get(route_type, {"report": "", "review": ""})


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
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "route_specific_artifact_executor_dry_run_ready":
        return {
            "id": "rerun_with_confirm_artifact_execution",
            "label": "Confirm route-specific artifact execution",
            "description": "Dry-run is ready; rerun with confirmation, reviewer, and note to execute the delegated artifact command.",
        }
    if status == "ready_to_execute_route_specific_artifact":
        return {
            "id": "execute_delegated_artifact_command",
            "label": "Execute delegated artifact command",
            "description": "The delegated command is ready to run.",
        }
    if status == "route_specific_artifact_executed":
        return {
            "id": "verify_route_specific_artifact",
            "label": "Verify route-specific artifact",
            "description": f"The `{route_type}` route executed; verify the resulting formal package artifact.",
        }
    if status == "blocked_by_missing_artifact_execution_confirmation":
        return {
            "id": "rerun_with_confirm_artifact_execution",
            "label": "Rerun with explicit artifact execution confirmation",
            "description": "Execute mode requires --confirm-artifact-execution.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_artifact_execution_metadata":
        return {
            "id": "record_artifact_execution_reviewer_and_note",
            "label": "Record artifact execution reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_command":
        return {
            "id": "repair_delegated_artifact_command_inputs",
            "label": "Repair delegated artifact command inputs",
            "description": "The selected route command ran but did not complete successfully.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_contract":
        return {
            "id": "repair_selected_route_execute_manifest",
            "label": "Repair selected route execute manifest",
            "description": "The execute manifest must contain exactly one clean route operation.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_selected_route_execute_manifest":
        return {
            "id": "record_selected_route_execute_manifest",
            "label": "Record selected route execute manifest",
            "description": "P7-AA must write a valid execute manifest before artifact dispatch.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_selected_route_execute_blockers",
        "label": "Resolve selected route execute blockers",
        "description": "P7-AA must be confirmed and manifest-recorded before route-specific execution.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_route_specific_artifact_executor_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTOR_PATH,
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
        "# Auto Mode Formal Package Route-Specific Artifact Executor",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- 路线类型：`{report['route_type']}`",
        f"- 可确认执行：{str(report['can_execute_route_specific_artifact_with_confirmation']).lower()}",
        f"- 已执行 route-specific artifact：{str(report['route_specific_artifact_executed']).lower()}",
        f"- delegated command 已运行：{str(report['route_specific_command_executed']).lower()}",
        f"- delegated status：`{report['delegated_status']}`",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- PDF 已生成：{str(report['rendered_pdf']).lower()}",
        f"- DOCX 已生成：{str(report['rendered_docx']).lower()}",
        f"- package manifest 已生成：{str(report['package_manifest_generated']).lower()}",
        f"- 人工验收已执行：{str(report['manual_acceptance_performed']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["route_specific_command"]:
        lines.extend(["", "## Delegated Command", ""])
        lines.append("```bash")
        lines.append(" ".join(str(item) for item in report["route_specific_command"]))
        lines.append("```")
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def extract_route_operation(selected_route_execute_manifest: dict[str, Any]) -> dict[str, Any]:
    operations = selected_route_execute_manifest.get("selected_route_execute_operations", [])
    return operations[0] if len(operations) == 1 else {}


def extract_route_type(selected_route_execute_manifest: dict[str, Any]) -> str:
    return extract_route_operation(selected_route_execute_manifest).get("route_type", "")


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

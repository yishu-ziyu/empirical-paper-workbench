from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.v1"
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.v1"
)
RESULT_REVIEW_READY_STATUS = "route_specific_artifact_execution_result_review_ready"
VERIFICATION_SUCCESS_STATUS = "route_specific_artifact_verified_for_review"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.json"
)
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry.md"
)
DEFAULT_ARTIFACT_EXECUTOR_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_executor.json")
DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_executor.md")
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_verification.json")
DEFAULT_VERIFICATION_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_verification.md")
ARTIFACT_VERIFICATION_COMMAND_PATH = "Program/auto_mode_formal_package_route_specific_artifact_verification.py"
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}
DELEGATED_SUCCESS_STATUSES = {
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
DELEGATED_PATHS = {
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


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
    project_root: Path,
    route_specific_artifact_execution_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> tuple[dict[str, Any], int]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    report = build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
        project_root,
        route_specific_artifact_execution_result_review,
        source_paths=source_paths,
        repo_root=repo_root,
    )
    if report["status"] != "ready_to_enter_route_specific_artifact_verification":
        return report, 0

    result = subprocess.run(
        report["route_specific_artifact_verification_entry_command"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    verification_report = load_json_or_empty(project_root / report["route_specific_artifact_verification_report_path"])
    verification_status = verification_report.get("status", "")
    report["route_specific_artifact_verification_entry_command_executed"] = True
    report["this_command_ran_route_specific_artifact_verification"] = True
    report["route_specific_artifact_verification_returncode"] = result.returncode
    report["route_specific_artifact_verification_status"] = verification_status
    report["route_specific_artifact_verification_result"] = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "status": verification_status,
        "report_path": report["route_specific_artifact_verification_report_path"],
        "review_path": report["route_specific_artifact_verification_review_path"],
        "route_specific_artifact_verification_report_summary": build_verification_report_summary(
            verification_report
        ),
    }
    if result.returncode == 0 and verification_status == VERIFICATION_SUCCESS_STATUS:
        mark_successful_verification_entry(report, verification_report)
        return report, 0

    report["status"] = "blocked_by_route_specific_artifact_verification_failure"
    report["blocking_reasons"] = dedupe(
        report["blocking_reasons"]
        + [
            f"route_specific_artifact_verification_command_failed:{report['verified_route_type']}",
            f"route_specific_artifact_verification_status:{verification_status or 'missing'}",
        ]
    )
    report["route_specific_artifact_verified"] = verification_report.get("route_specific_artifact_verified") is True
    report["verified_route_type"] = verification_report.get("verified_route_type", report["verified_route_type"])
    report["verification_artifact_record_count"] = len(verification_report.get("artifact_verification_records", []))
    report["artifact_verification_records"] = verification_report.get("artifact_verification_records", [])
    report["next_action"] = build_next_action(
        report["status"],
        report["blocking_reasons"],
        report["verified_route_type"],
    )
    return report, 2


def build_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry(
    project_root: Path,
    route_specific_artifact_execution_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    source_paths = source_paths or {}
    result_review_reasons = build_result_review_blocking_reasons(route_specific_artifact_execution_result_review)
    contract_reasons = (
        build_verification_input_record_contract_blocking_reasons(
            route_specific_artifact_execution_result_review
        )
        if not result_review_reasons
        else []
    )
    unavailable_reasons = (
        build_command_unavailable_reasons(repo_root)
        if not result_review_reasons and not contract_reasons
        else []
    )
    status = build_status(result_review_reasons, contract_reasons, unavailable_reasons)
    record = extract_verification_input_record(route_specific_artifact_execution_result_review)
    can_enter = not result_review_reasons and not contract_reasons and not unavailable_reasons
    route_type = record.get("verified_route_type", "") if can_enter else ""
    command = build_artifact_verification_entry_command(project_root, record) if can_enter else []
    blocking_reasons = dedupe(result_review_reasons + contract_reasons + unavailable_reasons)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": route_specific_artifact_execution_result_review.get("topic", ""),
        "source_paths": {
            "route_specific_artifact_execution_result_review": source_paths.get(
                "route_specific_artifact_execution_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": route_specific_artifact_execution_result_review.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "can_enter_route_specific_artifact_verification": can_enter,
        "route_specific_artifact_verification_entry_command": command,
        "route_specific_artifact_verification_entry_command_executed": False,
        "this_command_ran_route_specific_artifact_verification": False,
        "route_specific_artifact_verification_report_path": str(DEFAULT_VERIFICATION_PATH) if can_enter else "",
        "route_specific_artifact_verification_review_path": str(DEFAULT_VERIFICATION_REVIEW_PATH)
        if can_enter
        else "",
        "route_specific_artifact_verification_returncode": None,
        "route_specific_artifact_verification_status": "",
        "route_specific_artifact_verification_result": {},
        "route_specific_artifact_verified": False,
        "verification_artifact_record_count": 0,
        "artifact_verification_records": [],
        "delegated_status": record.get("delegated_status", "") if can_enter else "",
        "route_specific_command_executed": (
            route_specific_artifact_execution_result_review.get("route_specific_command_executed") is True
            if can_enter
            else False
        ),
        "route_specific_artifact_executed": (
            route_specific_artifact_execution_result_review.get("route_specific_artifact_executed") is True
            if can_enter
            else False
        ),
        "selected_route_executed": (
            route_specific_artifact_execution_result_review.get("selected_route_executed") is True
            if can_enter
            else False
        ),
        "export_or_acceptance_executed": (
            route_specific_artifact_execution_result_review.get("export_or_acceptance_executed") is True
            if can_enter
            else False
        ),
        "rendered_pdf": (
            route_specific_artifact_execution_result_review.get("rendered_pdf") is True if can_enter else False
        ),
        "rendered_docx": (
            route_specific_artifact_execution_result_review.get("rendered_docx") is True if can_enter else False
        ),
        "package_manifest_generated": (
            route_specific_artifact_execution_result_review.get("package_manifest_generated") is True
            if can_enter
            else False
        ),
        "manual_acceptance_performed": (
            route_specific_artifact_execution_result_review.get("manual_acceptance_performed") is True
            if can_enter
            else False
        ),
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_result_review": build_source_result_review_summary(
            route_specific_artifact_execution_result_review
        ),
        "route_specific_artifact_verification_input_record": record if can_enter else {},
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_result_review_blocking_reasons(
    route_specific_artifact_execution_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    if route_specific_artifact_execution_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("route_specific_artifact_execution_result_review_missing_or_invalid_schema")
    if route_specific_artifact_execution_result_review.get("status") != RESULT_REVIEW_READY_STATUS:
        reasons.append("route_specific_artifact_execution_result_review_not_ready")
    if route_specific_artifact_execution_result_review.get("artifact_execution_result_reviewed") is not True:
        reasons.append("artifact_execution_result_not_reviewed")
    if (
        route_specific_artifact_execution_result_review.get(
            "can_continue_to_route_specific_artifact_verification"
        )
        is not True
    ):
        reasons.append("result_review_cannot_continue_to_route_specific_artifact_verification")
    if not route_specific_artifact_execution_result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    for field in [
        "route_specific_command_executed",
        "route_specific_artifact_executed",
        "selected_route_executed",
        "export_or_acceptance_executed",
    ]:
        if route_specific_artifact_execution_result_review.get(field) is not True:
            reasons.append(f"result_review_{field}_missing")
    for field in ["formal_writeback_executed", "this_command_wrote_formal_state"]:
        if route_specific_artifact_execution_result_review.get(field) is True:
            reasons.append(f"result_review_{field}")
    if route_specific_artifact_execution_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    for flag, value in route_specific_artifact_execution_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_verification_input_record_contract_blocking_reasons(
    route_specific_artifact_execution_result_review: dict[str, Any],
) -> list[str]:
    records = route_specific_artifact_execution_result_review.get(
        "route_specific_artifact_verification_input_records",
        [],
    )
    if not records:
        return ["route_specific_artifact_verification_input_record_missing"]
    if not isinstance(records, list) or len(records) != 1:
        return ["route_specific_artifact_verification_input_record_not_single"]

    record = records[0]
    route_type = route_specific_artifact_execution_result_review.get("verified_route_type", "unknown")
    delegated_paths = DELEGATED_PATHS.get(route_type, {"report": "", "review": ""})
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"route_specific_artifact_verification_route_type_unknown:{route_type}")
    if record.get("record_id") != f"artifact_execution_result::{route_type}":
        reasons.append(f"route_specific_artifact_verification_input_record_id_mismatch:{route_type}")
    if record.get("verified_route_type") != route_type:
        reasons.append(f"route_specific_artifact_verification_input_record_route_type_mismatch:{route_type}")
    if record.get("artifact_executor_status") != "route_specific_artifact_executed":
        reasons.append(f"artifact_executor_status_mismatch:{route_type}")
    if record.get("artifact_executor_report_path") != str(DEFAULT_ARTIFACT_EXECUTOR_PATH):
        reasons.append(f"artifact_executor_report_path_mismatch:{route_type}")
    if record.get("artifact_executor_review_path") != str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH):
        reasons.append(f"artifact_executor_review_path_mismatch:{route_type}")
    if record.get("delegated_report_path") != delegated_paths["report"]:
        reasons.append(f"delegated_report_path_mismatch:{route_type}")
    if record.get("delegated_review_path") != delegated_paths["review"]:
        reasons.append(f"delegated_review_path_mismatch:{route_type}")
    if record.get("delegated_status") not in DELEGATED_SUCCESS_STATUSES.get(route_type, set()):
        reasons.append(f"delegated_status_not_success:{route_type}")
    if record.get("review_status") != "artifact_execution_accepted_for_route_specific_artifact_verification":
        reasons.append(f"route_specific_artifact_verification_input_record_review_status_mismatch:{route_type}")
    if record.get("can_continue_to_route_specific_artifact_verification") is not True:
        reasons.append(f"route_specific_artifact_verification_input_record_cannot_continue:{route_type}")
    return dedupe(reasons)


def build_command_unavailable_reasons(repo_root: Path) -> list[str]:
    command_path = repo_root / ARTIFACT_VERIFICATION_COMMAND_PATH
    if not command_path.exists() or command_path.is_dir():
        return [
            "route_specific_artifact_verification_command_file_missing:"
            f"{ARTIFACT_VERIFICATION_COMMAND_PATH}"
        ]
    return []


def build_status(
    result_review_reasons: list[str],
    contract_reasons: list[str],
    unavailable_reasons: list[str],
) -> str:
    if result_review_reasons:
        return "blocked_by_route_specific_artifact_execution_result_review"
    if contract_reasons:
        return "blocked_by_route_specific_artifact_verification_entry_contract"
    if unavailable_reasons:
        return "blocked_by_route_specific_artifact_verification_command_unavailable"
    return "ready_to_enter_route_specific_artifact_verification"


def extract_verification_input_record(route_specific_artifact_execution_result_review: dict[str, Any]) -> dict[str, Any]:
    records = route_specific_artifact_execution_result_review.get(
        "route_specific_artifact_verification_input_records",
        [],
    )
    return records[0] if isinstance(records, list) and len(records) == 1 and isinstance(records[0], dict) else {}


def build_artifact_verification_entry_command(project_root: Path, record: dict[str, Any]) -> list[str]:
    return [
        "python3",
        ARTIFACT_VERIFICATION_COMMAND_PATH,
        "--project-root",
        str(project_root),
        "--route-specific-artifact-executor",
        record.get("artifact_executor_report_path", str(DEFAULT_ARTIFACT_EXECUTOR_PATH)),
        "--delegated-report",
        record.get("delegated_report_path", ""),
        "--output-verification",
        str(DEFAULT_VERIFICATION_PATH),
        "--output-review",
        str(DEFAULT_VERIFICATION_REVIEW_PATH),
    ]


def mark_successful_verification_entry(report: dict[str, Any], verification_report: dict[str, Any]) -> None:
    report["status"] = "next_gate_route_specific_artifact_verification_entered"
    report["blocking_reasons"] = []
    report["verified_route_type"] = verification_report.get("verified_route_type", report["verified_route_type"])
    report["delegated_status"] = verification_report.get("delegated_status", report["delegated_status"])
    report["route_specific_artifact_verified"] = True
    report["verification_artifact_record_count"] = len(verification_report.get("artifact_verification_records", []))
    report["artifact_verification_records"] = verification_report.get("artifact_verification_records", [])
    report["selected_route_executed"] = verification_report.get("selected_route_executed") is True
    report["export_or_acceptance_executed"] = verification_report.get("export_or_acceptance_executed") is True
    report["rendered_pdf"] = verification_report.get("rendered_pdf") is True
    report["rendered_docx"] = verification_report.get("rendered_docx") is True
    report["package_manifest_generated"] = verification_report.get("package_manifest_generated") is True
    report["manual_acceptance_performed"] = verification_report.get("manual_acceptance_performed") is True
    report["can_write_product_state"] = False
    report["next_action"] = build_next_action(report["status"], [], report["verified_route_type"])


def build_verification_report_summary(verification_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": verification_report.get("schema_version", ""),
        "status": verification_report.get("status", ""),
        "route_type": verification_report.get("route_type", ""),
        "verified_route_type": verification_report.get("verified_route_type", ""),
        "delegated_status": verification_report.get("delegated_status", ""),
        "route_specific_artifact_verified": verification_report.get("route_specific_artifact_verified") is True,
        "artifact_verification_record_count": len(verification_report.get("artifact_verification_records", [])),
        "blocking_reasons": verification_report.get("blocking_reasons", []),
    }


def build_source_result_review_summary(
    route_specific_artifact_execution_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_execution_result_review.get("schema_version", ""),
        "status": route_specific_artifact_execution_result_review.get("status", ""),
        "verified_route_type": route_specific_artifact_execution_result_review.get("verified_route_type", ""),
        "artifact_execution_result_reviewed": (
            route_specific_artifact_execution_result_review.get("artifact_execution_result_reviewed") is True
        ),
        "can_continue_to_route_specific_artifact_verification": (
            route_specific_artifact_execution_result_review.get(
                "can_continue_to_route_specific_artifact_verification"
            )
            is True
        ),
        "verification_input_record_count": len(
            route_specific_artifact_execution_result_review.get(
                "route_specific_artifact_verification_input_records",
                [],
            )
            or []
        ),
        "blocking_reasons": route_specific_artifact_execution_result_review.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_execution_result_review.get("boundary_flags", {}),
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
        "verified_route_specific_artifact": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "next_gate_route_specific_artifact_verification_entered":
        return {
            "id": "review_route_specific_artifact_verification_entry_result",
            "label": "Review route-specific artifact verification entry result",
            "description": f"The `{route_type}` route artifact verification completed and can be reviewed.",
        }
    if status == "ready_to_enter_route_specific_artifact_verification":
        return {
            "id": "run_route_specific_artifact_verification",
            "label": "Run route-specific artifact verification",
            "description": f"The `{route_type}` route artifact can be verified by the existing verifier.",
        }
    if status == "blocked_by_route_specific_artifact_verification_entry_contract":
        return {
            "id": "repair_route_specific_artifact_verification_input_record",
            "label": "Repair route-specific artifact verification input record",
            "description": "P7-AS must provide exactly one accepted verification input record.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_verification_command_unavailable":
        return {
            "id": "restore_route_specific_artifact_verification_command",
            "label": "Restore route-specific artifact verification command",
            "description": "The existing artifact verification CLI must be available before P7-AT can run.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_verification_failure":
        return {
            "id": "repair_route_specific_artifact_verification_failure",
            "label": "Repair route-specific artifact verification failure",
            "description": "The verifier ran, but the selected route artifact was not verified.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_artifact_execution_result_review_blockers",
        "label": "Resolve P7-AS blockers",
        "description": "P7-AS must accept one executed route-specific artifact before verification can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_route_specific_artifact_verification_entry_outputs(
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
        "# Auto Mode Formal Package Next Gate Route-Specific Artifact Verification Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- delegated status：`{report['delegated_status']}`",
        "- 可进入 route-specific artifact verification："
        f"{str(report['can_enter_route_specific_artifact_verification']).lower()}",
        "- verification command 已执行："
        f"{str(report['route_specific_artifact_verification_entry_command_executed']).lower()}",
        "- 本命令运行 route-specific artifact verification："
        f"{str(report['this_command_ran_route_specific_artifact_verification']).lower()}",
        f"- verification status：`{report['route_specific_artifact_verification_status']}`",
        f"- 已验证 route-specific artifact：{str(report['route_specific_artifact_verified']).lower()}",
        f"- verification artifact record 数：{report['verification_artifact_record_count']}",
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
    if report["artifact_verification_records"]:
        lines.extend(["", "## Artifact Verification Records"])
        for record in report["artifact_verification_records"]:
            lines.append(
                f"- `{record['artifact_id']}`: `{record['path']}` / "
                f"status=`{record['verification_status']}`"
            )
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

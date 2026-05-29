from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.v1"
EXECUTION_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_execution.v1"
ARTIFACT_EXECUTOR_SCHEMA_VERSION = "p7.auto_mode_formal_package_route_specific_artifact_executor.v1"
EXECUTION_READY_STATUS = "next_gate_route_specific_artifact_executed"
ARTIFACT_EXECUTOR_SUCCESS_STATUS = "route_specific_artifact_executed"
DEFAULT_EXECUTION_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution.json"
)
DEFAULT_ARTIFACT_EXECUTOR_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_executor.json")
DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_executor.md")
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review.md"
)
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
ROUTE_FLAGS = {
    "pdf_export": {
        "rendered_pdf": True,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
    },
    "docx_export": {
        "rendered_pdf": False,
        "rendered_docx": True,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
    },
    "package_manifest": {
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": True,
        "manual_acceptance_performed": False,
    },
    "manual_acceptance": {
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": True,
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review(
    project_root: Path,
    route_specific_artifact_execution: dict[str, Any],
    route_specific_artifact_executor: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    execution_reasons = build_artifact_execution_blocking_reasons(route_specific_artifact_execution)
    executor_has_valid_schema = route_specific_artifact_executor.get("schema_version") == ARTIFACT_EXECUTOR_SCHEMA_VERSION
    contract_reasons = (
        build_artifact_execution_result_contract_blocking_reasons(
            route_specific_artifact_execution,
            route_specific_artifact_executor,
        )
        if not execution_reasons and executor_has_valid_schema
        else []
    )
    executor_reasons = (
        build_artifact_executor_output_blocking_reasons(
            route_specific_artifact_execution,
            route_specific_artifact_executor,
        )
        if not execution_reasons and not contract_reasons
        else []
    )
    blocking_reasons = dedupe(execution_reasons + contract_reasons + executor_reasons)
    status = build_status(execution_reasons, contract_reasons, executor_reasons)
    ready = status == "route_specific_artifact_execution_result_review_ready"
    route_type = route_specific_artifact_execution.get("verified_route_type", "") if ready else ""

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": route_specific_artifact_execution.get(
            "topic",
            route_specific_artifact_executor.get("topic", ""),
        ),
        "source_paths": {
            "route_specific_artifact_execution": source_paths.get(
                "route_specific_artifact_execution",
                str(DEFAULT_EXECUTION_PATH),
            ),
            "route_specific_artifact_executor": source_paths.get(
                "route_specific_artifact_executor",
                str(DEFAULT_ARTIFACT_EXECUTOR_PATH),
            ),
        },
        "source_status": route_specific_artifact_execution.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "artifact_executor_status": route_specific_artifact_executor.get("status", "") if ready else "",
        "artifact_execution_result_reviewed": ready,
        "can_continue_to_route_specific_artifact_verification": ready,
        "route_specific_artifact_verification_input_records": (
            build_route_specific_artifact_verification_input_records(route_specific_artifact_executor)
            if ready
            else []
        ),
        "route_specific_command_executed": route_specific_artifact_executor.get("route_specific_command_executed")
        is True
        if ready
        else False,
        "route_specific_artifact_executed": route_specific_artifact_executor.get("route_specific_artifact_executed")
        is True
        if ready
        else False,
        "selected_route_executed": route_specific_artifact_executor.get("selected_route_executed") is True
        if ready
        else False,
        "export_or_acceptance_executed": route_specific_artifact_executor.get("export_or_acceptance_executed")
        is True
        if ready
        else False,
        "rendered_pdf": route_specific_artifact_executor.get("rendered_pdf") is True if ready else False,
        "rendered_docx": route_specific_artifact_executor.get("rendered_docx") is True if ready else False,
        "package_manifest_generated": route_specific_artifact_executor.get("package_manifest_generated") is True
        if ready
        else False,
        "manual_acceptance_performed": route_specific_artifact_executor.get("manual_acceptance_performed") is True
        if ready
        else False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": route_specific_artifact_executor.get("can_write_product_state") is True
        if ready
        else False,
        "blocking_reasons": blocking_reasons,
        "source_artifact_execution": build_source_artifact_execution_summary(route_specific_artifact_execution),
        "source_artifact_executor": build_source_artifact_executor_summary(route_specific_artifact_executor),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_artifact_execution_blocking_reasons(route_specific_artifact_execution: dict[str, Any]) -> list[str]:
    reasons = []
    route_type = route_specific_artifact_execution.get("verified_route_type", "unknown")
    if route_specific_artifact_execution.get("schema_version") != EXECUTION_SCHEMA_VERSION:
        reasons.append("route_specific_artifact_execution_missing_or_invalid_schema")
    if route_specific_artifact_execution.get("status") != EXECUTION_READY_STATUS:
        reasons.append("route_specific_artifact_execution_not_completed")
    if route_specific_artifact_execution.get("route_specific_artifact_execution_command_executed") is not True:
        reasons.append("artifact_execution_command_not_executed")
    if route_specific_artifact_execution.get("this_command_ran_route_specific_artifact_executor") is not True:
        reasons.append("artifact_execution_did_not_run_artifact_executor")
    if route_specific_artifact_execution.get("route_specific_artifact_executor_returncode") != 0:
        reasons.append("artifact_executor_returncode_not_zero")
    if route_specific_artifact_execution.get("route_specific_artifact_executor_status") != ARTIFACT_EXECUTOR_SUCCESS_STATUS:
        reasons.append("artifact_executor_status_not_executed")
    for field in [
        "verified_route_type",
        "route_specific_artifact_executor_report_path",
        "route_specific_artifact_executor_review_path",
        "route_specific_artifact_executor_status",
    ]:
        if not route_specific_artifact_execution.get(field):
            reasons.append(f"{field}_missing")
    for field in [
        "route_specific_artifact_executed",
        "route_specific_command_executed",
        "selected_route_executed",
        "export_or_acceptance_executed",
    ]:
        if route_specific_artifact_execution.get(field) is not True:
            reasons.append(f"artifact_execution_{field}_missing")
    if route_type in VALID_ROUTE_TYPES and not route_flags_match(route_specific_artifact_execution, route_type):
        reasons.append(f"artifact_execution_route_flag_mismatch:{route_type}")
    if route_specific_artifact_execution.get("formal_writeback_executed") is True:
        reasons.append("artifact_execution_formal_writeback")
    if route_specific_artifact_execution.get("this_command_wrote_formal_state") is True:
        reasons.append("artifact_execution_wrote_formal_state")
    if route_type != "manual_acceptance" and route_specific_artifact_execution.get("can_write_product_state") is True:
        reasons.append(f"artifact_execution_product_state_write_not_allowed:{route_type}")
    if route_type == "manual_acceptance" and route_specific_artifact_execution.get("can_write_product_state") is not True:
        reasons.append("artifact_execution_manual_acceptance_product_state_not_recorded")
    if route_specific_artifact_execution.get("blocking_reasons"):
        reasons.append("source_artifact_execution_has_blocking_reasons")
    for flag, value in route_specific_artifact_execution.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"artifact_execution_boundary_violation:{flag}")
    return dedupe(reasons)


def build_artifact_execution_result_contract_blocking_reasons(
    route_specific_artifact_execution: dict[str, Any],
    route_specific_artifact_executor: dict[str, Any],
) -> list[str]:
    route_type = route_specific_artifact_execution.get("verified_route_type", "unknown")
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"artifact_executor_route_type_unknown:{route_type}")
    if route_specific_artifact_executor.get("route_type") != route_type:
        reasons.append(f"artifact_executor_route_type_mismatch:{route_type}")
    if route_specific_artifact_execution.get("route_specific_artifact_executor_report_path") != str(
        DEFAULT_ARTIFACT_EXECUTOR_PATH
    ):
        reasons.append(f"artifact_executor_report_path_mismatch:{route_type}")
    if route_specific_artifact_execution.get("route_specific_artifact_executor_review_path") != str(
        DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH
    ):
        reasons.append(f"artifact_executor_review_path_mismatch:{route_type}")
    if route_specific_artifact_execution.get("route_specific_artifact_executor_returncode") != 0:
        reasons.append(f"artifact_executor_returncode_mismatch:{route_type}")
    if route_specific_artifact_execution.get("route_specific_artifact_executor_status") != route_specific_artifact_executor.get(
        "status"
    ):
        reasons.append(f"artifact_executor_status_mismatch:{route_type}")

    result = route_specific_artifact_execution.get("route_specific_artifact_executor_result", {})
    if result.get("report_path") != str(DEFAULT_ARTIFACT_EXECUTOR_PATH):
        reasons.append(f"artifact_executor_result_report_path_mismatch:{route_type}")
    if result.get("review_path") != str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH):
        reasons.append(f"artifact_executor_result_review_path_mismatch:{route_type}")
    if result.get("returncode") != route_specific_artifact_execution.get("route_specific_artifact_executor_returncode"):
        reasons.append(f"artifact_executor_result_returncode_mismatch:{route_type}")
    if result.get("status") != route_specific_artifact_executor.get("status"):
        reasons.append(f"artifact_executor_result_status_mismatch:{route_type}")

    summary = result.get("route_specific_artifact_executor_report_summary", {})
    if summary:
        if summary.get("schema_version") != route_specific_artifact_executor.get("schema_version"):
            reasons.append(f"artifact_executor_summary_schema_mismatch:{route_type}")
        if summary.get("status") != route_specific_artifact_executor.get("status"):
            reasons.append(f"artifact_executor_summary_status_mismatch:{route_type}")
        if summary.get("mode") != route_specific_artifact_executor.get("mode"):
            reasons.append(f"artifact_executor_summary_mode_mismatch:{route_type}")
        if summary.get("route_type") != route_specific_artifact_executor.get("route_type"):
            reasons.append(f"artifact_executor_summary_route_type_mismatch:{route_type}")
        if summary.get("delegated_status") != route_specific_artifact_executor.get("delegated_status"):
            reasons.append(f"artifact_executor_summary_delegated_status_mismatch:{route_type}")
    return dedupe(reasons)


def build_artifact_executor_output_blocking_reasons(
    route_specific_artifact_execution: dict[str, Any],
    route_specific_artifact_executor: dict[str, Any],
) -> list[str]:
    route_type = route_specific_artifact_execution.get("verified_route_type", "unknown")
    reasons = []
    if route_specific_artifact_executor.get("schema_version") != ARTIFACT_EXECUTOR_SCHEMA_VERSION:
        reasons.append("artifact_executor_missing_or_invalid_schema")
    if route_specific_artifact_executor.get("status") != ARTIFACT_EXECUTOR_SUCCESS_STATUS:
        reasons.append("artifact_executor_not_completed")
    if route_specific_artifact_executor.get("mode") != "execute":
        reasons.append("artifact_executor_mode_not_execute")
    if route_specific_artifact_executor.get("confirm_artifact_execution") is not True:
        reasons.append("artifact_executor_confirmation_missing")
    if route_specific_artifact_executor.get("route_specific_artifact_executed") is not True:
        reasons.append("artifact_executor_route_specific_artifact_not_executed")
    if route_specific_artifact_executor.get("route_specific_command_executed") is not True:
        reasons.append("artifact_executor_route_specific_command_not_executed")
    if route_specific_artifact_executor.get("selected_route_executed") is not True:
        reasons.append("artifact_executor_selected_route_not_executed")
    if route_specific_artifact_executor.get("export_or_acceptance_executed") is not True:
        reasons.append("artifact_executor_export_or_acceptance_not_executed")
    if route_specific_artifact_executor.get("delegated_returncode") != 0:
        reasons.append("artifact_executor_delegated_returncode_not_zero")
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"artifact_executor_route_type_unknown:{route_type}")
    else:
        if route_specific_artifact_executor.get("delegated_status") not in DELEGATED_SUCCESS_STATUSES[route_type]:
            reasons.append(f"artifact_executor_delegated_status_not_success:{route_type}")
        expected_paths = DELEGATED_PATHS[route_type]
        if route_specific_artifact_executor.get("delegated_report_path") != expected_paths["report"]:
            reasons.append(f"artifact_executor_delegated_report_path_mismatch:{route_type}")
        if route_specific_artifact_executor.get("delegated_review_path") != expected_paths["review"]:
            reasons.append(f"artifact_executor_delegated_review_path_mismatch:{route_type}")
        if not route_flags_match(route_specific_artifact_executor, route_type):
            reasons.append(f"artifact_executor_route_flag_mismatch:{route_type}")
        if route_type != "manual_acceptance" and route_specific_artifact_executor.get("can_write_product_state") is True:
            reasons.append(f"artifact_executor_product_state_write_not_allowed:{route_type}")
        if route_type == "manual_acceptance" and route_specific_artifact_executor.get("can_write_product_state") is not True:
            reasons.append("artifact_executor_manual_acceptance_product_state_not_recorded")
    if route_specific_artifact_executor.get("formal_writeback_executed") is True:
        reasons.append("artifact_executor_formal_writeback")
    if route_specific_artifact_executor.get("this_command_wrote_formal_state") is True:
        reasons.append("artifact_executor_wrote_formal_state")
    if route_specific_artifact_executor.get("blocking_reasons"):
        reasons.append("artifact_executor_has_blocking_reasons")
    for flag, value in route_specific_artifact_executor.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"artifact_executor_boundary_violation:{flag}")
    return dedupe(reasons)


def route_flags_match(payload: dict[str, Any], route_type: str) -> bool:
    expected = ROUTE_FLAGS[route_type]
    return all(payload.get(flag) is expected_value for flag, expected_value in expected.items())


def build_status(
    execution_reasons: list[str],
    contract_reasons: list[str],
    executor_reasons: list[str],
) -> str:
    if execution_reasons:
        return "blocked_by_route_specific_artifact_execution"
    if contract_reasons:
        return "blocked_by_route_specific_artifact_execution_result_contract"
    if executor_reasons:
        return "blocked_by_route_specific_artifact_executor_output"
    return "route_specific_artifact_execution_result_review_ready"


def build_route_specific_artifact_verification_input_records(
    route_specific_artifact_executor: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = route_specific_artifact_executor.get("route_type", "")
    return [
        {
            "record_id": f"artifact_execution_result::{route_type}",
            "verified_route_type": route_type,
            "artifact_executor_status": route_specific_artifact_executor.get("status", ""),
            "artifact_executor_report_path": str(DEFAULT_ARTIFACT_EXECUTOR_PATH),
            "artifact_executor_review_path": str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH),
            "delegated_report_path": route_specific_artifact_executor.get("delegated_report_path", ""),
            "delegated_review_path": route_specific_artifact_executor.get("delegated_review_path", ""),
            "delegated_status": route_specific_artifact_executor.get("delegated_status", ""),
            "review_status": "artifact_execution_accepted_for_route_specific_artifact_verification",
            "can_continue_to_route_specific_artifact_verification": True,
        }
    ]


def build_source_artifact_execution_summary(route_specific_artifact_execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_execution.get("schema_version", ""),
        "status": route_specific_artifact_execution.get("status", ""),
        "verified_route_type": route_specific_artifact_execution.get("verified_route_type", ""),
        "route_specific_artifact_execution_command_executed": (
            route_specific_artifact_execution.get("route_specific_artifact_execution_command_executed") is True
        ),
        "this_command_ran_route_specific_artifact_executor": (
            route_specific_artifact_execution.get("this_command_ran_route_specific_artifact_executor") is True
        ),
        "route_specific_artifact_executor_returncode": route_specific_artifact_execution.get(
            "route_specific_artifact_executor_returncode"
        ),
        "route_specific_artifact_executor_status": route_specific_artifact_execution.get(
            "route_specific_artifact_executor_status",
            "",
        ),
        "blocking_reasons": route_specific_artifact_execution.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_execution.get("boundary_flags", {}),
    }


def build_source_artifact_executor_summary(route_specific_artifact_executor: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_executor.get("schema_version", ""),
        "status": route_specific_artifact_executor.get("status", ""),
        "mode": route_specific_artifact_executor.get("mode", ""),
        "route_type": route_specific_artifact_executor.get("route_type", ""),
        "route_specific_artifact_executed": (
            route_specific_artifact_executor.get("route_specific_artifact_executed") is True
        ),
        "route_specific_command_executed": (
            route_specific_artifact_executor.get("route_specific_command_executed") is True
        ),
        "delegated_status": route_specific_artifact_executor.get("delegated_status", ""),
        "delegated_report_path": route_specific_artifact_executor.get("delegated_report_path", ""),
        "blocking_reasons": route_specific_artifact_executor.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_executor.get("boundary_flags", {}),
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
    if status == "route_specific_artifact_execution_result_review_ready":
        return {
            "id": "run_route_specific_artifact_verification",
            "label": "Run route-specific artifact verification",
            "description": f"The `{route_type}` route-specific artifact execution is accepted for verification.",
        }
    if status == "blocked_by_route_specific_artifact_execution_result_contract":
        return {
            "id": "repair_artifact_execution_result_contract",
            "label": "Repair artifact execution result contract",
            "description": "P7-AR and the artifact executor output must describe the same executed artifact result.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_executor_output":
        return {
            "id": "repair_route_specific_artifact_executor_output",
            "label": "Repair route-specific artifact executor output",
            "description": "The artifact executor output must be completed and clean before artifact verification.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_route_specific_artifact_execution_blockers",
        "label": "Resolve P7-AR blockers",
        "description": "P7-AR must execute one route-specific artifact before result review can continue.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_route_specific_artifact_execution_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Route-Specific Artifact Execution Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- artifact executor status：`{report['artifact_executor_status']}`",
        f"- artifact execution result 已审阅：{str(report['artifact_execution_result_reviewed']).lower()}",
        "- 可进入 route-specific artifact verification："
        f"{str(report['can_continue_to_route_specific_artifact_verification']).lower()}",
        "- route-specific artifact verification input 数："
        f"{len(report['route_specific_artifact_verification_input_records'])}",
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
    if report["route_specific_artifact_verification_input_records"]:
        lines.extend(["", "## Route-Specific Artifact Verification Inputs"])
        for record in report["route_specific_artifact_verification_input_records"]:
            lines.append(f"- `{record['record_id']}`: {record['review_status']}")
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

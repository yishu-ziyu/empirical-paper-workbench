from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_selected_route_execute_result_review.v1"
NEXT_GATE_EXECUTE_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_selected_route_execute.v1"
SELECTED_ROUTE_EXECUTE_SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execute.v1"
EXECUTE_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execute_manifest.v1"
DEFAULT_NEXT_GATE_EXECUTE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_selected_route_execute.json"
)
DEFAULT_SELECTED_ROUTE_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execute.json")
DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_selected_route_execute.md")
DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH = Path(
    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
)
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_selected_route_execute_result_review.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_next_gate_selected_route_execute_result_review.md")
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
    project_root: Path,
    next_gate_selected_route_execute: dict[str, Any],
    selected_route_execute: dict[str, Any],
    selected_route_execute_manifest: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    next_gate_reasons = build_next_gate_execute_blocking_reasons(next_gate_selected_route_execute)
    contract_reasons = (
        build_selected_route_execute_result_contract_blocking_reasons(
            next_gate_selected_route_execute,
            selected_route_execute,
        )
        if not next_gate_reasons
        else []
    )
    manifest_reasons = (
        build_selected_route_execute_manifest_blocking_reasons(
            next_gate_selected_route_execute,
            selected_route_execute,
            selected_route_execute_manifest,
        )
        if not next_gate_reasons and not contract_reasons
        else []
    )
    blocking_reasons = dedupe(next_gate_reasons + contract_reasons + manifest_reasons)
    status = build_status(next_gate_reasons, contract_reasons, manifest_reasons)
    ready = status == "next_gate_selected_route_execute_result_review_ready"
    route_type = next_gate_selected_route_execute.get("verified_route_type", "") if not next_gate_reasons else ""

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": next_gate_selected_route_execute.get(
            "topic",
            selected_route_execute.get("topic", selected_route_execute_manifest.get("topic", "")),
        ),
        "source_paths": {
            "next_gate_selected_route_execute": source_paths.get(
                "next_gate_selected_route_execute",
                str(DEFAULT_NEXT_GATE_EXECUTE_PATH),
            ),
            "selected_route_execute": source_paths.get(
                "selected_route_execute",
                str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH),
            ),
            "selected_route_execute_manifest": source_paths.get(
                "selected_route_execute_manifest",
                str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH),
            ),
        },
        "source_status": next_gate_selected_route_execute.get("status", ""),
        "status": status,
        "verified_route_type": route_type if ready else "",
        "selected_route_execute_status": selected_route_execute.get("status", "") if ready else "",
        "selected_route_execute_result_reviewed": ready,
        "can_continue_to_route_specific_artifact_executor": ready,
        "selected_route_execute_command_executed": (
            next_gate_selected_route_execute.get("selected_route_execute_command_executed") is True
        ),
        "this_command_ran_selected_route_execute_command": False,
        "selected_route_execute_manifest_recorded": (
            selected_route_execute.get("selected_route_execute_manifest_recorded") is True
        )
        if ready
        else False,
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
        "route_specific_artifact_executor_input_records": (
            build_route_specific_artifact_executor_input_records(
                next_gate_selected_route_execute,
                selected_route_execute,
                selected_route_execute_manifest,
            )
            if ready
            else []
        ),
        "blocking_reasons": blocking_reasons,
        "source_next_gate_selected_route_execute": build_source_next_gate_execute_summary(
            next_gate_selected_route_execute
        ),
        "source_selected_route_execute": build_source_selected_route_execute_summary(selected_route_execute),
        "source_selected_route_execute_manifest": build_source_selected_route_execute_manifest_summary(
            selected_route_execute_manifest
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_next_gate_execute_blocking_reasons(next_gate_selected_route_execute: dict[str, Any]) -> list[str]:
    reasons = []
    if next_gate_selected_route_execute.get("schema_version") != NEXT_GATE_EXECUTE_SCHEMA_VERSION:
        reasons.append("next_gate_selected_route_execute_missing_or_invalid_schema")
    if next_gate_selected_route_execute.get("status") != "next_gate_selected_route_execute_command_executed":
        reasons.append("next_gate_selected_route_execute_not_completed")
    if next_gate_selected_route_execute.get("selected_route_execute_command_executed") is not True:
        reasons.append("selected_route_execute_command_not_executed")
    if next_gate_selected_route_execute.get("this_command_ran_selected_route_execute_command") is not True:
        reasons.append("source_execute_did_not_run_selected_route_execute_command")
    if next_gate_selected_route_execute.get("selected_route_execute_returncode") != 0:
        reasons.append("selected_route_execute_returncode_not_zero")
    if next_gate_selected_route_execute.get("selected_route_execute_status") != "selected_route_execute_manifest_recorded":
        reasons.append("selected_route_execute_status_not_manifest_recorded")
    if next_gate_selected_route_execute.get("selected_route_execute_manifest_recorded") is not True:
        reasons.append("selected_route_execute_manifest_not_recorded")
    for field in [
        "verified_route_type",
        "routed_next_gate",
        "selected_route_execute_report_path",
        "selected_route_execute_review_path",
        "selected_route_execute_manifest_path",
    ]:
        if not next_gate_selected_route_execute.get(field):
            reasons.append(f"{field}_missing")
    if next_gate_selected_route_execute.get("selected_route_executed") is True:
        reasons.append("next_gate_selected_route_execute_selected_route")
    if next_gate_selected_route_execute.get("export_or_acceptance_executed") is True:
        reasons.append("next_gate_selected_route_execute_exported_or_accepted")
    if next_gate_selected_route_execute.get("rendered_pdf") is True:
        reasons.append("next_gate_selected_route_execute_rendered_pdf")
    if next_gate_selected_route_execute.get("rendered_docx") is True:
        reasons.append("next_gate_selected_route_execute_rendered_docx")
    if next_gate_selected_route_execute.get("package_manifest_generated") is True:
        reasons.append("next_gate_selected_route_execute_generated_package_manifest")
    if next_gate_selected_route_execute.get("manual_acceptance_performed") is True:
        reasons.append("next_gate_selected_route_execute_performed_manual_acceptance")
    if next_gate_selected_route_execute.get("formal_writeback_executed") is True:
        reasons.append("next_gate_selected_route_execute_formal_writeback")
    if next_gate_selected_route_execute.get("this_command_wrote_formal_state") is True:
        reasons.append("next_gate_selected_route_execute_wrote_formal_state")
    if next_gate_selected_route_execute.get("can_write_product_state") is True:
        reasons.append("next_gate_selected_route_execute_allows_product_state_write")
    if next_gate_selected_route_execute.get("blocking_reasons"):
        reasons.append("source_next_gate_selected_route_execute_has_blocking_reasons")
    for flag, value in next_gate_selected_route_execute.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"next_gate_selected_route_execute_boundary_violation:{flag}")
    return dedupe(reasons)


def build_selected_route_execute_result_contract_blocking_reasons(
    next_gate_selected_route_execute: dict[str, Any],
    selected_route_execute: dict[str, Any],
) -> list[str]:
    route_type = next_gate_selected_route_execute.get("verified_route_type", "unknown")
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"selected_route_type_unknown:{route_type}")
    if next_gate_selected_route_execute.get("selected_route_execute_report_path") != str(
        DEFAULT_SELECTED_ROUTE_EXECUTE_PATH
    ):
        reasons.append(f"selected_route_execute_report_path_mismatch:{route_type}")
    if next_gate_selected_route_execute.get("selected_route_execute_review_path") != str(
        DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH
    ):
        reasons.append(f"selected_route_execute_review_path_mismatch:{route_type}")
    if next_gate_selected_route_execute.get("selected_route_execute_manifest_path") != str(
        DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH
    ):
        reasons.append(f"selected_route_execute_manifest_path_mismatch:{route_type}")

    delegated_result = next_gate_selected_route_execute.get("selected_route_execute_result", {})
    if delegated_result.get("report_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH):
        reasons.append(f"selected_route_execute_result_report_path_mismatch:{route_type}")
    if delegated_result.get("review_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH):
        reasons.append(f"selected_route_execute_result_review_path_mismatch:{route_type}")
    if delegated_result.get("manifest_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH):
        reasons.append(f"selected_route_execute_result_manifest_path_mismatch:{route_type}")
    if delegated_result.get("returncode") != next_gate_selected_route_execute.get("selected_route_execute_returncode"):
        reasons.append(f"selected_route_execute_result_returncode_mismatch:{route_type}")
    if delegated_result.get("status") != selected_route_execute.get("status"):
        reasons.append(f"selected_route_execute_result_status_mismatch:{route_type}")

    if selected_route_execute.get("schema_version") != SELECTED_ROUTE_EXECUTE_SCHEMA_VERSION:
        reasons.append(f"selected_route_execute_missing_or_invalid_schema:{route_type}")
    if selected_route_execute.get("status") != "selected_route_execute_manifest_recorded":
        reasons.append(f"selected_route_execute_status_mismatch:{route_type}")
    if selected_route_execute.get("status") != next_gate_selected_route_execute.get("selected_route_execute_status"):
        reasons.append(f"selected_route_execute_status_mismatch:{route_type}")
    if selected_route_execute.get("selected_route_execute_manifest_recorded") is not True:
        reasons.append(f"selected_route_execute_manifest_not_recorded:{route_type}")
    if selected_route_execute.get("selected_route_execute_manifest_path") != str(
        DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH
    ):
        reasons.append(f"selected_route_execute_manifest_path_mismatch:{route_type}")

    summary = delegated_result.get("selected_route_execute_report_summary", {})
    if summary.get("schema_version") != selected_route_execute.get("schema_version"):
        reasons.append(f"selected_route_execute_summary_schema_mismatch:{route_type}")
    if summary.get("status") != selected_route_execute.get("status"):
        reasons.append(f"selected_route_execute_summary_status_mismatch:{route_type}")
    if summary.get("selected_route_execute_manifest_recorded") != (
        selected_route_execute.get("selected_route_execute_manifest_recorded") is True
    ):
        reasons.append(f"selected_route_execute_summary_manifest_recorded_mismatch:{route_type}")
    if summary.get("selected_route_execute_operations_count") != len(
        selected_route_execute.get("selected_route_execute_operations", []) or []
    ):
        reasons.append(f"selected_route_execute_summary_operations_count_mismatch:{route_type}")

    reasons.extend(build_selected_route_execute_boundary_reasons(selected_route_execute, route_type))
    return dedupe(reasons)


def build_selected_route_execute_boundary_reasons(
    selected_route_execute: dict[str, Any],
    route_type: str,
) -> list[str]:
    reasons = []
    for field in [
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
        if selected_route_execute.get(field) is True:
            reasons.append(f"selected_route_execute_{field}:{route_type}")
    if selected_route_execute.get("blocking_reasons"):
        reasons.append(f"selected_route_execute_has_blocking_reasons:{route_type}")
    for flag, value in selected_route_execute.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"selected_route_execute_boundary_violation:{flag}")
    return reasons


def build_selected_route_execute_manifest_blocking_reasons(
    next_gate_selected_route_execute: dict[str, Any],
    selected_route_execute: dict[str, Any],
    selected_route_execute_manifest: dict[str, Any],
) -> list[str]:
    route_type = next_gate_selected_route_execute.get("verified_route_type", "unknown")
    reasons = []
    if selected_route_execute_manifest.get("schema_version") != EXECUTE_MANIFEST_SCHEMA_VERSION:
        reasons.append("selected_route_execute_manifest_missing_or_invalid_schema")
    if selected_route_execute_manifest.get("source_execute_report") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH):
        reasons.append(f"selected_route_execute_manifest_source_report_mismatch:{route_type}")
    if selected_route_execute_manifest.get("manifest_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH):
        reasons.append(f"selected_route_execute_manifest_path_mismatch:{route_type}")
    if selected_route_execute.get("selected_route_execute_manifest_path") and selected_route_execute_manifest.get(
        "manifest_path"
    ) != selected_route_execute.get("selected_route_execute_manifest_path"):
        reasons.append(f"selected_route_execute_manifest_report_path_mismatch:{route_type}")

    for field in [
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
        if selected_route_execute_manifest.get(field) is True:
            reasons.append(f"selected_route_execute_manifest_{field}:{route_type}")
    for flag, value in selected_route_execute_manifest.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"selected_route_execute_manifest_boundary_violation:{flag}")

    reasons.extend(build_route_operation_contract_blocking_reasons(selected_route_execute_manifest))
    return dedupe(reasons)


def build_route_operation_contract_blocking_reasons(
    selected_route_execute_manifest: dict[str, Any],
) -> list[str]:
    operations = selected_route_execute_manifest.get("selected_route_execute_operations", [])
    if not isinstance(operations, list) or len(operations) != 1:
        return ["selected_route_execute_operations_not_single"]
    operation = operations[0]
    route_type = operation.get("route_type", "unknown")
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"route_type_unknown:{route_type}")
    for field in ["operation_id", "route_execution_id", "routed_action", "next_command", "planned_outputs"]:
        if not operation.get(field):
            reasons.append(f"route_{field}_missing:{route_type}")
    if operation.get("operation_status") != "planned_not_executed":
        reasons.append(f"route_operation_not_planned:{route_type}")
    for field in [
        "will_execute_selected_route",
        "will_render_pdf",
        "will_render_docx",
        "will_generate_package_manifest",
        "will_perform_manual_acceptance",
        "will_write_product_state",
    ]:
        if operation.get(field) is True:
            reasons.append(f"route_operation_marked_{field.removeprefix('will_')}:{route_type}")
    return dedupe(reasons)


def build_status(
    next_gate_reasons: list[str],
    contract_reasons: list[str],
    manifest_reasons: list[str],
) -> str:
    if next_gate_reasons:
        return "blocked_by_next_gate_selected_route_execute"
    if contract_reasons:
        return "blocked_by_next_gate_selected_route_execute_result_contract"
    if manifest_reasons:
        return "blocked_by_selected_route_execute_manifest_review"
    return "next_gate_selected_route_execute_result_review_ready"


def build_route_specific_artifact_executor_input_records(
    next_gate_selected_route_execute: dict[str, Any],
    selected_route_execute: dict[str, Any],
    selected_route_execute_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    operation = selected_route_execute_manifest["selected_route_execute_operations"][0]
    route_type = operation.get("route_type", "")
    return [
        {
            "record_id": f"selected_route_execute_result::{route_type}",
            "verified_route_type": next_gate_selected_route_execute.get("verified_route_type", ""),
            "selected_route_execute_status": selected_route_execute.get("status", ""),
            "selected_route_execute_report_path": str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH),
            "selected_route_execute_manifest_path": str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH),
            "operation_id": operation.get("operation_id", ""),
            "route_execution_id": operation.get("route_execution_id", ""),
            "routed_action": operation.get("routed_action", ""),
            "next_command": operation.get("next_command", ""),
            "planned_outputs": operation.get("planned_outputs", []),
            "review_status": "selected_route_execute_manifest_accepted_for_route_specific_artifact_executor",
            "can_continue_to_route_specific_artifact_executor": True,
        }
    ]


def build_source_next_gate_execute_summary(next_gate_selected_route_execute: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": next_gate_selected_route_execute.get("schema_version", ""),
        "status": next_gate_selected_route_execute.get("status", ""),
        "verified_route_type": next_gate_selected_route_execute.get("verified_route_type", ""),
        "selected_route_execute_command_executed": (
            next_gate_selected_route_execute.get("selected_route_execute_command_executed") is True
        ),
        "selected_route_execute_status": next_gate_selected_route_execute.get("selected_route_execute_status", ""),
        "selected_route_execute_manifest_recorded": (
            next_gate_selected_route_execute.get("selected_route_execute_manifest_recorded") is True
        ),
        "source_blocking_reasons": next_gate_selected_route_execute.get("blocking_reasons", []),
        "boundary_flags": next_gate_selected_route_execute.get("boundary_flags", {}),
    }


def build_source_selected_route_execute_summary(selected_route_execute: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execute.get("schema_version", ""),
        "status": selected_route_execute.get("status", ""),
        "selected_route_execute_manifest_recorded": (
            selected_route_execute.get("selected_route_execute_manifest_recorded") is True
        ),
        "selected_route_execute_operations_count": len(
            selected_route_execute.get("selected_route_execute_operations", []) or []
        ),
        "blocking_reasons": selected_route_execute.get("blocking_reasons", []),
        "boundary_flags": selected_route_execute.get("boundary_flags", {}),
    }


def build_source_selected_route_execute_manifest_summary(
    selected_route_execute_manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execute_manifest.get("schema_version", ""),
        "source_execute_report": selected_route_execute_manifest.get("source_execute_report", ""),
        "manifest_path": selected_route_execute_manifest.get("manifest_path", ""),
        "selected_route_execute_operations_count": len(
            selected_route_execute_manifest.get("selected_route_execute_operations", []) or []
        ),
        "boundary_flags": selected_route_execute_manifest.get("boundary_flags", {}),
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
    if status == "next_gate_selected_route_execute_result_review_ready":
        return {
            "id": "run_route_specific_artifact_executor_dry_run",
            "label": "Run route-specific artifact executor dry-run",
            "description": f"The `{route_type}` selected route execute manifest is accepted for artifact execution.",
        }
    if status == "blocked_by_next_gate_selected_route_execute_result_contract":
        return {
            "id": "repair_selected_route_execute_result_contract",
            "label": "Repair selected route execute result contract",
            "description": "P7-AN and selected route execute report must describe the same completed manifest event.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_selected_route_execute_manifest_review":
        return {
            "id": "repair_selected_route_execute_manifest",
            "label": "Repair selected route execute manifest",
            "description": "The selected route execute manifest must be clean before artifact execution.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_next_gate_selected_route_execute_blockers",
        "label": "Resolve P7-AN blockers",
        "description": "P7-AN must execute selected route manifest recording before P7-AO can continue.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_selected_route_execute_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Selected Route Execute Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- selected route execute status：`{report['selected_route_execute_status']}`",
        "- selected route execute result 已审阅："
        f"{str(report['selected_route_execute_result_reviewed']).lower()}",
        "- 可进入 route-specific artifact executor："
        f"{str(report['can_continue_to_route_specific_artifact_executor']).lower()}",
        "- selected route execute command 已执行："
        f"{str(report['selected_route_execute_command_executed']).lower()}",
        "- 本命令运行 selected route execute command："
        f"{str(report['this_command_ran_selected_route_execute_command']).lower()}",
        "- selected route execute manifest 已记录："
        f"{str(report['selected_route_execute_manifest_recorded']).lower()}",
        "- route-specific artifact executor input 数："
        f"{len(report['route_specific_artifact_executor_input_records'])}",
        f"- 已运行 artifact executor：{str(report['route_specific_artifact_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 已渲染 PDF：{str(report['rendered_pdf']).lower()}",
        f"- 已渲染 DOCX：{str(report['rendered_docx']).lower()}",
        f"- 已生成 package manifest：{str(report['package_manifest_generated']).lower()}",
        f"- 已执行人工验收：{str(report['manual_acceptance_performed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["route_specific_artifact_executor_input_records"]:
        lines.extend(["", "## Route-Specific Artifact Executor Inputs"])
        for record in report["route_specific_artifact_executor_input_records"]:
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

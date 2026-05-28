from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.v1"
ENTRY_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.v1"
ARTIFACT_EXECUTOR_SCHEMA_VERSION = "p7.auto_mode_formal_package_route_specific_artifact_executor.v1"
ENTRY_READY_STATUS = "next_gate_route_specific_artifact_executor_entered"
ARTIFACT_EXECUTOR_DRY_RUN_STATUS = "route_specific_artifact_executor_dry_run_ready"
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
)
DEFAULT_ARTIFACT_EXECUTOR_PATH = Path("Results/json/auto_mode_formal_package_route_specific_artifact_executor.json")
DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_route_specific_artifact_executor.md")
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review.md"
)
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}
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


def build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
    project_root: Path,
    route_specific_artifact_executor_entry: dict[str, Any],
    route_specific_artifact_executor: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    entry_reasons = build_entry_blocking_reasons(route_specific_artifact_executor_entry)
    executor_has_valid_schema = (
        route_specific_artifact_executor.get("schema_version") == ARTIFACT_EXECUTOR_SCHEMA_VERSION
    )
    contract_reasons = (
        build_entry_result_contract_blocking_reasons(
            route_specific_artifact_executor_entry,
            route_specific_artifact_executor,
        )
        if not entry_reasons and executor_has_valid_schema
        else []
    )
    dry_run_reasons = (
        build_artifact_executor_dry_run_blocking_reasons(
            route_specific_artifact_executor_entry,
            route_specific_artifact_executor,
        )
        if not entry_reasons and not contract_reasons
        else []
    )
    status = build_status(entry_reasons, contract_reasons, dry_run_reasons)
    ready = status == "route_specific_artifact_executor_entry_result_review_ready"
    route_type = route_specific_artifact_executor_entry.get("verified_route_type", "") if ready else ""
    blocking_reasons = dedupe(entry_reasons + contract_reasons + dry_run_reasons)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": route_specific_artifact_executor_entry.get(
            "topic",
            route_specific_artifact_executor.get("topic", ""),
        ),
        "source_paths": {
            "route_specific_artifact_executor_entry": source_paths.get(
                "route_specific_artifact_executor_entry",
                str(DEFAULT_ENTRY_PATH),
            ),
            "route_specific_artifact_executor": source_paths.get(
                "route_specific_artifact_executor",
                str(DEFAULT_ARTIFACT_EXECUTOR_PATH),
            ),
        },
        "source_status": route_specific_artifact_executor_entry.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "route_specific_artifact_executor_status": (
            route_specific_artifact_executor.get("status", "") if ready else ""
        ),
        "artifact_executor_entry_result_reviewed": ready,
        "can_continue_to_route_specific_artifact_execution": ready,
        "route_specific_artifact_execution_records": (
            build_route_specific_artifact_execution_records(route_specific_artifact_executor)
            if ready
            else []
        ),
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
        "source_artifact_executor_entry": build_source_entry_summary(route_specific_artifact_executor_entry),
        "source_artifact_executor": build_source_artifact_executor_summary(route_specific_artifact_executor),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_entry_blocking_reasons(route_specific_artifact_executor_entry: dict[str, Any]) -> list[str]:
    reasons = []
    if route_specific_artifact_executor_entry.get("schema_version") != ENTRY_SCHEMA_VERSION:
        reasons.append("route_specific_artifact_executor_entry_missing_or_invalid_schema")
    if route_specific_artifact_executor_entry.get("status") != ENTRY_READY_STATUS:
        reasons.append("route_specific_artifact_executor_entry_not_completed")
    if route_specific_artifact_executor_entry.get("route_specific_artifact_executor_entry_command_executed") is not True:
        reasons.append("artifact_executor_entry_command_not_executed")
    if route_specific_artifact_executor_entry.get("this_command_ran_route_specific_artifact_executor") is not True:
        reasons.append("entry_did_not_run_artifact_executor")
    if route_specific_artifact_executor_entry.get("route_specific_artifact_executor_entered") is not True:
        reasons.append("artifact_executor_not_entered")
    if route_specific_artifact_executor_entry.get("route_specific_artifact_executor_returncode") != 0:
        reasons.append("artifact_executor_entry_returncode_not_zero")
    if (
        route_specific_artifact_executor_entry.get("route_specific_artifact_executor_status")
        != ARTIFACT_EXECUTOR_DRY_RUN_STATUS
    ):
        reasons.append("artifact_executor_entry_status_not_dry_run_ready")
    for field in [
        "verified_route_type",
        "route_specific_artifact_executor_report_path",
        "route_specific_artifact_executor_review_path",
        "route_specific_artifact_executor_status",
    ]:
        if not route_specific_artifact_executor_entry.get(field):
            reasons.append(f"{field}_missing")
    for field in EXECUTION_BOUNDARY_FIELDS:
        if route_specific_artifact_executor_entry.get(field) is True:
            reasons.append(f"entry_{field}")
    if route_specific_artifact_executor_entry.get("blocking_reasons"):
        reasons.append("source_entry_has_blocking_reasons")
    for flag, value in route_specific_artifact_executor_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"entry_boundary_violation:{flag}")
    return dedupe(reasons)


def build_entry_result_contract_blocking_reasons(
    route_specific_artifact_executor_entry: dict[str, Any],
    route_specific_artifact_executor: dict[str, Any],
) -> list[str]:
    route_type = route_specific_artifact_executor_entry.get("verified_route_type", "unknown")
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"artifact_executor_route_type_unknown:{route_type}")
    if route_type != route_specific_artifact_executor.get("route_type", ""):
        reasons.append(f"artifact_executor_route_type_mismatch:{route_type}")
    if route_specific_artifact_executor_entry.get("route_specific_artifact_executor_report_path") != str(
        DEFAULT_ARTIFACT_EXECUTOR_PATH
    ):
        reasons.append(f"artifact_executor_report_path_mismatch:{route_type}")
    if route_specific_artifact_executor_entry.get("route_specific_artifact_executor_review_path") != str(
        DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH
    ):
        reasons.append(f"artifact_executor_review_path_mismatch:{route_type}")

    result = route_specific_artifact_executor_entry.get("route_specific_artifact_executor_result", {})
    if result.get("report_path") != str(DEFAULT_ARTIFACT_EXECUTOR_PATH):
        reasons.append(f"artifact_executor_result_report_path_mismatch:{route_type}")
    if result.get("review_path") != str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH):
        reasons.append(f"artifact_executor_result_review_path_mismatch:{route_type}")
    if result.get("returncode") != route_specific_artifact_executor_entry.get(
        "route_specific_artifact_executor_returncode"
    ):
        reasons.append(f"artifact_executor_result_returncode_mismatch:{route_type}")
    if result.get("status") != route_specific_artifact_executor.get("status"):
        reasons.append(f"artifact_executor_result_status_mismatch:{route_type}")
    if route_specific_artifact_executor.get("status") != route_specific_artifact_executor_entry.get(
        "route_specific_artifact_executor_status"
    ):
        reasons.append(f"artifact_executor_status_mismatch:{route_type}")
    if route_specific_artifact_executor.get("status") != ARTIFACT_EXECUTOR_DRY_RUN_STATUS:
        reasons.append(f"artifact_executor_status_mismatch:{route_type}")

    summary = result.get("route_specific_artifact_executor_report_summary", {})
    if summary.get("schema_version") != route_specific_artifact_executor.get("schema_version"):
        reasons.append(f"artifact_executor_summary_schema_mismatch:{route_type}")
    if summary.get("status") != route_specific_artifact_executor.get("status"):
        reasons.append(f"artifact_executor_summary_status_mismatch:{route_type}")
    if summary.get("route_type") != route_specific_artifact_executor.get("route_type"):
        reasons.append(f"artifact_executor_summary_route_type_mismatch:{route_type}")
    return dedupe(reasons)


def build_artifact_executor_dry_run_blocking_reasons(
    route_specific_artifact_executor_entry: dict[str, Any],
    route_specific_artifact_executor: dict[str, Any],
) -> list[str]:
    reasons = []
    route_type = route_specific_artifact_executor_entry.get("verified_route_type", "unknown")
    if route_specific_artifact_executor.get("schema_version") != ARTIFACT_EXECUTOR_SCHEMA_VERSION:
        reasons.append("artifact_executor_missing_or_invalid_schema")
    if route_specific_artifact_executor.get("status") != ARTIFACT_EXECUTOR_DRY_RUN_STATUS:
        reasons.append("artifact_executor_dry_run_not_ready")
    if route_specific_artifact_executor.get("mode") != "dry-run":
        reasons.append("artifact_executor_mode_not_dry_run")
    if route_specific_artifact_executor.get("can_execute_route_specific_artifact_with_confirmation") is not True:
        reasons.append("artifact_executor_cannot_execute_with_confirmation")
    if route_specific_artifact_executor.get("route_type") != route_type:
        reasons.append(f"artifact_executor_route_type_mismatch:{route_type}")
    if not route_specific_artifact_executor.get("route_specific_command"):
        reasons.append(f"artifact_executor_route_specific_command_missing:{route_type}")
    for field in EXECUTION_BOUNDARY_FIELDS:
        if route_specific_artifact_executor.get(field) is True:
            reasons.append(f"artifact_executor_{field}")
    if route_specific_artifact_executor.get("blocking_reasons"):
        reasons.append("artifact_executor_has_blocking_reasons")
    for flag, value in route_specific_artifact_executor.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"artifact_executor_boundary_violation:{flag}")
    return dedupe(reasons)


def build_status(
    entry_reasons: list[str],
    contract_reasons: list[str],
    dry_run_reasons: list[str],
) -> str:
    if entry_reasons:
        return "blocked_by_route_specific_artifact_executor_entry"
    if contract_reasons:
        return "blocked_by_route_specific_artifact_executor_entry_result_contract"
    if dry_run_reasons:
        return "blocked_by_route_specific_artifact_executor_dry_run_report"
    return "route_specific_artifact_executor_entry_result_review_ready"


def build_route_specific_artifact_execution_records(
    route_specific_artifact_executor: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = route_specific_artifact_executor.get("route_type", "")
    return [
        {
            "record_id": f"artifact_executor_dry_run::{route_type}",
            "route_type": route_type,
            "artifact_executor_report_path": str(DEFAULT_ARTIFACT_EXECUTOR_PATH),
            "artifact_executor_review_path": str(DEFAULT_ARTIFACT_EXECUTOR_REVIEW_PATH),
            "route_specific_command": route_specific_artifact_executor.get("route_specific_command", []),
            "delegated_report_path": route_specific_artifact_executor.get("delegated_report_path", ""),
            "delegated_review_path": route_specific_artifact_executor.get("delegated_review_path", ""),
            "review_status": "artifact_executor_dry_run_accepted_for_explicit_artifact_execution",
            "can_continue_to_route_specific_artifact_execution": True,
        }
    ]


def build_source_entry_summary(route_specific_artifact_executor_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_executor_entry.get("schema_version", ""),
        "status": route_specific_artifact_executor_entry.get("status", ""),
        "verified_route_type": route_specific_artifact_executor_entry.get("verified_route_type", ""),
        "route_specific_artifact_executor_entered": (
            route_specific_artifact_executor_entry.get("route_specific_artifact_executor_entered") is True
        ),
        "route_specific_artifact_executor_status": route_specific_artifact_executor_entry.get(
            "route_specific_artifact_executor_status",
            "",
        ),
        "route_specific_artifact_executor_returncode": route_specific_artifact_executor_entry.get(
            "route_specific_artifact_executor_returncode"
        ),
        "blocking_reasons": route_specific_artifact_executor_entry.get("blocking_reasons", []),
        "boundary_flags": route_specific_artifact_executor_entry.get("boundary_flags", {}),
    }


def build_source_artifact_executor_summary(route_specific_artifact_executor: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_specific_artifact_executor.get("schema_version", ""),
        "status": route_specific_artifact_executor.get("status", ""),
        "mode": route_specific_artifact_executor.get("mode", ""),
        "route_type": route_specific_artifact_executor.get("route_type", ""),
        "route_specific_command_count": len(route_specific_artifact_executor.get("route_specific_command", [])),
        "route_specific_command_executed": (
            route_specific_artifact_executor.get("route_specific_command_executed") is True
        ),
        "route_specific_artifact_executed": (
            route_specific_artifact_executor.get("route_specific_artifact_executed") is True
        ),
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
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "route_specific_artifact_executor_entry_result_review_ready":
        return {
            "id": "enter_explicit_route_specific_artifact_execution_gate",
            "label": "Enter explicit route-specific artifact execution gate",
            "description": f"The `{route_type}` artifact executor dry-run is accepted for explicit execution.",
        }
    if status == "blocked_by_route_specific_artifact_executor_entry_result_contract":
        return {
            "id": "repair_artifact_executor_entry_result_contract",
            "label": "Repair artifact executor entry result contract",
            "description": "P7-AP entry and the artifact executor dry-run report must describe the same result.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_route_specific_artifact_executor_dry_run_report":
        return {
            "id": "repair_artifact_executor_dry_run_report",
            "label": "Repair artifact executor dry-run report",
            "description": "The artifact executor dry-run report must be clean before explicit artifact execution.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_route_specific_artifact_executor_entry_blockers",
        "label": "Resolve P7-AP blockers",
        "description": "P7-AP must enter the route-specific artifact executor dry-run before this result review can continue.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Route-Specific Artifact Executor Entry Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- artifact executor status：`{report['route_specific_artifact_executor_status']}`",
        "- artifact executor entry result 已审阅："
        f"{str(report['artifact_executor_entry_result_reviewed']).lower()}",
        "- 可进入显式 route-specific artifact execution："
        f"{str(report['can_continue_to_route_specific_artifact_execution']).lower()}",
        "- route-specific artifact execution record 数："
        f"{len(report['route_specific_artifact_execution_records'])}",
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
    if report["route_specific_artifact_execution_records"]:
        lines.extend(["", "## Route-Specific Artifact Execution Records"])
        for record in report["route_specific_artifact_execution_records"]:
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

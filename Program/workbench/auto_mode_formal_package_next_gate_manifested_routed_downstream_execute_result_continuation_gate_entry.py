from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry.v1"
)
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.v1"
)
EXPORT_READY_STATUS = "manifested_routed_next_gate_downstream_execute_result_review_ready"
MANUAL_READY_STATUS = "manifested_routed_next_gate_product_review_preparation_result_review_ready"
READY_STATUS = "ready_for_manifested_routed_downstream_execute_result_continuation_gate_entry"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.json"
)
DEFAULT_GATE_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry.md"
)

EXPORT_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest"}
ARTIFACT_ENTRY_REPORT_PATH = "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
ARTIFACT_ENTRY_REVIEW_PATH = "Reviews/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.md"
ARTIFACT_ENTRY_COMMAND_PATH = "Program/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.py"
PRODUCT_REVIEW_PACKET_REPORT_PATH = "Results/json/auto_mode_formal_package_product_review_packet.json"
PRODUCT_REVIEW_PACKET_REVIEW_PATH = "Reviews/auto_mode_formal_package_product_review_packet.md"


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry(
    downstream_execute_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    source_reasons = build_source_blocking_reasons(downstream_execute_result_review)
    boundary_reasons = (
        build_boundary_blocking_reasons(downstream_execute_result_review) if not source_reasons else []
    )
    contract_reasons = (
        build_continuation_contract_blocking_reasons(downstream_execute_result_review)
        if not source_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(source_reasons + boundary_reasons + contract_reasons)
    status = build_status(source_reasons, boundary_reasons, contract_reasons)
    ready = status == READY_STATUS
    route_type = downstream_execute_result_review.get("verified_route_type", "") if ready else ""
    continuation_kind = build_continuation_kind(downstream_execute_result_review) if ready else ""
    records = build_continuation_input_records(downstream_execute_result_review) if ready else []

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": downstream_execute_result_review.get("topic", ""),
        "source_paths": {
            "manifested_routed_downstream_execute_result_review": source_paths.get(
                "manifested_routed_downstream_execute_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": downstream_execute_result_review.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": downstream_execute_result_review.get("routed_next_gate", "") if ready else "",
        "downstream_kind": downstream_execute_result_review.get("downstream_kind", "") if ready else "",
        "continuation_kind": continuation_kind,
        "downstream_execute_result_continuation_gate_entry_recorded": ready,
        "can_request_downstream_execute_result_continuation": ready,
        "requires_explicit_continuation_command": any(
            record["requires_explicit_continuation_command"] for record in records
        ),
        "continuation_input_records": records,
        "continuation_command_executed": False,
        "this_command_ran_continuation_command": False,
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
        "source_result_review": build_source_result_review_summary(downstream_execute_result_review),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, records, blocking_reasons),
    }


def build_source_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    reasons = []
    if result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("manifested_routed_next_gate_downstream_execute_result_review_missing_or_invalid_schema")
    if result_review.get("status") not in {EXPORT_READY_STATUS, MANUAL_READY_STATUS}:
        reasons.append("manifested_routed_next_gate_downstream_execute_result_review_not_ready")
    if result_review.get("downstream_execute_result_reviewed") is not True:
        reasons.append("manifested_routed_next_gate_downstream_execute_result_not_reviewed")
    if result_review.get("can_continue_after_downstream_execute") is not True:
        reasons.append("manifested_routed_next_gate_downstream_execute_result_review_cannot_continue")
    if not result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if not result_review.get("downstream_kind"):
        reasons.append("downstream_kind_missing")
    if result_review.get("blocking_reasons"):
        reasons.append("source_downstream_execute_result_review_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    reasons = []
    if result_review.get("this_command_ran_downstream_command") is True:
        reasons.append("downstream_execute_result_review_ran_downstream_command")
    if result_review.get("route_specific_artifact_executed") is True:
        reasons.append("downstream_execute_result_review_executed_route_specific_artifact")
    if result_review.get("selected_route_executed") is True:
        reasons.append("downstream_execute_result_review_selected_route_executed")
    if result_review.get("export_or_acceptance_executed") is True:
        reasons.append("downstream_execute_result_review_executed_export_or_acceptance")
    if result_review.get("rendered_pdf") is True:
        reasons.append("downstream_execute_result_review_rendered_pdf")
    if result_review.get("rendered_docx") is True:
        reasons.append("downstream_execute_result_review_rendered_docx")
    if result_review.get("package_manifest_generated") is True:
        reasons.append("downstream_execute_result_review_generated_package_manifest")
    if result_review.get("manual_acceptance_performed") is True:
        reasons.append("downstream_execute_result_review_performed_manual_acceptance")
    if result_review.get("formal_writeback_executed") is True:
        reasons.append("downstream_execute_result_review_formal_writeback")
    if result_review.get("this_command_wrote_formal_state") is True:
        reasons.append("downstream_execute_result_review_wrote_formal_state")
    if result_review.get("can_write_product_state") is True:
        reasons.append("downstream_execute_result_review_allows_product_state_write")
    for flag, value in result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"downstream_execute_result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_continuation_contract_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    if result_review.get("status") == EXPORT_READY_STATUS:
        return build_export_continuation_contract_blocking_reasons(result_review)
    if result_review.get("status") == MANUAL_READY_STATUS:
        return build_manual_continuation_contract_blocking_reasons(result_review)
    return ["downstream_execute_result_review_ready_status_unknown"]


def build_export_continuation_contract_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    route_type = result_review.get("verified_route_type", "")
    records = result_review.get("route_specific_artifact_executor_input_records", []) or []
    other_records = result_review.get("product_review_preparation_result_records", []) or []
    reasons = []
    if route_type not in EXPORT_ROUTE_TYPES:
        reasons.append(f"route_specific_artifact_executor_route_type_not_allowed:{route_type}")
    if result_review.get("downstream_kind") != "selected_route_execution":
        reasons.append(f"route_specific_artifact_executor_downstream_kind_mismatch:{route_type}")
    if other_records:
        reasons.append("unexpected_continuation_record_set:product_review_preparation_result_records")
    if not records:
        reasons.append("route_specific_artifact_executor_input_record_missing")
        return dedupe(reasons)
    if len(records) != 1:
        reasons.append("route_specific_artifact_executor_input_record_not_single")
        return dedupe(reasons)

    record = records[0]
    if record.get("verified_route_type") != route_type:
        reasons.append(f"continuation_record_route_type_mismatch:{route_type}")
    if record.get("downstream_kind") != "selected_route_execution":
        reasons.append(f"route_specific_artifact_executor_input_downstream_kind_mismatch:{route_type}")
    if record.get("review_status") != "selected_route_execute_manifest_accepted_for_route_specific_artifact_executor":
        reasons.append(f"route_specific_artifact_executor_input_record_not_accepted:{route_type}")
    if record.get("can_continue_to_route_specific_artifact_executor") is not True:
        reasons.append(f"route_specific_artifact_executor_input_record_cannot_continue:{route_type}")
    if record.get("selected_route_execute_report_path") != "Results/json/auto_mode_formal_package_selected_route_execute.json":
        reasons.append(f"selected_route_execute_report_path_mismatch:{route_type}")
    if record.get("selected_route_execute_manifest_path") != (
        "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
    ):
        reasons.append(f"selected_route_execute_manifest_path_mismatch:{route_type}")
    for field in ["operation_id", "route_execution_id", "routed_action", "next_command", "planned_outputs"]:
        if not record.get(field):
            reasons.append(f"route_specific_artifact_executor_input_{field}_missing:{route_type}")
    return dedupe(reasons)


def build_manual_continuation_contract_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    route_type = result_review.get("verified_route_type", "")
    records = result_review.get("product_review_preparation_result_records", []) or []
    other_records = result_review.get("route_specific_artifact_executor_input_records", []) or []
    reasons = []
    if route_type != "manual_acceptance":
        reasons.append(f"product_review_preparation_route_type_not_allowed:{route_type}")
    if result_review.get("downstream_kind") != "product_review_preparation":
        reasons.append(f"product_review_preparation_downstream_kind_mismatch:{route_type}")
    if other_records:
        reasons.append("unexpected_continuation_record_set:route_specific_artifact_executor_input_records")
    if not records:
        reasons.append("product_review_preparation_result_record_missing")
        return dedupe(reasons)
    if len(records) != 1:
        reasons.append("product_review_preparation_result_record_not_single")
        return dedupe(reasons)

    record = records[0]
    if record.get("verified_route_type") != "manual_acceptance":
        reasons.append(f"product_review_preparation_result_record_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != "formal_package_delivery_completion_gate":
        reasons.append("product_review_preparation_result_record_gate_mismatch")
    if record.get("downstream_kind") != "product_review_preparation":
        reasons.append("product_review_preparation_result_record_kind_mismatch")
    if record.get("review_status") != "product_review_preparation_accepted_for_product_review_packet":
        reasons.append(f"product_review_preparation_result_record_not_accepted:{route_type}")
    if record.get("can_continue_to_product_review_packet") is not True:
        reasons.append(f"product_review_preparation_result_record_cannot_continue:{route_type}")
    if record.get("terminal_status") != "terminal_delivery_completion_ready_for_product_review":
        reasons.append(f"product_review_preparation_terminal_status_mismatch:{route_type}")
    return dedupe(reasons)


def build_status(
    source_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if source_reasons:
        return "blocked_by_manifested_routed_next_gate_downstream_execute_result_review"
    if boundary_reasons:
        return "blocked_by_manifested_routed_downstream_execute_result_continuation_boundary"
    if contract_reasons:
        return "blocked_by_manifested_routed_downstream_execute_result_continuation_contract"
    return READY_STATUS


def build_continuation_kind(result_review: dict[str, Any]) -> str:
    if result_review.get("status") == EXPORT_READY_STATUS:
        return "route_specific_artifact_executor_continuation"
    return "product_review_packet_continuation"


def build_continuation_input_records(result_review: dict[str, Any]) -> list[dict[str, Any]]:
    if result_review.get("status") == EXPORT_READY_STATUS:
        record = result_review["route_specific_artifact_executor_input_records"][0]
        route_type = result_review.get("verified_route_type", "")
        return [
            {
                "record_id": (
                    "manifested_routed_downstream_execute_result_continuation::"
                    f"route_specific_artifact_executor::{route_type}"
                ),
                "verified_route_type": route_type,
                "routed_next_gate": result_review.get("routed_next_gate", ""),
                "downstream_kind": result_review.get("downstream_kind", ""),
                "continuation_kind": "route_specific_artifact_executor_continuation",
                "next_command": "auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry",
                "command_path": ARTIFACT_ENTRY_COMMAND_PATH,
                "next_report_path": ARTIFACT_ENTRY_REPORT_PATH,
                "next_review_path": ARTIFACT_ENTRY_REVIEW_PATH,
                "selected_route_execute_report_path": record.get("selected_route_execute_report_path", ""),
                "selected_route_execute_review_path": record.get("selected_route_execute_review_path", ""),
                "selected_route_execute_manifest_path": record.get("selected_route_execute_manifest_path", ""),
                "operation_id": record.get("operation_id", ""),
                "route_execution_id": record.get("route_execution_id", ""),
                "routed_action": record.get("routed_action", ""),
                "route_specific_next_command": record.get("next_command", ""),
                "planned_outputs": record.get("planned_outputs", []),
                "review_status": "route_specific_artifact_executor_input_accepted_for_continuation",
                "requires_explicit_continuation_command": True,
                "can_continue_to_route_specific_artifact_executor_entry": True,
            }
        ]

    record = result_review["product_review_preparation_result_records"][0]
    return [
        {
            "record_id": (
                "manifested_routed_downstream_execute_result_continuation::"
                "product_review_packet::manual_acceptance"
            ),
            "verified_route_type": "manual_acceptance",
            "routed_next_gate": result_review.get("routed_next_gate", ""),
            "downstream_kind": result_review.get("downstream_kind", ""),
            "continuation_kind": "product_review_packet_continuation",
            "next_command": "product_review_packet",
            "command_path": "",
            "next_report_path": PRODUCT_REVIEW_PACKET_REPORT_PATH,
            "next_review_path": PRODUCT_REVIEW_PACKET_REVIEW_PATH,
            "source_product_review_preparation_report_path": record.get("next_report_path", ""),
            "source_product_review_preparation_review_path": record.get("next_review_path", ""),
            "terminal_status": record.get("terminal_status", ""),
            "terminal_completion": record.get("terminal_completion") is True,
            "review_status": "product_review_preparation_result_accepted_for_product_review_packet_continuation",
            "requires_explicit_continuation_command": False,
            "can_continue_to_product_review_packet": True,
        }
    ]


def build_source_result_review_summary(result_review: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": result_review.get("schema_version", ""),
        "status": result_review.get("status", ""),
        "verified_route_type": result_review.get("verified_route_type", ""),
        "routed_next_gate": result_review.get("routed_next_gate", ""),
        "downstream_kind": result_review.get("downstream_kind", ""),
        "downstream_execute_result_reviewed": result_review.get("downstream_execute_result_reviewed") is True,
        "can_continue_after_downstream_execute": (
            result_review.get("can_continue_after_downstream_execute") is True
        ),
        "route_specific_artifact_executor_input_records_count": len(
            result_review.get("route_specific_artifact_executor_input_records", []) or []
        ),
        "product_review_preparation_result_records_count": len(
            result_review.get("product_review_preparation_result_records", []) or []
        ),
        "blocking_reasons": result_review.get("blocking_reasons", []),
        "boundary_flags": result_review.get("boundary_flags", {}),
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


def build_next_action(
    status: str,
    records: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == READY_STATUS and records and records[0]["continuation_kind"] == "route_specific_artifact_executor_continuation":
        return {
            "id": "continue_to_route_specific_artifact_executor_entry",
            "label": "Continue to route-specific artifact executor entry",
            "description": "P7-BL has recorded the artifact executor continuation input for an explicit next node.",
        }
    if status == READY_STATUS:
        return {
            "id": "continue_to_product_review_packet",
            "label": "Continue to product-review packet",
            "description": "P7-BL has recorded the product-review packet continuation input.",
        }
    if status == "blocked_by_manifested_routed_downstream_execute_result_continuation_contract":
        return {
            "id": "repair_downstream_execute_result_continuation_record",
            "label": "Repair downstream execute result continuation record",
            "description": "P7-BK must expose one accepted continuation record for its branch.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_downstream_execute_result_continuation_boundary":
        return {
            "id": "repair_downstream_execute_result_continuation_boundary",
            "label": "Repair downstream execute result continuation boundary",
            "description": "P7-BK must remain a result-review node without formal execution side effects.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_downstream_execute_result_review_blockers",
        "label": "Resolve P7-BK result-review blockers",
        "description": "P7-BK must be ready before P7-BL can record a continuation entry.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_GATE_ENTRY_PATH,
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
        "# Auto Mode Formal Package Manifested Routed Downstream Execute Result Continuation Gate Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- downstream kind：`{report['downstream_kind']}`",
        f"- continuation kind：`{report['continuation_kind']}`",
        "- downstream execute result continuation gate entry 已记录："
        f"{str(report['downstream_execute_result_continuation_gate_entry_recorded']).lower()}",
        "- 可请求 downstream execute result continuation："
        f"{str(report['can_request_downstream_execute_result_continuation']).lower()}",
        "- 需要显式 continuation command："
        f"{str(report['requires_explicit_continuation_command']).lower()}",
        f"- continuation input 数：{len(report['continuation_input_records'])}",
        f"- 已运行 continuation command：{str(report['this_command_ran_continuation_command']).lower()}",
        f"- 已运行 artifact executor：{str(report['route_specific_artifact_executed']).lower()}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 已渲染 PDF：{str(report['rendered_pdf']).lower()}",
        f"- 已渲染 DOCX：{str(report['rendered_docx']).lower()}",
        f"- 已生成 package manifest：{str(report['package_manifest_generated']).lower()}",
        f"- 已执行人工验收：{str(report['manual_acceptance_performed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["continuation_input_records"]:
        lines.extend(["", "## Continuation Inputs"])
        for record in report["continuation_input_records"]:
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

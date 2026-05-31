from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review import (
    build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review,
)


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry_execute_gate_result_review.v1"
)
EXECUTE_GATE_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry_execute_gate.v1"
)
EXPORT_ENTERED_STATUS = (
    "manifested_routed_downstream_execute_result_continuation_artifact_executor_entry_entered"
)
MANUAL_RECORDED_STATUS = (
    "manifested_routed_downstream_execute_result_continuation_product_review_packet_preparation_recorded"
)
EXPORT_READY_STATUS = (
    "manifested_routed_downstream_execute_result_continuation_artifact_executor_entry_result_review_ready"
)
MANUAL_READY_STATUS = (
    "manifested_routed_downstream_execute_result_continuation_product_review_packet_preparation_result_review_ready"
)
DEFAULT_EXECUTE_GATE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry_execute_gate.json"
)
DEFAULT_ARTIFACT_EXECUTOR_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry.json"
)
DEFAULT_ARTIFACT_EXECUTOR_PATH = Path(
    "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json"
)
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry_execute_gate_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_"
    "continuation_gate_entry_execute_gate_result_review.md"
)
PRODUCT_REVIEW_PACKET_REPORT_PATH = "Results/json/auto_mode_formal_package_product_review_packet.json"
PRODUCT_REVIEW_PACKET_REVIEW_PATH = "Reviews/auto_mode_formal_package_product_review_packet.md"
EXECUTION_BOUNDARY_FIELDS = [
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
]


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_result_review(
    project_root: Path,
    continuation_execute_gate: dict[str, Any],
    route_specific_artifact_executor_entry: dict[str, Any],
    route_specific_artifact_executor: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    source_reasons = build_source_blocking_reasons(continuation_execute_gate)
    boundary_reasons = (
        build_execute_gate_boundary_blocking_reasons(continuation_execute_gate)
        if not source_reasons
        else []
    )
    route_review: dict[str, Any] = {}
    route_review_reasons: list[str] = []
    manual_contract_reasons: list[str] = []

    if not source_reasons and not boundary_reasons:
        if continuation_execute_gate.get("status") == EXPORT_ENTERED_STATUS:
            route_review = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
                project_root,
                route_specific_artifact_executor_entry,
                route_specific_artifact_executor,
                source_paths={
                    "route_specific_artifact_executor_entry": source_paths.get(
                        "route_specific_artifact_executor_entry",
                        str(DEFAULT_ARTIFACT_EXECUTOR_ENTRY_PATH),
                    ),
                    "route_specific_artifact_executor": source_paths.get(
                        "route_specific_artifact_executor",
                        str(DEFAULT_ARTIFACT_EXECUTOR_PATH),
                    ),
                },
            )
            route_review_reasons = route_review.get("blocking_reasons", [])
        elif continuation_execute_gate.get("status") == MANUAL_RECORDED_STATUS:
            manual_contract_reasons = build_product_review_packet_preparation_contract_blocking_reasons(
                continuation_execute_gate
            )

    status = build_status(
        continuation_execute_gate,
        source_reasons,
        boundary_reasons,
        route_review,
        manual_contract_reasons,
    )
    ready_export = status == EXPORT_READY_STATUS
    ready_manual = status == MANUAL_READY_STATUS
    ready = ready_export or ready_manual
    blocking_reasons = dedupe(source_reasons + boundary_reasons + route_review_reasons + manual_contract_reasons)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": continuation_execute_gate.get(
            "topic",
            route_specific_artifact_executor_entry.get(
                "topic",
                route_specific_artifact_executor.get("topic", ""),
            ),
        ),
        "source_paths": {
            "manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate": source_paths.get(
                "manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate",
                str(DEFAULT_EXECUTE_GATE_PATH),
            ),
            "route_specific_artifact_executor_entry": source_paths.get(
                "route_specific_artifact_executor_entry",
                str(DEFAULT_ARTIFACT_EXECUTOR_ENTRY_PATH),
            ),
            "route_specific_artifact_executor": source_paths.get(
                "route_specific_artifact_executor",
                str(DEFAULT_ARTIFACT_EXECUTOR_PATH),
            ),
        },
        "source_status": continuation_execute_gate.get("status", ""),
        "status": status,
        "verified_route_type": continuation_execute_gate.get("verified_route_type", "") if ready else "",
        "routed_next_gate": continuation_execute_gate.get("routed_next_gate", "") if ready else "",
        "downstream_kind": continuation_execute_gate.get("downstream_kind", "") if ready else "",
        "continuation_kind": continuation_execute_gate.get("continuation_kind", "") if ready else "",
        "downstream_execute_result_continuation_reviewed": ready,
        "can_continue_after_downstream_execute_result_continuation": ready,
        "can_continue_to_route_specific_artifact_execution": ready_export,
        "can_continue_to_product_review_packet": ready_manual,
        "route_specific_artifact_executor_entry_result_reviewed": ready_export,
        "route_specific_artifact_executor_status": route_review.get("route_specific_artifact_executor_status", "")
        if ready_export
        else "",
        "product_review_packet_preparation_reviewed": ready_manual,
        "route_specific_artifact_execution_records": route_review.get(
            "route_specific_artifact_execution_records",
            [],
        )
        if ready_export
        else [],
        "product_review_packet_input_records": (
            build_product_review_packet_input_records(continuation_execute_gate)
            if ready_manual
            else []
        ),
        "continuation_execute_command_executed": False,
        "this_command_ran_continuation_command": False,
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
        "source_execute_gate": build_source_execute_gate_summary(continuation_execute_gate),
        "source_route_specific_artifact_executor_entry_result_review": build_route_review_summary(route_review),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, continuation_execute_gate.get("verified_route_type", "")),
    }


def build_source_blocking_reasons(continuation_execute_gate: dict[str, Any]) -> list[str]:
    reasons = []
    status = continuation_execute_gate.get("status")
    if continuation_execute_gate.get("schema_version") != EXECUTE_GATE_SCHEMA_VERSION:
        reasons.append(
            "manifested_routed_downstream_execute_result_continuation_execute_gate_missing_or_invalid_schema"
        )
    if status not in {EXPORT_ENTERED_STATUS, MANUAL_RECORDED_STATUS}:
        reasons.append("manifested_routed_downstream_execute_result_continuation_execute_gate_not_completed")
    for field in ["verified_route_type", "routed_next_gate", "downstream_kind", "continuation_kind"]:
        if not continuation_execute_gate.get(field):
            reasons.append(f"{field}_missing")
    if continuation_execute_gate.get("blocking_reasons"):
        reasons.append("source_downstream_execute_result_continuation_execute_gate_has_blocking_reasons")
    return dedupe(reasons)


def build_execute_gate_boundary_blocking_reasons(continuation_execute_gate: dict[str, Any]) -> list[str]:
    reasons = []
    for field in EXECUTION_BOUNDARY_FIELDS:
        if continuation_execute_gate.get(field) is True:
            if field == "route_specific_artifact_executed":
                reasons.append("downstream_execute_result_continuation_execute_gate_executed_route_specific_artifact")
            elif field == "can_write_product_state":
                reasons.append("downstream_execute_result_continuation_execute_gate_allows_product_state_write")
            else:
                reasons.append(f"downstream_execute_result_continuation_execute_gate_{field}")
    for flag, value in continuation_execute_gate.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"downstream_execute_result_continuation_execute_gate_boundary_violation:{flag}")
    return dedupe(reasons)


def build_product_review_packet_preparation_contract_blocking_reasons(
    continuation_execute_gate: dict[str, Any],
) -> list[str]:
    route_type = continuation_execute_gate.get("verified_route_type", "unknown")
    records = continuation_execute_gate.get("product_review_packet_preparation_records", [])
    reasons = []
    if route_type != "manual_acceptance":
        reasons.append(f"product_review_packet_preparation_route_type_mismatch:{route_type}")
    if continuation_execute_gate.get("routed_next_gate") != "formal_package_delivery_completion_gate":
        reasons.append("product_review_packet_preparation_next_gate_mismatch")
    if continuation_execute_gate.get("downstream_kind") != "product_review_preparation":
        reasons.append("product_review_packet_preparation_downstream_kind_mismatch")
    if continuation_execute_gate.get("continuation_kind") != "product_review_packet_continuation":
        reasons.append("product_review_packet_preparation_continuation_kind_mismatch")
    if continuation_execute_gate.get("product_review_packet_preparation_recorded") is not True:
        reasons.append("product_review_packet_preparation_not_recorded")
    if (
        continuation_execute_gate.get("continuation_execute_command")
        or continuation_execute_gate.get("continuation_execute_command_executed") is True
        or continuation_execute_gate.get("this_command_ran_continuation_command") is True
        or continuation_execute_gate.get("route_specific_artifact_executor_entry_entered") is True
    ):
        reasons.append("product_review_packet_preparation_mixed_with_continuation_command_execution")
    if not isinstance(records, list) or not records:
        reasons.append("product_review_packet_preparation_record_missing")
        return dedupe(reasons)
    if len(records) != 1:
        reasons.append("product_review_packet_preparation_record_not_single")
        return dedupe(reasons)

    record = records[0]
    if record.get("record_id") != "product_review_packet_preparation::manual_acceptance":
        reasons.append("product_review_packet_preparation_record_id_mismatch")
    if record.get("verified_route_type") != "manual_acceptance":
        reasons.append(f"product_review_packet_preparation_route_type_mismatch:{route_type}")
    if record.get("continuation_kind") != "product_review_packet_continuation":
        reasons.append(f"product_review_packet_preparation_record_kind_mismatch:{route_type}")
    if record.get("next_report_path") != PRODUCT_REVIEW_PACKET_REPORT_PATH:
        reasons.append(f"product_review_packet_preparation_next_report_path_mismatch:{route_type}")
    if record.get("next_review_path") != PRODUCT_REVIEW_PACKET_REVIEW_PATH:
        reasons.append(f"product_review_packet_preparation_next_review_path_mismatch:{route_type}")
    if record.get("terminal_status") != "terminal_delivery_completion_ready_for_product_review":
        reasons.append(f"product_review_packet_preparation_terminal_status_mismatch:{route_type}")
    if record.get("terminal_completion") is not True:
        reasons.append(f"product_review_packet_preparation_terminal_completion_missing:{route_type}")
    if record.get("preparation_status") != "product_review_packet_preparation_recorded":
        reasons.append(f"product_review_packet_preparation_status_mismatch:{route_type}")
    if not str(record.get("reviewer", "")).strip():
        reasons.append(f"product_review_packet_preparation_reviewer_missing:{route_type}")
    if not str(record.get("note", "")).strip():
        reasons.append(f"product_review_packet_preparation_note_missing:{route_type}")
    return dedupe(reasons)


def build_status(
    continuation_execute_gate: dict[str, Any],
    source_reasons: list[str],
    boundary_reasons: list[str],
    route_review: dict[str, Any],
    manual_contract_reasons: list[str],
) -> str:
    if source_reasons:
        return "blocked_by_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate"
    if boundary_reasons:
        return "blocked_by_manifested_routed_downstream_execute_result_continuation_execute_boundary"
    if continuation_execute_gate.get("status") == MANUAL_RECORDED_STATUS:
        if manual_contract_reasons:
            return "blocked_by_product_review_packet_preparation_result_contract"
        return MANUAL_READY_STATUS
    if route_review.get("status") == "route_specific_artifact_executor_entry_result_review_ready":
        return EXPORT_READY_STATUS
    return route_review.get("status", "blocked_by_route_specific_artifact_executor_entry")


def build_product_review_packet_input_records(
    continuation_execute_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    record = continuation_execute_gate["product_review_packet_preparation_records"][0]
    return [
        {
            "record_id": record.get("record_id", ""),
            "verified_route_type": record.get("verified_route_type", ""),
            "continuation_kind": record.get("continuation_kind", ""),
            "next_report_path": record.get("next_report_path", ""),
            "next_review_path": record.get("next_review_path", ""),
            "source_product_review_preparation_report_path": record.get(
                "source_product_review_preparation_report_path",
                "",
            ),
            "source_product_review_preparation_review_path": record.get(
                "source_product_review_preparation_review_path",
                "",
            ),
            "terminal_status": record.get("terminal_status", ""),
            "terminal_completion": record.get("terminal_completion") is True,
            "review_status": "product_review_packet_preparation_accepted_for_product_review_packet",
            "can_continue_to_product_review_packet": True,
        }
    ]


def build_source_execute_gate_summary(continuation_execute_gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": continuation_execute_gate.get("schema_version", ""),
        "status": continuation_execute_gate.get("status", ""),
        "verified_route_type": continuation_execute_gate.get("verified_route_type", ""),
        "continuation_kind": continuation_execute_gate.get("continuation_kind", ""),
        "continuation_execute_command_executed": (
            continuation_execute_gate.get("continuation_execute_command_executed") is True
        ),
        "route_specific_artifact_executor_entry_entered": (
            continuation_execute_gate.get("route_specific_artifact_executor_entry_entered") is True
        ),
        "product_review_packet_preparation_recorded": (
            continuation_execute_gate.get("product_review_packet_preparation_recorded") is True
        ),
        "product_review_packet_preparation_records_count": len(
            continuation_execute_gate.get("product_review_packet_preparation_records", []) or []
        ),
        "source_blocking_reasons": continuation_execute_gate.get("blocking_reasons", []),
        "boundary_flags": continuation_execute_gate.get("boundary_flags", {}),
    }


def build_route_review_summary(route_review: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": route_review.get("schema_version", ""),
        "status": route_review.get("status", ""),
        "verified_route_type": route_review.get("verified_route_type", ""),
        "artifact_executor_entry_result_reviewed": (
            route_review.get("artifact_executor_entry_result_reviewed") is True
        ),
        "can_continue_to_route_specific_artifact_execution": (
            route_review.get("can_continue_to_route_specific_artifact_execution") is True
        ),
        "route_specific_artifact_execution_records_count": len(
            route_review.get("route_specific_artifact_execution_records", []) or []
        ),
        "blocking_reasons": route_review.get("blocking_reasons", []),
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
    if status == EXPORT_READY_STATUS:
        return {
            "id": "continue_to_route_specific_artifact_execution",
            "label": "Continue to route-specific artifact execution",
            "description": f"The `{route_type}` artifact executor entry result is accepted for explicit artifact execution.",
        }
    if status == MANUAL_READY_STATUS:
        return {
            "id": "continue_to_product_review_packet",
            "label": "Continue to product-review packet",
            "description": "The manual branch product-review packet preparation is accepted.",
        }
    if status == "blocked_by_product_review_packet_preparation_result_contract":
        return {
            "id": "repair_product_review_packet_preparation_record",
            "label": "Repair product-review packet preparation",
            "description": "Manual continuation must expose exactly one clean product-review packet preparation record.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_downstream_execute_result_continuation_execute_boundary":
        return {
            "id": "repair_downstream_execute_result_continuation_result_boundary",
            "label": "Repair continuation result boundary",
            "description": "P7-BM and delegated reports must remain free of formal artifact side effects.",
            "blocking_reasons": blocking_reasons,
        }
    if status in {
        "blocked_by_route_specific_artifact_executor_entry",
        "blocked_by_route_specific_artifact_executor_entry_result_contract",
        "blocked_by_route_specific_artifact_executor_dry_run_report",
    }:
        return {
            "id": "repair_route_specific_artifact_executor_entry_result",
            "label": "Repair artifact executor entry result",
            "description": "Export continuation must have a clean artifact executor entry result review.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_p7_bm_execute_gate_blockers",
        "label": "Resolve P7-BM execute gate blockers",
        "description": "P7-BM must complete an export or manual continuation before P7-BN can continue.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_result_review_outputs(
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
        "# Auto Mode Formal Package Manifested Routed Downstream Execute Result Continuation Gate Entry Execute Gate Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- downstream kind：`{report['downstream_kind']}`",
        f"- continuation kind：`{report['continuation_kind']}`",
        "- downstream execute result continuation 已审阅："
        f"{str(report['downstream_execute_result_continuation_reviewed']).lower()}",
        "- 可继续 downstream execute result continuation 后续链路："
        f"{str(report['can_continue_after_downstream_execute_result_continuation']).lower()}",
        "- 可继续 route-specific artifact execution："
        f"{str(report['can_continue_to_route_specific_artifact_execution']).lower()}",
        "- 可继续 product-review packet："
        f"{str(report['can_continue_to_product_review_packet']).lower()}",
        "- route-specific artifact execution record 数："
        f"{len(report['route_specific_artifact_execution_records'])}",
        "- product-review packet input record 数："
        f"{len(report['product_review_packet_input_records'])}",
        f"- 已运行 continuation command：{str(report['this_command_ran_continuation_command']).lower()}",
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
    if report["product_review_packet_input_records"]:
        lines.extend(["", "## Product Review Packet Inputs"])
        for record in report["product_review_packet_input_records"]:
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

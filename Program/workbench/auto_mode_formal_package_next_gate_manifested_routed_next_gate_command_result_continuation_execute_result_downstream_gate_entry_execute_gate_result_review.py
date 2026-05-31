from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.v1"
)
DOWNSTREAM_EXECUTE_GATE_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate.v1"
)
SELECTED_ROUTE_EXECUTE_SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execute.v1"
EXECUTE_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execute_manifest.v1"
DEFAULT_EXECUTE_GATE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate.json"
)
DEFAULT_SELECTED_ROUTE_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execute.json")
DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_selected_route_execute.md")
DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH = Path(
    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
)
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry_execute_gate_result_review.md"
)
EXPORT_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest"}
EXPORT_READY_STATUS = "manifested_routed_next_gate_downstream_execute_result_review_ready"
MANUAL_READY_STATUS = "manifested_routed_next_gate_product_review_preparation_result_review_ready"


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
    project_root: Path,
    downstream_execute_gate: dict[str, Any],
    selected_route_execute: dict[str, Any],
    selected_route_execute_manifest: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    source_reasons = build_source_blocking_reasons(downstream_execute_gate)
    boundary_reasons = [] if source_reasons else build_downstream_execute_boundary_reasons(downstream_execute_gate)
    route_type = downstream_execute_gate.get("verified_route_type", "")
    downstream_kind = downstream_execute_gate.get("downstream_kind", "")
    export_contract_reasons: list[str] = []
    manifest_reasons: list[str] = []
    manual_contract_reasons: list[str] = []

    if not source_reasons and not boundary_reasons:
        if downstream_execute_gate.get("status") == "manifested_routed_next_gate_downstream_selected_route_execute_command_executed":
            export_contract_reasons = build_export_contract_blocking_reasons(
                downstream_execute_gate,
                selected_route_execute,
            )
            if not export_contract_reasons:
                manifest_reasons = build_selected_route_execute_manifest_blocking_reasons(
                    selected_route_execute,
                    selected_route_execute_manifest,
                )
        elif downstream_execute_gate.get("status") == "manifested_routed_next_gate_downstream_product_review_preparation_recorded":
            manual_contract_reasons = build_manual_contract_blocking_reasons(downstream_execute_gate)

    blocking_reasons = dedupe(
        source_reasons
        + boundary_reasons
        + export_contract_reasons
        + manifest_reasons
        + manual_contract_reasons
    )
    status = build_status(
        downstream_execute_gate,
        source_reasons,
        boundary_reasons,
        export_contract_reasons,
        manifest_reasons,
        manual_contract_reasons,
    )
    export_ready = status == EXPORT_READY_STATUS
    manual_ready = status == MANUAL_READY_STATUS
    ready = export_ready or manual_ready

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": downstream_execute_gate.get(
            "topic",
            selected_route_execute.get("topic", selected_route_execute_manifest.get("topic", "")),
        ),
        "source_paths": {
            "manifested_routed_next_gate_downstream_execute_gate": source_paths.get(
                "manifested_routed_next_gate_downstream_execute_gate",
                str(DEFAULT_EXECUTE_GATE_PATH),
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
        "source_status": downstream_execute_gate.get("status", ""),
        "status": status,
        "verified_route_type": route_type if ready else "",
        "routed_next_gate": downstream_execute_gate.get("routed_next_gate", "") if ready else "",
        "downstream_kind": downstream_kind if ready else "",
        "downstream_execute_status": downstream_execute_gate.get("downstream_execute_status", "") if export_ready else "",
        "downstream_execute_result_reviewed": ready,
        "can_continue_after_downstream_execute": ready,
        "selected_route_execute_manifest_recorded": (
            selected_route_execute.get("selected_route_execute_manifest_recorded") is True
        )
        if export_ready
        else False,
        "product_review_preparation_recorded": (
            downstream_execute_gate.get("product_review_preparation_recorded") is True
        )
        if manual_ready
        else False,
        "this_command_ran_downstream_command": False,
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
        "route_specific_artifact_executor_input_records": (
            build_route_specific_artifact_executor_input_records(
                downstream_execute_gate,
                selected_route_execute,
                selected_route_execute_manifest,
            )
            if export_ready
            else []
        ),
        "product_review_preparation_result_records": (
            build_product_review_preparation_result_records(downstream_execute_gate) if manual_ready else []
        ),
        "blocking_reasons": blocking_reasons,
        "source_downstream_execute_gate": build_source_downstream_execute_gate_summary(downstream_execute_gate),
        "source_selected_route_execute": build_source_selected_route_execute_summary(selected_route_execute),
        "source_selected_route_execute_manifest": build_source_selected_route_execute_manifest_summary(
            selected_route_execute_manifest
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_source_blocking_reasons(downstream_execute_gate: dict[str, Any]) -> list[str]:
    reasons = []
    if downstream_execute_gate.get("schema_version") != DOWNSTREAM_EXECUTE_GATE_SCHEMA_VERSION:
        reasons.append("manifested_routed_next_gate_downstream_execute_gate_missing_or_invalid_schema")
    if downstream_execute_gate.get("status") not in {
        "manifested_routed_next_gate_downstream_selected_route_execute_command_executed",
        "manifested_routed_next_gate_downstream_product_review_preparation_recorded",
    }:
        reasons.append("manifested_routed_next_gate_downstream_execute_gate_not_completed")
    for field in ["verified_route_type", "routed_next_gate", "downstream_kind"]:
        if not downstream_execute_gate.get(field):
            reasons.append(f"{field}_missing")
    if downstream_execute_gate.get("blocking_reasons"):
        reasons.append("source_downstream_execute_gate_has_blocking_reasons")
    return dedupe(reasons)


def build_downstream_execute_boundary_reasons(downstream_execute_gate: dict[str, Any]) -> list[str]:
    reasons = []
    field_reasons = {
        "selected_route_executed": "downstream_execute_gate_selected_route_executed",
        "export_or_acceptance_executed": "downstream_execute_gate_exported_or_accepted",
        "rendered_pdf": "downstream_execute_gate_rendered_pdf",
        "rendered_docx": "downstream_execute_gate_rendered_docx",
        "package_manifest_generated": "downstream_execute_gate_generated_package_manifest",
        "manual_acceptance_performed": "downstream_execute_gate_performed_manual_acceptance",
        "formal_writeback_executed": "downstream_execute_gate_formal_writeback",
        "this_command_wrote_formal_state": "downstream_execute_gate_wrote_formal_state",
        "can_write_product_state": "downstream_execute_gate_allows_product_state_write",
    }
    for field, reason in field_reasons.items():
        if downstream_execute_gate.get(field) is True:
            reasons.append(reason)
    for flag, value in downstream_execute_gate.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"downstream_execute_gate_boundary_violation:{flag}")
    return dedupe(reasons)


def build_export_contract_blocking_reasons(
    downstream_execute_gate: dict[str, Any],
    selected_route_execute: dict[str, Any],
) -> list[str]:
    route_type = downstream_execute_gate.get("verified_route_type", "unknown")
    reasons = []
    if route_type not in EXPORT_ROUTE_TYPES:
        reasons.append(f"selected_route_execution_route_type_mismatch:{route_type}")
    if downstream_execute_gate.get("routed_next_gate") != "formal_package_export_acceptance_router":
        reasons.append(f"selected_route_execution_next_gate_mismatch:{route_type}")
    if downstream_execute_gate.get("downstream_kind") != "selected_route_execution":
        reasons.append(f"selected_route_execution_downstream_kind_mismatch:{route_type}")
    if downstream_execute_gate.get("downstream_execute_command_executed") is not True:
        reasons.append(f"downstream_execute_command_not_executed:{route_type}")
    if downstream_execute_gate.get("this_command_ran_downstream_command") is not True:
        reasons.append(f"downstream_execute_command_not_run_by_gate:{route_type}")
    if downstream_execute_gate.get("downstream_execute_returncode") != 0:
        reasons.append(f"downstream_execute_returncode_not_zero:{route_type}")
    if downstream_execute_gate.get("downstream_execute_status") != "selected_route_execute_manifest_recorded":
        reasons.append(f"downstream_execute_status_not_manifest_recorded:{route_type}")
    if downstream_execute_gate.get("selected_route_execute_manifest_recorded") is not True:
        reasons.append(f"downstream_execute_manifest_not_recorded:{route_type}")
    if downstream_execute_gate.get("product_review_preparation_recorded") is True:
        reasons.append(f"selected_route_execution_mixed_with_product_review_preparation:{route_type}")

    delegated_result = downstream_execute_gate.get("downstream_execute_result", {})
    if delegated_result.get("report_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH):
        reasons.append(f"downstream_execute_result_report_path_mismatch:{route_type}")
    if delegated_result.get("review_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH):
        reasons.append(f"downstream_execute_result_review_path_mismatch:{route_type}")
    if delegated_result.get("manifest_path") != str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH):
        reasons.append(f"downstream_execute_result_manifest_path_mismatch:{route_type}")
    if delegated_result.get("returncode") != downstream_execute_gate.get("downstream_execute_returncode"):
        reasons.append(f"downstream_execute_result_returncode_mismatch:{route_type}")
    if delegated_result.get("status") != selected_route_execute.get("status"):
        reasons.append(f"downstream_execute_result_status_mismatch:{route_type}")

    if selected_route_execute.get("schema_version") != SELECTED_ROUTE_EXECUTE_SCHEMA_VERSION:
        reasons.append(f"selected_route_execute_missing_or_invalid_schema:{route_type}")
    if selected_route_execute.get("status") != "selected_route_execute_manifest_recorded":
        reasons.append(f"selected_route_execute_status_mismatch:{route_type}")
    if selected_route_execute.get("status") != downstream_execute_gate.get("downstream_execute_status"):
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


def build_manual_contract_blocking_reasons(downstream_execute_gate: dict[str, Any]) -> list[str]:
    route_type = downstream_execute_gate.get("verified_route_type", "unknown")
    reasons = []
    if route_type != "manual_acceptance":
        reasons.append(f"product_review_preparation_route_type_mismatch:{route_type}")
    if downstream_execute_gate.get("routed_next_gate") != "formal_package_delivery_completion_gate":
        reasons.append("product_review_preparation_next_gate_mismatch")
    if downstream_execute_gate.get("downstream_kind") != "product_review_preparation":
        reasons.append("product_review_preparation_downstream_kind_mismatch")
    if downstream_execute_gate.get("product_review_preparation_recorded") is not True:
        reasons.append("product_review_preparation_not_recorded")
    if (
        downstream_execute_gate.get("downstream_execute_command_executed") is True
        or downstream_execute_gate.get("this_command_ran_downstream_command") is True
        or downstream_execute_gate.get("downstream_execute_returncode") is not None
        or downstream_execute_gate.get("downstream_execute_status")
        or downstream_execute_gate.get("downstream_execute_result")
        or downstream_execute_gate.get("selected_route_execute_manifest_recorded") is True
    ):
        reasons.append("product_review_preparation_mixed_with_downstream_command_execution")
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
    selected_route_execute: dict[str, Any],
    selected_route_execute_manifest: dict[str, Any],
) -> list[str]:
    operations = selected_route_execute_manifest.get("selected_route_execute_operations", [])
    route_type = operations[0].get("route_type", "unknown") if isinstance(operations, list) and operations else "unknown"
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
    if route_type not in EXPORT_ROUTE_TYPES:
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
    downstream_execute_gate: dict[str, Any],
    source_reasons: list[str],
    boundary_reasons: list[str],
    export_contract_reasons: list[str],
    manifest_reasons: list[str],
    manual_contract_reasons: list[str],
) -> str:
    if source_reasons:
        return "blocked_by_manifested_routed_next_gate_downstream_execute_gate"
    if boundary_reasons:
        return "blocked_by_manifested_routed_next_gate_downstream_execute_boundary"
    if manual_contract_reasons:
        return "blocked_by_manifested_routed_next_gate_product_review_preparation_contract"
    if export_contract_reasons:
        return "blocked_by_manifested_routed_next_gate_downstream_selected_route_execute_contract"
    if manifest_reasons:
        return "blocked_by_manifested_routed_next_gate_downstream_selected_route_manifest_review"
    if downstream_execute_gate.get("status") == "manifested_routed_next_gate_downstream_product_review_preparation_recorded":
        return MANUAL_READY_STATUS
    return EXPORT_READY_STATUS


def build_route_specific_artifact_executor_input_records(
    downstream_execute_gate: dict[str, Any],
    selected_route_execute: dict[str, Any],
    selected_route_execute_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    operation = selected_route_execute_manifest["selected_route_execute_operations"][0]
    route_type = operation.get("route_type", "")
    return [
        {
            "record_id": (
                "manifested_routed_downstream_execute_result_review::"
                f"route_specific_artifact_executor::{route_type}"
            ),
            "verified_route_type": downstream_execute_gate.get("verified_route_type", ""),
            "routed_next_gate": downstream_execute_gate.get("routed_next_gate", ""),
            "downstream_kind": downstream_execute_gate.get("downstream_kind", ""),
            "selected_route_execute_status": selected_route_execute.get("status", ""),
            "selected_route_execute_report_path": str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH),
            "selected_route_execute_review_path": str(DEFAULT_SELECTED_ROUTE_EXECUTE_REVIEW_PATH),
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


def build_product_review_preparation_result_records(
    downstream_execute_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    input_record = downstream_execute_gate.get("downstream_input_record", {})
    return [
        {
            "record_id": "manifested_routed_downstream_execute_result_review::product_review_preparation::manual_acceptance",
            "verified_route_type": downstream_execute_gate.get("verified_route_type", ""),
            "routed_next_gate": downstream_execute_gate.get("routed_next_gate", ""),
            "downstream_kind": downstream_execute_gate.get("downstream_kind", ""),
            "terminal_status": input_record.get("terminal_status", ""),
            "next_report_path": input_record.get("next_report_path", ""),
            "next_review_path": input_record.get("next_review_path", ""),
            "terminal_completion": input_record.get("terminal_completion") is True,
            "review_status": "product_review_preparation_accepted_for_product_review_packet",
            "can_continue_to_product_review_packet": True,
        }
    ]


def build_source_downstream_execute_gate_summary(downstream_execute_gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": downstream_execute_gate.get("schema_version", ""),
        "status": downstream_execute_gate.get("status", ""),
        "verified_route_type": downstream_execute_gate.get("verified_route_type", ""),
        "routed_next_gate": downstream_execute_gate.get("routed_next_gate", ""),
        "downstream_kind": downstream_execute_gate.get("downstream_kind", ""),
        "downstream_execute_command_executed": (
            downstream_execute_gate.get("downstream_execute_command_executed") is True
        ),
        "downstream_execute_status": downstream_execute_gate.get("downstream_execute_status", ""),
        "selected_route_execute_manifest_recorded": (
            downstream_execute_gate.get("selected_route_execute_manifest_recorded") is True
        ),
        "product_review_preparation_recorded": (
            downstream_execute_gate.get("product_review_preparation_recorded") is True
        ),
        "source_blocking_reasons": downstream_execute_gate.get("blocking_reasons", []),
        "boundary_flags": downstream_execute_gate.get("boundary_flags", {}),
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
    if status == EXPORT_READY_STATUS:
        return {
            "id": "continue_to_route_specific_artifact_executor",
            "label": "Continue to route-specific artifact executor",
            "description": f"The `{route_type}` downstream execute result is accepted for artifact execution.",
        }
    if status == MANUAL_READY_STATUS:
        return {
            "id": "continue_to_product_review_packet",
            "label": "Continue to product review packet",
            "description": "The manual terminal branch has a reviewed product-review preparation record.",
        }
    if status == "blocked_by_manifested_routed_next_gate_downstream_selected_route_execute_contract":
        return {
            "id": "repair_downstream_selected_route_execute_contract",
            "label": "Repair downstream selected-route execute contract",
            "description": "P7-BJ and selected-route execute report must describe the same completed manifest event.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_downstream_selected_route_manifest_review":
        return {
            "id": "repair_selected_route_execute_manifest",
            "label": "Repair selected-route execute manifest",
            "description": "The selected-route execute manifest must remain planned-only before continuation.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_product_review_preparation_contract":
        return {
            "id": "repair_product_review_preparation_record",
            "label": "Repair product-review preparation record",
            "description": "Manual terminal continuation must stay a pure product-review preparation record.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_downstream_execute_gate_blockers",
        "label": "Resolve P7-BJ downstream execute gate blockers",
        "description": "P7-BJ must finish downstream execution or product-review preparation before P7-BK can continue.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Downstream Execute Gate Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- downstream kind：`{report['downstream_kind']}`",
        "- downstream execute result 已审阅："
        f"{str(report['downstream_execute_result_reviewed']).lower()}",
        "- 可继续 downstream execute 后续链路："
        f"{str(report['can_continue_after_downstream_execute']).lower()}",
        "- selected route execute manifest 已记录："
        f"{str(report['selected_route_execute_manifest_recorded']).lower()}",
        "- product review preparation 已记录："
        f"{str(report['product_review_preparation_recorded']).lower()}",
        "- route-specific artifact executor input 数："
        f"{len(report['route_specific_artifact_executor_input_records'])}",
        "- product-review preparation result record 数："
        f"{len(report['product_review_preparation_result_records'])}",
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
    if report["route_specific_artifact_executor_input_records"]:
        lines.extend(["", "## Route-Specific Artifact Executor Inputs"])
        for record in report["route_specific_artifact_executor_input_records"]:
            lines.append(f"- `{record['record_id']}`: {record['review_status']}")
    if report["product_review_preparation_result_records"]:
        lines.extend(["", "## Product Review Preparation Result Records"])
        for record in report["product_review_preparation_result_records"]:
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

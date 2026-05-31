from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.v1"
ENTRY_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.v1"
LEDGER_SCHEMA_VERSION = "p7.auto_mode_formal_package_verified_route_completion_ledger.v1"
ENTRY_SUCCESS_STATUS = "next_gate_verified_route_completion_ledger_entered"
LEDGER_SUCCESS_STATUS = "verified_route_completion_ledger_recorded"
COMPLETION_RECORD_STATUS = "verified_route_completion_recorded"
DEFAULT_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry.json"
)
DEFAULT_LEDGER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_completion_ledger.json")
DEFAULT_LEDGER_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_verified_route_completion_ledger.md")
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review.md"
)
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}
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


def build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
    project_root: Path,
    verified_route_completion_ledger_entry: dict[str, Any],
    verified_route_completion_ledger: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    entry_reasons = build_entry_blocking_reasons(verified_route_completion_ledger_entry)
    ledger_reasons = (
        build_ledger_blocking_reasons(verified_route_completion_ledger)
        if not entry_reasons
        else []
    )
    contract_reasons = (
        build_entry_ledger_contract_blocking_reasons(
            verified_route_completion_ledger_entry,
            verified_route_completion_ledger,
        )
        if not entry_reasons and not ledger_reasons
        else []
    )
    boundary_reasons = (
        build_boundary_blocking_reasons(verified_route_completion_ledger)
        if not entry_reasons and not ledger_reasons and not contract_reasons
        else []
    )
    blocking_reasons = dedupe(entry_reasons + contract_reasons + ledger_reasons + boundary_reasons)
    status = build_status(entry_reasons, contract_reasons, ledger_reasons, boundary_reasons)
    ready = status == "verified_route_completion_ledger_entry_result_review_ready"
    route_type = verified_route_completion_ledger_entry.get("verified_route_type", "") if ready else ""
    records = verified_route_completion_ledger.get("route_completion_records", []) if ready else []

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": verified_route_completion_ledger_entry.get(
            "topic",
            verified_route_completion_ledger.get("topic", ""),
        ),
        "source_paths": {
            "verified_route_completion_ledger_entry": source_paths.get(
                "verified_route_completion_ledger_entry",
                str(DEFAULT_ENTRY_PATH),
            ),
            "verified_route_completion_ledger": source_paths.get(
                "verified_route_completion_ledger",
                str(DEFAULT_LEDGER_PATH),
            ),
        },
        "source_status": verified_route_completion_ledger_entry.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "verified_route_completion_ledger_status": (
            verified_route_completion_ledger.get("status", "") if ready else ""
        ),
        "verified_route_completion_ledger_entry_result_reviewed": ready,
        "can_continue_to_verified_route_next_gate_router": ready,
        "route_completion_ledger_recorded": (
            verified_route_completion_ledger.get("route_completion_ledger_recorded") is True if ready else False
        ),
        "can_enter_next_auto_mode_gate": (
            verified_route_completion_ledger.get("can_enter_next_auto_mode_gate") is True if ready else False
        ),
        "route_completion_record_count": len(records),
        "route_completion_records": records,
        "verified_route_next_gate_router_input_records": (
            build_verified_route_next_gate_router_input_records(
                verified_route_completion_ledger_entry,
                verified_route_completion_ledger,
            )
            if ready
            else []
        ),
        "verified_route_next_gate_router_executed": False,
        "this_command_ran_verified_route_next_gate_router": False,
        "entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_ledger_entry": build_source_entry_summary(verified_route_completion_ledger_entry),
        "source_ledger": build_source_ledger_summary(verified_route_completion_ledger),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type),
    }


def build_entry_blocking_reasons(verified_route_completion_ledger_entry: dict[str, Any]) -> list[str]:
    reasons = []
    route_type = verified_route_completion_ledger_entry.get("verified_route_type", "unknown")
    if verified_route_completion_ledger_entry.get("schema_version") != ENTRY_SCHEMA_VERSION:
        reasons.append("verified_route_completion_ledger_entry_missing_or_invalid_schema")
    if verified_route_completion_ledger_entry.get("status") != ENTRY_SUCCESS_STATUS:
        reasons.append("verified_route_completion_ledger_entry_not_completed")
    if verified_route_completion_ledger_entry.get("can_enter_verified_route_completion_ledger") is not True:
        reasons.append("ledger_entry_did_not_allow_completion_ledger")
    if verified_route_completion_ledger_entry.get("verified_route_completion_ledger_entry_command_executed") is not True:
        reasons.append("verified_route_completion_ledger_entry_command_not_executed")
    if verified_route_completion_ledger_entry.get("this_command_ran_verified_route_completion_ledger") is not True:
        reasons.append("ledger_entry_did_not_run_completion_ledger")
    if verified_route_completion_ledger_entry.get("verified_route_completion_ledger_returncode") != 0:
        reasons.append("verified_route_completion_ledger_returncode_not_zero")
    if verified_route_completion_ledger_entry.get("verified_route_completion_ledger_status") != LEDGER_SUCCESS_STATUS:
        reasons.append("verified_route_completion_ledger_status_not_recorded")
    if verified_route_completion_ledger_entry.get("route_completion_ledger_recorded") is not True:
        reasons.append("route_completion_ledger_not_recorded")
    if verified_route_completion_ledger_entry.get("can_enter_next_auto_mode_gate") is not True:
        reasons.append("ledger_entry_cannot_enter_next_auto_mode_gate")
    if not verified_route_completion_ledger_entry.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if verified_route_completion_ledger_entry.get("route_completion_record_count", 0) <= 0:
        reasons.append("route_completion_record_count_missing")
    if verified_route_completion_ledger_entry.get("route_specific_artifact_verified") is not True:
        reasons.append("ledger_entry_route_specific_artifact_not_verified")
    if verified_route_completion_ledger_entry.get("artifact_verification_record_count", 0) <= 0:
        reasons.append("artifact_verification_record_count_missing")
    for field in ["selected_route_executed", "export_or_acceptance_executed"]:
        if verified_route_completion_ledger_entry.get(field) is not True:
            reasons.append(f"ledger_entry_{field}_missing")
    for field in [
        "verified_route_completion_ledger_report_path",
        "verified_route_completion_ledger_review_path",
        "verified_route_completion_ledger_status",
    ]:
        if not verified_route_completion_ledger_entry.get(field):
            reasons.append(f"{field}_missing")
    if route_type in VALID_ROUTE_TYPES and not route_flags_match(verified_route_completion_ledger_entry, route_type):
        reasons.append(f"ledger_entry_route_flag_mismatch:{route_type}")
    for field in ["formal_writeback_executed", "this_command_wrote_formal_state", "can_write_product_state"]:
        if verified_route_completion_ledger_entry.get(field) is True:
            reasons.append(f"ledger_entry_{field}")
    if verified_route_completion_ledger_entry.get("blocking_reasons"):
        reasons.append("source_ledger_entry_has_blocking_reasons")
    for flag, value in verified_route_completion_ledger_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"ledger_entry_boundary_violation:{flag}")
    return dedupe(reasons)


def build_entry_ledger_contract_blocking_reasons(
    verified_route_completion_ledger_entry: dict[str, Any],
    verified_route_completion_ledger: dict[str, Any],
) -> list[str]:
    route_type = verified_route_completion_ledger_entry.get("verified_route_type", "unknown")
    entry_result = verified_route_completion_ledger_entry.get("verified_route_completion_ledger_result", {})
    summary = entry_result.get("verified_route_completion_ledger_report_summary", {})
    ledger_records = verified_route_completion_ledger.get("route_completion_records", []) or []
    entry_records = verified_route_completion_ledger_entry.get("route_completion_records", []) or []
    reasons = []
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"verified_route_type_unknown:{route_type}")
    if verified_route_completion_ledger_entry.get("verified_route_completion_ledger_report_path") != str(
        DEFAULT_LEDGER_PATH
    ):
        reasons.append(f"verified_route_completion_ledger_report_path_mismatch:{route_type}")
    if verified_route_completion_ledger_entry.get("verified_route_completion_ledger_review_path") != str(
        DEFAULT_LEDGER_REVIEW_PATH
    ):
        reasons.append(f"verified_route_completion_ledger_review_path_mismatch:{route_type}")
    if entry_result.get("report_path") != str(DEFAULT_LEDGER_PATH):
        reasons.append(f"verified_route_completion_ledger_result_report_path_mismatch:{route_type}")
    if entry_result.get("review_path") != str(DEFAULT_LEDGER_REVIEW_PATH):
        reasons.append(f"verified_route_completion_ledger_result_review_path_mismatch:{route_type}")
    if entry_result.get("returncode") != verified_route_completion_ledger_entry.get(
        "verified_route_completion_ledger_returncode"
    ):
        reasons.append(f"verified_route_completion_ledger_result_returncode_mismatch:{route_type}")
    if entry_result.get("status") != verified_route_completion_ledger.get("status"):
        reasons.append(f"verified_route_completion_ledger_result_status_mismatch:{route_type}")
    if verified_route_completion_ledger_entry.get("verified_route_completion_ledger_status") != (
        verified_route_completion_ledger.get("status")
    ):
        reasons.append(f"verified_route_completion_ledger_status_mismatch:{route_type}")
    if verified_route_completion_ledger_entry.get("route_completion_ledger_recorded") != (
        verified_route_completion_ledger.get("route_completion_ledger_recorded") is True
    ):
        reasons.append(f"route_completion_ledger_recorded_mismatch:{route_type}")
    if verified_route_completion_ledger_entry.get("can_enter_next_auto_mode_gate") != (
        verified_route_completion_ledger.get("can_enter_next_auto_mode_gate") is True
    ):
        reasons.append(f"can_enter_next_auto_mode_gate_mismatch:{route_type}")
    if verified_route_completion_ledger_entry.get("route_completion_record_count") != len(ledger_records):
        reasons.append(f"route_completion_record_count_mismatch:{route_type}")
    if entry_records != ledger_records:
        reasons.append(f"route_completion_records_mismatch:{route_type}")
    if summary.get("schema_version") != verified_route_completion_ledger.get("schema_version"):
        reasons.append(f"verified_route_completion_ledger_summary_schema_mismatch:{route_type}")
    if summary.get("status") != verified_route_completion_ledger.get("status"):
        reasons.append(f"verified_route_completion_ledger_summary_status_mismatch:{route_type}")
    if summary.get("verified_route_type") != verified_route_completion_ledger.get("verified_route_type"):
        reasons.append(f"verified_route_completion_ledger_summary_route_mismatch:{route_type}")
    if summary.get("route_completion_ledger_recorded") != (
        verified_route_completion_ledger.get("route_completion_ledger_recorded") is True
    ):
        reasons.append(f"verified_route_completion_ledger_summary_recorded_mismatch:{route_type}")
    if summary.get("can_enter_next_auto_mode_gate") != (
        verified_route_completion_ledger.get("can_enter_next_auto_mode_gate") is True
    ):
        reasons.append(f"verified_route_completion_ledger_summary_next_gate_mismatch:{route_type}")
    if summary.get("route_completion_record_count") != len(ledger_records):
        reasons.append(f"verified_route_completion_ledger_summary_record_count_mismatch:{route_type}")
    if summary.get("blocking_reasons") != verified_route_completion_ledger.get("blocking_reasons", []):
        reasons.append(f"verified_route_completion_ledger_summary_blockers_mismatch:{route_type}")
    return dedupe(reasons)


def build_ledger_blocking_reasons(verified_route_completion_ledger: dict[str, Any]) -> list[str]:
    route_type = verified_route_completion_ledger.get("verified_route_type", "unknown")
    records = verified_route_completion_ledger.get("route_completion_records", []) or []
    reasons = []
    if verified_route_completion_ledger.get("schema_version") != LEDGER_SCHEMA_VERSION:
        reasons.append("verified_route_completion_ledger_missing_or_invalid_schema")
    if verified_route_completion_ledger.get("status") != LEDGER_SUCCESS_STATUS:
        reasons.append("verified_route_completion_ledger_status_not_recorded")
    if verified_route_completion_ledger.get("route_completion_ledger_recorded") is not True:
        reasons.append("verified_route_completion_ledger_not_recorded")
    if verified_route_completion_ledger.get("can_enter_next_auto_mode_gate") is not True:
        reasons.append("verified_route_completion_ledger_cannot_enter_next_gate")
    if not verified_route_completion_ledger.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    elif route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"verified_route_type_unknown:{route_type}")
    if verified_route_completion_ledger.get("blocking_reasons"):
        reasons.append("source_ledger_has_blocking_reasons")
    if len(records) != 1:
        reasons.append("route_completion_records_missing" if not records else "route_completion_records_not_single")
        return dedupe(reasons)
    record = records[0]
    if record.get("route_type") != route_type:
        reasons.append(f"route_completion_record_route_mismatch:{route_type}")
    if record.get("completion_status") != COMPLETION_RECORD_STATUS:
        reasons.append(f"route_completion_record_not_recorded:{route_type}")
    if record.get("completion_id") != f"verified_route_completion::{route_type}":
        reasons.append(f"route_completion_id_mismatch:{route_type}")
    if record.get("can_enter_next_auto_mode_gate") is not True:
        reasons.append(f"route_completion_record_cannot_enter_next_gate:{route_type}")
    if record.get("artifact_count") != len(record.get("verified_artifacts", []) or []):
        reasons.append(f"route_completion_record_artifact_count_mismatch:{route_type}")
    if not record.get("verified_artifacts"):
        reasons.append(f"route_completion_record_artifacts_missing:{route_type}")
    for field in ["formal_writeback_executed", "this_command_wrote_formal_state", "can_write_product_state"]:
        if record.get(field) is True:
            reasons.append(f"route_completion_record_{field}:{route_type}")
    return dedupe(reasons)


def build_boundary_blocking_reasons(verified_route_completion_ledger: dict[str, Any]) -> list[str]:
    reasons = []
    for field in ["formal_writeback_executed", "this_command_wrote_formal_state", "can_write_product_state"]:
        if verified_route_completion_ledger.get(field) is True:
            reasons.append(f"verified_route_completion_ledger_{field}")
    for flag, value in verified_route_completion_ledger.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"verified_route_completion_ledger_boundary_violation:{flag}")
    return dedupe(reasons)


def build_status(
    entry_reasons: list[str],
    contract_reasons: list[str],
    ledger_reasons: list[str],
    boundary_reasons: list[str],
) -> str:
    if entry_reasons:
        return "blocked_by_verified_route_completion_ledger_entry"
    if contract_reasons:
        return "blocked_by_verified_route_completion_ledger_entry_result_contract"
    if ledger_reasons:
        return "blocked_by_verified_route_completion_ledger_review"
    if boundary_reasons:
        return "blocked_by_verified_route_completion_ledger_entry_result_boundary"
    return "verified_route_completion_ledger_entry_result_review_ready"


def build_verified_route_next_gate_router_input_records(
    verified_route_completion_ledger_entry: dict[str, Any],
    verified_route_completion_ledger: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = verified_route_completion_ledger_entry.get("verified_route_type", "")
    records = verified_route_completion_ledger.get("route_completion_records", []) or []
    completion_ids = [record.get("completion_id", "") for record in records]
    return [
        {
            "record_id": f"verified_route_next_gate_router_input::{route_type}",
            "verified_route_type": route_type,
            "verified_route_completion_ledger_status": verified_route_completion_ledger.get("status", ""),
            "verified_route_completion_ledger_report_path": str(DEFAULT_LEDGER_PATH),
            "verified_route_completion_ledger_review_path": str(DEFAULT_LEDGER_REVIEW_PATH),
            "route_completion_record_count": len(records),
            "route_completion_ids": completion_ids,
            "review_status": "verified_route_completion_ledger_entry_accepted_for_next_gate_router",
            "can_continue_to_verified_route_next_gate_router": True,
        }
    ]


def build_source_entry_summary(verified_route_completion_ledger_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": verified_route_completion_ledger_entry.get("schema_version", ""),
        "status": verified_route_completion_ledger_entry.get("status", ""),
        "verified_route_type": verified_route_completion_ledger_entry.get("verified_route_type", ""),
        "verified_route_completion_ledger_entry_command_executed": verified_route_completion_ledger_entry.get(
            "verified_route_completion_ledger_entry_command_executed"
        )
        is True,
        "this_command_ran_verified_route_completion_ledger": verified_route_completion_ledger_entry.get(
            "this_command_ran_verified_route_completion_ledger"
        )
        is True,
        "verified_route_completion_ledger_status": verified_route_completion_ledger_entry.get(
            "verified_route_completion_ledger_status",
            "",
        ),
        "route_completion_ledger_recorded": verified_route_completion_ledger_entry.get(
            "route_completion_ledger_recorded"
        )
        is True,
        "can_enter_next_auto_mode_gate": verified_route_completion_ledger_entry.get("can_enter_next_auto_mode_gate")
        is True,
        "route_completion_record_count": verified_route_completion_ledger_entry.get(
            "route_completion_record_count",
            0,
        ),
        "blocking_reasons": verified_route_completion_ledger_entry.get("blocking_reasons", []),
        "boundary_flags": verified_route_completion_ledger_entry.get("boundary_flags", {}),
    }


def build_source_ledger_summary(verified_route_completion_ledger: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": verified_route_completion_ledger.get("schema_version", ""),
        "status": verified_route_completion_ledger.get("status", ""),
        "verified_route_type": verified_route_completion_ledger.get("verified_route_type", ""),
        "route_completion_ledger_recorded": verified_route_completion_ledger.get("route_completion_ledger_recorded")
        is True,
        "can_enter_next_auto_mode_gate": verified_route_completion_ledger.get("can_enter_next_auto_mode_gate")
        is True,
        "route_completion_record_count": len(verified_route_completion_ledger.get("route_completion_records", []) or []),
        "formal_writeback_executed": verified_route_completion_ledger.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": verified_route_completion_ledger.get(
            "this_command_wrote_formal_state"
        )
        is True,
        "can_write_product_state": verified_route_completion_ledger.get("can_write_product_state") is True,
        "blocking_reasons": verified_route_completion_ledger.get("blocking_reasons", []),
        "boundary_flags": verified_route_completion_ledger.get("boundary_flags", {}),
    }


def route_flags_match(payload: dict[str, Any], route_type: str) -> bool:
    expected = ROUTE_FLAGS[route_type]
    return all(payload.get(flag) is expected_value for flag, expected_value in expected.items())


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
        "recorded_verified_route_completion_ledger": False,
    }


def build_next_action(status: str, blocking_reasons: list[str], route_type: str) -> dict[str, Any]:
    if status == "verified_route_completion_ledger_entry_result_review_ready":
        return {
            "id": "run_verified_route_next_gate_router",
            "label": "Run verified route next-gate router",
            "description": f"The `{route_type}` completion ledger is reviewed and can be routed onward.",
        }
    if status == "blocked_by_verified_route_completion_ledger_entry":
        return {
            "id": "resolve_verified_route_completion_ledger_entry_blockers",
            "label": "Resolve P7-AV blockers",
            "description": "P7-AV must enter the verified route completion ledger before review can continue.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_completion_ledger_entry_result_contract":
        return {
            "id": "repair_verified_route_completion_ledger_entry_result_contract",
            "label": "Repair P7-AV ledger result contract",
            "description": "P7-AV and the existing ledger output must describe the same recorded completion.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_completion_ledger_review":
        return {
            "id": "repair_verified_route_completion_ledger_output",
            "label": "Repair verified route completion ledger output",
            "description": "The ledger must contain one clean completion record before routing.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_verified_route_completion_ledger_review_boundary",
        "label": "Resolve ledger review boundary violation",
        "description": "P7-AW is read-only and cannot consume a state-writing ledger result.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Verified Route Completion Ledger Entry Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        "- ledger entry result reviewed："
        f"{str(report['verified_route_completion_ledger_entry_result_reviewed']).lower()}",
        "- 可继续到 verified route next-gate router："
        f"{str(report['can_continue_to_verified_route_next_gate_router']).lower()}",
        f"- ledger status：`{report['verified_route_completion_ledger_status']}`",
        f"- route completion ledger recorded：{str(report['route_completion_ledger_recorded']).lower()}",
        f"- 可进入下一 Auto Mode gate：{str(report['can_enter_next_auto_mode_gate']).lower()}",
        f"- route completion record 数：{report['route_completion_record_count']}",
        f"- router input record 数：{len(report['verified_route_next_gate_router_input_records'])}",
        "- 已执行 verified route next-gate router："
        f"{str(report['verified_route_next_gate_router_executed']).lower()}",
        "- 本命令运行 verified route next-gate router："
        f"{str(report['this_command_ran_verified_route_next_gate_router']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["verified_route_next_gate_router_input_records"]:
        lines.extend(["", "## Router Input Records"])
        for record in report["verified_route_next_gate_router_input_records"]:
            lines.append(
                f"- `{record['record_id']}`: route=`{record['verified_route_type']}`, "
                f"records={record['route_completion_record_count']}, "
                f"continue={str(record['can_continue_to_verified_route_next_gate_router']).lower()}"
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

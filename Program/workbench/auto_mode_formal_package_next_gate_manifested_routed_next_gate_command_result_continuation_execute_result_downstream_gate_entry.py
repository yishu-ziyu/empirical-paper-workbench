from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry.v1"
)
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_review.v1"
)
RESULT_REVIEW_READY_STATUS = (
    "manifested_routed_next_gate_result_continuation_execute_result_review_ready"
)
READY_STATUS = (
    "ready_for_manifested_routed_next_gate_result_continuation_execute_downstream_gate_entry"
)
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_review.json"
)
DEFAULT_GATE_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_"
    "continuation_execute_result_downstream_gate_entry.md"
)

DOWNSTREAM_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "record_key": "selected_route_execution_preflight_records",
        "other_record_key": "terminal_continuation_records",
        "review_status": "selected_route_preflight_accepted_for_explicit_route_execution",
        "continue_field": "can_continue_to_selected_route_execution",
        "downstream_kind": "selected_route_execution",
        "downstream_command": "auto_mode_formal_package_next_gate_selected_route_execute",
        "command_path": "Program/auto_mode_formal_package_next_gate_selected_route_execute.py",
        "next_report_path": "Results/json/auto_mode_formal_package_next_gate_selected_route_execute.json",
        "next_review_path": "Reviews/auto_mode_formal_package_next_gate_selected_route_execute.md",
        "downstream_status": "pending_explicit_selected_route_execution",
        "requires_explicit_downstream_command": True,
        "terminal_completion": False,
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "record_key": "terminal_continuation_records",
        "other_record_key": "selected_route_execution_preflight_records",
        "review_status": "terminal_continuation_accepted_for_product_review_preparation",
        "continue_field": "can_continue_to_product_review_preparation",
        "downstream_kind": "product_review_preparation",
        "downstream_command": "product_review_preparation",
        "command_path": "",
        "next_report_path": "Results/json/auto_mode_formal_package_product_review_preparation.json",
        "next_review_path": "Reviews/auto_mode_formal_package_product_review_preparation.md",
        "downstream_status": "pending_product_review_preparation",
        "requires_explicit_downstream_command": False,
        "terminal_completion": True,
    },
}

SELECTED_ROUTE_CONTRACTS = {
    "pdf_export": {
        "routed_action": "formal_pdf_export_preflight",
        "route_specific_next_command": "formal_pdf_export_execute",
        "planned_outputs": ["Submissions/formal_package/paper.pdf"],
    },
    "docx_export": {
        "routed_action": "formal_docx_export_preflight",
        "route_specific_next_command": "formal_docx_export_execute",
        "planned_outputs": ["Submissions/formal_package/paper.docx"],
    },
    "package_manifest": {
        "routed_action": "formal_submission_package_manifest_preflight",
        "route_specific_next_command": "formal_submission_package_manifest_execute",
        "planned_outputs": ["Submissions/formal_package/manifest.json"],
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
    continuation_execute_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    result_reasons = build_result_review_blocking_reasons(continuation_execute_result_review)
    boundary_reasons = (
        build_boundary_blocking_reasons(continuation_execute_result_review)
        if not result_reasons
        else []
    )
    contract_reasons = (
        build_downstream_contract_blocking_reasons(continuation_execute_result_review)
        if not result_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(result_reasons + boundary_reasons + contract_reasons)
    status = build_status(result_reasons, boundary_reasons, contract_reasons)
    ready = status == READY_STATUS
    route_type = continuation_execute_result_review.get("verified_route_type", "") if ready else ""
    routed_next_gate = continuation_execute_result_review.get("routed_next_gate", "") if ready else ""
    contract = DOWNSTREAM_CONTRACTS.get(routed_next_gate, {}) if ready else {}
    records = (
        build_downstream_input_records(continuation_execute_result_review)
        if ready
        else []
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": continuation_execute_result_review.get("topic", ""),
        "source_paths": {
            "manifested_routed_next_gate_command_result_continuation_execute_result_review": (
                source_paths.get(
                    "manifested_routed_next_gate_command_result_continuation_execute_result_review",
                    str(DEFAULT_RESULT_REVIEW_PATH),
                )
            ),
        },
        "source_status": continuation_execute_result_review.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "downstream_kind": contract.get("downstream_kind", "") if ready else "",
        "downstream_status": contract.get("downstream_status", "") if ready else "",
        "downstream_gate_entry_recorded": ready,
        "can_request_manifested_routed_next_gate_result_continuation_downstream": ready,
        "requires_explicit_downstream_command": any(
            record["requires_explicit_downstream_command"] for record in records
        ),
        "downstream_input_records": records,
        "downstream_command_executed": False,
        "this_command_ran_downstream_command": False,
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
            continuation_execute_result_review
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, records, blocking_reasons),
    }


def build_result_review_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    reasons = []
    if result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append(
            "manifested_routed_next_gate_result_continuation_execute_result_review_missing_or_invalid_schema"
        )
    if result_review.get("status") != RESULT_REVIEW_READY_STATUS:
        reasons.append(
            "manifested_routed_next_gate_result_continuation_execute_result_review_not_ready"
        )
    if result_review.get("continuation_execute_result_reviewed") is not True:
        reasons.append("manifested_routed_next_gate_result_continuation_execute_result_not_reviewed")
    if result_review.get("can_continue_after_manifested_routed_next_gate_result_continuation") is not True:
        reasons.append(
            "manifested_routed_next_gate_result_continuation_execute_result_review_cannot_continue"
        )
    if not result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if not result_review.get("routed_next_gate"):
        reasons.append("routed_next_gate_missing")
    if result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    reasons = []
    if result_review.get("this_command_ran_continuation") is True:
        reasons.append("result_review_ran_continuation")
    if result_review.get("selected_route_executed") is True:
        reasons.append("result_review_selected_route_executed")
    if result_review.get("export_or_acceptance_executed") is True:
        reasons.append("result_review_executed_export_or_acceptance")
    if result_review.get("formal_writeback_executed") is True:
        reasons.append("result_review_executed_formal_writeback")
    if result_review.get("this_command_wrote_formal_state") is True:
        reasons.append("result_review_wrote_formal_state")
    if result_review.get("can_write_product_state") is True:
        reasons.append("result_review_allows_product_state_write")
    for flag, value in result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_downstream_contract_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    route_type = result_review.get("verified_route_type", "")
    routed_next_gate = result_review.get("routed_next_gate", "")
    contract = DOWNSTREAM_CONTRACTS.get(routed_next_gate)
    if contract is None:
        return [f"routed_next_gate_unknown:{routed_next_gate}"]

    reasons = []
    if route_type not in contract["allowed_route_types"]:
        reasons.append(f"downstream_route_type_not_allowed:{route_type}")

    records = result_review.get(contract["record_key"], []) or []
    other_records = result_review.get(contract["other_record_key"], []) or []
    if other_records:
        reasons.append(f"unexpected_downstream_record_set:{contract['other_record_key']}")
    if not records:
        missing = (
            "selected_route_preflight_record_missing"
            if contract["record_key"] == "selected_route_execution_preflight_records"
            else "terminal_continuation_record_missing"
        )
        reasons.append(missing)
        return dedupe(reasons)
    if len(records) != 1:
        not_single = (
            "selected_route_preflight_record_not_single"
            if contract["record_key"] == "selected_route_execution_preflight_records"
            else "terminal_continuation_record_not_single"
        )
        reasons.append(not_single)
        return dedupe(reasons)

    record = records[0]
    if record.get("verified_route_type") != route_type:
        reasons.append(f"downstream_record_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != routed_next_gate:
        reasons.append(f"downstream_record_gate_mismatch:{routed_next_gate}")
    if record.get("review_status") != contract["review_status"]:
        reasons.append(f"downstream_record_not_accepted:{route_type}")
    if record.get(contract["continue_field"]) is not True:
        prefix = (
            "selected_route_downstream_record_cannot_continue"
            if contract["record_key"] == "selected_route_execution_preflight_records"
            else "terminal_downstream_record_cannot_continue"
        )
        reasons.append(f"{prefix}:{route_type}")

    if contract["record_key"] == "selected_route_execution_preflight_records":
        reasons.extend(build_selected_route_record_reasons(record, route_type))
    else:
        reasons.extend(build_terminal_record_reasons(record, route_type))
    return dedupe(reasons)


def build_selected_route_record_reasons(record: dict[str, Any], route_type: str) -> list[str]:
    route_contract = SELECTED_ROUTE_CONTRACTS.get(route_type, {})
    reasons = []
    if not route_contract:
        return [f"selected_route_contract_unknown:{route_type}"]
    if record.get("selected_route_preflight_status") != "ready_for_selected_formal_package_route_execution_review":
        reasons.append(f"selected_route_preflight_status_mismatch:{route_type}")
    if (
        record.get("selected_route_preflight_schema_version")
        != "p7.auto_mode_formal_package_selected_route_execution_preflight.v1"
    ):
        reasons.append(f"selected_route_preflight_schema_mismatch:{route_type}")
    if (
        record.get("selected_route_preflight_report_path")
        != "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
    ):
        reasons.append(f"selected_route_preflight_report_path_mismatch:{route_type}")
    if (
        record.get("selected_route_preflight_review_path")
        != "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md"
    ):
        reasons.append(f"selected_route_preflight_review_path_mismatch:{route_type}")
    if record.get("routed_action") != route_contract["routed_action"]:
        reasons.append(f"selected_route_record_routed_action_mismatch:{route_type}")
    if record.get("next_command") != route_contract["route_specific_next_command"]:
        reasons.append(f"selected_route_record_next_command_mismatch:{route_type}")
    if record.get("planned_outputs") != route_contract["planned_outputs"]:
        reasons.append(f"selected_route_record_outputs_mismatch:{route_type}")
    return reasons


def build_terminal_record_reasons(record: dict[str, Any], route_type: str) -> list[str]:
    reasons = []
    if record.get("terminal_status") != "terminal_delivery_completion_ready_for_product_review":
        reasons.append(f"terminal_downstream_record_status_mismatch:{route_type}")
    if record.get("terminal_report_path") != "Results/json/auto_mode_formal_package_delivery_completion_gate.json":
        reasons.append(f"terminal_downstream_record_report_path_mismatch:{route_type}")
    if record.get("terminal_review_path") != "Reviews/auto_mode_formal_package_delivery_completion_gate.md":
        reasons.append(f"terminal_downstream_record_review_path_mismatch:{route_type}")
    if record.get("next_command") != "product_review_preparation":
        reasons.append(f"terminal_downstream_record_next_command_mismatch:{route_type}")
    return reasons


def build_status(
    result_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if result_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_review"
    if boundary_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_boundary"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_contract"
    return READY_STATUS


def build_downstream_input_records(result_review: dict[str, Any]) -> list[dict[str, Any]]:
    route_type = result_review["verified_route_type"]
    routed_next_gate = result_review["routed_next_gate"]
    contract = DOWNSTREAM_CONTRACTS[routed_next_gate]
    source_record = result_review[contract["record_key"]][0]
    if contract["downstream_kind"] == "selected_route_execution":
        route_contract = SELECTED_ROUTE_CONTRACTS[route_type]
        source_report_path = source_record.get("selected_route_preflight_report_path", "")
        source_review_path = source_record.get("selected_route_preflight_review_path", "")
        route_specific_next_command = route_contract["route_specific_next_command"]
        planned_outputs = route_contract["planned_outputs"]
        terminal_status = ""
    else:
        source_report_path = source_record.get("terminal_report_path", "")
        source_review_path = source_record.get("terminal_review_path", "")
        route_specific_next_command = ""
        planned_outputs = []
        terminal_status = source_record.get("terminal_status", "")

    return [
        {
            "record_id": (
                "manifested_routed_continuation_execute_result_downstream::"
                f"{routed_next_gate}::{route_type}"
            ),
            "source_result_review_record_id": source_record.get("record_id", ""),
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "downstream_kind": contract["downstream_kind"],
            "downstream_command": contract["downstream_command"],
            "command_path": contract["command_path"],
            "route_specific_next_command": route_specific_next_command,
            "source_report_path": source_report_path,
            "source_review_path": source_review_path,
            "next_report_path": contract["next_report_path"],
            "next_review_path": contract["next_review_path"],
            "downstream_status": contract["downstream_status"],
            "terminal_status": terminal_status,
            "planned_outputs": planned_outputs,
            "requires_explicit_downstream_command": contract[
                "requires_explicit_downstream_command"
            ],
            "terminal_completion": contract["terminal_completion"],
            "will_run_downstream_command_by_this_command": False,
            "will_execute_selected_route_by_this_command": False,
            "will_execute_export_or_acceptance_by_this_command": False,
            "will_write_product_state_by_this_command": False,
        }
    ]


def build_source_result_review_summary(result_review: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": result_review.get("schema_version", ""),
        "status": result_review.get("status", ""),
        "verified_route_type": result_review.get("verified_route_type", ""),
        "routed_next_gate": result_review.get("routed_next_gate", ""),
        "continuation_execute_result_reviewed": (
            result_review.get("continuation_execute_result_reviewed") is True
        ),
        "can_continue_after_manifested_routed_next_gate_result_continuation": (
            result_review.get("can_continue_after_manifested_routed_next_gate_result_continuation")
            is True
        ),
        "selected_route_execution_preflight_records_count": len(
            result_review.get("selected_route_execution_preflight_records", []) or []
        ),
        "terminal_continuation_records_count": len(
            result_review.get("terminal_continuation_records", []) or []
        ),
        "source_blocking_reasons": result_review.get("blocking_reasons", []),
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
        "entered_continuation_execute_result_downstream_gate": False,
    }


def build_next_action(
    status: str,
    records: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == READY_STATUS and records:
        record = records[0]
        if record["downstream_kind"] == "product_review_preparation":
            return {
                "id": "prepare_product_review_from_terminal_continuation",
                "label": "Prepare product review",
                "description": "Terminal continuation downstream input is ready for product-review preparation.",
            }
        return {
            "id": "enter_manifested_continuation_selected_route_execution",
            "label": "Enter explicit selected-route execution",
            "description": "Selected-route execution downstream input is ready; execution remains explicit.",
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_review":
        return {
            "id": "resolve_p7_bh_result_review_blockers",
            "label": "Resolve P7-BH result review blockers",
            "description": "P7-BH must be ready before P7-BI can create downstream input.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_result_continuation_execute_result_downstream_boundary":
        return {
            "id": "remove_formal_action_from_p7_bh_result_review",
            "label": "Remove formal action from P7-BH input",
            "description": "P7-BI can only record a downstream entry; execution belongs to later explicit nodes.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "repair_p7_bh_downstream_record_contract",
        "label": "Repair P7-BH downstream record contract",
        "description": "P7-BH must expose exactly one clean downstream source record.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_outputs(
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Execute Result Downstream Gate Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- downstream kind：`{report['downstream_kind']}`",
        f"- downstream status：`{report['downstream_status']}`",
        f"- downstream gate entry 已记录：{str(report['downstream_gate_entry_recorded']).lower()}",
        "- 可请求 continuation downstream："
        f"{str(report['can_request_manifested_routed_next_gate_result_continuation_downstream']).lower()}",
        "- 需要显式 downstream command："
        f"{str(report['requires_explicit_downstream_command']).lower()}",
        f"- downstream input records：{len(report['downstream_input_records'])}",
        f"- 本命令运行 downstream command：{str(report['this_command_ran_downstream_command']).lower()}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if report["downstream_input_records"]:
        lines.extend(["", "## Downstream Input Records"])
        for record in report["downstream_input_records"]:
            lines.append(
                "- "
                f"`{record['record_id']}`: {record['downstream_kind']} "
                f"-> `{record['downstream_command']}`"
            )
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

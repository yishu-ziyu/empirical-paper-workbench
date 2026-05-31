from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.v1"
)
RESULT_REVIEW_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.v1"
)
RESULT_REVIEW_READY_STATUS = (
    "manifested_routed_next_gate_command_execute_gate_entry_result_review_ready"
)
READY_STATUS = "ready_for_manifested_routed_next_gate_command_result_continuation_gate_entry"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.json"
)
DEFAULT_GATE_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry.md"
)

CONTINUATION_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "delegated_schema_version": "p7.auto_mode_formal_package_export_acceptance_router.v1",
        "delegated_success_statuses": {"formal_package_export_acceptance_route_recorded"},
        "delegated_report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
        "delegated_review_path": "Reviews/auto_mode_formal_package_export_acceptance_router.md",
        "continuation_kind": "selected_route_execution_preflight",
        "next_command": "auto_mode_formal_package_selected_route_execution_preflight",
        "command_path": "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
        "next_report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
        "next_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
        "continuation_status": "pending_explicit_continuation_command",
        "requires_explicit_continuation_command": True,
        "completion_terminal": False,
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "delegated_schema_version": "p7.auto_mode_formal_package_delivery_completion_gate.v1",
        "delegated_success_statuses": {
            "formal_package_delivery_review_ready",
            "formal_package_delivery_completed",
        },
        "delegated_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
        "delegated_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
        "continuation_kind": "delivery_completion_terminal_record",
        "next_command": "none",
        "command_path": "",
        "next_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
        "next_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
        "continuation_status": "terminal_delivery_completion_ready_for_product_review",
        "requires_explicit_continuation_command": False,
        "completion_terminal": True,
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry(
    manifested_routed_next_gate_command_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    result_reasons = build_result_review_blocking_reasons(
        manifested_routed_next_gate_command_result_review
    )
    boundary_reasons = (
        build_boundary_blocking_reasons(manifested_routed_next_gate_command_result_review)
        if not result_reasons
        else []
    )
    contract_reasons = (
        build_continuation_contract_blocking_reasons(
            manifested_routed_next_gate_command_result_review
        )
        if not result_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(result_reasons + boundary_reasons + contract_reasons)
    status = build_status(result_reasons, boundary_reasons, contract_reasons)
    ready = status == READY_STATUS
    route_type = (
        manifested_routed_next_gate_command_result_review.get("verified_route_type", "")
        if ready
        else ""
    )
    routed_next_gate = (
        manifested_routed_next_gate_command_result_review.get("routed_next_gate", "")
        if ready
        else ""
    )
    records = (
        build_continuation_input_records(manifested_routed_next_gate_command_result_review)
        if ready
        else []
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": manifested_routed_next_gate_command_result_review.get("topic", ""),
        "source_paths": {
            "manifested_routed_next_gate_command_execute_gate_entry_result_review": (
                source_paths.get(
                    "manifested_routed_next_gate_command_execute_gate_entry_result_review",
                    str(DEFAULT_RESULT_REVIEW_PATH),
                )
            ),
        },
        "source_status": manifested_routed_next_gate_command_result_review.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "delegated_status": (
            manifested_routed_next_gate_command_result_review.get("delegated_status", "")
            if ready
            else ""
        ),
        "command_result_continuation_gate_entry_recorded": ready,
        "can_request_manifested_routed_next_gate_result_continuation": ready,
        "requires_explicit_continuation_command": any(
            record["requires_explicit_continuation_command"] for record in records
        ),
        "continuation_executed": False,
        "this_command_ran_continuation": False,
        "next_gate_command_executed": (
            manifested_routed_next_gate_command_result_review.get("next_gate_command_executed")
            is True
        ),
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "continuation_input_records": records,
        "blocking_reasons": blocking_reasons,
        "source_result_review": build_source_result_review_summary(
            manifested_routed_next_gate_command_result_review
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, records, blocking_reasons),
    }


def build_result_review_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    reasons = []
    if result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append(
            "manifested_routed_next_gate_command_result_review_missing_or_invalid_schema"
        )
    if result_review.get("status") != RESULT_REVIEW_READY_STATUS:
        reasons.append("manifested_routed_next_gate_command_result_review_not_ready")
    if result_review.get("command_execute_gate_entry_result_reviewed") is not True:
        reasons.append("manifested_routed_next_gate_command_result_not_reviewed")
    if result_review.get("can_continue_after_manifested_routed_next_gate_command") is not True:
        reasons.append("manifested_routed_next_gate_command_result_review_cannot_continue")
    if result_review.get("next_gate_command_executed") is not True:
        reasons.append("manifested_routed_next_gate_command_not_executed")
    if not result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if not result_review.get("routed_next_gate"):
        reasons.append("routed_next_gate_missing")
    if not result_review.get("delegated_status"):
        reasons.append("delegated_status_missing")
    if result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    reasons = []
    if result_review.get("this_command_ran_next_gate_command") is True:
        reasons.append("result_review_ran_next_gate_command")
    if result_review.get("this_command_entered_next_gate") is True:
        reasons.append("result_review_entered_next_gate")
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


def build_continuation_contract_blocking_reasons(result_review: dict[str, Any]) -> list[str]:
    route_type = result_review.get("verified_route_type", "")
    routed_next_gate = result_review.get("routed_next_gate", "")
    delegated_status = result_review.get("delegated_status", "")
    records = result_review.get("delegated_result_records", []) or []
    contract = CONTINUATION_CONTRACTS.get(routed_next_gate)
    reasons = []

    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{routed_next_gate}")
    else:
        if route_type not in contract["allowed_route_types"]:
            reasons.append(
                f"manifested_routed_result_continuation_route_type_not_allowed:{route_type}"
            )
        if delegated_status not in contract["delegated_success_statuses"]:
            reasons.append(
                f"manifested_routed_result_continuation_delegated_status_mismatch:{route_type}"
            )

    if len(records) != 1:
        reasons.append("delegated_result_record_missing" if not records else "delegated_result_record_not_single")
        return dedupe(reasons)

    record = records[0]
    if record.get("verified_route_type") != route_type:
        reasons.append(f"delegated_result_record_route_type_mismatch:{route_type}")
    if record.get("routed_next_gate") != routed_next_gate:
        reasons.append(f"delegated_result_record_gate_mismatch:{routed_next_gate}")
    if record.get("delegated_status") != delegated_status:
        reasons.append(f"delegated_result_record_status_mismatch:{route_type}")
    if record.get("review_status") != "delegated_next_gate_result_accepted_for_continuation":
        reasons.append(f"delegated_result_record_not_accepted:{route_type}")
    if record.get("can_continue_after_manifested_routed_next_gate_command") is not True:
        reasons.append(f"delegated_result_record_cannot_continue:{route_type}")

    if contract is not None:
        if record.get("delegated_schema_version") != contract["delegated_schema_version"]:
            reasons.append(f"delegated_result_record_schema_mismatch:{route_type}")
        if record.get("delegated_report_path") != contract["delegated_report_path"]:
            reasons.append(f"delegated_result_record_report_path_mismatch:{route_type}")
        if (
            record.get("delegated_review_path")
            and record.get("delegated_review_path") != contract["delegated_review_path"]
        ):
            reasons.append(f"delegated_result_record_review_path_mismatch:{route_type}")
    return dedupe(reasons)


def build_status(
    result_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if result_reasons:
        return "blocked_by_manifested_routed_next_gate_command_result_review"
    if boundary_reasons:
        return "blocked_by_manifested_routed_next_gate_command_result_continuation_boundary"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_command_result_continuation_contract"
    return READY_STATUS


def build_continuation_input_records(result_review: dict[str, Any]) -> list[dict[str, Any]]:
    route_type = result_review["verified_route_type"]
    routed_next_gate = result_review["routed_next_gate"]
    delegated_record = result_review["delegated_result_records"][0]
    contract = CONTINUATION_CONTRACTS[routed_next_gate]
    return [
        {
            "record_id": (
                "manifested_routed_next_gate_command_result_continuation::"
                f"{routed_next_gate}::{route_type}"
            ),
            "source_delegated_result_record_id": delegated_record.get("record_id", ""),
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "delegated_status": result_review.get("delegated_status", ""),
            "delegated_schema_version": delegated_record.get("delegated_schema_version", ""),
            "source_report_path": contract["delegated_report_path"],
            "source_review_path": contract["delegated_review_path"],
            "continuation_kind": contract["continuation_kind"],
            "next_command": contract["next_command"],
            "command_path": contract["command_path"],
            "next_report_path": contract["next_report_path"],
            "next_review_path": contract["next_review_path"],
            "continuation_status": contract["continuation_status"],
            "requires_explicit_continuation_command": contract[
                "requires_explicit_continuation_command"
            ],
            "completion_terminal": contract["completion_terminal"],
            "will_run_continuation_by_this_command": False,
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
        "delegated_status": result_review.get("delegated_status", ""),
        "command_execute_gate_entry_result_reviewed": (
            result_review.get("command_execute_gate_entry_result_reviewed") is True
        ),
        "can_continue_after_manifested_routed_next_gate_command": (
            result_review.get("can_continue_after_manifested_routed_next_gate_command") is True
        ),
        "delegated_result_records_count": len(result_review.get("delegated_result_records", []) or []),
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
        "entered_explicit_routed_next_gate_entry": False,
        "ran_manifested_routed_next_gate_command": False,
        "reviewed_manifested_routed_next_gate_command_result": False,
        "recorded_manifested_routed_next_gate_command_result_continuation": False,
    }


def build_next_action(
    status: str,
    records: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == READY_STATUS and records and records[0]["completion_terminal"]:
        return {
            "id": "review_terminal_delivery_completion",
            "label": "Review terminal delivery completion",
            "description": "The delivery completion result is ready for product-level review; this command did not write product state.",
        }
    if status == READY_STATUS:
        return {
            "id": records[0]["next_command"],
            "label": "Run explicit continuation command",
            "description": "A later command may continue into the selected route execution preflight; this command did not run it.",
        }
    if status == "blocked_by_manifested_routed_next_gate_command_result_continuation_contract":
        return {
            "id": "repair_manifested_routed_next_gate_command_result_continuation_contract",
            "label": "Repair continuation contract",
            "description": "P7-BF needs one consistent delegated result record for a known continuation.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_result_continuation_boundary":
        return {
            "id": "resolve_manifested_routed_next_gate_command_result_continuation_boundary",
            "label": "Resolve continuation boundary violation",
            "description": "P7-BF cannot consume a P7-BE result review with unsafe side-effect signals.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_manifested_routed_next_gate_command_result_review_blockers",
        "label": "Resolve P7-BE blockers",
        "description": "P7-BE must accept the delegated result before continuation input can be prepared.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_gate_entry_outputs(
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Result Continuation Gate Entry",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- delegated 状态：`{report['delegated_status']}`",
        "- continuation gate entry 已记录："
        f"{str(report['command_result_continuation_gate_entry_recorded']).lower()}",
        "- 可请求 manifested routed next gate result continuation："
        f"{str(report['can_request_manifested_routed_next_gate_result_continuation']).lower()}",
        "- 需要显式 continuation command："
        f"{str(report['requires_explicit_continuation_command']).lower()}",
        f"- continuation input records：{len(report['continuation_input_records'])}",
        f"- 已运行 continuation：{str(report['continuation_executed']).lower()}",
        f"- 本命令运行 continuation：{str(report['this_command_ran_continuation']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if report["continuation_input_records"]:
        lines.extend(["", "## Continuation Input Records"])
        for record in report["continuation_input_records"]:
            lines.append(
                "- "
                f"`{record['record_id']}`: {record['continuation_status']} "
                f"({record['next_command']})"
            )
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped

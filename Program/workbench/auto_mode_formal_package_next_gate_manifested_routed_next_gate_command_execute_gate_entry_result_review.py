from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.v1"
)
GATE_ENTRY_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.v1"
)
GATE_ENTRY_SUCCESS_STATUS = "manifested_routed_next_gate_command_execute_gate_entry_executed"
DEFAULT_GATE_ENTRY_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry.json"
)
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review.md"
)

DELEGATED_NEXT_GATE_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "schema_version": "p7.auto_mode_formal_package_export_acceptance_router.v1",
        "success_statuses": {"formal_package_export_acceptance_route_recorded"},
        "delegated_report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
        "delegated_review_path": "Reviews/auto_mode_formal_package_export_acceptance_router.md",
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "schema_version": "p7.auto_mode_formal_package_delivery_completion_gate.v1",
        "success_statuses": {
            "formal_package_delivery_review_ready",
            "formal_package_delivery_completed",
        },
        "delegated_report_path": "Results/json/auto_mode_formal_package_delivery_completion_gate.json",
        "delegated_review_path": "Reviews/auto_mode_formal_package_delivery_completion_gate.md",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(
    manifested_routed_next_gate_command_execute_gate_entry: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    gate_reasons = build_gate_entry_blocking_reasons(
        manifested_routed_next_gate_command_execute_gate_entry
    )
    boundary_reasons = (
        build_boundary_blocking_reasons(manifested_routed_next_gate_command_execute_gate_entry)
        if not gate_reasons
        else []
    )
    contract_reasons = (
        build_contract_blocking_reasons(manifested_routed_next_gate_command_execute_gate_entry)
        if not gate_reasons and not boundary_reasons
        else []
    )
    delegated_reasons = (
        build_delegated_result_blocking_reasons(manifested_routed_next_gate_command_execute_gate_entry)
        if not gate_reasons and not boundary_reasons and not contract_reasons
        else []
    )
    blocking_reasons = dedupe(gate_reasons + boundary_reasons + contract_reasons + delegated_reasons)
    status = build_status(gate_reasons, boundary_reasons, contract_reasons, delegated_reasons)
    ready = status == "manifested_routed_next_gate_command_execute_gate_entry_result_review_ready"
    route_type = (
        manifested_routed_next_gate_command_execute_gate_entry.get("verified_route_type", "")
        if not gate_reasons and not boundary_reasons and not contract_reasons
        else ""
    )
    routed_next_gate = (
        manifested_routed_next_gate_command_execute_gate_entry.get("routed_next_gate", "")
        if not gate_reasons and not boundary_reasons and not contract_reasons
        else ""
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": manifested_routed_next_gate_command_execute_gate_entry.get("topic", ""),
        "source_paths": {
            "manifested_routed_next_gate_command_execute_gate_entry": source_paths.get(
                "manifested_routed_next_gate_command_execute_gate_entry",
                str(DEFAULT_GATE_ENTRY_PATH),
            ),
        },
        "source_status": manifested_routed_next_gate_command_execute_gate_entry.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "delegated_status": (
            manifested_routed_next_gate_command_execute_gate_entry.get("delegated_status", "")
            if ready
            else ""
        ),
        "command_execute_gate_entry_result_reviewed": ready,
        "can_continue_after_manifested_routed_next_gate_command": ready,
        "next_gate_command_executed": (
            manifested_routed_next_gate_command_execute_gate_entry.get("next_gate_command_executed") is True
        ),
        "this_command_ran_next_gate_command": False,
        "next_gate_entered": (
            manifested_routed_next_gate_command_execute_gate_entry.get("next_gate_entered") is True
        ),
        "this_command_entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "delegated_result_records": (
            build_delegated_result_records(manifested_routed_next_gate_command_execute_gate_entry)
            if ready
            else []
        ),
        "blocking_reasons": blocking_reasons,
        "source_command_execute_gate_entry": build_source_gate_entry_summary(
            manifested_routed_next_gate_command_execute_gate_entry
        ),
        "source_delegated_result": build_source_delegated_result_summary(
            manifested_routed_next_gate_command_execute_gate_entry
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_gate_entry_blocking_reasons(
    gate_entry: dict[str, Any],
) -> list[str]:
    reasons = []
    if gate_entry.get("schema_version") != GATE_ENTRY_SCHEMA_VERSION:
        reasons.append("command_execute_gate_entry_missing_or_invalid_schema")
    if gate_entry.get("status") != GATE_ENTRY_SUCCESS_STATUS:
        reasons.append("command_execute_gate_entry_not_completed")
    if gate_entry.get("command_execute_gate_entry_executed") is not True:
        reasons.append("command_execute_gate_entry_not_executed")
    if gate_entry.get("manifested_command_execute_status") != "manifested_next_gate_command_executed":
        reasons.append("manifested_command_execute_not_completed")
    if gate_entry.get("next_gate_command_executed") is not True:
        reasons.append("next_gate_command_not_executed")
    if gate_entry.get("this_command_ran_next_gate_command") is not True:
        reasons.append("source_command_did_not_run_next_gate_command")
    for field in ["verified_route_type", "routed_next_gate", "delegated_report_path"]:
        if not gate_entry.get(field):
            reasons.append(f"{field}_missing")
    if gate_entry.get("blocking_reasons"):
        reasons.append("source_command_execute_gate_entry_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(gate_entry: dict[str, Any]) -> list[str]:
    reasons = []
    if gate_entry.get("formal_writeback_executed") is True:
        reasons.append("command_execute_gate_entry_executed_formal_writeback")
    if gate_entry.get("this_command_wrote_formal_state") is True:
        reasons.append("command_execute_gate_entry_wrote_formal_state")
    if gate_entry.get("can_write_product_state") is True:
        reasons.append("command_execute_gate_entry_allows_product_state_write")
    if gate_entry.get("export_or_acceptance_executed") is True:
        reasons.append("command_execute_gate_entry_executed_export_or_acceptance")
    for flag, value in gate_entry.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"command_execute_gate_entry_boundary_violation:{flag}")
    return dedupe(reasons)


def build_contract_blocking_reasons(gate_entry: dict[str, Any]) -> list[str]:
    route_type = gate_entry.get("verified_route_type", "unknown")
    routed_next_gate = gate_entry.get("routed_next_gate", "")
    contract = DELEGATED_NEXT_GATE_CONTRACTS.get(routed_next_gate)
    if contract is None:
        return [f"routed_next_gate_unknown:{routed_next_gate}"]

    reasons = []
    if route_type not in contract["allowed_route_types"]:
        reasons.append(f"delegated_next_gate_route_type_not_allowed:{route_type}")
    if gate_entry.get("delegated_returncode") != 0:
        reasons.append("delegated_returncode_not_zero")
    if not gate_entry.get("delegated_status"):
        reasons.append("delegated_status_missing")
    elif gate_entry.get("delegated_status") not in contract["success_statuses"]:
        reasons.append(f"delegated_status_not_success:{route_type}")
    if gate_entry.get("delegated_report_path") != contract["delegated_report_path"]:
        reasons.append(f"delegated_report_path_mismatch:{route_type}")
    if gate_entry.get("delegated_review_path") != contract["delegated_review_path"]:
        reasons.append(f"delegated_review_path_mismatch:{route_type}")

    delegated_result = gate_entry.get("delegated_result", {})
    if delegated_result.get("returncode") not in (None, 0):
        reasons.append("delegated_result_returncode_not_zero")
    if delegated_result.get("status") and delegated_result.get("status") != gate_entry.get("delegated_status"):
        reasons.append(f"delegated_result_status_mismatch:{route_type}")
    if delegated_result.get("report_path") and delegated_result.get("report_path") != contract["delegated_report_path"]:
        reasons.append(f"delegated_result_report_path_mismatch:{route_type}")
    if delegated_result.get("review_path") and delegated_result.get("review_path") != contract["delegated_review_path"]:
        reasons.append(f"delegated_result_review_path_mismatch:{route_type}")
    return dedupe(reasons)


def build_delegated_result_blocking_reasons(gate_entry: dict[str, Any]) -> list[str]:
    route_type = gate_entry.get("verified_route_type", "unknown")
    contract = DELEGATED_NEXT_GATE_CONTRACTS.get(gate_entry.get("routed_next_gate", ""), {})
    delegated_result = gate_entry.get("delegated_result", {})
    summary = delegated_result.get("delegated_report_summary", {})
    reasons = []
    if not summary:
        return [f"delegated_result_summary_missing:{route_type}"]
    if summary.get("schema_version") != contract.get("schema_version"):
        reasons.append(f"delegated_result_summary_schema_mismatch:{route_type}")
    if summary.get("status") not in contract.get("success_statuses", set()):
        reasons.append(f"delegated_result_summary_status_not_success:{route_type}")
    if summary.get("blocking_reasons"):
        reasons.append(f"delegated_result_summary_has_blocking_reasons:{route_type}")
    return dedupe(reasons)


def build_status(
    gate_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
    delegated_reasons: list[str],
) -> str:
    if gate_reasons:
        return "blocked_by_manifested_routed_next_gate_command_execute_gate_entry"
    if boundary_reasons:
        return "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_boundary"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_result_contract"
    if delegated_reasons:
        return "blocked_by_delegated_next_gate_result"
    return "manifested_routed_next_gate_command_execute_gate_entry_result_review_ready"


def build_delegated_result_records(gate_entry: dict[str, Any]) -> list[dict[str, Any]]:
    route_type = gate_entry.get("verified_route_type", "")
    routed_next_gate = gate_entry.get("routed_next_gate", "")
    delegated_result = gate_entry.get("delegated_result", {})
    summary = delegated_result.get("delegated_report_summary", {})
    return [
        {
            "record_id": f"manifested_routed_next_gate_command_result::{routed_next_gate}::{route_type}",
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "delegated_status": gate_entry.get("delegated_status", ""),
            "delegated_schema_version": summary.get("schema_version", ""),
            "delegated_report_path": gate_entry.get("delegated_report_path", ""),
            "delegated_review_path": gate_entry.get("delegated_review_path", ""),
            "review_status": "delegated_next_gate_result_accepted_for_continuation",
            "can_continue_after_manifested_routed_next_gate_command": True,
        }
    ]


def build_source_gate_entry_summary(gate_entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": gate_entry.get("schema_version", ""),
        "status": gate_entry.get("status", ""),
        "verified_route_type": gate_entry.get("verified_route_type", ""),
        "routed_next_gate": gate_entry.get("routed_next_gate", ""),
        "command_execute_gate_entry_executed": gate_entry.get("command_execute_gate_entry_executed") is True,
        "manifested_command_execute_status": gate_entry.get("manifested_command_execute_status", ""),
        "delegated_returncode": gate_entry.get("delegated_returncode"),
        "delegated_status": gate_entry.get("delegated_status", ""),
        "delegated_report_path": gate_entry.get("delegated_report_path", ""),
        "delegated_review_path": gate_entry.get("delegated_review_path", ""),
        "blocking_reasons": gate_entry.get("blocking_reasons", []),
        "boundary_flags": gate_entry.get("boundary_flags", {}),
    }


def build_source_delegated_result_summary(gate_entry: dict[str, Any]) -> dict[str, Any]:
    delegated_result = gate_entry.get("delegated_result", {})
    return {
        "returncode": delegated_result.get("returncode"),
        "status": delegated_result.get("status", ""),
        "report_path": delegated_result.get("report_path", ""),
        "review_path": delegated_result.get("review_path", ""),
        "delegated_report_summary": delegated_result.get("delegated_report_summary", {}),
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
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "manifested_routed_next_gate_command_execute_gate_entry_result_review_ready":
        return {
            "id": "continue_after_manifested_routed_next_gate_command",
            "label": "Continue after manifested routed next-gate command",
            "description": "The delegated next-gate result is accepted for continuation.",
        }
    if status == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_boundary":
        return {
            "id": "resolve_manifested_routed_next_gate_command_result_boundary",
            "label": "Resolve command result boundary",
            "description": "P7-BE cannot continue from a gate entry result with unsafe boundary signals.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_execute_gate_entry_result_contract":
        return {
            "id": "repair_manifested_routed_next_gate_command_result_contract",
            "label": "Repair delegated command result contract",
            "description": "P7-BD must report a successful delegated command result with matching paths and status.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_delegated_next_gate_result":
        return {
            "id": "repair_delegated_next_gate_result_summary",
            "label": "Repair delegated next-gate result summary",
            "description": "The delegated result summary must expose a valid success schema and no blockers.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_manifested_routed_next_gate_command_execute_gate_entry_blockers",
        "label": "Resolve P7-BD blockers",
        "description": "P7-BD must complete before P7-BE can review the delegated command result.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Command Execute Gate Entry Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        f"- delegated 状态：`{report['delegated_status']}`",
        "- command execute gate entry result 已审阅："
        f"{str(report['command_execute_gate_entry_result_reviewed']).lower()}",
        "- 可继续 manifested routed next gate command 后续流程："
        f"{str(report['can_continue_after_manifested_routed_next_gate_command']).lower()}",
        f"- delegated result records：{len(report['delegated_result_records'])}",
        f"- 本命令运行下一关命令：{str(report['this_command_ran_next_gate_command']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if report["delegated_result_records"]:
        lines.extend(["", "## Delegated Result Records"])
        for record in report["delegated_result_records"]:
            lines.append(
                "- "
                f"`{record['record_id']}`: {record['review_status']} "
                f"({record['delegated_report_path']})"
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

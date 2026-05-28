from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_manifested_next_gate_command_result_review.v1"
EXECUTE_SCHEMA_VERSION = "p7.auto_mode_formal_package_manifested_routed_next_gate_command_execute.v1"
DEFAULT_EXECUTE_PATH = Path(
    "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json"
)
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_manifested_next_gate_command_result_review.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_manifested_next_gate_command_result_review.md")

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


def build_auto_mode_formal_package_manifested_next_gate_command_result_review(
    project_root: Path,
    manifested_next_gate_command_execute: dict[str, Any],
    delegated_report: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    execute_reasons = build_execute_blocking_reasons(manifested_next_gate_command_execute)
    contract_reasons = (
        build_contract_blocking_reasons(manifested_next_gate_command_execute, delegated_report)
        if not execute_reasons
        else []
    )
    delegated_reasons = (
        build_delegated_report_blocking_reasons(manifested_next_gate_command_execute, delegated_report)
        if not execute_reasons and not contract_reasons
        else []
    )
    blocking_reasons = dedupe(execute_reasons + contract_reasons + delegated_reasons)
    status = build_status(execute_reasons, contract_reasons, delegated_reasons)
    ready = status == "manifested_next_gate_command_result_review_ready"
    route_type = (
        manifested_next_gate_command_execute.get("verified_route_type", "")
        if not execute_reasons and not contract_reasons
        else ""
    )
    routed_next_gate = (
        manifested_next_gate_command_execute.get("routed_next_gate", "")
        if not execute_reasons and not contract_reasons
        else ""
    )
    delegated_status = delegated_report.get("status", "") if ready else ""

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": manifested_next_gate_command_execute.get("topic", delegated_report.get("topic", "")),
        "source_paths": {
            "manifested_next_gate_command_execute": source_paths.get(
                "manifested_next_gate_command_execute",
                str(DEFAULT_EXECUTE_PATH),
            ),
            "delegated_report": source_paths.get(
                "delegated_report",
                manifested_next_gate_command_execute.get("delegated_report_path", ""),
            ),
        },
        "source_status": manifested_next_gate_command_execute.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "delegated_status": delegated_status,
        "delegated_next_gate_result_reviewed": ready,
        "can_continue_after_delegated_next_gate": ready,
        "next_gate_command_executed": (
            manifested_next_gate_command_execute.get("next_gate_command_executed") is True
        ),
        "this_command_ran_next_gate_command": False,
        "next_gate_entered": manifested_next_gate_command_execute.get("next_gate_entered") is True,
        "this_command_entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "delegated_result_records": (
            build_delegated_result_records(manifested_next_gate_command_execute, delegated_report)
            if ready
            else []
        ),
        "blocking_reasons": blocking_reasons,
        "source_execute": build_source_execute_summary(manifested_next_gate_command_execute),
        "source_delegated_report": build_source_delegated_report_summary(delegated_report),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_execute_blocking_reasons(
    manifested_next_gate_command_execute: dict[str, Any],
) -> list[str]:
    reasons = []
    if manifested_next_gate_command_execute.get("schema_version") != EXECUTE_SCHEMA_VERSION:
        reasons.append("manifested_next_gate_command_execute_missing_or_invalid_schema")
    if manifested_next_gate_command_execute.get("status") != "manifested_next_gate_command_executed":
        reasons.append("manifested_next_gate_command_execute_not_completed")
    if manifested_next_gate_command_execute.get("next_gate_command_executed") is not True:
        reasons.append("next_gate_command_not_executed")
    if manifested_next_gate_command_execute.get("this_command_ran_next_gate_command") is not True:
        reasons.append("this_command_did_not_run_next_gate_command")
    if manifested_next_gate_command_execute.get("delegated_returncode") != 0:
        reasons.append("delegated_returncode_not_zero")
    for field in [
        "verified_route_type",
        "routed_next_gate",
        "delegated_report_path",
        "delegated_status",
    ]:
        if not manifested_next_gate_command_execute.get(field):
            reasons.append(f"{field}_missing")
    if manifested_next_gate_command_execute.get("this_command_wrote_formal_state") is True:
        reasons.append("manifested_next_gate_command_execute_wrote_formal_state")
    if manifested_next_gate_command_execute.get("can_write_product_state") is True:
        reasons.append("manifested_next_gate_command_execute_allows_product_state_write")
    if manifested_next_gate_command_execute.get("blocking_reasons"):
        reasons.append("source_execute_has_blocking_reasons")
    for flag, value in manifested_next_gate_command_execute.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"manifested_next_gate_command_execute_boundary_violation:{flag}")
    return dedupe(reasons)


def build_contract_blocking_reasons(
    manifested_next_gate_command_execute: dict[str, Any],
    delegated_report: dict[str, Any],
) -> list[str]:
    route_type = manifested_next_gate_command_execute.get("verified_route_type", "unknown")
    routed_next_gate = manifested_next_gate_command_execute.get("routed_next_gate", "")
    contract = DELEGATED_NEXT_GATE_CONTRACTS.get(routed_next_gate)
    if contract is None:
        return [f"routed_next_gate_unknown:{routed_next_gate}"]

    reasons = []
    if route_type not in contract["allowed_route_types"]:
        reasons.append(f"delegated_next_gate_route_type_not_allowed:{route_type}")
    if manifested_next_gate_command_execute.get("delegated_report_path") != contract["delegated_report_path"]:
        reasons.append(f"delegated_report_path_mismatch:{route_type}")
    delegated_review_path = manifested_next_gate_command_execute.get("delegated_review_path", "")
    if delegated_review_path and delegated_review_path != contract["delegated_review_path"]:
        reasons.append(f"delegated_review_path_mismatch:{route_type}")

    delegated_result = manifested_next_gate_command_execute.get("delegated_result", {})
    if delegated_result.get("report_path") and delegated_result.get("report_path") != contract["delegated_report_path"]:
        reasons.append(f"delegated_result_report_path_mismatch:{route_type}")
    if delegated_result.get("review_path") and delegated_result.get("review_path") != contract["delegated_review_path"]:
        reasons.append(f"delegated_result_review_path_mismatch:{route_type}")

    execute_delegated_status = manifested_next_gate_command_execute.get("delegated_status", "")
    delegated_report_status = delegated_report.get("status", "")
    if (
        delegated_report_status in contract["success_statuses"]
        and execute_delegated_status != delegated_report_status
    ):
        reasons.append(f"delegated_status_mismatch:{route_type}")
    if delegated_result.get("status") and delegated_result.get("status") != execute_delegated_status:
        reasons.append(f"delegated_result_status_mismatch:{route_type}")
    return dedupe(reasons)


def build_delegated_report_blocking_reasons(
    manifested_next_gate_command_execute: dict[str, Any],
    delegated_report: dict[str, Any],
) -> list[str]:
    route_type = manifested_next_gate_command_execute.get("verified_route_type", "unknown")
    routed_next_gate = manifested_next_gate_command_execute.get("routed_next_gate", "")
    contract = DELEGATED_NEXT_GATE_CONTRACTS.get(routed_next_gate, {})
    reasons = []
    if delegated_report.get("schema_version") != contract.get("schema_version"):
        reasons.append(f"delegated_next_gate_report_missing_or_invalid_schema:{route_type}")
    if delegated_report.get("status") not in contract.get("success_statuses", set()):
        reasons.append(f"delegated_next_gate_status_not_success:{route_type}")
    if delegated_report.get("blocking_reasons"):
        reasons.append(f"delegated_next_gate_report_has_blocking_reasons:{route_type}")
    if routed_next_gate == "formal_package_export_acceptance_router":
        if delegated_report.get("route_recorded") is not True:
            reasons.append(f"delegated_export_acceptance_route_not_recorded:{route_type}")
        if delegated_report.get("can_route_export_or_acceptance") is not True:
            reasons.append(f"delegated_export_acceptance_cannot_route:{route_type}")
        if delegated_report.get("export_or_acceptance_executed") is True:
            reasons.append(f"delegated_export_acceptance_executed_boundary_violation:{route_type}")
    if delegated_report.get("this_command_wrote_formal_state") is True:
        reasons.append(f"delegated_next_gate_report_wrote_formal_state:{route_type}")
    if delegated_report.get("can_write_product_state") is True:
        reasons.append(f"delegated_next_gate_report_allows_product_state_write:{route_type}")
    for flag, value in delegated_report.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"delegated_next_gate_report_boundary_violation:{flag}")
    return dedupe(reasons)


def build_status(
    execute_reasons: list[str],
    contract_reasons: list[str],
    delegated_reasons: list[str],
) -> str:
    if execute_reasons:
        return "blocked_by_manifested_next_gate_command_execute"
    if contract_reasons:
        return "blocked_by_manifested_next_gate_command_result_contract"
    if delegated_reasons:
        return "blocked_by_delegated_next_gate_report"
    return "manifested_next_gate_command_result_review_ready"


def build_delegated_result_records(
    manifested_next_gate_command_execute: dict[str, Any],
    delegated_report: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = manifested_next_gate_command_execute.get("verified_route_type", "")
    routed_next_gate = manifested_next_gate_command_execute.get("routed_next_gate", "")
    return [
        {
            "record_id": f"manifested_next_gate_result::{routed_next_gate}::{route_type}",
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "delegated_status": delegated_report.get("status", ""),
            "delegated_schema_version": delegated_report.get("schema_version", ""),
            "delegated_report_path": manifested_next_gate_command_execute.get("delegated_report_path", ""),
            "delegated_review_path": manifested_next_gate_command_execute.get("delegated_review_path", ""),
            "review_status": "delegated_next_gate_result_accepted_for_continuation",
            "can_continue_after_delegated_next_gate": True,
        }
    ]


def build_source_execute_summary(manifested_next_gate_command_execute: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": manifested_next_gate_command_execute.get("schema_version", ""),
        "status": manifested_next_gate_command_execute.get("status", ""),
        "verified_route_type": manifested_next_gate_command_execute.get("verified_route_type", ""),
        "routed_next_gate": manifested_next_gate_command_execute.get("routed_next_gate", ""),
        "delegated_report_path": manifested_next_gate_command_execute.get("delegated_report_path", ""),
        "delegated_review_path": manifested_next_gate_command_execute.get("delegated_review_path", ""),
        "delegated_returncode": manifested_next_gate_command_execute.get("delegated_returncode"),
        "delegated_status": manifested_next_gate_command_execute.get("delegated_status", ""),
        "source_blocking_reasons": manifested_next_gate_command_execute.get("blocking_reasons", []),
        "boundary_flags": manifested_next_gate_command_execute.get("boundary_flags", {}),
    }


def build_source_delegated_report_summary(delegated_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": delegated_report.get("schema_version", ""),
        "status": delegated_report.get("status", ""),
        "blocking_reasons": delegated_report.get("blocking_reasons", []),
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
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "manifested_next_gate_command_result_review_ready":
        return {
            "id": "continue_after_delegated_next_gate",
            "label": "Continue after delegated next-gate result",
            "description": "The delegated next-gate output is accepted for continuation.",
        }
    if status == "blocked_by_manifested_next_gate_command_execute":
        return {
            "id": "resolve_manifested_next_gate_command_execute_blockers",
            "label": "Resolve P7-AI execute blockers",
            "description": "P7-AI must complete a delegated next-gate command before result review can continue.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_next_gate_command_result_contract":
        return {
            "id": "repair_manifested_next_gate_result_contract",
            "label": "Repair delegated result contract",
            "description": "The executed next-gate route, report path, or delegated status does not match contract.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "repair_delegated_next_gate_report",
        "label": "Repair delegated next-gate report",
        "description": "The delegated report must expose a valid schema, success status, and clean boundary flags.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_manifested_next_gate_command_result_review_outputs(
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
        "# Auto Mode Formal Package Manifested Next Gate Command Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        f"- delegated 状态：`{report['delegated_status']}`",
        f"- 已审阅 delegated 结果：{str(report['delegated_next_gate_result_reviewed']).lower()}",
        f"- 可继续下一关后续流程：{str(report['can_continue_after_delegated_next_gate']).lower()}",
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

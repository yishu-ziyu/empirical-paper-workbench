from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_workflow_continuation_preflight.v1"
RESULT_REVIEW_SCHEMA_VERSION = "p7.auto_mode_formal_package_manifested_next_gate_command_result_review.v1"
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_manifested_next_gate_command_result_review.json"
)
DEFAULT_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_next_gate_workflow_continuation_preflight.md")

CONTINUATION_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "delegated_schema_version": "p7.auto_mode_formal_package_export_acceptance_router.v1",
        "delegated_status": "formal_package_export_acceptance_route_recorded",
        "delegated_report_path": "Results/json/auto_mode_formal_package_export_acceptance_router.json",
        "delegated_review_path": "Reviews/auto_mode_formal_package_export_acceptance_router.md",
        "next_command": "auto_mode_formal_package_selected_route_execution_preflight",
        "command_path": "Program/auto_mode_formal_package_selected_route_execution_preflight.py",
        "next_report_path": "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json",
        "next_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
        "continuation_kind": "selected_route_execution_preflight",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(
    manifested_next_gate_command_result_review: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    result_reasons = build_result_review_blocking_reasons(manifested_next_gate_command_result_review)
    boundary_reasons = (
        build_boundary_blocking_reasons(manifested_next_gate_command_result_review)
        if not result_reasons
        else []
    )
    contract_reasons = (
        build_continuation_contract_blocking_reasons(manifested_next_gate_command_result_review)
        if not result_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(result_reasons + boundary_reasons + contract_reasons)
    status = build_status(result_reasons, boundary_reasons, contract_reasons)
    ready = status == "ready_for_next_gate_workflow_continuation_review"
    route_type = manifested_next_gate_command_result_review.get("verified_route_type", "") if ready else ""
    routed_next_gate = manifested_next_gate_command_result_review.get("routed_next_gate", "") if ready else ""
    plan = (
        build_workflow_continuation_plan(manifested_next_gate_command_result_review)
        if ready
        else []
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": manifested_next_gate_command_result_review.get("topic", ""),
        "source_paths": {
            "manifested_next_gate_command_result_review": source_paths.get(
                "manifested_next_gate_command_result_review",
                str(DEFAULT_RESULT_REVIEW_PATH),
            ),
        },
        "source_status": manifested_next_gate_command_result_review.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "can_request_next_gate_workflow_continuation": ready,
        "requires_explicit_workflow_continuation_command": ready,
        "workflow_continuation_executed": False,
        "this_command_ran_continuation": False,
        "next_gate_command_executed": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_result_review": build_source_result_review_summary(
            manifested_next_gate_command_result_review
        ),
        "workflow_continuation_plan": plan,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, plan, blocking_reasons),
    }


def build_result_review_blocking_reasons(
    manifested_next_gate_command_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    if manifested_next_gate_command_result_review.get("schema_version") != RESULT_REVIEW_SCHEMA_VERSION:
        reasons.append("manifested_next_gate_command_result_review_missing_or_invalid_schema")
    if (
        manifested_next_gate_command_result_review.get("status")
        != "manifested_next_gate_command_result_review_ready"
    ):
        reasons.append("manifested_next_gate_command_result_review_not_ready")
    if manifested_next_gate_command_result_review.get("delegated_next_gate_result_reviewed") is not True:
        reasons.append("manifested_next_gate_result_not_reviewed")
    if manifested_next_gate_command_result_review.get("can_continue_after_delegated_next_gate") is not True:
        reasons.append("manifested_next_gate_result_review_cannot_continue")
    if manifested_next_gate_command_result_review.get("next_gate_command_executed") is not True:
        reasons.append("manifested_next_gate_command_not_executed")
    if not manifested_next_gate_command_result_review.get("verified_route_type"):
        reasons.append("verified_route_type_missing")
    if not manifested_next_gate_command_result_review.get("routed_next_gate"):
        reasons.append("routed_next_gate_missing")
    if not manifested_next_gate_command_result_review.get("delegated_status"):
        reasons.append("delegated_status_missing")
    if manifested_next_gate_command_result_review.get("blocking_reasons"):
        reasons.append("source_result_review_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(
    manifested_next_gate_command_result_review: dict[str, Any],
) -> list[str]:
    reasons = []
    if manifested_next_gate_command_result_review.get("this_command_ran_next_gate_command") is True:
        reasons.append("result_review_ran_next_gate_command")
    if manifested_next_gate_command_result_review.get("this_command_entered_next_gate") is True:
        reasons.append("result_review_entered_next_gate")
    if manifested_next_gate_command_result_review.get("export_or_acceptance_executed") is True:
        reasons.append("result_review_executed_export_or_acceptance")
    if manifested_next_gate_command_result_review.get("formal_writeback_executed") is True:
        reasons.append("result_review_executed_formal_writeback")
    if manifested_next_gate_command_result_review.get("this_command_wrote_formal_state") is True:
        reasons.append("result_review_wrote_formal_state")
    if manifested_next_gate_command_result_review.get("can_write_product_state") is True:
        reasons.append("result_review_allows_product_state_write")
    for flag, value in manifested_next_gate_command_result_review.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"result_review_boundary_violation:{flag}")
    return dedupe(reasons)


def build_continuation_contract_blocking_reasons(
    manifested_next_gate_command_result_review: dict[str, Any],
) -> list[str]:
    route_type = manifested_next_gate_command_result_review.get("verified_route_type", "")
    routed_next_gate = manifested_next_gate_command_result_review.get("routed_next_gate", "")
    delegated_status = manifested_next_gate_command_result_review.get("delegated_status", "")
    records = manifested_next_gate_command_result_review.get("delegated_result_records", []) or []
    contract = CONTINUATION_CONTRACTS.get(routed_next_gate)
    reasons = []
    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{routed_next_gate}")
    else:
        if route_type not in contract["allowed_route_types"]:
            reasons.append(f"workflow_continuation_route_type_not_allowed:{route_type}")
        if delegated_status != contract["delegated_status"]:
            reasons.append(f"workflow_continuation_delegated_status_mismatch:{route_type}")
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
    if record.get("can_continue_after_delegated_next_gate") is not True:
        reasons.append(f"delegated_result_record_cannot_continue:{route_type}")
    if contract is not None:
        if record.get("delegated_schema_version") != contract["delegated_schema_version"]:
            reasons.append(f"delegated_result_record_schema_mismatch:{route_type}")
        if record.get("delegated_report_path") != contract["delegated_report_path"]:
            reasons.append(f"delegated_result_record_report_path_mismatch:{route_type}")
        if record.get("delegated_review_path") and record.get("delegated_review_path") != contract["delegated_review_path"]:
            reasons.append(f"delegated_result_record_review_path_mismatch:{route_type}")
    return dedupe(reasons)


def build_status(
    result_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if result_reasons:
        return "blocked_by_manifested_next_gate_command_result_review"
    if boundary_reasons:
        return "blocked_by_next_gate_workflow_continuation_boundary"
    if contract_reasons:
        return "blocked_by_next_gate_workflow_continuation_contract"
    return "ready_for_next_gate_workflow_continuation_review"


def build_workflow_continuation_plan(
    manifested_next_gate_command_result_review: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = manifested_next_gate_command_result_review["verified_route_type"]
    routed_next_gate = manifested_next_gate_command_result_review["routed_next_gate"]
    record = manifested_next_gate_command_result_review["delegated_result_records"][0]
    contract = CONTINUATION_CONTRACTS[routed_next_gate]
    return [
        {
            "continuation_id": f"next_gate_workflow_continuation::{routed_next_gate}::{route_type}",
            "source_delegated_result_record_id": record.get("record_id", ""),
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "delegated_status": manifested_next_gate_command_result_review.get("delegated_status", ""),
            "continuation_kind": contract["continuation_kind"],
            "next_command": contract["next_command"],
            "command_path": contract["command_path"],
            "source_report_path": contract["delegated_report_path"],
            "next_report_path": contract["next_report_path"],
            "next_review_path": contract["next_review_path"],
            "continuation_status": "pending_explicit_workflow_continuation_command",
            "requires_explicit_workflow_continuation_command": True,
            "will_run_continuation_by_this_command": False,
            "will_execute_export_or_acceptance_by_this_command": False,
            "will_write_product_state_by_this_command": False,
        }
    ]


def build_source_result_review_summary(
    manifested_next_gate_command_result_review: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": manifested_next_gate_command_result_review.get("schema_version", ""),
        "status": manifested_next_gate_command_result_review.get("status", ""),
        "verified_route_type": manifested_next_gate_command_result_review.get("verified_route_type", ""),
        "routed_next_gate": manifested_next_gate_command_result_review.get("routed_next_gate", ""),
        "delegated_status": manifested_next_gate_command_result_review.get("delegated_status", ""),
        "delegated_next_gate_result_reviewed": (
            manifested_next_gate_command_result_review.get("delegated_next_gate_result_reviewed")
            is True
        ),
        "can_continue_after_delegated_next_gate": (
            manifested_next_gate_command_result_review.get("can_continue_after_delegated_next_gate")
            is True
        ),
        "delegated_result_records_count": len(
            manifested_next_gate_command_result_review.get("delegated_result_records", []) or []
        ),
        "source_blocking_reasons": manifested_next_gate_command_result_review.get("blocking_reasons", []),
        "boundary_flags": manifested_next_gate_command_result_review.get("boundary_flags", {}),
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


def build_next_action(
    status: str,
    plan: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == "ready_for_next_gate_workflow_continuation_review":
        return {
            "id": plan[0]["next_command"],
            "label": "Run explicit next-gate workflow continuation preflight",
            "description": "A later command may prepare the selected route execution preflight; this command did not run it.",
        }
    if status == "blocked_by_next_gate_workflow_continuation_contract":
        return {
            "id": "repair_next_gate_workflow_continuation_contract",
            "label": "Repair continuation contract",
            "description": "P7-AJ must expose one consistent delegated result record for a known continuation.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_workflow_continuation_boundary":
        return {
            "id": "resolve_next_gate_workflow_continuation_boundary",
            "label": "Resolve continuation boundary violation",
            "description": "P7-AK is report-only and cannot consume result-review side effects.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_manifested_next_gate_result_review_blockers",
        "label": "Resolve P7-AJ blockers",
        "description": "P7-AJ must accept a delegated result before workflow continuation can be planned.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_workflow_continuation_preflight_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_PREFLIGHT_PATH,
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
        "# Auto Mode Formal Package Next Gate Workflow Continuation Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        f"- 可请求 workflow continuation：{str(report['can_request_next_gate_workflow_continuation']).lower()}",
        f"- 需要单独 continuation 命令：{str(report['requires_explicit_workflow_continuation_command']).lower()}",
        f"- continuation plan 数：{len(report['workflow_continuation_plan'])}",
        f"- 已运行 continuation：{str(report['workflow_continuation_executed']).lower()}",
        f"- 本命令运行 continuation：{str(report['this_command_ran_continuation']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Workflow Continuation Plan"])
    if report["workflow_continuation_plan"]:
        for item in report["workflow_continuation_plan"]:
            lines.append(f"- `{item['continuation_id']}` -> `{item['next_command']}`")
    else:
        lines.append("- 无；等待 P7-AJ 接受 delegated next-gate 结果。")
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

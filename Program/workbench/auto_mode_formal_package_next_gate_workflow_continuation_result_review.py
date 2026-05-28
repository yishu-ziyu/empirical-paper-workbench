from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_workflow_continuation_result_review.v1"
EXECUTE_SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_workflow_continuation_execute.v1"
SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_selected_route_execution_preflight.v1"
)
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json")
DEFAULT_SELECTED_ROUTE_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_package_selected_route_execution_preflight.json"
)
DEFAULT_RESULT_REVIEW_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json"
)
DEFAULT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_workflow_continuation_result_review.md"
)

CONTINUATION_RESULT_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "schema_version": SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION,
        "success_statuses": {"ready_for_selected_formal_package_route_execution_review"},
        "continuation_report_path": str(DEFAULT_SELECTED_ROUTE_PREFLIGHT_PATH),
        "continuation_review_path": "Reviews/auto_mode_formal_package_selected_route_execution_preflight.md",
    },
}

SELECTED_ROUTE_EXECUTION_CONTRACTS = {
    "pdf_export": {
        "routed_action": "formal_pdf_export_preflight",
        "next_command": "formal_pdf_export_execute",
        "planned_outputs": ["Submissions/formal_package/paper.pdf"],
    },
    "docx_export": {
        "routed_action": "formal_docx_export_preflight",
        "next_command": "formal_docx_export_execute",
        "planned_outputs": ["Submissions/formal_package/paper.docx"],
    },
    "package_manifest": {
        "routed_action": "formal_submission_package_manifest_preflight",
        "next_command": "formal_submission_package_manifest_execute",
        "planned_outputs": ["Submissions/formal_package/manifest.json"],
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_workflow_continuation_result_review(
    project_root: Path,
    next_gate_workflow_continuation_execute: dict[str, Any],
    selected_route_execution_preflight: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    del project_root
    source_paths = source_paths or {}
    execute_reasons = build_execute_blocking_reasons(next_gate_workflow_continuation_execute)
    contract_reasons = (
        build_continuation_result_contract_blocking_reasons(
            next_gate_workflow_continuation_execute,
            selected_route_execution_preflight,
        )
        if not execute_reasons
        else []
    )
    selected_route_reasons = (
        build_selected_route_preflight_blocking_reasons(
            next_gate_workflow_continuation_execute,
            selected_route_execution_preflight,
        )
        if not execute_reasons and not contract_reasons
        else []
    )
    blocking_reasons = dedupe(execute_reasons + contract_reasons + selected_route_reasons)
    status = build_status(execute_reasons, contract_reasons, selected_route_reasons)
    ready = status == "next_gate_workflow_continuation_result_review_ready"
    route_type = (
        next_gate_workflow_continuation_execute.get("verified_route_type", "")
        if not execute_reasons and not contract_reasons
        else ""
    )
    routed_next_gate = (
        next_gate_workflow_continuation_execute.get("routed_next_gate", "")
        if not execute_reasons and not contract_reasons
        else ""
    )
    selected_route_status = selected_route_execution_preflight.get("status", "") if ready else ""

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": next_gate_workflow_continuation_execute.get(
            "topic",
            selected_route_execution_preflight.get("topic", ""),
        ),
        "source_paths": {
            "next_gate_workflow_continuation_execute": source_paths.get(
                "next_gate_workflow_continuation_execute",
                str(DEFAULT_EXECUTE_PATH),
            ),
            "selected_route_execution_preflight": source_paths.get(
                "selected_route_execution_preflight",
                next_gate_workflow_continuation_execute.get("continuation_report_path", ""),
            ),
        },
        "source_status": next_gate_workflow_continuation_execute.get("status", ""),
        "status": status,
        "verified_route_type": route_type,
        "routed_next_gate": routed_next_gate,
        "continuation_status": (
            next_gate_workflow_continuation_execute.get("continuation_status", "") if ready else ""
        ),
        "selected_route_preflight_status": selected_route_status,
        "workflow_continuation_result_reviewed": ready,
        "can_continue_to_selected_route_execution": ready,
        "workflow_continuation_executed": (
            next_gate_workflow_continuation_execute.get("workflow_continuation_executed") is True
        ),
        "this_command_ran_continuation": False,
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "selected_route_execution_preflight_records": (
            build_selected_route_execution_preflight_records(
                next_gate_workflow_continuation_execute,
                selected_route_execution_preflight,
            )
            if ready
            else []
        ),
        "blocking_reasons": blocking_reasons,
        "source_execute": build_source_execute_summary(next_gate_workflow_continuation_execute),
        "source_selected_route_preflight": build_source_selected_route_preflight_summary(
            selected_route_execution_preflight
        ),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons, route_type, selected_route_execution_preflight),
    }


def build_execute_blocking_reasons(
    next_gate_workflow_continuation_execute: dict[str, Any],
) -> list[str]:
    reasons = []
    if next_gate_workflow_continuation_execute.get("schema_version") != EXECUTE_SCHEMA_VERSION:
        reasons.append("next_gate_workflow_continuation_execute_missing_or_invalid_schema")
    if next_gate_workflow_continuation_execute.get("status") != "next_gate_workflow_continuation_executed":
        reasons.append("next_gate_workflow_continuation_execute_not_completed")
    if next_gate_workflow_continuation_execute.get("workflow_continuation_executed") is not True:
        reasons.append("workflow_continuation_not_executed")
    if next_gate_workflow_continuation_execute.get("this_command_ran_continuation") is not True:
        reasons.append("source_execute_did_not_run_continuation")
    if next_gate_workflow_continuation_execute.get("continuation_returncode") != 0:
        reasons.append("continuation_returncode_not_zero")
    for field in [
        "verified_route_type",
        "routed_next_gate",
        "continuation_report_path",
        "continuation_status",
    ]:
        if not next_gate_workflow_continuation_execute.get(field):
            reasons.append(f"{field}_missing")
    if next_gate_workflow_continuation_execute.get("selected_route_executed") is True:
        reasons.append("next_gate_workflow_continuation_execute_selected_route")
    if next_gate_workflow_continuation_execute.get("export_or_acceptance_executed") is True:
        reasons.append("next_gate_workflow_continuation_execute_exported_or_accepted")
    if next_gate_workflow_continuation_execute.get("formal_writeback_executed") is True:
        reasons.append("next_gate_workflow_continuation_execute_formal_writeback")
    if next_gate_workflow_continuation_execute.get("this_command_wrote_formal_state") is True:
        reasons.append("next_gate_workflow_continuation_execute_wrote_formal_state")
    if next_gate_workflow_continuation_execute.get("can_write_product_state") is True:
        reasons.append("next_gate_workflow_continuation_execute_allows_product_state_write")
    if next_gate_workflow_continuation_execute.get("blocking_reasons"):
        reasons.append("source_execute_has_blocking_reasons")
    for flag, value in next_gate_workflow_continuation_execute.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"next_gate_workflow_continuation_execute_boundary_violation:{flag}")
    return dedupe(reasons)


def build_continuation_result_contract_blocking_reasons(
    next_gate_workflow_continuation_execute: dict[str, Any],
    selected_route_execution_preflight: dict[str, Any],
) -> list[str]:
    route_type = next_gate_workflow_continuation_execute.get("verified_route_type", "unknown")
    routed_next_gate = next_gate_workflow_continuation_execute.get("routed_next_gate", "")
    contract = CONTINUATION_RESULT_CONTRACTS.get(routed_next_gate)
    if contract is None:
        return [f"routed_next_gate_unknown:{routed_next_gate}"]

    reasons = []
    if route_type not in contract["allowed_route_types"]:
        reasons.append(f"workflow_continuation_route_type_not_allowed:{route_type}")
    if next_gate_workflow_continuation_execute.get("continuation_report_path") != contract["continuation_report_path"]:
        reasons.append(f"continuation_report_path_mismatch:{route_type}")
    continuation_review_path = next_gate_workflow_continuation_execute.get("continuation_review_path", "")
    if continuation_review_path and continuation_review_path != contract["continuation_review_path"]:
        reasons.append(f"continuation_review_path_mismatch:{route_type}")

    continuation_result = next_gate_workflow_continuation_execute.get("continuation_result", {})
    if (
        continuation_result.get("report_path")
        and continuation_result.get("report_path") != contract["continuation_report_path"]
    ):
        reasons.append(f"continuation_result_report_path_mismatch:{route_type}")
    if (
        continuation_result.get("review_path")
        and continuation_result.get("review_path") != contract["continuation_review_path"]
    ):
        reasons.append(f"continuation_result_review_path_mismatch:{route_type}")

    execute_status = next_gate_workflow_continuation_execute.get("continuation_status", "")
    selected_route_status = selected_route_execution_preflight.get("status", "")
    if selected_route_status in contract["success_statuses"] and execute_status != selected_route_status:
        reasons.append(f"continuation_status_mismatch:{route_type}")
    if continuation_result.get("status") and continuation_result.get("status") != execute_status:
        reasons.append(f"continuation_result_status_mismatch:{route_type}")
    return dedupe(reasons)


def build_selected_route_preflight_blocking_reasons(
    next_gate_workflow_continuation_execute: dict[str, Any],
    selected_route_execution_preflight: dict[str, Any],
) -> list[str]:
    route_type = next_gate_workflow_continuation_execute.get("verified_route_type", "unknown")
    routed_next_gate = next_gate_workflow_continuation_execute.get("routed_next_gate", "")
    continuation_contract = CONTINUATION_RESULT_CONTRACTS.get(routed_next_gate, {})
    route_contract = SELECTED_ROUTE_EXECUTION_CONTRACTS.get(route_type, {})
    reasons = []
    if selected_route_execution_preflight.get("schema_version") != continuation_contract.get("schema_version"):
        reasons.append(f"selected_route_preflight_missing_or_invalid_schema:{route_type}")
    if selected_route_execution_preflight.get("status") not in continuation_contract.get(
        "success_statuses",
        set(),
    ):
        reasons.append(f"selected_route_preflight_status_not_ready:{route_type}")
    if selected_route_execution_preflight.get("can_request_selected_route_execution") is not True:
        reasons.append(f"selected_route_preflight_cannot_request_execution:{route_type}")
    if selected_route_execution_preflight.get("requires_explicit_route_execute_command") is not True:
        reasons.append(f"selected_route_preflight_missing_explicit_route_command:{route_type}")
    if selected_route_execution_preflight.get("selected_route_executed") is True:
        reasons.append(f"selected_route_preflight_already_executed:{route_type}")
    if selected_route_execution_preflight.get("export_or_acceptance_executed") is True:
        reasons.append(f"selected_route_preflight_export_or_acceptance_executed:{route_type}")
    if selected_route_execution_preflight.get("rendered_pdf") is True:
        reasons.append(f"selected_route_preflight_rendered_pdf:{route_type}")
    if selected_route_execution_preflight.get("rendered_docx") is True:
        reasons.append(f"selected_route_preflight_rendered_docx:{route_type}")
    if selected_route_execution_preflight.get("package_manifest_generated") is True:
        reasons.append(f"selected_route_preflight_generated_package_manifest:{route_type}")
    if selected_route_execution_preflight.get("manual_acceptance_performed") is True:
        reasons.append(f"selected_route_preflight_performed_manual_acceptance:{route_type}")
    if selected_route_execution_preflight.get("formal_writeback_executed") is True:
        reasons.append(f"selected_route_preflight_formal_writeback:{route_type}")
    if selected_route_execution_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append(f"selected_route_preflight_wrote_formal_state:{route_type}")
    if selected_route_execution_preflight.get("can_write_product_state") is True:
        reasons.append(f"selected_route_preflight_allows_product_state_write:{route_type}")
    if selected_route_execution_preflight.get("blocking_reasons"):
        reasons.append(f"selected_route_preflight_has_blocking_reasons:{route_type}")

    plan = selected_route_execution_preflight.get("selected_route_execution_plan", [])
    if not isinstance(plan, list) or len(plan) != 1:
        reasons.append(f"selected_route_execution_plan_not_single:{route_type}")
    elif route_contract:
        item = plan[0]
        if item.get("route_type") != route_type:
            reasons.append(f"selected_route_plan_route_type_mismatch:{route_type}")
        if item.get("routed_action") != route_contract["routed_action"]:
            reasons.append(f"selected_route_plan_routed_action_mismatch:{route_type}")
        if item.get("next_command") != route_contract["next_command"]:
            reasons.append(f"selected_route_plan_next_command_mismatch:{route_type}")
        if item.get("planned_outputs") != route_contract["planned_outputs"]:
            reasons.append(f"selected_route_plan_outputs_mismatch:{route_type}")
        if item.get("execution_status") != "pending_explicit_route_execute_command":
            reasons.append(f"selected_route_plan_not_pending:{route_type}")
        if item.get("requires_explicit_route_execute_command") is not True:
            reasons.append(f"selected_route_plan_missing_explicit_command:{route_type}")
        if item.get("will_execute_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_execute:{route_type}")
        if item.get("will_render_pdf_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_render_pdf:{route_type}")
        if item.get("will_render_docx_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_render_docx:{route_type}")
        if item.get("will_generate_manifest_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_generate_manifest:{route_type}")
        if item.get("will_perform_manual_acceptance_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_manual_acceptance:{route_type}")
        if item.get("will_write_product_state_by_this_command") is True:
            reasons.append(f"selected_route_plan_marked_product_state_write:{route_type}")

    for flag, value in selected_route_execution_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"selected_route_preflight_boundary_violation:{flag}")
    return dedupe(reasons)


def build_status(
    execute_reasons: list[str],
    contract_reasons: list[str],
    selected_route_reasons: list[str],
) -> str:
    if execute_reasons:
        return "blocked_by_next_gate_workflow_continuation_execute"
    if contract_reasons:
        return "blocked_by_next_gate_workflow_continuation_result_contract"
    if selected_route_reasons:
        return "blocked_by_selected_route_execution_preflight_report"
    return "next_gate_workflow_continuation_result_review_ready"


def build_selected_route_execution_preflight_records(
    next_gate_workflow_continuation_execute: dict[str, Any],
    selected_route_execution_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    route_type = next_gate_workflow_continuation_execute.get("verified_route_type", "")
    routed_next_gate = next_gate_workflow_continuation_execute.get("routed_next_gate", "")
    plan_item = selected_route_execution_preflight.get("selected_route_execution_plan", [{}])[0]
    return [
        {
            "record_id": f"workflow_continuation_result::{routed_next_gate}::{route_type}",
            "verified_route_type": route_type,
            "routed_next_gate": routed_next_gate,
            "selected_route_preflight_status": selected_route_execution_preflight.get("status", ""),
            "selected_route_preflight_schema_version": selected_route_execution_preflight.get("schema_version", ""),
            "selected_route_preflight_report_path": next_gate_workflow_continuation_execute.get(
                "continuation_report_path",
                "",
            ),
            "selected_route_preflight_review_path": next_gate_workflow_continuation_execute.get(
                "continuation_review_path",
                "",
            ),
            "routed_action": plan_item.get("routed_action", ""),
            "next_command": plan_item.get("next_command", ""),
            "planned_outputs": plan_item.get("planned_outputs", []),
            "review_status": "selected_route_preflight_accepted_for_explicit_route_execution",
            "can_continue_to_selected_route_execution": True,
        }
    ]


def build_source_execute_summary(
    next_gate_workflow_continuation_execute: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": next_gate_workflow_continuation_execute.get("schema_version", ""),
        "status": next_gate_workflow_continuation_execute.get("status", ""),
        "verified_route_type": next_gate_workflow_continuation_execute.get("verified_route_type", ""),
        "routed_next_gate": next_gate_workflow_continuation_execute.get("routed_next_gate", ""),
        "workflow_continuation_executed": (
            next_gate_workflow_continuation_execute.get("workflow_continuation_executed") is True
        ),
        "this_command_ran_continuation": (
            next_gate_workflow_continuation_execute.get("this_command_ran_continuation") is True
        ),
        "continuation_report_path": next_gate_workflow_continuation_execute.get("continuation_report_path", ""),
        "continuation_review_path": next_gate_workflow_continuation_execute.get("continuation_review_path", ""),
        "continuation_returncode": next_gate_workflow_continuation_execute.get("continuation_returncode"),
        "continuation_status": next_gate_workflow_continuation_execute.get("continuation_status", ""),
        "source_blocking_reasons": next_gate_workflow_continuation_execute.get("blocking_reasons", []),
        "boundary_flags": next_gate_workflow_continuation_execute.get("boundary_flags", {}),
    }


def build_source_selected_route_preflight_summary(
    selected_route_execution_preflight: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execution_preflight.get("schema_version", ""),
        "status": selected_route_execution_preflight.get("status", ""),
        "can_request_selected_route_execution": (
            selected_route_execution_preflight.get("can_request_selected_route_execution") is True
        ),
        "requires_explicit_route_execute_command": (
            selected_route_execution_preflight.get("requires_explicit_route_execute_command") is True
        ),
        "selected_route_execution_plan_count": len(
            selected_route_execution_preflight.get("selected_route_execution_plan", []) or []
        ),
        "selected_route_executed": selected_route_execution_preflight.get("selected_route_executed") is True,
        "export_or_acceptance_executed": (
            selected_route_execution_preflight.get("export_or_acceptance_executed") is True
        ),
        "blocking_reasons": selected_route_execution_preflight.get("blocking_reasons", []),
        "boundary_flags": selected_route_execution_preflight.get("boundary_flags", {}),
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
    blocking_reasons: list[str],
    route_type: str,
    selected_route_execution_preflight: dict[str, Any],
) -> dict[str, Any]:
    if status == "next_gate_workflow_continuation_result_review_ready":
        plan = selected_route_execution_preflight.get("selected_route_execution_plan", [{}])
        next_command = plan[0].get("next_command", "selected_route_execute") if plan else "selected_route_execute"
        return {
            "id": next_command,
            "label": "Run explicit selected route execute command",
            "description": f"The `{route_type}` selected route preflight is accepted for explicit route execution.",
        }
    if status == "blocked_by_next_gate_workflow_continuation_execute":
        return {
            "id": "resolve_workflow_continuation_execute_blockers",
            "label": "Resolve P7-AL execute blockers",
            "description": "P7-AL must complete a continuation command before result review can continue.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_next_gate_workflow_continuation_result_contract":
        return {
            "id": "repair_workflow_continuation_result_contract",
            "label": "Repair workflow continuation result contract",
            "description": "The continuation route, report path, review path, or status does not match contract.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "repair_selected_route_execution_preflight",
        "label": "Repair selected route execution preflight",
        "description": "The selected route execution preflight must be ready and clean before route execution.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_workflow_continuation_result_review_outputs(
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
        "# Auto Mode Formal Package Next Gate Workflow Continuation Result Review",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        f"- continuation 状态：`{report['continuation_status']}`",
        f"- selected route preflight 状态：`{report['selected_route_preflight_status']}`",
        f"- 已审阅 continuation 结果：{str(report['workflow_continuation_result_reviewed']).lower()}",
        "- 可继续 selected route execution："
        f"{str(report['can_continue_to_selected_route_execution']).lower()}",
        "- selected route preflight records："
        f"{len(report['selected_route_execution_preflight_records'])}",
        f"- source 已运行 continuation：{str(report['workflow_continuation_executed']).lower()}",
        f"- 本命令运行 continuation：{str(report['this_command_ran_continuation']).lower()}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if report["selected_route_execution_preflight_records"]:
        lines.extend(["", "## Selected Route Preflight Records"])
        for record in report["selected_route_execution_preflight_records"]:
            lines.append(
                "- "
                f"`{record['record_id']}`: {record['review_status']} "
                f"-> `{record['next_command']}`"
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

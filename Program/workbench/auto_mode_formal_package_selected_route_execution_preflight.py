from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execution_preflight.v1"
ROUTER_SCHEMA_VERSION = "p7.auto_mode_formal_package_export_acceptance_router.v1"
DEFAULT_ROUTER_PATH = Path("Results/json/auto_mode_formal_package_export_acceptance_router.json")
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execution_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_selected_route_execution_preflight.md")

ROUTE_EXECUTION_CONTRACTS = {
    "formal_pdf_export_preflight": {
        "route_type": "pdf_export",
        "planned_outputs": ["Submissions/formal_package/paper.pdf"],
        "next_command": "formal_pdf_export_execute",
    },
    "formal_docx_export_preflight": {
        "route_type": "docx_export",
        "planned_outputs": ["Submissions/formal_package/paper.docx"],
        "next_command": "formal_docx_export_execute",
    },
    "formal_submission_package_manifest_preflight": {
        "route_type": "package_manifest",
        "planned_outputs": ["Submissions/formal_package/manifest.json"],
        "next_command": "formal_submission_package_manifest_execute",
    },
    "manual_acceptance_packet_preflight": {
        "route_type": "manual_acceptance",
        "planned_outputs": ["Reviews/formal_package_manual_acceptance.md"],
        "next_command": "formal_package_manual_acceptance_execute",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_selected_route_execution_preflight(
    export_acceptance_router: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    router_reasons = build_router_blocking_reasons(export_acceptance_router)
    boundary_reasons = build_router_boundary_blocking_reasons(export_acceptance_router) if not router_reasons else []
    contract_reasons = (
        build_selected_route_contract_blocking_reasons(export_acceptance_router)
        if not router_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = router_reasons + boundary_reasons + contract_reasons
    status = build_status(router_reasons, boundary_reasons, contract_reasons)
    ready = status == "ready_for_selected_formal_package_route_execution_review"
    plan = build_selected_route_execution_plan(export_acceptance_router) if ready else []
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": export_acceptance_router.get("topic", ""),
        "source_paths": {
            "export_acceptance_router": source_paths.get("export_acceptance_router", str(DEFAULT_ROUTER_PATH)),
        },
        "source_status": export_acceptance_router.get("status", ""),
        "status": status,
        "can_request_selected_route_execution": ready,
        "requires_explicit_route_execute_command": ready,
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
        "source_router": build_source_router(export_acceptance_router),
        "selected_route_execution_plan": plan,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, plan, blocking_reasons),
    }


def build_router_blocking_reasons(export_acceptance_router: dict[str, Any]) -> list[str]:
    reasons = []
    if export_acceptance_router.get("schema_version") != ROUTER_SCHEMA_VERSION:
        reasons.append("export_acceptance_router_missing_or_invalid_schema")
    if export_acceptance_router.get("status") != "formal_package_export_acceptance_route_recorded":
        reasons.append("export_acceptance_router_not_route_recorded")
    if export_acceptance_router.get("can_route_export_or_acceptance") is not True:
        reasons.append("export_acceptance_router_cannot_route")
    if export_acceptance_router.get("route_recorded") is not True:
        reasons.append("export_acceptance_router_route_not_recorded")
    if not export_acceptance_router.get("routed_action"):
        reasons.append("export_acceptance_router_routed_action_missing")
    request = export_acceptance_router.get("route_request", {})
    if request.get("metadata_complete") is not True:
        reasons.append("export_acceptance_router_metadata_incomplete")
    if request.get("confirm_route") is not True:
        reasons.append("export_acceptance_router_confirmation_missing")
    return dedupe(reasons)


def build_router_boundary_blocking_reasons(export_acceptance_router: dict[str, Any]) -> list[str]:
    reasons = []
    if export_acceptance_router.get("export_or_acceptance_executed") is True:
        reasons.append("export_acceptance_router_already_executed_export_or_acceptance")
    if export_acceptance_router.get("rendered_pdf") is True:
        reasons.append("export_acceptance_router_rendered_pdf")
    if export_acceptance_router.get("rendered_docx") is True:
        reasons.append("export_acceptance_router_rendered_docx")
    if export_acceptance_router.get("formal_writeback_executed") is True:
        reasons.append("export_acceptance_router_executed_formal_writeback")
    if export_acceptance_router.get("this_command_wrote_formal_state") is True:
        reasons.append("export_acceptance_router_wrote_formal_state")
    if export_acceptance_router.get("can_write_product_state") is True:
        reasons.append("export_acceptance_router_allows_product_state_write")
    for flag, value in export_acceptance_router.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"export_acceptance_router_boundary_violation:{flag}")
    return dedupe(reasons)


def build_selected_route_contract_blocking_reasons(export_acceptance_router: dict[str, Any]) -> list[str]:
    reasons = []
    routed_action = export_acceptance_router.get("routed_action", "")
    selected_plan_item = export_acceptance_router.get("selected_plan_item", {})
    if routed_action not in ROUTE_EXECUTION_CONTRACTS:
        reasons.append(f"selected_route_unknown:{routed_action}")
    if not selected_plan_item:
        reasons.append("selected_plan_item_missing")
        return dedupe(reasons)
    if selected_plan_item.get("action_id") != routed_action:
        reasons.append("selected_route_action_mismatch")
    if selected_plan_item.get("execution_status") != "pending_explicit_export_or_acceptance_command":
        reasons.append(f"selected_route_not_pending:{routed_action}")
    if selected_plan_item.get("requires_explicit_export_or_acceptance_command") is not True:
        reasons.append(f"selected_route_missing_explicit_command_requirement:{routed_action}")
    if selected_plan_item.get("this_command_rendered_or_accepted") is True:
        reasons.append(f"selected_route_already_rendered_or_accepted:{routed_action}")
    if selected_plan_item.get("this_command_wrote_product_state") is True:
        reasons.append(f"selected_route_wrote_product_state:{routed_action}")
    source_targets = selected_plan_item.get("source_formal_targets", [])
    if not source_targets:
        reasons.append(f"selected_route_source_targets_missing:{routed_action}")
    for target in source_targets:
        if not target.startswith("Submissions/formal_package/"):
            reasons.append(f"selected_route_source_target_outside_formal_package:{target}")
    return dedupe(reasons)


def build_status(
    router_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if router_reasons or boundary_reasons:
        return "blocked_by_export_acceptance_router"
    if contract_reasons:
        return "blocked_by_selected_route_contract"
    return "ready_for_selected_formal_package_route_execution_review"


def build_source_router(export_acceptance_router: dict[str, Any]) -> dict[str, Any]:
    request = export_acceptance_router.get("route_request", {})
    return {
        "schema_version": export_acceptance_router.get("schema_version", ""),
        "status": export_acceptance_router.get("status", ""),
        "decision": export_acceptance_router.get("decision", ""),
        "can_route_export_or_acceptance": export_acceptance_router.get("can_route_export_or_acceptance") is True,
        "route_recorded": export_acceptance_router.get("route_recorded") is True,
        "routed_action": export_acceptance_router.get("routed_action", ""),
        "metadata_complete": request.get("metadata_complete") is True,
        "confirm_route": request.get("confirm_route") is True,
        "source_blocking_reasons": export_acceptance_router.get("blocking_reasons", []),
    }


def build_selected_route_execution_plan(export_acceptance_router: dict[str, Any]) -> list[dict[str, Any]]:
    routed_action = export_acceptance_router.get("routed_action", "")
    contract = ROUTE_EXECUTION_CONTRACTS[routed_action]
    selected_plan_item = export_acceptance_router.get("selected_plan_item", {})
    return [
        {
            "route_execution_id": f"selected_formal_package_route_execution::{routed_action}",
            "routed_action": routed_action,
            "route_type": contract["route_type"],
            "next_command": contract["next_command"],
            "source_formal_targets": selected_plan_item.get("source_formal_targets", []),
            "planned_outputs": contract["planned_outputs"],
            "execution_status": "pending_explicit_route_execute_command",
            "requires_explicit_route_execute_command": True,
            "will_execute_by_this_command": False,
            "will_render_pdf_by_this_command": False,
            "will_render_docx_by_this_command": False,
            "will_generate_manifest_by_this_command": False,
            "will_perform_manual_acceptance_by_this_command": False,
            "will_write_product_state_by_this_command": False,
        }
    ]


def build_boundary_flags() -> dict[str, bool]:
    return {
        "modified_formal_manuscript": False,
        "modified_formal_bibliography": False,
        "modified_project_bibliography": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "modified_product_state": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "reran_models": False,
        "modified_statistical_execution_artifacts": False,
        "executed_target_adapters": False,
        "wrote_formal_state": False,
        "created_or_repaired_candidate_targets": False,
        "promoted_candidate_targets": False,
        "exported_or_accepted_formal_package": False,
        "generated_package_manifest": False,
        "performed_manual_acceptance": False,
    }


def build_next_action(
    status: str,
    plan: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == "ready_for_selected_formal_package_route_execution_review":
        return {
            "id": plan[0]["next_command"],
            "label": "Run explicit selected route execute command",
            "description": "A later command may execute this selected route; this preflight did not export or accept anything.",
        }
    if status == "blocked_by_selected_route_contract":
        return {
            "id": "repair_selected_route_contract",
            "label": "Repair selected route contract",
            "description": "The P7-Y selected route must match a known pending route before execution preflight.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "record_export_acceptance_route",
        "label": "Record export / acceptance route",
        "description": "P7-Y must record one clean route before selected route execution preflight can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_selected_route_execution_preflight_outputs(
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
        "# Auto Mode Formal Package Selected Route Execution Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 可请求 selected route 执行：{str(report['can_request_selected_route_execution']).lower()}",
        f"- 需要单独执行命令：{str(report['requires_explicit_route_execute_command']).lower()}",
        f"- 执行计划数：{len(report['selected_route_execution_plan'])}",
        f"- 已执行 selected route：{str(report['selected_route_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 已渲染 PDF：{str(report['rendered_pdf']).lower()}",
        f"- 已渲染 DOCX：{str(report['rendered_docx']).lower()}",
        f"- 已生成 package manifest：{str(report['package_manifest_generated']).lower()}",
        f"- 已执行人工验收：{str(report['manual_acceptance_performed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Selected Route Execution Plan"])
    if report["selected_route_execution_plan"]:
        for item in report["selected_route_execution_plan"]:
            lines.append(f"- `{item['routed_action']}` -> `{item['next_command']}`")
    else:
        lines.append("- 无；等待 P7-Y 记录一条可执行路线。")
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

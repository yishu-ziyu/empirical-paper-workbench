from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_export_acceptance_router.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_package_export_acceptance_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_export_acceptance_preflight.json")
DEFAULT_ROUTER_PATH = Path("Results/json/auto_mode_formal_package_export_acceptance_router.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_export_acceptance_router.md")

DECISION_ACTIONS = {
    "defer": "",
    "pdf_export": "formal_pdf_export_preflight",
    "docx_export": "formal_docx_export_preflight",
    "package_manifest": "formal_submission_package_manifest_preflight",
    "manual_acceptance": "manual_acceptance_packet_preflight",
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_export_acceptance_router(
    export_acceptance_preflight: dict[str, Any],
    *,
    decision: str = "defer",
    confirm_route: bool = False,
    reviewer: str = "",
    note: str = "",
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(export_acceptance_preflight)
    selected_action = DECISION_ACTIONS.get(decision)
    decision_reasons = [] if selected_action is not None else [f"export_acceptance_decision_invalid:{decision}"]
    route_reasons = (
        build_route_blocking_reasons(
            export_acceptance_preflight,
            selected_action or "",
            confirm_route=confirm_route,
            reviewer=reviewer,
            note=note,
        )
        if not preflight_reasons and not decision_reasons and decision != "defer"
        else []
    )
    blocking_reasons = preflight_reasons + decision_reasons + route_reasons
    status = build_status(preflight_reasons, decision_reasons, decision, route_reasons)
    route_recorded = status == "formal_package_export_acceptance_route_recorded"
    selected_plan_item = find_plan_item(export_acceptance_preflight, selected_action or "") if route_recorded else {}
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": export_acceptance_preflight.get("topic", ""),
        "source_paths": {
            "export_acceptance_preflight": source_paths.get(
                "export_acceptance_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "source_status": export_acceptance_preflight.get("status", ""),
        "status": status,
        "decision": decision,
        "route_request": {
            "decision": decision,
            "confirm_route": confirm_route,
            "reviewer": reviewer,
            "note": note,
            "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
        },
        "can_route_export_or_acceptance": route_recorded,
        "route_recorded": route_recorded,
        "routed_action": selected_action if route_recorded else "",
        "selected_plan_item": selected_plan_item,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "preflight_summary": build_preflight_summary(export_acceptance_preflight),
        "export_acceptance_plan": export_acceptance_preflight.get("export_acceptance_plan", []),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, selected_action or "", blocking_reasons),
    }


def build_preflight_blocking_reasons(export_acceptance_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if export_acceptance_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("export_acceptance_preflight_missing_or_invalid_schema")
    if export_acceptance_preflight.get("status") != "ready_for_formal_package_export_acceptance_review":
        reasons.append("export_acceptance_preflight_not_ready")
    if export_acceptance_preflight.get("can_enter_formal_package_export_acceptance") is not True:
        reasons.append("export_acceptance_preflight_cannot_enter")
    if export_acceptance_preflight.get("requires_explicit_export_or_acceptance_command") is not True:
        reasons.append("export_acceptance_preflight_missing_explicit_command_requirement")
    if export_acceptance_preflight.get("export_or_acceptance_executed") is True:
        reasons.append("export_acceptance_preflight_already_executed_export_or_acceptance")
    if export_acceptance_preflight.get("rendered_pdf") is True:
        reasons.append("export_acceptance_preflight_rendered_pdf")
    if export_acceptance_preflight.get("rendered_docx") is True:
        reasons.append("export_acceptance_preflight_rendered_docx")
    if export_acceptance_preflight.get("formal_writeback_executed") is True:
        reasons.append("export_acceptance_preflight_executed_formal_writeback")
    if export_acceptance_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("export_acceptance_preflight_wrote_formal_state")
    if export_acceptance_preflight.get("can_write_product_state") is True:
        reasons.append("export_acceptance_preflight_allows_product_state_write")
    for flag, value in export_acceptance_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"export_acceptance_preflight_boundary_violation:{flag}")
    if not reasons and not export_acceptance_preflight.get("export_acceptance_plan"):
        reasons.append("export_acceptance_preflight_plan_missing")
    return dedupe(reasons)


def build_route_blocking_reasons(
    export_acceptance_preflight: dict[str, Any],
    selected_action: str,
    *,
    confirm_route: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    reasons = []
    plan_item = find_plan_item(export_acceptance_preflight, selected_action)
    if not plan_item:
        reasons.append(f"export_acceptance_action_not_in_preflight_plan:{selected_action}")
    else:
        if plan_item.get("execution_status") != "pending_explicit_export_or_acceptance_command":
            reasons.append(f"export_acceptance_action_not_pending:{selected_action}")
        if plan_item.get("requires_explicit_export_or_acceptance_command") is not True:
            reasons.append(f"export_acceptance_action_missing_explicit_command_requirement:{selected_action}")
        if plan_item.get("this_command_rendered_or_accepted") is True:
            reasons.append(f"export_acceptance_action_already_rendered_or_accepted:{selected_action}")
        if plan_item.get("this_command_wrote_product_state") is True:
            reasons.append(f"export_acceptance_action_wrote_product_state:{selected_action}")
    if not confirm_route:
        reasons.append("confirm_route_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("route_note_required")
    return dedupe(reasons)


def build_status(
    preflight_reasons: list[str],
    decision_reasons: list[str],
    decision: str,
    route_reasons: list[str],
) -> str:
    if preflight_reasons:
        return "blocked_by_export_acceptance_preflight"
    if decision_reasons:
        return "blocked_by_unknown_export_acceptance_decision"
    if decision == "defer":
        return "waiting_for_formal_package_export_acceptance_decision"
    if "confirm_route_required" in route_reasons:
        return "blocked_by_missing_export_acceptance_route_confirmation"
    if "reviewer_required" in route_reasons or "route_note_required" in route_reasons:
        return "blocked_by_export_acceptance_route_metadata"
    if route_reasons:
        return "blocked_by_export_acceptance_route"
    return "formal_package_export_acceptance_route_recorded"


def build_preflight_summary(export_acceptance_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": export_acceptance_preflight.get("schema_version", ""),
        "status": export_acceptance_preflight.get("status", ""),
        "can_enter_formal_package_export_acceptance": (
            export_acceptance_preflight.get("can_enter_formal_package_export_acceptance") is True
        ),
        "requires_explicit_export_or_acceptance_command": (
            export_acceptance_preflight.get("requires_explicit_export_or_acceptance_command") is True
        ),
        "export_acceptance_plan_count": len(export_acceptance_preflight.get("export_acceptance_plan", [])),
        "source_blocking_reasons": export_acceptance_preflight.get("blocking_reasons", []),
    }


def find_plan_item(export_acceptance_preflight: dict[str, Any], action_id: str) -> dict[str, Any]:
    for item in export_acceptance_preflight.get("export_acceptance_plan", []):
        if item.get("action_id") == action_id:
            return item
    return {}


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


def build_next_action(status: str, selected_action: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "formal_package_export_acceptance_route_recorded":
        return {
            "id": selected_action,
            "label": "Run selected explicit export / acceptance preflight",
            "description": "A later command may consume this route; this router did not export or accept anything.",
        }
    if status == "waiting_for_formal_package_export_acceptance_decision":
        return {
            "id": "choose_formal_package_export_acceptance_route",
            "label": "Choose export / acceptance route",
            "description": "Select pdf_export, docx_export, package_manifest, manual_acceptance, or defer.",
        }
    if status == "blocked_by_export_acceptance_preflight":
        return {
            "id": "complete_export_acceptance_preflight",
            "label": "Complete export / acceptance preflight",
            "description": "P7-X must be ready before a route can be recorded.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "repair_export_acceptance_route_request",
        "label": "Repair export / acceptance route request",
        "description": "Provide a valid confirmed route with reviewer and note.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_export_acceptance_router_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_ROUTER_PATH,
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
        "# Auto Mode Formal Package Export / Acceptance Router",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 决策：`{report['decision']}`",
        f"- 可记录导出/验收路线：{str(report['can_route_export_or_acceptance']).lower()}",
        f"- 已记录路线：{str(report['route_recorded']).lower()}",
        f"- 路由动作：`{report['routed_action']}`",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 已渲染 PDF：{str(report['rendered_pdf']).lower()}",
        f"- 已渲染 DOCX：{str(report['rendered_docx']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Route Request"])
    request = report["route_request"]
    lines.append(f"- confirm_route: {str(request['confirm_route']).lower()}")
    lines.append(f"- reviewer: `{request['reviewer']}`")
    lines.append(f"- note: `{request['note']}`")
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

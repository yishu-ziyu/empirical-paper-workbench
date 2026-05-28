from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_routed_next_gate_entry_preflight.v1"
ROUTER_SCHEMA_VERSION = "p7.auto_mode_formal_package_verified_route_next_gate_router.v1"
RECORDED_ROUTER_STATUS = "verified_route_next_gate_route_recorded"
DEFAULT_ROUTER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_next_gate_router.json")
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md")

NEXT_GATE_ENTRY_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_actions": {"continue_formal_package_export_acceptance_cycle"},
        "next_command": "auto_mode_formal_package_export_acceptance_router",
        "entry_kind": "continue_export_acceptance_cycle",
    },
    "formal_package_delivery_completion_gate": {
        "allowed_actions": {"finalize_formal_package_delivery_review"},
        "next_command": "auto_mode_formal_package_delivery_completion_gate",
        "entry_kind": "delivery_completion",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_routed_next_gate_entry_preflight(
    verified_route_next_gate_router: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    router_reasons = build_router_blocking_reasons(verified_route_next_gate_router)
    boundary_reasons = (
        build_boundary_blocking_reasons(verified_route_next_gate_router) if not router_reasons else []
    )
    contract_reasons = (
        build_contract_blocking_reasons(verified_route_next_gate_router)
        if not router_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(router_reasons + boundary_reasons + contract_reasons)
    status = build_status(router_reasons, boundary_reasons, contract_reasons)
    ready = status == "ready_for_routed_next_gate_entry_review"
    entry_plan = build_next_gate_entry_plan(verified_route_next_gate_router) if ready else []

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": verified_route_next_gate_router.get("topic", ""),
        "source_paths": {
            "verified_route_next_gate_router": source_paths.get(
                "verified_route_next_gate_router",
                str(DEFAULT_ROUTER_PATH),
            ),
        },
        "source_status": verified_route_next_gate_router.get("status", ""),
        "status": status,
        "verified_route_type": verified_route_next_gate_router.get("verified_route_type", "") if ready else "",
        "routed_next_gate": verified_route_next_gate_router.get("routed_next_gate", "") if ready else "",
        "can_request_routed_next_gate_entry": ready,
        "requires_explicit_next_gate_entry_command": ready,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_router": build_source_router_summary(verified_route_next_gate_router),
        "next_gate_entry_plan": entry_plan,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, entry_plan, blocking_reasons),
    }


def build_router_blocking_reasons(verified_route_next_gate_router: dict[str, Any]) -> list[str]:
    reasons = []
    if verified_route_next_gate_router.get("schema_version") != ROUTER_SCHEMA_VERSION:
        reasons.append("verified_route_next_gate_router_missing_or_invalid_schema")
    if verified_route_next_gate_router.get("status") != RECORDED_ROUTER_STATUS:
        reasons.append("verified_route_next_gate_router_not_route_recorded")
    if verified_route_next_gate_router.get("next_gate_route_recorded") is not True:
        reasons.append("verified_route_next_gate_router_route_not_recorded")
    if verified_route_next_gate_router.get("can_enter_routed_next_gate") is not True:
        reasons.append("verified_route_next_gate_router_cannot_enter_routed_next_gate")
    if not verified_route_next_gate_router.get("routed_next_gate"):
        reasons.append("verified_route_next_gate_router_routed_next_gate_missing")
    if not verified_route_next_gate_router.get("verified_route_type"):
        reasons.append("verified_route_next_gate_router_verified_route_type_missing")
    if verified_route_next_gate_router.get("blocking_reasons"):
        reasons.append("source_router_has_blocking_reasons")
    return dedupe(reasons)


def build_boundary_blocking_reasons(verified_route_next_gate_router: dict[str, Any]) -> list[str]:
    reasons = []
    if verified_route_next_gate_router.get("this_command_entered_next_gate") is True:
        reasons.append("verified_route_next_gate_router_entered_next_gate")
    if verified_route_next_gate_router.get("export_or_acceptance_executed") is True:
        reasons.append("verified_route_next_gate_router_executed_export_or_acceptance")
    if verified_route_next_gate_router.get("formal_writeback_executed") is True:
        reasons.append("verified_route_next_gate_router_formal_writeback_executed")
    if verified_route_next_gate_router.get("this_command_wrote_formal_state") is True:
        reasons.append("verified_route_next_gate_router_wrote_formal_state")
    if verified_route_next_gate_router.get("can_write_product_state") is True:
        reasons.append("verified_route_next_gate_router_allows_product_state_write")
    for flag, value in verified_route_next_gate_router.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"verified_route_next_gate_router_boundary_violation:{flag}")
    return dedupe(reasons)


def build_contract_blocking_reasons(verified_route_next_gate_router: dict[str, Any]) -> list[str]:
    reasons = []
    routed_next_gate = verified_route_next_gate_router.get("routed_next_gate", "")
    route_type = verified_route_next_gate_router.get("verified_route_type", "")
    route = verified_route_next_gate_router.get("next_gate_route", {})

    contract = NEXT_GATE_ENTRY_CONTRACTS.get(routed_next_gate)
    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{routed_next_gate}")
    if not route:
        reasons.append("next_gate_route_missing")
        return dedupe(reasons)
    if route.get("gate_id") != routed_next_gate:
        reasons.append(f"next_gate_route_gate_mismatch:{routed_next_gate}")
    if route.get("route_type") != route_type:
        reasons.append(f"next_gate_route_type_mismatch:{route_type}")
    if route.get("route_id") != f"verified_route_next_gate::{route_type}":
        reasons.append(f"next_gate_route_id_mismatch:{route_type}")
    if route.get("routing_status") != "pending_next_auto_mode_gate":
        reasons.append(f"next_gate_route_not_pending:{route_type}")
    if route.get("requires_explicit_next_gate_command") is not True:
        reasons.append(f"next_gate_route_missing_explicit_command_requirement:{route_type}")
    if route.get("this_command_entered_next_gate") is True:
        reasons.append(f"next_gate_route_already_entered:{route_type}")
    if contract is not None and route.get("next_gate_action") not in contract["allowed_actions"]:
        reasons.append(f"next_gate_action_not_allowed:{routed_next_gate}")
    return dedupe(reasons)


def build_status(
    router_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if router_reasons:
        return "blocked_by_verified_route_next_gate_router"
    if boundary_reasons:
        return "blocked_by_routed_next_gate_entry_boundary"
    if contract_reasons:
        return "blocked_by_routed_next_gate_entry_contract"
    return "ready_for_routed_next_gate_entry_review"


def build_source_router_summary(verified_route_next_gate_router: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": verified_route_next_gate_router.get("schema_version", ""),
        "status": verified_route_next_gate_router.get("status", ""),
        "verified_route_type": verified_route_next_gate_router.get("verified_route_type", ""),
        "next_gate_route_recorded": verified_route_next_gate_router.get("next_gate_route_recorded") is True,
        "can_enter_routed_next_gate": verified_route_next_gate_router.get("can_enter_routed_next_gate")
        is True,
        "routed_next_gate": verified_route_next_gate_router.get("routed_next_gate", ""),
        "next_gate_route": verified_route_next_gate_router.get("next_gate_route", {}),
        "this_command_entered_next_gate": verified_route_next_gate_router.get(
            "this_command_entered_next_gate"
        )
        is True,
        "export_or_acceptance_executed": verified_route_next_gate_router.get(
            "export_or_acceptance_executed"
        )
        is True,
        "formal_writeback_executed": verified_route_next_gate_router.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": verified_route_next_gate_router.get(
            "this_command_wrote_formal_state"
        )
        is True,
        "can_write_product_state": verified_route_next_gate_router.get("can_write_product_state") is True,
        "source_blocking_reasons": verified_route_next_gate_router.get("blocking_reasons", []),
        "boundary_flags": verified_route_next_gate_router.get("boundary_flags", {}),
    }


def build_next_gate_entry_plan(verified_route_next_gate_router: dict[str, Any]) -> list[dict[str, Any]]:
    route = verified_route_next_gate_router["next_gate_route"]
    gate_id = verified_route_next_gate_router["routed_next_gate"]
    route_type = verified_route_next_gate_router["verified_route_type"]
    contract = NEXT_GATE_ENTRY_CONTRACTS[gate_id]
    return [
        {
            "entry_id": f"routed_next_gate_entry::{gate_id}::{route_type}",
            "source_route_id": route["route_id"],
            "verified_route_type": route_type,
            "gate_id": gate_id,
            "entry_kind": contract["entry_kind"],
            "next_gate_action": route["next_gate_action"],
            "next_command": contract["next_command"],
            "entry_status": "pending_explicit_next_gate_entry_command",
            "requires_explicit_next_gate_entry_command": True,
            "will_enter_next_gate_by_this_command": False,
            "will_execute_export_or_acceptance_by_this_command": False,
            "will_write_product_state_by_this_command": False,
            "handoff_summary": route.get("description", ""),
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
        "reran_models": False,
        "modified_statistical_execution_artifacts": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "generated_package_manifest": False,
        "performed_manual_acceptance": False,
        "entered_next_gate": False,
        "wrote_formal_state": False,
    }


def build_next_action(
    status: str,
    entry_plan: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == "ready_for_routed_next_gate_entry_review":
        return {
            "id": entry_plan[0]["next_command"],
            "label": "Run explicit routed next-gate entry command",
            "description": "A later command may enter this routed gate; this preflight did not enter it.",
        }
    if status == "blocked_by_routed_next_gate_entry_contract":
        return {
            "id": "repair_routed_next_gate_entry_contract",
            "label": "Repair routed next-gate entry contract",
            "description": "P7-AE must provide one clean pending next-gate route before entry preflight.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_boundary":
        return {
            "id": "resolve_routed_next_gate_entry_boundary_violation",
            "label": "Resolve routed next-gate entry boundary violation",
            "description": "The P7-AF preflight is read-only and cannot consume router side-effect signals.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_verified_route_next_gate_router_blockers",
        "label": "Resolve P7-AE blockers",
        "description": "P7-AE must record a routed next-gate route before entry preflight.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_routed_next_gate_entry_preflight_outputs(
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
        "# Auto Mode Formal Package Routed Next Gate Entry Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        f"- 可请求进入路由下一关：{str(report['can_request_routed_next_gate_entry']).lower()}",
        f"- 需要单独进入命令：{str(report['requires_explicit_next_gate_entry_command']).lower()}",
        f"- 进入计划数：{len(report['next_gate_entry_plan'])}",
        f"- 本命令进入下一关：{str(report['this_command_entered_next_gate']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["next_gate_entry_plan"]:
        lines.extend(["", "## Next Gate Entry Plan"])
        for item in report["next_gate_entry_plan"]:
            lines.append(f"- `{item['entry_id']}` -> `{item['next_command']}`")
            lines.append(f"- gate：`{item['gate_id']}`")
            lines.append(f"- action：`{item['next_gate_action']}`")
            lines.append(
                "- explicit entry command required："
                f"{str(item['requires_explicit_next_gate_entry_command']).lower()}"
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

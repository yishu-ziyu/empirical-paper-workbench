from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_verified_route_next_gate_router.v1"
LEDGER_SCHEMA_VERSION = "p7.auto_mode_formal_package_verified_route_completion_ledger.v1"
DEFAULT_LEDGER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_completion_ledger.json")
DEFAULT_ROUTER_PATH = Path("Results/json/auto_mode_formal_package_verified_route_next_gate_router.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_verified_route_next_gate_router.md")
RECORDED_LEDGER_STATUS = "verified_route_completion_ledger_recorded"
RECORDED_COMPLETION_STATUS = "verified_route_completion_recorded"
NEXT_GATE_BY_ROUTE = {
    "pdf_export": {
        "gate_id": "formal_package_export_acceptance_router",
        "next_gate_action": "continue_formal_package_export_acceptance_cycle",
        "description": "PDF route completion is verified; choose the next export or acceptance route explicitly.",
    },
    "docx_export": {
        "gate_id": "formal_package_export_acceptance_router",
        "next_gate_action": "continue_formal_package_export_acceptance_cycle",
        "description": "DOCX route completion is verified; choose the next export or acceptance route explicitly.",
    },
    "package_manifest": {
        "gate_id": "formal_package_export_acceptance_router",
        "next_gate_action": "continue_formal_package_export_acceptance_cycle",
        "description": "Package manifest completion is verified; choose the next export or acceptance route explicitly.",
    },
    "manual_acceptance": {
        "gate_id": "formal_package_delivery_completion_gate",
        "next_gate_action": "finalize_formal_package_delivery_review",
        "description": "Manual acceptance completion is verified; enter the delivery completion gate.",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_verified_route_next_gate_router(
    verified_route_completion_ledger: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    ledger_reasons = build_ledger_blocking_reasons(verified_route_completion_ledger)
    contract_reasons = []
    boundary_reasons = []
    if not ledger_reasons:
        contract_reasons = build_next_gate_contract_blocking_reasons(verified_route_completion_ledger)
    if not ledger_reasons and not contract_reasons:
        boundary_reasons = build_boundary_blocking_reasons(verified_route_completion_ledger)

    blocking_reasons = dedupe(ledger_reasons + contract_reasons + boundary_reasons)
    status = build_status(ledger_reasons, contract_reasons, boundary_reasons)
    route_recorded = status == "verified_route_next_gate_route_recorded"
    route_type = verified_route_completion_ledger.get("verified_route_type", "")
    next_gate_route = build_next_gate_route(verified_route_completion_ledger) if route_recorded else {}
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": verified_route_completion_ledger.get("topic", ""),
        "source_paths": {
            "verified_route_completion_ledger": source_paths.get(
                "verified_route_completion_ledger",
                str(DEFAULT_LEDGER_PATH),
            ),
        },
        "source_status": verified_route_completion_ledger.get("status", ""),
        "status": status,
        "verified_route_type": route_type if route_recorded else "",
        "next_gate_route_recorded": route_recorded,
        "can_enter_routed_next_gate": route_recorded,
        "routed_next_gate": next_gate_route.get("gate_id", ""),
        "next_gate_route": next_gate_route,
        "route_completion_records_count": len(
            verified_route_completion_ledger.get("route_completion_records", []) or []
        ),
        "route_completion_ledger_recorded": verified_route_completion_ledger.get(
            "route_completion_ledger_recorded"
        )
        is True,
        "can_enter_next_auto_mode_gate": verified_route_completion_ledger.get("can_enter_next_auto_mode_gate")
        is True,
        "export_or_acceptance_executed": False,
        "this_command_entered_next_gate": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_ledger": build_source_ledger_summary(verified_route_completion_ledger),
        "route_completion_records": verified_route_completion_ledger.get("route_completion_records", [])
        if route_recorded
        else [],
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, next_gate_route, blocking_reasons),
    }


def build_ledger_blocking_reasons(verified_route_completion_ledger: dict[str, Any]) -> list[str]:
    reasons = []
    if verified_route_completion_ledger.get("schema_version") != LEDGER_SCHEMA_VERSION:
        reasons.append("verified_route_completion_ledger_missing_or_invalid_schema")
    if verified_route_completion_ledger.get("status") != RECORDED_LEDGER_STATUS:
        reasons.append("verified_route_completion_ledger_status_not_recorded")
    if verified_route_completion_ledger.get("route_completion_ledger_recorded") is not True:
        reasons.append("verified_route_completion_ledger_not_recorded")
    if verified_route_completion_ledger.get("can_enter_next_auto_mode_gate") is not True:
        reasons.append("verified_route_completion_ledger_cannot_enter_next_gate")
    if verified_route_completion_ledger.get("blocking_reasons"):
        reasons.append("source_ledger_has_blocking_reasons")
    return dedupe(reasons)


def build_next_gate_contract_blocking_reasons(verified_route_completion_ledger: dict[str, Any]) -> list[str]:
    route_type = verified_route_completion_ledger.get("verified_route_type", "")
    records = verified_route_completion_ledger.get("route_completion_records", []) or []
    reasons = []
    if not route_type:
        reasons.append("verified_route_type_missing")
    elif route_type not in NEXT_GATE_BY_ROUTE:
        reasons.append(f"verified_route_type_unknown:{route_type}")
    if len(records) != 1:
        reasons.append("route_completion_records_missing" if not records else "route_completion_records_not_single")
        return dedupe(reasons)
    record = records[0]
    record_route_type = record.get("route_type", "")
    if record_route_type != route_type:
        reasons.append(f"route_completion_record_route_mismatch:{route_type}")
    if record.get("completion_status") != RECORDED_COMPLETION_STATUS:
        reasons.append(f"route_completion_record_not_recorded:{route_type}")
    if record.get("completion_id") != f"verified_route_completion::{route_type}":
        reasons.append(f"route_completion_id_mismatch:{route_type}")
    if record.get("can_enter_next_auto_mode_gate") is not True:
        reasons.append(f"route_completion_record_cannot_enter_next_gate:{route_type}")
    if record.get("formal_writeback_executed") is True:
        reasons.append(f"route_completion_record_formal_writeback_executed:{route_type}")
    if record.get("this_command_wrote_formal_state") is True:
        reasons.append(f"route_completion_record_wrote_formal_state:{route_type}")
    if record.get("can_write_product_state") is True:
        reasons.append(f"route_completion_record_allows_product_state_write:{route_type}")
    if not record.get("verified_artifacts"):
        reasons.append(f"route_completion_record_artifacts_missing:{route_type}")
    return dedupe(reasons)


def build_boundary_blocking_reasons(verified_route_completion_ledger: dict[str, Any]) -> list[str]:
    reasons = []
    if verified_route_completion_ledger.get("formal_writeback_executed") is True:
        reasons.append("source_ledger_formal_writeback_executed")
    if verified_route_completion_ledger.get("this_command_wrote_formal_state") is True:
        reasons.append("source_ledger_wrote_formal_state")
    if verified_route_completion_ledger.get("can_write_product_state") is True:
        reasons.append("source_ledger_allows_product_state_write")
    for flag, value in verified_route_completion_ledger.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"source_ledger_boundary_violation:{flag}")
    return dedupe(reasons)


def build_status(
    ledger_reasons: list[str],
    contract_reasons: list[str],
    boundary_reasons: list[str],
) -> str:
    if ledger_reasons:
        return "blocked_by_verified_route_completion_ledger"
    if contract_reasons:
        return "blocked_by_verified_route_next_gate_contract"
    if boundary_reasons:
        return "blocked_by_verified_route_next_gate_boundary"
    return "verified_route_next_gate_route_recorded"


def build_next_gate_route(verified_route_completion_ledger: dict[str, Any]) -> dict[str, Any]:
    route_type = verified_route_completion_ledger.get("verified_route_type", "")
    mapping = NEXT_GATE_BY_ROUTE[route_type]
    return {
        "route_id": f"verified_route_next_gate::{route_type}",
        "route_type": route_type,
        "gate_id": mapping["gate_id"],
        "next_gate_action": mapping["next_gate_action"],
        "routing_status": "pending_next_auto_mode_gate",
        "requires_explicit_next_gate_command": True,
        "this_command_entered_next_gate": False,
        "description": mapping["description"],
    }


def build_source_ledger_summary(verified_route_completion_ledger: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": verified_route_completion_ledger.get("schema_version", ""),
        "status": verified_route_completion_ledger.get("status", ""),
        "verified_route_type": verified_route_completion_ledger.get("verified_route_type", ""),
        "route_completion_ledger_recorded": verified_route_completion_ledger.get(
            "route_completion_ledger_recorded"
        )
        is True,
        "can_enter_next_auto_mode_gate": verified_route_completion_ledger.get("can_enter_next_auto_mode_gate")
        is True,
        "route_completion_records_count": len(
            verified_route_completion_ledger.get("route_completion_records", []) or []
        ),
        "formal_writeback_executed": verified_route_completion_ledger.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": verified_route_completion_ledger.get(
            "this_command_wrote_formal_state"
        )
        is True,
        "can_write_product_state": verified_route_completion_ledger.get("can_write_product_state") is True,
        "blocking_reasons": verified_route_completion_ledger.get("blocking_reasons", []),
        "boundary_flags": verified_route_completion_ledger.get("boundary_flags", {}),
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
    }


def build_next_action(
    status: str,
    next_gate_route: dict[str, Any],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == "verified_route_next_gate_route_recorded":
        return {
            "id": next_gate_route["gate_id"],
            "label": "Run routed next Auto Mode gate",
            "description": next_gate_route["description"],
        }
    if status == "blocked_by_verified_route_completion_ledger":
        return {
            "id": "resolve_verified_route_completion_ledger_blockers",
            "label": "Resolve P7-AD blockers",
            "description": "P7-AD must record a verified route completion ledger before routing.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_route_next_gate_contract":
        return {
            "id": "repair_verified_route_next_gate_contract",
            "label": "Repair verified route next-gate contract",
            "description": "The ledger must contain exactly one clean completion record with a known route type.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_verified_route_next_gate_boundary_violation",
        "label": "Resolve next-gate boundary violation",
        "description": "The next-gate router is read-only and cannot consume a ledger with state-write flags.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_verified_route_next_gate_router_outputs(
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
        "# Auto Mode Formal Package Verified Route Next Gate Router",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 已记录下一关路由：{str(report['next_gate_route_recorded']).lower()}",
        f"- 可进入路由下一关：{str(report['can_enter_routed_next_gate']).lower()}",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        f"- route completion records：{report['route_completion_records_count']}",
        f"- 本命令进入下一关：{str(report['this_command_entered_next_gate']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["next_gate_route"]:
        route = report["next_gate_route"]
        lines.extend(["", "## Next Gate Route"])
        lines.append(f"- `{route['route_id']}` -> `{route['gate_id']}`")
        lines.append(f"- action：`{route['next_gate_action']}`")
        lines.append(f"- explicit command required：{str(route['requires_explicit_next_gate_command']).lower()}")
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

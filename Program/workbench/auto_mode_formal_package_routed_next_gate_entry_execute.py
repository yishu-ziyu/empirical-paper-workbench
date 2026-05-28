from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_routed_next_gate_entry_execute.v1"
ENTRY_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_package_routed_next_gate_entry_manifest.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_package_routed_next_gate_entry_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json")
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_routed_next_gate_entry_execute.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_routed_next_gate_entry_execute.md")
DEFAULT_ENTRY_MANIFEST_PATH = Path(
    "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
)
VALID_MODES = {"dry-run", "execute"}

GATE_ENTRY_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "allowed_actions": {"continue_formal_package_export_acceptance_cycle"},
        "next_command": "auto_mode_formal_package_export_acceptance_router",
        "entry_kind": "continue_export_acceptance_cycle",
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "allowed_actions": {"finalize_formal_package_delivery_review"},
        "next_command": "auto_mode_formal_package_delivery_completion_gate",
        "entry_kind": "delivery_completion",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_routed_next_gate_entry_execute(
    routed_next_gate_entry_preflight: dict[str, Any],
    mode: str = "dry-run",
    confirm_entry: bool = False,
    reviewer: str = "",
    note: str = "",
    entry_manifest_path: Path = DEFAULT_ENTRY_MANIFEST_PATH,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(routed_next_gate_entry_preflight)
    contract_reasons = (
        build_entry_plan_contract_blocking_reasons(routed_next_gate_entry_preflight)
        if not preflight_reasons
        else []
    )
    entry_reasons = build_entry_blocking_reasons(mode, confirm_entry, reviewer, note)
    blocking_reasons = dedupe(preflight_reasons + contract_reasons + entry_reasons)
    status = build_status(mode, preflight_reasons, contract_reasons, entry_reasons)
    operations = (
        build_routed_next_gate_entry_operations(routed_next_gate_entry_preflight)
        if not preflight_reasons and not contract_reasons
        else []
    )
    manifest_recorded = status == "routed_next_gate_entry_manifest_recorded"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": routed_next_gate_entry_preflight.get("topic", ""),
        "source_paths": {
            "routed_next_gate_entry_preflight": source_paths.get(
                "routed_next_gate_entry_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "source_status": routed_next_gate_entry_preflight.get("status", ""),
        "status": status,
        "mode": mode,
        "confirm_entry": confirm_entry,
        "verified_route_type": routed_next_gate_entry_preflight.get("verified_route_type", "")
        if operations
        else "",
        "routed_next_gate": routed_next_gate_entry_preflight.get("routed_next_gate", "") if operations else "",
        "can_enter_routed_next_gate_with_confirmation": not preflight_reasons and not contract_reasons,
        "routed_next_gate_entry_manifest_recorded": manifest_recorded,
        "routed_next_gate_entry_manifest_path": str(entry_manifest_path) if manifest_recorded else "",
        "next_gate_entry_manifested": manifest_recorded,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "next_gate_command_executed": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_preflight": build_source_preflight(routed_next_gate_entry_preflight),
        "entry_request": build_entry_request(mode, confirm_entry, reviewer, note),
        "routed_next_gate_entry_operations": operations,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_preflight_blocking_reasons(routed_next_gate_entry_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if routed_next_gate_entry_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("routed_next_gate_entry_preflight_missing_or_invalid_schema")
    if routed_next_gate_entry_preflight.get("status") != "ready_for_routed_next_gate_entry_review":
        reasons.append("routed_next_gate_entry_preflight_not_ready")
    if routed_next_gate_entry_preflight.get("can_request_routed_next_gate_entry") is not True:
        reasons.append("routed_next_gate_entry_preflight_cannot_request_entry")
    if routed_next_gate_entry_preflight.get("requires_explicit_next_gate_entry_command") is not True:
        reasons.append("routed_next_gate_entry_preflight_missing_explicit_command_requirement")
    if not routed_next_gate_entry_preflight.get("verified_route_type"):
        reasons.append("routed_next_gate_entry_preflight_verified_route_type_missing")
    if not routed_next_gate_entry_preflight.get("routed_next_gate"):
        reasons.append("routed_next_gate_entry_preflight_routed_next_gate_missing")
    if routed_next_gate_entry_preflight.get("next_gate_entered") is True:
        reasons.append("routed_next_gate_entry_preflight_already_entered_next_gate")
    if routed_next_gate_entry_preflight.get("this_command_entered_next_gate") is True:
        reasons.append("routed_next_gate_entry_preflight_entered_next_gate")
    if routed_next_gate_entry_preflight.get("export_or_acceptance_executed") is True:
        reasons.append("routed_next_gate_entry_preflight_executed_export_or_acceptance")
    if routed_next_gate_entry_preflight.get("formal_writeback_executed") is True:
        reasons.append("routed_next_gate_entry_preflight_executed_formal_writeback")
    if routed_next_gate_entry_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("routed_next_gate_entry_preflight_wrote_formal_state")
    if routed_next_gate_entry_preflight.get("can_write_product_state") is True:
        reasons.append("routed_next_gate_entry_preflight_allows_product_state_write")
    if routed_next_gate_entry_preflight.get("blocking_reasons"):
        reasons.append("source_preflight_has_blocking_reasons")
    if not routed_next_gate_entry_preflight.get("next_gate_entry_plan"):
        reasons.append("routed_next_gate_entry_plan_missing")
    for flag, value in routed_next_gate_entry_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"routed_next_gate_entry_preflight_boundary_violation:{flag}")
    return dedupe(reasons)


def build_entry_plan_contract_blocking_reasons(
    routed_next_gate_entry_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    plan = routed_next_gate_entry_preflight.get("next_gate_entry_plan", [])
    if len(plan) != 1:
        reasons.append("routed_next_gate_entry_plan_not_single")
        return reasons

    item = plan[0]
    route_type = item.get("verified_route_type", "unknown")
    routed_next_gate = routed_next_gate_entry_preflight.get("routed_next_gate", "")
    contract = GATE_ENTRY_CONTRACTS.get(routed_next_gate)
    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{routed_next_gate}")
    else:
        if route_type not in contract["allowed_route_types"]:
            reasons.append(f"routed_next_gate_entry_route_type_not_allowed:{route_type}")
        if item.get("next_gate_action") not in contract["allowed_actions"]:
            reasons.append(f"routed_next_gate_entry_action_not_allowed:{routed_next_gate}")
        if item.get("next_command") != contract["next_command"]:
            reasons.append(f"routed_next_gate_entry_next_command_mismatch:{route_type}")
        if item.get("entry_kind") != contract["entry_kind"]:
            reasons.append(f"routed_next_gate_entry_kind_mismatch:{route_type}")

    if item.get("gate_id") != routed_next_gate:
        reasons.append(f"routed_next_gate_entry_gate_mismatch:{routed_next_gate}")
    if route_type != routed_next_gate_entry_preflight.get("verified_route_type", ""):
        reasons.append(f"routed_next_gate_entry_route_type_mismatch:{route_type}")
    if item.get("entry_id") != f"routed_next_gate_entry::{routed_next_gate}::{route_type}":
        reasons.append(f"routed_next_gate_entry_id_mismatch:{route_type}")
    if not item.get("source_route_id"):
        reasons.append(f"routed_next_gate_entry_source_route_missing:{route_type}")
    if not item.get("next_command"):
        reasons.append(f"routed_next_gate_entry_next_command_missing:{route_type}")
    if item.get("entry_status") != "pending_explicit_next_gate_entry_command":
        reasons.append(f"routed_next_gate_entry_not_pending:{route_type}")
    if item.get("requires_explicit_next_gate_entry_command") is not True:
        reasons.append(f"routed_next_gate_entry_missing_explicit_command_requirement:{route_type}")
    if item.get("will_enter_next_gate_by_this_command") is True:
        reasons.append(f"routed_next_gate_entry_marked_enter_by_this_command:{route_type}")
    if item.get("will_execute_export_or_acceptance_by_this_command") is True:
        reasons.append(f"routed_next_gate_entry_marked_export_or_acceptance:{route_type}")
    if item.get("will_write_product_state_by_this_command") is True:
        reasons.append(f"routed_next_gate_entry_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_entry_blocking_reasons(
    mode: str,
    confirm_entry: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["routed_next_gate_entry_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_entry:
        reasons.append("confirm_entry_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("entry_note_required")
    return reasons


def build_status(
    mode: str,
    preflight_reasons: list[str],
    contract_reasons: list[str],
    entry_reasons: list[str],
) -> str:
    if preflight_reasons:
        return "blocked_by_routed_next_gate_entry_preflight"
    if contract_reasons:
        return "blocked_by_routed_next_gate_entry_contract"
    if "routed_next_gate_entry_mode_invalid" in entry_reasons:
        return "blocked_by_routed_next_gate_entry_mode"
    if mode == "dry-run":
        return "routed_next_gate_entry_dry_run_ready"
    if "confirm_entry_required" in entry_reasons:
        return "blocked_by_missing_routed_next_gate_entry_confirmation"
    if entry_reasons:
        return "blocked_by_routed_next_gate_entry_metadata"
    return "routed_next_gate_entry_manifest_recorded"


def build_source_preflight(routed_next_gate_entry_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": routed_next_gate_entry_preflight.get("schema_version", ""),
        "status": routed_next_gate_entry_preflight.get("status", ""),
        "verified_route_type": routed_next_gate_entry_preflight.get("verified_route_type", ""),
        "routed_next_gate": routed_next_gate_entry_preflight.get("routed_next_gate", ""),
        "can_request_routed_next_gate_entry": routed_next_gate_entry_preflight.get(
            "can_request_routed_next_gate_entry"
        )
        is True,
        "requires_explicit_next_gate_entry_command": routed_next_gate_entry_preflight.get(
            "requires_explicit_next_gate_entry_command"
        )
        is True,
        "next_gate_entered": routed_next_gate_entry_preflight.get("next_gate_entered") is True,
        "this_command_entered_next_gate": routed_next_gate_entry_preflight.get(
            "this_command_entered_next_gate"
        )
        is True,
        "export_or_acceptance_executed": routed_next_gate_entry_preflight.get(
            "export_or_acceptance_executed"
        )
        is True,
        "formal_writeback_executed": routed_next_gate_entry_preflight.get("formal_writeback_executed")
        is True,
        "this_command_wrote_formal_state": routed_next_gate_entry_preflight.get(
            "this_command_wrote_formal_state"
        )
        is True,
        "can_write_product_state": routed_next_gate_entry_preflight.get("can_write_product_state") is True,
        "entry_plan_count": len(routed_next_gate_entry_preflight.get("next_gate_entry_plan", [])),
        "blocking_reasons": routed_next_gate_entry_preflight.get("blocking_reasons", []),
        "boundary_flags": routed_next_gate_entry_preflight.get("boundary_flags", {}),
    }


def build_entry_request(mode: str, confirm_entry: bool, reviewer: str, note: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_entry": confirm_entry,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_routed_next_gate_entry_operations(
    routed_next_gate_entry_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = []
    for item in routed_next_gate_entry_preflight.get("next_gate_entry_plan", []):
        route_type = item.get("verified_route_type", "")
        gate_id = item.get("gate_id", "")
        operations.append(
            {
                "operation_id": f"routed_next_gate_entry_execute::{gate_id}::{route_type}",
                "entry_id": item.get("entry_id", ""),
                "source_route_id": item.get("source_route_id", ""),
                "verified_route_type": route_type,
                "gate_id": gate_id,
                "entry_kind": item.get("entry_kind", ""),
                "next_gate_action": item.get("next_gate_action", ""),
                "next_command": item.get("next_command", ""),
                "operation_status": "planned_not_entered",
                "will_record_entry_manifest_on_confirm": True,
                "will_enter_next_gate": False,
                "will_run_next_gate_command": False,
                "will_execute_export_or_acceptance": False,
                "will_write_product_state": False,
                "handoff_summary": item.get("handoff_summary", ""),
            }
        )
    return operations


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
    if status == "routed_next_gate_entry_dry_run_ready":
        return {
            "id": "review_routed_next_gate_entry_dry_run_then_confirm_manifest",
            "label": "Review routed next-gate entry dry-run",
            "description": "Dry-run is ready; a confirmed execute can record the routed next-gate entry manifest.",
        }
    if status == "routed_next_gate_entry_manifest_recorded":
        return {
            "id": "run_manifested_routed_next_gate",
            "label": "Run manifested routed next gate",
            "description": "Entry manifest is recorded; a later node may run the next gate command.",
        }
    if status == "blocked_by_missing_routed_next_gate_entry_confirmation":
        return {
            "id": "rerun_with_confirm_entry",
            "label": "Rerun with explicit confirm entry",
            "description": "Execute mode requires --confirm-entry.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_metadata":
        return {
            "id": "record_entry_reviewer_and_note",
            "label": "Record entry reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_mode":
        return {
            "id": "choose_valid_routed_next_gate_entry_mode",
            "label": "Choose valid routed next-gate entry mode",
            "description": "Mode must be dry-run or execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_routed_next_gate_entry_contract":
        return {
            "id": "repair_routed_next_gate_entry_execute_contract",
            "label": "Repair routed next-gate entry execute contract",
            "description": "P7-AF must expose exactly one clean entry plan before the execute gate can continue.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_routed_next_gate_entry_preflight_blockers",
        "label": "Resolve routed next-gate entry preflight blockers",
        "description": "Routed next-gate entry execute cannot proceed until P7-AF is ready.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_routed_next_gate_entry_execute_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTE_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
    entry_manifest_path: Path = DEFAULT_ENTRY_MANIFEST_PATH,
) -> tuple[Path, Path, Path | None]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    absolute_manifest = None
    if report["routed_next_gate_entry_manifest_recorded"]:
        absolute_manifest = project_root / entry_manifest_path
        absolute_manifest.parent.mkdir(parents=True, exist_ok=True)
        absolute_manifest.write_text(
            json.dumps(build_entry_manifest(report, entry_manifest_path), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return absolute_report, absolute_review, absolute_manifest


def build_entry_manifest(report: dict[str, Any], entry_manifest_path: Path) -> dict[str, Any]:
    return {
        "schema_version": ENTRY_MANIFEST_SCHEMA_VERSION,
        "generated_at": report["generated_at"],
        "topic": report.get("topic", ""),
        "source_execute_report": str(DEFAULT_EXECUTE_PATH),
        "manifest_path": str(entry_manifest_path),
        "reviewer": report["entry_request"]["reviewer"],
        "note": report["entry_request"]["note"],
        "verified_route_type": report.get("verified_route_type", ""),
        "routed_next_gate": report.get("routed_next_gate", ""),
        "next_gate_entry_manifested": True,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "next_gate_command_executed": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "routed_next_gate_entry_operations": report["routed_next_gate_entry_operations"],
        "boundary_flags": build_boundary_flags(),
    }


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Formal Package Routed Next Gate Entry Execute",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        f"- 可确认进入下一关：{str(report['can_enter_routed_next_gate_with_confirmation']).lower()}",
        f"- entry manifest 已记录：{str(report['routed_next_gate_entry_manifest_recorded']).lower()}",
        f"- entry operation 数：{len(report['routed_next_gate_entry_operations'])}",
        f"- 已进入下一关：{str(report['next_gate_entered']).lower()}",
        f"- 已运行下一关命令：{str(report['next_gate_command_executed']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Routed Next Gate Entry Operations"])
    if report["routed_next_gate_entry_operations"]:
        for operation in report["routed_next_gate_entry_operations"]:
            lines.append(f"- `{operation['operation_id']}`: {operation['operation_status']}")
            lines.append(f"- next command：`{operation['next_command']}`")
    else:
        lines.append("- 无；等待 routed next-gate entry preflight ready。")
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

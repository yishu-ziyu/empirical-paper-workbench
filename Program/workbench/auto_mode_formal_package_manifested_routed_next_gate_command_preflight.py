from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_manifested_routed_next_gate_command_preflight.v1"
ENTRY_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_package_routed_next_gate_entry_manifest.v1"
DEFAULT_ENTRY_MANIFEST_PATH = Path(
    "workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json"
)
DEFAULT_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json"
)
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.md")

NEXT_GATE_COMMAND_CONTRACTS = {
    "formal_package_export_acceptance_router": {
        "allowed_route_types": {"pdf_export", "docx_export", "package_manifest"},
        "allowed_actions": {"continue_formal_package_export_acceptance_cycle"},
        "next_command": "auto_mode_formal_package_export_acceptance_router",
        "command_path": "Program/auto_mode_formal_package_export_acceptance_router.py",
        "command_kind": "continue_export_acceptance_cycle",
    },
    "formal_package_delivery_completion_gate": {
        "allowed_route_types": {"manual_acceptance"},
        "allowed_actions": {"finalize_formal_package_delivery_review"},
        "next_command": "auto_mode_formal_package_delivery_completion_gate",
        "command_path": "Program/auto_mode_formal_package_delivery_completion_gate.py",
        "command_kind": "delivery_completion",
    },
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(
    routed_next_gate_entry_manifest: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    manifest_reasons = build_manifest_blocking_reasons(routed_next_gate_entry_manifest)
    boundary_reasons = (
        build_boundary_blocking_reasons(routed_next_gate_entry_manifest) if not manifest_reasons else []
    )
    contract_reasons = (
        build_contract_blocking_reasons(routed_next_gate_entry_manifest)
        if not manifest_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = dedupe(manifest_reasons + boundary_reasons + contract_reasons)
    status = build_status(manifest_reasons, boundary_reasons, contract_reasons)
    ready = status == "ready_for_manifested_routed_next_gate_command_review"
    command_plan = build_next_gate_command_call_plan(routed_next_gate_entry_manifest) if ready else []

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": routed_next_gate_entry_manifest.get("topic", ""),
        "source_paths": {
            "routed_next_gate_entry_manifest": source_paths.get(
                "routed_next_gate_entry_manifest",
                str(DEFAULT_ENTRY_MANIFEST_PATH),
            ),
        },
        "source_status": "manifested" if routed_next_gate_entry_manifest.get("next_gate_entry_manifested") else "",
        "status": status,
        "verified_route_type": routed_next_gate_entry_manifest.get("verified_route_type", "") if ready else "",
        "routed_next_gate": routed_next_gate_entry_manifest.get("routed_next_gate", "") if ready else "",
        "can_request_manifested_next_gate_command_execution": ready,
        "requires_explicit_next_gate_command_execute": ready,
        "next_gate_command_executed": False,
        "this_command_ran_next_gate_command": False,
        "next_gate_entered": False,
        "this_command_entered_next_gate": False,
        "export_or_acceptance_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_manifest": build_source_manifest_summary(routed_next_gate_entry_manifest),
        "next_gate_command_call_plan": command_plan,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, command_plan, blocking_reasons),
    }


def build_manifest_blocking_reasons(routed_next_gate_entry_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    if routed_next_gate_entry_manifest.get("schema_version") != ENTRY_MANIFEST_SCHEMA_VERSION:
        reasons.append("routed_next_gate_entry_manifest_missing_or_invalid_schema")
    if routed_next_gate_entry_manifest.get("next_gate_entry_manifested") is not True:
        reasons.append("routed_next_gate_entry_not_manifested")
    if not routed_next_gate_entry_manifest.get("verified_route_type"):
        reasons.append("routed_next_gate_entry_manifest_verified_route_type_missing")
    if not routed_next_gate_entry_manifest.get("routed_next_gate"):
        reasons.append("routed_next_gate_entry_manifest_routed_next_gate_missing")
    return dedupe(reasons)


def build_boundary_blocking_reasons(routed_next_gate_entry_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    if routed_next_gate_entry_manifest.get("next_gate_entered") is True:
        reasons.append("routed_next_gate_entry_manifest_entered_next_gate")
    if routed_next_gate_entry_manifest.get("this_command_entered_next_gate") is True:
        reasons.append("routed_next_gate_entry_manifest_entered_next_gate")
    if routed_next_gate_entry_manifest.get("next_gate_command_executed") is True:
        reasons.append("routed_next_gate_entry_manifest_ran_next_gate_command")
    if routed_next_gate_entry_manifest.get("export_or_acceptance_executed") is True:
        reasons.append("routed_next_gate_entry_manifest_executed_export_or_acceptance")
    if routed_next_gate_entry_manifest.get("formal_writeback_executed") is True:
        reasons.append("routed_next_gate_entry_manifest_executed_formal_writeback")
    if routed_next_gate_entry_manifest.get("this_command_wrote_formal_state") is True:
        reasons.append("routed_next_gate_entry_manifest_wrote_formal_state")
    if routed_next_gate_entry_manifest.get("can_write_product_state") is True:
        reasons.append("routed_next_gate_entry_manifest_allows_product_state_write")
    for flag, value in routed_next_gate_entry_manifest.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"routed_next_gate_entry_manifest_boundary_violation:{flag}")
    return dedupe(reasons)


def build_contract_blocking_reasons(routed_next_gate_entry_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    operations = routed_next_gate_entry_manifest.get("routed_next_gate_entry_operations", [])
    if not operations:
        return ["routed_next_gate_entry_operations_missing"]
    if not isinstance(operations, list) or len(operations) != 1:
        return ["routed_next_gate_entry_operations_not_single"]

    operation = operations[0]
    route_type = operation.get("verified_route_type", "")
    routed_next_gate = routed_next_gate_entry_manifest.get("routed_next_gate", "")
    manifest_route_type = routed_next_gate_entry_manifest.get("verified_route_type", "")
    contract = NEXT_GATE_COMMAND_CONTRACTS.get(routed_next_gate)

    if contract is None:
        reasons.append(f"routed_next_gate_unknown:{routed_next_gate}")
    else:
        if route_type not in contract["allowed_route_types"]:
            reasons.append(f"next_gate_command_route_type_not_allowed:{route_type}")
        if operation.get("next_gate_action") not in contract["allowed_actions"]:
            reasons.append(f"next_gate_command_action_not_allowed:{routed_next_gate}")
        next_command = operation.get("next_command", "")
        if not next_command:
            reasons.append(f"next_gate_command_missing:{route_type}")
        elif next_command != contract["next_command"]:
            reasons.append(f"next_gate_command_mismatch:{route_type}")

    if operation.get("gate_id") != routed_next_gate:
        reasons.append(f"routed_next_gate_entry_operation_gate_mismatch:{routed_next_gate}")
    if route_type != manifest_route_type:
        reasons.append(f"routed_next_gate_entry_operation_route_type_mismatch:{route_type}")
    if operation.get("operation_status") != "planned_not_entered":
        reasons.append(f"routed_next_gate_entry_operation_not_planned:{route_type}")
    if operation.get("entry_id") != f"routed_next_gate_entry::{routed_next_gate}::{route_type}":
        reasons.append(f"routed_next_gate_entry_id_mismatch:{route_type}")
    if not operation.get("operation_id"):
        reasons.append(f"routed_next_gate_entry_operation_id_missing:{route_type}")
    if operation.get("will_run_next_gate_command") is True:
        reasons.append(f"next_gate_command_operation_marked_run_command:{route_type}")
    if operation.get("will_enter_next_gate") is True:
        reasons.append(f"next_gate_command_operation_marked_enter_next_gate:{route_type}")
    if operation.get("will_execute_export_or_acceptance") is True:
        reasons.append(f"next_gate_command_operation_marked_export_or_acceptance:{route_type}")
    if operation.get("will_write_product_state") is True:
        reasons.append(f"next_gate_command_operation_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_status(
    manifest_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if manifest_reasons:
        return "blocked_by_routed_next_gate_entry_manifest"
    if boundary_reasons:
        return "blocked_by_manifested_routed_next_gate_command_boundary"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_command_contract"
    return "ready_for_manifested_routed_next_gate_command_review"


def build_source_manifest_summary(routed_next_gate_entry_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": routed_next_gate_entry_manifest.get("schema_version", ""),
        "verified_route_type": routed_next_gate_entry_manifest.get("verified_route_type", ""),
        "routed_next_gate": routed_next_gate_entry_manifest.get("routed_next_gate", ""),
        "next_gate_entry_manifested": routed_next_gate_entry_manifest.get("next_gate_entry_manifested") is True,
        "next_gate_entered": routed_next_gate_entry_manifest.get("next_gate_entered") is True,
        "this_command_entered_next_gate": routed_next_gate_entry_manifest.get("this_command_entered_next_gate")
        is True,
        "next_gate_command_executed": routed_next_gate_entry_manifest.get("next_gate_command_executed") is True,
        "export_or_acceptance_executed": routed_next_gate_entry_manifest.get("export_or_acceptance_executed")
        is True,
        "formal_writeback_executed": routed_next_gate_entry_manifest.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": routed_next_gate_entry_manifest.get("this_command_wrote_formal_state")
        is True,
        "can_write_product_state": routed_next_gate_entry_manifest.get("can_write_product_state") is True,
        "operation_count": len(routed_next_gate_entry_manifest.get("routed_next_gate_entry_operations", [])),
        "boundary_flags": routed_next_gate_entry_manifest.get("boundary_flags", {}),
    }


def build_next_gate_command_call_plan(
    routed_next_gate_entry_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    operation = routed_next_gate_entry_manifest["routed_next_gate_entry_operations"][0]
    route_type = operation["verified_route_type"]
    gate_id = operation["gate_id"]
    contract = NEXT_GATE_COMMAND_CONTRACTS[gate_id]
    return [
        {
            "command_plan_id": f"manifested_routed_next_gate_command::{gate_id}::{route_type}",
            "source_operation_id": operation["operation_id"],
            "source_entry_id": operation["entry_id"],
            "verified_route_type": route_type,
            "gate_id": gate_id,
            "next_gate_action": operation["next_gate_action"],
            "next_command": contract["next_command"],
            "command_path": contract["command_path"],
            "command_args": ["--project-root", "."],
            "command_kind": contract["command_kind"],
            "command_status": "pending_explicit_next_gate_command_execute",
            "requires_explicit_next_gate_command_execute": True,
            "will_run_next_gate_command_by_this_command": False,
            "will_enter_next_gate_by_this_command": False,
            "will_execute_export_or_acceptance_by_this_command": False,
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
    command_plan: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == "ready_for_manifested_routed_next_gate_command_review":
        return {
            "id": command_plan[0]["next_command"],
            "label": "Review manifested routed next-gate command plan",
            "description": "A later execute gate may run this command after explicit command execution approval.",
        }
    if status == "blocked_by_manifested_routed_next_gate_command_boundary":
        return {
            "id": "resolve_manifested_routed_next_gate_command_boundary",
            "label": "Resolve manifested routed next-gate command boundary",
            "description": "P7-AH only prepares a command plan and cannot consume a manifest with side-effect signals.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_command_contract":
        return {
            "id": "repair_manifested_routed_next_gate_command_contract",
            "label": "Repair manifested routed next-gate command contract",
            "description": "P7-AG must provide exactly one clean next-gate entry operation before command preflight.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "record_routed_next_gate_entry_manifest",
        "label": "Record routed next-gate entry manifest",
        "description": "P7-AG must record an entry manifest before P7-AH can prepare a command plan.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_manifested_routed_next_gate_command_preflight_outputs(
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
        "# Auto Mode Formal Package Manifested Routed Next Gate Command Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- 路由下一关：`{report['routed_next_gate']}`",
        "- 可请求执行下一关命令："
        f"{str(report['can_request_manifested_next_gate_command_execution']).lower()}",
        "- 需要单独 execute 命令："
        f"{str(report['requires_explicit_next_gate_command_execute']).lower()}",
        f"- 命令计划数：{len(report['next_gate_command_call_plan'])}",
        f"- 本命令运行下一关命令：{str(report['this_command_ran_next_gate_command']).lower()}",
        f"- 已进入下一关：{str(report['next_gate_entered']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["next_gate_command_call_plan"]:
        lines.extend(["", "## Next Gate Command Call Plan"])
        for item in report["next_gate_command_call_plan"]:
            lines.append(f"- `{item['command_plan_id']}` -> `{item['next_command']}`")
            lines.append(f"- command path：`{item['command_path']}`")
            lines.append(f"- status：`{item['command_status']}`")
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

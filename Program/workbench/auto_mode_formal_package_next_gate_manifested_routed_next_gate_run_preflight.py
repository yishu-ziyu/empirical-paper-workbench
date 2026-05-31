from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.auto_mode_formal_package_manifested_routed_next_gate_command_preflight import (
    DEFAULT_ENTRY_MANIFEST_PATH,
    build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight,
)


SCHEMA_VERSION = "p7.auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.v1"
EXPLICIT_ENTRY_GATE_SCHEMA_VERSION = (
    "p7.auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.v1"
)
EXPLICIT_ENTRY_GATE_SUCCESS_STATUS = "explicit_routed_next_gate_entry_manifest_recorded"
MANIFESTED_COMMAND_READY_STATUS = "ready_for_manifested_routed_next_gate_command_review"
DEFAULT_EXPLICIT_ENTRY_GATE_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate.json"
)
DEFAULT_RUN_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.json"
)
DEFAULT_RUN_PREFLIGHT_REVIEW_PATH = Path(
    "Reviews/auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight.md"
)


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_dir():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
    explicit_routed_next_gate_entry_gate: dict[str, Any],
    routed_next_gate_entry_manifest: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    gate_reasons = build_gate_blocking_reasons(explicit_routed_next_gate_entry_gate)
    probe = (
        {}
        if gate_reasons
        else build_auto_mode_formal_package_manifested_routed_next_gate_command_preflight(
            routed_next_gate_entry_manifest,
            source_paths={
                "routed_next_gate_entry_manifest": source_paths.get(
                    "routed_next_gate_entry_manifest",
                    str(DEFAULT_ENTRY_MANIFEST_PATH),
                ),
            },
        )
    )
    manifest_reasons, boundary_reasons, manifest_contract_reasons = split_probe_blocking_reasons(probe)
    gate_manifest_contract_reasons = (
        build_gate_manifest_contract_blocking_reasons(
            explicit_routed_next_gate_entry_gate,
            routed_next_gate_entry_manifest,
        )
        if not gate_reasons and not manifest_reasons and not boundary_reasons
        else []
    )
    contract_reasons = dedupe(manifest_contract_reasons + gate_manifest_contract_reasons)
    blocking_reasons = dedupe(gate_reasons + manifest_reasons + boundary_reasons + contract_reasons)
    status = build_status(gate_reasons, manifest_reasons, boundary_reasons, contract_reasons)
    ready = status == "ready_for_manifested_routed_next_gate_run_preflight"
    command_plan = probe.get("next_gate_command_call_plan", []) if ready else []
    input_records = (
        build_manifested_routed_next_gate_run_input_records(
            explicit_routed_next_gate_entry_gate,
            routed_next_gate_entry_manifest,
            command_plan,
            source_paths,
        )
        if ready
        else []
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "topic": explicit_routed_next_gate_entry_gate.get("topic")
        or routed_next_gate_entry_manifest.get("topic", ""),
        "source_paths": {
            "explicit_routed_next_gate_entry_gate": source_paths.get(
                "explicit_routed_next_gate_entry_gate",
                str(DEFAULT_EXPLICIT_ENTRY_GATE_PATH),
            ),
            "routed_next_gate_entry_manifest": source_paths.get(
                "routed_next_gate_entry_manifest",
                str(DEFAULT_ENTRY_MANIFEST_PATH),
            ),
        },
        "source_status": explicit_routed_next_gate_entry_gate.get("status", ""),
        "status": status,
        "verified_route_type": explicit_routed_next_gate_entry_gate.get("verified_route_type", "") if ready else "",
        "routed_next_gate": explicit_routed_next_gate_entry_gate.get("routed_next_gate", "") if ready else "",
        "manifested_routed_next_gate_run_preflight_reviewed": ready,
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
        "source_explicit_routed_next_gate_entry_gate": build_source_gate_summary(
            explicit_routed_next_gate_entry_gate
        ),
        "source_routed_next_gate_entry_manifest": build_source_manifest_summary(
            routed_next_gate_entry_manifest
        ),
        "manifested_command_preflight_probe": build_probe_summary(probe),
        "next_gate_command_call_plan": command_plan,
        "next_gate_command_call_plan_count": len(command_plan),
        "manifested_routed_next_gate_run_input_records": input_records,
        "manifested_routed_next_gate_run_input_record_count": len(input_records),
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, command_plan, blocking_reasons),
    }


def build_gate_blocking_reasons(explicit_routed_next_gate_entry_gate: dict[str, Any]) -> list[str]:
    reasons = []
    if explicit_routed_next_gate_entry_gate.get("schema_version") != EXPLICIT_ENTRY_GATE_SCHEMA_VERSION:
        reasons.append("explicit_routed_next_gate_entry_gate_missing_or_invalid_schema")
    if explicit_routed_next_gate_entry_gate.get("status") != EXPLICIT_ENTRY_GATE_SUCCESS_STATUS:
        reasons.append("explicit_routed_next_gate_entry_gate_not_manifest_recorded")
    if explicit_routed_next_gate_entry_gate.get("routed_next_gate_entry_manifest_recorded") is not True:
        reasons.append("explicit_routed_next_gate_entry_gate_not_manifest_recorded")
    if explicit_routed_next_gate_entry_gate.get("explicit_routed_next_gate_entry_gate_executed") is not True:
        reasons.append("explicit_routed_next_gate_entry_gate_not_executed")
    if explicit_routed_next_gate_entry_gate.get("explicit_routed_next_gate_entry_execute_status") != (
        "routed_next_gate_entry_manifest_recorded"
    ):
        reasons.append("explicit_routed_next_gate_entry_execute_status_not_recorded")
    if not explicit_routed_next_gate_entry_gate.get("verified_route_type"):
        reasons.append("explicit_routed_next_gate_entry_gate_verified_route_type_missing")
    if not explicit_routed_next_gate_entry_gate.get("routed_next_gate"):
        reasons.append("explicit_routed_next_gate_entry_gate_routed_next_gate_missing")
    if not explicit_routed_next_gate_entry_gate.get("routed_next_gate_entry_manifest_path"):
        reasons.append("routed_next_gate_entry_manifest_path_missing")
    if not explicit_routed_next_gate_entry_gate.get("explicit_routed_next_gate_entry_operations"):
        reasons.append("explicit_routed_next_gate_entry_operations_missing")
    if explicit_routed_next_gate_entry_gate.get("blocking_reasons"):
        reasons.append("explicit_routed_next_gate_entry_gate_has_blocking_reasons")

    boundary_fields = {
        "next_gate_entered": "explicit_routed_next_gate_entry_gate_entered_next_gate",
        "this_command_entered_next_gate": "explicit_routed_next_gate_entry_gate_entered_next_gate",
        "next_gate_command_executed": "explicit_routed_next_gate_entry_gate_ran_next_gate_command",
        "export_or_acceptance_executed": "explicit_routed_next_gate_entry_gate_executed_export_or_acceptance",
        "rendered_pdf": "explicit_routed_next_gate_entry_gate_rendered_pdf",
        "rendered_docx": "explicit_routed_next_gate_entry_gate_rendered_docx",
        "package_manifest_generated": "explicit_routed_next_gate_entry_gate_generated_package_manifest",
        "manual_acceptance_performed": "explicit_routed_next_gate_entry_gate_performed_manual_acceptance",
        "formal_writeback_executed": "explicit_routed_next_gate_entry_gate_executed_formal_writeback",
        "this_command_wrote_formal_state": "explicit_routed_next_gate_entry_gate_wrote_formal_state",
        "can_write_product_state": "explicit_routed_next_gate_entry_gate_allows_product_state_write",
    }
    for field, reason in boundary_fields.items():
        if explicit_routed_next_gate_entry_gate.get(field) is True:
            reasons.append(reason)
    for flag, value in explicit_routed_next_gate_entry_gate.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"explicit_routed_next_gate_entry_gate_boundary_violation:{flag}")
    return dedupe(reasons)


def split_probe_blocking_reasons(probe: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    status = probe.get("status", "")
    reasons = probe.get("blocking_reasons", [])
    if status == "blocked_by_routed_next_gate_entry_manifest":
        return reasons, [], []
    if status == "blocked_by_manifested_routed_next_gate_command_boundary":
        return [], reasons, []
    if status == "blocked_by_manifested_routed_next_gate_command_contract":
        return [], [], reasons
    return [], [], []


def build_gate_manifest_contract_blocking_reasons(
    explicit_routed_next_gate_entry_gate: dict[str, Any],
    routed_next_gate_entry_manifest: dict[str, Any],
) -> list[str]:
    route_type = explicit_routed_next_gate_entry_gate.get("verified_route_type", "unknown")
    reasons = []
    gate_route_type = explicit_routed_next_gate_entry_gate.get("verified_route_type", "")
    manifest_route_type = routed_next_gate_entry_manifest.get("verified_route_type", "")
    gate_next_gate = explicit_routed_next_gate_entry_gate.get("routed_next_gate", "")
    manifest_next_gate = routed_next_gate_entry_manifest.get("routed_next_gate", "")
    gate_manifest_path = explicit_routed_next_gate_entry_gate.get("routed_next_gate_entry_manifest_path", "")
    manifest_path = routed_next_gate_entry_manifest.get("manifest_path", "")
    gate_operations = explicit_routed_next_gate_entry_gate.get("explicit_routed_next_gate_entry_operations", [])
    manifest_operations = routed_next_gate_entry_manifest.get("routed_next_gate_entry_operations", [])

    if gate_route_type != manifest_route_type:
        reasons.append(f"gate_manifest_route_type_mismatch:{route_type}")
    if gate_next_gate != manifest_next_gate:
        reasons.append(f"gate_manifest_routed_next_gate_mismatch:{route_type}")
    if gate_manifest_path != str(DEFAULT_ENTRY_MANIFEST_PATH) or manifest_path != str(DEFAULT_ENTRY_MANIFEST_PATH):
        reasons.append(f"routed_next_gate_entry_manifest_path_mismatch:{route_type}")
    if len(gate_operations) != len(manifest_operations):
        reasons.append(f"gate_manifest_operation_count_mismatch:{route_type}")
    if gate_operations and manifest_operations:
        gate_operation = gate_operations[0]
        manifest_operation = manifest_operations[0]
        for field in ["operation_id", "entry_id", "verified_route_type", "gate_id", "next_command"]:
            if gate_operation.get(field) != manifest_operation.get(field):
                reasons.append(f"gate_manifest_operation_{field}_mismatch:{route_type}")
    return dedupe(reasons)


def build_status(
    gate_reasons: list[str],
    manifest_reasons: list[str],
    boundary_reasons: list[str],
    contract_reasons: list[str],
) -> str:
    if gate_reasons:
        return "blocked_by_explicit_routed_next_gate_entry_gate"
    if manifest_reasons:
        return "blocked_by_routed_next_gate_entry_manifest"
    if boundary_reasons:
        return "blocked_by_manifested_routed_next_gate_run_boundary"
    if contract_reasons:
        return "blocked_by_manifested_routed_next_gate_run_contract"
    return "ready_for_manifested_routed_next_gate_run_preflight"


def build_manifested_routed_next_gate_run_input_records(
    explicit_routed_next_gate_entry_gate: dict[str, Any],
    routed_next_gate_entry_manifest: dict[str, Any],
    command_plan: list[dict[str, Any]],
    source_paths: dict[str, str],
) -> list[dict[str, Any]]:
    if not command_plan:
        return []
    route_type = explicit_routed_next_gate_entry_gate["verified_route_type"]
    gate_id = explicit_routed_next_gate_entry_gate["routed_next_gate"]
    plan = command_plan[0]
    return [
        {
            "record_id": f"manifested_routed_next_gate_run_input::{gate_id}::{route_type}",
            "verified_route_type": route_type,
            "routed_next_gate": gate_id,
            "explicit_routed_next_gate_entry_gate_report_path": source_paths.get(
                "explicit_routed_next_gate_entry_gate",
                str(DEFAULT_EXPLICIT_ENTRY_GATE_PATH),
            ),
            "routed_next_gate_entry_manifest_path": source_paths.get(
                "routed_next_gate_entry_manifest",
                str(DEFAULT_ENTRY_MANIFEST_PATH),
            ),
            "manifested_command_preflight_status": MANIFESTED_COMMAND_READY_STATUS,
            "command_plan_id": plan["command_plan_id"],
            "source_operation_id": plan["source_operation_id"],
            "source_entry_id": plan["source_entry_id"],
            "next_command": plan["next_command"],
            "command_path": plan["command_path"],
            "command_kind": plan["command_kind"],
            "requires_explicit_next_gate_command_execute": True,
            "review_status": "manifested_routed_next_gate_run_preflight_ready_for_command_execute_gate",
            "manifest_operation_count": len(routed_next_gate_entry_manifest.get("routed_next_gate_entry_operations", [])),
        }
    ]


def build_source_gate_summary(explicit_routed_next_gate_entry_gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": explicit_routed_next_gate_entry_gate.get("schema_version", ""),
        "status": explicit_routed_next_gate_entry_gate.get("status", ""),
        "verified_route_type": explicit_routed_next_gate_entry_gate.get("verified_route_type", ""),
        "routed_next_gate": explicit_routed_next_gate_entry_gate.get("routed_next_gate", ""),
        "routed_next_gate_entry_manifest_recorded": explicit_routed_next_gate_entry_gate.get(
            "routed_next_gate_entry_manifest_recorded"
        )
        is True,
        "explicit_routed_next_gate_entry_gate_executed": explicit_routed_next_gate_entry_gate.get(
            "explicit_routed_next_gate_entry_gate_executed"
        )
        is True,
        "explicit_routed_next_gate_entry_execute_status": explicit_routed_next_gate_entry_gate.get(
            "explicit_routed_next_gate_entry_execute_status",
            "",
        ),
        "routed_next_gate_entry_manifest_path": explicit_routed_next_gate_entry_gate.get(
            "routed_next_gate_entry_manifest_path",
            "",
        ),
        "operation_count": len(
            explicit_routed_next_gate_entry_gate.get("explicit_routed_next_gate_entry_operations", [])
            or []
        ),
        "blocking_reasons": explicit_routed_next_gate_entry_gate.get("blocking_reasons", []),
        "boundary_flags": explicit_routed_next_gate_entry_gate.get("boundary_flags", {}),
    }


def build_source_manifest_summary(routed_next_gate_entry_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": routed_next_gate_entry_manifest.get("schema_version", ""),
        "verified_route_type": routed_next_gate_entry_manifest.get("verified_route_type", ""),
        "routed_next_gate": routed_next_gate_entry_manifest.get("routed_next_gate", ""),
        "manifest_path": routed_next_gate_entry_manifest.get("manifest_path", ""),
        "next_gate_entry_manifested": routed_next_gate_entry_manifest.get("next_gate_entry_manifested") is True,
        "next_gate_entered": routed_next_gate_entry_manifest.get("next_gate_entered") is True,
        "next_gate_command_executed": routed_next_gate_entry_manifest.get("next_gate_command_executed") is True,
        "export_or_acceptance_executed": routed_next_gate_entry_manifest.get("export_or_acceptance_executed")
        is True,
        "formal_writeback_executed": routed_next_gate_entry_manifest.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": routed_next_gate_entry_manifest.get("this_command_wrote_formal_state")
        is True,
        "can_write_product_state": routed_next_gate_entry_manifest.get("can_write_product_state") is True,
        "operation_count": len(routed_next_gate_entry_manifest.get("routed_next_gate_entry_operations", []) or []),
        "boundary_flags": routed_next_gate_entry_manifest.get("boundary_flags", {}),
    }


def build_probe_summary(probe: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": probe.get("schema_version", ""),
        "status": probe.get("status", ""),
        "verified_route_type": probe.get("verified_route_type", ""),
        "routed_next_gate": probe.get("routed_next_gate", ""),
        "can_request_manifested_next_gate_command_execution": probe.get(
            "can_request_manifested_next_gate_command_execution"
        )
        is True,
        "next_gate_command_call_plan_count": len(probe.get("next_gate_command_call_plan", []) or []),
        "blocking_reasons": probe.get("blocking_reasons", []),
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
    }


def build_next_action(
    status: str,
    command_plan: list[dict[str, Any]],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if status == "ready_for_manifested_routed_next_gate_run_preflight":
        return {
            "id": "manifested_routed_next_gate_command_execute_gate",
            "label": "Review manifested routed next-gate command execute gate",
            "description": "P7-BD may execute the planned command only after explicit command approval.",
            "next_command": command_plan[0]["next_command"],
        }
    if status == "blocked_by_routed_next_gate_entry_manifest":
        return {
            "id": "record_routed_next_gate_entry_manifest",
            "label": "Record routed next-gate entry manifest",
            "description": "P7-BB must provide a valid entry manifest before P7-BC can preflight a run.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_run_boundary":
        return {
            "id": "resolve_manifested_routed_next_gate_run_boundary",
            "label": "Resolve manifested routed next-gate run boundary",
            "description": "P7-BC cannot continue from artifacts that already crossed execution boundaries.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_manifested_routed_next_gate_run_contract":
        return {
            "id": "repair_manifested_routed_next_gate_run_contract",
            "label": "Repair manifested routed next-gate run contract",
            "description": "P7-BB and the entry manifest must point to the same clean next-gate command.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_explicit_routed_next_gate_entry_gate_blockers",
        "label": "Resolve P7-BB blockers",
        "description": "P7-BB must record the routed next-gate entry manifest before P7-BC can continue.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_RUN_PREFLIGHT_PATH,
    review_path: Path = DEFAULT_RUN_PREFLIGHT_REVIEW_PATH,
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
        "# Auto Mode Formal Package Next Gate Manifested Routed Next Gate Run Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- verified route type：`{report['verified_route_type']}`",
        f"- routed next gate：`{report['routed_next_gate']}`",
        "- run preflight 已审阅："
        f"{str(report['manifested_routed_next_gate_run_preflight_reviewed']).lower()}",
        "- 可请求执行下一关命令："
        f"{str(report['can_request_manifested_next_gate_command_execution']).lower()}",
        "- 需要单独 execute 命令："
        f"{str(report['requires_explicit_next_gate_command_execute']).lower()}",
        f"- 命令计划数：{report['next_gate_command_call_plan_count']}",
        f"- run input records：{report['manifested_routed_next_gate_run_input_record_count']}",
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
    if report["manifested_routed_next_gate_run_input_records"]:
        lines.extend(["", "## Run Input Records"])
        for item in report["manifested_routed_next_gate_run_input_records"]:
            lines.append(f"- `{item['record_id']}` -> `{item['next_command']}`")
            lines.append(f"- review status：`{item['review_status']}`")
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

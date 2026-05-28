from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execute.v1"
EXECUTE_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execute_manifest.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_package_selected_route_execution_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execution_preflight.json")
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_package_selected_route_execute.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_selected_route_execute.md")
DEFAULT_EXECUTE_MANIFEST_PATH = Path(
    "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
)
VALID_MODES = {"dry-run", "execute"}
VALID_ROUTE_TYPES = {"pdf_export", "docx_export", "package_manifest", "manual_acceptance"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_selected_route_execute(
    selected_route_execution_preflight: dict[str, Any],
    mode: str = "dry-run",
    confirm_execute: bool = False,
    reviewer: str = "",
    note: str = "",
    execute_manifest_path: Path = DEFAULT_EXECUTE_MANIFEST_PATH,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(selected_route_execution_preflight)
    contract_reasons = (
        build_selected_route_contract_blocking_reasons(selected_route_execution_preflight)
        if not preflight_reasons
        else []
    )
    execute_reasons = build_execute_blocking_reasons(mode, confirm_execute, reviewer, note)
    blocking_reasons = preflight_reasons + contract_reasons + execute_reasons
    status = build_status(mode, preflight_reasons, contract_reasons, execute_reasons)
    operations = (
        build_selected_route_execute_operations(selected_route_execution_preflight)
        if not preflight_reasons and not contract_reasons
        else []
    )
    manifest_recorded = status == "selected_route_execute_manifest_recorded"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": selected_route_execution_preflight.get("topic", ""),
        "source_paths": {
            "selected_route_execution_preflight": source_paths.get(
                "selected_route_execution_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "status": status,
        "mode": mode,
        "confirm_execute": confirm_execute,
        "can_execute_selected_route_with_confirmation": not preflight_reasons and not contract_reasons,
        "selected_route_execute_manifest_recorded": manifest_recorded,
        "selected_route_execute_manifest_path": str(execute_manifest_path) if manifest_recorded else "",
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
        "source_preflight": build_source_preflight(selected_route_execution_preflight),
        "execute_request": build_execute_request(mode, confirm_execute, reviewer, note),
        "selected_route_execute_operations": operations,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_preflight_blocking_reasons(selected_route_execution_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if selected_route_execution_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("selected_route_execution_preflight_missing_or_invalid_schema")
    if selected_route_execution_preflight.get("status") != "ready_for_selected_formal_package_route_execution_review":
        reasons.append("selected_route_execution_preflight_not_ready")
    if selected_route_execution_preflight.get("can_request_selected_route_execution") is not True:
        reasons.append("selected_route_execution_preflight_cannot_request_execution")
    if selected_route_execution_preflight.get("requires_explicit_route_execute_command") is not True:
        reasons.append("selected_route_execution_preflight_missing_explicit_command_requirement")
    if selected_route_execution_preflight.get("selected_route_executed") is True:
        reasons.append("selected_route_execution_preflight_already_executed_selected_route")
    if selected_route_execution_preflight.get("export_or_acceptance_executed") is True:
        reasons.append("selected_route_execution_preflight_already_executed_export_or_acceptance")
    if selected_route_execution_preflight.get("rendered_pdf") is True:
        reasons.append("selected_route_execution_preflight_rendered_pdf")
    if selected_route_execution_preflight.get("rendered_docx") is True:
        reasons.append("selected_route_execution_preflight_rendered_docx")
    if selected_route_execution_preflight.get("package_manifest_generated") is True:
        reasons.append("selected_route_execution_preflight_generated_package_manifest")
    if selected_route_execution_preflight.get("manual_acceptance_performed") is True:
        reasons.append("selected_route_execution_preflight_performed_manual_acceptance")
    if selected_route_execution_preflight.get("formal_writeback_executed") is True:
        reasons.append("selected_route_execution_preflight_executed_formal_writeback")
    if selected_route_execution_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("selected_route_execution_preflight_wrote_formal_state")
    if selected_route_execution_preflight.get("can_write_product_state") is True:
        reasons.append("selected_route_execution_preflight_allows_product_state_write")
    if not selected_route_execution_preflight.get("selected_route_execution_plan"):
        reasons.append("selected_route_execution_plan_missing")
    for flag, value in selected_route_execution_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"selected_route_execution_preflight_boundary_violation:{flag}")
    return dedupe(reasons)


def build_selected_route_contract_blocking_reasons(
    selected_route_execution_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    plan = selected_route_execution_preflight.get("selected_route_execution_plan", [])
    if len(plan) != 1:
        reasons.append("selected_route_execution_plan_not_single")
        return reasons
    item = plan[0]
    route_type = item.get("route_type", "unknown")
    if route_type not in VALID_ROUTE_TYPES:
        reasons.append(f"selected_route_type_unknown:{route_type}")
    if not item.get("route_execution_id"):
        reasons.append(f"selected_route_execution_id_missing:{route_type}")
    if not item.get("routed_action"):
        reasons.append(f"selected_route_routed_action_missing:{route_type}")
    if not item.get("next_command"):
        reasons.append(f"selected_route_next_command_missing:{route_type}")
    if not item.get("planned_outputs"):
        reasons.append(f"selected_route_planned_outputs_missing:{route_type}")
    if item.get("execution_status") != "pending_explicit_route_execute_command":
        reasons.append(f"selected_route_not_pending:{route_type}")
    if item.get("requires_explicit_route_execute_command") is not True:
        reasons.append(f"selected_route_missing_explicit_command_requirement:{route_type}")
    if item.get("will_execute_by_this_command") is True:
        reasons.append(f"selected_route_marked_execute_by_this_command:{route_type}")
    if item.get("will_render_pdf_by_this_command") is True:
        reasons.append(f"selected_route_marked_render_pdf:{route_type}")
    if item.get("will_render_docx_by_this_command") is True:
        reasons.append(f"selected_route_marked_render_docx:{route_type}")
    if item.get("will_generate_manifest_by_this_command") is True:
        reasons.append(f"selected_route_marked_generate_manifest:{route_type}")
    if item.get("will_perform_manual_acceptance_by_this_command") is True:
        reasons.append(f"selected_route_marked_manual_acceptance:{route_type}")
    if item.get("will_write_product_state_by_this_command") is True:
        reasons.append(f"selected_route_marked_product_state_write:{route_type}")
    return dedupe(reasons)


def build_execute_blocking_reasons(
    mode: str,
    confirm_execute: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["selected_route_execute_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_execute:
        reasons.append("confirm_execute_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("execute_note_required")
    return reasons


def build_status(
    mode: str,
    preflight_reasons: list[str],
    contract_reasons: list[str],
    execute_reasons: list[str],
) -> str:
    if preflight_reasons:
        return "blocked_by_selected_route_execution_preflight"
    if contract_reasons:
        return "blocked_by_selected_route_execute_contract"
    if "selected_route_execute_mode_invalid" in execute_reasons:
        return "blocked_by_selected_route_execute_mode"
    if mode == "dry-run":
        return "selected_route_execute_dry_run_ready"
    if "confirm_execute_required" in execute_reasons:
        return "blocked_by_missing_selected_route_execute_confirmation"
    if execute_reasons:
        return "blocked_by_selected_route_execute_metadata"
    return "selected_route_execute_manifest_recorded"


def build_source_preflight(selected_route_execution_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": selected_route_execution_preflight.get("schema_version", ""),
        "status": selected_route_execution_preflight.get("status", ""),
        "can_request_selected_route_execution": selected_route_execution_preflight.get(
            "can_request_selected_route_execution"
        )
        is True,
        "requires_explicit_route_execute_command": selected_route_execution_preflight.get(
            "requires_explicit_route_execute_command"
        )
        is True,
        "selected_route_executed": selected_route_execution_preflight.get("selected_route_executed") is True,
        "export_or_acceptance_executed": selected_route_execution_preflight.get("export_or_acceptance_executed")
        is True,
        "rendered_pdf": selected_route_execution_preflight.get("rendered_pdf") is True,
        "rendered_docx": selected_route_execution_preflight.get("rendered_docx") is True,
        "package_manifest_generated": selected_route_execution_preflight.get("package_manifest_generated") is True,
        "manual_acceptance_performed": selected_route_execution_preflight.get("manual_acceptance_performed") is True,
        "formal_writeback_executed": selected_route_execution_preflight.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": selected_route_execution_preflight.get("this_command_wrote_formal_state")
        is True,
        "can_write_product_state": selected_route_execution_preflight.get("can_write_product_state") is True,
        "selected_route_execution_plan_count": len(
            selected_route_execution_preflight.get("selected_route_execution_plan", [])
        ),
        "blocking_reasons": selected_route_execution_preflight.get("blocking_reasons", []),
    }


def build_execute_request(mode: str, confirm_execute: bool, reviewer: str, note: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_execute": confirm_execute,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_selected_route_execute_operations(
    selected_route_execution_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = []
    for item in selected_route_execution_preflight.get("selected_route_execution_plan", []):
        route_type = item.get("route_type", "")
        operations.append(
            {
                "operation_id": f"selected_route_execute::{route_type}",
                "route_execution_id": item.get("route_execution_id", ""),
                "routed_action": item.get("routed_action", ""),
                "route_type": route_type,
                "next_command": item.get("next_command", ""),
                "planned_outputs": item.get("planned_outputs", []),
                "operation_status": "planned_not_executed",
                "will_execute_selected_route": False,
                "will_render_pdf": False,
                "will_render_docx": False,
                "will_generate_package_manifest": False,
                "will_perform_manual_acceptance": False,
                "will_write_product_state": False,
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


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "selected_route_execute_dry_run_ready":
        return {
            "id": "review_selected_route_execute_dry_run_then_confirm_manifest",
            "label": "Review selected route execute dry-run",
            "description": "Dry-run is ready; a confirmed execute can record the selected route execute manifest.",
        }
    if status == "selected_route_execute_manifest_recorded":
        return {
            "id": "implement_route_specific_artifact_executor",
            "label": "Implement route-specific artifact executor",
            "description": "Execute manifest is recorded; a later node must render, export, manifest, or accept the route.",
        }
    if status == "blocked_by_missing_selected_route_execute_confirmation":
        return {
            "id": "rerun_with_confirm_execute",
            "label": "Rerun with explicit confirm execute",
            "description": "Execute mode requires --confirm-execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_selected_route_execute_metadata":
        return {
            "id": "record_execute_reviewer_and_note",
            "label": "Record execute reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_selected_route_execute_mode":
        return {
            "id": "choose_valid_selected_route_execute_mode",
            "label": "Choose valid selected route execute mode",
            "description": "Mode must be dry-run or execute.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_selected_route_execute_contract":
        return {
            "id": "repair_selected_route_execute_contract",
            "label": "Repair selected route execute contract",
            "description": "P7-Z must expose exactly one clean selected route before the execute gate can continue.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_selected_route_execution_preflight_blockers",
        "label": "Resolve selected route execution preflight blockers",
        "description": "Selected route execute cannot proceed until P7-Z is ready.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_selected_route_execute_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTE_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
    execute_manifest_path: Path = DEFAULT_EXECUTE_MANIFEST_PATH,
) -> tuple[Path, Path, Path | None]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    absolute_manifest = None
    if report["selected_route_execute_manifest_recorded"]:
        absolute_manifest = project_root / execute_manifest_path
        absolute_manifest.parent.mkdir(parents=True, exist_ok=True)
        absolute_manifest.write_text(
            json.dumps(build_execute_manifest(report, execute_manifest_path), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return absolute_report, absolute_review, absolute_manifest


def build_execute_manifest(report: dict[str, Any], execute_manifest_path: Path) -> dict[str, Any]:
    return {
        "schema_version": EXECUTE_MANIFEST_SCHEMA_VERSION,
        "generated_at": report["generated_at"],
        "topic": report.get("topic", ""),
        "source_execute_report": str(DEFAULT_EXECUTE_PATH),
        "manifest_path": str(execute_manifest_path),
        "reviewer": report["execute_request"]["reviewer"],
        "note": report["execute_request"]["note"],
        "selected_route_executed": False,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "package_manifest_generated": False,
        "manual_acceptance_performed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "selected_route_execute_operations": report["selected_route_execute_operations"],
        "boundary_flags": build_boundary_flags(),
    }


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Formal Package Selected Route Execute",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- 可确认 execute：{str(report['can_execute_selected_route_with_confirmation']).lower()}",
        f"- execute manifest 已记录：{str(report['selected_route_execute_manifest_recorded']).lower()}",
        f"- selected route operation 数：{len(report['selected_route_execute_operations'])}",
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
    lines.extend(["", "## Selected Route Execute Operations"])
    if report["selected_route_execute_operations"]:
        for operation in report["selected_route_execute_operations"]:
            lines.append(f"- `{operation['operation_id']}`: {operation['operation_status']}")
    else:
        lines.append("- 无；等待 selected route execution preflight ready。")
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

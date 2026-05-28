from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_execution.v1"
EXECUTION_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_execution_manifest.v1"
DEFAULT_READINESS_PATH = Path("Results/json/auto_mode_formal_target_adapter_readiness.json")
DEFAULT_EXECUTION_PATH = Path("Results/json/auto_mode_formal_target_adapter_execution.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_execution.md")
DEFAULT_EXECUTION_ROOT = Path("workspace/formal_target_adapter_execution/auto_mode")
DEFAULT_EXECUTION_MANIFEST_PATH = DEFAULT_EXECUTION_ROOT / "formal_target_adapter_execution_manifest.json"
VALID_MODES = {"dry-run", "execute"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_execution(
    target_adapter_readiness: dict[str, Any],
    mode: str = "dry-run",
    confirm_execution: bool = False,
    reviewer: str = "",
    note: str = "",
    execution_manifest_path: Path = DEFAULT_EXECUTION_MANIFEST_PATH,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    readiness_reasons = build_readiness_blocking_reasons(target_adapter_readiness)
    execution_reasons = build_execution_blocking_reasons(mode, confirm_execution, reviewer, note)
    blocking_reasons = readiness_reasons + execution_reasons
    status = build_status(mode, readiness_reasons, execution_reasons)
    adapter_execution_plan = build_adapter_execution_plan(target_adapter_readiness) if not readiness_reasons else []
    execution_manifest_recorded = status == "target_adapter_execution_manifest_recorded"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": target_adapter_readiness.get("topic", ""),
        "source_paths": {
            "target_adapter_readiness": source_paths.get("target_adapter_readiness", str(DEFAULT_READINESS_PATH)),
        },
        "status": status,
        "mode": mode,
        "confirm_execution": confirm_execution,
        "can_execute_with_confirmation": not readiness_reasons,
        "execution_manifest_recorded": execution_manifest_recorded,
        "execution_manifest_path": str(execution_manifest_path) if execution_manifest_recorded else "",
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_readiness": build_source_readiness(target_adapter_readiness),
        "execution_request": build_execution_request(mode, confirm_execution, reviewer, note),
        "adapter_execution_plan": adapter_execution_plan,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_readiness_blocking_reasons(target_adapter_readiness: dict[str, Any]) -> list[str]:
    reasons = []
    if target_adapter_readiness.get("schema_version") != "p7.auto_mode_formal_target_adapter_readiness.v1":
        reasons.append("target_adapter_readiness_missing_or_invalid_schema")
    if target_adapter_readiness.get("status") != "ready_for_formal_target_adapter_review":
        reasons.append("target_adapter_readiness_not_ready")
    if target_adapter_readiness.get("can_request_target_adapter_execution") is not True:
        reasons.append("target_adapter_readiness_cannot_request_execution")
    if target_adapter_readiness.get("formal_target_adapters_executed") is True:
        reasons.append("target_adapter_readiness_already_executed_adapters")
    if target_adapter_readiness.get("formal_writeback_executed") is True:
        reasons.append("target_adapter_readiness_already_executed_formal_writeback")
    if target_adapter_readiness.get("this_command_wrote_formal_state") is True:
        reasons.append("target_adapter_readiness_already_wrote_formal_state")
    if target_adapter_readiness.get("can_write_product_state") is True:
        reasons.append("target_adapter_readiness_allows_product_state_write")
    if not target_adapter_readiness.get("adapter_mappings"):
        reasons.append("adapter_mappings_missing")
    for mapping in target_adapter_readiness.get("adapter_mappings", []):
        group = mapping.get("writeback_target_group", "unknown")
        if mapping.get("mapping_status") != "ready_for_target_adapter":
            reasons.append(f"adapter_mapping_not_ready:{group}")
        if mapping.get("requires_target_adapter_execution") is not True:
            reasons.append(f"adapter_mapping_missing_execution_requirement:{group}")
        if mapping.get("executed_by_this_command") is True:
            reasons.append(f"adapter_mapping_already_executed:{group}")
        if not mapping.get("adapter_id"):
            reasons.append(f"adapter_mapping_missing_adapter_id:{group}")
        if not mapping.get("candidate_targets"):
            reasons.append(f"adapter_mapping_missing_candidate_targets:{group}")
        if any(target.get("will_be_written_by_this_command") is True for target in mapping.get("candidate_targets", [])):
            reasons.append(f"adapter_mapping_candidate_target_already_marked_write:{group}")
    for flag, value in target_adapter_readiness.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"target_adapter_readiness_boundary_violation:{flag}")
    return reasons


def build_execution_blocking_reasons(
    mode: str,
    confirm_execution: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["execution_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_execution:
        reasons.append("confirm_execution_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("execution_note_required")
    return reasons


def build_status(mode: str, readiness_reasons: list[str], execution_reasons: list[str]) -> str:
    if readiness_reasons:
        return "blocked_by_target_adapter_readiness"
    if "execution_mode_invalid" in execution_reasons:
        return "blocked_by_execution_mode"
    if mode == "dry-run":
        return "target_adapter_execution_dry_run_ready"
    if "confirm_execution_required" in execution_reasons:
        return "blocked_by_missing_execution_confirmation"
    if execution_reasons:
        return "blocked_by_execution_metadata"
    return "target_adapter_execution_manifest_recorded"


def build_source_readiness(target_adapter_readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": target_adapter_readiness.get("schema_version", ""),
        "status": target_adapter_readiness.get("status", ""),
        "can_request_target_adapter_execution": target_adapter_readiness.get(
            "can_request_target_adapter_execution"
        )
        is True,
        "formal_target_adapters_executed": target_adapter_readiness.get("formal_target_adapters_executed") is True,
        "formal_writeback_executed": target_adapter_readiness.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": target_adapter_readiness.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": target_adapter_readiness.get("can_write_product_state") is True,
        "adapter_mappings_count": len(target_adapter_readiness.get("adapter_mappings", [])),
        "blocking_reasons": target_adapter_readiness.get("blocking_reasons", []),
    }


def build_execution_request(mode: str, confirm_execution: bool, reviewer: str, note: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_execution": confirm_execution,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_adapter_execution_plan(target_adapter_readiness: dict[str, Any]) -> list[dict[str, Any]]:
    plan = []
    for index, mapping in enumerate(target_adapter_readiness.get("adapter_mappings", []), start=1):
        plan.append(
            {
                "execution_id": f"target_adapter::{index:02d}::{mapping.get('writeback_target_group', '')}",
                "operation_id": mapping.get("operation_id", ""),
                "category": mapping.get("category", ""),
                "writeback_target_group": mapping.get("writeback_target_group", ""),
                "adapter_id": mapping.get("adapter_id", ""),
                "source_artifacts": mapping.get("source_artifacts", []),
                "candidate_targets": mapping.get("candidate_targets", []),
                "execution_status": "planned_not_executed",
                "requires_materialization_node": True,
                "executed_by_this_command": False,
            }
        )
    return plan


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
        "created_candidate_targets": False,
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "target_adapter_execution_dry_run_ready":
        return {
            "id": "review_adapter_execution_dry_run_then_confirm_manifest",
            "label": "Review adapter execution dry-run",
            "description": "Dry-run is ready; a confirmed execute can record an execution manifest for materialization.",
        }
    if status == "target_adapter_execution_manifest_recorded":
        return {
            "id": "implement_adapter_materialization_node",
            "label": "Implement adapter materialization node",
            "description": "Execution manifest is recorded; a later node must materialize candidate targets.",
        }
    if status == "blocked_by_missing_execution_confirmation":
        return {
            "id": "rerun_with_confirm_execution",
            "label": "Rerun with explicit confirm execution",
            "description": "Execute mode requires --confirm-execution.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_execution_metadata":
        return {
            "id": "record_execution_reviewer_and_note",
            "label": "Record execution reviewer and note",
            "description": "Execute mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_execution_mode":
        return {
            "id": "choose_valid_execution_mode",
            "label": "Choose valid execution mode",
            "description": "Mode must be dry-run or execute.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_target_adapter_readiness_blockers",
        "label": "Resolve target adapter readiness blockers",
        "description": "Target adapter execution cannot proceed until P7-N readiness is ready.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_execution_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTION_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
    execution_manifest_path: Path = DEFAULT_EXECUTION_MANIFEST_PATH,
) -> tuple[Path, Path, Path | None]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    absolute_manifest = None
    if report["execution_manifest_recorded"]:
        absolute_manifest = project_root / execution_manifest_path
        absolute_manifest.parent.mkdir(parents=True, exist_ok=True)
        absolute_manifest.write_text(
            json.dumps(build_execution_manifest(report, execution_manifest_path), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return absolute_report, absolute_review, absolute_manifest


def build_execution_manifest(report: dict[str, Any], execution_manifest_path: Path) -> dict[str, Any]:
    return {
        "schema_version": EXECUTION_MANIFEST_SCHEMA_VERSION,
        "generated_at": report["generated_at"],
        "topic": report.get("topic", ""),
        "source_execution_report": str(DEFAULT_EXECUTION_PATH),
        "manifest_path": str(execution_manifest_path),
        "reviewer": report["execution_request"]["reviewer"],
        "note": report["execution_request"]["note"],
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "candidate_targets_created": False,
        "adapter_execution_plan": report["adapter_execution_plan"],
        "boundary_flags": build_boundary_flags(),
    }


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Formal Target Adapter Execution",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- 可确认 execute：{str(report['can_execute_with_confirmation']).lower()}",
        f"- execution manifest 已记录：{str(report['execution_manifest_recorded']).lower()}",
        f"- 已执行 target adapters：{str(report['formal_target_adapters_executed']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Adapter Execution Plan"])
    if report["adapter_execution_plan"]:
        for item in report["adapter_execution_plan"]:
            lines.append(f"- `{item['execution_id']}`: {item['execution_status']}")
    else:
        lines.append("- 无；等待 target adapter readiness ready。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_materialization_execute.v1"
MATERIALIZATION_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_materialization_manifest.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_materialization_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_target_adapter_materialization_preflight.json")
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_target_adapter_materialization_execute.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_materialization_execute.md")
DEFAULT_MATERIALIZATION_ROOT = Path("workspace/formal_target_adapter_materialization/auto_mode")
DEFAULT_MATERIALIZATION_MANIFEST_PATH = DEFAULT_MATERIALIZATION_ROOT / "formal_target_adapter_materialization_manifest.json"
VALID_MODES = {"dry-run", "materialize"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_materialization_execute(
    project_root: Path,
    materialization_preflight: dict[str, Any],
    mode: str = "dry-run",
    confirm_materialize: bool = False,
    reviewer: str = "",
    note: str = "",
    materialization_manifest_path: Path = DEFAULT_MATERIALIZATION_MANIFEST_PATH,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(materialization_preflight)
    contract_reasons = (
        build_materialization_contract_blocking_reasons(project_root, materialization_preflight)
        if not preflight_reasons
        else []
    )
    materialize_reasons = build_materialize_blocking_reasons(mode, confirm_materialize, reviewer, note)
    blocking_reasons = preflight_reasons + contract_reasons + materialize_reasons
    status = build_status(mode, preflight_reasons, contract_reasons, materialize_reasons)
    operations = (
        build_materialization_operations(project_root, materialization_preflight)
        if not preflight_reasons and not contract_reasons
        else []
    )
    candidate_targets_materialized = status == "adapter_materialization_completed"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": materialization_preflight.get("topic", ""),
        "source_paths": {
            "materialization_preflight": source_paths.get("materialization_preflight", str(DEFAULT_PREFLIGHT_PATH)),
        },
        "status": status,
        "mode": mode,
        "confirm_materialize": confirm_materialize,
        "can_materialize_with_confirmation": not preflight_reasons and not contract_reasons,
        "materialization_manifest_recorded": candidate_targets_materialized,
        "materialization_manifest_path": str(materialization_manifest_path) if candidate_targets_materialized else "",
        "candidate_targets_materialized": candidate_targets_materialized,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_preflight": build_source_preflight(materialization_preflight),
        "materialization_request": build_materialization_request(mode, confirm_materialize, reviewer, note),
        "materialization_operations": operations,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_preflight_blocking_reasons(materialization_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if materialization_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("materialization_preflight_missing_or_invalid_schema")
    if materialization_preflight.get("status") != "ready_for_adapter_materialization_review":
        reasons.append("materialization_preflight_not_ready")
    if materialization_preflight.get("can_request_adapter_materialization") is not True:
        reasons.append("materialization_preflight_cannot_request_materialization")
    if materialization_preflight.get("requires_explicit_materialize_command") is not True:
        reasons.append("materialization_preflight_missing_explicit_command_requirement")
    if materialization_preflight.get("candidate_targets_materialized") is True:
        reasons.append("materialization_preflight_already_materialized_targets")
    if materialization_preflight.get("formal_target_adapters_executed") is True:
        reasons.append("materialization_preflight_already_executed_adapters")
    if materialization_preflight.get("formal_writeback_executed") is True:
        reasons.append("materialization_preflight_already_executed_formal_writeback")
    if materialization_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("materialization_preflight_already_wrote_formal_state")
    if materialization_preflight.get("can_write_product_state") is True:
        reasons.append("materialization_preflight_allows_product_state_write")
    if not materialization_preflight.get("materialization_plan"):
        reasons.append("materialization_plan_missing")
    for flag, value in materialization_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"materialization_preflight_boundary_violation:{flag}")
    return reasons


def build_materialization_contract_blocking_reasons(
    project_root: Path,
    materialization_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    for item in materialization_preflight.get("materialization_plan", []):
        group = item.get("writeback_target_group", "unknown")
        source_artifacts = item.get("source_artifacts", [])
        candidate_targets = item.get("candidate_targets", [])
        if item.get("materialization_status") != "planned_not_materialized":
            reasons.append(f"materialization_status_not_planned:{group}")
        if item.get("requires_explicit_materialize_command") is not True:
            reasons.append(f"materialization_explicit_command_requirement_missing:{group}")
        if item.get("will_materialize_by_this_command") is True:
            reasons.append(f"materialization_already_marked_write:{group}")
        if not item.get("materialization_id"):
            reasons.append(f"materialization_id_missing:{group}")
        if not item.get("adapter_id"):
            reasons.append(f"adapter_id_missing:{group}")
        if not source_artifacts:
            reasons.append(f"materialization_source_artifacts_missing:{group}")
        if not candidate_targets:
            reasons.append(f"materialization_candidate_targets_missing:{group}")
        if source_artifacts and candidate_targets and len(source_artifacts) != len(candidate_targets):
            reasons.append(f"materialization_source_target_count_mismatch:{group}")
        for source in source_artifacts:
            path = source.get("path", "")
            if not path:
                reasons.append(f"materialization_source_path_missing:{group}")
                continue
            if not (project_root / path).exists():
                reasons.append(f"materialization_source_missing:{group}")
        for target in candidate_targets:
            path = target.get("path", "")
            if not path:
                reasons.append(f"materialization_target_path_missing:{group}")
                continue
            if (project_root / path).exists() or target.get("exists") is True:
                reasons.append(f"materialization_target_already_exists:{group}")
            if target.get("will_be_written_by_this_command") is True:
                reasons.append(f"materialization_target_already_marked_write:{group}")
    return dedupe(reasons)


def build_materialize_blocking_reasons(
    mode: str,
    confirm_materialize: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["materialize_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_materialize:
        reasons.append("confirm_materialize_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("materialization_note_required")
    return reasons


def build_status(
    mode: str,
    preflight_reasons: list[str],
    contract_reasons: list[str],
    materialize_reasons: list[str],
) -> str:
    if preflight_reasons:
        return "blocked_by_materialization_preflight"
    if contract_reasons:
        return "blocked_by_materialization_contract"
    if "materialize_mode_invalid" in materialize_reasons:
        return "blocked_by_materialize_mode"
    if mode == "dry-run":
        return "adapter_materialization_dry_run_ready"
    if "confirm_materialize_required" in materialize_reasons:
        return "blocked_by_missing_materialization_confirmation"
    if materialize_reasons:
        return "blocked_by_materialization_metadata"
    return "adapter_materialization_completed"


def build_source_preflight(materialization_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": materialization_preflight.get("schema_version", ""),
        "status": materialization_preflight.get("status", ""),
        "can_request_adapter_materialization": materialization_preflight.get("can_request_adapter_materialization")
        is True,
        "requires_explicit_materialize_command": materialization_preflight.get("requires_explicit_materialize_command")
        is True,
        "candidate_targets_materialized": materialization_preflight.get("candidate_targets_materialized") is True,
        "formal_target_adapters_executed": materialization_preflight.get("formal_target_adapters_executed") is True,
        "formal_writeback_executed": materialization_preflight.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": materialization_preflight.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": materialization_preflight.get("can_write_product_state") is True,
        "materialization_plan_count": len(materialization_preflight.get("materialization_plan", [])),
        "blocking_reasons": materialization_preflight.get("blocking_reasons", []),
    }


def build_materialization_request(mode: str, confirm_materialize: bool, reviewer: str, note: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_materialize": confirm_materialize,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_materialization_operations(
    project_root: Path,
    materialization_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = []
    for index, item in enumerate(materialization_preflight.get("materialization_plan", []), start=1):
        group = item.get("writeback_target_group", "")
        pairs = []
        for source, target in zip(item.get("source_artifacts", []), item.get("candidate_targets", []), strict=True):
            source_path = source.get("path", "")
            target_path = target.get("path", "")
            pairs.append(
                {
                    "source_path": source_path,
                    "source_exists": bool(source_path and (project_root / source_path).exists()),
                    "target_path": target_path,
                    "target_exists": bool(target_path and (project_root / target_path).exists()),
                    "will_write_candidate_target": False,
                }
            )
        operations.append(
            {
                "operation_id": f"adapter_materialization::{index:02d}::{group}",
                "materialization_id": item.get("materialization_id", ""),
                "execution_id": item.get("execution_id", ""),
                "writeback_target_group": group,
                "adapter_id": item.get("adapter_id", ""),
                "operation_status": "planned_not_materialized",
                "artifact_pairs": pairs,
                "writes_formal_state": False,
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
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "adapter_materialization_dry_run_ready":
        return {
            "id": "review_materialization_dry_run_then_confirm",
            "label": "Review materialization dry-run",
            "description": "Dry-run is ready; rerun with explicit materialize confirmation to create candidate targets.",
        }
    if status == "adapter_materialization_completed":
        return {
            "id": "verify_materialized_candidate_targets",
            "label": "Verify materialized candidate targets",
            "description": "Candidate targets were materialized; a later node must verify them before any formal promotion.",
        }
    if status == "blocked_by_materialization_contract":
        return {
            "id": "repair_materialization_inputs",
            "label": "Repair materialization inputs",
            "description": "Source artifacts must exist and candidate targets must be absent before materialization.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_missing_materialization_confirmation":
        return {
            "id": "rerun_with_confirm_materialize",
            "label": "Rerun with explicit materialize confirmation",
            "description": "Materialize mode requires --confirm-materialize.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_materialization_metadata":
        return {
            "id": "record_materialization_reviewer_and_note",
            "label": "Record materialization reviewer and note",
            "description": "Materialize mode requires reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_materialize_mode":
        return {
            "id": "choose_valid_materialize_mode",
            "label": "Choose valid materialize mode",
            "description": "Mode must be dry-run or materialize.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_materialization_preflight_blockers",
        "label": "Resolve materialization preflight blockers",
        "description": "Adapter materialization cannot proceed until P7-P is ready.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_materialization_execute_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTE_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
    materialization_manifest_path: Path = DEFAULT_MATERIALIZATION_MANIFEST_PATH,
) -> tuple[Path, Path, Path | None]:
    absolute_manifest = None
    materialized_targets: list[dict[str, Any]] = []
    if report["candidate_targets_materialized"]:
        materialized_targets = materialize_candidate_targets(project_root, report["materialization_operations"])
        absolute_manifest = project_root / materialization_manifest_path
        absolute_manifest.parent.mkdir(parents=True, exist_ok=True)
        absolute_manifest.write_text(
            json.dumps(build_materialization_manifest(report, materialization_manifest_path, materialized_targets), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review, absolute_manifest


def materialize_candidate_targets(
    project_root: Path,
    operations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    materialized = []
    for operation in operations:
        for pair in operation.get("artifact_pairs", []):
            source = project_root / pair["source_path"]
            target = project_root / pair["target_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            materialized.append(
                {
                    "operation_id": operation["operation_id"],
                    "writeback_target_group": operation["writeback_target_group"],
                    "source_path": pair["source_path"],
                    "target_path": pair["target_path"],
                    "bytes": target.stat().st_size,
                }
            )
    return materialized


def build_materialization_manifest(
    report: dict[str, Any],
    materialization_manifest_path: Path,
    materialized_targets: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": MATERIALIZATION_MANIFEST_SCHEMA_VERSION,
        "generated_at": report["generated_at"],
        "topic": report.get("topic", ""),
        "source_execute_report": str(DEFAULT_EXECUTE_PATH),
        "manifest_path": str(materialization_manifest_path),
        "reviewer": report["materialization_request"]["reviewer"],
        "note": report["materialization_request"]["note"],
        "candidate_targets_materialized": True,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "materialized_targets": materialized_targets,
        "boundary_flags": build_boundary_flags(),
    }


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Formal Target Adapter Materialization Execute",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- 可确认 materialize：{str(report['can_materialize_with_confirmation']).lower()}",
        f"- materialization manifest 已记录：{str(report['materialization_manifest_recorded']).lower()}",
        f"- 已 materialize candidate targets：{str(report['candidate_targets_materialized']).lower()}",
        f"- 已执行 target adapters：{str(report['formal_target_adapters_executed']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Materialization Operations"])
    if report["materialization_operations"]:
        for item in report["materialization_operations"]:
            lines.append(f"- `{item['operation_id']}`: {item['operation_status']}")
    else:
        lines.append("- 无；等待 materialization preflight ready。")
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

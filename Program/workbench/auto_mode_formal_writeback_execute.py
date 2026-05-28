from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_writeback_execute.v1"
APPLY_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_writeback_apply_manifest.v1"
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_writeback_execution_preflight.json")
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_writeback_execute.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_writeback_execute.md")
DEFAULT_APPLY_ROOT = Path("workspace/formal_writeback_apply/auto_mode")
DEFAULT_APPLY_MANIFEST_PATH = DEFAULT_APPLY_ROOT / "formal_writeback_apply_manifest.json"
VALID_MODES = {"dry-run", "apply"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_writeback_execute(
    execution_preflight: dict[str, Any],
    mode: str = "dry-run",
    confirm_apply: bool = False,
    reviewer: str = "",
    note: str = "",
    apply_manifest_path: Path = DEFAULT_APPLY_MANIFEST_PATH,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(execution_preflight)
    apply_reasons = build_apply_blocking_reasons(mode, confirm_apply, reviewer, note)
    blocking_reasons = preflight_reasons + apply_reasons
    status = build_status(mode, preflight_reasons, apply_reasons)
    planned_operations = build_planned_operations(execution_preflight) if not preflight_reasons else []
    apply_manifest_recorded = status == "formal_writeback_apply_manifest_recorded"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": execution_preflight.get("topic", ""),
        "source_paths": {
            "formal_writeback_execution_preflight": source_paths.get(
                "formal_writeback_execution_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "status": status,
        "mode": mode,
        "confirm_apply": confirm_apply,
        "can_apply_with_confirmation": not preflight_reasons,
        "apply_manifest_recorded": apply_manifest_recorded,
        "apply_manifest_path": str(apply_manifest_path) if apply_manifest_recorded else "",
        "formal_writeback_executed": False,
        "formal_target_adapters_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_preflight": build_source_preflight(execution_preflight),
        "apply_request": build_apply_request(mode, confirm_apply, reviewer, note),
        "planned_operations": planned_operations,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_preflight_blocking_reasons(execution_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if execution_preflight.get("schema_version") != "p7.auto_mode_formal_writeback_execution_preflight.v1":
        reasons.append("execution_preflight_missing_or_invalid_schema")
    if execution_preflight.get("status") != "ready_for_formal_writeback_execution_review":
        reasons.append("execution_preflight_not_ready")
    if execution_preflight.get("can_request_formal_writeback_execution") is not True:
        reasons.append("execution_preflight_cannot_request_execution")
    if execution_preflight.get("requires_explicit_execute_command") is not True:
        reasons.append("execution_preflight_missing_explicit_command_requirement")
    if execution_preflight.get("formal_writeback_executed") is True:
        reasons.append("execution_preflight_already_executed_writeback")
    if execution_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("execution_preflight_already_wrote_formal_state")
    if execution_preflight.get("can_write_product_state") is True:
        reasons.append("execution_preflight_allows_product_state_write")
    if not execution_preflight.get("execution_plan"):
        reasons.append("execution_plan_missing")
    for flag, value in execution_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"execution_preflight_boundary_violation:{flag}")
    return reasons


def build_apply_blocking_reasons(mode: str, confirm_apply: bool, reviewer: str, note: str) -> list[str]:
    if mode not in VALID_MODES:
        return ["execute_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_apply:
        reasons.append("confirm_apply_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("apply_note_required")
    return reasons


def build_status(mode: str, preflight_reasons: list[str], apply_reasons: list[str]) -> str:
    if preflight_reasons:
        return "blocked_by_execution_preflight"
    if "execute_mode_invalid" in apply_reasons:
        return "blocked_by_execute_mode"
    if mode == "dry-run":
        return "formal_writeback_dry_run_ready"
    if "confirm_apply_required" in apply_reasons:
        return "blocked_by_missing_apply_confirmation"
    if apply_reasons:
        return "blocked_by_apply_metadata"
    return "formal_writeback_apply_manifest_recorded"


def build_source_preflight(execution_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": execution_preflight.get("schema_version", ""),
        "status": execution_preflight.get("status", ""),
        "can_request_formal_writeback_execution": execution_preflight.get("can_request_formal_writeback_execution")
        is True,
        "requires_explicit_execute_command": execution_preflight.get("requires_explicit_execute_command") is True,
        "formal_writeback_executed": execution_preflight.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": execution_preflight.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": execution_preflight.get("can_write_product_state") is True,
        "execution_plan_count": len(execution_preflight.get("execution_plan", [])),
        "blocking_reasons": execution_preflight.get("blocking_reasons", []),
    }


def build_apply_request(mode: str, confirm_apply: bool, reviewer: str, note: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_apply": confirm_apply,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_planned_operations(execution_preflight: dict[str, Any]) -> list[dict[str, Any]]:
    operations = []
    for index, item in enumerate(execution_preflight.get("execution_plan", []), start=1):
        category = item.get("category", "")
        operations.append(
            {
                "operation_id": f"formal_writeback::{index:02d}::{category}",
                "category": category,
                "label": item.get("label", ""),
                "writeback_target_group": item.get("writeback_target_group", ""),
                "evidence_refs": item.get("evidence_refs", []),
                "operation_status": "planned_not_executed",
                "requires_target_adapter": True,
                "executed_by_this_command": False,
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
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "formal_writeback_dry_run_ready":
        return {
            "id": "review_dry_run_then_confirm_apply_manifest",
            "label": "Review dry-run and optionally confirm apply manifest",
            "description": "Dry-run is ready; a confirmed apply can record the manifest for later target adapters.",
        }
    if status == "formal_writeback_apply_manifest_recorded":
        return {
            "id": "implement_formal_target_adapters",
            "label": "Implement formal target adapters",
            "description": "Apply manifest is recorded; later adapters must perform audited target writes.",
        }
    if status == "blocked_by_missing_apply_confirmation":
        return {
            "id": "rerun_with_confirm_apply",
            "label": "Rerun with explicit confirm apply",
            "description": "Apply mode requires --confirm-apply.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_apply_metadata":
        return {
            "id": "record_apply_reviewer_and_note",
            "label": "Record apply reviewer and note",
            "description": "Apply mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_execute_mode":
        return {
            "id": "choose_valid_execute_mode",
            "label": "Choose valid execute mode",
            "description": "Mode must be dry-run or apply.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_execution_preflight_blockers",
        "label": "Resolve execution preflight blockers",
        "description": "Formal writeback execute cannot proceed until P7-L is ready.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_writeback_execute_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTE_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
    apply_manifest_path: Path = DEFAULT_APPLY_MANIFEST_PATH,
) -> tuple[Path, Path, Path | None]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    absolute_manifest = None
    if report["apply_manifest_recorded"]:
        absolute_manifest = project_root / apply_manifest_path
        absolute_manifest.parent.mkdir(parents=True, exist_ok=True)
        absolute_manifest.write_text(
            json.dumps(build_apply_manifest(report, apply_manifest_path), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return absolute_report, absolute_review, absolute_manifest


def build_apply_manifest(report: dict[str, Any], apply_manifest_path: Path) -> dict[str, Any]:
    return {
        "schema_version": APPLY_MANIFEST_SCHEMA_VERSION,
        "generated_at": report["generated_at"],
        "topic": report.get("topic", ""),
        "source_execute_report": str(DEFAULT_EXECUTE_PATH),
        "manifest_path": str(apply_manifest_path),
        "reviewer": report["apply_request"]["reviewer"],
        "note": report["apply_request"]["note"],
        "formal_writeback_executed": False,
        "formal_target_adapters_executed": False,
        "operations": report["planned_operations"],
        "boundary_flags": build_boundary_flags(),
    }


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Formal Writeback Execute",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- 可确认 apply：{str(report['can_apply_with_confirmation']).lower()}",
        f"- apply manifest 已记录：{str(report['apply_manifest_recorded']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Planned Operations"])
    if report["planned_operations"]:
        for operation in report["planned_operations"]:
            lines.append(f"- `{operation['operation_id']}`: {operation['operation_status']}")
    else:
        lines.append("- 无；等待执行预检 ready。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"

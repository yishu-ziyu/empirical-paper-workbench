from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_execute.v1"
PROMOTION_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_manifest.v1"
PREFLIGHT_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.v1"
DEFAULT_PREFLIGHT_PATH = Path(
    "Results/json/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json"
)
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_target_adapter_candidate_promotion_execute.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_candidate_promotion_execute.md")
DEFAULT_PROMOTION_ROOT = Path("workspace/formal_target_adapter_candidate_promotion/auto_mode")
DEFAULT_PROMOTION_MANIFEST_PATH = DEFAULT_PROMOTION_ROOT / "formal_target_adapter_candidate_promotion_manifest.json"
VALID_MODES = {"dry-run", "promote"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_candidate_promotion_execute(
    project_root: Path,
    promotion_execution_preflight: dict[str, Any],
    mode: str = "dry-run",
    confirm_promote: bool = False,
    reviewer: str = "",
    note: str = "",
    promotion_manifest_path: Path = DEFAULT_PROMOTION_MANIFEST_PATH,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    preflight_reasons = build_preflight_blocking_reasons(promotion_execution_preflight)
    contract_reasons = (
        build_promotion_contract_blocking_reasons(project_root, promotion_execution_preflight)
        if not preflight_reasons
        else []
    )
    promote_reasons = build_promote_blocking_reasons(mode, confirm_promote, reviewer, note)
    blocking_reasons = preflight_reasons + contract_reasons + promote_reasons
    status = build_status(mode, preflight_reasons, contract_reasons, promote_reasons)
    operations = (
        build_promotion_operations(project_root, promotion_execution_preflight)
        if not preflight_reasons and not contract_reasons
        else []
    )
    completed = status == "verified_candidate_promotion_completed"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": promotion_execution_preflight.get("topic", ""),
        "source_paths": {
            "promotion_execution_preflight": source_paths.get(
                "promotion_execution_preflight",
                str(DEFAULT_PREFLIGHT_PATH),
            ),
        },
        "status": status,
        "mode": mode,
        "confirm_promote": confirm_promote,
        "can_promote_with_confirmation": not preflight_reasons and not contract_reasons,
        "promotion_manifest_recorded": completed,
        "promotion_manifest_path": str(promotion_manifest_path) if completed else "",
        "candidate_targets_promoted": completed,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": completed,
        "this_command_wrote_formal_state": completed,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_preflight": build_source_preflight(promotion_execution_preflight),
        "promotion_request": build_promotion_request(mode, confirm_promote, reviewer, note),
        "promotion_operations": operations,
        "boundary_flags": build_boundary_flags(completed),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_preflight_blocking_reasons(promotion_execution_preflight: dict[str, Any]) -> list[str]:
    reasons = []
    if promotion_execution_preflight.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        reasons.append("promotion_execution_preflight_missing_or_invalid_schema")
    if promotion_execution_preflight.get("status") != "ready_for_verified_candidate_promotion_execution_review":
        reasons.append("promotion_execution_preflight_not_ready")
    if promotion_execution_preflight.get("can_request_verified_candidate_promotion_execution") is not True:
        reasons.append("promotion_execution_preflight_cannot_request_execution")
    if promotion_execution_preflight.get("requires_explicit_promotion_execute_command") is not True:
        reasons.append("promotion_execution_preflight_missing_explicit_command_requirement")
    if promotion_execution_preflight.get("candidate_targets_promoted") is True:
        reasons.append("promotion_execution_preflight_already_promoted_candidates")
    if promotion_execution_preflight.get("formal_writeback_executed") is True:
        reasons.append("promotion_execution_preflight_already_executed_formal_writeback")
    if promotion_execution_preflight.get("this_command_wrote_formal_state") is True:
        reasons.append("promotion_execution_preflight_already_wrote_formal_state")
    if promotion_execution_preflight.get("can_write_product_state") is True:
        reasons.append("promotion_execution_preflight_allows_product_state_write")
    if not promotion_execution_preflight.get("promotion_execution_plan"):
        reasons.append("promotion_execution_plan_missing")
    for flag, value in promotion_execution_preflight.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"promotion_execution_preflight_boundary_violation:{flag}")
    return reasons


def build_promotion_contract_blocking_reasons(
    project_root: Path,
    promotion_execution_preflight: dict[str, Any],
) -> list[str]:
    reasons = []
    for item in promotion_execution_preflight.get("promotion_execution_plan", []):
        group = item.get("writeback_target_group", "unknown")
        candidate_path = item.get("candidate_path", "")
        formal_target_path = item.get("formal_target_path", "")
        candidate = project_root / candidate_path
        formal_target = project_root / formal_target_path
        if item.get("execution_status") != "pending_explicit_promotion_execute_command":
            reasons.append(f"promotion_execution_status_not_pending:{group}")
        if item.get("requires_explicit_promotion_execute_command") is not True:
            reasons.append(f"promotion_execute_requirement_missing:{group}")
        if item.get("promoted_by_this_command") is True:
            reasons.append(f"promotion_item_already_promoted:{group}")
        if item.get("this_command_wrote_formal_state") is True:
            reasons.append(f"promotion_item_already_wrote_formal_state:{group}")
        if not candidate_path:
            reasons.append(f"candidate_path_missing:{group}")
            continue
        if not candidate_path.startswith("Submissions/auto_mode/"):
            reasons.append(f"candidate_path_outside_auto_mode_submission:{group}")
        if not candidate.exists():
            reasons.append(f"candidate_target_missing:{group}")
        if not formal_target_path:
            reasons.append(f"formal_target_path_missing:{group}")
            continue
        if not formal_target_path.startswith("Submissions/formal_package/"):
            reasons.append(f"formal_target_path_outside_formal_package:{group}")
        if formal_target.exists():
            reasons.append(f"formal_target_already_exists:{group}")
        if candidate.exists() and item.get("candidate_bytes") != candidate.stat().st_size:
            reasons.append(f"candidate_bytes_mismatch:{group}")
        if candidate.exists() and item.get("candidate_sha256") != sha256_file(candidate):
            reasons.append(f"candidate_sha256_mismatch:{group}")
    return dedupe(reasons)


def build_promote_blocking_reasons(
    mode: str,
    confirm_promote: bool,
    reviewer: str,
    note: str,
) -> list[str]:
    if mode not in VALID_MODES:
        return ["promotion_mode_invalid"]
    if mode == "dry-run":
        return []
    reasons = []
    if not confirm_promote:
        reasons.append("confirm_promote_required")
    if not reviewer.strip():
        reasons.append("reviewer_required")
    if not note.strip():
        reasons.append("promotion_note_required")
    return reasons


def build_status(
    mode: str,
    preflight_reasons: list[str],
    contract_reasons: list[str],
    promote_reasons: list[str],
) -> str:
    if preflight_reasons:
        return "blocked_by_candidate_promotion_execution_preflight"
    if contract_reasons:
        return "blocked_by_candidate_promotion_contract"
    if "promotion_mode_invalid" in promote_reasons:
        return "blocked_by_promotion_mode"
    if mode == "dry-run":
        return "candidate_promotion_dry_run_ready"
    if "confirm_promote_required" in promote_reasons:
        return "blocked_by_missing_candidate_promotion_confirmation"
    if promote_reasons:
        return "blocked_by_candidate_promotion_metadata"
    return "verified_candidate_promotion_completed"


def build_source_preflight(promotion_execution_preflight: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": promotion_execution_preflight.get("schema_version", ""),
        "status": promotion_execution_preflight.get("status", ""),
        "can_request_verified_candidate_promotion_execution": promotion_execution_preflight.get(
            "can_request_verified_candidate_promotion_execution"
        )
        is True,
        "requires_explicit_promotion_execute_command": promotion_execution_preflight.get(
            "requires_explicit_promotion_execute_command"
        )
        is True,
        "candidate_targets_promoted": promotion_execution_preflight.get("candidate_targets_promoted") is True,
        "formal_writeback_executed": promotion_execution_preflight.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": promotion_execution_preflight.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": promotion_execution_preflight.get("can_write_product_state") is True,
        "promotion_execution_plan_count": len(promotion_execution_preflight.get("promotion_execution_plan", [])),
        "blocking_reasons": promotion_execution_preflight.get("blocking_reasons", []),
    }


def build_promotion_request(mode: str, confirm_promote: bool, reviewer: str, note: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "confirm_promote": confirm_promote,
        "reviewer": reviewer,
        "note": note,
        "metadata_complete": bool(reviewer.strip()) and bool(note.strip()),
    }


def build_promotion_operations(
    project_root: Path,
    promotion_execution_preflight: dict[str, Any],
) -> list[dict[str, Any]]:
    operations = []
    for item in promotion_execution_preflight.get("promotion_execution_plan", []):
        candidate_path = item.get("candidate_path", "")
        formal_target_path = item.get("formal_target_path", "")
        operations.append(
            {
                "execution_id": item.get("execution_id", ""),
                "promotion_id": item.get("promotion_id", ""),
                "operation_id": item.get("operation_id", ""),
                "writeback_target_group": item.get("writeback_target_group", ""),
                "candidate_path": candidate_path,
                "candidate_exists": bool(candidate_path and (project_root / candidate_path).exists()),
                "candidate_bytes": item.get("candidate_bytes"),
                "candidate_sha256": item.get("candidate_sha256", ""),
                "formal_target_path": formal_target_path,
                "formal_target_exists": bool(formal_target_path and (project_root / formal_target_path).exists()),
                "operation_status": "planned_not_promoted",
                "will_write_formal_target": False,
            }
        )
    return operations


def build_boundary_flags(promoted: bool = False) -> dict[str, bool]:
    return {
        "modified_formal_manuscript": promoted,
        "modified_formal_bibliography": promoted,
        "modified_project_bibliography": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "modified_product_state": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "reran_models": False,
        "modified_statistical_execution_artifacts": False,
        "executed_target_adapters": False,
        "wrote_formal_state": promoted,
        "created_or_repaired_candidate_targets": False,
        "promoted_candidate_targets": promoted,
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "candidate_promotion_dry_run_ready":
        return {
            "id": "review_candidate_promotion_dry_run_then_confirm",
            "label": "Review candidate promotion dry-run",
            "description": "Dry-run is ready; rerun with explicit promote confirmation to write formal targets.",
        }
    if status == "verified_candidate_promotion_completed":
        return {
            "id": "verify_formal_package_after_candidate_promotion",
            "label": "Verify formal package after candidate promotion",
            "description": "Candidate targets were promoted into the formal package; verify package artifacts next.",
        }
    if status == "blocked_by_candidate_promotion_contract":
        return {
            "id": "repair_candidate_promotion_inputs",
            "label": "Repair candidate promotion inputs",
            "description": "Candidate files must exist, match approval checks, and formal targets must be absent.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_missing_candidate_promotion_confirmation":
        return {
            "id": "rerun_with_confirm_promote",
            "label": "Rerun with explicit promote confirmation",
            "description": "Promote mode requires --confirm-promote.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_candidate_promotion_metadata":
        return {
            "id": "record_promotion_reviewer_and_note",
            "label": "Record promotion reviewer and note",
            "description": "Promote mode requires a reviewer and note.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_promotion_mode":
        return {
            "id": "choose_valid_promotion_mode",
            "label": "Choose valid promotion mode",
            "description": "Mode must be dry-run or promote.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "resolve_candidate_promotion_execution_preflight_blockers",
        "label": "Resolve candidate promotion execution preflight blockers",
        "description": "Candidate promotion cannot proceed until P7-U is ready.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_candidate_promotion_execute_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_EXECUTE_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
    promotion_manifest_path: Path = DEFAULT_PROMOTION_MANIFEST_PATH,
) -> tuple[Path, Path, Path | None]:
    promoted_targets: list[dict[str, Any]] = []
    absolute_manifest = None
    if report["candidate_targets_promoted"]:
        promoted_targets = promote_candidate_targets(project_root, report["promotion_operations"])
        absolute_manifest = project_root / promotion_manifest_path
        absolute_manifest.parent.mkdir(parents=True, exist_ok=True)
        absolute_manifest.write_text(
            json.dumps(build_promotion_manifest(report, promotion_manifest_path, promoted_targets), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review, absolute_manifest


def promote_candidate_targets(project_root: Path, operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    promoted = []
    for operation in operations:
        candidate = project_root / operation["candidate_path"]
        formal_target = project_root / operation["formal_target_path"]
        formal_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidate, formal_target)
        promoted.append(
            {
                "execution_id": operation["execution_id"],
                "promotion_id": operation["promotion_id"],
                "writeback_target_group": operation["writeback_target_group"],
                "candidate_path": operation["candidate_path"],
                "formal_target_path": operation["formal_target_path"],
                "bytes": formal_target.stat().st_size,
                "sha256": sha256_file(formal_target),
            }
        )
    return promoted


def build_promotion_manifest(
    report: dict[str, Any],
    promotion_manifest_path: Path,
    promoted_targets: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": PROMOTION_MANIFEST_SCHEMA_VERSION,
        "generated_at": report["generated_at"],
        "topic": report.get("topic", ""),
        "source_execute_report": str(DEFAULT_EXECUTE_PATH),
        "manifest_path": str(promotion_manifest_path),
        "reviewer": report["promotion_request"]["reviewer"],
        "note": report["promotion_request"]["note"],
        "candidate_targets_promoted": True,
        "formal_writeback_executed": True,
        "this_command_wrote_formal_state": True,
        "can_write_product_state": False,
        "promoted_targets": promoted_targets,
        "boundary_flags": build_boundary_flags(True),
    }


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Auto Mode Formal Target Adapter Candidate Promotion Execute",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 模式：`{report['mode']}`",
        f"- 可确认 promote：{str(report['can_promote_with_confirmation']).lower()}",
        f"- promotion manifest 已记录：{str(report['promotion_manifest_recorded']).lower()}",
        f"- 已提升 candidate targets：{str(report['candidate_targets_promoted']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Promotion Operations"])
    if report["promotion_operations"]:
        for item in report["promotion_operations"]:
            lines.append(f"- `{item['execution_id']}`: {item['operation_status']}")
    else:
        lines.append("- 无；等待 promotion execution preflight ready。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

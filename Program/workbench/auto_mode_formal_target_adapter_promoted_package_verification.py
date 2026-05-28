from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_promoted_package_verification.v1"
EXECUTE_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_execute.v1"
PROMOTION_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_manifest.v1"
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_target_adapter_candidate_promotion_execute.json")
DEFAULT_PROMOTION_MANIFEST_PATH = Path(
    "workspace/formal_target_adapter_candidate_promotion/auto_mode/formal_target_adapter_candidate_promotion_manifest.json"
)
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_target_adapter_promoted_package_verification.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_promoted_package_verification.md")
ALLOWED_SOURCE_BOUNDARY_TRUE_FLAGS = {
    "modified_formal_manuscript",
    "modified_formal_bibliography",
    "wrote_formal_state",
    "promoted_candidate_targets",
}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_promoted_package_verification(
    project_root: Path,
    candidate_promotion_execute: dict[str, Any],
    promotion_manifest: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    execute_reasons = build_execute_blocking_reasons(candidate_promotion_execute)
    manifest_reasons = build_manifest_blocking_reasons(promotion_manifest) if not execute_reasons else []
    boundary_reasons = (
        build_boundary_blocking_reasons(candidate_promotion_execute, promotion_manifest)
        if not execute_reasons and not manifest_reasons
        else []
    )
    target_reasons = (
        build_target_verification_blocking_reasons(project_root, candidate_promotion_execute, promotion_manifest)
        if not execute_reasons and not manifest_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = execute_reasons + manifest_reasons + boundary_reasons + target_reasons
    status = build_status(execute_reasons, manifest_reasons, boundary_reasons, target_reasons)
    target_records = (
        build_formal_target_verification_records(project_root, promotion_manifest)
        if not blocking_reasons
        else []
    )
    verified = status == "promoted_formal_package_verified_for_review"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": candidate_promotion_execute.get("topic") or promotion_manifest.get("topic", ""),
        "source_paths": {
            "candidate_promotion_execute": source_paths.get(
                "candidate_promotion_execute",
                str(DEFAULT_EXECUTE_PATH),
            ),
            "promotion_manifest": source_paths.get("promotion_manifest", str(DEFAULT_PROMOTION_MANIFEST_PATH)),
        },
        "status": status,
        "formal_package_verified": verified,
        "promoted_formal_targets_verified": verified,
        "candidate_targets_promoted": candidate_promotion_execute.get("candidate_targets_promoted") is True,
        "source_formal_writeback_executed": candidate_promotion_execute.get("formal_writeback_executed") is True,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_execute": build_source_execute(candidate_promotion_execute),
        "source_promotion_manifest": build_source_promotion_manifest(promotion_manifest),
        "formal_target_verification_records": target_records,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_execute_blocking_reasons(candidate_promotion_execute: dict[str, Any]) -> list[str]:
    reasons = []
    if candidate_promotion_execute.get("schema_version") != EXECUTE_SCHEMA_VERSION:
        reasons.append("candidate_promotion_execute_missing_or_invalid_schema")
    if candidate_promotion_execute.get("status") != "verified_candidate_promotion_completed":
        reasons.append("candidate_promotion_execute_not_completed")
    if candidate_promotion_execute.get("promotion_manifest_recorded") is not True:
        reasons.append("promotion_manifest_not_recorded")
    if candidate_promotion_execute.get("candidate_targets_promoted") is not True:
        reasons.append("candidate_targets_not_promoted")
    if candidate_promotion_execute.get("formal_writeback_executed") is not True:
        reasons.append("candidate_promotion_execute_did_not_write_formal_state")
    if candidate_promotion_execute.get("this_command_wrote_formal_state") is not True:
        reasons.append("candidate_promotion_execute_missing_formal_state_write_flag")
    if candidate_promotion_execute.get("formal_target_adapters_executed") is True:
        reasons.append("candidate_promotion_execute_already_executed_target_adapters")
    if candidate_promotion_execute.get("can_write_product_state") is True:
        reasons.append("candidate_promotion_execute_allows_product_state_write")
    if candidate_promotion_execute.get("promotion_manifest_recorded") is True and not candidate_promotion_execute.get(
        "promotion_manifest_path"
    ):
        reasons.append("promotion_manifest_path_missing")
    return reasons


def build_manifest_blocking_reasons(promotion_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    if promotion_manifest.get("schema_version") != PROMOTION_MANIFEST_SCHEMA_VERSION:
        reasons.append("promotion_manifest_missing_or_invalid_schema")
    if promotion_manifest.get("candidate_targets_promoted") is not True:
        reasons.append("promotion_manifest_candidate_targets_not_promoted")
    if promotion_manifest.get("formal_writeback_executed") is not True:
        reasons.append("promotion_manifest_did_not_write_formal_state")
    if promotion_manifest.get("this_command_wrote_formal_state") is not True:
        reasons.append("promotion_manifest_missing_formal_state_write_flag")
    if promotion_manifest.get("can_write_product_state") is True:
        reasons.append("promotion_manifest_allows_product_state_write")
    if not promotion_manifest.get("promoted_targets"):
        reasons.append("promoted_targets_missing")
    return reasons


def build_boundary_blocking_reasons(
    candidate_promotion_execute: dict[str, Any],
    promotion_manifest: dict[str, Any],
) -> list[str]:
    reasons = []
    for flag, value in candidate_promotion_execute.get("boundary_flags", {}).items():
        if value is True and flag not in ALLOWED_SOURCE_BOUNDARY_TRUE_FLAGS:
            reasons.append(f"candidate_promotion_execute_boundary_violation:{flag}")
    for flag, value in promotion_manifest.get("boundary_flags", {}).items():
        if value is True and flag not in ALLOWED_SOURCE_BOUNDARY_TRUE_FLAGS:
            reasons.append(f"promotion_manifest_boundary_violation:{flag}")
    return reasons


def build_target_verification_blocking_reasons(
    project_root: Path,
    candidate_promotion_execute: dict[str, Any],
    promotion_manifest: dict[str, Any],
) -> list[str]:
    reasons = []
    execute_targets = {
        item.get("formal_target_path", "")
        for item in candidate_promotion_execute.get("promotion_operations", [])
        if item.get("formal_target_path")
    }
    for target in promotion_manifest.get("promoted_targets", []):
        group = target.get("writeback_target_group", "unknown")
        candidate_path = target.get("candidate_path", "")
        formal_target_path = target.get("formal_target_path", "")
        if candidate_path and not candidate_path.startswith("Submissions/auto_mode/"):
            reasons.append(f"candidate_path_outside_auto_mode_submission:{group}")
        if not formal_target_path:
            reasons.append(f"formal_target_path_missing:{group}")
            continue
        if not formal_target_path.startswith("Submissions/formal_package/"):
            reasons.append(f"formal_target_outside_formal_package:{group}")
            continue
        if execute_targets and formal_target_path not in execute_targets:
            reasons.append(f"promoted_formal_target_not_in_execute_operations:{group}")
        absolute_target = project_root / formal_target_path
        if not absolute_target.exists():
            reasons.append(f"promoted_formal_target_missing:{group}")
            continue
        actual_bytes = absolute_target.stat().st_size
        expected_bytes = target.get("bytes")
        if expected_bytes is None:
            reasons.append(f"promoted_formal_target_manifest_bytes_missing:{group}")
        elif actual_bytes != expected_bytes:
            reasons.append(f"promoted_formal_target_bytes_mismatch:{group}")
        expected_sha256 = target.get("sha256", "")
        actual_sha256 = sha256_file(absolute_target)
        if not expected_sha256:
            reasons.append(f"promoted_formal_target_manifest_sha256_missing:{group}")
        elif actual_sha256 != expected_sha256:
            reasons.append(f"promoted_formal_target_sha256_mismatch:{group}")
    return dedupe(reasons)


def build_status(
    execute_reasons: list[str],
    manifest_reasons: list[str],
    boundary_reasons: list[str],
    target_reasons: list[str],
) -> str:
    if execute_reasons:
        return "blocked_by_candidate_promotion_execute"
    if manifest_reasons:
        return "blocked_by_candidate_promotion_manifest"
    if boundary_reasons:
        return "blocked_by_candidate_promotion_boundary"
    if target_reasons:
        return "blocked_by_promoted_formal_package_verification"
    return "promoted_formal_package_verified_for_review"


def build_source_execute(candidate_promotion_execute: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": candidate_promotion_execute.get("schema_version", ""),
        "status": candidate_promotion_execute.get("status", ""),
        "promotion_manifest_recorded": candidate_promotion_execute.get("promotion_manifest_recorded") is True,
        "promotion_manifest_path": candidate_promotion_execute.get("promotion_manifest_path", ""),
        "candidate_targets_promoted": candidate_promotion_execute.get("candidate_targets_promoted") is True,
        "formal_writeback_executed": candidate_promotion_execute.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": candidate_promotion_execute.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": candidate_promotion_execute.get("can_write_product_state") is True,
        "promotion_operations_count": len(candidate_promotion_execute.get("promotion_operations", [])),
        "blocking_reasons": candidate_promotion_execute.get("blocking_reasons", []),
    }


def build_source_promotion_manifest(promotion_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": promotion_manifest.get("schema_version", ""),
        "manifest_path": promotion_manifest.get("manifest_path", ""),
        "source_execute_report": promotion_manifest.get("source_execute_report", ""),
        "reviewer": promotion_manifest.get("reviewer", ""),
        "candidate_targets_promoted": promotion_manifest.get("candidate_targets_promoted") is True,
        "formal_writeback_executed": promotion_manifest.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": promotion_manifest.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": promotion_manifest.get("can_write_product_state") is True,
        "promoted_targets_count": len(promotion_manifest.get("promoted_targets", [])),
    }


def build_formal_target_verification_records(
    project_root: Path,
    promotion_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    records = []
    for target in promotion_manifest.get("promoted_targets", []):
        absolute_target = project_root / target["formal_target_path"]
        records.append(
            {
                "execution_id": target.get("execution_id", ""),
                "promotion_id": target.get("promotion_id", ""),
                "writeback_target_group": target.get("writeback_target_group", ""),
                "candidate_path": target.get("candidate_path", ""),
                "formal_target_path": target["formal_target_path"],
                "exists": True,
                "bytes": absolute_target.stat().st_size,
                "manifest_bytes": target.get("bytes"),
                "sha256": sha256_file(absolute_target),
                "manifest_sha256": target.get("sha256", ""),
                "verification_status": "verified",
            }
        )
    return records


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
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "promoted_formal_package_verified_for_review":
        return {
            "id": "review_verified_formal_package_for_export",
            "label": "Review verified formal package for export",
            "description": "Promoted formal targets are verified; downstream package export or acceptance can proceed.",
        }
    if status == "blocked_by_candidate_promotion_manifest":
        return {
            "id": "repair_or_record_candidate_promotion_manifest",
            "label": "Repair or record candidate promotion manifest",
            "description": "A valid P7-V promotion manifest is required before formal package verification.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_candidate_promotion_boundary":
        return {
            "id": "repair_candidate_promotion_boundary_violation",
            "label": "Repair candidate promotion boundary violation",
            "description": "The promotion source reports unrelated side effects and cannot feed package verification.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_promoted_formal_package_verification":
        return {
            "id": "repair_promoted_formal_package_targets",
            "label": "Repair promoted formal package targets",
            "description": "Promoted formal targets must exist and match manifest byte and SHA256 checks.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "complete_verified_candidate_promotion",
        "label": "Complete verified candidate promotion",
        "description": "P7-V must complete candidate promotion before formal package verification can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_promoted_package_verification_outputs(
    project_root: Path,
    report: dict[str, Any],
    report_path: Path = DEFAULT_VERIFICATION_PATH,
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
        "# Auto Mode Formal Target Adapter Promoted Package Verification",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- formal package 已验证：{str(report['formal_package_verified']).lower()}",
        f"- promoted formal targets 已验证：{str(report['promoted_formal_targets_verified']).lower()}",
        f"- 本节点执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Formal Target Verification Records"])
    if report["formal_target_verification_records"]:
        for item in report["formal_target_verification_records"]:
            lines.append(f"- `{item['formal_target_path']}`: {item['verification_status']}")
    else:
        lines.append("- 无；等待 candidate promotion execute completed。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped

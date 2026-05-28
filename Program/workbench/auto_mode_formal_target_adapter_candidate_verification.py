from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_verification.v1"
EXECUTE_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_materialization_execute.v1"
MATERIALIZATION_MANIFEST_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_materialization_manifest.v1"
DEFAULT_EXECUTE_PATH = Path("Results/json/auto_mode_formal_target_adapter_materialization_execute.json")
DEFAULT_MATERIALIZATION_MANIFEST_PATH = Path(
    "workspace/formal_target_adapter_materialization/auto_mode/formal_target_adapter_materialization_manifest.json"
)
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_target_adapter_candidate_verification.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_candidate_verification.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_candidate_verification(
    project_root: Path,
    materialization_execute: dict[str, Any],
    materialization_manifest: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    execute_reasons = build_execute_blocking_reasons(materialization_execute)
    manifest_reasons = build_manifest_blocking_reasons(materialization_manifest) if not execute_reasons else []
    boundary_reasons = (
        build_boundary_blocking_reasons(materialization_execute, materialization_manifest)
        if not execute_reasons and not manifest_reasons
        else []
    )
    target_reasons = (
        build_target_verification_blocking_reasons(project_root, materialization_manifest)
        if not execute_reasons and not manifest_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = execute_reasons + manifest_reasons + boundary_reasons + target_reasons
    status = build_status(execute_reasons, manifest_reasons, boundary_reasons, target_reasons)
    target_records = build_target_verification_records(project_root, materialization_manifest) if not blocking_reasons else []
    verified = status == "candidate_targets_verified_for_review"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": materialization_execute.get("topic") or materialization_manifest.get("topic", ""),
        "source_paths": {
            "materialization_execute": source_paths.get("materialization_execute", str(DEFAULT_EXECUTE_PATH)),
            "materialization_manifest": source_paths.get(
                "materialization_manifest",
                str(DEFAULT_MATERIALIZATION_MANIFEST_PATH),
            ),
        },
        "status": status,
        "candidate_targets_verified": verified,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_execute": build_source_execute(materialization_execute),
        "source_materialization_manifest": build_source_materialization_manifest(materialization_manifest),
        "target_verification_records": target_records,
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_execute_blocking_reasons(materialization_execute: dict[str, Any]) -> list[str]:
    reasons = []
    if materialization_execute.get("schema_version") != EXECUTE_SCHEMA_VERSION:
        reasons.append("materialization_execute_missing_or_invalid_schema")
    if materialization_execute.get("status") != "adapter_materialization_completed":
        reasons.append("materialization_execute_not_completed")
    if materialization_execute.get("materialization_manifest_recorded") is not True:
        reasons.append("materialization_manifest_not_recorded")
    if materialization_execute.get("candidate_targets_materialized") is not True:
        reasons.append("candidate_targets_not_materialized")
    if materialization_execute.get("formal_target_adapters_executed") is True:
        reasons.append("materialization_execute_already_executed_adapters")
    if materialization_execute.get("formal_writeback_executed") is True:
        reasons.append("materialization_execute_already_executed_formal_writeback")
    if materialization_execute.get("this_command_wrote_formal_state") is True:
        reasons.append("materialization_execute_already_wrote_formal_state")
    if materialization_execute.get("can_write_product_state") is True:
        reasons.append("materialization_execute_allows_product_state_write")
    if materialization_execute.get("materialization_manifest_recorded") is True and not materialization_execute.get(
        "materialization_manifest_path"
    ):
        reasons.append("materialization_manifest_path_missing")
    return reasons


def build_manifest_blocking_reasons(materialization_manifest: dict[str, Any]) -> list[str]:
    reasons = []
    if materialization_manifest.get("schema_version") != MATERIALIZATION_MANIFEST_SCHEMA_VERSION:
        reasons.append("materialization_manifest_missing_or_invalid_schema")
    if materialization_manifest.get("candidate_targets_materialized") is not True:
        reasons.append("materialization_manifest_candidate_targets_not_materialized")
    if materialization_manifest.get("formal_target_adapters_executed") is True:
        reasons.append("materialization_manifest_already_executed_adapters")
    if materialization_manifest.get("formal_writeback_executed") is True:
        reasons.append("materialization_manifest_already_executed_formal_writeback")
    if materialization_manifest.get("this_command_wrote_formal_state") is True:
        reasons.append("materialization_manifest_already_wrote_formal_state")
    if materialization_manifest.get("can_write_product_state") is True:
        reasons.append("materialization_manifest_allows_product_state_write")
    if not materialization_manifest.get("materialized_targets"):
        reasons.append("materialized_targets_missing")
    return reasons


def build_boundary_blocking_reasons(
    materialization_execute: dict[str, Any],
    materialization_manifest: dict[str, Any],
) -> list[str]:
    reasons = []
    for flag, value in materialization_execute.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"materialization_execute_boundary_violation:{flag}")
    for flag, value in materialization_manifest.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"materialization_manifest_boundary_violation:{flag}")
    return reasons


def build_target_verification_blocking_reasons(
    project_root: Path,
    materialization_manifest: dict[str, Any],
) -> list[str]:
    reasons = []
    for target in materialization_manifest.get("materialized_targets", []):
        group = target.get("writeback_target_group", "unknown")
        target_path = target.get("target_path", "")
        if not target_path:
            reasons.append(f"candidate_target_path_missing:{group}")
            continue
        if not target_path.startswith("Submissions/auto_mode/"):
            reasons.append(f"candidate_target_outside_auto_mode_submission:{group}")
        absolute_target = project_root / target_path
        if not absolute_target.exists():
            reasons.append(f"candidate_target_missing:{group}")
            continue
        expected_bytes = target.get("bytes")
        actual_bytes = absolute_target.stat().st_size
        if expected_bytes is None:
            reasons.append(f"candidate_target_manifest_bytes_missing:{group}")
        elif actual_bytes != expected_bytes:
            reasons.append(f"candidate_target_bytes_mismatch:{group}")
    return dedupe(reasons)


def build_status(
    execute_reasons: list[str],
    manifest_reasons: list[str],
    boundary_reasons: list[str],
    target_reasons: list[str],
) -> str:
    if execute_reasons:
        return "blocked_by_materialization_execute"
    if manifest_reasons:
        return "blocked_by_materialization_manifest"
    if boundary_reasons:
        return "blocked_by_materialization_boundary"
    if target_reasons:
        return "blocked_by_candidate_target_verification"
    return "candidate_targets_verified_for_review"


def build_source_execute(materialization_execute: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": materialization_execute.get("schema_version", ""),
        "status": materialization_execute.get("status", ""),
        "materialization_manifest_recorded": materialization_execute.get("materialization_manifest_recorded") is True,
        "materialization_manifest_path": materialization_execute.get("materialization_manifest_path", ""),
        "candidate_targets_materialized": materialization_execute.get("candidate_targets_materialized") is True,
        "formal_target_adapters_executed": materialization_execute.get("formal_target_adapters_executed") is True,
        "formal_writeback_executed": materialization_execute.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": materialization_execute.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": materialization_execute.get("can_write_product_state") is True,
        "blocking_reasons": materialization_execute.get("blocking_reasons", []),
    }


def build_source_materialization_manifest(materialization_manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": materialization_manifest.get("schema_version", ""),
        "manifest_path": materialization_manifest.get("manifest_path", ""),
        "source_execute_report": materialization_manifest.get("source_execute_report", ""),
        "reviewer": materialization_manifest.get("reviewer", ""),
        "candidate_targets_materialized": materialization_manifest.get("candidate_targets_materialized") is True,
        "formal_target_adapters_executed": materialization_manifest.get("formal_target_adapters_executed") is True,
        "formal_writeback_executed": materialization_manifest.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": materialization_manifest.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": materialization_manifest.get("can_write_product_state") is True,
        "materialized_targets_count": len(materialization_manifest.get("materialized_targets", [])),
    }


def build_target_verification_records(
    project_root: Path,
    materialization_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    records = []
    for target in materialization_manifest.get("materialized_targets", []):
        absolute_target = project_root / target["target_path"]
        content = absolute_target.read_bytes()
        records.append(
            {
                "operation_id": target.get("operation_id", ""),
                "writeback_target_group": target.get("writeback_target_group", ""),
                "source_path": target.get("source_path", ""),
                "target_path": target["target_path"],
                "exists": True,
                "bytes": len(content),
                "manifest_bytes": target.get("bytes"),
                "sha256": hashlib.sha256(content).hexdigest(),
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
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "candidate_targets_verified_for_review":
        return {
            "id": "review_verified_candidate_targets_before_promotion",
            "label": "Review verified candidate targets",
            "description": "Candidate targets are verified; a later node must decide whether they can feed formal promotion.",
        }
    if status == "blocked_by_materialization_manifest":
        return {
            "id": "repair_or_record_materialization_manifest",
            "label": "Repair or record materialization manifest",
            "description": "A valid P7-Q materialization manifest is required before target verification.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_materialization_boundary":
        return {
            "id": "repair_materialization_boundary_violation",
            "label": "Repair materialization boundary violation",
            "description": "Materialization reports a boundary violation and cannot feed target verification.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_candidate_target_verification":
        return {
            "id": "repair_materialized_candidate_targets",
            "label": "Repair materialized candidate targets",
            "description": "Materialized targets must exist and match manifest byte counts.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "complete_adapter_materialization",
        "label": "Complete adapter materialization",
        "description": "P7-Q must complete materialization before candidate target verification can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_candidate_verification_outputs(
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
        "# Auto Mode Formal Target Adapter Candidate Verification",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- candidate targets 已验证：{str(report['candidate_targets_verified']).lower()}",
        f"- 已执行 target adapters：{str(report['formal_target_adapters_executed']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Target Verification Records"])
    if report["target_verification_records"]:
        for item in report["target_verification_records"]:
            lines.append(f"- `{item['target_path']}`: {item['verification_status']}")
    else:
        lines.append("- 无；等待 materialization execute completed。")
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

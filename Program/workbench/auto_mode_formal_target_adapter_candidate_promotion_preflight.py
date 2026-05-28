from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_promotion_preflight.v1"
VERIFICATION_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_candidate_verification.v1"
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_target_adapter_candidate_verification.json")
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_target_adapter_candidate_promotion_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_target_adapter_candidate_promotion_preflight.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_target_adapter_candidate_promotion_preflight(
    candidate_verification: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    verification_reasons = build_verification_blocking_reasons(candidate_verification)
    boundary_reasons = build_boundary_blocking_reasons(candidate_verification) if not verification_reasons else []
    record_reasons = (
        build_record_blocking_reasons(candidate_verification)
        if not verification_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = verification_reasons + boundary_reasons + record_reasons
    status = build_status(verification_reasons, boundary_reasons, record_reasons)
    ready = status == "ready_for_verified_candidate_promotion_review"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": candidate_verification.get("topic", ""),
        "source_paths": {
            "candidate_verification": source_paths.get("candidate_verification", str(DEFAULT_VERIFICATION_PATH)),
        },
        "status": status,
        "can_request_verified_candidate_promotion_approval": ready,
        "requires_separate_promotion_approval": ready,
        "requires_explicit_promotion_execute_command": ready,
        "candidate_targets_promoted": False,
        "formal_target_adapters_executed": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_candidate_verification": build_source_candidate_verification(candidate_verification),
        "promotion_plan": build_promotion_plan(candidate_verification) if ready else [],
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_verification_blocking_reasons(candidate_verification: dict[str, Any]) -> list[str]:
    reasons = []
    if candidate_verification.get("schema_version") != VERIFICATION_SCHEMA_VERSION:
        reasons.append("candidate_verification_missing_or_invalid_schema")
    if candidate_verification.get("status") != "candidate_targets_verified_for_review":
        reasons.append("candidate_verification_not_ready")
    if candidate_verification.get("candidate_targets_verified") is not True:
        reasons.append("candidate_targets_not_verified")
    if candidate_verification.get("formal_target_adapters_executed") is True:
        reasons.append("candidate_verification_already_executed_target_adapters")
    if candidate_verification.get("formal_writeback_executed") is True:
        reasons.append("candidate_verification_already_executed_formal_writeback")
    if candidate_verification.get("this_command_wrote_formal_state") is True:
        reasons.append("candidate_verification_already_wrote_formal_state")
    if candidate_verification.get("can_write_product_state") is True:
        reasons.append("candidate_verification_allows_product_state_write")
    if candidate_verification.get("blocking_reasons"):
        reasons.append("candidate_verification_has_blocking_reasons")
    if not candidate_verification.get("target_verification_records"):
        reasons.append("target_verification_records_missing")
    return reasons


def build_boundary_blocking_reasons(candidate_verification: dict[str, Any]) -> list[str]:
    reasons = []
    for flag, value in candidate_verification.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"candidate_verification_boundary_violation:{flag}")
    return reasons


def build_record_blocking_reasons(candidate_verification: dict[str, Any]) -> list[str]:
    reasons = []
    seen_targets: set[str] = set()
    for record in candidate_verification.get("target_verification_records", []):
        group = record.get("writeback_target_group", "unknown")
        target_path = record.get("target_path", "")
        if not group:
            reasons.append("candidate_record_group_missing")
        if not target_path:
            reasons.append(f"candidate_target_path_missing:{group}")
            continue
        if target_path in seen_targets:
            reasons.append(f"candidate_target_duplicate:{group}")
        seen_targets.add(target_path)
        if not target_path.startswith("Submissions/auto_mode/"):
            reasons.append(f"candidate_target_outside_auto_mode_submission:{group}")
        if record.get("exists") is not True:
            reasons.append(f"candidate_target_not_confirmed_existing:{group}")
        if record.get("verification_status") != "verified":
            reasons.append(f"candidate_target_not_verified:{group}")
        if not is_sha256(record.get("sha256", "")):
            reasons.append(f"candidate_target_sha256_missing_or_invalid:{group}")
        if record.get("bytes") is None:
            reasons.append(f"candidate_target_bytes_missing:{group}")
        if record.get("manifest_bytes") is not None and record.get("bytes") != record.get("manifest_bytes"):
            reasons.append(f"candidate_target_bytes_mismatch:{group}")
    return dedupe(reasons)


def build_status(
    verification_reasons: list[str],
    boundary_reasons: list[str],
    record_reasons: list[str],
) -> str:
    if verification_reasons:
        return "blocked_by_candidate_verification"
    if boundary_reasons:
        return "blocked_by_candidate_verification_boundary"
    if record_reasons:
        return "blocked_by_verified_candidate_records"
    return "ready_for_verified_candidate_promotion_review"


def build_source_candidate_verification(candidate_verification: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": candidate_verification.get("schema_version", ""),
        "status": candidate_verification.get("status", ""),
        "candidate_targets_verified": candidate_verification.get("candidate_targets_verified") is True,
        "formal_target_adapters_executed": candidate_verification.get("formal_target_adapters_executed") is True,
        "formal_writeback_executed": candidate_verification.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": candidate_verification.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": candidate_verification.get("can_write_product_state") is True,
        "target_verification_records_count": len(candidate_verification.get("target_verification_records", [])),
        "blocking_reasons": candidate_verification.get("blocking_reasons", []),
    }


def build_promotion_plan(candidate_verification: dict[str, Any]) -> list[dict[str, Any]]:
    plan = []
    for index, record in enumerate(candidate_verification.get("target_verification_records", []), start=1):
        group = record.get("writeback_target_group", "")
        candidate_path = record.get("target_path", "")
        plan.append(
            {
                "promotion_id": f"verified_candidate_promotion::{index:02d}::{group}",
                "operation_id": record.get("operation_id", ""),
                "writeback_target_group": group,
                "source_path": record.get("source_path", ""),
                "candidate_path": candidate_path,
                "candidate_bytes": record.get("bytes"),
                "candidate_sha256": record.get("sha256", ""),
                "formal_target_path": build_formal_target_path(candidate_path),
                "promotion_status": "pending_separate_approval",
                "requires_separate_promotion_approval": True,
                "requires_explicit_promotion_execute_command": True,
                "promoted_by_this_command": False,
                "writes_formal_state": False,
            }
        )
    return plan


def build_formal_target_path(candidate_path: str) -> str:
    prefix = "Submissions/auto_mode/"
    if not candidate_path.startswith(prefix):
        return ""
    remainder = candidate_path[len(prefix) :]
    parts = remainder.split("/", 1)
    if len(parts) != 2:
        return ""
    return f"Submissions/formal_package/{parts[1]}"


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
    if status == "ready_for_verified_candidate_promotion_review":
        return {
            "id": "review_verified_candidate_promotion_preflight",
            "label": "Review verified candidate promotion preflight",
            "description": "Verified candidates can request a later explicit promotion approval and execute node.",
        }
    if status == "blocked_by_candidate_verification_boundary":
        return {
            "id": "repair_candidate_verification_boundary",
            "label": "Repair candidate verification boundary violation",
            "description": "P7-R boundary flags must be clean before candidate promotion preflight.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_verified_candidate_records":
        return {
            "id": "repair_verified_candidate_records",
            "label": "Repair verified candidate records",
            "description": "Each candidate target needs a verified record with path, bytes, and SHA256 evidence.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "complete_candidate_target_verification",
        "label": "Complete candidate target verification",
        "description": "P7-R must verify candidate targets before promotion preflight can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_target_adapter_candidate_promotion_preflight_outputs(
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
        "# Auto Mode Formal Target Adapter Candidate Promotion Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 可请求 verified candidate promotion approval：{str(report['can_request_verified_candidate_promotion_approval']).lower()}",
        f"- 需要单独 promotion approval：{str(report['requires_separate_promotion_approval']).lower()}",
        f"- 需要显式 promotion execute 命令：{str(report['requires_explicit_promotion_execute_command']).lower()}",
        f"- 已提升 candidate targets：{str(report['candidate_targets_promoted']).lower()}",
        f"- 已执行正式写回：{str(report['formal_writeback_executed']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Promotion Plan"])
    if report["promotion_plan"]:
        for item in report["promotion_plan"]:
            lines.append(f"- `{item['promotion_id']}`: {item['promotion_status']}")
    else:
        lines.append("- 无；等待 candidate verification ready。")
    lines.extend(["", "## Next Action"])
    lines.append(f"- `{report['next_action']['id']}`: {report['next_action']['description']}")
    return "\n".join(lines) + "\n"


def is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value.lower())


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped

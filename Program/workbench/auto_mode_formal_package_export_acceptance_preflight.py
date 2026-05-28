from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.auto_mode_formal_package_export_acceptance_preflight.v1"
VERIFICATION_SCHEMA_VERSION = "p7.auto_mode_formal_target_adapter_promoted_package_verification.v1"
DEFAULT_VERIFICATION_PATH = Path("Results/json/auto_mode_formal_target_adapter_promoted_package_verification.json")
DEFAULT_PREFLIGHT_PATH = Path("Results/json/auto_mode_formal_package_export_acceptance_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/auto_mode_formal_package_export_acceptance_preflight.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_auto_mode_formal_package_export_acceptance_preflight(
    promoted_package_verification: dict[str, Any],
    *,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    verification_reasons = build_verification_blocking_reasons(promoted_package_verification)
    boundary_reasons = (
        build_boundary_blocking_reasons(promoted_package_verification)
        if not verification_reasons
        else []
    )
    target_reasons = (
        build_formal_target_record_blocking_reasons(promoted_package_verification)
        if not verification_reasons and not boundary_reasons
        else []
    )
    blocking_reasons = verification_reasons + boundary_reasons + target_reasons
    status = build_status(verification_reasons, boundary_reasons, target_reasons)
    ready = status == "ready_for_formal_package_export_acceptance_review"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": promoted_package_verification.get("topic", ""),
        "source_paths": {
            "promoted_package_verification": source_paths.get(
                "promoted_package_verification",
                str(DEFAULT_VERIFICATION_PATH),
            ),
        },
        "status": status,
        "can_enter_formal_package_export_acceptance": ready,
        "requires_explicit_export_or_acceptance_command": ready,
        "export_or_acceptance_executed": False,
        "rendered_pdf": False,
        "rendered_docx": False,
        "formal_writeback_executed": False,
        "this_command_wrote_formal_state": False,
        "can_write_product_state": False,
        "blocking_reasons": blocking_reasons,
        "source_verification": build_source_verification(promoted_package_verification),
        "formal_package_summary": build_formal_package_summary(promoted_package_verification),
        "export_acceptance_plan": build_export_acceptance_plan(promoted_package_verification) if ready else [],
        "boundary_flags": build_boundary_flags(),
        "next_action": build_next_action(status, blocking_reasons),
    }


def build_verification_blocking_reasons(promoted_package_verification: dict[str, Any]) -> list[str]:
    reasons = []
    if promoted_package_verification.get("schema_version") != VERIFICATION_SCHEMA_VERSION:
        reasons.append("promoted_formal_package_verification_missing_or_invalid_schema")
    if promoted_package_verification.get("status") != "promoted_formal_package_verified_for_review":
        reasons.append("promoted_formal_package_verification_not_ready")
    if promoted_package_verification.get("formal_package_verified") is not True:
        reasons.append("formal_package_not_verified")
    if promoted_package_verification.get("promoted_formal_targets_verified") is not True:
        reasons.append("promoted_formal_targets_not_verified")
    if promoted_package_verification.get("candidate_targets_promoted") is not True:
        reasons.append("candidate_targets_not_promoted")
    if promoted_package_verification.get("source_formal_writeback_executed") is not True:
        reasons.append("source_formal_writeback_not_executed")
    if promoted_package_verification.get("formal_writeback_executed") is True:
        reasons.append("promoted_package_verification_executed_formal_writeback")
    if promoted_package_verification.get("this_command_wrote_formal_state") is True:
        reasons.append("promoted_package_verification_wrote_formal_state")
    return reasons


def build_boundary_blocking_reasons(promoted_package_verification: dict[str, Any]) -> list[str]:
    reasons = []
    if promoted_package_verification.get("can_write_product_state") is True:
        reasons.append("promoted_package_verification_allows_product_state_write")
    for flag, value in promoted_package_verification.get("boundary_flags", {}).items():
        if value is True:
            reasons.append(f"promoted_package_verification_boundary_violation:{flag}")
    return reasons


def build_formal_target_record_blocking_reasons(promoted_package_verification: dict[str, Any]) -> list[str]:
    records = promoted_package_verification.get("formal_target_verification_records", [])
    if not records:
        return ["formal_target_verification_records_missing"]
    reasons = []
    for record in records:
        group = record.get("writeback_target_group", "unknown")
        target_path = record.get("formal_target_path", "")
        if record.get("verification_status") != "verified":
            reasons.append(f"formal_target_not_verified:{group}")
        if record.get("exists") is not True:
            reasons.append(f"formal_target_missing:{group}")
        if not target_path:
            reasons.append(f"formal_target_path_missing:{group}")
            continue
        if not target_path.startswith("Submissions/formal_package/"):
            reasons.append(f"formal_target_outside_formal_package:{group}")
        if record.get("bytes") != record.get("manifest_bytes"):
            reasons.append(f"formal_target_bytes_mismatch:{group}")
        if record.get("sha256") != record.get("manifest_sha256"):
            reasons.append(f"formal_target_sha256_mismatch:{group}")
    return dedupe(reasons)


def build_status(
    verification_reasons: list[str],
    boundary_reasons: list[str],
    target_reasons: list[str],
) -> str:
    if verification_reasons:
        return "blocked_by_promoted_package_verification"
    if boundary_reasons:
        return "blocked_by_promoted_package_verification_boundary"
    if target_reasons:
        return "blocked_by_formal_package_target_records"
    return "ready_for_formal_package_export_acceptance_review"


def build_source_verification(promoted_package_verification: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": promoted_package_verification.get("schema_version", ""),
        "status": promoted_package_verification.get("status", ""),
        "formal_package_verified": promoted_package_verification.get("formal_package_verified") is True,
        "promoted_formal_targets_verified": promoted_package_verification.get("promoted_formal_targets_verified") is True,
        "candidate_targets_promoted": promoted_package_verification.get("candidate_targets_promoted") is True,
        "source_formal_writeback_executed": promoted_package_verification.get("source_formal_writeback_executed") is True,
        "formal_writeback_executed": promoted_package_verification.get("formal_writeback_executed") is True,
        "this_command_wrote_formal_state": promoted_package_verification.get("this_command_wrote_formal_state") is True,
        "can_write_product_state": promoted_package_verification.get("can_write_product_state") is True,
        "target_record_count": len(promoted_package_verification.get("formal_target_verification_records", [])),
        "blocking_reasons": promoted_package_verification.get("blocking_reasons", []),
    }


def build_formal_package_summary(promoted_package_verification: dict[str, Any]) -> dict[str, Any]:
    records = promoted_package_verification.get("formal_target_verification_records", [])
    return {
        "formal_target_count": len(records),
        "target_groups": [record.get("writeback_target_group", "") for record in records],
        "formal_target_paths": [record.get("formal_target_path", "") for record in records],
        "all_targets_verified": bool(records) and all(
            record.get("verification_status") == "verified" for record in records
        ),
    }


def build_export_acceptance_plan(promoted_package_verification: dict[str, Any]) -> list[dict[str, Any]]:
    records = promoted_package_verification.get("formal_target_verification_records", [])
    formal_targets = [record.get("formal_target_path", "") for record in records]
    return [
        build_plan_item(
            "formal_pdf_export_preflight",
            "Prepare formal PDF export preflight",
            "Confirm the verified formal package can feed a later PDF export command.",
            formal_targets,
        ),
        build_plan_item(
            "formal_docx_export_preflight",
            "Prepare formal DOCX export preflight",
            "Confirm the verified formal package can feed a later DOCX export command.",
            formal_targets,
        ),
        build_plan_item(
            "formal_submission_package_manifest_preflight",
            "Prepare formal submission package manifest preflight",
            "Confirm PDF/DOCX/package manifest generation remains a later explicit step.",
            formal_targets,
        ),
        build_plan_item(
            "manual_acceptance_packet_preflight",
            "Prepare manual acceptance packet preflight",
            "Confirm human acceptance can review the verified formal target list.",
            formal_targets,
        ),
    ]


def build_plan_item(
    action_id: str,
    label: str,
    description: str,
    formal_targets: list[str],
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "label": label,
        "description": description,
        "source_formal_targets": formal_targets,
        "execution_status": "pending_explicit_export_or_acceptance_command",
        "requires_explicit_export_or_acceptance_command": True,
        "this_command_rendered_or_accepted": False,
        "this_command_wrote_product_state": False,
    }


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
    }


def build_next_action(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    if status == "ready_for_formal_package_export_acceptance_review":
        return {
            "id": "review_formal_package_export_acceptance_preflight",
            "label": "Review formal package export / acceptance preflight",
            "description": "The verified formal package can proceed to a separate export or acceptance command.",
        }
    if status == "blocked_by_promoted_package_verification_boundary":
        return {
            "id": "repair_promoted_package_verification_boundary",
            "label": "Repair promoted package verification boundary",
            "description": "P7-W must be read-only before it can feed export / acceptance preflight.",
            "blocking_reasons": blocking_reasons,
        }
    if status == "blocked_by_formal_package_target_records":
        return {
            "id": "repair_formal_package_target_records",
            "label": "Repair formal package target records",
            "description": "Formal package target records must be verified and inside the formal package.",
            "blocking_reasons": blocking_reasons,
        }
    return {
        "id": "complete_promoted_package_verification",
        "label": "Complete promoted package verification",
        "description": "P7-W must verify the formal package before export / acceptance preflight can run.",
        "blocking_reasons": blocking_reasons,
    }


def write_auto_mode_formal_package_export_acceptance_preflight_outputs(
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
        "# Auto Mode Formal Package Export / Acceptance Preflight",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        f"- 可进入导出/验收：{str(report['can_enter_formal_package_export_acceptance']).lower()}",
        f"- 需要显式导出/验收命令：{str(report['requires_explicit_export_or_acceptance_command']).lower()}",
        f"- 已执行导出/验收：{str(report['export_or_acceptance_executed']).lower()}",
        f"- 已渲染 PDF：{str(report['rendered_pdf']).lower()}",
        f"- 已渲染 DOCX：{str(report['rendered_docx']).lower()}",
        f"- 本命令写入正式层：{str(report['this_command_wrote_formal_state']).lower()}",
        f"- 写入 state/product：{str(report['can_write_product_state']).lower()}",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## Blocking Reasons"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## Export / Acceptance Plan"])
    if report["export_acceptance_plan"]:
        for item in report["export_acceptance_plan"]:
            lines.append(f"- `{item['action_id']}`: {item['execution_status']}")
    else:
        lines.append("- 无；等待 promoted formal package verification ready。")
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

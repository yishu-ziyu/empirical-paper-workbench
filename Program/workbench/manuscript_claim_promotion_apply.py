from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


def build_manuscript_claim_promotion_apply(
    project_root: Path,
    *,
    patch_report_path: Path,
    reviewer: str,
    note: str,
    confirm_apply: bool,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    patch_report = load_json(patch_report_path)
    operation = first_operation(patch_report)
    target_path = resolve_target_path(project_root, operation)
    blocking_reasons = build_blocking_reasons(
        patch_report=patch_report,
        operation=operation,
        target_path=target_path,
        reviewer=reviewer,
        note=note,
        confirm_apply=confirm_apply,
    )

    before_sha = sha256_file(target_path) if target_path and target_path.exists() else None
    applied_operations: list[dict[str, Any]] = []
    if not blocking_reasons and target_path is not None:
        approved_findings = load_json(target_path)
        apply_operation_to_approved_findings(approved_findings, operation, reviewer=reviewer, note=note)
        write_json(target_path, approved_findings)
        applied_operations.append(operation)
    after_sha = sha256_file(target_path) if target_path and target_path.exists() else None
    after = snapshot_formal_state(project_root)
    applied = bool(applied_operations)

    report = {
        "schema_version": "p6.manuscript_claim_promotion_apply.v1",
        "generated_at": utc_now(),
        "status": "claim_promotion_patch_applied" if applied else "claim_promotion_apply_blocked",
        "source_patch_report": relative_or_absolute(patch_report_path, project_root),
        "target_approved_findings": relative_or_absolute(target_path, project_root) if target_path else None,
        "formal_writeback_allowed": applied,
        "applied": applied,
        "applied_operations": applied_operations,
        "application_review": {
            "action": "apply",
            "reviewer": reviewer,
            "note": note,
            "applied_at": utc_now() if applied else None,
        },
        "approved_findings_before_sha256": before_sha,
        "approved_findings_after_sha256": after_sha,
        "blocking_reasons": blocking_reasons,
        "this_command_wrote_approved_findings": applied,
        "this_command_wrote_sections": False,
        "this_command_wrote_docx": False,
        "this_command_wrote_pdf": False,
        "this_command_wrote_state_product": False,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(applied),
    }
    return report, 0 if applied else 2


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def first_operation(patch_report: dict[str, Any]) -> dict[str, Any]:
    operations = patch_report.get("patch_operations") or []
    return operations[0] if operations else {}


def resolve_target_path(project_root: Path, operation: dict[str, Any]) -> Path | None:
    target = operation.get("target_path")
    if not target:
        return None
    path = Path(str(target))
    return path if path.is_absolute() else project_root / path


def build_blocking_reasons(
    *,
    patch_report: dict[str, Any],
    operation: dict[str, Any],
    target_path: Path | None,
    reviewer: str,
    note: str,
    confirm_apply: bool,
) -> list[str]:
    reasons: list[str] = []
    if patch_report.get("status") != "claim_promotion_patch_ready":
        reasons.append("patch_not_ready")
    if patch_report.get("ready_for_apply") is not True:
        reasons.append("patch_not_marked_ready_for_apply")
    if patch_report.get("applied") is True:
        reasons.append("patch_already_applied")
    if operation.get("type") != "add_claim_to_approved_finding":
        reasons.append("unsupported_patch_operation")
    if not operation.get("source_finding_id"):
        reasons.append("missing_source_finding_id")
    if not operation.get("claim_text"):
        reasons.append("missing_claim_text")
    if not reviewer.strip():
        reasons.append("missing_reviewer")
    if not note.strip():
        reasons.append("missing_review_note")
    if confirm_apply is not True:
        reasons.append("missing_confirm_apply")
    if target_path is None:
        reasons.append("missing_target_path")
    elif not target_path.exists():
        reasons.append("target_approved_findings_missing")
    else:
        approved_findings = load_json(target_path)
        if find_target_finding(approved_findings, str(operation.get("source_finding_id"))) is None:
            reasons.append("target_finding_missing")
    return reasons


def apply_operation_to_approved_findings(
    approved_findings: dict[str, Any],
    operation: dict[str, Any],
    *,
    reviewer: str,
    note: str,
) -> None:
    finding = find_target_finding(approved_findings, str(operation["source_finding_id"]))
    if finding is None:
        raise ValueError("target_finding_missing")
    finding["claim"] = operation["claim_text"]
    finding["claim_source_proposal_id"] = operation.get("proposal_id")
    finding["claim_source_table_id"] = operation.get("source_table_id")
    finding["claim_promoted_at"] = utc_now()
    finding["claim_promotion_review"] = {
        "action": "apply",
        "reviewer": reviewer,
        "note": note,
    }
    approved_findings["canonical_write_allowed"] = False
    approved_findings["last_claim_promotion"] = {
        "proposal_id": operation.get("proposal_id"),
        "finding_id": operation.get("source_finding_id"),
        "applied_at": finding["claim_promoted_at"],
        "reviewer": reviewer,
    }


def find_target_finding(approved_findings: dict[str, Any], finding_id: str) -> dict[str, Any] | None:
    for finding in approved_findings.get("findings") or []:
        if finding.get("finding_id") == finding_id and finding.get("review_status") == "approved":
            return finding
    return None


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_next_action(applied: bool) -> dict[str, str]:
    if applied:
        return {
            "id": "rerun_manuscript_section_claim_ledger",
            "label": "重跑章节论断账本",
            "description": "正式 finding 已有 claim，下一步可重新检查 Main Results 是否消费该论断。",
        }
    return {
        "id": "repair_claim_promotion_apply_inputs",
        "label": "修复 claim promotion apply 输入",
        "description": "先修复 patch、目标 finding 或显式确认参数，再重新运行 apply。",
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_manuscript_claim_promotion_apply_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    write_json(report_path, report)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(render_review_markdown(report), encoding="utf-8")
    return report_path, review_path


def render_review_markdown(report: dict[str, Any]) -> str:
    blockers = report.get("blocking_reasons") or []
    blocker_lines = "\n".join(f"- `{item}`" for item in blockers) if blockers else "- 无"
    operation = (report.get("applied_operations") or [{}])[0]
    return "\n".join(
        [
            "# Claim Promotion Apply",
            "",
            f"- 状态：`{report.get('status')}`",
            f"- applied：`{str(report.get('applied')).lower()}`",
            f"- formal_writeback_allowed：`{str(report.get('formal_writeback_allowed')).lower()}`",
            f"- target：`{report.get('target_approved_findings')}`",
            f"- before_sha256：`{report.get('approved_findings_before_sha256')}`",
            f"- after_sha256：`{report.get('approved_findings_after_sha256')}`",
            "",
            "## Applied Operation",
            "",
            f"- proposal_id：`{operation.get('proposal_id')}`",
            f"- source_finding_id：`{operation.get('source_finding_id')}`",
            f"- source_table_id：`{operation.get('source_table_id')}`",
            "",
            "## Blocking Reasons",
            "",
            blocker_lines,
            "",
        ]
    )

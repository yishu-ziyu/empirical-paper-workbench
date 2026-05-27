from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


def build_manuscript_claim_promotion_patch(
    project_root: Path,
    *,
    review_report_path: Path,
    target_approved_findings_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    review_report = load_json(review_report_path)
    proposal = review_report.get("proposal") or {}
    blocking_reasons = build_blocking_reasons(review_report, proposal)
    ready_for_apply = not blocking_reasons
    operation = build_patch_operation(project_root, target_approved_findings_path, review_report, proposal)
    after = snapshot_formal_state(project_root)

    report = {
        "schema_version": "p6.manuscript_claim_promotion_patch.v1",
        "generated_at": utc_now(),
        "status": "claim_promotion_patch_ready" if ready_for_apply else "claim_promotion_patch_blocked",
        "source_review_report": relative_or_absolute(review_report_path, project_root),
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "ready_for_apply": ready_for_apply,
        "applied": False,
        "patch_operations": [operation] if ready_for_apply else [],
        "human_review_evidence": review_report.get("human_review") or {},
        "blocking_reasons": blocking_reasons,
        "this_command_wrote_formal_state": False,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(ready_for_apply),
    }
    return report, 0 if ready_for_apply else 2


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_blocking_reasons(review_report: dict[str, Any], proposal: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if review_report.get("status") != "claim_proposal_approved_for_promotion":
        reasons.append("claim_proposal_not_approved_for_promotion")
    if review_report.get("promotion_allowed") is not True:
        reasons.append("promotion_not_allowed")
    if review_report.get("promoted_to_claims") is True:
        reasons.append("claim_proposal_already_promoted")
    if review_report.get("human_review", {}).get("action") != "approve":
        reasons.append("human_review_action_not_approve")
    if not proposal.get("proposal_id"):
        reasons.append("missing_proposal_id")
    if not proposal.get("source_finding_id"):
        reasons.append("missing_source_finding_id")
    if not proposal.get("proposed_claim_text"):
        reasons.append("missing_proposed_claim_text")
    return reasons


def build_patch_operation(
    project_root: Path,
    target_approved_findings_path: Path,
    review_report: dict[str, Any],
    proposal: dict[str, Any],
) -> dict[str, Any]:
    proposal_id = proposal.get("proposal_id")
    return {
        "operation_id": f"{proposal_id}::promote_claim",
        "type": "add_claim_to_approved_finding",
        "target_path": relative_or_absolute(target_approved_findings_path, project_root),
        "source_finding_id": proposal.get("source_finding_id"),
        "source_table_id": proposal.get("source_table_id"),
        "proposal_id": proposal_id,
        "claim_text": proposal.get("proposed_claim_text"),
        "review_report": review_report.get("source_claim_ledger"),
        "reviewer": review_report.get("human_review", {}).get("reviewer"),
        "review_note": review_report.get("human_review", {}).get("note"),
    }


def build_next_action(ready_for_apply: bool) -> dict[str, Any]:
    if ready_for_apply:
        return {
            "id": "apply_claim_promotion_patch_after_human_confirm",
            "owner_agent": "VerifierAgent",
            "reason": "补丁已生成；下一节点可以在显式确认后应用到正式 finding。",
        }
    return {
        "id": "fix_claim_promotion_patch_input",
        "owner_agent": "VerifierAgent",
        "reason": "review report 尚未满足写回补丁生成条件。",
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_manuscript_claim_promotion_patch(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_manuscript_claim_promotion_patch_markdown(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_manuscript_claim_promotion_patch_markdown(report), encoding="utf-8")
    return path


def build_manuscript_claim_promotion_patch_markdown(report: dict[str, Any]) -> str:
    operation = (report.get("patch_operations") or [{}])[0]
    lines = [
        "# Claim Promotion Patch",
        "",
        f"- 状态：`{report.get('status')}`",
        f"- ready_for_apply：`{str(report.get('ready_for_apply')).lower()}`",
        f"- applied：`{str(report.get('applied')).lower()}`",
        f"- formal_writeback_allowed：`{str(report.get('formal_writeback_allowed')).lower()}`",
        "",
        "## Patch Operation",
        "",
        f"- type：`{operation.get('type')}`",
        f"- target_path：`{operation.get('target_path')}`",
        f"- source_finding_id：`{operation.get('source_finding_id')}`",
        f"- source_table_id：`{operation.get('source_table_id')}`",
        f"- proposal_id：`{operation.get('proposal_id')}`",
        f"- claim_text：{operation.get('claim_text')}",
        "",
        "## Next Action",
        "",
        f"- `{report.get('next_action', {}).get('id')}`",
    ]
    for reason in report.get("blocking_reasons", []):
        lines.append(f"- 阻断：`{reason}`")
    lines.append("")
    return "\n".join(lines)

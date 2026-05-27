from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


VALID_ACTIONS = {"approve", "reject", "needs_revision"}
STATUS_BY_ACTION = {
    "approve": "claim_proposal_approved_for_promotion",
    "reject": "claim_proposal_rejected",
    "needs_revision": "claim_proposal_needs_revision",
}


def build_manuscript_claim_proposal_review(
    project_root: Path,
    *,
    claim_ledger_path: Path,
    proposal_id: str,
    action: str,
    reviewer: str,
    note: str,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    claim_ledger = load_json(claim_ledger_path)
    proposal = find_claim_proposal(claim_ledger, proposal_id)
    action_is_valid = action in VALID_ACTIONS
    blocking_reasons = build_blocking_reasons(proposal, action)
    status = STATUS_BY_ACTION.get(action, "claim_proposal_review_blocked") if proposal else "claim_proposal_not_found"
    after = snapshot_formal_state(project_root)

    report = {
        "schema_version": "p6.manuscript_claim_proposal_review.v1",
        "generated_at": utc_now(),
        "status": status if not blocking_reasons else "claim_proposal_review_blocked",
        "source_claim_ledger": relative_or_absolute(claim_ledger_path, project_root),
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "promotion_allowed": bool(proposal and action == "approve" and not blocking_reasons),
        "promoted_to_claims": False,
        "proposal": proposal,
        "human_review": {
            "proposal_id": proposal_id,
            "action": action,
            "reviewer": reviewer,
            "note": note,
            "reviewed_at": utc_now(),
        },
        "blocking_reasons": blocking_reasons,
        "this_command_wrote_formal_state": False,
        "this_command_promoted_claim": False,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(action, action_is_valid, proposal, blocking_reasons),
    }
    return report, 0 if proposal and action_is_valid and not blocking_reasons else 2


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_claim_proposal(claim_ledger: dict[str, Any], proposal_id: str) -> dict[str, Any] | None:
    for section in claim_ledger.get("sections", []):
        for proposal in section.get("claim_proposals", []):
            if proposal.get("proposal_id") == proposal_id:
                return proposal
    return None


def build_blocking_reasons(proposal: dict[str, Any] | None, action: str) -> list[str]:
    reasons: list[str] = []
    if proposal is None:
        reasons.append("claim_proposal_not_found")
    if action not in VALID_ACTIONS:
        reasons.append("invalid_review_action")
    if proposal and proposal.get("review_status") != "needs_human_review":
        reasons.append("claim_proposal_not_waiting_for_human_review")
    return reasons


def build_next_action(
    action: str,
    action_is_valid: bool,
    proposal: dict[str, Any] | None,
    blocking_reasons: list[str],
) -> dict[str, Any]:
    if blocking_reasons or not action_is_valid or proposal is None:
        return {
            "id": "fix_claim_proposal_review_input",
            "owner_agent": "VerifierAgent",
            "reason": "审阅动作或 proposal id 无法通过校验；需要先修正输入。",
        }
    if action == "approve":
        return {
            "id": "promote_reviewed_proposal_in_separate_node",
            "owner_agent": "VerifierAgent",
            "reason": "人工已同意 proposal 进入下一步；正式论断写回必须由单独节点执行。",
        }
    if action == "reject":
        return {
            "id": "return_to_manuscript_or_finding_revision",
            "owner_agent": "ManuscriptAgent",
            "reason": "人工拒绝 proposal；回到草案层修订论断或证据解释。",
        }
    return {
        "id": "revise_claim_proposal",
        "owner_agent": "ManuscriptAgent",
        "reason": "人工要求修改 proposal；修改后再次进入审阅。",
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_manuscript_claim_proposal_review(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_manuscript_claim_proposal_review_markdown(path: Path, report: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_manuscript_claim_proposal_review_markdown(report), encoding="utf-8")
    return path


def build_manuscript_claim_proposal_review_markdown(report: dict[str, Any]) -> str:
    proposal = report.get("proposal") or {}
    human_review = report.get("human_review", {})
    lines = [
        "# Claim Proposal Review",
        "",
        f"- 状态：`{report.get('status')}`",
        f"- proposal：`{human_review.get('proposal_id')}`",
        f"- 动作：`{human_review.get('action')}`",
        f"- 审阅人：`{human_review.get('reviewer')}`",
        f"- promotion_allowed：`{str(report.get('promotion_allowed')).lower()}`",
        f"- promoted_to_claims：`{str(report.get('promoted_to_claims')).lower()}`",
        f"- formal_writeback_allowed：`{str(report.get('formal_writeback_allowed')).lower()}`",
        "",
        "## Proposal",
        "",
        f"- proposed_claim_text：{proposal.get('proposed_claim_text')}",
        f"- source_finding_id：`{proposal.get('source_finding_id')}`",
        f"- source_table_id：`{proposal.get('source_table_id')}`",
        "",
        "## Note",
        "",
        human_review.get("note") or "",
        "",
        "## Next Action",
        "",
        f"- `{report.get('next_action', {}).get('id')}`",
    ]
    for reason in report.get("blocking_reasons", []):
        lines.append(f"- 阻断：`{reason}`")
    lines.append("")
    return "\n".join(lines)

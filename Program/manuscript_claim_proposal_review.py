from __future__ import annotations

import argparse
from pathlib import Path

from workbench.manuscript_claim_proposal_review import (
    build_manuscript_claim_proposal_review,
    write_manuscript_claim_proposal_review,
    write_manuscript_claim_proposal_review_markdown,
)
from workbench.paper_revision_round import snapshot_formal_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record a human review decision for a manuscript claim proposal.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--claim-ledger",
        default="Results/json/manuscript_section_claim_ledger.json",
        help="Claim ledger JSON path relative to project root.",
    )
    parser.add_argument("--proposal-id", required=True, help="Claim proposal id to review.")
    parser.add_argument("--action", required=True, help="One of approve, reject, needs_revision.")
    parser.add_argument("--reviewer", required=True, help="Human reviewer name or id.")
    parser.add_argument("--note", default="", help="Human review note.")
    parser.add_argument(
        "--output-report",
        default="Results/json/manuscript_claim_proposal_review.json",
        help="Output review JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/manuscript_claim_proposal_review.md",
        help="Output human-readable review path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    claim_ledger_path = resolve_path(project_root, args.claim_ledger)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)

    if not claim_ledger_path.exists():
        raise FileNotFoundError(f"Manuscript section claim ledger not found: {args.claim_ledger}")

    formal_state_before = snapshot_formal_state(project_root)
    report, exit_code = build_manuscript_claim_proposal_review(
        project_root,
        claim_ledger_path=claim_ledger_path,
        proposal_id=args.proposal_id,
        action=args.action,
        reviewer=args.reviewer,
        note=args.note,
        formal_state_before=formal_state_before,
    )
    report_path = write_manuscript_claim_proposal_review(output_report_path, report)
    review_path = write_manuscript_claim_proposal_review_markdown(output_review_path, report)

    print(f"[econ-workbench] manuscript_claim_proposal_review={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] manuscript_claim_proposal_review_md={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] action={report.get('human_review', {}).get('action')}")
    print(f"[econ-workbench] promotion_allowed={str(report.get('promotion_allowed')).lower()}")
    print(f"[econ-workbench] promoted_to_claims={str(report.get('promoted_to_claims')).lower()}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report.get('formal_writeback_allowed')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

from workbench.manuscript_claim_promotion_patch import (
    build_manuscript_claim_promotion_patch,
    write_manuscript_claim_promotion_patch,
    write_manuscript_claim_promotion_patch_markdown,
)
from workbench.paper_revision_round import snapshot_formal_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a formal-claim promotion patch from an approved claim proposal.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--review-report",
        default="Results/json/manuscript_claim_proposal_review.json",
        help="Claim proposal review JSON path relative to project root.",
    )
    parser.add_argument(
        "--target-approved-findings",
        default="Results/json/approved_findings.json",
        help="Formal approved findings JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/manuscript_claim_promotion_patch.json",
        help="Output patch JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/manuscript_claim_promotion_patch.md",
        help="Output human-readable patch review path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    review_report_path = resolve_path(project_root, args.review_report)
    target_approved_findings_path = resolve_path(project_root, args.target_approved_findings)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)

    if not review_report_path.exists():
        raise FileNotFoundError(f"Claim proposal review report not found: {args.review_report}")

    formal_state_before = snapshot_formal_state(project_root)
    report, exit_code = build_manuscript_claim_promotion_patch(
        project_root,
        review_report_path=review_report_path,
        target_approved_findings_path=target_approved_findings_path,
        formal_state_before=formal_state_before,
    )
    report_path = write_manuscript_claim_promotion_patch(output_report_path, report)
    review_path = write_manuscript_claim_promotion_patch_markdown(output_review_path, report)

    print(f"[econ-workbench] manuscript_claim_promotion_patch={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] manuscript_claim_promotion_patch_md={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] ready_for_apply={str(report.get('ready_for_apply')).lower()}")
    print(f"[econ-workbench] applied={str(report.get('applied')).lower()}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report.get('formal_writeback_allowed')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

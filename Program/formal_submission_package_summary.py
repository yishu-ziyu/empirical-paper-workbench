from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_submission_package_summary import (
    DEFAULT_APPROVED_CANDIDATE_SNAPSHOT,
    DEFAULT_OUTPUT_REPORT,
    DEFAULT_OUTPUT_REVIEW,
    DEFAULT_OUTPUT_SUMMARY,
    DEFAULT_SOURCE_MANIFEST,
    build_formal_submission_package_summary,
    write_formal_submission_package_summary_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Expose the formal submission package as a compact product acceptance state.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument("--source-manifest", default=DEFAULT_SOURCE_MANIFEST, help="P6-D formal package manifest report.")
    parser.add_argument("--approved-candidate-snapshot", default=DEFAULT_APPROVED_CANDIDATE_SNAPSHOT)
    parser.add_argument(
        "--output-report",
        default=DEFAULT_OUTPUT_REPORT,
        help="Full summary report path relative to project root.",
    )
    parser.add_argument(
        "--output-summary",
        default=DEFAULT_OUTPUT_SUMMARY,
        help="Product state summary path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_OUTPUT_REVIEW,
        help="Human-readable product acceptance entry review path relative to project root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    summary, exit_code = build_formal_submission_package_summary(
        project_root,
        source_manifest_path=project_root / args.source_manifest,
        approved_candidate_snapshot_path=project_root / args.approved_candidate_snapshot,
    )
    report_path, summary_path, review_path = write_formal_submission_package_summary_outputs(
        project_root / args.output_report,
        project_root / args.output_summary,
        project_root / args.output_review,
        summary,
    )
    print(f"[econ-workbench] formal_submission_package_summary_report={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_submission_package_summary_state={summary_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_submission_package_summary_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={summary.get('status')}")
    print(f"[econ-workbench] ready_for_manual_acceptance={str(summary.get('ready_for_manual_acceptance')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

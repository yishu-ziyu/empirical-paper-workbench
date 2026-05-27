from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_submission_package_manual_acceptance import (
    DEFAULT_OUTPUT_REPORT,
    DEFAULT_OUTPUT_REVIEW,
    DEFAULT_OUTPUT_STATE,
    DEFAULT_SUMMARY,
    VALID_DECISIONS,
    build_formal_submission_package_manual_acceptance,
    snapshot_protected_formal_state,
    write_formal_submission_package_manual_acceptance_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record human manual acceptance for the formal submission package.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument("--summary", default=DEFAULT_SUMMARY, help="Formal package summary JSON path.")
    parser.add_argument(
        "--decision",
        choices=sorted(VALID_DECISIONS),
        required=True,
        help="Human decision for the formal PDF/DOCX package.",
    )
    parser.add_argument("--actor", default="user", help="Acceptance actor.")
    parser.add_argument("--note", default="", help="Human acceptance note.")
    parser.add_argument("--output-report", default=DEFAULT_OUTPUT_REPORT)
    parser.add_argument("--output-state", default=DEFAULT_OUTPUT_STATE)
    parser.add_argument("--output-review", default=DEFAULT_OUTPUT_REVIEW)
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    summary_path = resolve_path(project_root, args.summary)
    output_report_path = resolve_path(project_root, args.output_report)
    output_state_path = resolve_path(project_root, args.output_state)
    output_review_path = resolve_path(project_root, args.output_review)

    report, exit_code = build_formal_submission_package_manual_acceptance(
        project_root,
        summary_path=summary_path,
        decision=args.decision,
        actor=args.actor,
        note=args.note,
        formal_state_before=snapshot_protected_formal_state(project_root),
    )
    report_path, state_path, review_path = write_formal_submission_package_manual_acceptance_outputs(
        output_report_path,
        output_state_path,
        output_review_path,
        report,
    )

    print(f"[econ-workbench] formal_submission_package_manual_acceptance={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_submission_package_manual_acceptance_state={state_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_submission_package_manual_acceptance_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] accepted={str(report.get('accepted')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_package_provenance_lock_check import (
    DEFAULT_DOCX_EXPORT_REPORT,
    DEFAULT_FINAL_WRITEBACK_REPORT,
    DEFAULT_OUTPUT_REPORT,
    DEFAULT_OUTPUT_REVIEW,
    DEFAULT_PACKAGE_MANIFEST,
    DEFAULT_SUBMISSION_MANIFEST_REPORT,
    DEFAULT_SUBMISSION_SUMMARY_REPORT,
    build_formal_package_provenance_lock_check,
    write_formal_package_provenance_lock_check_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether the formal package still has locked provenance.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument("--final-writeback-report", default=DEFAULT_FINAL_WRITEBACK_REPORT)
    parser.add_argument("--docx-export-report", default=DEFAULT_DOCX_EXPORT_REPORT)
    parser.add_argument("--submission-manifest-report", default=DEFAULT_SUBMISSION_MANIFEST_REPORT)
    parser.add_argument("--submission-summary-report", default=DEFAULT_SUBMISSION_SUMMARY_REPORT)
    parser.add_argument("--package-manifest", default=DEFAULT_PACKAGE_MANIFEST)
    parser.add_argument("--output-report", default=DEFAULT_OUTPUT_REPORT)
    parser.add_argument("--output-review", default=DEFAULT_OUTPUT_REVIEW)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    report, exit_code = build_formal_package_provenance_lock_check(
        project_root,
        final_writeback_report_path=project_root / args.final_writeback_report,
        docx_export_report_path=project_root / args.docx_export_report,
        submission_manifest_report_path=project_root / args.submission_manifest_report,
        submission_summary_report_path=project_root / args.submission_summary_report,
        package_manifest_path=project_root / args.package_manifest,
    )
    report_path, review_path = write_formal_package_provenance_lock_check_outputs(
        project_root / args.output_report,
        project_root / args.output_review,
        report,
    )
    print(f"[econ-workbench] formal_package_provenance_lock_check_report={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_package_provenance_lock_check_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(
        "[econ-workbench] can_continue_manual_acceptance="
        f"{str((report.get('final_package_acceptance') or {}).get('can_continue_manual_acceptance')).lower()}"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

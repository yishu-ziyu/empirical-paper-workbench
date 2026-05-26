from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_submission_package_manifest import (
    DEFAULT_OUTPUT_REPORT,
    DEFAULT_OUTPUT_REVIEW,
    DEFAULT_P6A_REPORT,
    DEFAULT_P6B_REPORT,
    DEFAULT_P6C_REPORT,
    DEFAULT_PACKAGE_MANIFEST,
    build_formal_submission_package_manifest,
    write_formal_submission_package_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble the formal submission package manifest for manual acceptance.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument("--p6a-report", default=DEFAULT_P6A_REPORT, help="P6-A final PDF writeback report.")
    parser.add_argument("--p6b-report", default=DEFAULT_P6B_REPORT, help="P6-B formal docx preflight report.")
    parser.add_argument("--p6c-report", default=DEFAULT_P6C_REPORT, help="P6-C formal docx export report.")
    parser.add_argument(
        "--output-report",
        default=DEFAULT_OUTPUT_REPORT,
        help="Formal submission package manifest report path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_OUTPUT_REVIEW,
        help="Human-readable package acceptance review path relative to project root.",
    )
    parser.add_argument(
        "--package-manifest",
        default=DEFAULT_PACKAGE_MANIFEST,
        help="Self-contained manifest path inside the formal package.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    report, exit_code = build_formal_submission_package_manifest(
        project_root,
        p6a_report_path=project_root / args.p6a_report,
        p6b_report_path=project_root / args.p6b_report,
        p6c_report_path=project_root / args.p6c_report,
        package_manifest_path=project_root / args.package_manifest,
    )
    report_path, review_path = write_formal_submission_package_outputs(
        project_root / args.output_report,
        project_root / args.output_review,
        report,
    )
    print(f"[econ-workbench] formal_submission_package_manifest={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_submission_package_acceptance={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] package_manifest_written={str(report.get('package_manifest_written')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_docx_export_preflight import (
    DEFAULT_APPROVAL_LEDGER,
    DEFAULT_APPROVAL_REPORT,
    DEFAULT_EXPECTED_DOCX,
    DEFAULT_FINAL_WRITEBACK_REPORT,
    DEFAULT_OUTPUT_REPORT,
    DEFAULT_OUTPUT_REVIEW,
    build_formal_docx_export_preflight,
    write_formal_docx_export_preflight_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight formal package docx export without generating docx.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--final-writeback-report",
        default=DEFAULT_FINAL_WRITEBACK_REPORT,
        help="Final PDF writeback report path relative to project root.",
    )
    parser.add_argument(
        "--approval-report",
        default=DEFAULT_APPROVAL_REPORT,
        help="Final PDF approval report path relative to project root.",
    )
    parser.add_argument(
        "--approval-ledger",
        default=DEFAULT_APPROVAL_LEDGER,
        help="Writeback approval ledger path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_OUTPUT_REPORT,
        help="Preflight JSON output path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_OUTPUT_REVIEW,
        help="Human-readable review output path relative to project root.",
    )
    parser.add_argument(
        "--expected-docx",
        default=DEFAULT_EXPECTED_DOCX,
        help="Expected final docx path relative to project root.",
    )
    parser.add_argument("--pandoc-bin", default="pandoc", help="Pandoc executable to inspect.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    report, exit_code = build_formal_docx_export_preflight(
        project_root,
        final_writeback_report_path=project_root / args.final_writeback_report,
        approval_report_path=project_root / args.approval_report,
        approval_ledger_path=project_root / args.approval_ledger,
        expected_docx_path=project_root / args.expected_docx,
        pandoc_bin=args.pandoc_bin,
    )
    report_path, review_path = write_formal_docx_export_preflight_outputs(
        project_root / args.output_report,
        project_root / args.output_review,
        report,
    )
    print(f"[econ-workbench] formal_docx_export_preflight={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_docx_export_preflight_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] can_export_docx={str(report.get('can_export_docx')).lower()}")
    print(f"[econ-workbench] wrote_docx={str(report.get('this_command_wrote_docx')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

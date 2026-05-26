from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_pdf_final_writeback import (
    DEFAULT_APPROVAL_LEDGER,
    DEFAULT_APPROVAL_REPORT,
    DEFAULT_CANDIDATE_REPORT,
    DEFAULT_FINAL_PREFLIGHT,
    DEFAULT_OUTPUT_PDF,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_formal_pdf_final_writeback,
    snapshot_formal_state,
    write_formal_pdf_final_writeback_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote an approved PDF candidate into the final package.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--candidate-report",
        default=DEFAULT_CANDIDATE_REPORT,
        help="PDF candidate report path relative to project root.",
    )
    parser.add_argument(
        "--final-preflight",
        default=DEFAULT_FINAL_PREFLIGHT,
        help="Final writeback preflight path relative to project root.",
    )
    parser.add_argument(
        "--approval-report",
        default=DEFAULT_APPROVAL_REPORT,
        help="Final approval report path relative to project root.",
    )
    parser.add_argument(
        "--approval-ledger",
        default=DEFAULT_APPROVAL_LEDGER,
        help="Writeback approval ledger path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_REPORT_PATH,
        help="Output final writeback report JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_REVIEW_PATH,
        help="Output final writeback review Markdown path relative to project root.",
    )
    parser.add_argument(
        "--output-pdf",
        default=DEFAULT_OUTPUT_PDF,
        help="Output final PDF path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    candidate_report_path = resolve_path(project_root, args.candidate_report)
    final_preflight_path = resolve_path(project_root, args.final_preflight)
    approval_report_path = resolve_path(project_root, args.approval_report)
    approval_ledger_path = resolve_path(project_root, args.approval_ledger)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    output_pdf_path = resolve_path(project_root, args.output_pdf)

    report, exit_code = build_formal_pdf_final_writeback(
        project_root,
        candidate_report_path=candidate_report_path,
        final_preflight_path=final_preflight_path,
        approval_report_path=approval_report_path,
        approval_ledger_path=approval_ledger_path,
        output_pdf_path=output_pdf_path,
        formal_state_before=snapshot_formal_state(project_root),
    )
    report_path, review_path = write_formal_pdf_final_writeback_outputs(
        output_report_path,
        output_review_path,
        report,
    )

    print(f"[econ-workbench] formal_pdf_final_writeback={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_pdf_final_writeback_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] final_pdf={report.get('final_pdf')}")
    print(f"[econ-workbench] wrote_final_pdf={str(report.get('this_command_wrote_final_pdf')).lower()}")
    print(f"[econ-workbench] wrote_docx={str(report.get('this_command_wrote_docx')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

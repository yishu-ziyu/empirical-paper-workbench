from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_pdf_candidate_review import (
    DEFAULT_CANDIDATE_REPORT,
    DEFAULT_FINAL_PREFLIGHT,
    DEFAULT_REVIEW_DOC,
    DEFAULT_REVIEW_REPORT,
    build_formal_pdf_candidate_review,
    snapshot_formal_state,
    write_formal_pdf_candidate_review_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review a P5 formal PDF candidate before final writeback.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--candidate-report",
        default=DEFAULT_CANDIDATE_REPORT,
        help="PDF candidate report path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_REVIEW_REPORT,
        help="Output candidate review JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_REVIEW_DOC,
        help="Output candidate review Markdown path relative to project root.",
    )
    parser.add_argument(
        "--output-final-preflight",
        default=DEFAULT_FINAL_PREFLIGHT,
        help="Output final writeback preflight JSON path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    candidate_report_path = resolve_path(project_root, args.candidate_report)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    output_final_preflight_path = resolve_path(project_root, args.output_final_preflight)

    report, final_preflight, exit_code = build_formal_pdf_candidate_review(
        project_root,
        candidate_report_path=candidate_report_path,
        output_report_path=output_report_path,
        output_review_path=output_review_path,
        output_final_preflight_path=output_final_preflight_path,
        formal_state_before=snapshot_formal_state(project_root),
    )
    report_path, review_path, final_preflight_path = write_formal_pdf_candidate_review_outputs(
        output_report_path,
        output_review_path,
        output_final_preflight_path,
        report,
        final_preflight,
    )

    print(f"[econ-workbench] formal_pdf_candidate_review={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_pdf_candidate_review_doc={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_pdf_final_writeback_preflight={final_preflight_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] can_request_final_approval={str(report.get('can_request_final_approval')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_pdf_candidate import (
    DEFAULT_PDF_PATH,
    DEFAULT_PREFLIGHT_REPORT,
    DEFAULT_QMD_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REPRODUCE_SCRIPT,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SOURCE_MAP,
    build_formal_pdf_candidate,
    snapshot_formal_state,
    write_formal_pdf_candidate_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a P5 formal paper PDF candidate.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--preflight-report",
        default=DEFAULT_PREFLIGHT_REPORT,
        help="Formal PDF export preflight report path relative to project root.",
    )
    parser.add_argument(
        "--source-map",
        default=DEFAULT_SOURCE_MAP,
        help="Formal manuscript source map path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_REPORT_PATH,
        help="Output PDF candidate report JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_REVIEW_PATH,
        help="Output PDF candidate review Markdown path relative to project root.",
    )
    parser.add_argument(
        "--output-qmd",
        default=DEFAULT_QMD_PATH,
        help="Output QMD candidate source path relative to project root.",
    )
    parser.add_argument(
        "--output-pdf",
        default=DEFAULT_PDF_PATH,
        help="Output PDF candidate path relative to project root.",
    )
    parser.add_argument(
        "--reproduce-script",
        default=DEFAULT_REPRODUCE_SCRIPT,
        help="Output shell script for rerunning candidate render.",
    )
    parser.add_argument(
        "--render-mode",
        choices=["auto", "source-only"],
        default="auto",
        help="auto renders PDF when toolchain is ready; source-only writes QMD/report without rendering.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    preflight_report_path = resolve_path(project_root, args.preflight_report)
    source_map_path = resolve_path(project_root, args.source_map)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    output_qmd_path = resolve_path(project_root, args.output_qmd)
    output_pdf_path = resolve_path(project_root, args.output_pdf)
    reproduce_script_path = resolve_path(project_root, args.reproduce_script)

    report, exit_code = build_formal_pdf_candidate(
        project_root,
        preflight_report_path=preflight_report_path,
        source_map_path=source_map_path,
        output_report_path=output_report_path,
        output_review_path=output_review_path,
        output_qmd_path=output_qmd_path,
        output_pdf_path=output_pdf_path,
        reproduce_script_path=reproduce_script_path,
        render_mode=args.render_mode,
        formal_state_before=snapshot_formal_state(project_root),
    )
    report_path, review_path = write_formal_pdf_candidate_outputs(
        output_report_path,
        output_review_path,
        report,
    )

    print(f"[econ-workbench] formal_pdf_candidate={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_pdf_candidate_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] output_qmd={report.get('output_qmd')}")
    print(f"[econ-workbench] output_pdf={report.get('output_pdf')}")
    print(f"[econ-workbench] output_pdf_exists={str(report.get('output_pdf_exists')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

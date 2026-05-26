from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_docx_export import (
    DEFAULT_GENERIC_MANIFEST,
    DEFAULT_LOG_PATH,
    DEFAULT_OUTPUT_DOCX,
    DEFAULT_OUTPUT_REPORT,
    DEFAULT_OUTPUT_REVIEW,
    DEFAULT_PREFLIGHT_REPORT,
    build_formal_docx_export,
    write_formal_docx_export_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export the approved formal package docx after P6-B preflight.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--preflight-report",
        default=DEFAULT_PREFLIGHT_REPORT,
        help="Formal docx export preflight report path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_OUTPUT_REPORT,
        help="Formal docx export JSON report path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_OUTPUT_REVIEW,
        help="Human-readable formal docx export review path relative to project root.",
    )
    parser.add_argument(
        "--output-docx",
        default=DEFAULT_OUTPUT_DOCX,
        help="Final formal docx path relative to project root.",
    )
    parser.add_argument(
        "--log-path",
        default=DEFAULT_LOG_PATH,
        help="Formal docx export log path relative to project root.",
    )
    parser.add_argument(
        "--generic-manifest",
        default=DEFAULT_GENERIC_MANIFEST,
        help="Generic export manifest path written by Program/export_docx.py.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    repo_root = Path(__file__).resolve().parents[1]
    report, exit_code = build_formal_docx_export(
        project_root,
        repo_root=repo_root,
        preflight_report_path=project_root / args.preflight_report,
        output_docx_path=project_root / args.output_docx,
        log_path=project_root / args.log_path,
        generic_manifest_path=project_root / args.generic_manifest,
    )
    report_path, review_path = write_formal_docx_export_outputs(
        project_root / args.output_report,
        project_root / args.output_review,
        report,
    )
    print(f"[econ-workbench] formal_docx_export={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_docx_export_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] docx={report.get('docx')}")
    print(f"[econ-workbench] wrote_docx={str(report.get('this_command_wrote_docx')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

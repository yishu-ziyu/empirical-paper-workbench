from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_pdf_export_preflight import (
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SOURCE_MAP,
    DEFAULT_TASKS_PATH,
    build_formal_pdf_export_preflight,
    snapshot_formal_state,
    write_formal_pdf_export_preflight_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight P5 formal PDF export readiness.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--source-map",
        default=DEFAULT_SOURCE_MAP,
        help="P5-C formal manuscript source map path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_REPORT_PATH,
        help="Output formal PDF export preflight JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_REVIEW_PATH,
        help="Output formal PDF export preflight Markdown path relative to project root.",
    )
    parser.add_argument(
        "--output-tasks",
        default=DEFAULT_TASKS_PATH,
        help="Output formal PDF export preflight task JSON path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    source_map_path = resolve_path(project_root, args.source_map)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    output_tasks_path = resolve_path(project_root, args.output_tasks)

    formal_state_before = snapshot_formal_state(project_root)
    report = build_formal_pdf_export_preflight(
        project_root,
        source_map_path,
        output_report_path=output_report_path,
        formal_state_before=formal_state_before,
    )
    report_path, review_path, tasks_path = write_formal_pdf_export_preflight_outputs(
        output_report_path,
        output_review_path,
        output_tasks_path,
        report,
    )

    print(f"[econ-workbench] formal_pdf_export_preflight={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_pdf_export_preflight_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] preflight_tasks={tasks_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] can_export_pdf_candidate={str(report.get('can_export_pdf_candidate')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

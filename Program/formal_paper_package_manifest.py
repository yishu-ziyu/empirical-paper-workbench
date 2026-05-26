from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_paper_package_manifest import (
    DEFAULT_APPROVAL_REPORT,
    DEFAULT_APPROVAL_STATE,
    DEFAULT_PACKAGE_ROOT,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_formal_paper_package_manifest,
    load_json,
    snapshot_formal_state,
    write_formal_paper_package_manifest_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the P5 formal paper package manifest and skeleton.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--approval-report",
        default=DEFAULT_APPROVAL_REPORT,
        help="P5-A approval report path relative to project root.",
    )
    parser.add_argument(
        "--approval-state",
        default=DEFAULT_APPROVAL_STATE,
        help="Writeback approval state path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_REPORT_PATH,
        help="Output formal package manifest JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_REVIEW_PATH,
        help="Output formal package review Markdown path relative to project root.",
    )
    parser.add_argument(
        "--package-root",
        default=DEFAULT_PACKAGE_ROOT,
        help="Formal package root directory relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    approval_report_path = resolve_path(project_root, args.approval_report)
    approval_state_path = resolve_path(project_root, args.approval_state)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    package_root = resolve_path(project_root, args.package_root)

    if not approval_report_path.exists():
        raise FileNotFoundError(f"Formal writeback approval report not found: {args.approval_report}")
    if not approval_state_path.exists():
        raise FileNotFoundError(f"Formal writeback approval state not found: {args.approval_state}")

    formal_state_before = snapshot_formal_state(project_root)
    report = build_formal_paper_package_manifest(
        project_root,
        load_json(approval_report_path),
        approval_report_path,
        load_json(approval_state_path),
        approval_state_path,
        package_root,
        formal_state_before=formal_state_before,
    )
    report_path, review_path = write_formal_paper_package_manifest_outputs(
        output_report_path,
        output_review_path,
        report,
    )

    print(f"[econ-workbench] formal_paper_package_manifest={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_paper_package_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] package_root={package_root.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] can_build_package={str(report.get('can_build_package')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

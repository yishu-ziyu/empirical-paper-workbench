from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_package_candidate_snapshot_freeze import (
    DEFAULT_FINAL_WRITEBACK_REPORT,
    DEFAULT_OUTPUT_REPORT,
    DEFAULT_OUTPUT_REVIEW,
    DEFAULT_OUTPUT_SNAPSHOT,
    DEFAULT_PROVENANCE_LOCK_REPORT,
    build_formal_package_candidate_snapshot_freeze,
    write_formal_package_candidate_snapshot_freeze_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze the approved candidate PDF authority without rewriting final package artifacts."
    )
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument("--provenance-lock-report", default=DEFAULT_PROVENANCE_LOCK_REPORT)
    parser.add_argument("--final-writeback-report", default=DEFAULT_FINAL_WRITEBACK_REPORT)
    parser.add_argument("--output-report", default=DEFAULT_OUTPUT_REPORT)
    parser.add_argument("--output-review", default=DEFAULT_OUTPUT_REVIEW)
    parser.add_argument("--output-snapshot", default=DEFAULT_OUTPUT_SNAPSHOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    report, snapshot, exit_code = build_formal_package_candidate_snapshot_freeze(
        project_root,
        provenance_lock_report_path=project_root / args.provenance_lock_report,
        final_writeback_report_path=project_root / args.final_writeback_report,
        output_snapshot_path=project_root / args.output_snapshot,
    )
    report_path, review_path, snapshot_path = write_formal_package_candidate_snapshot_freeze_outputs(
        project_root / args.output_report,
        project_root / args.output_review,
        project_root / args.output_snapshot,
        report,
        snapshot,
    )
    print(f"[econ-workbench] formal_package_candidate_snapshot_freeze_report={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_package_candidate_snapshot_freeze_review={review_path.relative_to(project_root)}")
    if snapshot_path is not None:
        print(
            "[econ-workbench] formal_package_candidate_snapshot_freeze_snapshot="
            f"{snapshot_path.relative_to(project_root)}"
        )
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] snapshot_written={str(report.get('snapshot_written')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

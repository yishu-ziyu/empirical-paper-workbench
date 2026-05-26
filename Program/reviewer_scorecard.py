from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from workbench.reviewer_scorecard import build_reviewer_scorecard_report, write_reviewer_scorecard_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build P4 reviewer scorecard from method diagnostics.")
    parser.add_argument("--project-root", default=".", help="Project root.")
    parser.add_argument(
        "--output-report",
        default="Results/json/reviewer_scorecard_report.json",
        help="Output reviewer scorecard report path, relative to project root unless absolute.",
    )
    parser.add_argument("--profile", default="aer_like", help="Quality profile.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    output = Path(args.output_report)
    if not output.is_absolute():
        output = project_root / output

    try:
        report = build_reviewer_scorecard_report(project_root, profile=args.profile)
        report_path = write_reviewer_scorecard_report(project_root, report, output)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"[econ-workbench] reviewer_scorecard_failed={exc}", file=sys.stderr)
        return 1

    print(f"[econ-workbench] reviewer_scorecard={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] overall_verdict={report['overall_verdict']}")
    print(f"[econ-workbench] overall_score={report['overall_score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

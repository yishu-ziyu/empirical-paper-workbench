from __future__ import annotations

import argparse
from pathlib import Path

from workbench.paper_quality import build_paper_quality_report, write_paper_quality_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a paper package quality report.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--draft",
        default=None,
        help="Markdown draft path relative to project root. Defaults to generated draft paths.",
    )
    parser.add_argument(
        "--output",
        default="Results/json/paper_quality_report.json",
        help="Quality report path relative to project root.",
    )
    parser.add_argument(
        "--profile",
        choices=["general_working_paper", "aer_like"],
        default="general_working_paper",
        help="Quality profile. aer_like activates AEA/AER-style metadata gates.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    draft = resolve_path(project_root, args.draft)
    output = resolve_path(project_root, args.output)
    report = build_paper_quality_report(project_root, draft, profile=args.profile)
    report_path = write_paper_quality_report(project_root, report, output)
    print(f"[econ-workbench] paper_quality={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] verdict={','.join(report['verdict'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

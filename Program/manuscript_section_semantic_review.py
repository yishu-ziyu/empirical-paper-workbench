from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.manuscript_section_semantic_review import (
    build_manuscript_section_semantic_review,
    write_manuscript_section_semantic_review,
    write_manuscript_section_semantic_review_markdown,
)
from workbench.paper_revision_round import snapshot_formal_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review expanded manuscript sections against consumed evidence.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--draft-expansion-report",
        default="Results/json/manuscript_section_draft_expansion_report.json",
        help="Draft expansion report path relative to project root.",
    )
    parser.add_argument(
        "--section",
        action="append",
        default=[],
        help="Target manuscript section to review. Can be passed more than once.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/manuscript_section_semantic_review.json",
        help="Output semantic review JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/manuscript_section_semantic_review.md",
        help="Output semantic review Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def expanded_sections(report: dict) -> list[str]:
    return [
        section["section"]
        for section in report.get("sections", [])
        if section.get("section") and section.get("status") == "section_draft_expanded"
    ]


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    draft_expansion_report_path = resolve_path(project_root, args.draft_expansion_report)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)

    if not draft_expansion_report_path.exists():
        raise FileNotFoundError(f"Manuscript section draft expansion report not found: {args.draft_expansion_report}")

    formal_state_before = snapshot_formal_state(project_root)
    draft_expansion_report = json.loads(draft_expansion_report_path.read_text(encoding="utf-8"))
    target_sections = args.section or expanded_sections(draft_expansion_report)
    if not target_sections:
        raise ValueError("No target sections were requested and no expanded sections were found.")

    report = build_manuscript_section_semantic_review(
        project_root,
        draft_expansion_report,
        draft_expansion_report_path,
        target_sections=target_sections,
        formal_state_before=formal_state_before,
    )
    report_path = write_manuscript_section_semantic_review(output_report_path, report)
    review_path = write_manuscript_section_semantic_review_markdown(output_review_path, report)

    summary = report.get("summary", {})
    print(f"[econ-workbench] manuscript_section_semantic_review={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] manuscript_section_semantic_review_md={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] passed={summary.get('passed', 0)} needs_revision={summary.get('needs_revision', 0)}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report.get('formal_writeback_allowed')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

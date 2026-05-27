from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.manuscript_section_evidence_bindings import (
    build_manuscript_section_evidence_bindings_report,
    write_manuscript_section_evidence_bindings_report,
    write_manuscript_section_evidence_bindings_review,
)
from workbench.paper_revision_round import snapshot_formal_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bind draft manuscript section scaffolds to local evidence artifacts.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--revision-round",
        default="Results/json/paper_revision_round.json",
        help="Revision round JSON path relative to project root.",
    )
    parser.add_argument(
        "--scaffold-report",
        default="Results/json/manuscript_section_scaffold_report.json",
        help="Section scaffold report path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/manuscript_section_evidence_bindings.json",
        help="Output evidence binding report path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/manuscript_section_evidence_bindings.md",
        help="Output human review Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    revision_round_path = resolve_path(project_root, args.revision_round)
    scaffold_report_path = resolve_path(project_root, args.scaffold_report)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)

    if not revision_round_path.exists():
        raise FileNotFoundError(f"Paper revision round not found: {args.revision_round}")
    if not scaffold_report_path.exists():
        raise FileNotFoundError(f"Manuscript section scaffold report not found: {args.scaffold_report}")

    formal_state_before = snapshot_formal_state(project_root)
    revision_round = json.loads(revision_round_path.read_text(encoding="utf-8"))
    scaffold_report = json.loads(scaffold_report_path.read_text(encoding="utf-8"))
    report = build_manuscript_section_evidence_bindings_report(
        project_root,
        revision_round,
        revision_round_path,
        scaffold_report,
        scaffold_report_path,
        formal_state_before=formal_state_before,
    )
    report_path = write_manuscript_section_evidence_bindings_report(output_report_path, report)
    review_path = write_manuscript_section_evidence_bindings_review(output_review_path, report)

    summary = report.get("summary", {})
    print(f"[econ-workbench] manuscript_section_evidence_bindings={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] manuscript_section_evidence_bindings_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] bound={summary.get('bound', 0)} missing={summary.get('missing', 0)}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report.get('formal_writeback_allowed')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

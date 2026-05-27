from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.manuscript_section_draft_expansion import (
    build_manuscript_section_draft_expansion_report,
    write_manuscript_section_draft_expansion_report,
    write_manuscript_section_draft_expansion_review,
)
from workbench.paper_revision_round import snapshot_formal_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Expand draft manuscript sections from bound local evidence.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--evidence-bindings",
        default="Results/json/manuscript_section_evidence_bindings.json",
        help="Evidence binding report path relative to project root.",
    )
    parser.add_argument(
        "--section",
        action="append",
        default=[],
        help="Target manuscript section to expand. Can be passed more than once.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/manuscript_section_draft_expansion_report.json",
        help="Output draft expansion report path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/manuscript_section_draft_expansion.md",
        help="Output human review Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def evidence_bound_sections(evidence_bindings: dict) -> list[str]:
    return [
        section["section"]
        for section in evidence_bindings.get("sections", [])
        if section.get("section") and section.get("status") == "evidence_bound"
    ]


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    evidence_bindings_path = resolve_path(project_root, args.evidence_bindings)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)

    if not evidence_bindings_path.exists():
        raise FileNotFoundError(f"Manuscript section evidence bindings not found: {args.evidence_bindings}")

    formal_state_before = snapshot_formal_state(project_root)
    evidence_bindings = json.loads(evidence_bindings_path.read_text(encoding="utf-8"))
    target_sections = args.section or evidence_bound_sections(evidence_bindings)
    if not target_sections:
        raise ValueError("No target sections were requested and no evidence-bound sections were found.")

    report = build_manuscript_section_draft_expansion_report(
        project_root,
        evidence_bindings,
        evidence_bindings_path,
        target_sections=target_sections,
        formal_state_before=formal_state_before,
    )
    report_path = write_manuscript_section_draft_expansion_report(output_report_path, report)
    review_path = write_manuscript_section_draft_expansion_review(output_review_path, report)

    summary = report.get("summary", {})
    print(f"[econ-workbench] manuscript_section_draft_expansion_report={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] manuscript_section_draft_expansion_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] expanded={summary.get('expanded', 0)} blocked={summary.get('blocked', 0)}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report.get('formal_writeback_allowed')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

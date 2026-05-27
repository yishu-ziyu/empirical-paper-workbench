from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.manuscript_section_claim_ledger import (
    build_manuscript_section_claim_ledger,
    write_manuscript_section_claim_ledger,
    write_manuscript_section_claim_ledger_markdown,
)
from workbench.paper_revision_round import snapshot_formal_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a reviewable claim ledger from passed section semantic review.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--semantic-review",
        default="Results/json/manuscript_section_semantic_review.json",
        help="Semantic review report path relative to project root.",
    )
    parser.add_argument(
        "--section",
        action="append",
        default=[],
        help="Target manuscript section to ledger. Can be passed more than once.",
    )
    parser.add_argument(
        "--output-ledger",
        default="Results/json/manuscript_section_claim_ledger.json",
        help="Output claim ledger JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/manuscript_section_claim_ledger.md",
        help="Output claim ledger Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def passed_sections(report: dict) -> list[str]:
    return [
        section["section"]
        for section in report.get("sections", [])
        if section.get("section") and section.get("verdict") == "passed"
    ]


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    semantic_review_path = resolve_path(project_root, args.semantic_review)
    output_ledger_path = resolve_path(project_root, args.output_ledger)
    output_review_path = resolve_path(project_root, args.output_review)

    if not semantic_review_path.exists():
        raise FileNotFoundError(f"Manuscript section semantic review not found: {args.semantic_review}")

    formal_state_before = snapshot_formal_state(project_root)
    semantic_review = json.loads(semantic_review_path.read_text(encoding="utf-8"))
    target_sections = args.section or passed_sections(semantic_review)
    if not target_sections:
        raise ValueError("No target sections were requested and no passed semantic review sections were found.")

    report = build_manuscript_section_claim_ledger(
        project_root,
        semantic_review,
        semantic_review_path,
        target_sections=target_sections,
        formal_state_before=formal_state_before,
    )
    ledger_path = write_manuscript_section_claim_ledger(output_ledger_path, report)
    review_path = write_manuscript_section_claim_ledger_markdown(output_review_path, report)

    summary = report.get("summary", {})
    print(f"[econ-workbench] manuscript_section_claim_ledger={ledger_path.relative_to(project_root)}")
    print(f"[econ-workbench] manuscript_section_claim_ledger_md={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] claims={summary.get('claims', 0)} needs_revision={summary.get('needs_revision', 0)}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report.get('formal_writeback_allowed')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

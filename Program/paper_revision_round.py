from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.paper_revision_round import (
    build_paper_revision_round,
    snapshot_formal_state,
    write_manuscript_section_work_order_files,
    write_paper_revision_round,
    write_revision_review_markdown,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a reviewable paper revision round from the Agent Task Queue.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--expansion-plan",
        default="Results/json/paper_expansion_plan.json",
        help="Paper expansion plan path relative to project root.",
    )
    parser.add_argument(
        "--supervisor-context",
        default="Results/json/paper_supervisor_context.json",
        help="Optional Supervisor context path relative to project root.",
    )
    parser.add_argument(
        "--output-round",
        default="Results/json/paper_revision_round.json",
        help="Output revision round JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/paper_revision_round.md",
        help="Output human review Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def load_optional_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    expansion_plan_path = resolve_path(project_root, args.expansion_plan)
    supervisor_context_path = resolve_path(project_root, args.supervisor_context)
    output_round_path = resolve_path(project_root, args.output_round)
    output_review_path = resolve_path(project_root, args.output_review)

    if not expansion_plan_path.exists():
        raise FileNotFoundError(f"Paper expansion plan not found: {args.expansion_plan}")

    formal_state_before = snapshot_formal_state(project_root)
    expansion_plan = json.loads(expansion_plan_path.read_text(encoding="utf-8"))
    supervisor_context = load_optional_json(supervisor_context_path)
    revision_round = build_paper_revision_round(
        project_root,
        expansion_plan,
        expansion_plan_path,
        supervisor_context=supervisor_context,
        supervisor_context_path=supervisor_context_path if supervisor_context is not None else None,
        formal_state_before=formal_state_before,
    )
    round_path = write_paper_revision_round(output_round_path, revision_round)
    review_path = write_revision_review_markdown(output_review_path, revision_round)
    section_work_order_paths = write_manuscript_section_work_order_files(project_root, revision_round)

    print(f"[econ-workbench] paper_revision_round={round_path.relative_to(project_root)}")
    print(f"[econ-workbench] revision_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] agent_packets={len(revision_round.get('agent_packets', []))}")
    print(f"[econ-workbench] manuscript_section_work_orders={len(section_work_order_paths)}")
    print(f"[econ-workbench] formal_writeback_allowed={str(revision_round.get('formal_writeback_allowed')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.paper_package import (
    build_paper_expansion_plan,
    build_structured_manuscript,
    build_supervisor_context_bundle,
    write_paper_expansion_plan,
    write_structured_manuscript,
    write_supervisor_context_bundle,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a PDF-first paper package plan and structured manuscript.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--quality-report",
        default="Results/json/paper_quality_report.json",
        help="Paper quality report path relative to project root.",
    )
    parser.add_argument(
        "--source-draft",
        default=None,
        help="Optional source draft path relative to project root. Defaults to the draft in the quality report.",
    )
    parser.add_argument(
        "--source-manifest",
        default=None,
        help="Optional PDF export manifest path relative to project root. Its next_review_tasks enter the next Supervisor queue.",
    )
    parser.add_argument(
        "--output-plan",
        default="Results/json/paper_expansion_plan.json",
        help="Expansion plan path relative to project root.",
    )
    parser.add_argument(
        "--output-manuscript",
        default="Manuscripts/generated/paper_package_draft.md",
        help="Structured manuscript path relative to project root.",
    )
    parser.add_argument(
        "--output-supervisor-context",
        default="Results/json/paper_supervisor_context.json",
        help="LLM Supervisor context bundle path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def resolve_source_draft(project_root: Path, args: argparse.Namespace, quality_report: dict) -> Path | None:
    explicit = resolve_path(project_root, args.source_draft)
    if explicit is not None:
        return explicit
    draft_value = quality_report.get("draft_path")
    if not draft_value:
        return None
    return resolve_path(project_root, str(draft_value))


def load_source_manifest(project_root: Path, value: str | None) -> tuple[Path | None, dict | None]:
    path = resolve_path(project_root, value)
    if path is None:
        return None, None
    if not path.exists():
        raise FileNotFoundError(f"PDF export manifest not found: {value}")
    return path, json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    quality_report_path = resolve_path(project_root, args.quality_report)
    if quality_report_path is None or not quality_report_path.exists():
        raise FileNotFoundError(f"Paper quality report not found: {args.quality_report}")

    quality_report = json.loads(quality_report_path.read_text(encoding="utf-8"))
    output_plan = resolve_path(project_root, args.output_plan)
    output_manuscript = resolve_path(project_root, args.output_manuscript)
    output_supervisor_context = resolve_path(project_root, args.output_supervisor_context)
    if output_plan is None or output_manuscript is None or output_supervisor_context is None:
        raise ValueError("Output paths are required.")

    source_manifest_path, source_manifest = load_source_manifest(project_root, args.source_manifest)
    plan = build_paper_expansion_plan(
        project_root,
        quality_report,
        source_manifest=source_manifest,
        source_manifest_path=source_manifest_path,
    )
    plan_path = write_paper_expansion_plan(project_root, plan, output_plan)
    source_draft = resolve_source_draft(project_root, args, quality_report)
    manuscript = build_structured_manuscript(project_root, plan, source_draft)
    manuscript_path = write_structured_manuscript(output_manuscript, manuscript)
    supervisor_context = build_supervisor_context_bundle(
        project_root,
        quality_report,
        plan,
        plan_path,
        manuscript_path,
    )
    supervisor_context_path = write_supervisor_context_bundle(output_supervisor_context, supervisor_context)

    print(f"[econ-workbench] paper_expansion_plan={plan_path.relative_to(project_root)}")
    print(f"[econ-workbench] paper_package_draft={manuscript_path.relative_to(project_root)}")
    print(f"[econ-workbench] paper_supervisor_context={supervisor_context_path.relative_to(project_root)}")
    print(f"[econ-workbench] agent_tasks={len(plan.get('agent_task_queue', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

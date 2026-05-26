from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.paper_revision_gate_recompute import (
    build_revision_gate_recompute,
    snapshot_formal_state,
    write_revision_gate_recompute_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify revision evidence packets against current quality gates.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--evidence-manifest",
        default="Results/json/paper_revision_evidence_packets.json",
        help="Evidence packet manifest path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/paper_revision_gate_recompute.json",
        help="Output gate recompute JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/paper_revision_gate_recompute.md",
        help="Output gate recompute review Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    evidence_manifest_path = resolve_path(project_root, args.evidence_manifest)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)

    if not evidence_manifest_path.exists():
        raise FileNotFoundError(f"Paper revision evidence manifest not found: {args.evidence_manifest}")

    formal_state_before = snapshot_formal_state(project_root)
    evidence_manifest = json.loads(evidence_manifest_path.read_text(encoding="utf-8"))
    report = build_revision_gate_recompute(
        project_root,
        evidence_manifest,
        evidence_manifest_path,
        formal_state_before=formal_state_before,
    )
    report_path, review_path = write_revision_gate_recompute_outputs(
        output_report_path,
        output_review_path,
        report,
    )

    status_counts = report.get("status_counts", {})
    print(f"[econ-workbench] paper_revision_gate_recompute={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] gate_recompute_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] task_results={len(report.get('task_results', []))}")
    print(f"[econ-workbench] cleared={status_counts.get('cleared', 0)}")
    print(f"[econ-workbench] still_blocking={status_counts.get('still_blocking', 0)}")
    print(f"[econ-workbench] manual_review_required={status_counts.get('manual_review_required', 0)}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report.get('formal_writeback_allowed')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

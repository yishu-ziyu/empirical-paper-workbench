from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.formal_writeback_preflight import (
    build_formal_writeback_preflight,
    snapshot_formal_state,
    write_formal_writeback_preflight_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the formal writeback preflight ledger and preview.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--gate-recompute",
        default="Results/json/paper_revision_gate_recompute.json",
        help="Gate recompute ledger path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/formal_writeback_preflight.json",
        help="Output preflight JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/formal_writeback_preflight.md",
        help="Output preflight review Markdown path relative to project root.",
    )
    parser.add_argument(
        "--output-preview",
        default="Manuscripts/generated/previews/formal_writeback_preflight.md",
        help="Output draft-layer writeback preview Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    gate_path = resolve_path(project_root, args.gate_recompute)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    output_preview_path = resolve_path(project_root, args.output_preview)

    if not gate_path.exists():
        raise FileNotFoundError(f"Paper revision gate recompute ledger not found: {args.gate_recompute}")

    formal_state_before = snapshot_formal_state(project_root)
    gate_recompute = json.loads(gate_path.read_text(encoding="utf-8"))
    report = build_formal_writeback_preflight(
        project_root,
        gate_recompute,
        gate_path,
        output_preview_path,
        formal_state_before=formal_state_before,
    )
    report_path, review_path, preview_path = write_formal_writeback_preflight_outputs(
        output_report_path,
        output_review_path,
        output_preview_path,
        report,
    )

    print(f"[econ-workbench] formal_writeback_preflight={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_writeback_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_writeback_preview={preview_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] writeback_scope={len(report.get('writeback_scope', []))}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report.get('formal_writeback_allowed')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

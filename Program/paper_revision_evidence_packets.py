from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.paper_revision_evidence_packets import (
    build_revision_evidence_packets,
    snapshot_formal_state,
    write_revision_evidence_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build draft-layer evidence packets from a paper revision round.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--revision-round",
        default="Results/json/paper_revision_round.json",
        help="Revision round JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-manifest",
        default="Results/json/paper_revision_evidence_packets.json",
        help="Output evidence manifest JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/paper_revision_evidence_packets.md",
        help="Output evidence review Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    revision_round_path = resolve_path(project_root, args.revision_round)
    output_manifest_path = resolve_path(project_root, args.output_manifest)
    output_review_path = resolve_path(project_root, args.output_review)

    if not revision_round_path.exists():
        raise FileNotFoundError(f"Paper revision round not found: {args.revision_round}")

    formal_state_before = snapshot_formal_state(project_root)
    revision_round = json.loads(revision_round_path.read_text(encoding="utf-8"))
    manifest = build_revision_evidence_packets(
        project_root,
        revision_round,
        revision_round_path,
        formal_state_before=formal_state_before,
    )
    manifest_path, review_path = write_revision_evidence_outputs(
        project_root,
        output_manifest_path,
        output_review_path,
        manifest,
    )

    print(f"[econ-workbench] paper_revision_evidence_packets={manifest_path.relative_to(project_root)}")
    print(f"[econ-workbench] revision_evidence_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] task_results={len(manifest.get('task_results', []))}")
    print(f"[econ-workbench] evidence_packet_ready={manifest.get('status_counts', {}).get('evidence_packet_ready', 0)}")
    print(f"[econ-workbench] needs_manual_review={manifest.get('status_counts', {}).get('needs_manual_review', 0)}")
    print(f"[econ-workbench] formal_writeback_allowed={str(manifest.get('formal_writeback_allowed')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

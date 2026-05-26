from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_evidence_materializer import (
    DEFAULT_EVIDENCE_IDS,
    DEFAULT_PROPOSAL_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_formal_evidence_materialization,
    snapshot_formal_state,
    write_formal_evidence_materialization_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize high-confidence formal package evidence files.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--proposal",
        default=DEFAULT_PROPOSAL_PATH,
        help="Evidence registry patch proposal path relative to project root.",
    )
    parser.add_argument(
        "--evidence-ids",
        default=",".join(DEFAULT_EVIDENCE_IDS),
        help="Comma-separated evidence ids to materialize.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_REPORT_PATH,
        help="Output materialization JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_REVIEW_PATH,
        help="Output materialization Markdown review path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    proposal_path = resolve_path(project_root, args.proposal)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    evidence_ids = [args.evidence_ids]

    formal_state_before = snapshot_formal_state(project_root)
    report = build_formal_evidence_materialization(
        project_root,
        proposal_path,
        evidence_ids,
        output_report_path=output_report_path,
        formal_state_before=formal_state_before,
    )
    report_path, review_path = write_formal_evidence_materialization_outputs(
        output_report_path,
        output_review_path,
        report,
    )

    print(f"[econ-workbench] formal_evidence_materialization={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_evidence_materialization_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] materialized={len(report.get('materialized') or [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

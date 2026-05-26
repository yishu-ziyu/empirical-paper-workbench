from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_evidence_registry_resolver import (
    DEFAULT_PREFLIGHT_REPORT,
    DEFAULT_PROPOSAL_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_formal_evidence_registry_resolution,
    snapshot_formal_state,
    write_formal_evidence_registry_resolution_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve P5 formal evidence registry gaps from local artifacts.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--preflight-report",
        default=DEFAULT_PREFLIGHT_REPORT,
        help="P5-D formal PDF export preflight report path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_REPORT_PATH,
        help="Output formal evidence registry resolution JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_REVIEW_PATH,
        help="Output formal evidence registry resolution Markdown path relative to project root.",
    )
    parser.add_argument(
        "--output-proposal",
        default=DEFAULT_PROPOSAL_PATH,
        help="Output evidence registry patch proposal JSON path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    preflight_report_path = resolve_path(project_root, args.preflight_report)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    output_proposal_path = resolve_path(project_root, args.output_proposal)

    formal_state_before = snapshot_formal_state(project_root)
    report = build_formal_evidence_registry_resolution(
        project_root,
        preflight_report_path,
        output_report_path=output_report_path,
        formal_state_before=formal_state_before,
    )
    report_path, review_path, proposal_path = write_formal_evidence_registry_resolution_outputs(
        output_report_path,
        output_review_path,
        output_proposal_path,
        report,
    )

    print(f"[econ-workbench] formal_evidence_registry_resolution={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_evidence_registry_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] evidence_registry_patch_proposal={proposal_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] patch_items={report.get('patch_summary', {}).get('total', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

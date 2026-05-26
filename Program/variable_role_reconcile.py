from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from workbench.variable_role_reconcile import (  # noqa: E402
    build_variable_role_reconciliation,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a review-gated variable role reconciliation proposal.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--output-proposal",
        default="state/proposals/variable_role_reconciliation.json",
        help="Proposal JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/variable_role_reconciliation_report.json",
        help="Report JSON path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def fail(code: str, message: str) -> int:
    print(json.dumps({"error": {"code": code, "message": message}}, ensure_ascii=False), file=sys.stderr)
    return 1


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    output_proposal = resolve_path(project_root, args.output_proposal)
    output_report = resolve_path(project_root, args.output_report)

    try:
        proposal, report = build_variable_role_reconciliation(project_root)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return fail("variable_role_reconciliation_failed", str(exc))

    proposal_path = write_json(output_proposal, proposal)
    report_path = write_json(output_report, report)
    print(f"[econ-workbench] variable_role_reconciliation={proposal_path.relative_to(project_root)}")
    print(f"[econ-workbench] variable_role_reconciliation_report={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={proposal.get('status')}")
    print(f"[econ-workbench] conflicts={len(proposal.get('detected_conflicts', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.formal_writeback_approval import (
    DEFAULT_APPROVAL_PATH,
    VALID_ACTIONS,
    build_formal_writeback_approval,
    snapshot_formal_state,
    write_formal_writeback_approval_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record human approval for entering P5 formal paper package.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--preflight",
        default="Results/json/formal_writeback_preflight.json",
        help="Formal writeback preflight JSON path relative to project root.",
    )
    parser.add_argument(
        "--action",
        choices=sorted(VALID_ACTIONS),
        required=True,
        help="Human decision for the formal package entry gate.",
    )
    parser.add_argument("--note", default="", help="Human review note.")
    parser.add_argument("--actor", default="user", help="Approval actor name.")
    parser.add_argument(
        "--approval-state",
        default=DEFAULT_APPROVAL_PATH,
        help="Writeback approval state path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/formal_writeback_approval.json",
        help="Output approval JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default="Reviews/formal_writeback_approval.md",
        help="Output approval review Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    preflight_path = resolve_path(project_root, args.preflight)
    approval_path = resolve_path(project_root, args.approval_state)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)

    if not preflight_path.exists():
        raise FileNotFoundError(f"Formal writeback preflight not found: {args.preflight}")

    formal_state_before = snapshot_formal_state(project_root)
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    report = build_formal_writeback_approval(
        project_root,
        preflight,
        preflight_path,
        action=args.action,
        note=args.note,
        actor=args.actor,
        approval_path=approval_path,
        formal_state_before=formal_state_before,
    )
    report_path, review_path = write_formal_writeback_approval_outputs(
        output_report_path,
        output_review_path,
        report,
    )

    print(f"[econ-workbench] formal_writeback_approval={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_writeback_approval_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] approval_state={approval_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] can_enter_p5={str(report.get('can_enter_p5')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from pathlib import Path

from workbench.formal_pdf_final_approval import (
    DEFAULT_APPROVAL_PATH,
    DEFAULT_APPROVAL_REPORT,
    DEFAULT_APPROVAL_REVIEW,
    DEFAULT_FINAL_PREFLIGHT,
    VALID_ACTIONS,
    build_formal_pdf_final_approval,
    snapshot_formal_state,
    write_formal_pdf_final_approval_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record human final approval for a formal PDF candidate.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--final-preflight",
        default=DEFAULT_FINAL_PREFLIGHT,
        help="Final writeback preflight JSON path relative to project root.",
    )
    parser.add_argument(
        "--action",
        choices=sorted(VALID_ACTIONS),
        required=True,
        help="Human decision for the final PDF/docx writeback gate.",
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
        default=DEFAULT_APPROVAL_REPORT,
        help="Output final approval JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_APPROVAL_REVIEW,
        help="Output final approval Markdown path relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    final_preflight_path = resolve_path(project_root, args.final_preflight)
    approval_path = resolve_path(project_root, args.approval_state)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)

    if not final_preflight_path.exists():
        raise FileNotFoundError(f"Final PDF writeback preflight not found: {args.final_preflight}")

    final_preflight = json.loads(final_preflight_path.read_text(encoding="utf-8"))
    report, exit_code = build_formal_pdf_final_approval(
        project_root,
        final_preflight,
        final_preflight_path,
        action=args.action,
        note=args.note,
        actor=args.actor,
        approval_path=approval_path,
        formal_state_before=snapshot_formal_state(project_root),
    )
    report_path, review_path = write_formal_pdf_final_approval_outputs(
        output_report_path,
        output_review_path,
        report,
    )

    print(f"[econ-workbench] formal_pdf_final_approval={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_pdf_final_approval_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] approval_state={approval_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] can_enter_p6={str(report.get('can_enter_p6')).lower()}")
    print(f"[econ-workbench] final_writeback_authorized={str(report.get('final_writeback_authorized')).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

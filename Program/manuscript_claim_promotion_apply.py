from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from workbench.manuscript_claim_promotion_apply import (  # noqa: E402
    build_manuscript_claim_promotion_apply,
    write_manuscript_claim_promotion_apply_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply an approved claim promotion patch to approved_findings.json."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--patch-report", default="Results/json/manuscript_claim_promotion_patch.json")
    parser.add_argument("--output-report", default="Results/json/manuscript_claim_promotion_apply.json")
    parser.add_argument("--output-review", default="Reviews/manuscript_claim_promotion_apply.md")
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--confirm-apply", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    report, exit_code = build_manuscript_claim_promotion_apply(
        project_root,
        patch_report_path=project_root / args.patch_report,
        reviewer=args.reviewer,
        note=args.note,
        confirm_apply=args.confirm_apply,
    )
    report_path, review_path = write_manuscript_claim_promotion_apply_outputs(
        project_root / args.output_report,
        project_root / args.output_review,
        report,
    )
    print(f"manuscript_claim_promotion_apply={report_path}")
    print(f"manuscript_claim_promotion_apply_md={review_path}")
    print(f"status={report['status']}")
    print(f"applied={str(report['applied']).lower()}")
    print(f"formal_writeback_allowed={str(report['formal_writeback_allowed']).lower()}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

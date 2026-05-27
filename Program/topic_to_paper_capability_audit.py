from __future__ import annotations

import argparse
from pathlib import Path

from workbench.topic_to_paper_capability_audit import (
    DEFAULT_OUTPUT_REPORT,
    DEFAULT_OUTPUT_REVIEW,
    build_topic_to_paper_capability_audit,
    write_topic_to_paper_capability_audit_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit whether a research topic can be reproduced into a paper package.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument("--topic", required=True, help="Research topic to audit against the current workbench state.")
    parser.add_argument("--output-report", default=DEFAULT_OUTPUT_REPORT)
    parser.add_argument("--output-review", default=DEFAULT_OUTPUT_REVIEW)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    report, exit_code = build_topic_to_paper_capability_audit(project_root, args.topic)
    report_path, review_path = write_topic_to_paper_capability_audit_outputs(
        project_root / args.output_report,
        project_root / args.output_review,
        report,
    )
    print(f"[econ-workbench] topic_to_paper_capability_audit={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] topic_to_paper_capability_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] current_topic_reproducibility={report.get('current_topic_reproducibility')}")
    print(f"[econ-workbench] general_topic_automation={report.get('general_topic_automation')}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

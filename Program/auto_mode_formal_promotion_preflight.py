from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_promotion_preflight import (  # noqa: E402
    DEFAULT_DECISION_PATH,
    DEFAULT_PACKAGE_MANIFEST_PATH,
    DEFAULT_PACKET_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_promotion_preflight,
    load_json_or_empty,
    write_auto_mode_formal_promotion_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Auto Mode formal promotion preflight without writeback.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--final-review-decision", default=str(DEFAULT_DECISION_PATH))
    parser.add_argument("--final-review-packet", default=str(DEFAULT_PACKET_PATH))
    parser.add_argument("--package-manifest", default=str(DEFAULT_PACKAGE_MANIFEST_PATH))
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    decision = load_json_or_empty(project_root / args.final_review_decision)
    packet = load_json_or_empty(project_root / args.final_review_packet)
    package_manifest = load_json_or_empty(project_root / args.package_manifest)
    report = build_auto_mode_formal_promotion_preflight(
        decision,
        packet,
        package_manifest,
        source_paths={
            "final_review_decision": str(Path(args.final_review_decision)),
            "final_review_packet": str(Path(args.final_review_packet)),
            "package_manifest": str(Path(args.package_manifest)),
        },
    )
    report_path, review_path = write_auto_mode_formal_promotion_preflight_outputs(
        project_root,
        report,
        Path(args.output_report),
        Path(args.output_review),
    )
    print(f"[econ-workbench] auto_mode_formal_promotion_preflight={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_formal_promotion_preflight_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] can_request_formal_writeback_approval={str(report['can_request_formal_writeback_approval']).lower()}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report['formal_writeback_allowed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

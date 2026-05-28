from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_writeback_execution_preflight import (  # noqa: E402
    DEFAULT_APPROVAL_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_writeback_execution_preflight,
    load_json_or_empty,
    write_auto_mode_formal_writeback_execution_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Auto Mode formal writeback execution preflight without executing writeback.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--formal-writeback-approval", default=str(DEFAULT_APPROVAL_PATH))
    parser.add_argument("--output-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    approval = load_json_or_empty(project_root / args.formal_writeback_approval)
    report = build_auto_mode_formal_writeback_execution_preflight(
        approval,
        source_paths={
            "formal_writeback_approval": str(Path(args.formal_writeback_approval)),
        },
    )
    report_path, review_path = write_auto_mode_formal_writeback_execution_preflight_outputs(
        project_root,
        report,
        Path(args.output_preflight),
        Path(args.output_review),
    )
    print(f"[econ-workbench] auto_mode_formal_writeback_execution_preflight={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_formal_writeback_execution_preflight_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] can_request_formal_writeback_execution={str(report['can_request_formal_writeback_execution']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

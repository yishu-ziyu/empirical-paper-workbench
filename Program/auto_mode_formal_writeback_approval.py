from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_writeback_approval import (  # noqa: E402
    DEFAULT_APPROVAL_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_DECISIONS,
    build_auto_mode_formal_writeback_approval,
    load_json_or_empty,
    write_auto_mode_formal_writeback_approval_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Auto Mode formal writeback approval without executing writeback.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--formal-promotion-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--decision", choices=sorted(VALID_DECISIONS), default="defer")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-approval", default=str(DEFAULT_APPROVAL_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight = load_json_or_empty(project_root / args.formal_promotion_preflight)
    report = build_auto_mode_formal_writeback_approval(
        preflight,
        decision=args.decision,
        reviewer=args.reviewer,
        note=args.note,
        source_paths={
            "formal_promotion_preflight": str(Path(args.formal_promotion_preflight)),
        },
    )
    report_path, review_path = write_auto_mode_formal_writeback_approval_outputs(
        project_root,
        report,
        Path(args.output_approval),
        Path(args.output_review),
    )
    print(f"[econ-workbench] auto_mode_formal_writeback_approval={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_formal_writeback_approval_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] approved={str(report['approved']).lower()}")
    print(f"[econ-workbench] formal_writeback_allowed={str(report['formal_writeback_allowed']).lower()}")
    print(
        "[econ-workbench] can_enter_formal_writeback_execution_preflight="
        f"{str(report['can_enter_formal_writeback_execution_preflight']).lower()}"
    )
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_approval import (  # noqa: E402
    DEFAULT_APPROVAL_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_DECISIONS,
    build_auto_mode_formal_target_adapter_candidate_promotion_approval,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_candidate_promotion_approval_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Auto Mode formal target adapter candidate promotion approval gate.",
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-promotion-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--decision", default="defer", choices=sorted(VALID_DECISIONS))
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-approval", default=str(DEFAULT_APPROVAL_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight = load_json_or_empty(project_root / args.candidate_promotion_preflight)
    report = build_auto_mode_formal_target_adapter_candidate_promotion_approval(
        preflight,
        decision=args.decision,
        reviewer=args.reviewer,
        note=args.note,
        source_paths={
            "candidate_promotion_preflight": str(Path(args.candidate_promotion_preflight)),
        },
    )
    report_path, review_path = write_auto_mode_formal_target_adapter_candidate_promotion_approval_outputs(
        project_root,
        report,
        Path(args.output_approval),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_candidate_promotion_approval={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_candidate_promotion_approval_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] approved={str(report['approved']).lower()}")
    print(
        "[econ-workbench] "
        f"verified_candidate_promotion_allowed={str(report['verified_candidate_promotion_allowed']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"can_enter_verified_candidate_promotion_execution_preflight="
        f"{str(report['can_enter_verified_candidate_promotion_execution_preflight']).lower()}"
    )
    print(f"[econ-workbench] approved_promotion_plan={len(report['approved_promotion_plan'])}")
    print(f"[econ-workbench] candidate_targets_promoted={str(report['candidate_targets_promoted']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

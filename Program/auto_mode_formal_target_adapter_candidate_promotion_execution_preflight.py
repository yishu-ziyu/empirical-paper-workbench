from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_execution_preflight import (  # noqa: E402
    DEFAULT_APPROVAL_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Auto Mode verified candidate promotion execution preflight without promoting candidates.",
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-promotion-approval", default=str(DEFAULT_APPROVAL_PATH))
    parser.add_argument("--output-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    approval = load_json_or_empty(project_root / args.candidate_promotion_approval)
    report = build_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight(
        approval,
        source_paths={
            "candidate_promotion_approval": str(Path(args.candidate_promotion_approval)),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight_outputs(
            project_root,
            report,
            Path(args.output_preflight),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_candidate_promotion_execution_preflight="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_candidate_promotion_execution_preflight_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(
        "[econ-workbench] "
        f"can_request_verified_candidate_promotion_execution="
        f"{str(report['can_request_verified_candidate_promotion_execution']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"requires_explicit_promotion_execute_command="
        f"{str(report['requires_explicit_promotion_execute_command']).lower()}"
    )
    print(f"[econ-workbench] promotion_execution_plan={len(report['promotion_execution_plan'])}")
    print(f"[econ-workbench] candidate_targets_promoted={str(report['candidate_targets_promoted']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

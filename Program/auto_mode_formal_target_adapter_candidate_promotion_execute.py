from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_execute import (  # noqa: E402
    DEFAULT_EXECUTE_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_PROMOTION_MANIFEST_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    build_auto_mode_formal_target_adapter_candidate_promotion_execute,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_candidate_promotion_execute_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or execute Auto Mode verified candidate promotion.",
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--promotion-execution-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--mode", default="dry-run", choices=sorted(VALID_MODES))
    parser.add_argument("--confirm-promote", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--promotion-manifest", default=str(DEFAULT_PROMOTION_MANIFEST_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight = load_json_or_empty(project_root / args.promotion_execution_preflight)
    report = build_auto_mode_formal_target_adapter_candidate_promotion_execute(
        project_root,
        preflight,
        mode=args.mode,
        confirm_promote=args.confirm_promote,
        reviewer=args.reviewer,
        note=args.note,
        promotion_manifest_path=Path(args.promotion_manifest),
        source_paths={
            "promotion_execution_preflight": str(Path(args.promotion_execution_preflight)),
        },
    )
    report_path, review_path, manifest_path = write_auto_mode_formal_target_adapter_candidate_promotion_execute_outputs(
        project_root,
        report,
        Path(args.output_execute),
        Path(args.output_review),
        Path(args.promotion_manifest),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_candidate_promotion_execute={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_candidate_promotion_execute_review={review_path.relative_to(project_root)}"
    )
    if manifest_path is not None:
        print(
            "[econ-workbench] "
            f"auto_mode_formal_target_adapter_candidate_promotion_manifest={manifest_path.relative_to(project_root)}"
        )
    print(f"[econ-workbench] status={report['status']}")
    print(
        "[econ-workbench] "
        f"can_promote_with_confirmation={str(report['can_promote_with_confirmation']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"promotion_manifest_recorded={str(report['promotion_manifest_recorded']).lower()}"
    )
    print(f"[econ-workbench] promotion_operations={len(report['promotion_operations'])}")
    print(f"[econ-workbench] candidate_targets_promoted={str(report['candidate_targets_promoted']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

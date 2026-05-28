from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_promoted_package_verification import (  # noqa: E402
    DEFAULT_EXECUTE_PATH,
    DEFAULT_PROMOTION_MANIFEST_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_VERIFICATION_PATH,
    build_auto_mode_formal_target_adapter_promoted_package_verification,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_promoted_package_verification_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Auto Mode promoted formal package targets without writing product state.",
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--candidate-promotion-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--promotion-manifest", default=str(DEFAULT_PROMOTION_MANIFEST_PATH))
    parser.add_argument("--output-verification", default=str(DEFAULT_VERIFICATION_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    candidate_promotion_execute = load_json_or_empty(project_root / args.candidate_promotion_execute)
    promotion_manifest = load_json_or_empty(project_root / args.promotion_manifest)
    report = build_auto_mode_formal_target_adapter_promoted_package_verification(
        project_root,
        candidate_promotion_execute,
        promotion_manifest,
        source_paths={
            "candidate_promotion_execute": str(Path(args.candidate_promotion_execute)),
            "promotion_manifest": str(Path(args.promotion_manifest)),
        },
    )
    report_path, review_path = write_auto_mode_formal_target_adapter_promoted_package_verification_outputs(
        project_root,
        report,
        Path(args.output_verification),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_promoted_package_verification={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_promoted_package_verification_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] formal_package_verified={str(report['formal_package_verified']).lower()}")
    print(
        "[econ-workbench] "
        f"promoted_formal_targets_verified={str(report['promoted_formal_targets_verified']).lower()}"
    )
    print(f"[econ-workbench] formal_target_verification_records={len(report['formal_target_verification_records'])}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

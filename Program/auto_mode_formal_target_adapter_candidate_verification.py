from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_candidate_verification import (  # noqa: E402
    DEFAULT_EXECUTE_PATH,
    DEFAULT_MATERIALIZATION_MANIFEST_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_VERIFICATION_PATH,
    build_auto_mode_formal_target_adapter_candidate_verification,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_candidate_verification_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Auto Mode formal target adapter candidate verification.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--materialization-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--materialization-manifest", default=str(DEFAULT_MATERIALIZATION_MANIFEST_PATH))
    parser.add_argument("--output-verification", default=str(DEFAULT_VERIFICATION_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    execute_report = load_json_or_empty(project_root / args.materialization_execute)
    materialization_manifest = load_json_or_empty(project_root / args.materialization_manifest)
    report = build_auto_mode_formal_target_adapter_candidate_verification(
        project_root,
        execute_report,
        materialization_manifest,
        source_paths={
            "materialization_execute": str(Path(args.materialization_execute)),
            "materialization_manifest": str(Path(args.materialization_manifest)),
        },
    )
    report_path, review_path = write_auto_mode_formal_target_adapter_candidate_verification_outputs(
        project_root,
        report,
        Path(args.output_verification),
        Path(args.output_review),
    )
    print(f"[econ-workbench] auto_mode_formal_target_adapter_candidate_verification={report_path.relative_to(project_root)}")
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_candidate_verification_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] candidate_targets_verified={str(report['candidate_targets_verified']).lower()}")
    print(f"[econ-workbench] target_verification_records={len(report['target_verification_records'])}")
    print(f"[econ-workbench] formal_target_adapters_executed={str(report['formal_target_adapters_executed']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

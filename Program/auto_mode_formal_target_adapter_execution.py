from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_execution import (  # noqa: E402
    DEFAULT_EXECUTION_MANIFEST_PATH,
    DEFAULT_EXECUTION_PATH,
    DEFAULT_READINESS_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    build_auto_mode_formal_target_adapter_execution,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_execution_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Auto Mode formal target adapter execution gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--target-adapter-readiness", default=str(DEFAULT_READINESS_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-execution", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execution", default=str(DEFAULT_EXECUTION_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--execution-manifest", default=str(DEFAULT_EXECUTION_MANIFEST_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    readiness = load_json_or_empty(project_root / args.target_adapter_readiness)
    report = build_auto_mode_formal_target_adapter_execution(
        readiness,
        mode=args.mode,
        confirm_execution=args.confirm_execution,
        reviewer=args.reviewer,
        note=args.note,
        execution_manifest_path=Path(args.execution_manifest),
        source_paths={
            "target_adapter_readiness": str(Path(args.target_adapter_readiness)),
        },
    )
    report_path, review_path, manifest_path = write_auto_mode_formal_target_adapter_execution_outputs(
        project_root,
        report,
        Path(args.output_execution),
        Path(args.output_review),
        Path(args.execution_manifest),
    )
    print(f"[econ-workbench] auto_mode_formal_target_adapter_execution={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_formal_target_adapter_execution_review={review_path.relative_to(project_root)}")
    if manifest_path is not None:
        print(f"[econ-workbench] auto_mode_formal_target_adapter_execution_manifest={manifest_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] adapter_execution_plan={len(report['adapter_execution_plan'])}")
    print(f"[econ-workbench] execution_manifest_recorded={str(report['execution_manifest_recorded']).lower()}")
    print(f"[econ-workbench] formal_target_adapters_executed={str(report['formal_target_adapters_executed']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

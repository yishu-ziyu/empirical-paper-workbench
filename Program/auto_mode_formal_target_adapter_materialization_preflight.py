from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_materialization_preflight import (  # noqa: E402
    DEFAULT_EXECUTION_MANIFEST_PATH,
    DEFAULT_EXECUTION_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_target_adapter_materialization_preflight,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_materialization_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Auto Mode formal target adapter materialization preflight.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--target-adapter-execution", default=str(DEFAULT_EXECUTION_PATH))
    parser.add_argument("--execution-manifest", default=str(DEFAULT_EXECUTION_MANIFEST_PATH))
    parser.add_argument("--output-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    execution = load_json_or_empty(project_root / args.target_adapter_execution)
    execution_manifest = load_json_or_empty(project_root / args.execution_manifest)
    report = build_auto_mode_formal_target_adapter_materialization_preflight(
        execution,
        execution_manifest,
        source_paths={
            "target_adapter_execution": str(Path(args.target_adapter_execution)),
            "execution_manifest": str(Path(args.execution_manifest)),
        },
    )
    report_path, review_path = write_auto_mode_formal_target_adapter_materialization_preflight_outputs(
        project_root,
        report,
        Path(args.output_preflight),
        Path(args.output_review),
    )
    print(f"[econ-workbench] auto_mode_formal_target_adapter_materialization_preflight={report_path.relative_to(project_root)}")
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_materialization_preflight_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] materialization_plan={len(report['materialization_plan'])}")
    print(f"[econ-workbench] can_request_adapter_materialization={str(report['can_request_adapter_materialization']).lower()}")
    print(f"[econ-workbench] requires_explicit_materialize_command={str(report['requires_explicit_materialize_command']).lower()}")
    print(f"[econ-workbench] candidate_targets_materialized={str(report['candidate_targets_materialized']).lower()}")
    print(f"[econ-workbench] formal_target_adapters_executed={str(report['formal_target_adapters_executed']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

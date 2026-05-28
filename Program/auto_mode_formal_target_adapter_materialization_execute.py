from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_materialization_execute import (  # noqa: E402
    DEFAULT_EXECUTE_PATH,
    DEFAULT_MATERIALIZATION_MANIFEST_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    build_auto_mode_formal_target_adapter_materialization_execute,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_materialization_execute_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Auto Mode formal target adapter materialization execute gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--materialization-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-materialize", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--materialization-manifest", default=str(DEFAULT_MATERIALIZATION_MANIFEST_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight = load_json_or_empty(project_root / args.materialization_preflight)
    report = build_auto_mode_formal_target_adapter_materialization_execute(
        project_root,
        preflight,
        mode=args.mode,
        confirm_materialize=args.confirm_materialize,
        reviewer=args.reviewer,
        note=args.note,
        materialization_manifest_path=Path(args.materialization_manifest),
        source_paths={
            "materialization_preflight": str(Path(args.materialization_preflight)),
        },
    )
    report_path, review_path, manifest_path = write_auto_mode_formal_target_adapter_materialization_execute_outputs(
        project_root,
        report,
        Path(args.output_execute),
        Path(args.output_review),
        Path(args.materialization_manifest),
    )
    print(f"[econ-workbench] auto_mode_formal_target_adapter_materialization_execute={report_path.relative_to(project_root)}")
    print(
        "[econ-workbench] "
        f"auto_mode_formal_target_adapter_materialization_execute_review={review_path.relative_to(project_root)}"
    )
    if manifest_path is not None:
        print(
            "[econ-workbench] "
            f"auto_mode_formal_target_adapter_materialization_manifest={manifest_path.relative_to(project_root)}"
        )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] materialization_operations={len(report['materialization_operations'])}")
    print(f"[econ-workbench] can_materialize_with_confirmation={str(report['can_materialize_with_confirmation']).lower()}")
    print(f"[econ-workbench] materialization_manifest_recorded={str(report['materialization_manifest_recorded']).lower()}")
    print(f"[econ-workbench] candidate_targets_materialized={str(report['candidate_targets_materialized']).lower()}")
    print(f"[econ-workbench] formal_target_adapters_executed={str(report['formal_target_adapters_executed']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_writeback_execute import (  # noqa: E402
    DEFAULT_APPLY_MANIFEST_PATH,
    DEFAULT_EXECUTE_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    build_auto_mode_formal_writeback_execute,
    load_json_or_empty,
    write_auto_mode_formal_writeback_execute_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Auto Mode formal writeback execute dry-run or apply-manifest recording.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--execution-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-apply", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--apply-manifest", default=str(DEFAULT_APPLY_MANIFEST_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight = load_json_or_empty(project_root / args.execution_preflight)
    report = build_auto_mode_formal_writeback_execute(
        preflight,
        mode=args.mode,
        confirm_apply=args.confirm_apply,
        reviewer=args.reviewer,
        note=args.note,
        apply_manifest_path=Path(args.apply_manifest),
        source_paths={
            "formal_writeback_execution_preflight": str(Path(args.execution_preflight)),
        },
    )
    report_path, review_path, manifest_path = write_auto_mode_formal_writeback_execute_outputs(
        project_root,
        report,
        Path(args.output_execute),
        Path(args.output_review),
        Path(args.apply_manifest),
    )
    print(f"[econ-workbench] auto_mode_formal_writeback_execute={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_formal_writeback_execute_review={review_path.relative_to(project_root)}")
    if manifest_path is not None:
        print(f"[econ-workbench] auto_mode_formal_writeback_apply_manifest={manifest_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] apply_manifest_recorded={str(report['apply_manifest_recorded']).lower()}")
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

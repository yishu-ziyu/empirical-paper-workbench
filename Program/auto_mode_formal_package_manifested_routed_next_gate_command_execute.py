from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_manifested_routed_next_gate_command_execute import (  # noqa: E402
    DEFAULT_EXECUTE_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    load_json_or_empty,
    run_auto_mode_formal_package_manifested_routed_next_gate_command_execute,
    write_auto_mode_formal_package_manifested_routed_next_gate_command_execute_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a manifested routed next-gate command execute gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifested-routed-next-gate-command-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-command-execute", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight_path = Path(args.manifested_routed_next_gate_command_preflight)
    preflight = load_json_or_empty(project_root / preflight_path)
    report, _exit_code = run_auto_mode_formal_package_manifested_routed_next_gate_command_execute(
        project_root,
        preflight,
        mode=args.mode,
        confirm_command_execute=args.confirm_command_execute,
        reviewer=args.reviewer,
        note=args.note,
        source_paths={
            "manifested_routed_next_gate_command_preflight": str(preflight_path),
        },
        repo_root=REPO_ROOT,
    )
    report_path, review_path = write_auto_mode_formal_package_manifested_routed_next_gate_command_execute_outputs(
        project_root,
        report,
        Path(args.output_execute),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_manifested_routed_next_gate_command_execute="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_manifested_routed_next_gate_command_execute_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "can_execute_manifested_next_gate_command_with_confirmation="
        f"{str(report['can_execute_manifested_next_gate_command_with_confirmation']).lower()}"
    )
    print(f"[econ-workbench] delegated_command={len(report['delegated_command'])}")
    print(f"[econ-workbench] next_gate_command_executed={str(report['next_gate_command_executed']).lower()}")
    print(
        "[econ-workbench] "
        f"this_command_ran_next_gate_command={str(report['this_command_ran_next_gate_command']).lower()}"
    )
    print(f"[econ-workbench] delegated_status={report['delegated_status']}")
    print(f"[econ-workbench] next_gate_entered={str(report['next_gate_entered']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

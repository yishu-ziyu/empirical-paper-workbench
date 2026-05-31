from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry import (  # noqa: E402
    DEFAULT_GATE_ENTRY_PATH,
    DEFAULT_GATE_ENTRY_REVIEW_PATH,
    DEFAULT_MANIFESTED_COMMAND_EXECUTE_PATH,
    DEFAULT_MANIFESTED_COMMAND_EXECUTE_REVIEW_PATH,
    DEFAULT_RUN_PREFLIGHT_PATH,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gate execution of a manifested routed next-gate command from P7-BC."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifested-routed-next-gate-run-preflight", default=str(DEFAULT_RUN_PREFLIGHT_PATH))
    parser.add_argument("--confirm-command-execute", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-gate-entry", default=str(DEFAULT_GATE_ENTRY_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_GATE_ENTRY_REVIEW_PATH))
    parser.add_argument("--manifested-command-execute-output", default=str(DEFAULT_MANIFESTED_COMMAND_EXECUTE_PATH))
    parser.add_argument(
        "--manifested-command-execute-review",
        default=str(DEFAULT_MANIFESTED_COMMAND_EXECUTE_REVIEW_PATH),
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight_path = Path(args.manifested_routed_next_gate_run_preflight)
    preflight = load_json_or_empty(project_root / preflight_path)
    report, _exit_code = run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry(
        project_root,
        preflight,
        confirm_command_execute=args.confirm_command_execute,
        reviewer=args.reviewer,
        note=args.note,
        source_paths={
            "manifested_routed_next_gate_run_preflight": str(preflight_path),
        },
        repo_root=REPO_ROOT,
        manifested_command_execute_report_path=Path(args.manifested_command_execute_output),
        manifested_command_execute_review_path=Path(args.manifested_command_execute_review),
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_outputs(
            project_root,
            report,
            Path(args.output_gate_entry),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        f"command_execute_gate_entry_executed={str(report['command_execute_gate_entry_executed']).lower()}"
    )
    print(f"[econ-workbench] manifested_command_execute_status={report['manifested_command_execute_status']}")
    print(f"[econ-workbench] delegated_command={len(report['delegated_command'])}")
    print(f"[econ-workbench] next_gate_command_executed={str(report['next_gate_command_executed']).lower()}")
    print(
        "[econ-workbench] "
        f"this_command_ran_next_gate_command={str(report['this_command_ran_next_gate_command']).lower()}"
    )
    print(f"[econ-workbench] next_gate_entered={str(report['next_gate_entered']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

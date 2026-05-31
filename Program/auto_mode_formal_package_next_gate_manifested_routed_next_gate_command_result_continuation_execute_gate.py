from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate import (  # noqa: E402
    DEFAULT_EXECUTE_PATH,
    DEFAULT_GATE_ENTRY_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a manifested routed next-gate command result continuation execute gate."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--manifested-routed-next-gate-command-result-continuation-gate-entry",
        default=str(DEFAULT_GATE_ENTRY_PATH),
    )
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-continuation-execute", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute-gate", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    gate_entry_path = Path(args.manifested_routed_next_gate_command_result_continuation_gate_entry)
    gate_entry = load_json_or_empty(project_root / gate_entry_path)
    report, _exit_code = (
        run_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate(
            project_root,
            gate_entry,
            mode=args.mode,
            confirm_continuation_execute=args.confirm_continuation_execute,
            reviewer=args.reviewer,
            note=args.note,
            source_paths={
                "manifested_routed_next_gate_command_result_continuation_gate_entry": (
                    str(gate_entry_path)
                ),
            },
            repo_root=REPO_ROOT,
        )
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate_outputs(
            project_root,
            report,
            Path(args.output_execute_gate),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_gate_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "can_execute_manifested_routed_next_gate_result_continuation_with_confirmation="
        f"{str(report['can_execute_manifested_routed_next_gate_result_continuation_with_confirmation']).lower()}"
    )
    print(
        "[econ-workbench] "
        "requires_explicit_continuation_command="
        f"{str(report['requires_explicit_continuation_command']).lower()}"
    )
    print(f"[econ-workbench] continuation_command={len(report['continuation_command'])}")
    print(f"[econ-workbench] continuation_executed={str(report['continuation_executed']).lower()}")
    print(f"[econ-workbench] this_command_ran_continuation={str(report['this_command_ran_continuation']).lower()}")
    print(f"[econ-workbench] terminal_continuation_recorded={str(report['terminal_continuation_recorded']).lower()}")
    print(
        "[econ-workbench] "
        "this_command_recorded_terminal_continuation="
        f"{str(report['this_command_recorded_terminal_continuation']).lower()}"
    )
    print(f"[econ-workbench] continuation_status={report['continuation_status']}")
    print(f"[econ-workbench] selected_route_executed={str(report['selected_route_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

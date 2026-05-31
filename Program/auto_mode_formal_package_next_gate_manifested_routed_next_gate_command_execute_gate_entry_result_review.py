from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review import (  # noqa: E402
    DEFAULT_GATE_ENTRY_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review a manifested routed next-gate command execute gate entry result."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifested-routed-next-gate-command-execute-gate-entry", default=str(DEFAULT_GATE_ENTRY_PATH))
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    gate_entry_path = Path(args.manifested_routed_next_gate_command_execute_gate_entry)
    gate_entry = load_json_or_empty(project_root / gate_entry_path)
    report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review(
        gate_entry,
        source_paths={
            "manifested_routed_next_gate_command_execute_gate_entry": str(gate_entry_path),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review_outputs(
            project_root,
            report,
            Path(args.output_result_review),
            Path(args.output_review),
        )
    )

    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_execute_gate_entry_result_review_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(f"[econ-workbench] delegated_status={report['delegated_status']}")
    print(
        "[econ-workbench] "
        "command_execute_gate_entry_result_reviewed="
        f"{str(report['command_execute_gate_entry_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_continue_after_manifested_routed_next_gate_command="
        f"{str(report['can_continue_after_manifested_routed_next_gate_command']).lower()}"
    )
    print(f"[econ-workbench] delegated_result_records={len(report['delegated_result_records'])}")
    print(f"[econ-workbench] next_gate_command_executed={str(report['next_gate_command_executed']).lower()}")
    print(
        "[econ-workbench] "
        f"this_command_ran_next_gate_command={str(report['this_command_ran_next_gate_command']).lower()}"
    )
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

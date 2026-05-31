from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review import (  # noqa: E402
    DEFAULT_EXECUTE_GATE_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review a manifested routed next-gate continuation execute result."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--manifested-routed-next-gate-command-result-continuation-execute-gate",
        default=str(DEFAULT_EXECUTE_GATE_PATH),
    )
    parser.add_argument("--selected-route-execution-preflight", default="")
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    execute_gate_path = Path(args.manifested_routed_next_gate_command_result_continuation_execute_gate)
    execute_gate = load_json_or_empty(project_root / execute_gate_path)

    selected_route_path = (
        Path(args.selected_route_execution_preflight)
        if args.selected_route_execution_preflight
        else None
    )
    if (
        selected_route_path is None
        and execute_gate.get("continuation_report_path")
        and execute_gate.get("completion_terminal") is not True
    ):
        selected_route_path = Path(execute_gate["continuation_report_path"])
    selected_route_preflight = (
        load_json_or_empty(project_root / selected_route_path) if selected_route_path else {}
    )

    report = (
        build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review(
            project_root,
            execute_gate,
            selected_route_preflight,
            source_paths={
                "manifested_routed_next_gate_command_result_continuation_execute_gate": (
                    str(execute_gate_path)
                ),
                "selected_route_execution_preflight": (
                    str(selected_route_path) if selected_route_path else ""
                ),
            },
        )
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review_outputs(
            project_root,
            report,
            Path(args.output_result_review),
            Path(args.output_review),
        )
    )

    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_review_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(f"[econ-workbench] continuation_status={report['continuation_status']}")
    print(f"[econ-workbench] selected_route_preflight_status={report['selected_route_preflight_status']}")
    print(f"[econ-workbench] terminal_status={report['terminal_status']}")
    print(
        "[econ-workbench] "
        "continuation_execute_result_reviewed="
        f"{str(report['continuation_execute_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_continue_after_manifested_routed_next_gate_result_continuation="
        f"{str(report['can_continue_after_manifested_routed_next_gate_result_continuation']).lower()}"
    )
    print(
        "[econ-workbench] "
        "selected_route_execution_preflight_records="
        f"{len(report['selected_route_execution_preflight_records'])}"
    )
    print(
        "[econ-workbench] "
        f"terminal_continuation_records={len(report['terminal_continuation_records'])}"
    )
    print(f"[econ-workbench] continuation_executed={str(report['continuation_executed']).lower()}")
    print(
        "[econ-workbench] "
        "terminal_continuation_recorded="
        f"{str(report['terminal_continuation_recorded']).lower()}"
    )
    print(f"[econ-workbench] this_command_ran_continuation={str(report['this_command_ran_continuation']).lower()}")
    print(f"[econ-workbench] selected_route_executed={str(report['selected_route_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

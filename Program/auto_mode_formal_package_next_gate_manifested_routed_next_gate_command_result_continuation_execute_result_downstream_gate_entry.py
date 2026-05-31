from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry import (  # noqa: E402
    DEFAULT_GATE_ENTRY_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record a downstream gate entry from a manifested routed continuation result review."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--manifested-routed-next-gate-command-result-continuation-execute-result-review",
        default=str(DEFAULT_RESULT_REVIEW_PATH),
    )
    parser.add_argument("--output-gate-entry", default=str(DEFAULT_GATE_ENTRY_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result_review_path = Path(
        args.manifested_routed_next_gate_command_result_continuation_execute_result_review
    )
    result_review = load_json_or_empty(project_root / result_review_path)
    report = (
        build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry(
            result_review,
            source_paths={
                "manifested_routed_next_gate_command_result_continuation_execute_result_review": (
                    str(result_review_path)
                ),
            },
        )
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_outputs(
            project_root,
            report,
            Path(args.output_gate_entry),
            Path(args.output_review),
        )
    )

    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(f"[econ-workbench] downstream_kind={report['downstream_kind']}")
    print(f"[econ-workbench] downstream_status={report['downstream_status']}")
    print(
        "[econ-workbench] "
        "downstream_gate_entry_recorded="
        f"{str(report['downstream_gate_entry_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_request_manifested_routed_next_gate_result_continuation_downstream="
        f"{str(report['can_request_manifested_routed_next_gate_result_continuation_downstream']).lower()}"
    )
    print(
        "[econ-workbench] "
        "requires_explicit_downstream_command="
        f"{str(report['requires_explicit_downstream_command']).lower()}"
    )
    print(f"[econ-workbench] downstream_input_records={len(report['downstream_input_records'])}")
    print(
        "[econ-workbench] "
        f"downstream_command_executed={str(report['downstream_command_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"this_command_ran_downstream_command={str(report['this_command_ran_downstream_command']).lower()}"
    )
    print(f"[econ-workbench] selected_route_executed={str(report['selected_route_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

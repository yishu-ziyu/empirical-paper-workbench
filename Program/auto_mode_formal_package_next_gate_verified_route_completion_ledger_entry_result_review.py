from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review import (  # noqa: E402
    DEFAULT_ENTRY_PATH,
    DEFAULT_LEDGER_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review P7-AV completion ledger entry before the verified route next-gate router."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--verified-route-completion-ledger-entry",
        default=str(DEFAULT_ENTRY_PATH),
    )
    parser.add_argument(
        "--verified-route-completion-ledger",
        default=str(DEFAULT_LEDGER_PATH),
    )
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    entry_path = Path(args.verified_route_completion_ledger_entry)
    ledger_path = Path(args.verified_route_completion_ledger)
    entry = load_json_or_empty(project_root / entry_path)
    ledger = load_json_or_empty(project_root / ledger_path)
    report = build_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review(
        project_root,
        entry,
        ledger,
        source_paths={
            "verified_route_completion_ledger_entry": str(entry_path),
            "verified_route_completion_ledger": str(ledger_path),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review_outputs(
            project_root,
            report,
            Path(args.output_result_review),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_result_review_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(
        "[econ-workbench] "
        "verified_route_completion_ledger_entry_result_reviewed="
        f"{str(report['verified_route_completion_ledger_entry_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_continue_to_verified_route_next_gate_router="
        f"{str(report['can_continue_to_verified_route_next_gate_router']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"verified_route_completion_ledger_status={report['verified_route_completion_ledger_status']}"
    )
    print(
        "[econ-workbench] "
        f"route_completion_ledger_recorded={str(report['route_completion_ledger_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"can_enter_next_auto_mode_gate={str(report['can_enter_next_auto_mode_gate']).lower()}"
    )
    print(f"[econ-workbench] route_completion_records={report['route_completion_record_count']}")
    print(
        "[econ-workbench] "
        "verified_route_next_gate_router_input_records="
        f"{len(report['verified_route_next_gate_router_input_records'])}"
    )
    print(
        "[econ-workbench] "
        f"verified_route_next_gate_router_executed={str(report['verified_route_next_gate_router_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "this_command_ran_verified_route_next_gate_router="
        f"{str(report['this_command_ran_verified_route_next_gate_router']).lower()}"
    )
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

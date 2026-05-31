from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry import (  # noqa: E402
    DEFAULT_ENTRY_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry,
    write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enter the routed next gate entry preflight after P7-AY accepts the router result."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--verified-route-next-gate-router-entry-result-review",
        default=str(DEFAULT_RESULT_REVIEW_PATH),
    )
    parser.add_argument("--output-entry", default=str(DEFAULT_ENTRY_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result_review_path = Path(args.verified_route_next_gate_router_entry_result_review)
    result_review = load_json_or_empty(project_root / result_review_path)
    report, _exit_code = run_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry(
        project_root,
        result_review,
        source_paths={
            "verified_route_next_gate_router_entry_result_review": str(result_review_path),
        },
        repo_root=REPO_ROOT,
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_outputs(
            project_root,
            report,
            Path(args.output_entry),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "can_enter_routed_next_gate_entry_preflight="
        f"{str(report['can_enter_routed_next_gate_entry_preflight']).lower()}"
    )
    print(
        "[econ-workbench] "
        "routed_next_gate_entry_preflight_entry_command_executed="
        f"{str(report['routed_next_gate_entry_preflight_entry_command_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "this_command_ran_routed_next_gate_entry_preflight="
        f"{str(report['this_command_ran_routed_next_gate_entry_preflight']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"routed_next_gate_entry_preflight_status={report['routed_next_gate_entry_preflight_status']}"
    )
    print(
        "[econ-workbench] "
        f"can_request_routed_next_gate_entry={str(report['can_request_routed_next_gate_entry']).lower()}"
    )
    print(f"[econ-workbench] next_gate_entry_plan={len(report['next_gate_entry_plan'])}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

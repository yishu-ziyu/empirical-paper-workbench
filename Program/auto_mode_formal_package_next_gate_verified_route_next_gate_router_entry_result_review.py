from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review import (  # noqa: E402
    DEFAULT_ENTRY_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_ROUTER_PATH,
    build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review P7-AX before routed next-gate entry preflight."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--verified-route-next-gate-router-entry", default=str(DEFAULT_ENTRY_PATH))
    parser.add_argument("--verified-route-next-gate-router", default=str(DEFAULT_ROUTER_PATH))
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    entry_path = Path(args.verified_route_next_gate_router_entry)
    router_path = Path(args.verified_route_next_gate_router)
    entry = load_json_or_empty(project_root / entry_path)
    router = load_json_or_empty(project_root / router_path)
    report = build_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review(
        project_root,
        entry,
        router,
        source_paths={
            "verified_route_next_gate_router_entry": str(entry_path),
            "verified_route_next_gate_router": str(router_path),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review_outputs(
            project_root,
            report,
            Path(args.output_result_review),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_verified_route_next_gate_router_entry_result_review_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "verified_route_next_gate_router_entry_result_reviewed="
        f"{str(report['verified_route_next_gate_router_entry_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_continue_to_routed_next_gate_entry_preflight="
        f"{str(report['can_continue_to_routed_next_gate_entry_preflight']).lower()}"
    )
    print(f"[econ-workbench] next_gate_route_recorded={str(report['next_gate_route_recorded']).lower()}")
    print(f"[econ-workbench] can_enter_routed_next_gate={str(report['can_enter_routed_next_gate']).lower()}")
    print(
        "[econ-workbench] "
        f"routed_next_gate_entry_preflight_input_records="
        f"{len(report['routed_next_gate_entry_preflight_input_records'])}"
    )
    print(
        "[econ-workbench] "
        "routed_next_gate_entry_preflight_executed="
        f"{str(report['routed_next_gate_entry_preflight_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "this_command_ran_routed_next_gate_entry_preflight="
        f"{str(report['this_command_ran_routed_next_gate_entry_preflight']).lower()}"
    )
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

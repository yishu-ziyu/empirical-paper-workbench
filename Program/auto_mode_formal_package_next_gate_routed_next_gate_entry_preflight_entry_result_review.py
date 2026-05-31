from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review import (  # noqa: E402
    DEFAULT_ENTRY_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review P7-AZ before the explicit routed next-gate entry gate."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--routed-next-gate-entry-preflight-entry", default=str(DEFAULT_ENTRY_PATH))
    parser.add_argument("--routed-next-gate-entry-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    entry_path = Path(args.routed_next_gate_entry_preflight_entry)
    preflight_path = Path(args.routed_next_gate_entry_preflight)
    entry = load_json_or_empty(project_root / entry_path)
    preflight = load_json_or_empty(project_root / preflight_path)
    report = build_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review(
        project_root,
        entry,
        preflight,
        source_paths={
            "routed_next_gate_entry_preflight_entry": str(entry_path),
            "routed_next_gate_entry_preflight": str(preflight_path),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review_outputs(
            project_root,
            report,
            Path(args.output_result_review),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_routed_next_gate_entry_preflight_entry_result_review_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        f"routed_next_gate_entry_preflight_status={report['routed_next_gate_entry_preflight_status']}"
    )
    print(
        "[econ-workbench] "
        "routed_next_gate_entry_preflight_entry_result_reviewed="
        f"{str(report['routed_next_gate_entry_preflight_entry_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_continue_to_explicit_routed_next_gate_entry="
        f"{str(report['can_continue_to_explicit_routed_next_gate_entry']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"can_request_routed_next_gate_entry={str(report['can_request_routed_next_gate_entry']).lower()}"
    )
    print(
        "[econ-workbench] "
        "requires_explicit_next_gate_entry_command="
        f"{str(report['requires_explicit_next_gate_entry_command']).lower()}"
    )
    print(f"[econ-workbench] next_gate_entry_plan={report['next_gate_entry_plan_count']}")
    print(
        "[econ-workbench] "
        "explicit_routed_next_gate_entry_input_records="
        f"{len(report['explicit_routed_next_gate_entry_input_records'])}"
    )
    print(
        "[econ-workbench] "
        "explicit_routed_next_gate_entry_executed="
        f"{str(report['explicit_routed_next_gate_entry_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"this_command_entered_next_gate={str(report['this_command_entered_next_gate']).lower()}"
    )
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

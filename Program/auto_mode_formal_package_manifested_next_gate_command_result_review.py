from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_manifested_next_gate_command_result_review import (  # noqa: E402
    DEFAULT_EXECUTE_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_package_manifested_next_gate_command_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_manifested_next_gate_command_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a manifested next-gate command result.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifested-next-gate-command-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--delegated-report", default="")
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    execute_path = Path(args.manifested_next_gate_command_execute)
    execute_report = load_json_or_empty(project_root / execute_path)
    delegated_report_path = Path(args.delegated_report) if args.delegated_report else None
    if delegated_report_path is None and execute_report.get("delegated_report_path"):
        delegated_report_path = Path(execute_report["delegated_report_path"])
    delegated_report = load_json_or_empty(project_root / delegated_report_path) if delegated_report_path else {}

    source_paths = {
        "manifested_next_gate_command_execute": str(execute_path),
        "delegated_report": str(delegated_report_path) if delegated_report_path else "",
    }
    report = build_auto_mode_formal_package_manifested_next_gate_command_result_review(
        project_root,
        execute_report,
        delegated_report,
        source_paths=source_paths,
    )
    report_path, review_path = write_auto_mode_formal_package_manifested_next_gate_command_result_review_outputs(
        project_root,
        report,
        Path(args.output_result_review),
        Path(args.output_review),
    )

    print(
        "[econ-workbench] "
        "auto_mode_formal_package_manifested_next_gate_command_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_manifested_next_gate_command_result_review_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(f"[econ-workbench] delegated_status={report['delegated_status']}")
    print(
        "[econ-workbench] "
        "delegated_next_gate_result_reviewed="
        f"{str(report['delegated_next_gate_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_continue_after_delegated_next_gate="
        f"{str(report['can_continue_after_delegated_next_gate']).lower()}"
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

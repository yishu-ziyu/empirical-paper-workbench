from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry import (  # noqa: E402
    DEFAULT_ENTRY_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enter the route-specific artifact executor from P7-AO.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--next-gate-selected-route-execute-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-artifact-executor-entry", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-entry", default=str(DEFAULT_ENTRY_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result_review_path = Path(args.next_gate_selected_route_execute_result_review)
    result_review = load_json_or_empty(project_root / result_review_path)
    report, _exit_code = run_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry(
        project_root,
        result_review,
        mode=args.mode,
        confirm_artifact_executor_entry=args.confirm_artifact_executor_entry,
        reviewer=args.reviewer,
        note=args.note,
        source_paths={
            "next_gate_selected_route_execute_result_review": str(result_review_path),
        },
        repo_root=REPO_ROOT,
    )
    report_path, review_path = write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_outputs(
        project_root,
        report,
        Path(args.output_entry),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(
        "[econ-workbench] "
        "can_enter_route_specific_artifact_executor_with_confirmation="
        f"{str(report['can_enter_route_specific_artifact_executor_with_confirmation']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"route_specific_artifact_executor_entry_command="
        f"{len(report['route_specific_artifact_executor_entry_command'])}"
    )
    print(
        "[econ-workbench] "
        "route_specific_artifact_executor_entry_command_executed="
        f"{str(report['route_specific_artifact_executor_entry_command_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "this_command_ran_route_specific_artifact_executor="
        f"{str(report['this_command_ran_route_specific_artifact_executor']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"route_specific_artifact_executor_entered="
        f"{str(report['route_specific_artifact_executor_entered']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"route_specific_artifact_executor_status={report['route_specific_artifact_executor_status']}"
    )
    print(f"[econ-workbench] route_specific_command_executed={str(report['route_specific_command_executed']).lower()}")
    print(f"[econ-workbench] route_specific_artifact_executed={str(report['route_specific_artifact_executed']).lower()}")
    print(f"[econ-workbench] selected_route_executed={str(report['selected_route_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] rendered_pdf={str(report['rendered_pdf']).lower()}")
    print(f"[econ-workbench] rendered_docx={str(report['rendered_docx']).lower()}")
    print(f"[econ-workbench] package_manifest_generated={str(report['package_manifest_generated']).lower()}")
    print(f"[econ-workbench] manual_acceptance_performed={str(report['manual_acceptance_performed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

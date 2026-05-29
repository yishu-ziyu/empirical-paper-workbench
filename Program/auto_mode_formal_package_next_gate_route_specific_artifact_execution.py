from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_execution import (  # noqa: E402
    DEFAULT_EXECUTION_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MANUAL_DECISIONS,
    VALID_MODES,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_route_specific_artifact_execution,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_execution_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute a route-specific artifact after P7-AQ result review approval."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--route-specific-artifact-executor-entry-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-artifact-execution", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--manual-decision", choices=sorted(VALID_MANUAL_DECISIONS), default="defer")
    parser.add_argument("--manual-actor", default="")
    parser.add_argument("--manual-note", default="")
    parser.add_argument("--output-execution", default=str(DEFAULT_EXECUTION_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result_review_path = Path(args.route_specific_artifact_executor_entry_result_review)
    result_review = load_json_or_empty(project_root / result_review_path)
    report, _exit_code = run_auto_mode_formal_package_next_gate_route_specific_artifact_execution(
        project_root,
        result_review,
        mode=args.mode,
        confirm_artifact_execution=args.confirm_artifact_execution,
        reviewer=args.reviewer,
        note=args.note,
        manual_decision=args.manual_decision,
        manual_actor=args.manual_actor,
        manual_note=args.manual_note,
        source_paths={
            "route_specific_artifact_executor_entry_result_review": str(result_review_path),
        },
        repo_root=REPO_ROOT,
    )
    report_path, review_path = write_auto_mode_formal_package_next_gate_route_specific_artifact_execution_outputs(
        project_root,
        report,
        Path(args.output_execution),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_route_specific_artifact_execution="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_route_specific_artifact_execution_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(
        "[econ-workbench] "
        "can_execute_route_specific_artifact_with_confirmation="
        f"{str(report['can_execute_route_specific_artifact_with_confirmation']).lower()}"
    )
    print(
        "[econ-workbench] "
        "route_specific_artifact_execution_command="
        f"{len(report['route_specific_artifact_execution_command'])}"
    )
    print(
        "[econ-workbench] "
        "route_specific_artifact_execution_command_executed="
        f"{str(report['route_specific_artifact_execution_command_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "this_command_ran_route_specific_artifact_executor="
        f"{str(report['this_command_ran_route_specific_artifact_executor']).lower()}"
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

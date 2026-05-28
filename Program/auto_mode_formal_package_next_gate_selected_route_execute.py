from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_selected_route_execute import (  # noqa: E402
    DEFAULT_EXECUTE_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_selected_route_execute,
    write_auto_mode_formal_package_next_gate_selected_route_execute_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a next-gate selected route execute gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--next-gate-workflow-continuation-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-selected-route-execute", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result_review_path = Path(args.next_gate_workflow_continuation_result_review)
    result_review = load_json_or_empty(project_root / result_review_path)
    report, _exit_code = run_auto_mode_formal_package_next_gate_selected_route_execute(
        project_root,
        result_review,
        mode=args.mode,
        confirm_selected_route_execute=args.confirm_selected_route_execute,
        reviewer=args.reviewer,
        note=args.note,
        source_paths={
            "next_gate_workflow_continuation_result_review": str(result_review_path),
        },
        repo_root=REPO_ROOT,
    )
    report_path, review_path = write_auto_mode_formal_package_next_gate_selected_route_execute_outputs(
        project_root,
        report,
        Path(args.output_execute),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_selected_route_execute={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_selected_route_execute_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "can_execute_selected_route_with_confirmation="
        f"{str(report['can_execute_selected_route_with_confirmation']).lower()}"
    )
    print(f"[econ-workbench] selected_route_execute_command={len(report['selected_route_execute_command'])}")
    print(
        "[econ-workbench] "
        "selected_route_execute_command_executed="
        f"{str(report['selected_route_execute_command_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "this_command_ran_selected_route_execute_command="
        f"{str(report['this_command_ran_selected_route_execute_command']).lower()}"
    )
    print(f"[econ-workbench] selected_route_execute_status={report['selected_route_execute_status']}")
    print(
        "[econ-workbench] "
        "selected_route_execute_manifest_recorded="
        f"{str(report['selected_route_execute_manifest_recorded']).lower()}"
    )
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

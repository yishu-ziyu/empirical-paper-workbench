from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_selected_route_execute_result_review import (  # noqa: E402
    DEFAULT_NEXT_GATE_EXECUTE_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH,
    DEFAULT_SELECTED_ROUTE_EXECUTE_PATH,
    build_auto_mode_formal_package_next_gate_selected_route_execute_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_selected_route_execute_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a next-gate selected route execute result.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--next-gate-selected-route-execute", default=str(DEFAULT_NEXT_GATE_EXECUTE_PATH))
    parser.add_argument("--selected-route-execute", default=str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH))
    parser.add_argument("--selected-route-execute-manifest", default=str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH))
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    next_gate_execute_path = Path(args.next_gate_selected_route_execute)
    selected_route_execute_path = Path(args.selected_route_execute)
    selected_route_execute_manifest_path = Path(args.selected_route_execute_manifest)
    next_gate_execute = load_json_or_empty(project_root / next_gate_execute_path)
    selected_route_execute = load_json_or_empty(project_root / selected_route_execute_path)
    selected_route_execute_manifest = load_json_or_empty(project_root / selected_route_execute_manifest_path)
    report = build_auto_mode_formal_package_next_gate_selected_route_execute_result_review(
        project_root,
        next_gate_execute,
        selected_route_execute,
        selected_route_execute_manifest,
        source_paths={
            "next_gate_selected_route_execute": str(next_gate_execute_path),
            "selected_route_execute": str(selected_route_execute_path),
            "selected_route_execute_manifest": str(selected_route_execute_manifest_path),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_selected_route_execute_result_review_outputs(
            project_root,
            report,
            Path(args.output_result_review),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_selected_route_execute_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_selected_route_execute_result_review_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] selected_route_execute_status={report['selected_route_execute_status']}")
    print(
        "[econ-workbench] "
        "selected_route_execute_result_reviewed="
        f"{str(report['selected_route_execute_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_continue_to_route_specific_artifact_executor="
        f"{str(report['can_continue_to_route_specific_artifact_executor']).lower()}"
    )
    print(
        "[econ-workbench] "
        "selected_route_execute_manifest_recorded="
        f"{str(report['selected_route_execute_manifest_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        "route_specific_artifact_executor_input_records="
        f"{len(report['route_specific_artifact_executor_input_records'])}"
    )
    print(
        "[econ-workbench] "
        f"route_specific_artifact_executed={str(report['route_specific_artifact_executed']).lower()}"
    )
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] rendered_pdf={str(report['rendered_pdf']).lower()}")
    print(f"[econ-workbench] rendered_docx={str(report['rendered_docx']).lower()}")
    print(f"[econ-workbench] package_manifest_generated={str(report['package_manifest_generated']).lower()}")
    print(f"[econ-workbench] manual_acceptance_performed={str(report['manual_acceptance_performed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review import (  # noqa: E402
    DEFAULT_ARTIFACT_EXECUTOR_PATH,
    DEFAULT_ENTRY_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review route-specific artifact executor entry output from P7-AP."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--route-specific-artifact-executor-entry", default=str(DEFAULT_ENTRY_PATH))
    parser.add_argument("--route-specific-artifact-executor", default=str(DEFAULT_ARTIFACT_EXECUTOR_PATH))
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    entry_path = Path(args.route_specific_artifact_executor_entry)
    artifact_executor_path = Path(args.route_specific_artifact_executor)
    entry = load_json_or_empty(project_root / entry_path)
    artifact_executor = load_json_or_empty(project_root / artifact_executor_path)
    report = build_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review(
        project_root,
        entry,
        artifact_executor,
        source_paths={
            "route_specific_artifact_executor_entry": str(entry_path),
            "route_specific_artifact_executor": str(artifact_executor_path),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review_outputs(
            project_root,
            report,
            Path(args.output_result_review),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_route_specific_artifact_executor_entry_result_review_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(
        "[econ-workbench] "
        f"route_specific_artifact_executor_status={report['route_specific_artifact_executor_status']}"
    )
    print(
        "[econ-workbench] "
        "artifact_executor_entry_result_reviewed="
        f"{str(report['artifact_executor_entry_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "can_continue_to_route_specific_artifact_execution="
        f"{str(report['can_continue_to_route_specific_artifact_execution']).lower()}"
    )
    print(
        "[econ-workbench] "
        "route_specific_artifact_execution_records="
        f"{len(report['route_specific_artifact_execution_records'])}"
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

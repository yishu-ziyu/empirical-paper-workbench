from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review import (  # noqa: E402
    DEFAULT_EXECUTE_GATE_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH,
    DEFAULT_SELECTED_ROUTE_EXECUTE_PATH,
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a manifested routed downstream execute gate result.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--manifested-routed-next-gate-command-result-continuation-execute-result-downstream-gate-entry-execute-gate",
        default=str(DEFAULT_EXECUTE_GATE_PATH),
    )
    parser.add_argument("--selected-route-execute", default=str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH))
    parser.add_argument("--selected-route-execute-manifest", default=str(DEFAULT_SELECTED_ROUTE_EXECUTE_MANIFEST_PATH))
    parser.add_argument("--output-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    downstream_execute_gate_path = Path(
        args.manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate
    )
    selected_route_execute_path = Path(args.selected_route_execute)
    selected_route_execute_manifest_path = Path(args.selected_route_execute_manifest)
    downstream_execute_gate = load_json_or_empty(project_root / downstream_execute_gate_path)
    selected_route_execute = load_json_or_empty(project_root / selected_route_execute_path)
    selected_route_execute_manifest = load_json_or_empty(project_root / selected_route_execute_manifest_path)
    report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review(
        project_root,
        downstream_execute_gate,
        selected_route_execute,
        selected_route_execute_manifest,
        source_paths={
            "manifested_routed_next_gate_downstream_execute_gate": str(downstream_execute_gate_path),
            "selected_route_execute": str(selected_route_execute_path),
            "selected_route_execute_manifest": str(selected_route_execute_manifest_path),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_command_result_continuation_execute_result_downstream_gate_entry_execute_gate_result_review_outputs(
            project_root,
            report,
            Path(args.output_result_review),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_review="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_review_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] downstream_kind={report['downstream_kind']}")
    print(
        "[econ-workbench] "
        f"downstream_execute_result_reviewed={str(report['downstream_execute_result_reviewed']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"can_continue_after_downstream_execute={str(report['can_continue_after_downstream_execute']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"selected_route_execute_manifest_recorded={str(report['selected_route_execute_manifest_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        "route_specific_artifact_executor_input_records="
        f"{len(report['route_specific_artifact_executor_input_records'])}"
    )
    print(
        "[econ-workbench] "
        f"product_review_preparation_result_records={len(report['product_review_preparation_result_records'])}"
    )
    print(f"[econ-workbench] selected_route_executed={str(report['selected_route_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

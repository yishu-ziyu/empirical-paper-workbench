from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate import (  # noqa: E402
    DEFAULT_EXECUTE_GATE_PATH,
    DEFAULT_GATE_ENTRY_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate,
    write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute or preview the downstream execute result continuation gate entry."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--manifested-routed-downstream-execute-result-continuation-gate-entry",
        default=str(DEFAULT_GATE_ENTRY_PATH),
    )
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-downstream-execute-result-continuation", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute-gate", default=str(DEFAULT_EXECUTE_GATE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    gate_entry_path = Path(args.manifested_routed_downstream_execute_result_continuation_gate_entry)
    gate_entry = load_json_or_empty(project_root / gate_entry_path)
    report, _exit_code = (
        run_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate(
            project_root,
            gate_entry,
            mode=args.mode,
            confirm_downstream_execute_result_continuation=(
                args.confirm_downstream_execute_result_continuation
            ),
            reviewer=args.reviewer,
            note=args.note,
            source_paths={
                "manifested_routed_downstream_execute_result_continuation_gate_entry": str(gate_entry_path),
            },
            repo_root=REPO_ROOT,
        )
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_outputs(
            project_root,
            report,
            Path(args.output_execute_gate),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_downstream_execute_result_continuation_gate_entry_execute_gate_md="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] continuation_kind={report['continuation_kind']}")
    print(
        "[econ-workbench] "
        "can_execute_downstream_execute_result_continuation_with_confirmation="
        f"{str(report['can_execute_downstream_execute_result_continuation_with_confirmation']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"requires_explicit_continuation_command={str(report['requires_explicit_continuation_command']).lower()}"
    )
    print(f"[econ-workbench] continuation_execute_command={len(report['continuation_execute_command'])}")
    print(
        "[econ-workbench] "
        f"continuation_execute_command_executed={str(report['continuation_execute_command_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"this_command_ran_continuation_command={str(report['this_command_ran_continuation_command']).lower()}"
    )
    print(
        "[econ-workbench] "
        "route_specific_artifact_executor_entry_entered="
        f"{str(report['route_specific_artifact_executor_entry_entered']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"route_specific_artifact_executor_entry_status={report['route_specific_artifact_executor_entry_status']}"
    )
    print(
        "[econ-workbench] "
        f"product_review_packet_preparation_recorded={str(report['product_review_packet_preparation_recorded']).lower()}"
    )
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

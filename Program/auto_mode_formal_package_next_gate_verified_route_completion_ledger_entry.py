from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry import (  # noqa: E402
    DEFAULT_ENTRY_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry,
    write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enter existing verified route completion ledger after P7-AU result review."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--route-specific-artifact-verification-entry-result-review",
        default=str(DEFAULT_RESULT_REVIEW_PATH),
    )
    parser.add_argument("--output-entry", default=str(DEFAULT_ENTRY_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result_review_path = Path(args.route_specific_artifact_verification_entry_result_review)
    result_review = load_json_or_empty(project_root / result_review_path)
    report, _exit_code = run_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry(
        project_root,
        result_review,
        source_paths={
            "route_specific_artifact_verification_entry_result_review": str(result_review_path),
        },
        repo_root=REPO_ROOT,
    )
    report_path, review_path = write_auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_outputs(
        project_root,
        report,
        Path(args.output_entry),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_verified_route_completion_ledger_entry_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(
        "[econ-workbench] "
        "can_enter_verified_route_completion_ledger="
        f"{str(report['can_enter_verified_route_completion_ledger']).lower()}"
    )
    print(
        "[econ-workbench] "
        "verified_route_completion_ledger_entry_command_executed="
        f"{str(report['verified_route_completion_ledger_entry_command_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        "this_command_ran_verified_route_completion_ledger="
        f"{str(report['this_command_ran_verified_route_completion_ledger']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"verified_route_completion_ledger_status={report['verified_route_completion_ledger_status']}"
    )
    print(
        "[econ-workbench] "
        f"route_completion_ledger_recorded={str(report['route_completion_ledger_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"can_enter_next_auto_mode_gate={str(report['can_enter_next_auto_mode_gate']).lower()}"
    )
    print(f"[econ-workbench] route_completion_records={report['route_completion_record_count']}")
    print(
        "[econ-workbench] "
        f"route_specific_artifact_verified={str(report['route_specific_artifact_verified']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"artifact_verification_record_count={report['artifact_verification_record_count']}"
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

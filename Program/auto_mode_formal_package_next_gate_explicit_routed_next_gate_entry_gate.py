from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate import (  # noqa: E402
    DEFAULT_ENTRY_MANIFEST_PATH,
    DEFAULT_EXECUTE_PATH,
    DEFAULT_EXECUTE_REVIEW_PATH,
    DEFAULT_GATE_PATH,
    DEFAULT_GATE_REVIEW_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    VALID_MODES,
    load_json_or_empty,
    run_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate,
    write_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run P7-BB explicit routed next-gate entry gate after P7-BA accepts preflight."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--routed-next-gate-entry-preflight-entry-result-review",
        default=str(DEFAULT_RESULT_REVIEW_PATH),
    )
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="execute")
    parser.add_argument("--confirm-entry", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-gate", default=str(DEFAULT_GATE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_GATE_REVIEW_PATH))
    parser.add_argument("--execute-report", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--execute-review", default=str(DEFAULT_EXECUTE_REVIEW_PATH))
    parser.add_argument("--entry-manifest", default=str(DEFAULT_ENTRY_MANIFEST_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result_review_path = Path(args.routed_next_gate_entry_preflight_entry_result_review)
    result_review = load_json_or_empty(project_root / result_review_path)
    report, _exit_code = run_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate(
        project_root,
        result_review,
        mode=args.mode,
        confirm_entry=args.confirm_entry,
        reviewer=args.reviewer,
        note=args.note,
        source_paths={
            "routed_next_gate_entry_preflight_entry_result_review": str(result_review_path),
        },
        execute_report_path=Path(args.execute_report),
        execute_review_path=Path(args.execute_review),
        entry_manifest_path=Path(args.entry_manifest),
    )
    report_path, review_path = write_auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate_outputs(
        project_root,
        report,
        Path(args.output_gate),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_next_gate_explicit_routed_next_gate_entry_gate_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "can_execute_explicit_routed_next_gate_entry="
        f"{str(report['can_execute_explicit_routed_next_gate_entry']).lower()}"
    )
    print(
        "[econ-workbench] "
        "explicit_routed_next_gate_entry_gate_executed="
        f"{str(report['explicit_routed_next_gate_entry_gate_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"explicit_routed_next_gate_entry_execute_status={report['explicit_routed_next_gate_entry_execute_status']}"
    )
    print(
        "[econ-workbench] "
        f"routed_next_gate_entry_manifest_recorded="
        f"{str(report['routed_next_gate_entry_manifest_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"explicit_routed_next_gate_entry_operations="
        f"{len(report['explicit_routed_next_gate_entry_operations'])}"
    )
    print(f"[econ-workbench] next_gate_entered={str(report['next_gate_entered']).lower()}")
    print(f"[econ-workbench] next_gate_command_executed={str(report['next_gate_command_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

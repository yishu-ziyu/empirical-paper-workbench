from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_route_specific_artifact_executor import (  # noqa: E402
    DEFAULT_EXECUTE_MANIFEST_PATH,
    DEFAULT_EXECUTOR_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SELECTED_ROUTE_EXECUTE_PATH,
    VALID_MANUAL_DECISIONS,
    VALID_MODES,
    load_json_or_empty,
    run_auto_mode_formal_package_route_specific_artifact_executor,
    write_auto_mode_formal_package_route_specific_artifact_executor_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Auto Mode route-specific formal package artifact executor.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--selected-route-execute", default=str(DEFAULT_SELECTED_ROUTE_EXECUTE_PATH))
    parser.add_argument("--execute-manifest", default=str(DEFAULT_EXECUTE_MANIFEST_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-artifact-execution", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--manual-decision", choices=sorted(VALID_MANUAL_DECISIONS), default="defer")
    parser.add_argument("--manual-actor", default="")
    parser.add_argument("--manual-note", default="")
    parser.add_argument("--output-executor", default=str(DEFAULT_EXECUTOR_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    selected_route_execute = load_json_or_empty(project_root / args.selected_route_execute)
    execute_manifest = load_json_or_empty(project_root / args.execute_manifest)
    report, _exit_code = run_auto_mode_formal_package_route_specific_artifact_executor(
        project_root,
        selected_route_execute,
        execute_manifest,
        mode=args.mode,
        confirm_artifact_execution=args.confirm_artifact_execution,
        reviewer=args.reviewer,
        note=args.note,
        manual_decision=args.manual_decision,
        manual_actor=args.manual_actor,
        manual_note=args.manual_note,
        source_paths={
            "selected_route_execute": str(Path(args.selected_route_execute)),
            "selected_route_execute_manifest": str(Path(args.execute_manifest)),
        },
        repo_root=REPO_ROOT,
    )
    report_path, review_path = write_auto_mode_formal_package_route_specific_artifact_executor_outputs(
        project_root,
        report,
        Path(args.output_executor),
        Path(args.output_review),
    )
    print(f"[econ-workbench] auto_mode_formal_package_route_specific_artifact_executor={report_path.relative_to(project_root)}")
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_route_specific_artifact_executor_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] route_type={report['route_type']}")
    print(
        "[econ-workbench] "
        f"route_specific_command_executed={str(report['route_specific_command_executed']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"route_specific_artifact_executed={str(report['route_specific_artifact_executed']).lower()}"
    )
    print(f"[econ-workbench] delegated_status={report['delegated_status']}")
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

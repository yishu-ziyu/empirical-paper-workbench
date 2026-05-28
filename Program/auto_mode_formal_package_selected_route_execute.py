from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_selected_route_execute import (  # noqa: E402
    DEFAULT_EXECUTE_MANIFEST_PATH,
    DEFAULT_EXECUTE_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    build_auto_mode_formal_package_selected_route_execute,
    load_json_or_empty,
    write_auto_mode_formal_package_selected_route_execute_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Auto Mode selected formal package route execute gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--selected-route-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-execute", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--execute-manifest", default=str(DEFAULT_EXECUTE_MANIFEST_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight = load_json_or_empty(project_root / args.selected_route_preflight)
    report = build_auto_mode_formal_package_selected_route_execute(
        preflight,
        mode=args.mode,
        confirm_execute=args.confirm_execute,
        reviewer=args.reviewer,
        note=args.note,
        execute_manifest_path=Path(args.execute_manifest),
        source_paths={
            "selected_route_execution_preflight": str(Path(args.selected_route_preflight)),
        },
    )
    report_path, review_path, manifest_path = write_auto_mode_formal_package_selected_route_execute_outputs(
        project_root,
        report,
        Path(args.output_execute),
        Path(args.output_review),
        Path(args.execute_manifest),
    )
    print(f"[econ-workbench] auto_mode_formal_package_selected_route_execute={report_path.relative_to(project_root)}")
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_selected_route_execute_review={review_path.relative_to(project_root)}"
    )
    if manifest_path is not None:
        print(
            "[econ-workbench] "
            f"auto_mode_formal_package_selected_route_execute_manifest={manifest_path.relative_to(project_root)}"
        )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(
        "[econ-workbench] "
        "can_execute_selected_route_with_confirmation="
        f"{str(report['can_execute_selected_route_with_confirmation']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"selected_route_execute_manifest_recorded={str(report['selected_route_execute_manifest_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"selected_route_execute_operations={len(report['selected_route_execute_operations'])}"
    )
    print(f"[econ-workbench] selected_route_executed={str(report['selected_route_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] rendered_pdf={str(report['rendered_pdf']).lower()}")
    print(f"[econ-workbench] rendered_docx={str(report['rendered_docx']).lower()}")
    print(f"[econ-workbench] package_manifest_generated={str(report['package_manifest_generated']).lower()}")
    print(f"[econ-workbench] manual_acceptance_performed={str(report['manual_acceptance_performed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

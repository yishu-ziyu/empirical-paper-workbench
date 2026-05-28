from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_selected_route_execution_preflight import (  # noqa: E402
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_ROUTER_PATH,
    build_auto_mode_formal_package_selected_route_execution_preflight,
    load_json_or_empty,
    write_auto_mode_formal_package_selected_route_execution_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build selected formal package route execution preflight without exporting or accepting.",
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--export-acceptance-router", default=str(DEFAULT_ROUTER_PATH))
    parser.add_argument("--output-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    router = load_json_or_empty(project_root / args.export_acceptance_router)
    report = build_auto_mode_formal_package_selected_route_execution_preflight(
        router,
        source_paths={
            "export_acceptance_router": str(Path(args.export_acceptance_router)),
        },
    )
    report_path, review_path = write_auto_mode_formal_package_selected_route_execution_preflight_outputs(
        project_root,
        report,
        Path(args.output_preflight),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_selected_route_execution_preflight={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_selected_route_execution_preflight_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(
        "[econ-workbench] "
        f"can_request_selected_route_execution={str(report['can_request_selected_route_execution']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"requires_explicit_route_execute_command={str(report['requires_explicit_route_execute_command']).lower()}"
    )
    print(f"[econ-workbench] selected_route_execution_plan={len(report['selected_route_execution_plan'])}")
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

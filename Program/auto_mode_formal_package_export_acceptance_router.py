from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_export_acceptance_router import (  # noqa: E402
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_ROUTER_PATH,
    build_auto_mode_formal_package_export_acceptance_router,
    load_json_or_empty,
    write_auto_mode_formal_package_export_acceptance_router_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record an explicit Auto Mode formal package export / acceptance route without exporting.",
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--export-acceptance-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument(
        "--decision",
        default="defer",
        help="defer, pdf_export, docx_export, package_manifest, or manual_acceptance.",
    )
    parser.add_argument("--confirm-route", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-router", default=str(DEFAULT_ROUTER_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight = load_json_or_empty(project_root / args.export_acceptance_preflight)
    report = build_auto_mode_formal_package_export_acceptance_router(
        preflight,
        decision=args.decision,
        confirm_route=args.confirm_route,
        reviewer=args.reviewer,
        note=args.note,
        source_paths={
            "export_acceptance_preflight": str(Path(args.export_acceptance_preflight)),
        },
    )
    report_path, review_path = write_auto_mode_formal_package_export_acceptance_router_outputs(
        project_root,
        report,
        Path(args.output_router),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_export_acceptance_router={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_export_acceptance_router_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(
        "[econ-workbench] "
        f"can_route_export_or_acceptance={str(report['can_route_export_or_acceptance']).lower()}"
    )
    print(f"[econ-workbench] route_recorded={str(report['route_recorded']).lower()}")
    print(f"[econ-workbench] routed_action={report['routed_action']}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] rendered_pdf={str(report['rendered_pdf']).lower()}")
    print(f"[econ-workbench] rendered_docx={str(report['rendered_docx']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

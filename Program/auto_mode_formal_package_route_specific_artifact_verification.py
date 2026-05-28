from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_route_specific_artifact_verification import (  # noqa: E402
    DEFAULT_EXECUTOR_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_VERIFICATION_PATH,
    build_auto_mode_formal_package_route_specific_artifact_verification,
    load_json_or_empty,
    write_auto_mode_formal_package_route_specific_artifact_verification_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Auto Mode route-specific formal package artifact.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--route-specific-artifact-executor", default=str(DEFAULT_EXECUTOR_PATH))
    parser.add_argument("--delegated-report", default="")
    parser.add_argument("--output-verification", default=str(DEFAULT_VERIFICATION_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    executor_path = Path(args.route_specific_artifact_executor)
    executor = load_json_or_empty(project_root / executor_path)
    delegated_path_value = args.delegated_report or executor.get("delegated_report_path", "")
    delegated_path = Path(delegated_path_value) if delegated_path_value else None
    delegated = load_json_or_empty(project_root / delegated_path) if delegated_path is not None else {}
    report = build_auto_mode_formal_package_route_specific_artifact_verification(
        project_root,
        executor,
        delegated,
        source_paths={
            "route_specific_artifact_executor": str(executor_path),
            "delegated_report": delegated_path_value,
        },
    )
    report_path, review_path = write_auto_mode_formal_package_route_specific_artifact_verification_outputs(
        project_root,
        report,
        Path(args.output_verification),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_route_specific_artifact_verification={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_route_specific_artifact_verification_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] route_type={report['route_type']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] delegated_status={report['delegated_status']}")
    print(f"[econ-workbench] route_specific_artifact_verified={str(report['route_specific_artifact_verified']).lower()}")
    print(f"[econ-workbench] selected_route_executed={str(report['selected_route_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

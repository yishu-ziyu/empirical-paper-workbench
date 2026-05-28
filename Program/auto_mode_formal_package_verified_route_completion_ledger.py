from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_verified_route_completion_ledger import (  # noqa: E402
    DEFAULT_LEDGER_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_VERIFICATION_PATH,
    build_auto_mode_formal_package_verified_route_completion_ledger,
    load_json_or_empty,
    write_auto_mode_formal_package_verified_route_completion_ledger_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Auto Mode verified route completion ledger.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--route-specific-artifact-verification", default=str(DEFAULT_VERIFICATION_PATH))
    parser.add_argument("--output-ledger", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    verification_path = Path(args.route_specific_artifact_verification)
    verification = load_json_or_empty(project_root / verification_path)
    report = build_auto_mode_formal_package_verified_route_completion_ledger(
        verification,
        source_paths={
            "route_specific_artifact_verification": str(verification_path),
        },
    )
    report_path, review_path = write_auto_mode_formal_package_verified_route_completion_ledger_outputs(
        project_root,
        report,
        Path(args.output_ledger),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_verified_route_completion_ledger={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_verified_route_completion_ledger_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(
        "[econ-workbench] "
        f"route_completion_ledger_recorded={str(report['route_completion_ledger_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"can_enter_next_auto_mode_gate={str(report['can_enter_next_auto_mode_gate']).lower()}"
    )
    print(f"[econ-workbench] route_completion_records={len(report['route_completion_records'])}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

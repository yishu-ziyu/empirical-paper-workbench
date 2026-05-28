from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_verified_route_next_gate_router import (  # noqa: E402
    DEFAULT_LEDGER_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_ROUTER_PATH,
    build_auto_mode_formal_package_verified_route_next_gate_router,
    load_json_or_empty,
    write_auto_mode_formal_package_verified_route_next_gate_router_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Route Auto Mode verified route completion to the next gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--verified-route-completion-ledger", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--output-router", default=str(DEFAULT_ROUTER_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    ledger_path = Path(args.verified_route_completion_ledger)
    ledger = load_json_or_empty(project_root / ledger_path)
    report = build_auto_mode_formal_package_verified_route_next_gate_router(
        ledger,
        source_paths={
            "verified_route_completion_ledger": str(ledger_path),
        },
    )
    report_path, review_path = write_auto_mode_formal_package_verified_route_next_gate_router_outputs(
        project_root,
        report,
        Path(args.output_router),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_verified_route_next_gate_router={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_verified_route_next_gate_router_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(f"[econ-workbench] next_gate_route_recorded={str(report['next_gate_route_recorded']).lower()}")
    print(f"[econ-workbench] can_enter_routed_next_gate={str(report['can_enter_routed_next_gate']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_routed_next_gate_entry_preflight import (  # noqa: E402
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_ROUTER_PATH,
    build_auto_mode_formal_package_routed_next_gate_entry_preflight,
    load_json_or_empty,
    write_auto_mode_formal_package_routed_next_gate_entry_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare routed next Auto Mode gate entry without entering it.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--verified-route-next-gate-router", default=str(DEFAULT_ROUTER_PATH))
    parser.add_argument("--output-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    router_path = Path(args.verified_route_next_gate_router)
    router = load_json_or_empty(project_root / router_path)
    report = build_auto_mode_formal_package_routed_next_gate_entry_preflight(
        router,
        source_paths={
            "verified_route_next_gate_router": str(router_path),
        },
    )
    report_path, review_path = write_auto_mode_formal_package_routed_next_gate_entry_preflight_outputs(
        project_root,
        report,
        Path(args.output_preflight),
        Path(args.output_review),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_routed_next_gate_entry_preflight={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_routed_next_gate_entry_preflight_review={review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        f"can_request_routed_next_gate_entry={str(report['can_request_routed_next_gate_entry']).lower()}"
    )
    print(f"[econ-workbench] next_gate_entry_plan={len(report['next_gate_entry_plan'])}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

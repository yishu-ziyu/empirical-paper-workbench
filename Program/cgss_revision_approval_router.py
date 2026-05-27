from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_revision_approval_router import (  # noqa: E402
    DEFAULT_APPROVAL_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_WORK_ORDER_RESULT_PATH,
    DEFAULT_WORK_ORDER_REVIEW_PATH,
    build_cgss_revision_approval_route,
    load_json_or_empty,
    write_cgss_revision_approval_route_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a CGSS revision approval record to the next workflow step.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--approval", default=str(DEFAULT_APPROVAL_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--work-order-result", default=str(DEFAULT_WORK_ORDER_RESULT_PATH))
    parser.add_argument("--work-order-review", default=str(DEFAULT_WORK_ORDER_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    approval_record = load_json_or_empty(project_root / args.approval)
    route = build_cgss_revision_approval_route(approval_record)
    review_path, written_work_orders = write_cgss_revision_approval_route_outputs(
        project_root,
        route,
        Path(args.output_review),
        Path(args.output_result),
        Path(args.work_order_result),
        Path(args.work_order_review),
    )
    print(f"[econ-workbench] cgss_revision_approval_router_result={Path(args.output_result)}")
    print(f"[econ-workbench] cgss_revision_approval_router_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={route['status']}")
    print(f"[econ-workbench] route={route['route']}")
    print(f"[econ-workbench] decision={route['decision']}")
    print(f"[econ-workbench] work_orders={len(written_work_orders)}")
    print(f"[econ-workbench] formal_writeback_allowed={str(route['formal_writeback_allowed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(route['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

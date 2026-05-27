from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_revision_work_orders import (  # noqa: E402
    DEFAULT_QUEUE_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    build_cgss_revision_work_orders,
    load_json_or_empty,
    write_revision_work_order_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Expand an approved CGSS revision queue into draft-layer work orders.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    queue = load_json_or_empty(project_root / args.queue)
    manifest = build_cgss_revision_work_orders(queue)
    result_path, review_path, written_files = write_revision_work_order_outputs(
        project_root,
        manifest,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_revision_work_orders={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_revision_work_orders_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={manifest['status']}")
    print(f"[econ-workbench] work_orders={len(manifest['work_orders'])}")
    print(f"[econ-workbench] written_work_orders={len(written_files)}")
    print(f"[econ-workbench] blocking_reasons={','.join(manifest['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

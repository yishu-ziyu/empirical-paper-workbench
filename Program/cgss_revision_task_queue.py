from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_revision_task_queue import (  # noqa: E402
    DEFAULT_LITERATURE_REVIEW_PACKET_PATH,
    DEFAULT_LITERATURE_SEED_PACKAGE_PATH,
    DEFAULT_METHOD_STRUCTURE_GATE_PACKET_PATH,
    DEFAULT_REVIEW_PATH,
    build_cgss_revision_task_queue,
    load_json_or_empty,
    write_revision_task_queue_review,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a draft-layer CGSS reviewer-style revision task queue.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--literature-seed-package", default=str(DEFAULT_LITERATURE_SEED_PACKAGE_PATH))
    parser.add_argument("--literature-review-packet", default=str(DEFAULT_LITERATURE_REVIEW_PACKET_PATH))
    parser.add_argument("--method-structure-gate-packet", default=str(DEFAULT_METHOD_STRUCTURE_GATE_PACKET_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    literature_seed_package = load_json_or_empty(project_root / args.literature_seed_package)
    literature_review_packet = load_json_or_empty(project_root / args.literature_review_packet)
    method_structure_gate_packet = load_json_or_empty(project_root / args.method_structure_gate_packet)
    queue = build_cgss_revision_task_queue(
        literature_seed_package,
        literature_review_packet,
        method_structure_gate_packet,
        source_paths={
            "literature_seed_package": args.literature_seed_package,
            "literature_review_packet": args.literature_review_packet,
            "method_structure_gate_packet": args.method_structure_gate_packet,
        },
    )
    review_path = write_revision_task_queue_review(project_root, queue, Path(args.output_review))
    print(f"[econ-workbench] cgss_revision_task_queue_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={queue['status']}")
    print(f"[econ-workbench] agent_tasks={len(queue['agent_task_queue'])}")
    print(f"[econ-workbench] blocking_reasons={','.join(queue['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

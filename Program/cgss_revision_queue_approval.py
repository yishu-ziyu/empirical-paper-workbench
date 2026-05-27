from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_revision_queue_approval import (  # noqa: E402
    DEFAULT_APPROVED_QUEUE_PATH,
    DEFAULT_QUEUE_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    build_revision_queue_approval,
    load_json_or_empty,
    write_revision_queue_approval_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a human decision for the CGSS revision task queue.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    parser.add_argument("--decision", choices=["defer", "approve", "revise", "reject"], default="defer")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--output-approved-queue", default=str(DEFAULT_APPROVED_QUEUE_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    queue = load_json_or_empty(project_root / args.queue)
    record = build_revision_queue_approval(
        queue,
        decision=args.decision,
        reviewer=args.reviewer,
        note=args.note,
    )
    result_path, review_path, approved_queue_path = write_revision_queue_approval_outputs(
        project_root,
        record,
        Path(args.output_result),
        Path(args.output_review),
        Path(args.output_approved_queue),
    )
    print(f"[econ-workbench] cgss_revision_queue_approval={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_revision_queue_approval_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={record['status']}")
    print(f"[econ-workbench] decision={record['decision']}")
    print(f"[econ-workbench] approved={str(record['approved']).lower()}")
    if approved_queue_path is None:
        print("[econ-workbench] approved_queue=none")
    else:
        print(f"[econ-workbench] approved_queue={approved_queue_path.relative_to(project_root)}")
    print(f"[econ-workbench] blocking_reasons={','.join(record['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

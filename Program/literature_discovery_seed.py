from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.literature_discovery_seed import (  # noqa: E402
    DEFAULT_DATASET_INDEX_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_literature_discovery_seed,
    load_json,
    write_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable literature discovery seed without formal bibliography writeback.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--dataset-index", default=str(DEFAULT_DATASET_INDEX_PATH))
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    dataset_index_path = project_root / args.dataset_index
    dataset_index = load_json(dataset_index_path) if dataset_index_path.exists() else None
    report = build_literature_discovery_seed(
        topic=args.topic,
        dataset_index=dataset_index,
        source_paths={"dataset_index": str(Path(args.dataset_index))},
    )
    report_path, review_path = write_report(
        project_root,
        report,
        Path(args.output_report),
        Path(args.output_review),
    )
    print(f"[econ-workbench] literature_discovery_seed={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] literature_discovery_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    return 0 if report["status"] == "needs_human_literature_discovery_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())

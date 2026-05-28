from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.method_knowledge_base import (  # noqa: E402
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_method_knowledge_base,
    write_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a queryable empirical method knowledge base report.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--query", default="")
    parser.add_argument(
        "--profile",
        choices=["working_paper", "aer_like", "top_journal"],
        default="working_paper",
    )
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    kb = build_method_knowledge_base(project_root, query=args.query, profile=args.profile)
    report_path, review_path = write_outputs(
        project_root,
        kb,
        Path(args.output_report),
        Path(args.output_review),
    )
    print(f"[econ-workbench] method_knowledge_base={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] method_knowledge_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={kb['status']}")
    print(f"[econ-workbench] recommended_checks={len(kb['recommended_checks'])}")
    return 0 if kb["status"] != "blocked_missing_methodology_sources" else 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.parent_education_wage_execution_readiness import (  # noqa: E402
    DEFAULT_LEDGER_PATH,
    DEFAULT_REVIEW_PATH,
    build_parent_education_wage_execution_readiness_ledger,
    repair_parent_education_wage_design_draft,
    write_parent_education_wage_execution_readiness_ledger,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate P2 execution-readiness ledger for parent education wage demo.")
    parser.add_argument("--project-root", default=".", help="Project root path.")
    parser.add_argument("--output-ledger", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    repair_parent_education_wage_design_draft(project_root)
    ledger = build_parent_education_wage_execution_readiness_ledger(project_root)
    json_path, review_path = write_parent_education_wage_execution_readiness_ledger(
        project_root,
        ledger,
        Path(args.output_ledger),
        Path(args.output_review),
    )
    print(f"[econ-workbench] p2_execution_readiness={json_path.relative_to(project_root)}")
    print(f"[econ-workbench] p2_execution_readiness_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={ledger['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.parent_education_wage_method_execution_ledger import (  # noqa: E402
    DEFAULT_LEDGER_PATH,
    DEFAULT_REVIEW_PATH,
    build_parent_education_wage_method_execution_ledger,
    write_parent_education_wage_method_execution_ledger,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the parent-education wage P1-C method execution ledger.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--output-ledger", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    ledger = build_parent_education_wage_method_execution_ledger(project_root)
    ledger_path, review_path = write_parent_education_wage_method_execution_ledger(
        project_root,
        ledger,
        Path(args.output_ledger),
        Path(args.output_review),
    )
    print(f"[econ-workbench] p1c_method_execution_ledger={ledger_path.relative_to(project_root)}")
    print(f"[econ-workbench] p1c_method_execution_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={ledger['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

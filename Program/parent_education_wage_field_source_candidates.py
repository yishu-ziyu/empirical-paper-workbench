from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Program.workbench.parent_education_wage_field_source_candidates import (  # noqa: E402
    run_parent_education_wage_field_source_candidates,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate parent-education wage field source candidates.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument("--data-root", default=None, help="Optional CFPS data root override.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    data_root = Path(args.data_root).expanduser().resolve() if args.data_root else None
    ledger, json_path, review_path = run_parent_education_wage_field_source_candidates(project_root, data_root=data_root)
    print(f"[econ-workbench] p4_field_source_candidates={json_path.relative_to(project_root)}")
    print(f"[econ-workbench] review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={ledger['status']}")
    print(f"[econ-workbench] candidate_count={ledger['candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

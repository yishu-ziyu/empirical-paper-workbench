from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Program.workbench.parent_education_wage_draft_package import (  # noqa: E402
    run_parent_education_wage_draft_package,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate parent-education wage DraftPackage.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    package, json_path = run_parent_education_wage_draft_package(project_root)
    print(f"[econ-workbench] p3_draft_package={json_path.relative_to(project_root)}")
    print(f"[econ-workbench] paper_draft={package['outputs']['docx']}")
    print(f"[econ-workbench] status={package['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

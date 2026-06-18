from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Program.workbench.parent_education_wage_variable_role_preflight import (  # noqa: E402
    run_parent_education_wage_variable_role_preflight,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate parent-education wage VariableRoleSet draft preflight.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    preflight, json_path, review_path = run_parent_education_wage_variable_role_preflight(project_root)
    print(f"[econ-workbench] p5_variable_role_preflight={json_path.relative_to(project_root)}")
    print(f"[econ-workbench] review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={preflight['status']}")
    print(f"[econ-workbench] can_write_formal_variable_roles={preflight['can_write_formal_variable_roles']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

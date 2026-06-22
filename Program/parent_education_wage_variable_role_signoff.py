from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Program.workbench.parent_education_wage_variable_role_signoff import (  # noqa: E402
    promote_parent_education_wage_variable_role_signoff,
    run_parent_education_wage_variable_role_signoff,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate P6 human signoff package for parent-education wage variable roles.")
    parser.add_argument("--project-root", default=".", help="Project root. Defaults to current directory.")
    parser.add_argument("--promote-payload-json", default="", help="Optional JSON payload for editable draft promotion.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if args.promote_payload_json:
        result = promote_parent_education_wage_variable_role_signoff(
            project_root,
            json.loads(args.promote_payload_json),
        )
        print(json.dumps({"status": result["status"]}, ensure_ascii=False))
        return

    signoff, json_path, review_path = run_parent_education_wage_variable_role_signoff(project_root)
    print(
        json.dumps(
            {
                "status": signoff["status"],
                "json": json_path.relative_to(project_root).as_posix(),
                "review": review_path.relative_to(project_root).as_posix(),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

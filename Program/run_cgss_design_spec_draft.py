from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_design_spec_draft import (  # noqa: E402
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_ROLE_DRAFT_PATH,
    build_cgss_design_spec_draft,
    load_json,
    write_cgss_design_spec_draft_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable CGSS DesignSpec draft.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--role-draft", default=str(DEFAULT_ROLE_DRAFT_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    role_draft = load_json(project_root / args.role_draft)
    draft = build_cgss_design_spec_draft(
        role_draft,
        source_paths={"dataset_bound_variable_role_draft": args.role_draft},
    )
    result_path, review_path = write_cgss_design_spec_draft_outputs(
        project_root,
        draft,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_design_spec_draft={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_design_spec_draft_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={draft['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(draft['blocking_reasons'])}")
    return 0 if draft["status"] == "needs_human_design_spec_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())

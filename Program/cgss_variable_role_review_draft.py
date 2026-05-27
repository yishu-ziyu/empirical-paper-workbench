from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_variable_role_review_draft import (  # noqa: E402
    DEFAULT_EVIDENCE_PACKAGE_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_VARIABLE_CANDIDATES_PATH,
    build_variable_role_review_draft,
    load_json,
    write_review_draft_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable CGSS variable-role draft.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--evidence-package", default=str(DEFAULT_EVIDENCE_PACKAGE_PATH))
    parser.add_argument("--variable-candidates", default=str(DEFAULT_VARIABLE_CANDIDATES_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    evidence_package = load_json(project_root / args.evidence_package)
    variable_candidates = load_json(project_root / args.variable_candidates)
    draft = build_variable_role_review_draft(
        evidence_package,
        variable_candidates,
        source_paths={
            "evidence_package": args.evidence_package,
            "variable_candidates": args.variable_candidates,
        },
    )
    result_path, review_path = write_review_draft_outputs(
        project_root,
        draft,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_variable_role_review_draft={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_variable_role_review_draft_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={draft['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(draft['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

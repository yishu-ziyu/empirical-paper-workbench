from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_literature_seed_package import (  # noqa: E402
    DEFAULT_EVIDENCE_PACKAGE_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_ROLE_REVIEW_DRAFT_PATH,
    build_literature_seed_package,
    load_json,
    write_literature_seed_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable CGSS literature seed package.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--role-review-draft", default=str(DEFAULT_ROLE_REVIEW_DRAFT_PATH))
    parser.add_argument("--evidence-package", default=str(DEFAULT_EVIDENCE_PACKAGE_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    role_review_draft = load_json(project_root / args.role_review_draft)
    evidence_package = load_json(project_root / args.evidence_package)
    package = build_literature_seed_package(
        role_review_draft,
        evidence_package,
        source_paths={
            "variable_role_review_draft": args.role_review_draft,
            "evidence_package": args.evidence_package,
        },
    )
    result_path, review_path = write_literature_seed_outputs(
        project_root,
        package,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_literature_seed_package={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_literature_seed_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={package['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(package['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

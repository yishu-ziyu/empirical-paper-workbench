from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_verified_bibliography_candidates import (  # noqa: E402
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SOURCE_PREFLIGHT_PATH,
    build_verified_bibliography_candidates,
    load_json,
    write_verified_bibliography_candidate_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build reviewable CGSS verified bibliography candidates.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--source-preflight", default=str(DEFAULT_SOURCE_PREFLIGHT_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    source_preflight = load_json(project_root / args.source_preflight)
    package = build_verified_bibliography_candidates(
        source_preflight,
        source_paths={"source_preflight": args.source_preflight},
    )
    result_path, review_path = write_verified_bibliography_candidate_outputs(
        project_root,
        package,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_verified_bibliography_candidates={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_verified_bibliography_candidates_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={package['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(package['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

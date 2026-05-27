from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_literature_source_verification_preflight import (  # noqa: E402
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SEED_PACKAGE_PATH,
    build_literature_source_verification_preflight,
    load_json,
    write_literature_source_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable CGSS literature source verification preflight.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--seed-package", default=str(DEFAULT_SEED_PACKAGE_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    seed_package = load_json(project_root / args.seed_package)
    preflight = build_literature_source_verification_preflight(
        seed_package,
        source_paths={"literature_seed_package": args.seed_package},
    )
    result_path, review_path = write_literature_source_preflight_outputs(
        project_root,
        preflight,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_literature_source_preflight={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_literature_source_preflight_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={preflight['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(preflight['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

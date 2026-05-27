from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_results_evidence_package import (  # noqa: E402
    DEFAULT_MINIMAL_MODEL_PATH,
    DEFAULT_ORDERED_ROBUSTNESS_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    build_results_evidence_package,
    load_json,
    write_evidence_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a CGSS writing-ready result evidence package.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--minimal-model", default=str(DEFAULT_MINIMAL_MODEL_PATH))
    parser.add_argument("--ordered-robustness", default=str(DEFAULT_ORDERED_ROBUSTNESS_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    minimal_model = load_json(project_root / args.minimal_model)
    ordered_robustness = load_json(project_root / args.ordered_robustness)
    package = build_results_evidence_package(
        minimal_model,
        ordered_robustness,
        source_paths={
            "minimal_model": args.minimal_model,
            "ordered_robustness": args.ordered_robustness,
        },
    )
    result_path, review_path = write_evidence_outputs(
        project_root,
        package,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_results_evidence_package={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_results_evidence_package_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={package['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(package['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

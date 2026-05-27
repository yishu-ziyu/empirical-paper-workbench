from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_run_plan_seed import (  # noqa: E402
    DEFAULT_DESIGN_DRAFT_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    build_cgss_run_plan_seed,
    load_json,
    write_cgss_run_plan_seed_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable CGSS RunPlan seed.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--design-draft", default=str(DEFAULT_DESIGN_DRAFT_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    design_draft = load_json(project_root / args.design_draft)
    report = build_cgss_run_plan_seed(
        design_draft,
        source_paths={"design_spec_draft": args.design_draft},
    )
    result_path, review_path = write_cgss_run_plan_seed_outputs(
        project_root,
        report,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_run_plan_seed={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_run_plan_seed_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(report['blocking_reasons'])}")
    return 0 if report["status"] == "needs_human_run_plan_seed_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())

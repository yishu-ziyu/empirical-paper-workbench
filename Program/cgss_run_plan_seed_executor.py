from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_run_plan_seed_executor import (  # noqa: E402
    DEFAULT_APPROVED_SEED_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_TOPIC,
    execute_approved_cgss_run_plan_seed,
    load_json_or_empty,
    write_cgss_run_plan_seed_execution_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute approved CGSS RunPlan seed in draft layer.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--approved-seed", default=str(DEFAULT_APPROVED_SEED_PATH))
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    approved_seed = load_json_or_empty(project_root / args.approved_seed)
    report = execute_approved_cgss_run_plan_seed(project_root, approved_seed, args.topic)
    result_path, review_path = write_cgss_run_plan_seed_execution_outputs(
        project_root,
        report,
        Path(args.output_result),
        Path(args.output_review),
    )

    print(f"[econ-workbench] cgss_run_plan_seed_execution={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_run_plan_seed_execution_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] ran_models={str(report['ran_models']).lower()}")
    if report.get("evidence_package"):
        print(f"[econ-workbench] evidence_status={report['evidence_package'].get('status', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_minimal_model import (  # noqa: E402
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    load_cgss_2023_frame,
    run_cgss_minimal_model,
    write_model_outputs,
)


DEFAULT_DATASET = Path(
    "/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/"
    "A004CGSS中国综合社会调查/中国综合社会调查2023/CGSS2023.dta"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a minimal CGSS social-capital/happiness model.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    dataset = Path(args.dataset)
    frame = load_cgss_2023_frame(dataset)
    report = run_cgss_minimal_model(frame, args.topic, str(dataset))
    result_path, review_path = write_model_outputs(
        project_root,
        report,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_minimal_model={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_minimal_model_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] nobs={report['sample']['nobs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

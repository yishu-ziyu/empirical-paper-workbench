from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_dataset_bound_variable_role_draft import (  # noqa: E402
    DEFAULT_DATA_DISCOVERY_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_VARIABLE_CANDIDATES_PATH,
    build_dataset_bound_variable_role_draft,
    load_json,
    write_dataset_bound_role_draft_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a DatasetBinding-constrained CGSS variable-role draft."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--data-discovery", default=str(DEFAULT_DATA_DISCOVERY_PATH))
    parser.add_argument("--variable-candidates", default=str(DEFAULT_VARIABLE_CANDIDATES_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    data_discovery_path = Path(args.data_discovery)
    variable_candidates_path = Path(args.variable_candidates)
    data_discovery = load_json(project_root / data_discovery_path)
    variable_candidates = load_json(project_root / variable_candidates_path)
    draft = build_dataset_bound_variable_role_draft(
        data_discovery=data_discovery,
        variable_candidates=variable_candidates,
        source_paths={
            "data_discovery": str(data_discovery_path),
            "variable_candidates": str(variable_candidates_path),
        },
    )
    result_path, review_path = write_dataset_bound_role_draft_outputs(
        project_root,
        draft,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] dataset_bound_variable_role_draft={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] dataset_bound_variable_role_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={draft['status']}")
    return 0 if draft["status"] == "needs_human_dataset_bound_role_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())

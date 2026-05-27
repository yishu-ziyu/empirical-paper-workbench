from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_acceptance_chain import (  # noqa: E402
    DEFAULT_DATASET_INDEX_PATH,
    DEFAULT_LEVEL3_GATE_PATH,
    DEFAULT_LITERATURE_SEED_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_acceptance_chain,
    load_json,
    write_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate Auto Mode acceptance readiness without formal writeback.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--dataset-index", default=str(DEFAULT_DATASET_INDEX_PATH))
    parser.add_argument("--literature-seed", default=str(DEFAULT_LITERATURE_SEED_PATH))
    parser.add_argument("--level3-gate", default=str(DEFAULT_LEVEL3_GATE_PATH))
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    dataset_index = load_json(project_root / args.dataset_index) if (project_root / args.dataset_index).exists() else {}
    literature_seed = load_json(project_root / args.literature_seed) if (project_root / args.literature_seed).exists() else {}
    level3_gate = load_json(project_root / args.level3_gate) if (project_root / args.level3_gate).exists() else {}
    report = build_auto_mode_acceptance_chain(
        dataset_index=dataset_index,
        literature_seed=literature_seed,
        level3_gate=level3_gate,
        source_paths={
            "dataset_index": str(Path(args.dataset_index)),
            "literature_seed": str(Path(args.literature_seed)),
            "level3_gate": str(Path(args.level3_gate)),
        },
    )
    report_path, review_path = write_report(
        project_root,
        report,
        Path(args.output_report),
        Path(args.output_review),
    )
    print(f"[econ-workbench] auto_mode_acceptance_chain={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_acceptance_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] package_readiness={report['package_readiness']}")
    return 0 if report["status"] in {"needs_auto_mode_repair", "needs_human_final_review"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

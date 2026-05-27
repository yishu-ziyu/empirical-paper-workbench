from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_data_discovery import (  # noqa: E402
    DEFAULT_DATA_ROOT,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    discover_cgss_data_assets,
    write_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan local CGSS assets and create a DatasetBinding draft.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--topic", required=True)
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    report = discover_cgss_data_assets(Path(args.data_root), args.topic)
    report_path, review_path = write_report(
        project_root,
        report,
        Path(args.output_report),
        Path(args.output_review),
    )
    recommended = report["dataset_binding_draft"].get("recommended_dataset") or {}
    print(f"[econ-workbench] cgss_data_discovery={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_data_discovery_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    if recommended:
        print(f"[econ-workbench] recommended_dataset={recommended.get('year')} {recommended.get('path')}")
    return 0 if report["status"] == "needs_human_dataset_binding_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())

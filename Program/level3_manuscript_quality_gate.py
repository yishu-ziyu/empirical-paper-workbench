from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.level3_manuscript_quality_gate import (  # noqa: E402
    DEFAULT_MANIFEST_PATH,
    DEFAULT_PAPER_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_level3_quality_gate,
    load_json,
    write_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Level 3 manuscript quality gate without formal writeback.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--paper", default=str(DEFAULT_PAPER_PATH))
    parser.add_argument("--package-manifest", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    paper_path = project_root / args.paper
    manifest_path = project_root / args.package_manifest
    paper_text = paper_path.read_text(encoding="utf-8")
    package_manifest = load_json(manifest_path) if manifest_path.exists() else {}
    report = build_level3_quality_gate(
        paper_text=paper_text,
        package_manifest=package_manifest,
        source_paths={"paper": str(Path(args.paper)), "package_manifest": str(Path(args.package_manifest))},
    )
    report_path, review_path = write_report(
        project_root,
        report,
        Path(args.output_report),
        Path(args.output_review),
    )
    print(f"[econ-workbench] level3_quality_gate={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] level3_quality_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] gate_status={report['gate_status']}")
    return 0 if report["status"] == "needs_human_level3_quality_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())

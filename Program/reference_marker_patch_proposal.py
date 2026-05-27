from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.reference_marker_patch_proposal import (  # noqa: E402
    DEFAULT_CANDIDATE_PAPER_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SOURCE_PAPER_PATH,
    build_reference_marker_patch,
    write_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose candidate-reference human-review markers without source paper overwrite.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--source-paper", default=str(DEFAULT_SOURCE_PAPER_PATH))
    parser.add_argument("--candidate-paper", default=str(DEFAULT_CANDIDATE_PAPER_PATH))
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    source_paper_path = project_root / args.source_paper
    paper_text = source_paper_path.read_text(encoding="utf-8")
    patch = build_reference_marker_patch(
        paper_text=paper_text,
        source_path=str(Path(args.source_paper)),
    )
    report_path, review_path, candidate_path = write_outputs(
        project_root=project_root,
        patch=patch,
        report_path=Path(args.output_report),
        review_path=Path(args.output_review),
        candidate_paper_path=Path(args.candidate_paper),
    )
    print(f"[econ-workbench] reference_marker_patch={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] reference_marker_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] reference_marked_candidate={candidate_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={patch['status']}")
    print(f"[econ-workbench] changed_references={len(patch['changed_references'])}")
    return 0 if patch["status"] in {"needs_human_reference_marker_review", "no_reference_marker_patch_needed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

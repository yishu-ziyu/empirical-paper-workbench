from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_literature_review_draft_packet import (  # noqa: E402
    DEFAULT_BIBLIOGRAPHY_CANDIDATES_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    build_literature_review_draft_packet,
    load_json,
    write_literature_review_draft_packet_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable CGSS literature review draft packet.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--bibliography-candidates", default=str(DEFAULT_BIBLIOGRAPHY_CANDIDATES_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    bibliography_candidates = load_json(project_root / args.bibliography_candidates)
    packet = build_literature_review_draft_packet(
        bibliography_candidates,
        source_paths={"bibliography_candidates": args.bibliography_candidates},
    )
    result_path, review_path = write_literature_review_draft_packet_outputs(
        project_root,
        packet,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_literature_review_draft_packet={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_literature_review_draft_packet_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={packet['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(packet['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_exploratory_paper_assembler import (  # noqa: E402
    DEFAULT_LITERATURE_PACKET_PATH,
    DEFAULT_PAPER_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_RESULTS_EVIDENCE_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SECTION_PACKAGE_PATH,
    build_cgss_exploratory_paper_package,
    load_json_or_empty,
    write_cgss_exploratory_paper_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble CGSS manuscript sections into a reviewable exploratory paper.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--section-package", default=str(DEFAULT_SECTION_PACKAGE_PATH))
    parser.add_argument("--results-evidence", default=str(DEFAULT_RESULTS_EVIDENCE_PATH))
    parser.add_argument("--literature-packet", default=str(DEFAULT_LITERATURE_PACKET_PATH))
    parser.add_argument("--output-paper", default=str(DEFAULT_PAPER_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    section_package = load_json_or_empty(project_root / args.section_package)
    results_evidence = load_json_or_empty(project_root / args.results_evidence)
    literature_packet = load_json_or_empty(project_root / args.literature_packet)

    package = build_cgss_exploratory_paper_package(
        section_package,
        results_evidence,
        literature_packet,
        {
            "manuscript_sections": args.section_package,
            "results_evidence_package": args.results_evidence,
            "literature_review_draft_packet": args.literature_packet,
        },
    )
    paper_path, result_path, review_path = write_cgss_exploratory_paper_outputs(
        project_root,
        package,
        Path(args.output_paper),
        Path(args.output_result),
        Path(args.output_review),
    )

    print(f"[econ-workbench] cgss_exploratory_paper={paper_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_exploratory_paper_assembly={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_exploratory_paper_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={package['status']}")
    print(f"[econ-workbench] chinese_characters={package.get('paper_metrics', {}).get('chinese_characters', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

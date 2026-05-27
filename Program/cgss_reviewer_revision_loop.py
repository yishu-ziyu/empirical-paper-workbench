from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_reviewer_revision_loop import (  # noqa: E402
    DEFAULT_LITERATURE_PACKET_PATH,
    DEFAULT_METHOD_GATE_PATH,
    DEFAULT_PAPER_ASSEMBLY_PATH,
    DEFAULT_PAPER_PATH,
    DEFAULT_PAPER_REV1_PATH,
    DEFAULT_RESULTS_EVIDENCE_PATH,
    DEFAULT_REVIEWER_REPORT_PATH,
    DEFAULT_REVISION_TASK_QUEUE_PATH,
    build_cgss_reviewer_revision_loop,
    load_json_or_empty,
    load_text_or_empty,
    write_cgss_reviewer_revision_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a CGSS reviewer-style revision loop.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--paper", default=str(DEFAULT_PAPER_PATH))
    parser.add_argument("--paper-assembly", default=str(DEFAULT_PAPER_ASSEMBLY_PATH))
    parser.add_argument("--method-gate", default=str(DEFAULT_METHOD_GATE_PATH))
    parser.add_argument("--results-evidence", default=str(DEFAULT_RESULTS_EVIDENCE_PATH))
    parser.add_argument("--literature-packet", default=str(DEFAULT_LITERATURE_PACKET_PATH))
    parser.add_argument("--output-reviewer-report", default=str(DEFAULT_REVIEWER_REPORT_PATH))
    parser.add_argument("--output-revision-queue", default=str(DEFAULT_REVISION_TASK_QUEUE_PATH))
    parser.add_argument("--output-paper-rev1", default=str(DEFAULT_PAPER_REV1_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    loop = build_cgss_reviewer_revision_loop(
        paper_markdown=load_text_or_empty(project_root / args.paper),
        paper_assembly=load_json_or_empty(project_root / args.paper_assembly),
        method_gate=load_json_or_empty(project_root / args.method_gate),
        results_evidence=load_json_or_empty(project_root / args.results_evidence),
        literature_packet=load_json_or_empty(project_root / args.literature_packet),
        source_paths={
            "paper": args.paper,
            "paper_assembly": args.paper_assembly,
            "method_gate": args.method_gate,
            "results_evidence": args.results_evidence,
            "literature_packet": args.literature_packet,
        },
    )
    paths = write_cgss_reviewer_revision_outputs(
        project_root,
        loop,
        Path(args.output_reviewer_report),
        Path(args.output_revision_queue),
        Path(args.output_paper_rev1),
    )
    print(f"[econ-workbench] cgss_reviewer_report={paths['reviewer_report'].relative_to(project_root)}")
    print(f"[econ-workbench] cgss_revision_task_queue={paths['revision_task_queue'].relative_to(project_root)}")
    print(f"[econ-workbench] cgss_paper_rev1={paths['paper_rev1'].relative_to(project_root)}")
    print(f"[econ-workbench] status={loop['status']}")
    print(f"[econ-workbench] tasks={len(loop.get('revision_task_queue', {}).get('tasks', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_method_gate import (  # noqa: E402
    DEFAULT_EVIDENCE_PACKAGE_PATH,
    DEFAULT_LITERATURE_PACKET_PATH,
    DEFAULT_PAPER_ASSEMBLY_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    build_cgss_method_gate,
    load_json_or_empty,
    write_cgss_method_gate_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable CGSS AER-like method gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--profile", choices=["working_paper", "aer_like"], default="working_paper")
    parser.add_argument("--evidence-package", default=str(DEFAULT_EVIDENCE_PACKAGE_PATH))
    parser.add_argument("--literature-packet", default=str(DEFAULT_LITERATURE_PACKET_PATH))
    parser.add_argument("--paper-assembly", default=str(DEFAULT_PAPER_ASSEMBLY_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    evidence_package = load_json_or_empty(project_root / args.evidence_package)
    literature_packet = load_json_or_empty(project_root / args.literature_packet)
    paper_assembly = load_json_or_empty(project_root / args.paper_assembly)
    gate = build_cgss_method_gate(
        evidence_package,
        literature_packet,
        paper_assembly,
        profile=args.profile,
        source_paths={
            "evidence_package": args.evidence_package,
            "literature_packet": args.literature_packet,
            "paper_assembly": args.paper_assembly,
        },
    )
    result_path, review_path = write_cgss_method_gate_outputs(
        project_root,
        gate,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_method_gate={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_method_gate_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={gate['status']}")
    print(f"[econ-workbench] gate_status={gate['gate_status']}")
    print(f"[econ-workbench] required={gate['gate_enforcement']['required']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

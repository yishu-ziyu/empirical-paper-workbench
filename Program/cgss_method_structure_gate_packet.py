from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_method_structure_gate_packet import (  # noqa: E402
    DEFAULT_EVIDENCE_PACKAGE_PATH,
    DEFAULT_LITERATURE_PACKET_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    build_method_structure_gate_packet,
    load_json,
    write_method_structure_gate_packet_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewable CGSS method and paper structure gate packet.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--evidence-package", default=str(DEFAULT_EVIDENCE_PACKAGE_PATH))
    parser.add_argument("--literature-packet", default=str(DEFAULT_LITERATURE_PACKET_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    evidence_package = load_json(project_root / args.evidence_package)
    literature_packet = load_json(project_root / args.literature_packet)
    packet = build_method_structure_gate_packet(
        evidence_package,
        literature_packet,
        source_paths={
            "evidence_package": args.evidence_package,
            "literature_packet": args.literature_packet,
        },
    )
    result_path, review_path = write_method_structure_gate_packet_outputs(
        project_root,
        packet,
        Path(args.output_result),
        Path(args.output_review),
    )
    print(f"[econ-workbench] cgss_method_structure_gate_packet={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_method_structure_gate_packet_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={packet['status']}")
    print(f"[econ-workbench] blocking_reasons={','.join(packet['blocking_reasons'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_final_review_packet import (  # noqa: E402
    DEFAULT_ACCEPTANCE_CHAIN_PATH,
    DEFAULT_DECISION_PATH,
    DEFAULT_DECISION_REVIEW_PATH,
    DEFAULT_PACKAGE_MANIFEST_PATH,
    DEFAULT_PACKET_PATH,
    DEFAULT_PACKET_REVIEW_PATH,
    build_auto_mode_final_review_decision,
    build_auto_mode_final_review_packet,
    load_json_or_empty,
    write_auto_mode_final_review_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and route an Auto Mode final review packet.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--acceptance-chain", default=str(DEFAULT_ACCEPTANCE_CHAIN_PATH))
    parser.add_argument("--package-manifest", default=str(DEFAULT_PACKAGE_MANIFEST_PATH))
    parser.add_argument("--decision", default="defer", choices=["defer", "approve", "revise", "reject"])
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-packet", default=str(DEFAULT_PACKET_PATH))
    parser.add_argument("--output-packet-review", default=str(DEFAULT_PACKET_REVIEW_PATH))
    parser.add_argument("--output-decision", default=str(DEFAULT_DECISION_PATH))
    parser.add_argument("--output-decision-review", default=str(DEFAULT_DECISION_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    acceptance_chain = load_json_or_empty(project_root / args.acceptance_chain)
    package_manifest = load_json_or_empty(project_root / args.package_manifest)
    packet = build_auto_mode_final_review_packet(
        acceptance_chain,
        package_manifest,
        source_paths={
            "acceptance_chain": str(Path(args.acceptance_chain)),
            "package_manifest": str(Path(args.package_manifest)),
        },
    )
    decision = build_auto_mode_final_review_decision(
        packet,
        decision=args.decision,
        reviewer=args.reviewer,
        note=args.note,
    )
    packet_path, packet_review_path, decision_path, decision_review_path = write_auto_mode_final_review_outputs(
        project_root,
        packet,
        decision,
        Path(args.output_packet),
        Path(args.output_packet_review),
        Path(args.output_decision),
        Path(args.output_decision_review),
    )
    print(f"[econ-workbench] auto_mode_final_review_packet={packet_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_final_review_packet_review={packet_review_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_final_review_decision={decision_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_final_review_decision_review={decision_review_path.relative_to(project_root)}")
    print(f"[econ-workbench] packet_status={packet['status']}")
    print(f"[econ-workbench] decision_status={decision['status']}")
    print(f"[econ-workbench] decision_route={decision['route']}")
    print(f"[econ-workbench] formal_writeback_allowed={str(decision['formal_writeback_allowed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(decision['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

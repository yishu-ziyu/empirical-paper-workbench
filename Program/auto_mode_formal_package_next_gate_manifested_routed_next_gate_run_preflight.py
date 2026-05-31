from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight import (  # noqa: E402
    DEFAULT_ENTRY_MANIFEST_PATH,
    DEFAULT_EXPLICIT_ENTRY_GATE_PATH,
    DEFAULT_RUN_PREFLIGHT_PATH,
    DEFAULT_RUN_PREFLIGHT_REVIEW_PATH,
    build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight a manifested routed next-gate run from P7-BB and the entry manifest."
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument(
        "--explicit-routed-next-gate-entry-gate",
        default=str(DEFAULT_EXPLICIT_ENTRY_GATE_PATH),
    )
    parser.add_argument("--routed-next-gate-entry-manifest", default=str(DEFAULT_ENTRY_MANIFEST_PATH))
    parser.add_argument("--output-preflight", default=str(DEFAULT_RUN_PREFLIGHT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_RUN_PREFLIGHT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    gate_path = Path(args.explicit_routed_next_gate_entry_gate)
    manifest_path = Path(args.routed_next_gate_entry_manifest)
    gate = load_json_or_empty(project_root / gate_path)
    manifest = load_json_or_empty(project_root / manifest_path)
    report = build_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight(
        gate,
        manifest,
        source_paths={
            "explicit_routed_next_gate_entry_gate": str(gate_path),
            "routed_next_gate_entry_manifest": str(manifest_path),
        },
    )
    report_path, review_path = (
        write_auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight_outputs(
            project_root,
            report,
            Path(args.output_preflight),
            Path(args.output_review),
        )
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_manifested_routed_next_gate_run_preflight_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "can_request_manifested_next_gate_command_execution="
        f"{str(report['can_request_manifested_next_gate_command_execution']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"next_gate_command_call_plan={report['next_gate_command_call_plan_count']}"
    )
    print(
        "[econ-workbench] "
        "manifested_routed_next_gate_run_input_records="
        f"{report['manifested_routed_next_gate_run_input_record_count']}"
    )
    print(f"[econ-workbench] next_gate_command_executed={str(report['next_gate_command_executed']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

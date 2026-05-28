from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_routed_next_gate_entry_execute import (  # noqa: E402
    DEFAULT_ENTRY_MANIFEST_PATH,
    DEFAULT_EXECUTE_PATH,
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_REVIEW_PATH,
    VALID_MODES,
    build_auto_mode_formal_package_routed_next_gate_entry_execute,
    load_json_or_empty,
    write_auto_mode_formal_package_routed_next_gate_entry_execute_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Auto Mode routed next-gate entry execute gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--routed-next-gate-entry-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--mode", choices=sorted(VALID_MODES), default="dry-run")
    parser.add_argument("--confirm-entry", action="store_true")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--output-execute", default=str(DEFAULT_EXECUTE_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    parser.add_argument("--entry-manifest", default=str(DEFAULT_ENTRY_MANIFEST_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preflight_path = Path(args.routed_next_gate_entry_preflight)
    preflight = load_json_or_empty(project_root / preflight_path)
    report = build_auto_mode_formal_package_routed_next_gate_entry_execute(
        preflight,
        mode=args.mode,
        confirm_entry=args.confirm_entry,
        reviewer=args.reviewer,
        note=args.note,
        entry_manifest_path=Path(args.entry_manifest),
        source_paths={
            "routed_next_gate_entry_preflight": str(preflight_path),
        },
    )
    report_path, review_path, manifest_path = write_auto_mode_formal_package_routed_next_gate_entry_execute_outputs(
        project_root,
        report,
        Path(args.output_execute),
        Path(args.output_review),
        Path(args.entry_manifest),
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_routed_next_gate_entry_execute={report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        f"auto_mode_formal_package_routed_next_gate_entry_execute_review={review_path.relative_to(project_root)}"
    )
    if manifest_path is not None:
        print(
            "[econ-workbench] "
            f"auto_mode_formal_package_routed_next_gate_entry_manifest={manifest_path.relative_to(project_root)}"
        )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] mode={report['mode']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "can_enter_routed_next_gate_with_confirmation="
        f"{str(report['can_enter_routed_next_gate_with_confirmation']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"routed_next_gate_entry_manifest_recorded="
        f"{str(report['routed_next_gate_entry_manifest_recorded']).lower()}"
    )
    print(
        "[econ-workbench] "
        f"routed_next_gate_entry_operations={len(report['routed_next_gate_entry_operations'])}"
    )
    print(f"[econ-workbench] next_gate_entered={str(report['next_gate_entered']).lower()}")
    print(f"[econ-workbench] next_gate_command_executed={str(report['next_gate_command_executed']).lower()}")
    print(f"[econ-workbench] export_or_acceptance_executed={str(report['export_or_acceptance_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

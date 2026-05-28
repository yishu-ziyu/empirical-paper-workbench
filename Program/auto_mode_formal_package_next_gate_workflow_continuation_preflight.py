from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_package_next_gate_workflow_continuation_preflight import (  # noqa: E402
    DEFAULT_PREFLIGHT_PATH,
    DEFAULT_RESULT_REVIEW_PATH,
    DEFAULT_REVIEW_PATH,
    build_auto_mode_formal_package_next_gate_workflow_continuation_preflight,
    load_json_or_empty,
    write_auto_mode_formal_package_next_gate_workflow_continuation_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare next-gate workflow continuation preflight.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifested-next-gate-command-result-review", default=str(DEFAULT_RESULT_REVIEW_PATH))
    parser.add_argument("--output-preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    result_review_path = Path(args.manifested_next_gate_command_result_review)
    result_review = load_json_or_empty(project_root / result_review_path)
    report = build_auto_mode_formal_package_next_gate_workflow_continuation_preflight(
        result_review,
        source_paths={
            "manifested_next_gate_command_result_review": str(result_review_path),
        },
    )
    report_path, review_path = write_auto_mode_formal_package_next_gate_workflow_continuation_preflight_outputs(
        project_root,
        report,
        Path(args.output_preflight),
        Path(args.output_review),
    )

    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_workflow_continuation_preflight="
        f"{report_path.relative_to(project_root)}"
    )
    print(
        "[econ-workbench] "
        "auto_mode_formal_package_next_gate_workflow_continuation_preflight_review="
        f"{review_path.relative_to(project_root)}"
    )
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_route_type={report['verified_route_type']}")
    print(f"[econ-workbench] routed_next_gate={report['routed_next_gate']}")
    print(
        "[econ-workbench] "
        "can_request_next_gate_workflow_continuation="
        f"{str(report['can_request_next_gate_workflow_continuation']).lower()}"
    )
    print(
        "[econ-workbench] "
        "requires_explicit_workflow_continuation_command="
        f"{str(report['requires_explicit_workflow_continuation_command']).lower()}"
    )
    print(f"[econ-workbench] workflow_continuation_plan={len(report['workflow_continuation_plan'])}")
    print(f"[econ-workbench] workflow_continuation_executed={str(report['workflow_continuation_executed']).lower()}")
    print(f"[econ-workbench] this_command_ran_continuation={str(report['this_command_ran_continuation']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

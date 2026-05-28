from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.auto_mode_formal_target_adapter_readiness import (  # noqa: E402
    DEFAULT_APPLY_MANIFEST_PATH,
    DEFAULT_PACKAGE_MANIFEST_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_TARGET_ROOT,
    build_auto_mode_formal_target_adapter_readiness,
    load_json_or_empty,
    write_auto_mode_formal_target_adapter_readiness_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Auto Mode formal target adapter readiness mapping.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--apply-manifest", default=str(DEFAULT_APPLY_MANIFEST_PATH))
    parser.add_argument("--package-manifest", default=str(DEFAULT_PACKAGE_MANIFEST_PATH))
    parser.add_argument("--target-root", default=str(DEFAULT_TARGET_ROOT))
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    apply_manifest = load_json_or_empty(project_root / args.apply_manifest)
    package_manifest = load_json_or_empty(project_root / args.package_manifest)
    report = build_auto_mode_formal_target_adapter_readiness(
        project_root,
        apply_manifest,
        package_manifest,
        target_root=Path(args.target_root),
        source_paths={
            "apply_manifest": str(Path(args.apply_manifest)),
            "package_manifest": str(Path(args.package_manifest)),
        },
    )
    report_path, review_path = write_auto_mode_formal_target_adapter_readiness_outputs(
        project_root,
        report,
        Path(args.output_report),
        Path(args.output_review),
    )
    print(f"[econ-workbench] auto_mode_formal_target_adapter_readiness={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] auto_mode_formal_target_adapter_readiness_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] adapter_mappings={len(report['adapter_mappings'])}")
    print(
        "[econ-workbench] can_request_target_adapter_execution="
        f"{str(report['can_request_target_adapter_execution']).lower()}"
    )
    print(
        "[econ-workbench] formal_target_adapters_executed="
        f"{str(report['formal_target_adapters_executed']).lower()}"
    )
    print(f"[econ-workbench] formal_writeback_executed={str(report['formal_writeback_executed']).lower()}")
    print(f"[econ-workbench] this_command_wrote_formal_state={str(report['this_command_wrote_formal_state']).lower()}")
    print(f"[econ-workbench] can_write_product_state={str(report['can_write_product_state']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

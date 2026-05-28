from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.statistical_adapter_contract import (  # noqa: E402
    DEFAULT_CGSS_RESULTS_EVIDENCE_PATH,
    DEFAULT_METHOD_EXECUTION_PATH,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    build_statistical_adapter_contract,
    load_json_or_empty,
    write_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize statistical execution artifacts into an Auto Mode adapter contract.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--method-execution", default=str(DEFAULT_METHOD_EXECUTION_PATH))
    parser.add_argument("--cgss-results-evidence", default=str(DEFAULT_CGSS_RESULTS_EVIDENCE_PATH))
    parser.add_argument("--output-report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    method_execution_path = project_root / args.method_execution
    cgss_results_path = project_root / args.cgss_results_evidence
    contract = build_statistical_adapter_contract(
        method_execution=load_json_or_empty(method_execution_path),
        cgss_results_evidence=load_json_or_empty(cgss_results_path),
        source_paths={
            "method_execution": str(Path(args.method_execution)),
            "cgss_results_evidence": str(Path(args.cgss_results_evidence)),
        },
    )
    report_path, review_path = write_outputs(
        project_root,
        contract,
        Path(args.output_report),
        Path(args.output_review),
    )
    print(f"[econ-workbench] statistical_adapter_contract={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] statistical_adapter_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={contract['status']}")
    print(f"[econ-workbench] normalized_results={len(contract['normalized_results'])}")
    return 0 if contract["status"] != "blocked_missing_statistical_sources" else 2


if __name__ == "__main__":
    raise SystemExit(main())

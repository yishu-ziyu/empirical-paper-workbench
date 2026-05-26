from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from workbench.method_diagnostics import build_method_diagnostics_report, write_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run review-gated empirical method diagnostics.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--output-report",
        default="Results/json/method_diagnostics_report.json",
        help="Method diagnostics report JSON path relative to project root.",
    )
    parser.add_argument(
        "--profile",
        choices=["general_working_paper", "aer_like"],
        default="aer_like",
        help="Method diagnostics profile.",
    )
    parser.add_argument("--max-leave-one-out", type=int, default=10, help="Maximum leave-one-out units to summarize.")
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def fail(code: str, message: str) -> int:
    print(json.dumps({"error": {"code": code, "message": message}}, ensure_ascii=False), file=sys.stderr)
    return 1


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    output_report = resolve_path(project_root, args.output_report)

    try:
        report = build_method_diagnostics_report(project_root, profile=args.profile, max_leave_one_out=args.max_leave_one_out)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return fail("method_diagnostics_failed", str(exc))

    report_path = write_json(output_report, report)
    print(f"[econ-workbench] method_diagnostics_report={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] method_family={report.get('method_family')}")
    print(f"[econ-workbench] method_subtype={report.get('method_subtype')}")
    print(f"[econ-workbench] status={report.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

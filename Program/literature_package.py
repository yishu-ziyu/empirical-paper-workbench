from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from workbench.literature_package import build_literature_package, write_literature_package  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a review-gated literature package for the paper workflow.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--output-dir",
        default="Data/literature/processed",
        help="Processed literature directory relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default="Results/json/literature_package_report.json",
        help="Report JSON path relative to project root.",
    )
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
    output_dir = resolve_path(project_root, args.output_dir)
    output_report = resolve_path(project_root, args.output_report)

    try:
        report, candidate_rows, verified_rows, matrix_md = build_literature_package(project_root)
        paths = write_literature_package(project_root, report, candidate_rows, verified_rows, matrix_md, output_dir, output_report)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return fail("literature_package_failed", str(exc))

    print(f"[econ-workbench] candidate_literature={paths['candidate_literature'].relative_to(project_root)}")
    print(f"[econ-workbench] verified_bibliography={paths['verified_bibliography'].relative_to(project_root)}")
    print(f"[econ-workbench] contribution_matrix={paths['contribution_matrix'].relative_to(project_root)}")
    print(f"[econ-workbench] literature_package_report={paths['literature_package_report'].relative_to(project_root)}")
    print(f"[econ-workbench] status={report['status']}")
    print(f"[econ-workbench] verified_count={report['counts']['verified_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

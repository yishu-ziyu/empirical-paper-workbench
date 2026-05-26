from __future__ import annotations

import argparse
from pathlib import Path

from workbench.formal_manuscript_source_assembly import (
    DEFAULT_PACKAGE_ROOT,
    DEFAULT_REPORT_PATH,
    DEFAULT_REVIEW_PATH,
    DEFAULT_SOURCE_MANIFEST,
    build_formal_manuscript_source_map,
    load_json,
    snapshot_formal_state,
    write_formal_manuscript_source_map_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble P5 formal manuscript source placeholders.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--source-manifest",
        default=DEFAULT_SOURCE_MANIFEST,
        help="P5-B formal package manifest path relative to project root.",
    )
    parser.add_argument(
        "--output-report",
        default=DEFAULT_REPORT_PATH,
        help="Output formal manuscript source map JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-review",
        default=DEFAULT_REVIEW_PATH,
        help="Output formal manuscript source review Markdown path relative to project root.",
    )
    parser.add_argument(
        "--package-root",
        default=DEFAULT_PACKAGE_ROOT,
        help="Formal package root directory relative to project root.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    source_manifest_path = resolve_path(project_root, args.source_manifest)
    output_report_path = resolve_path(project_root, args.output_report)
    output_review_path = resolve_path(project_root, args.output_review)
    package_root = resolve_path(project_root, args.package_root)

    if not source_manifest_path.exists():
        raise FileNotFoundError(f"Formal package manifest not found: {args.source_manifest}")

    formal_state_before = snapshot_formal_state(project_root)
    report = build_formal_manuscript_source_map(
        project_root,
        load_json(source_manifest_path),
        source_manifest_path,
        package_root,
        formal_state_before=formal_state_before,
    )
    report_path, review_path = write_formal_manuscript_source_map_outputs(
        output_report_path,
        output_review_path,
        report,
    )

    print(f"[econ-workbench] formal_manuscript_source_map={report_path.relative_to(project_root)}")
    print(f"[econ-workbench] formal_manuscript_source_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] section_sources={report.get('section_sources_path')}")
    print(f"[econ-workbench] status={report.get('status')}")
    print(f"[econ-workbench] can_prepare_pdf_preflight={str(report.get('can_prepare_pdf_preflight')).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

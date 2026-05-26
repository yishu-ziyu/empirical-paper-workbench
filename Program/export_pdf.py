from __future__ import annotations

import argparse
from pathlib import Path

from workbench.export import (
    build_pdf_export_manifest,
    pdf_export_preflight,
    run_export_command,
    write_manifest,
    write_pdf_full_chain_reproduce_script,
    write_pdf_reproduce_script,
    write_pdf_review_doc,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export generated Quarto draft to PDF.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--source",
        default="Manuscripts/generated/paper_draft.qmd",
        help="QMD source path relative to project root.",
    )
    parser.add_argument(
        "--output",
        default="Submissions/paper_draft.pdf",
        help="PDF output path relative to project root.",
    )
    parser.add_argument(
        "--manifest",
        default="Submissions/pdf_export_manifest.json",
        help="PDF export manifest path relative to project root.",
    )
    parser.add_argument(
        "--review-doc",
        default="Submissions/pdf_first_review.md",
        help="Markdown review document path relative to project root.",
    )
    parser.add_argument(
        "--reproduce-script",
        default="Submissions/reproduce_pdf_first.sh",
        help="Shell script path for rerunning the PDF export.",
    )
    parser.add_argument(
        "--paper-config",
        default=None,
        help="Paper config path relative to project root. When provided, a full-chain reproduce script can be written.",
    )
    parser.add_argument(
        "--full-reproduce-script",
        default=None,
        help="Shell script path for rerunning run_paper.py and then PDF export.",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Only write export manifest and skip rendering.",
    )
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (project_root / path).resolve()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    source = resolve_path(project_root, args.source)
    output = resolve_path(project_root, args.output)
    manifest_path = resolve_path(project_root, args.manifest)
    review_doc = resolve_path(project_root, args.review_doc)
    reproduce_script = resolve_path(project_root, args.reproduce_script)
    paper_config = resolve_path(project_root, args.paper_config) if args.paper_config else None
    full_reproduce_script = (
        resolve_path(project_root, args.full_reproduce_script) if args.full_reproduce_script else None
    )
    log_path = project_root / "Results" / "logs" / "export_pdf.log"

    command = [
        "quarto",
        "render",
        str(source),
        "--to",
        "pdf",
        "--output",
        output.name,
    ]
    preflight = pdf_export_preflight(project_root, source, output)
    manifest = build_pdf_export_manifest(
        project_root=project_root,
        source_qmd=source,
        output_pdf=output,
        command=command,
        preflight=preflight,
        log_path=log_path,
        review_doc=review_doc,
        reproduce_script=reproduce_script,
        full_reproduce_script=full_reproduce_script,
    )
    write_manifest(manifest_path, manifest)
    write_pdf_reproduce_script(reproduce_script, project_root, source, output, manifest_path, review_doc)
    if paper_config is not None and full_reproduce_script is not None:
        write_pdf_full_chain_reproduce_script(
            full_reproduce_script,
            project_root,
            paper_config,
            source,
            output,
            manifest_path,
            review_doc,
            reproduce_script,
            full_reproduce_script,
        )
    write_pdf_review_doc(
        review_doc,
        project_root,
        source,
        output,
        manifest_path,
        log_path,
        reproduce_script,
        full_reproduce_script,
        preflight,
        manifest,
    )

    if preflight["status"] != "ready":
        print(f"[econ-workbench] pdf_preflight={preflight['status']}")
        print(f"[econ-workbench] manifest={manifest_path.relative_to(project_root)}")
        return 2
    if args.preflight_only:
        print("[econ-workbench] pdf_preflight=ready")
        print(f"[econ-workbench] manifest={manifest_path.relative_to(project_root)}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    result = run_export_command(command, log_path, cwd=output.parent)
    manifest = build_pdf_export_manifest(
        project_root=project_root,
        source_qmd=source,
        output_pdf=output,
        command=command,
        preflight=preflight,
        log_path=log_path,
        review_doc=review_doc,
        reproduce_script=reproduce_script,
        full_reproduce_script=full_reproduce_script,
    )
    write_manifest(manifest_path, manifest)
    if result.returncode != 0:
        return result.returncode

    print(f"[econ-workbench] exported={output.relative_to(project_root)}")
    print(f"[econ-workbench] manifest={manifest_path.relative_to(project_root)}")
    print(f"[econ-workbench] log={log_path.relative_to(project_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

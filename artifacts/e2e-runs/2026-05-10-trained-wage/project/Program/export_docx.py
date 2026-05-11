from __future__ import annotations

import argparse
from pathlib import Path

from workbench.export import build_export_manifest, run_pandoc, write_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export generated Markdown draft to docx.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--source",
        default="Manuscripts/generated/paper_draft.md",
        help="Markdown source path relative to project root.",
    )
    parser.add_argument(
        "--output",
        default="Submissions/paper_draft.docx",
        help="docx output path relative to project root.",
    )
    parser.add_argument(
        "--reference-doc",
        default="Manuscripts/templates/reference.docx",
        help="Optional reference doc path relative to project root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    source = project_root / args.source
    output = project_root / args.output
    reference_doc = project_root / args.reference_doc
    log_path = project_root / "Results" / "logs" / "export_docx.log"
    manifest_path = project_root / "Submissions" / "export_manifest.json"

    if not source.exists():
        raise SystemExit(f"Missing Markdown source: {source}")

    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "pandoc",
        str(source),
        "-o",
        str(output),
        "--citeproc",
        "--bibliography",
        str(project_root / "Manuscripts" / "references.bib"),
    ]
    reference_arg = reference_doc if reference_doc.exists() else None
    if reference_arg is not None:
        command.extend(["--reference-doc", str(reference_arg)])

    result = run_pandoc(command, log_path)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    manifest = build_export_manifest(
        project_root=project_root,
        markdown_path=source,
        docx_path=output,
        reference_doc=reference_arg,
        command=command,
    )
    write_manifest(manifest_path, manifest)

    print(f"[econ-workbench] exported={output.relative_to(project_root)}")
    print(f"[econ-workbench] manifest={manifest_path.relative_to(project_root)}")
    print(f"[econ-workbench] log={log_path.relative_to(project_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


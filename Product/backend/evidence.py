from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


DATA_SUFFIXES = {".dta", ".csv", ".xlsx", ".xls", ".sav", ".parquet", ".feather"}
LITERATURE_SUFFIXES = {".pdf", ".bib", ".md", ".txt", ".ris"}
CODE_SUFFIXES = {".py", ".do", ".R", ".r", ".jl"}
RESULT_SUFFIXES = {".json", ".md", ".txt", ".csv", ".rtf", ".png", ".jpg", ".jpeg", ".pdf", ".docx"}


def file_record(path: Path, base: Path, include_hash: bool = False) -> dict[str, Any]:
    stat = path.stat()
    record: dict[str, Any] = {
        "name": path.name,
        "path": str(path.relative_to(base)),
        "suffix": path.suffix.lower(),
        "size": stat.st_size,
    }
    if include_hash and stat.st_size <= 20_000_000:
        record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return record


def scan_files(root: Path, rel: str, suffixes: set[str], include_hash: bool = False) -> list[dict[str, Any]]:
    start = root / rel
    if not start.exists():
        return []
    return [
        file_record(path, root, include_hash=include_hash)
        for path in sorted(start.rglob("*"))
        if path.is_file() and path.suffix.lower() in suffixes
    ]


def build_evidence_inventory(project_root: Path, profile: dict[str, Any]) -> dict[str, Any]:
    paths = profile["paths"]
    root = project_root.resolve()
    manuscript_sections = scan_files(root, str(Path(paths["manuscript"]) / "sections_v21"), {".md"})
    if not manuscript_sections:
        manuscript_sections = scan_files(root, paths["manuscript"], {".md"})
    return {
        "project_root": str(root),
        "layout": profile["layout"],
        "datasets": scan_files(root, paths["data"], DATA_SUFFIXES),
        "code_files": scan_files(root, paths["code"], CODE_SUFFIXES),
        "results_files": scan_files(root, paths["results"], RESULT_SUFFIXES),
        "literature_files": scan_files(root, paths["literature"], LITERATURE_SUFFIXES, include_hash=True),
        "reference_files": scan_files(root, paths["references"], LITERATURE_SUFFIXES, include_hash=False),
        "manuscript_sections": manuscript_sections,
    }


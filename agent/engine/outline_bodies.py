"""Outline chapter body completeness for generate + export.

Empty outline pads and heading-only drafts used to become empty ``\\section`` /
Heading1s. Generate and export treat a chapter as written only when it has
prose (or a table) after ATX headings are stripped.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

_HEADING_RE = re.compile(r"^#{1,6}\s+.*$", re.M)

CHAPTER_TYPES = (
    "intro",
    "lit_review",
    "data_desc",
    "methods",
    "results",
    "conclusion",
)


def prose_without_headings(content: Any) -> str:
    return _HEADING_RE.sub("", str(content or "")).strip()


def chapter_has_body(chapter: Any) -> bool:
    if not isinstance(chapter, Mapping):
        return False
    return bool(prose_without_headings(chapter.get("content")))


def written_by_type(body_chapters: Any) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for chapter in body_chapters or []:
        if not isinstance(chapter, Mapping):
            continue
        chapter_type = str(chapter.get("type") or "").strip()
        if chapter_type and chapter_type not in found:
            found[chapter_type] = dict(chapter)
    return found


def outline_specs(state: Mapping[str, Any] | None) -> list[dict]:
    outline = (state or {}).get("outline") or []
    specs: list[dict] = []
    seen: set[str] = set()
    for entry in outline:
        if not isinstance(entry, Mapping):
            continue
        chapter_type = str(entry.get("type") or "").strip()
        if not chapter_type or chapter_type in seen:
            continue
        seen.add(chapter_type)
        specs.append(dict(entry))
    return specs


def missing_outline_specs(state: Mapping[str, Any] | None) -> list[dict]:
    bodies = written_by_type((state or {}).get("body_chapters") or [])
    return [
        spec
        for spec in outline_specs(state)
        if not chapter_has_body(bodies.get(str(spec.get("type") or "")))
    ]

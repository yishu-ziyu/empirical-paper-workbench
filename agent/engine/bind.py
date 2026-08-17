"""Project node products into chapter-prompt kwargs.

Truth for overlapping keys comes from state written by graph nodes,
not from HTTP or client-supplied placeholders.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from engine.readiness import claim_mode


def format_entries(entries: Iterable[Any]) -> str:
    """Turn literature_entries into a prompt-facing reference list."""
    lines: list[str] = []
    for entry in entries or []:
        if not isinstance(entry, Mapping):
            continue
        authors = entry.get("authors") or []
        if isinstance(authors, (list, tuple)):
            author_str = ", ".join(str(a) for a in authors if a)
        else:
            author_str = str(authors)
        year = entry.get("year")
        year_str = str(year) if year not in (None, "") else "n.d."
        title = str(entry.get("title") or "").strip()
        if author_str and title:
            lines.append(f"{author_str} ({year_str}). {title}.")
        elif title:
            lines.append(f"({year_str}). {title}.")
        elif author_str:
            lines.append(f"{author_str} ({year_str}).")
    return "\n".join(lines)


def bind_chapter_kwargs(state: Mapping[str, Any], chapter_spec: Mapping[str, Any]) -> dict:
    rd = state.get("research_direction") or {}
    if not isinstance(rd, Mapping):
        rd = {}
    spec = chapter_spec if isinstance(chapter_spec, Mapping) else {}
    rob = state.get("robustness_results") or {}
    if not isinstance(rob, Mapping):
        rob = {}
    diag = state.get("identification_diag") or {}
    if not isinstance(diag, Mapping):
        diag = {}
    return {
        "research_question": rd.get("question") or state.get("research_question") or "",
        "method": spec.get("method") or rd.get("method") or "",
        "results": state.get("results") or "",
        "robustness_table": rob.get("summary_table") or "",
        "key_references": format_entries(state.get("literature_entries") or []),
        "citation_indices": state.get("citation_indices") or {},
        "star_rating": state.get("star_rating"),
        "claim": claim_mode(state),
        "identification_report": diag.get("report") or "",
    }

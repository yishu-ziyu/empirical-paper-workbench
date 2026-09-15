"""FL query from confirmed session.design facets. Not a free-written LLM query."""
from __future__ import annotations

from typing import Any


def session_design(state: Any) -> dict[str, Any] | None:
    if not isinstance(state, dict):
        return None
    design = state.get("design")
    if isinstance(design, dict):
        return design
    session = state.get("session")
    if isinstance(session, dict) and isinstance(session.get("design"), dict):
        return session["design"]
    return None


def design_is_confirmed(state_or_design: Any) -> bool:
    design = state_or_design
    if isinstance(state_or_design, dict) and "status" not in state_or_design:
        design = session_design(state_or_design)
    if not isinstance(design, dict):
        return False
    return design.get("status") == "confirmed" and design.get("confirmed") is True


def build_query(design: dict[str, Any] | None) -> str:
    if not isinstance(design, dict):
        return ""
    parts: list[str] = []
    source = design.get("source") if isinstance(design.get("source"), dict) else {}
    for key in ("title", "question"):
        val = str(source.get(key) or "").strip()
        if val:
            parts.append(val)
    for key in ("method", "outcome", "treatment"):
        val = str(design.get(key) or "").strip()
        if val:
            parts.append(val)
    return " ".join(parts)

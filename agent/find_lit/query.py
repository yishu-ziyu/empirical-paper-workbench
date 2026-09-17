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
    """topic_positioning: who worked on this question/method/outcome/treatment."""
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


# method_check asks a different question: does *this* method hold here, and when
# does it break. Same design facets, different query planning.
METHOD_FAILURE_MODE_TERMS: dict[str, list[str]] = {
    "did": ["parallel trends", "staggered treatment timing", "negative weights"],
    "iv": ["weak instruments", "exclusion restriction", "first stage"],
    "rd": ["running variable manipulation", "bandwidth sensitivity", "continuity"],
}
DEFAULT_FAILURE_MODE_TERMS = ["assumptions", "identification failure", "limitations"]


def classify_method(method: Any) -> str | None:
    """Collapse a free-text method to did / iv / rd, else None."""
    raw = str(method or "").strip().lower()
    if not raw:
        return None
    if "did" in raw or "双重差分" in raw or "difference in differences" in raw:
        return "did"
    if raw in {"iv", "2sls"} or "工具变量" in raw or "instrumental variable" in raw:
        return "iv"
    if raw in {"rd", "rdd"} or "断点" in raw or "regression discontinuity" in raw:
        return "rd"
    return None


def failure_mode_terms(design: dict[str, Any] | None) -> list[str]:
    method = design.get("method") if isinstance(design, dict) else None
    return METHOD_FAILURE_MODE_TERMS.get(
        classify_method(method), DEFAULT_FAILURE_MODE_TERMS
    )


def build_method_check_query(design: dict[str, Any] | None) -> str:
    """method_check: method name + applicability / failure-mode words."""
    if not isinstance(design, dict):
        return ""
    parts: list[str] = []
    for key in ("method", "outcome"):
        val = str(design.get(key) or "").strip()
        if val:
            parts.append(val)
    parts.extend(failure_mode_terms(design))
    return " ".join(p for p in parts if p)


def build_risk_queries(design: dict[str, Any] | None) -> list[str]:
    """One query per must-check threat so coverage is per-risk, not per-count."""
    if not isinstance(design, dict):
        return []
    method = str(design.get("method") or "").strip()
    return [
        " ".join(p for p in (method, term) if p)
        for term in failure_mode_terms(design)
    ]

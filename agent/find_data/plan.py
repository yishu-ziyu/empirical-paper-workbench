"""FD-BE-plan: confirmed design facets → find-data plan (DECIDE-7 / R-sources).

Reads only a confirmed ``session.design``. Emits ``session.find_data`` with
a where/how plan and ``route_family``. Does not attach data, does not set
``dataAttached`` / ``allow_did``, and does not treat fixtures as found data.
Honesty recut: real fetch / external venues first; teaching extracts only
as an optional labeled shelf. Candidates stay empty unless a prior suggest
already labeled them.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from agent.data_honesty import CAPTAIN_LOCAL_REAL
from agent.find_data.honesty import project_honest_find_data

ROUTE_FAMILIES = ("educ_wage", "minwage", "growth", "macro", "else")

# Real-fetch / external venues first (DECIDE-10). Teaching extracts are not
# the primary venue and are not find success.
PRIMARY_VENUE = {
    "educ_wage": "IPUMS",
    "minwage": "Card zip",
    "growth": "WDI",
    "macro": "FRED",
    "else": "Dataverse",
}

# Named landing paths. Dataverse is the always-on backup except when it is
# already the primary venue. Fixture names stay off this list.
_VENUES = {
    "educ_wage": ("IPUMS", "Dataverse"),
    "minwage": ("Card zip", "Dataverse"),
    "growth": ("WDI", "Dataverse"),
    "macro": ("FRED", "Dataverse"),
    "else": ("Dataverse",),
}

CAPTAIN_LOCAL_HOW = (
    " First-class acquire (source=captain-local-real): upload a real local "
    "panel (CSV or Stata .dta); interim OK for real Desktop/经济学论文 files. "
    "Never teaching toys."
)

_MINWAGE = re.compile(
    r"最低工资|minimum[\s\-]?wages?|min[\s_]?wage|"
    r"card[\s&\-]+krueger|card[\s]+and[\s]+krueger|"
    r"nj[\s\-–]?pa|new\s*jersey.{0,24}pennsylvania",
    re.I,
)
_SCHOOLING = re.compile(
    r"受教育|教育年限|schooling|\beducation\b|\beduc\b|教育|mincer|明瑟",
    re.I,
)
_WAGE_EARN = re.compile(r"(?<!最低)工资|\bwages?\b|收入|earnings", re.I)
_GROWTH = re.compile(
    r"\bbarro\b|巴罗|经济增长|economic\s+growth|determinants of growth|"
    r"跨国增长|增长回归|cross[\s\-]?country\s+growth|"
    r"world\s+development\s+indicators|\bwdi\b",
    re.I,
)
_MACRO = re.compile(
    r"\bfred\b|宏观|利率|通胀|通货膨胀|失业率|unemployment\s+rate|"
    r"federal\s+funds|interest\s+rates?|inflation|cpi\b|gdp\s+deflator|"
    r"monetary|money\s+supply|aggregates?",
    re.I,
)


class DesignUnconfirmed(ValueError):
    """FD must not emit an authoritative plan against missing/draft design."""

    def __init__(self, reason: str = "design_unconfirmed") -> None:
        super().__init__(reason)
        self.reason = reason


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _as_text(value: Any) -> str:
    return str(value or "").strip()


def is_confirmed_design(design: Any) -> bool:
    """True iff the infer-design lock is set (status=confirmed and confirmed=true)."""
    if not isinstance(design, dict):
        return False
    return design.get("status") == "confirmed" and design.get("confirmed") is True


def _source(design: dict[str, Any]) -> dict[str, Any]:
    raw = design.get("source")
    return raw if isinstance(raw, dict) else {}


def _interaction_terms(design: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    for item in design.get("interactions") or []:
        if not isinstance(item, dict):
            continue
        term = _as_text(item.get("term"))
        if not term:
            left = _as_text(item.get("left"))
            right = _as_text(item.get("right"))
            if left and right:
                term = f"{left}:{right}"
        if term and term not in terms:
            terms.append(term)
    return terms


def _facet_blob(design: dict[str, Any]) -> str:
    source = _source(design)
    parts = [
        _as_text(design.get("outcome")),
        _as_text(design.get("treatment")),
        _as_text(design.get("method")),
        _as_text(source.get("title")),
        _as_text(source.get("question")),
        " ".join(_as_text(c) for c in (design.get("controls") or []) if _as_text(c)),
        " ".join(_interaction_terms(design)),
    ]
    return " ".join(p for p in parts if p)


def _treatment_key(design: dict[str, Any]) -> str:
    return re.sub(r"[\s\-]+", "_", _as_text(design.get("treatment")).lower())


def _outcome_key(design: dict[str, Any]) -> str:
    return re.sub(r"[\s\-]+", "_", _as_text(design.get("outcome")).lower())


def classify_route_family(design: dict[str, Any]) -> str:
    """R-sources first-match. Ambiguous / unmatched → ``else`` (Dataverse).

    ``minwage`` is checked before ``educ_wage`` so "minimum wage" does not
    fall into the generic wage row. Catalog ids are ignored.
    """
    blob = _facet_blob(design)
    treatment = _treatment_key(design)
    outcome = _outcome_key(design)

    minwage_slots = treatment in {
        "min_wage",
        "minwage",
        "minimum_wage",
        "minimumwage",
    }
    if minwage_slots or _MINWAGE.search(blob):
        return "minwage"

    schooling = bool(
        _SCHOOLING.search(blob)
        or treatment in {"schooling", "educ", "education", "educ_years"}
    )
    wage = bool(
        outcome in {"wage", "wages", "earnings", "income"}
        or (_WAGE_EARN.search(blob) and not _MINWAGE.search(blob))
    )
    if schooling and wage:
        return "educ_wage"

    growth_slots = outcome in {
        "growth",
        "gdp_growth",
        "gdp_pc_growth",
        "economic_growth",
    }
    if growth_slots or _GROWTH.search(blob):
        return "growth"

    if _MACRO.search(blob):
        return "macro"

    return "else"


def search_facets(design: dict[str, Any]) -> dict[str, Any]:
    """Y / X / method / interactions used to search (not a confirm substitute)."""
    source = _source(design)
    outcome = _as_text(design.get("outcome"))
    treatment = _as_text(design.get("treatment"))
    method = _as_text(design.get("method"))
    controls = [
        _as_text(item)
        for item in (design.get("controls") or [])
        if _as_text(item)
    ]
    interactions = _interaction_terms(design)
    title = _as_text(source.get("title"))
    question = _as_text(source.get("question"))
    query_terms: list[str] = []
    for item in (outcome, treatment, method, *controls, *interactions):
        if item and item not in query_terms:
            query_terms.append(item)
    return {
        "method": method,
        "outcome": outcome,
        "treatment": treatment,
        "controls": controls,
        "interactions": interactions,
        "qType": _as_text(design.get("qType")),
        "title": title,
        "question": question,
        "query_terms": query_terms,
    }


def _how(family: str, facets: dict[str, Any]) -> str:
    outcome = facets["outcome"] or "confirmed outcome"
    treatment = facets["treatment"] or "confirmed treatment"
    method = facets["method"] or "confirmed method"
    terms = ", ".join(facets["query_terms"]) or f"{outcome} {treatment} {method}"
    shelf = (
        "Optional teaching-known extract may appear on the teaching shelf "
        "— not a find result."
    )
    if family == "educ_wage":
        body = (
            f"Open the IPUMS CPS/USA extract landing and request columns bound "
            f"to confirmed outcome '{outcome}' and treatment '{treatment}'. "
            f"Search Dataverse as backup using: {terms}. {shelf}"
        )
    elif family == "minwage":
        body = (
            f"Follow the Card zip at the author-published NJ–PA page. "
            f"Search Dataverse for confirmed outcome '{outcome}' and "
            f"treatment '{treatment}' (method {method}). {shelf}"
        )
    elif family == "growth":
        body = (
            f"Use World Bank WDI for confirmed growth outcome '{outcome}'. "
            f"Search Dataverse as backup using: {terms}. {shelf}"
        )
    elif family == "macro":
        body = (
            f"Search FRED for series matching confirmed outcome '{outcome}' "
            f"and treatment '{treatment}'. Search Dataverse as backup using: "
            f"{terms}."
        )
    else:
        body = (
            f"Search Dataverse for confirmed outcome '{outcome}', treatment "
            f"'{treatment}', and method '{method}'. Query terms: {terms}."
        )
    return body + CAPTAIN_LOCAL_HOW


def _where(family: str) -> str:
    if family == "educ_wage":
        return "IPUMS extract landing"
    if family == "minwage":
        return "Card zip"
    if family == "growth":
        return "WDI"
    if family == "macro":
        return "FRED"
    return "Dataverse"


def _empty_find_data() -> dict[str, Any]:
    return {
        "status": "missing",
        "planned_at": None,
        "route_family": None,
        "primary_venue": None,
        "plan": None,
        "candidates": [],
        "teaching_shelf": None,
    }


def build_find_data_plan(
    design: Any,
    *,
    now: str | None = None,
    prior: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build ``session.find_data`` from a confirmed design.

    Raises ``DesignUnconfirmed`` when design is missing or still draft.
    Candidates stay empty unless *prior* already has honesty-labeled rows.
    This slice never prefills a fixture as found data.
    """
    if not is_confirmed_design(design):
        raise DesignUnconfirmed("design_unconfirmed")

    family = classify_route_family(design)
    facets = search_facets(design)
    where = _where(family)
    how = _how(family, facets)
    record = {
        "status": "planned",
        "planned_at": now or _utc_now(),
        "route_family": family,
        "primary_venue": PRIMARY_VENUE[family],
        "plan": {
            "where": where,
            "how": how,
            "venues": [CAPTAIN_LOCAL_REAL, *list(_VENUES[family])],
            "search_facets": facets,
        },
        "candidates": [],
        "teaching_shelf": None,
    }
    if isinstance(prior, dict):
        projected = project_honest_find_data(prior)
        record["candidates"] = list(projected.get("candidates") or [])
        record["teaching_shelf"] = projected.get("teaching_shelf")
    return record


def read_find_data(state: dict[str, Any] | None) -> dict[str, Any]:
    """Return stored plan only while design remains confirmed. Else missing."""
    state = state or {}
    if not is_confirmed_design(state.get("design")):
        return _empty_find_data()
    stored = state.get("find_data")
    if not isinstance(stored, dict) or stored.get("status") != "planned":
        return _empty_find_data()
    return project_honest_find_data(stored)


__all__ = [
    "CAPTAIN_LOCAL_HOW",
    "DesignUnconfirmed",
    "PRIMARY_VENUE",
    "ROUTE_FAMILIES",
    "build_find_data_plan",
    "classify_route_family",
    "is_confirmed_design",
    "read_find_data",
    "search_facets",
]

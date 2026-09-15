"""Title-first research-design draft (INF-BE-propose / DECIDE-6).

Reads only the session title and optional research-question text.
Writes a ``session.design`` draft. Does not lock, attach data, or
treat a catalog entry id as the method source of truth.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from ..norms.loader import assert_propose_gates
from .spec import norm_method

# Catalog identity tokens named in the infer-design contract. A title that
# *is* one of these is not a research question; it cannot open DiD.
_CATALOG_IDENTITY = frozenset(
    {
        "ck1994",
        "ck1994-long",
        "minimum-wage-employment",
        "barro1991",
        "barro1991-growth",
    }
)

_CK_TREATMENT = re.compile(
    r"最低工资|minimum[\s\-]?wages?|min[\s_]?wage",
    re.I,
)
_CK_OUTCOME = re.compile(r"就业|employment|雇佣", re.I)
_CK_PAPER = re.compile(
    r"card[\s&\-]+krueger|card[\s]+and[\s]+krueger",
    re.I,
)
_NJ_MINWAGE = re.compile(
    r"(新泽西|new\s*jersey).{0,32}(最低工资|minimum[\s\-]?wage)"
    r"|(最低工资|minimum[\s\-]?wage).{0,32}(新泽西|new\s*jersey)",
    re.I,
)

_DID_METHOD = re.compile(
    r"双重差分|倍差法|"
    r"difference[\s\-]*in[\s\-]*differences?|"
    r"diff[\s\-]*in[\s\-]*diff|"
    r"\bdid\b|"
    r"difference_in_differences",
    re.I,
)
_IV_METHOD = re.compile(
    r"工具变量|instrumental[\s\-]?variables?|\b2sls\b|\biv\b",
    re.I,
)
_RD_METHOD = re.compile(
    r"断点回归|回归断点|regression[\s\-]?discontinuity|\brdd\b|\brd\b",
    re.I,
)
_SCM_METHOD = re.compile(r"合成控制|synthetic[\s_\-]?control|\bscm\b", re.I)

_SCHOOLING = re.compile(r"受教育|教育年限|schooling|\beducation\b|教育", re.I)
_WAGES = re.compile(r"(?<!最低)工资|\bwages?\b|收入|earnings", re.I)
_BARRO = re.compile(
    r"\bbarro\b|经济增长|economic\s+growth|determinants of growth|"
    r"跨国增长|增长回归",
    re.I,
)

_DID_INTERACTION = {
    "kind": "did",
    "left": "treated",
    "right": "period",
    "term": "treated:period",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _blob(title: str, question: str) -> str:
    return f"{title} {question}".strip()


def _catalog_identity_key(text: str) -> str:
    return re.sub(r"\s+", "", text.strip().lower()).replace("_", "-")


def _is_catalog_identity(title: str, question: str) -> bool:
    """True when the *whole* title (and empty RQ) is a catalog id token."""
    if str(question or "").strip():
        return False
    key = _catalog_identity_key(title)
    if not key:
        return False
    return key in _CATALOG_IDENTITY


def _is_ck_class(text: str) -> bool:
    if _CK_PAPER.search(text) or _NJ_MINWAGE.search(text):
        return True
    return bool(_CK_TREATMENT.search(text) and _CK_OUTCOME.search(text))


def _explicit_method(text: str) -> str | None:
    if _DID_METHOD.search(text):
        return "did"
    if _IV_METHOD.search(text):
        return "iv"
    if _RD_METHOD.search(text):
        return "rd"
    if _SCM_METHOD.search(text):
        return "scm"
    return None


def _did_slots(text: str) -> dict[str, str]:
    outcome = "employment" if _CK_OUTCOME.search(text) else ""
    treatment = "min_wage" if _CK_TREATMENT.search(text) else ""
    return {
        "outcome": outcome,
        "treatment": treatment,
        "group": "treated",
        "treated": "treated",
        "period": "post",
    }


def _ols_slots(text: str) -> dict[str, str]:
    if _SCHOOLING.search(text) and _WAGES.search(text):
        return {"outcome": "wages", "treatment": "schooling"}
    if _BARRO.search(text):
        return {"outcome": "growth", "treatment": ""}
    return {"outcome": "", "treatment": ""}


def _qtype_for(method: str) -> str:
    if method == "ols":
        return "average"
    return "causal"


def propose_design(
    title: str,
    question: str = "",
    *,
    now: str | None = None,
) -> dict[str, Any]:
    """Build a ``session.design`` draft from title (+ optional RQ).

    Always returns ``status=draft``. Never sets catalog id, ``allow_did``,
    ``dataAttached``, or chapter bodies.
    """
    title = str(title or "").strip()
    question = str(question or "").strip()
    if not title:
        raise ValueError("title required")

    text = _blob(title, question)
    catalog_only = _is_catalog_identity(title, question)

    if catalog_only:
        method = "ols"
        slots = _ols_slots(text)
        interactions: list[dict[str, str]] = []
    elif _is_ck_class(text):
        method = "did"
        slots = _did_slots(text)
        interactions = [dict(_DID_INTERACTION)]
    else:
        named = _explicit_method(text)
        method = named or "ols"
        if method == "did":
            slots = _did_slots(text)
            interactions = [dict(_DID_INTERACTION)]
        else:
            slots = _ols_slots(text)
            interactions = []

    stored = norm_method(method) or "ols"
    draft: dict[str, Any] = {
        "status": "draft",
        "confirmed": False,
        "proposed_at": now or _utc_now(),
        "confirmed_at": None,
        "source": {"title": title, "question": question},
        "method": stored,
        "outcome": slots.get("outcome", ""),
        "treatment": slots.get("treatment", ""),
        "controls": [],
        "group": slots.get("group", ""),
        "treated": slots.get("treated", ""),
        "period": slots.get("period", ""),
        "time_col": "",
        "id_col": "",
        "first_treat_col": "",
        "interactions": interactions,
        "qType": _qtype_for(stored),
        "heterogeneity_groups": [],
        "catalog_entry_id": None,
    }
    assert_propose_gates(draft)
    return draft


__all__ = ["propose_design"]

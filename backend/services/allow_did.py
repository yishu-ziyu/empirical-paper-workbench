"""DiD permission gate (DID-BE-gate recut; DECIDE-6).

Permission is a derived projection of confirmed ``session.design``:

1. ``status == "confirmed"``
2. ``method`` normalizes to ``did``
3. the confirmed design names the treated×period main term

Catalog identity (``ck1994``, ``ck1994_long``, ``minimum-wage-employment``,
…), TITLE/TOPIC text, form ``method=did``, and a stamped ``allow_did`` flag
are not setters. Missing / null / absent is false. Fail closed.

``confirmed_did_method`` is the hard-block hook for DID-BE-spec: confirmed
``method=did`` even when the interaction is missing. This module does not
force a formula or return 409.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from agent.design.spec import norm_method

_CARD_TEACHING = "card_1995"

_DUMMY_NAMES = frozenset(
    {
        "treat_post",
        "treatpost",
        "treatxpost",
        "treat_x_post",
        "treated_period",
        "treated_post",
        "did",
        "nj_after",
        "njxafter",
        "nj_x_after",
    }
)

# treat:post / treat * post / treat × post / treat#post / treat x post
_INTERACTION_RE = re.compile(
    r"(?i)\b(treated|treat|nj)\s*(?::|\*|×|#|x)\s*(period|post|after)\b"
    r"|\b(period|post|after)\s*(?::|\*|×|#|x)\s*(treated|treat|nj)\b"
)

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def design_from_state(state: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Read ``session.design`` from state. Missing is unconfirmed."""
    if not isinstance(state, dict):
        return None
    design = state.get("design")
    return design if isinstance(design, dict) else None


def design_is_confirmed(design: Mapping[str, Any] | None) -> bool:
    """True only when status and confirmed agree on lock. Fail closed."""
    if not isinstance(design, dict):
        return False
    status = str(design.get("status") or "").strip().lower()
    confirmed = design.get("confirmed")
    return status == "confirmed" and confirmed is True


def confirmed_did_method(state: Mapping[str, Any] | None) -> bool:
    """Hard-block trigger: confirmed ``design.method=did`` (or alias).

    Does not require treated×period. DID-BE-spec owns force + 409 when
    this is true and the interaction is missing.
    """
    if _is_card_teaching(state):
        return False
    design = design_from_state(state)
    if not design_is_confirmed(design):
        return False
    assert design is not None
    return norm_method(design.get("method")) == "did"


def has_treated_period_interaction(design: Mapping[str, Any] | None) -> bool:
    """True when the design names the 2×2 main term (§2.4).

    Treated or period slots alone, ``id_col`` + ``time_col``, TWFE absorb
    syntax, and ``first_treat_col`` do not count.
    """
    if not isinstance(design, dict):
        return False
    for blob in _interaction_blobs(design):
        if _INTERACTION_RE.search(blob):
            return True
        tokens = {_norm(tok) for tok in _TOKEN_RE.findall(blob)}
        if tokens & _DUMMY_NAMES:
            return True
    return False


def did_interaction_missing(state: Mapping[str, Any] | None) -> bool:
    """Confirmed DiD design with no treated×period term. Spec hard-block."""
    design = design_from_state(state)
    return confirmed_did_method(state) and not has_treated_period_interaction(design)


def session_allow_did(state: Mapping[str, Any] | None) -> bool:
    """DiD permission. Catalog id / title / form method / stamps ignored."""
    if _is_card_teaching(state):
        return False
    design = design_from_state(state)
    if not confirmed_did_method(state):
        return False
    return has_treated_period_interaction(design)


def _interaction_blobs(design: Mapping[str, Any]) -> list[str]:
    blobs: list[str] = []
    raw = design.get("interactions")
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            kind = str(item.get("kind") or "").strip().lower()
            if kind and kind != "did":
                continue
            left = str(item.get("left") or "").strip()
            right = str(item.get("right") or "").strip()
            term = str(item.get("term") or "").strip()
            parts = [term, left, right]
            if left and right:
                parts.append(f"{left}:{right}")
            blob = " ".join(part for part in parts if part)
            if blob:
                blobs.append(blob)
    return blobs


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.strip().lower())


def _is_card_teaching(state: Mapping[str, Any] | None) -> bool:
    if not isinstance(state, dict):
        return False
    for key in ("research_lab", "research"):
        block = state.get(key)
        if isinstance(block, dict) and block.get("teaching_case") == _CARD_TEACHING:
            return True
    return False

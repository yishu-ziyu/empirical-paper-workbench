"""R-lit-bar chapter write gate. Search never writes chapters."""
from __future__ import annotations

from typing import Any

from .cards import MIN_CARDS, is_verifiable
from .query import design_is_confirmed


def find_lit_record(state: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(state, dict):
        return {}
    rec = state.get("find_lit")
    if isinstance(rec, dict):
        return rec
    session = state.get("session")
    if isinstance(session, dict) and isinstance(session.get("find_lit"), dict):
        return session["find_lit"]
    return {}


def literature_write_blockers(state: dict[str, Any] | None) -> list[str]:
    """Formal path only: confirmed design must pass R-lit-bar before lit_review.

    Unconfirmed / missing design is out of this product line; return [].
    """
    if not design_is_confirmed(state):
        return []
    rec = find_lit_record(state)
    cards = [c for c in (rec.get("cards") or []) if isinstance(c, dict)]
    verifiable = [c for c in cards if is_verifiable(c)]
    blockers: list[str] = []
    if len(verifiable) < MIN_CARDS:
        blockers.append("r_lit_bar_need_5_cards")
    checked = [str(i) for i in (rec.get("checked_ids") or []) if i]
    if not checked:
        blockers.append("r_lit_bar_no_checked")
        return blockers
    by_id = {str(c.get("id")): c for c in verifiable if c.get("id")}
    for cid in checked:
        card = by_id.get(cid)
        if card is None:
            blockers.append("r_lit_bar_unchecked_or_unverified")
            break
    return blockers


def literature_write_allowed(state: dict[str, Any] | None) -> bool:
    return not literature_write_blockers(state)

"""session.design confirm lock (INF-BE-confirm / DECIDE-6).

Confirm is the only transition that locks ``session.design``. This module
does not propose a draft, suggest data, attach, or set ``allow_did``.

Gate hook for later integrate (gold/classic prefill, DC-BE-suggest,
DID-BE-gate, PREWRITE ``set_direction`` / ``main_specification``):

    locked_design(state)  →  None unless status=confirmed and confirmed=true

Callers that would treat a catalog id, gold body, or form click as the
authoritative spec must call this and fail closed / no-op when it is None.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DESIGN_NOT_PROPOSED = "design_not_proposed"
STATUS_DRAFT = "draft"
STATUS_CONFIRMED = "confirmed"


class DesignNotProposed(ValueError):
    """Confirm was requested without a draft. Fail closed."""

    code = DESIGN_NOT_PROPOSED


def utc_now_iso(now: datetime | None = None) -> str:
    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return stamp.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_design(state: Any) -> dict[str, Any] | None:
    if not isinstance(state, dict):
        return None
    raw = state.get("design")
    return raw if isinstance(raw, dict) else None


def public_design(state: Any) -> dict[str, Any] | None:
    """Snapshot projection. Unknown shapes are unconfirmed (None)."""
    design = read_design(state)
    if design is None:
        return None
    if design.get("status") not in {STATUS_DRAFT, STATUS_CONFIRMED}:
        return None
    return dict(design)


def is_confirmed_object(design: Any) -> bool:
    if not isinstance(design, dict):
        return False
    return design.get("status") == STATUS_CONFIRMED and design.get("confirmed") is True


def is_design_confirmed(state: Any) -> bool:
    """True iff session.design is the locked (confirmed) object."""
    return is_confirmed_object(read_design(state))


def locked_design(state: Any) -> dict[str, Any] | None:
    """Authoritative design for downstream, or None (unconfirmed / missing).

    DECIDE-6 accept bullet 4: missing or ``status=draft`` must not unlock
    gold / classic prefilled spec or locked ``main_specification``.
    DECIDE-6 accept bullet 5: after confirm, suggest/attach may consume this
    object; this function only exposes the lock, it does not suggest.
    """
    design = read_design(state)
    if not is_confirmed_object(design):
        return None
    return dict(design)


def lock_confirmed_design(
    design: Any,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Draft → confirmed. Already confirmed is idempotent. No draft → error."""
    if not isinstance(design, dict):
        raise DesignNotProposed
    if is_confirmed_object(design):
        locked = dict(design)
        locked["catalog_entry_id"] = None
        return locked
    if design.get("status") != STATUS_DRAFT:
        raise DesignNotProposed
    locked = dict(design)
    locked["status"] = STATUS_CONFIRMED
    locked["confirmed"] = True
    locked["confirmed_at"] = utc_now_iso(now)
    locked["catalog_entry_id"] = None
    return locked

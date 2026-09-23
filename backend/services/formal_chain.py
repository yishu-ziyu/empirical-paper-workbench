"""Formal confirmation chain gates (FORMAL-CONFIRMATION-CHAIN-1/2).

Fail-closed backend guards for the frozen business dependencies on the formal
TITLE/TOPIC path:

- confirm-attach (``dataAttached``) before direction admission, PREWRITE-PAUSE
  flags, and estimate (``docs/contracts/data-completion-contract.md`` §2 / §2a);
- a confirmed ``session.design`` before downstream gates treat the design as
  locked (``docs/contracts/infer-design-contract.md`` §5.2 rule 4).

Boundary (frozen by the data-completion contract §2.1):

- Sessions carry an explicit category. ``session_kind=formal`` is written when
  the new flow creates a session (``POST /sessions``) or admits a durable
  upload; sessions with an explicit ``upload_readiness`` are the upload-era /
  classic-5-era path and are formal as well.
- ``session_kind=legacy``, or a session with no category marker and no
  explicit formal-era field, is legacy (upload-recovery KTD7 keeps working
  unchanged). Omission never means legacy for a session the new flow created:
  a formal session without a confirmed design is refused, not waved through.
- Card teaching sessions are a separate product line and are never gated here.

Reading data is not a formal execution: structure checks, feasibility work and
preview generation stay available without a confirmed design. Only the formal
analysis itself (direction admission, PREWRITE flags, estimate) is gated.
"""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

CODE_DATA_NOT_ATTACHED = "data_not_attached"
CODE_DESIGN_UNCONFIRMED = "design_unconfirmed"

_READY = "READY"
_CARD_TEACHING = "card_1995"

SESSION_KIND_FORMAL = "formal"
SESSION_KIND_LEGACY = "legacy"
SESSION_KIND_CARD_TEACHING = "card_teaching"

_SESSION_KIND_KEYS = ("session_kind", "sessionKind")


def formal_category_fields() -> dict[str, str]:
    """Explicit category written by the new flow when it creates a session."""
    return {"session_kind": SESSION_KIND_FORMAL}


def read_session_kind(state: dict[str, Any]) -> str | None:
    for key in _SESSION_KIND_KEYS:
        raw = state.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip().lower()
    return None


def _is_card_teaching(state: dict[str, Any]) -> bool:
    if read_session_kind(state) == SESSION_KIND_CARD_TEACHING:
        return True
    lab = state.get("research_lab")
    return (
        isinstance(lab, dict) and lab.get("teaching_case") == _CARD_TEACHING
    )


def formal_path_applies(state: dict[str, Any]) -> bool:
    """True when the session is on the new formal path (not legacy / Card).

    ``session_kind`` is authoritative when present: a session explicitly
    marked formal is gated even before it has data, and one explicitly marked
    legacy is not gated. Without a marker, the upload-era fields decide.
    """
    if _is_card_teaching(state):
        return False
    kind = read_session_kind(state)
    if kind == SESSION_KIND_FORMAL:
        return True
    if kind == SESSION_KIND_LEGACY:
        return False
    return "upload_readiness" in state or isinstance(state.get("design"), dict)


def attach_gate_applies(state: dict[str, Any]) -> bool:
    """Confirm-attach gate scope: upload-era / classic-5-era sessions only.

    Frozen by data-completion §2.1: new formal sessions carry an explicit
    ``upload_readiness``; legacy sessions (no such field) keep KTD-era
    behavior. A bare ``design`` object without upload-era ingest is a
    direct-bind session (e.g. DID-spec fixtures) and is not attach-gated.
    """
    if _is_card_teaching(state):
        return False
    return "upload_readiness" in state


def read_data_attached(state: dict[str, Any]) -> bool:
    return state.get("dataAttached") is True or state.get("data_attached") is True


def require_confirm_attached(state: dict[str, Any]) -> None:
    """Refuse unless the current candidate is confirm-attached (formal path)."""
    if not attach_gate_applies(state):
        return
    if read_data_attached(state):
        return
    raise HTTPException(
        status_code=409,
        detail={"code": CODE_DATA_NOT_ATTACHED},
    )


def is_design_locked(design: Any) -> bool:
    """True only for the locked shape written by design confirm."""
    return (
        isinstance(design, dict)
        and design.get("status") == "confirmed"
        and design.get("confirmed") is True
    )


def require_design_confirmed(state: dict[str, Any]) -> None:
    """Refuse unless the formal session carries a confirmed design.

    Applies to the whole formal path, not only to sessions that already
    produced a design object: a missing, ``None``, malformed or draft design
    must not unlock formal analysis (infer-design §5.2 rule 4). Legacy and
    Card teaching sessions keep their own path.
    """
    if not formal_path_applies(state):
        return
    if is_design_locked(state.get("design")):
        return
    raise HTTPException(
        status_code=409,
        detail={"code": CODE_DESIGN_UNCONFIRMED},
    )


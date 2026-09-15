"""Title/catalog gate for the narrow DiD exception (DID-BE-gate).

``allow_did`` defaults false. Only classic Card–Krueger / minwage TITLE/TOPIC
or catalog identity may set true. Form ``method=did`` is not a setter.

Does not load catalog bytes, does not force treated×period, and does not
rewrite the OLS lock. Missing / null / absent is false.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

# Catalog identity tokens. Do not invent inventory rows; match known ids only.
MINWAGE_ENTRY_IDS = frozenset(
    {
        "minimum-wage-employment",
        "ck1994",
    }
)

_CARD_TEACHING = "card_1995"
_CLASSIC5 = "classic-5"

_CK_RE = re.compile(
    r"card[\s\-–—&.]*krueger|卡德[\s\-·]*克鲁格|\bck1994\b",
    re.IGNORECASE,
)
_MINWAGE_RE = re.compile(
    r"minimum[\s\-]*wages?|\bmin[\s\-]?wages?\b|\bminwage\b|最低工资",
    re.IGNORECASE,
)
_ENTRY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def normalize_entry_id(entry_id: object) -> str:
    text = str(entry_id or "").strip()
    if not text or not _ENTRY_RE.fullmatch(text):
        return ""
    return text


def catalog_identity_allows(entry_id: object) -> bool:
    return normalize_entry_id(entry_id) in MINWAGE_ENTRY_IDS


def title_topic_allows(title: str = "", topic: str = "") -> bool:
    text = " ".join(part for part in (title.strip(), topic.strip()) if part)
    if not text:
        return False
    return bool(_CK_RE.search(text) or _MINWAGE_RE.search(text))


def allow_did_for(
    *,
    title: str = "",
    topic: str = "",
    entry_id: object = None,
    method: object = None,
) -> bool:
    """Return the gate. ``method`` is accepted only so callers cannot hide it."""
    del method
    if catalog_identity_allows(entry_id):
        return True
    return title_topic_allows(title, topic)


def session_allow_did(state: Mapping[str, Any] | None) -> bool:
    """Derive ``allow_did`` from title/catalog inputs. Fail closed."""
    if not isinstance(state, dict):
        return False
    if _is_card_teaching(state):
        return False
    title, topic = title_topic_from_state(state)
    return allow_did_for(
        title=title,
        topic=topic,
        entry_id=catalog_entry_id_from_state(state),
    )


def title_topic_from_state(state: Mapping[str, Any]) -> tuple[str, str]:
    pinned = state.get("title_topic")
    if isinstance(pinned, dict):
        title = str(pinned.get("title") or "").strip()
        topic = str(pinned.get("topic") or "").strip()
        if title or topic:
            return title, topic
    direction = state.get("research_direction")
    if isinstance(direction, dict):
        question = str(direction.get("question") or "").strip()
        topic = str(direction.get("topic") or "").strip()
        if question or topic:
            return question, topic
    return "", ""


def catalog_entry_id_from_state(state: Mapping[str, Any]) -> str:
    candidate = state.get("attach_candidate")
    if isinstance(candidate, dict):
        source = str(candidate.get("source") or "").strip()
        if source == _CLASSIC5:
            return normalize_entry_id(candidate.get("entry_id"))
        if source == "user_file":
            return ""
    identity = state.get("catalog_identity")
    if isinstance(identity, dict):
        return normalize_entry_id(identity.get("entry_id"))
    return ""


def catalog_identity_payload(entry_id: object) -> dict[str, str] | None:
    normalized = normalize_entry_id(entry_id)
    if not normalized:
        return None
    return {"catalog_id": _CLASSIC5, "entry_id": normalized}


def gate_updates(state: Mapping[str, Any], **fields: Any) -> dict[str, Any]:
    """Merge writes and stamp the derived ``allow_did`` flag."""
    merged = {**dict(state), **fields}
    return {**fields, "allow_did": session_allow_did(merged)}


def _is_card_teaching(state: Mapping[str, Any]) -> bool:
    for key in ("research_lab", "research"):
        block = state.get(key)
        if isinstance(block, dict) and block.get("teaching_case") == _CARD_TEACHING:
            return True
    return False

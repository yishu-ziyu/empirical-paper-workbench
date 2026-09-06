"""Card Claim language boundary. Deterministic policy, not LLM, not exact-sentence-only.

Grounding, write-gate, and the Paper badge must import this module.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

_CAUSAL_EN = re.compile(
    r"\b(?:causes?|causing|increases?|increasing|raises?|raising|"
    r"leads\s+to|leading\s+to|causal\s+effect)\b",
    re.IGNORECASE,
)
_CAUSAL_ZH = re.compile(r"导致|使.{0,12}提高|因果影响|因果效应")
_CAVEAT_EN = re.compile(
    r"under the college-proximity iv assumptions|"
    r"iv estimates suggest|"
    r"local causal return|"
    r"\blate\b",
    re.IGNORECASE,
)
_CAVEAT_ZH = re.compile(r"在工具变量假设成立时|IV 估计表明|局部因果回报")
_SENTENCE_SPLIT = re.compile(r"(?<=[。！？.!?])\s+")


def _sentences(text: str) -> list[str]:
    raw = (text or "").strip()
    if not raw:
        return []
    parts = _SENTENCE_SPLIT.split(raw)
    return [part.strip() for part in parts if part.strip()]


def _has_unconditional_causal(sentence: str) -> bool:
    if not (_CAUSAL_EN.search(sentence) or _CAUSAL_ZH.search(sentence)):
        return False
    if _CAVEAT_EN.search(sentence) or _CAVEAT_ZH.search(sentence):
        return False
    return True


def wording_exceeds_evidence(claim: Mapping[str, Any] | None, content: str) -> bool:
    """True when body text crosses the Card claim language bound."""
    text = content or ""
    payload = claim if isinstance(claim, Mapping) else {}
    forbidden = str(payload.get("unsupported_wording") or "").strip()
    if forbidden and forbidden in text:
        return True
    return any(_has_unconditional_causal(sentence) for sentence in _sentences(text))

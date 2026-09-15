"""classic-5 catalog read + confirmed-design ranking (DC-BE-suggest).

Read-only. Does not attach, does not set ``dataAttached``, does not lock
spec / gold bodies, and does not load catalog bytes (that loader is
DC-BE-attach). Catalog entries are candidates only, never an answer key.

Without a confirmed ``session.design``, ranking is not a success path.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from agent.design.spec import norm_method
from config import PRODUCT_ROOT

CATALOG_ID = "classic-5"
OWN_FILE_ACTION = "upload_own_file"
CATALOG_ENV_FILE = "ECONPAPER_CLASSIC5_CATALOG"
CATALOG_ENV_DIR = "ECONPAPER_CLASSIC5_DIR"
_DEFAULT_CATALOG = PRODUCT_ROOT / "fixtures" / "classic-5" / "catalog.json"

_WORD_RE = re.compile(r"[a-z0-9]+")
_CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]+")
_STOP = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "的",
    "了",
    "与",
    "及",
    "和",
    "在",
    "对",
    "中",
    "是",
    "为",
}
_METHOD_BONUS = 5.0
_VAR_EXACT_BONUS = 4.0
_VAR_TOKEN_BONUS = 2.0


@dataclass(frozen=True)
class Classic5Entry:
    entry_id: str
    title: str
    topic: str
    tags: tuple[str, ...]
    method: str = ""
    outcome: str = ""
    treatment: str = ""


def catalog_path() -> Path:
    """Resolve the ranking catalog file (env override, then reserved tree)."""
    env_file = (os.getenv(CATALOG_ENV_FILE) or "").strip()
    if env_file:
        return Path(env_file).expanduser()
    env_dir = (os.getenv(CATALOG_ENV_DIR) or "").strip()
    if env_dir:
        return Path(env_dir).expanduser() / "catalog.json"
    return _DEFAULT_CATALOG


def read_catalog(path: Path | None = None) -> list[Classic5Entry]:
    """Read classic-5 ranking metadata. Missing or invalid files yield []."""
    catalog = path if path is not None else catalog_path()
    try:
        raw = json.loads(catalog.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return []
    if not isinstance(raw, dict) or raw.get("catalog_id") != CATALOG_ID:
        return []
    items = raw.get("entries")
    if not isinstance(items, list):
        return []

    seen: set[str] = set()
    entries: list[Classic5Entry] = []
    for item in items:
        parsed = _parse_entry(item)
        if parsed is None or parsed.entry_id in seen:
            continue
        seen.add(parsed.entry_id)
        entries.append(parsed)
    return entries


def design_is_confirmed(design: object) -> bool:
    """Stub-read ``session.design`` confirm. Missing / draft fails closed."""
    if not isinstance(design, dict):
        return False
    status = str(design.get("status") or "").strip().lower()
    if status == "confirmed":
        return True
    if status == "draft":
        return False
    return design.get("confirmed") is True


def rank_entries_for_design(
    entries: Iterable[Classic5Entry],
    design: dict,
    title: str = "",
    topic: str = "",
) -> list[tuple[Classic5Entry, float]]:
    """Rank catalog candidates against a confirmed design. Does not attach."""
    method = norm_method(design.get("method"))
    outcome = str(design.get("outcome") or "").strip()
    treatment = str(design.get("treatment") or "").strip()
    query = _query_text(title, topic, outcome, treatment)
    scored: list[tuple[Classic5Entry, float]] = []
    for entry in entries:
        entry_method = norm_method(entry.method)
        if method and entry_method and entry_method != method:
            continue
        score = _design_score(query, entry, method, outcome, treatment)
        scored.append((entry, score))
    scored.sort(key=lambda item: (-item[1], item[0].entry_id))
    return scored


def suggest_candidates(
    title: str = "",
    topic: str = "",
    design: object = None,
) -> dict:
    """Build the suggest payload. Never sets attach / spec / allow_did."""
    title = (title or "").strip()
    topic = (topic or "").strip()
    confirmed = design_is_confirmed(design)
    design_dict = design if isinstance(design, dict) else {}
    if confirmed:
        source = design_dict.get("source")
        if isinstance(source, dict):
            title = title or str(source.get("title") or "").strip()
            topic = topic or str(source.get("question") or "").strip()
        ranked = rank_entries_for_design(read_catalog(), design_dict, title, topic)
    else:
        ranked = []
    return {
        "catalog_id": CATALOG_ID,
        "title": title,
        "topic": topic,
        "design_confirmed": confirmed,
        "candidates": [
            {
                "catalog_id": CATALOG_ID,
                "entry_id": entry.entry_id,
                "source": CATALOG_ID,
                "title": entry.title,
                "topic": entry.topic,
                "tags": list(entry.tags),
                "method": entry.method,
                "outcome": entry.outcome,
                "treatment": entry.treatment,
                "score": score,
                "attached": False,
            }
            for entry, score in ranked
        ],
        "own_file": {"action": OWN_FILE_ACTION, "catalog": False},
        "attached": False,
    }


def _parse_entry(item: object) -> Classic5Entry | None:
    if not isinstance(item, dict):
        return None
    entry_id = str(item.get("id") or "").strip()
    title = str(item.get("title") or "").strip()
    if not entry_id or not title:
        return None
    tags = tuple(
        str(tag).strip()
        for tag in (item.get("tags") or [])
        if str(tag).strip()
    )
    method = norm_method(item.get("method")) or ""
    return Classic5Entry(
        entry_id=entry_id,
        title=title,
        topic=str(item.get("topic") or "").strip(),
        tags=tags,
        method=method,
        outcome=str(item.get("outcome") or "").strip(),
        treatment=str(item.get("treatment") or "").strip(),
    )


def _query_text(*parts: str) -> str:
    return " ".join(part.strip() for part in parts if part and part.strip())


def _tokens(text: str) -> set[str]:
    lowered = text.lower()
    tokens: set[str] = set()
    for word in _WORD_RE.findall(lowered):
        if word not in _STOP and len(word) >= 2:
            tokens.add(word)
    for run in _CJK_RUN_RE.findall(text):
        tokens.update(run[i : i + 2] for i in range(len(run) - 1))
        if len(run) >= 2:
            tokens.add(run)
    return tokens - _STOP


def _score(query: str, entry: Classic5Entry) -> float:
    if not query:
        return 0.0
    q_tokens = _tokens(query)
    q_raw = query.lower()
    tag_score = 0.0
    for tag in entry.tags:
        lowered = tag.lower()
        if lowered and lowered in q_raw:
            tag_score += 3.0
        tag_score += float(len(_tokens(tag) & q_tokens))
    title_hits = float(len(_tokens(entry.title) & q_tokens))
    topic_hits = float(len(_tokens(entry.topic) & q_tokens))
    return tag_score + 2.0 * title_hits + topic_hits


def _var_score(query_tokens: set[str], slot: str, entry_slot: str, entry: Classic5Entry) -> float:
    if not slot:
        return 0.0
    lowered = slot.lower()
    if entry_slot and lowered == entry_slot.lower():
        return _VAR_EXACT_BONUS
    haystack = _tokens(" ".join((entry_slot, entry.title, entry.topic, " ".join(entry.tags))))
    overlap = _tokens(slot) & (haystack | query_tokens)
    return _VAR_TOKEN_BONUS * float(len(overlap)) if overlap else 0.0


def _design_score(
    query: str,
    entry: Classic5Entry,
    method: str | None,
    outcome: str,
    treatment: str,
) -> float:
    score = _score(query, entry)
    entry_method = norm_method(entry.method)
    if method and entry_method and entry_method == method:
        score += _METHOD_BONUS
    q_tokens = _tokens(query)
    score += _var_score(q_tokens, outcome, entry.outcome, entry)
    score += _var_score(q_tokens, treatment, entry.treatment, entry)
    return score

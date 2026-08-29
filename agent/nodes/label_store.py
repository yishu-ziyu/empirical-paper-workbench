"""学习标签落盘：跳出 session 内存，进程关掉还能读。

每条事件是一次通过/否决（人或三位审稿代理）。
训练只用 ``labels`` 字段；``auto_decision`` / ``agreed_with_auto`` 只给对照分析，
禁止把分数写进 labels。
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .learning_labels import assert_no_mock_score, collect_learning_labels

_LOCK = threading.Lock()
_FORBIDDEN = ("reward", "score", "review_score")

REVIEWER_HUMAN = "human"
REVIEWER_PERSONA = "persona_agent"
ARM_HUMAN = "human"
ARM_SEE_AUTO = "see_auto"
ARM_BLIND = "blind"


def default_path() -> Path:
    env = (os.environ.get("LEARNING_LABELS_PATH") or "").strip()
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "data" / "learning_labels.jsonl"


def _strip_forbidden(item: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = dict(item)
    for key in _FORBIDDEN:
        cleaned.pop(key, None)
    return cleaned


def event_from_decision(
    state: Dict[str, Any],
    *,
    decision: str,
    reviewer: Optional[str] = None,
    comment: Optional[str] = None,
    reviewer_kind: str = REVIEWER_HUMAN,
    persona: Optional[str] = None,
    ab_arm: str = ARM_HUMAN,
    auto_decision: Optional[str] = None,
) -> Dict[str, Any]:
    """把一次决策收成可落盘事件。labels 里不含分数。"""
    labels = [_strip_forbidden(item) for item in collect_learning_labels(state)]
    assert_no_mock_score(labels)
    chapter_index = state.get("review_chapter_index")
    if not isinstance(chapter_index, int):
        current = state.get("current_chapter_index") or 0
        chapter_index = current - 1 if isinstance(current, int) else 0
    chapter_type = None
    chapters = state.get("body_chapters") or []
    if isinstance(chapter_index, int) and 0 <= chapter_index < len(chapters):
        chapter = chapters[chapter_index]
        if isinstance(chapter, dict):
            chapter_type = chapter.get("type")
    if auto_decision is None:
        scores = state.get("review_scores") or []
        if isinstance(chapter_index, int) and 0 <= chapter_index < len(scores):
            try:
                auto_decision = "pass" if float(scores[chapter_index]) >= 0.7 else "fail"
            except (TypeError, ValueError):
                auto_decision = None
    agreed = None
    if auto_decision in {"pass", "fail"} and decision in {"accept", "reject"}:
        agreed = (decision == "accept" and auto_decision == "pass") or (
            decision == "reject" and auto_decision == "fail"
        )
    event = {
        "event_id": str(uuid.uuid4()),
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": state.get("session_id"),
        "chapter_index": chapter_index,
        "chapter_type": chapter_type,
        "reviewer": reviewer or state.get("hitl_reviewer"),
        "reviewer_kind": reviewer_kind,
        "persona": persona,
        "ab_arm": ab_arm,
        "decision": decision,
        "comment": comment or state.get("hitl_comment"),
        "auto_decision": auto_decision,
        "agreed_with_auto": agreed,
        "labels": labels,
    }
    return event


def append_event(event: Dict[str, Any], path: Optional[Path] = None) -> Dict[str, Any]:
    """追加一条事件。创建父目录。"""
    labels = event.get("labels") or []
    if not isinstance(labels, list):
        raise ValueError("labels 必须是列表")
    event = {**event, "labels": [_strip_forbidden(item) for item in labels if isinstance(item, dict)]}
    assert_no_mock_score(event["labels"])
    target = path or default_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, ensure_ascii=False)
    with _LOCK:
        with target.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    return event


def read_events(
    path: Optional[Path] = None,
    *,
    session_id: Optional[str] = None,
    reviewer_kind: Optional[str] = None,
    ab_arm: Optional[str] = None,
) -> List[Dict[str, Any]]:
    target = path or default_path()
    if not target.exists():
        return []
    out: List[Dict[str, Any]] = []
    with target.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(item, dict):
                continue
            if session_id and item.get("session_id") != session_id:
                continue
            if reviewer_kind and item.get("reviewer_kind") != reviewer_kind:
                continue
            if ab_arm and item.get("ab_arm") != ab_arm:
                continue
            out.append(item)
    return out


def summarize(events: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """对照分析：谁更容易跟着机器走。"""
    rows = list(events)
    by_arm: Dict[str, List[Dict[str, Any]]] = {}
    by_persona: Dict[str, List[Dict[str, Any]]] = {}
    for item in rows:
        by_arm.setdefault(str(item.get("ab_arm") or "unknown"), []).append(item)
        persona = item.get("persona") or item.get("reviewer_kind") or "unknown"
        by_persona.setdefault(str(persona), []).append(item)

    def _rate(items: List[Dict[str, Any]], field: str) -> Optional[float]:
        flagged = [item for item in items if item.get(field) is not None]
        if not flagged:
            return None
        if field == "reject_rate":
            return round(sum(1 for item in items if item.get("decision") == "reject") / len(items), 3)
        hits = [item for item in flagged if item.get(field) is True]
        return round(len(hits) / len(flagged), 3)

    def _arm_stats(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "n": len(items),
            "reject_rate": round(
                sum(1 for item in items if item.get("decision") == "reject") / len(items), 3
            )
            if items
            else None,
            "agree_with_auto": _rate(items, "agreed_with_auto"),
        }

    return {
        "n": len(rows),
        "by_arm": {key: _arm_stats(val) for key, val in sorted(by_arm.items())},
        "by_persona": {key: _arm_stats(val) for key, val in sorted(by_persona.items())},
    }

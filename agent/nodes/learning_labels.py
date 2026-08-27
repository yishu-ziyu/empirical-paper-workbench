"""#11: 学习标签只从真事件收，不用 mock 综合分当奖励。

四类入口（#2）：
- 人点了否决 / 通过
- 改到顶了仍过不了 0.7
- CHARLS / StatsPAI / 评审 / 文献检索降级
- DOI 对得上；正文 [N] 落在编号表里

标签里禁止出现 reward / score，避免把假分漏进训练。
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from state import EconPaperState

_DOI_RE = re.compile(r"^10\.\d+/\S+")
_CITE_RE = re.compile(r"\[(\d+)\]")
_FORBIDDEN_KEYS = ("reward", "score", "review_score")

HITL_REJECT = "hitl_reject"
HITL_ACCEPT = "hitl_accept"
REVIEW_CAPPED_FAIL = "review_capped_fail"
DEGRADATION = "degradation"
CITATION_UNGROUNDED = "citation_ungrounded"
CITATION_GROUNDED = "citation_grounded"


def _label(source: str, polarity: str, **extra: Any) -> Dict[str, Any]:
    item: Dict[str, Any] = {"source": source, "polarity": polarity}
    item.update(extra)
    for key in _FORBIDDEN_KEYS:
        item.pop(key, None)
    return item


def _hitl_labels(state: EconPaperState) -> List[Dict[str, Any]]:
    decision = str(state.get("hitl_decision") or "").strip()
    chapter = state.get("review_chapter_index")
    if decision == "reject":
        return [_label(HITL_REJECT, "negative", chapter_index=chapter)]
    if decision == "accept":
        return [_label(HITL_ACCEPT, "positive", chapter_index=chapter)]
    return []


def _capped_fail_labels(state: EconPaperState) -> List[Dict[str, Any]]:
    idx = state.get("review_chapter_index")
    scores = state.get("review_scores") or []
    iteration = state.get("review_iteration") or 0
    max_iterations = min(state.get("max_review_iterations", 2), 3)
    if idx is None or not isinstance(idx, int):
        return []
    if idx < 0 or idx >= len(scores):
        return []
    try:
        score = float(scores[idx])
    except (TypeError, ValueError):
        return []
    if iteration >= max_iterations and score < 0.7:
        return [_label(REVIEW_CAPPED_FAIL, "negative", chapter_index=idx)]
    return []


def _degradation_labels(state: EconPaperState) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in state.get("degradations") or []:
        if not isinstance(item, dict):
            continue
        node = str(item.get("node") or "")
        if not node:
            continue
        out.append(_label(DEGRADATION, "negative", node=node))
    if state.get("review_degraded"):
        out.append(_label(DEGRADATION, "negative", node="review_chapter"))
    if state.get("literature_source") == "mock_degraded":
        out.append(_label(DEGRADATION, "negative", node="search_literature"))
    estimate = state.get("estimate")
    if isinstance(estimate, dict) and estimate.get("status") in {"degraded", "error"}:
        out.append(_label(DEGRADATION, "negative", node="estimate"))
    robustness = state.get("robustness_results")
    if isinstance(robustness, dict) and robustness.get("degraded"):
        out.append(_label(DEGRADATION, "negative", node="robustness_check"))
    if state.get("degraded"):
        out.append(_label(DEGRADATION, "negative", node="export_docx"))
    return out


def _citation_labels(state: EconPaperState) -> List[Dict[str, Any]]:
    from nodes.review_sources.structure_checks import check_structure

    chapters = state.get("body_chapters") or []
    indices = state.get("citation_indices")
    out: List[Dict[str, Any]] = []
    for chapter in chapters:
        if not isinstance(chapter, dict) or chapter.get("type") != "lit_review":
            continue
        content = str(chapter.get("content") or "")
        failures = check_structure(
            "lit_review",
            content,
            citation_indices=indices,
        )
        chapter_index = chapter.get("chapter_index")
        if "invented_citation" in failures:
            out.append(
                _label(
                    CITATION_UNGROUNDED,
                    "negative",
                    chapter_index=chapter_index,
                )
            )
            continue
        if not _CITE_RE.search(content):
            continue
        dois_ok = True
        entries = state.get("literature_entries") or []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            doi = entry.get("doi")
            if not doi:
                continue
            if not _DOI_RE.match(str(doi)):
                dois_ok = False
                break
        if dois_ok:
            out.append(
                _label(
                    CITATION_GROUNDED,
                    "positive",
                    chapter_index=chapter_index,
                )
            )
        else:
            out.append(
                _label(
                    CITATION_UNGROUNDED,
                    "negative",
                    chapter_index=chapter_index,
                    reason="doi_unresolvable",
                )
            )
    return out


def collect_learning_labels(state: EconPaperState) -> List[Dict[str, Any]]:
    """从当前 state 抽出可训练事件。不含 mock 分数。"""
    raw = (
        _hitl_labels(state)
        + _capped_fail_labels(state)
        + _degradation_labels(state)
        + _citation_labels(state)
    )
    seen: set = set()
    unique: List[Dict[str, Any]] = []
    for item in raw:
        key = (
            item.get("source"),
            item.get("polarity"),
            item.get("chapter_index"),
            item.get("node"),
            item.get("reason"),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def assert_no_mock_score(labels: List[Dict[str, Any]]) -> None:
    """Fitness：标签不得携带分数当奖励。"""
    for item in labels:
        for key in _FORBIDDEN_KEYS:
            assert key not in item, f"标签禁止带 {key}: {item}"

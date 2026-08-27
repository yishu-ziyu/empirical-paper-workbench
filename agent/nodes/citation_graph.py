"""ADR-0009: 引用图谱构建节点。

Stage 1: 按 (year, title) 升序分配引用编号 [1], [2], ...
Stage 2: 调 Semantic Scholar references API 填充 citation_graph.edges
         ({from: source_doi, to: cited_doi})。
#8: 被引跳先把集外 DOI 写进 literature_entries（仍 <= 20），再留边。
    两端都在扩完后的集合里才保留边。

设计要点（见 docs/adr/0009-citation-graph-and-references.md）：
- API 调用失败时该 entry 的 edges 降级为空（不阻塞 graph）
- API key 从 SEMANTIC_SCHOLAR_API_KEY 读，缺失时全降级为空 edges
- 限制单次构建的 API 调用数（避免 rate limit；MAX_API_CALL_ENTRIES）
- 测试通过 monkeypatch 替换 semantic_scholar_references 为 fake
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from nodes.search_literature import MAX_LITERATURE_ENTRIES, _entry_key, _merge_unique
from protocols import CitationGraphOutput, LiteratureEntry
from state import EconPaperState

# 单次构建最多对多少条文献调 references API
# Semantic Scholar 无 key 限 100 次/5分钟，这里保守取 5
# （文献检索本身已限制 MAX_LITERATURE_ENTRIES=20，5 次足够代表性中心节点）
MAX_API_CALL_ENTRIES = 5

# #8 被引跳：L0 里 citation 最高的几条
CITATION_HOP_TOP_N = 3


def _get_api_key() -> str | None:
    """读 SEMANTIC_SCHOLAR_API_KEY 环境变量。缺失返回 None。"""
    return os.environ.get("SEMANTIC_SCHOLAR_API_KEY")


def _citation_rank(entry: Any) -> tuple:
    """citation 高的在前；没有被引数就看 relevance，再看年份。"""
    cites = entry.get("citation_count")
    if cites is None:
        cites = entry.get("citationCount")
    try:
        cites_n = float(cites or 0)
    except (TypeError, ValueError):
        cites_n = 0.0
    try:
        rel = float(entry.get("relevance_score") or 0)
    except (TypeError, ValueError):
        rel = 0.0
    try:
        year = int(entry.get("year") or 0)
    except (TypeError, ValueError):
        year = 0
    return (cites_n, rel, year)


def _entry_for_cited_doi(doi: str) -> LiteratureEntry:
    """集外被引 DOI → 文献条目。mock 库有就用全文，没有就只留 DOI。"""
    from nodes.literature_sources.mock_corpus import mock_literature_corpus

    for entry in mock_literature_corpus():
        if entry.get("doi") == doi:
            copied = dict(entry)
            return copied
    return LiteratureEntry(
        title=doi,
        authors=[],
        year=0,
        abstract="",
        doi=doi,
        source="citation_hop",
        relevance_score=0.4,
    )


def _fetch_cited_dois(
    doi: str,
    api_key: Optional[str],
    semantic_scholar_references,
) -> Optional[List[str]]:
    """调 references API。失败返回 None，调用方跳过该条。"""
    try:
        cited = semantic_scholar_references(doi=doi, api_key=api_key)
    except Exception:
        return None
    if not cited:
        return []
    return [c for c in cited if isinstance(c, str) and c]


def build_citation_graph(state: EconPaperState) -> CitationGraphOutput:
    """构建引用图谱，并允许被引跳扩展文献集。

    1. 读 literature_entries（L0）
    2. 对 citation 最高的 3 条调 references API，集外 DOI 写入文献集（<= 20）
    3. 为扩完后的文献分配引用编号 [1], [2], ...
    4. 边只保留两端都在扩完后集合里的
    5. 返回 citation_graph + citation_indices + literature_entries
    """
    entries: List[Any] = list(state.get("literature_entries", []) or [])
    if not entries:
        return {
            "citation_graph": {"entries": [], "edges": [], "indices": {}},
            "citation_indices": {},
            "literature_entries": [],
            "literature_actions": list(state.get("literature_actions") or []),
        }

    from nodes.literature_sources.semantic_scholar import (
        semantic_scholar_references,
    )

    api_key = _get_api_key()
    doi_entries = [
        e for e in entries
        if isinstance(e.get("doi"), str) and e.get("doi")
    ]
    hop_targets = sorted(doi_entries, key=_citation_rank, reverse=True)[
        :CITATION_HOP_TOP_N
    ]

    ref_cache: Dict[str, List[str]] = {}
    calls_made = 0
    for entry in hop_targets:
        if calls_made >= MAX_API_CALL_ENTRIES:
            break
        source_doi = entry.get("doi")
        if not source_doi or source_doi in ref_cache:
            continue
        calls_made += 1
        cited = _fetch_cited_dois(source_doi, api_key, semantic_scholar_references)
        if cited is None:
            continue
        ref_cache[source_doi] = cited

    extras: List[LiteratureEntry] = []
    existing = {_entry_key(e) for e in entries if _entry_key(e)}
    for cited_list in ref_cache.values():
        for cited_doi in cited_list:
            if cited_doi in existing:
                continue
            extras.append(_entry_for_cited_doi(cited_doi))
            existing.add(cited_doi)

    expanded = _merge_unique(entries, extras, limit=MAX_LITERATURE_ENTRIES)
    doi_set = {
        e.get("doi") for e in expanded
        if e.get("doi") and isinstance(e.get("doi"), str)
    }

    # 剩余 API 预算：给还没查过的条目补边
    remaining = [
        e for e in expanded
        if isinstance(e.get("doi"), str)
        and e.get("doi")
        and e.get("doi") not in ref_cache
    ]
    remaining_sorted = sorted(
        remaining, key=lambda e: (e.get("year", 0) or 0, e.get("title", "") or "")
    )
    for entry in remaining_sorted:
        if calls_made >= MAX_API_CALL_ENTRIES:
            break
        source_doi = entry.get("doi")
        calls_made += 1
        cited = _fetch_cited_dois(source_doi, api_key, semantic_scholar_references)
        if cited is None:
            continue
        ref_cache[source_doi] = cited

    edges: List[Dict[str, Any]] = []
    for source_doi, cited_list in ref_cache.items():
        if source_doi not in doi_set:
            continue
        for cited_doi in cited_list:
            if cited_doi in doi_set and cited_doi != source_doi:
                edges.append({"from": source_doi, "to": cited_doi})

    sorted_entries = sorted(
        expanded, key=lambda e: (e.get("year", 0) or 0, e.get("title", "") or "")
    )

    citation_indices: Dict[str, int] = {}
    for i, entry in enumerate(sorted_entries, start=1):
        key = entry.get("doi") or entry.get("title", "")
        if not key:
            key = f"__no_key_{i}"
        citation_indices[key] = i

    graph = {
        "entries": sorted_entries,
        "edges": edges,
        "indices": citation_indices,
    }

    actions = list(state.get("literature_actions") or [])
    if extras and "citation_hop" not in actions:
        actions.append("citation_hop")

    return {
        "citation_graph": graph,
        "citation_indices": citation_indices,
        "literature_entries": expanded,
        "literature_actions": actions,
    }

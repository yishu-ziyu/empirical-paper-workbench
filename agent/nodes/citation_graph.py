"""ADR-0009: 引用图谱构建节点。

Stage 1: 按 (year, title) 升序分配引用编号 [1], [2], ...
Stage 2: 调 Semantic Scholar references API 填充 citation_graph.edges
         ({from: source_doi, to: cited_doi})。只在两端 DOI 都在
         literature_entries 内时保留边（去除图谱外的引用噪声）。

设计要点（见 docs/adr/0009-citation-graph-and-references.md）：
- API 调用失败时该 entry 的 edges 降级为空（不阻塞 graph）
- API key 从 SEMANTIC_SCHOLAR_API_KEY 读，缺失时全降级为空 edges
- 限制单次构建的 API 调用数（避免 rate limit；MAX_API_CALL_ENTRIES）
- 测试通过 monkeypatch 替换 semantic_scholar_references 为 fake
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

from protocols import CitationGraphOutput
from state import EconPaperState

# 单次构建最多对多少条文献调 references API
# Semantic Scholar 无 key 限 100 次/5分钟，这里保守取 5
# （文献检索本身已限制 MAX_LITERATURE_ENTRIES=20，5 次足够代表性中心节点）
MAX_API_CALL_ENTRIES = 5


def _get_api_key() -> str | None:
    """读 SEMANTIC_SCHOLAR_API_KEY 环境变量。缺失返回 None。"""
    return os.environ.get("SEMANTIC_SCHOLAR_API_KEY")


def _build_edges_via_api(
    sorted_entries: List[Any],
    doi_set: set[str],
) -> List[Dict[str, Any]]:
    """ADR-0009 Stage 2: 调 Semantic Scholar references API 构建 edges。

    遍历 sorted_entries 中有 DOI 的条目（上限 MAX_API_CALL_ENTRIES），
    调 semantic_scholar_references 获取其引用的 DOI 列表，
    只保留 cited_doi 也在 doi_set 内的边（去除图谱外引用噪声）。

    API 调用失败时该 entry 跳过（不抛异常，降级为该 entry 无出边）。

    Args:
        sorted_entries: 按 (year, title) 排序后的文献条目
        doi_set: 文献条目 DOI 集合（用于过滤边）

    Returns:
        List[{from: source_doi, to: cited_doi}]
    """
    # 延迟 import：避免单测无网络依赖时 import 链触发 API 客户端加载
    # 同时使 monkeypatch.setattr(nodes.citation_graph,
    #   "semantic_scholar_references", fake) 生效
    from nodes.literature_sources.semantic_scholar import (
        semantic_scholar_references,
    )

    api_key = _get_api_key()
    edges: List[Dict[str, Any]] = []
    calls_made = 0

    for entry in sorted_entries:
        if calls_made >= MAX_API_CALL_ENTRIES:
            break
        source_doi = entry.get("doi")
        if not source_doi or not isinstance(source_doi, str):
            continue
        if source_doi not in doi_set:
            # 防御：理论不会触发，sorted_entries 本就来自 literature_entries
            continue

        calls_made += 1
        try:
            cited_dois = semantic_scholar_references(
                doi=source_doi,
                api_key=api_key,
            )
        except Exception:
            # API 失败（网络/限流/解析错误）：该 entry 无出边，继续下一个
            continue

        for cited_doi in cited_dois:
            if cited_doi in doi_set and cited_doi != source_doi:
                edges.append({"from": source_doi, "to": cited_doi})

    return edges


def build_citation_graph(state: EconPaperState) -> CitationGraphOutput:
    """构建引用图谱。

    1. 读 literature_entries
    2. 为每条文献分配引用编号 [1], [2], ...（按年份升序，同年按 title 字母序）
    3. Stage 2: 调 Semantic Scholar references API 构建 edges（{from, to}）
       - API key 缺失或调用失败时 edges 为空（降级，不阻塞）
       - 只保留两端 DOI 都在图谱内的边
    4. 返回 citation_graph + citation_indices
    """
    entries: List[Any] = state.get("literature_entries", []) or []
    if not entries:
        return {
            "citation_graph": {"entries": [], "edges": [], "indices": {}},
            "citation_indices": {},
        }

    # 按 (year, title) 排序分配编号
    sorted_entries = sorted(
        entries, key=lambda e: (e.get("year", 0) or 0, e.get("title", "") or "")
    )

    citation_indices: Dict[str, int] = {}
    for i, entry in enumerate(sorted_entries, start=1):
        key = entry.get("doi") or entry.get("title", "")
        if not key:
            # 兜底：用 index 作 key（避免空 key 互相覆盖）
            key = f"__no_key_{i}"
        citation_indices[key] = i

    # Stage 2: Semantic Scholar references API 构建真实引用关系边
    doi_set = {
        e.get("doi") for e in sorted_entries
        if e.get("doi") and isinstance(e.get("doi"), str)
    }
    edges = _build_edges_via_api(sorted_entries, doi_set)

    graph = {
        "entries": sorted_entries,
        "edges": edges,
        "indices": citation_indices,
    }

    return {
        "citation_graph": graph,
        "citation_indices": citation_indices,
    }

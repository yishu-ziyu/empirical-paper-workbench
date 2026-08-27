"""ADR-0004 Stage 3/4: 文献检索节点。

基于 research_direction 派生查询，检索相关文献，
为 generate_outline 的 lit_review 章节提供素材。

pytest / ECONPAPER_LLM=mock 走 mock 文献库。
运行时最后一档是 Crossref（取代 ADR-0010「默认 mock」）。
literature_source 可切：mock / crossref / semantic_scholar / apodex /
disabled。apodex 为两周免费 API 耗材实验，无 key / 失败降级 mock_degraded。
crossref / semantic_scholar 失败降级 mock_degraded。
"""
from __future__ import annotations

from typing import Any, List

from protocols import LiteratureEntry, LiteratureOutput
from state import EconPaperState

# 文献检索限长（Fitness Function）
MAX_LITERATURE_ENTRIES = 20

# 运行时常量：是否启用文献检索（不入 state）
LITERATURE_ENABLED = True


def resolve_literature_source(state: EconPaperState) -> str:
    """显式 state → pytest / ECONPAPER_LLM=mock → LITERATURE_SOURCE → crossref。

    运行时最后一档是 crossref，取代 ADR-0010「默认 mock」。
    """
    import os

    from llm.ssot import in_pytest

    explicit = str(state.get("literature_source") or "").strip()
    if explicit:
        return explicit
    if in_pytest() or os.environ.get("ECONPAPER_LLM") == "mock":
        return "mock"
    env = (os.environ.get("LITERATURE_SOURCE") or "").strip()
    if env:
        return env
    return "crossref"


def _build_query(research_direction: Any, title: str = "") -> str:
    """从研究方向四问派生检索查询。title 参数保留兼容，不拼进查询。"""
    parts: List[str] = []
    if isinstance(research_direction, str) and research_direction.strip():
        parts.append(research_direction.strip())
    elif isinstance(research_direction, dict):
        for key in ("question", "method", "dv", "iv"):
            val = research_direction.get(key)
            if isinstance(val, str) and val.strip():
                parts.append(val.strip())
            elif isinstance(val, list):
                parts.extend(str(v) for v in val if v)
    return " ".join(parts) if parts else "economics"


def _mock_search(query: str) -> List[LiteratureEntry]:
    """Stage 3: 用 mock_literature_corpus + filter_by_query 检索。

    lazy import 避免循环依赖。返回按 query 关键词匹配后的文献列表，
    每条 relevance_score 已按命中次数调整。
    """
    from nodes.literature_sources.mock_corpus import (
        filter_by_query,
        mock_literature_corpus,
    )

    corpus = mock_literature_corpus()
    return filter_by_query(corpus, query)


def search_literature(state: EconPaperState) -> LiteratureOutput:
    """基于 research_direction 检索文献。

    1. 从 state['research_direction'] 派生 literature_query（不拼标题）；
    2. 按 literature_source 配置分发：
       - "disabled"：返回空列表（保持 graph 拓扑稳定）
       - "crossref"：Crossref works search（失败降级 mock_degraded）
       - "semantic_scholar"：调真实 API（无 API key 或调用失败时降级为 "mock_degraded"）
       - 其他（pytest 默认 "mock"；运行时默认 "crossref"）：用对应源
    3. 去重（按 doi 或 title 规范化）；
    4. 限长 <= MAX_LITERATURE_ENTRIES；
    5. 返回 LiteratureOutput（不含 outline / body_chapters）。

    降级路径（Stage 4）：
    - SEMANTIC_SCHOLAR_API_KEY 缺失但 literature_source == "semantic_scholar"
      → 用 mock 文献库，literature_source 标记为 "mock_degraded"
    - API 调用失败（网络/HTTP 错误）
      → 用 mock 文献库，literature_source 标记为 "mock_degraded"
    """
    research_direction = state.get("research_direction", "")
    query = _build_query(research_direction)
    source = resolve_literature_source(state)

    if source == "disabled":
        return {
            "literature_entries": [],
            "literature_query": query,
            "literature_source": "disabled",
            "literature_produced_by": "search_literature",
        }

    # 按 literature_source 分发。pytest 默认 mock；运行时默认 crossref。
    # crossref / semantic_scholar 失败一律降级 mock_degraded。
    effective_source = source
    if source == "apodex":
        from nodes.literature_sources.apodex import (
            get_api_key_from_env,
            apodex_search,
        )

        api_key = get_api_key_from_env()
        if not api_key:
            entries = _mock_search(query)
            effective_source = "mock_degraded"
        else:
            try:
                entries = apodex_search(query, api_key)
            except RuntimeError:
                entries = _mock_search(query)
                effective_source = "mock_degraded"
    elif source == "semantic_scholar":
        from nodes.literature_sources.semantic_scholar import (
            get_api_key_from_env,
            semantic_scholar_search,
        )

        api_key = get_api_key_from_env()
        if not api_key:
            entries = _mock_search(query)
            effective_source = "mock_degraded"
        else:
            try:
                entries = semantic_scholar_search(query, api_key)
            except RuntimeError:
                entries = _mock_search(query)
                effective_source = "mock_degraded"
    elif source == "crossref":
        from nodes.literature_sources.crossref import crossref_search

        try:
            entries = crossref_search(query)
        except RuntimeError:
            entries = _mock_search(query)
            effective_source = "mock_degraded"
    else:
        entries = _mock_search(query)

    # 去重（按 doi 或 title 规范化）
    seen: set = set()
    unique: List[LiteratureEntry] = []
    for e in entries:
        key = e.get("doi") or (e.get("title", "").lower().strip() if e.get("title") else "")
        if key and key not in seen:
            seen.add(key)
            unique.append(e)

    # 限长
    unique = unique[:MAX_LITERATURE_ENTRIES]

    return {
        "literature_entries": unique,
        "literature_query": query,
        "literature_source": effective_source,
        "literature_produced_by": "search_literature",
    }

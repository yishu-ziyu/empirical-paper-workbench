"""ADR-0004 Stage 3/4: 文献检索节点。

基于 research_direction + title_chapter.title 派生查询，检索相关文献，
为 generate_outline 的 lit_review 章节提供素材。

Stage 3 用 mock 文献库（nodes.literature_sources.mock_corpus，30 条经济学顶刊
条目覆盖 5 子领域）；Stage 4 可选接 Semantic Scholar API（按 literature_source
配置分发：mock / semantic_scholar / disabled）。
"""
from __future__ import annotations

from typing import Any, List

from protocols import LiteratureEntry, LiteratureOutput
from state import EconPaperState

# 文献检索限长（Fitness Function）
MAX_LITERATURE_ENTRIES = 20

# 运行时常量：是否启用文献检索（不入 state）
LITERATURE_ENABLED = True


def _build_query(research_direction: Any, title: str) -> str:
    """从 research_direction + title 派生检索查询。

    research_direction 兼容两种形态：
    - str：直接拼接（测试用例 / 简化场景）
    - dict：取 question（或 method）字段拼接（set_direction 节点产出形态）
    - 其他：忽略
    """
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
    if title and isinstance(title, str) and title.strip():
        parts.append(title.strip())
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

    1. 从 state['research_direction'] + state['title_chapter'].title 派生 literature_query；
    2. 按 literature_source 配置分发：
       - "disabled"：返回空列表（保持 graph 拓扑稳定）
       - "semantic_scholar"：调真实 API（无 API key 或调用失败时降级为 "mock_degraded"）
       - 其他（默认 "mock"）：用 mock 文献库
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
    title_chapter = state.get("title_chapter", {})
    title = title_chapter.get("title", "") if isinstance(title_chapter, dict) else ""

    query = _build_query(research_direction, title)
    source = state.get("literature_source", "mock")

    if source == "disabled":
        return {
            "literature_entries": [],
            "literature_query": query,
            "literature_source": "disabled",
        }

    # Stage 4: 按 literature_source 分发
    effective_source = source
    if source == "semantic_scholar":
        # lazy import 避免循环依赖 / 启动时网络副作用
        from nodes.literature_sources.semantic_scholar import (
            get_api_key_from_env,
            semantic_scholar_search,
        )

        api_key = get_api_key_from_env()
        if not api_key:
            # 降级：无 API key，用 mock
            entries = _mock_search(query)
            effective_source = "mock_degraded"
        else:
            try:
                entries = semantic_scholar_search(query, api_key)
            except RuntimeError:
                # 降级：API 调用失败，用 mock
                entries = _mock_search(query)
                effective_source = "mock_degraded"
    else:
        # 默认 mock
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
    }

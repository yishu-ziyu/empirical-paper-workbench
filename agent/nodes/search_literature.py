"""ADR-0004 Stage 3/4: 文献检索节点。

基于 research_direction 派生查询，检索相关文献，
为 generate_outline 的 lit_review 章节提供素材。

pytest / ECONPAPER_LLM=mock 走 mock 文献库。
运行时最后一档是 Crossref（取代 ADR-0010「默认 mock」）。
literature_source 可切：mock / crossref / semantic_scholar / disabled。
crossref / semantic_scholar 失败降级 mock_degraded。

#8：词袋一枪之后硬编码两跳——方法锚 + 该方法的威胁，不让模型自由写 query。
"""
from __future__ import annotations

from typing import Any, Iterable, List, Optional, Tuple

from protocols import LiteratureEntry, LiteratureOutput
from state import EconPaperState

# 文献检索限长（Fitness Function）
MAX_LITERATURE_ENTRIES = 20

# 运行时常量：是否启用文献检索（不入 state）
LITERATURE_ENABLED = True

# mock 库里的方法锚（#8 识别锚跳）。key 与 design.spec.norm_method 对齐。
METHOD_ANCHOR_DOIS = {
    "did": "10.1016/j.jeconom.2022.019",  # Callaway–Sant'Anna
    "iv": "10.1016/j.jeconom.2021.020",  # Stock–Yogo
    "rd": "10.1016/j.jeconom.2020.021",  # Lee–Lemieux
}

# 该方法的威胁（#8 反证跳）。空格分词，命中 mock 摘要里已有的词。
METHOD_THREAT_QUERIES = {
    "did": "交错 DID staggered treatment",
    "iv": "弱工具 weak instruments",
    "rd": "断点操纵 discontinuity manipulation",
}


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


def _entry_key(entry: Any) -> str:
    """去重键：优先 doi，否则 title 小写。"""
    doi = entry.get("doi") if isinstance(entry, dict) else None
    if doi and isinstance(doi, str) and doi.strip():
        return doi.strip()
    title = entry.get("title", "") if isinstance(entry, dict) else ""
    return (title or "").lower().strip()


def _merge_unique(
    *groups: Iterable[Any],
    limit: int = MAX_LITERATURE_ENTRIES,
) -> List[LiteratureEntry]:
    """按组优先级合并去重，先出现的留下，总长 <= limit。"""
    seen: set = set()
    unique: List[LiteratureEntry] = []
    for group in groups:
        for entry in group or []:
            key = _entry_key(entry)
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(entry)
            if len(unique) >= limit:
                return unique
    return unique


def _method_family(research_direction: Any) -> Optional[str]:
    """把研究方向的 method 收成 did / iv / rd。对不上就当没有。"""
    method = ""
    if isinstance(research_direction, dict):
        method = str(research_direction.get("method") or "")
    elif isinstance(research_direction, str):
        method = research_direction

    try:
        from design.spec import norm_method

        key = norm_method(method)
        if key in METHOD_ANCHOR_DOIS:
            return key
        if key == "rdd":
            return "rd"
    except Exception:
        pass

    raw = (method or "").strip().lower()
    if not raw:
        return None
    if raw in {"did", "rdd", "rd", "iv"}:
        return "rd" if raw in {"rd", "rdd"} else raw
    if "did" in raw or "双重差分" in raw:
        return "did"
    if "工具变量" in raw or raw == "2sls":
        return "iv"
    if "断点" in raw or "rdd" in raw:
        return "rd"
    return None


def _method_anchors(family: Optional[str]) -> List[LiteratureEntry]:
    """从 mock 库取出该方法的锚点论文。库里没有就空。"""
    if not family:
        return []
    doi = METHOD_ANCHOR_DOIS.get(family)
    if not doi:
        return []
    from nodes.literature_sources.mock_corpus import mock_literature_corpus

    for entry in mock_literature_corpus():
        if entry.get("doi") == doi:
            return [dict(entry)]
    return []


def _dispatch_search(query: str, source: str) -> Tuple[List[LiteratureEntry], str]:
    """按源检索。失败降级 mock_degraded，不往外抛。"""
    if source == "semantic_scholar":
        from nodes.literature_sources.semantic_scholar import (
            get_api_key_from_env,
            semantic_scholar_search,
        )

        api_key = get_api_key_from_env()
        if not api_key:
            return _mock_search(query), "mock_degraded"
        try:
            return semantic_scholar_search(query, api_key), "semantic_scholar"
        except RuntimeError:
            return _mock_search(query), "mock_degraded"
    if source == "crossref":
        from nodes.literature_sources.crossref import crossref_search

        try:
            return crossref_search(query), "crossref"
        except RuntimeError:
            return _mock_search(query), "mock_degraded"
    return _mock_search(query), source


def search_literature(state: EconPaperState) -> LiteratureOutput:
    """基于 research_direction 检索文献。

    1. 从 state['research_direction'] 派生 literature_query（不拼标题）；
    2. 按 literature_source 配置分发：
       - "disabled"：返回空列表（保持 graph 拓扑稳定）
       - "crossref"：Crossref works search（失败降级 mock_degraded）
       - "semantic_scholar"：调真实 API（无 API key 或调用失败时降级为 "mock_degraded"）
       - 其他（pytest 默认 "mock"；运行时默认 "crossref"）：用对应源
    3. #8 方法锚跳 + 反证跳（硬编码，不让模型写 query）；
    4. 去重（按 doi 或 title 规范化）；
    5. 限长 <= MAX_LITERATURE_ENTRIES；
    6. 返回 LiteratureOutput（不含 outline / body_chapters）。

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

    entries, effective_source = _dispatch_search(query, source)

    family = _method_family(research_direction)
    anchors = _method_anchors(family)
    threat: List[LiteratureEntry] = []
    if family:
        threat_query = METHOD_THREAT_QUERIES.get(family, "")
        if threat_query:
            threat_source = (
                "mock"
                if effective_source in {"mock", "mock_degraded"}
                else source
            )
            threat, _threat_src = _dispatch_search(threat_query, threat_source)

    unique = _merge_unique(anchors, entries, threat)

    return {
        "literature_entries": unique,
        "literature_query": query,
        "literature_source": effective_source,
        "literature_produced_by": "search_literature",
    }

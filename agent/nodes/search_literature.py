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

import json
import re
from typing import Any, Dict, List, Mapping

from protocols import LiteratureEntry, LiteratureOutput
from state import EconPaperState

_STANCES = ("支持", "不支持", "说不清")
_STANCE_SET = frozenset(_STANCES)

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


def doi_to_url(doi: Any) -> str:
    """有 DOI 才拼 https://doi.org/{doi}，否则空串。"""
    raw = str(doi or "").strip()
    if not raw:
        return ""
    lower = raw.lower()
    if "doi.org/" in lower:
        tail = raw.split("doi.org/", 1)[-1].lstrip("/")
        return f"https://doi.org/{tail}" if tail else ""
    if lower.startswith("doi:"):
        raw = raw[4:].strip()
    raw = raw.lstrip("/")
    if raw.lower().startswith("10."):
        return f"https://doi.org/{raw}"
    return ""


def _question_from_state(state: Mapping[str, Any]) -> str:
    rd = state.get("research_direction")
    if isinstance(rd, dict):
        return str(rd.get("question") or "").strip()
    if isinstance(rd, str):
        return rd.strip()
    return ""


def _parse_stances(text: str, n: int) -> Dict[int, str]:
    """从模型输出抽出每篇立场。对不上篇数或词不在三选一里则丢弃。"""
    blob = (text or "").strip()
    if not blob or n <= 0:
        return {}
    data: Any = None
    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", blob, re.S)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                data = None
    if not isinstance(data, list) or len(data) != n:
        return {}
    out: Dict[int, str] = {}
    for i, item in enumerate(data):
        if isinstance(item, str):
            stance = item.strip()
        elif isinstance(item, dict):
            stance = str(item.get("stance") or item.get("label") or "").strip()
        else:
            continue
        if stance in _STANCE_SET:
            out[i] = stance
    return out


def attach_stances(entries: List[LiteratureEntry], question: str) -> None:
    """对照研究方向给每篇标立场。失败不加 stance，不改写章门。"""
    if not question or not entries:
        return
    lines = []
    for i, entry in enumerate(entries, start=1):
        title = str(entry.get("title") or "").strip()
        abstract = str(entry.get("abstract") or "").strip()[:400]
        lines.append(f"{i}. {title}\n{abstract}")
    prompt = (
        "研究方向：\n"
        f"{question}\n\n"
        "下面每篇文献，只根据标题和摘要，判断它对这个研究方向是"
        "「支持」「不支持」还是「说不清」。\n"
        "对照的是研究方向，不是尚未写下的综述句子。\n\n"
        + "\n\n".join(lines)
        + "\n\n只返回 JSON 数组，长度必须等于文献篇数，"
        "每项只能是 支持、不支持、说不清 之一。不要其它文字。"
    )
    try:
        from llm.call_llm import call_llm

        text = call_llm(prompt, node_type="default")
    except Exception:
        return
    parsed = _parse_stances(text, len(entries))
    for i, stance in parsed.items():
        entries[i]["stance"] = stance


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
    unique = [dict(e) for e in unique[:MAX_LITERATURE_ENTRIES]]
    for entry in unique:
        entry["url"] = doi_to_url(entry.get("doi"))
    attach_stances(unique, _question_from_state(state))

    return {
        "literature_entries": unique,
        "literature_query": query,
        "literature_source": effective_source,
        "literature_produced_by": "search_literature",
    }

"""ADR-0004 Stage 4: Semantic Scholar API 客户端。

真实文献检索，支持 API key 与无 key 两种模式。
无 key 时受 rate limit（100 次/5分钟）；有 key 时更高。

设计要点：
- 用 urllib 标准库（不引入 requests 等第三方依赖，保持轻量）
- 超时 10 秒（避免网络问题阻塞 graph）
- relevance_score 按返回顺序递减（Semantic Scholar 默认按相关性排序）
- DOI 可能为 None（externalIds 里不一定有 DOI）
- 失败抛 RuntimeError，由 search_literature 节点捕获并降级
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import List, Optional

from ...protocols import LiteratureEntry


# Semantic Scholar Graph API - paper search endpoint
SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
# 请求字段：title / authors / year / abstract / externalIds（含 DOI）
SEMANTIC_SCHOLAR_FIELDS = "title,authors,year,abstract,externalIds"
# 单次请求最大返回数（API 上限 100，这里保守取 20，与 MAX_LITERATURE_ENTRIES 对齐）
MAX_RESULTS = 20
# HTTP 超时秒数（避免网络问题阻塞 graph）
HTTP_TIMEOUT_SECONDS = 10


def semantic_scholar_search(
    query: str,
    api_key: Optional[str] = None,
    max_results: int = MAX_RESULTS,
) -> List[LiteratureEntry]:
    """调用 Semantic Scholar API 检索文献。

    Args:
        query: 检索查询串
        api_key: 可选 API key（无则受 rate limit：100 次/5分钟）
        max_results: 最大返回数（<= MAX_RESULTS=20）

    Returns:
        List[LiteratureEntry]，每项含 title/authors/year/abstract/doi/
        source/relevance_score。relevance_score 按返回顺序递减（最低 0.3）。

    Raises:
        RuntimeError: API 调用失败（网络/HTTP 错误/JSON 解析错误）
    """
    if not query or not query.strip():
        return []

    params = urllib.parse.urlencode(
        {
            "query": query,
            "limit": min(max_results, MAX_RESULTS),
            "fields": SEMANTIC_SCHOLAR_FIELDS,
        }
    )
    url = f"{SEMANTIC_SCHOLAR_BASE}?{params}"

    headers = {"Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
    except Exception as e:
        raise RuntimeError(f"Semantic Scholar API 调用失败: {e}") from e

    papers = data.get("data", []) or []
    entries: List[LiteratureEntry] = []
    for i, paper in enumerate(papers):
        # relevance_score 按返回顺序递减（Semantic Scholar 默认按相关性排序）
        # 最低 0.3，与 mock_corpus filter_by_query 的下限对齐
        score = max(0.3, 1.0 - i * 0.05)
        authors = [
            a.get("name", "")
            for a in (paper.get("authors") or [])
            if a.get("name")
        ]
        external_ids = paper.get("externalIds") or {}
        doi = external_ids.get("DOI")

        entries.append(
            LiteratureEntry(
                title=paper.get("title", "") or "",
                authors=authors,
                year=paper.get("year") or 0,
                abstract=paper.get("abstract", "") or "",
                doi=doi,
                source="semantic_scholar",
                relevance_score=score,
            )
        )

    return entries


def get_api_key_from_env() -> Optional[str]:
    """从环境变量读 SEMANTIC_SCHOLAR_API_KEY。

    缺失时返回 None，调用方应据此降级为 mock_degraded。
    """
    return os.environ.get("SEMANTIC_SCHOLAR_API_KEY")


# ADR-0009 Stage 2: Semantic Scholar references endpoint
# 获取某篇论文引用的其他论文（references），用于构建 citation_graph.edges
SEMANTIC_SCHOLAR_REFS_URL = "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
SEMANTIC_SCHOLAR_REFS_FIELDS = "externalIds,title"


def semantic_scholar_references(
    doi: str,
    api_key: Optional[str] = None,
    max_results: int = MAX_RESULTS,
) -> List[str]:
    """ADR-0009 Stage 2: 获取某篇 DOI 论文引用的其他论文 DOI 列表。

    调 Semantic Scholar references endpoint，返回被引用论文的 DOI 列表。
    用于构建 citation_graph.edges（{from: doi, to: doi}）。

    Args:
        doi: 查询论文的 DOI（如 "10.1/xxx"）
        api_key: 可选 API key
        max_results: 最大返回数

    Returns:
        List[str]: 被引用论文的 DOI 列表（可能为空）

    Raises:
        RuntimeError: API 调用失败
    """
    if not doi or not doi.strip():
        return []

    # Semantic Scholar 用 DOI: 前缀作为 paper_id
    paper_id = f"DOI:{doi}"
    url = SEMANTIC_SCHOLAR_REFS_URL.format(paper_id=urllib.parse.quote(paper_id, safe=""))
    params = urllib.parse.urlencode(
        {"limit": min(max_results, MAX_RESULTS), "fields": SEMANTIC_SCHOLAR_REFS_FIELDS}
    )
    full_url = f"{url}?{params}"

    headers = {"Accept": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
    except Exception as e:
        raise RuntimeError(f"Semantic Scholar references API 调用失败: {e}") from e

    refs = data.get("data", []) or []
    cited_dois: List[str] = []
    for ref in refs:
        cited_paper = ref.get("citedPaper") or {}
        external_ids = cited_paper.get("externalIds") or {}
        cited_doi = external_ids.get("DOI")
        if cited_doi:
            cited_dois.append(cited_doi)

    return cited_dois

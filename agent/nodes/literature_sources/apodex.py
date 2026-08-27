"""Apodex 深搜文献源（OpenAI 兼容端点）——两周免费 API 耗材实验。

设计边界（与 crossref / semantic_scholar 源一致，stdlib only）：
- 无 APODEX_API_KEY 或调用失败 → search_literature 降级 mock_degraded
- 本模块对产品是可选旁路，**不构成任何硬依赖**；key 过期即自然退场
- 响应契约：POST {base}/chat/completions，要求模型只输出 JSON 数组，
  每项 {title, authors[], year, doi?, abstract?}；摘要/开放全文的
  精读旁路留给后续 ticket（当前仅条目级）
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, List

FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)
HTTP_TIMEOUT_SECONDS = 60
MAX_RESULTS = 20


def get_api_key_from_env() -> str | None:
    key = (os.environ.get("APODEX_API_KEY") or "").strip()
    return key or None


def _base_url() -> str:
    return (os.environ.get("APODEX_BASE_URL") or "https://api.apodex.ai/v1").rstrip("/")


def _model() -> str:
    return (os.environ.get("APODEX_MODEL") or "apodex-1.1").strip()


def parse_entries(payload: dict[str, Any]) -> List[dict[str, Any]]:
    """把 chat.completions 响应解成 LiteratureEntry 列表。

    宽进严出：内容外层允许 \u200b```json 围栏；丢无 title 项；
    year 字符串强转 int；authors 单字符串视作单作者。
    解析失败抛 ValueError（调用方包成 RuntimeError 走降级）。
    """
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("apodex: empty choices")
    message = (choices[0] or {}).get("message") or {}
    raw = str(message.get("content") or "")
    cleaned = FENCE_RE.sub("", raw).strip()
    start, end = cleaned.find("["), cleaned.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("apodex: no JSON array in content")
    items = json.loads(cleaned[start : end + 1])
    if not isinstance(items, list):
        raise ValueError("apodex: content is not an array")

    entries: List[dict[str, Any]] = []
    for item in items[:MAX_RESULTS]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        authors = item.get("authors")
        if isinstance(authors, str):
            authors = [authors]
        if not isinstance(authors, list):
            authors = []
        try:
            year = int(str(item.get("year")).strip())
        except (TypeError, ValueError):
            year = None
        entry: dict[str, Any] = {
            "title": title,
            "authors": [str(a) for a in authors if str(a).strip()][:8],
            "year": year,
            "source": "apodex",
            "relevance_score": 1.0,
        }
        doi = str(item.get("doi") or "").strip()
        if doi:
            entry["doi"] = doi
        abstract = str(item.get("abstract") or "").strip()
        if abstract:
            entry["abstract"] = abstract[:500]
        entries.append(entry)
    return entries


def apodex_search(query: str, api_key: str) -> List[dict[str, Any]]:
    """调 Apodex OpenAI 兼容端点做深搜，返回规范条目列表。

    网络/HTTP/解析任何一环失败都抛 RuntimeError，由节点层统一降级。
    """
    body = json.dumps(
        {
            "model": _model(),
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a bibliographic search assistant for "
                        "empirical economics. Return ONLY a JSON array of "
                        "real, verifiable papers. Each item: {title, authors "
                        "(array of surnames), year, doi if known, abstract "
                        "(<=2 sentences)}. No prose, no markdown fences."
                    ),
                },
                {"role": "user", "content": f"Find key papers about: {query}"},
            ],
            "temperature": 0.2,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{_base_url()}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"apodex search failed: {exc}") from exc
    try:
        return parse_entries(payload)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

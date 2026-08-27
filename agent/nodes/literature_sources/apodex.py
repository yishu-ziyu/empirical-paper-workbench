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
# 免费核心模型思维链很重，完整响应可达数分钟：默认 4 分钟，
# 环境变量 APODEX_TIMEOUT_SECONDS 可调。
HTTP_TIMEOUT_SECONDS = int(os.environ.get("APODEX_TIMEOUT_SECONDS") or 240)
MAX_RESULTS = 20


def get_api_key_from_env() -> str | None:
    key = (os.environ.get("APODEX_API_KEY") or "").strip()
    return key or None


def _base_url() -> str:
    return (os.environ.get("APODEX_BASE_URL") or "https://api.apodex.ai/v1").rstrip("/")


def _model() -> str:
    """默认用两周免费的 核心 模型（平台横幅：Apodex 1.1 / 1.1 Mini
    API 免费两周）。带 *deep-research / *deep-solve 后缀的属于
    Deep Research 计费线（限时 8 折，仍收费），绝不作默认。
    可用清单以 GET /v1/models 为准。"""
    return (os.environ.get("APODEX_MODEL") or "apodex-1.1").strip()


def _iter_top_level_objects(text: str):
    """依次产出连排 JSON 文本里的每个完整对象（Extra-data 安全）。"""
    decoder = json.JSONDecoder()
    i = 0
    while True:
        b = text.find("{", i)
        if b == -1:
            return
        try:
            obj, end = decoder.raw_decode(text, b)
        except json.JSONDecodeError:
            i = b + 1
            continue
        yield obj
        i = end


def _collect_content_strings(node: Any, out: List[str]) -> None:
    """递归收集 content / reasoning_content 字符串字段。

    免费核心模型思考很重，截断场景下最终数组可能只存在于
    reasoning_content 尾部——一并扫描。
    """
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("content", "reasoning_content") and isinstance(v, str):
                out.append(v)
            else:
                _collect_content_strings(v, out)
    elif isinstance(node, list):
        for item in node:
            _collect_content_strings(item, out)


def _scan_arrays(text: str):
    """单段文本扫所有合法顶层数组。空数组不算命中（噪声如 choices:[]），
    但记录出现过；全部为空时返回 [] 由调用方判语义。"""
    decoder = json.JSONDecoder()
    best: list | None = None
    saw_any = False
    i = 0
    while True:
        b = text.find("[", i)
        if b == -1:
            return best if best is not None else ([] if saw_any else None)
        try:
            obj, end = decoder.raw_decode(text, b)
        except json.JSONDecodeError:
            i = b + 1
            continue
        i = end
        if not isinstance(obj, list):
            continue
        saw_any = True
        if obj and (best is None or len(obj) > len(best)):
            best = obj


def _is_entry_array(arr: Any) -> bool:
    """文献数组：成员是带非空 title 字符串的 dict（数量过半即认）。"""
    if not isinstance(arr, list) or not arr:
        return False
    dicts = [x for x in arr if isinstance(x, dict)]
    if len(dicts) < max(1, len(arr) // 2):
        return False
    titled = sum(1 for x in dicts if str(x.get("title") or "").strip())
    return titled >= max(1, len(dicts) // 2)


def _best_array_among(texts: List[str]) -> list | None:
    """优先选"像文献数组"的候选；没有才退回最大普通数组；全空返回 []。"""
    best_shaped: list | None = None
    best_plain: list | None = None
    saw_any = False
    for t in texts:
        found = _scan_arrays(t or "")
        if found is None:
            continue
        for arr in ([found] if not isinstance(found, list) else [found]):
            if not isinstance(arr, list):
                continue
            saw_any = True
            if _is_entry_array(arr):
                if best_shaped is None or len(arr) > len(best_shaped):
                    best_shaped = arr
            elif arr and (best_plain is None or len(arr) > len(best_plain)):
                best_plain = arr
    if best_shaped is not None:
        return best_shaped
    if best_plain is not None:
        return best_plain
    return [] if saw_any else None


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
    # 深研模型可能无视"只输出数组"的指令：内容混 prose / 围栏 / 连排
    # JSON。候选文本 = 整段 + 所有递归收集到的 content 字符串；
    # 各自扫合法顶层数组，取元素最多的那份——宁解析，不因形态炸掉。
    candidates = [cleaned]
    inner: List[str] = []
    _collect_content_strings({"choices": choices}, inner)
    # 连排 JSON 体：逐个解出顶层对象再收里面的 content（转义内层数组只有
    # 解析后才可见）
    for obj in _iter_top_level_objects(cleaned):
        _collect_content_strings(obj, inner)
    candidates.extend(inner)
    best = _best_array_among(candidates)
    if not isinstance(best, list):
        raise ValueError("apodex: no JSON array in content")
    items = best

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


def _assemble_sse(raw: bytes) -> str:
    """把 text/event-stream 的增量 chunk 拼成完整 assistant 内容。

    只认 data: 行；跳过 [DONE] 与不含 content 的 delta（如
    reasoning_steps 思维流）；非 SSE JSON 体原样返回文本（交上层解析）。
    """
    text = raw.decode("utf-8", errors="replace")
    stripped = text.lstrip()
    if not stripped.startswith("data:") and not stripped.startswith("event:"):
        return text
    parts: List[str] = []
    for line in stripped.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload_text = line[len("data:"):].strip()
        if not payload_text or payload_text == "[DONE]":
            continue
        try:
            chunk = json.loads(payload_text)
        except json.JSONDecodeError:
            continue
        choices = chunk.get("choices") or []
        if not choices:
            continue
        delta = (choices[0] or {}).get("delta") or {}
        piece = delta.get("content")
        if isinstance(piece, str):
            parts.append(piece)
    return "".join(parts)


def _max_tokens() -> int:
    """免费核心模型思考很重（实测 6k 上限会在思维链中途截断），
    两周窗口内这两个模型不产生费用，默认放宽到 20000；可用环境变量
    APODEX_MAX_TOKENS 覆盖。"""
    raw = (os.environ.get("APODEX_MAX_TOKENS") or "").strip()
    return int(raw) if raw.isdigit() else 20000


def apodex_search(query: str, api_key: str) -> List[dict[str, Any]]:
    """调 Apodex OpenAI 兼容端点做深搜，返回规范条目列表。

    网络/HTTP/解析任何一环失败都抛 RuntimeError，由节点层统一降级。
    服务端可能无视 stream:false 强推 SSE——两种响应形态都能吃。
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
            "stream": False,
            "max_tokens": _max_tokens(),
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
            raw = resp.read()
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {
                "choices": [
                    {"message": {"content": _assemble_sse(raw)}}
                ]
            }
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"apodex search failed: {exc}") from exc
    try:
        return parse_entries(payload)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

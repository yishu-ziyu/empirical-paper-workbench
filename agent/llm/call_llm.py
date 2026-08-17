"""统一 LLM 调用入口。

mock：返回各节点原来的占位串，单测语义不变。
其他 provider：OpenAI 兼容 POST /chat/completions（本机默认 MiniMax）。
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Optional

from .router import router, LLMConfig

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_THINK_OPEN = re.compile(r"<think>.*", re.DOTALL | re.IGNORECASE)

_MOCK_TEXT = {
    "title": "Placeholder Title from LLM",
    "outline": "Placeholder outline from LLM",
    "generate": "Placeholder chapter content from LLM",
    "review": "Mock LLM response",
    "default": "Mock LLM response",
}


def _strip_think(text: str) -> str:
    cleaned = _THINK_BLOCK.sub("", text)
    cleaned = _THINK_OPEN.sub("", cleaned)
    return cleaned.strip()


def _extract_content(payload: object) -> str:
    if not isinstance(payload, dict):
        raise RuntimeError("LLM 响应不是 JSON 对象")
    choices = payload.get("choices") or []
    if not choices:
        raise RuntimeError("LLM 响应没有 choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") in ("text", "output_text"):
                parts.append(str(item.get("text") or ""))
            elif isinstance(item, str):
                parts.append(item)
        content = "".join(parts)
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("LLM 响应没有文本")
    cleaned = _strip_think(content)
    if not cleaned:
        raise RuntimeError("LLM 响应没有文本")
    return cleaned


def _chat_completions(config: LLMConfig, prompt: str, system: Optional[str]) -> str:
    if not config.api_key:
        raise RuntimeError("LLM API key 缺失")
    base = (config.base_url or "https://api.minimaxi.com/v1").rstrip("/")
    url = f"{base}/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload: dict = {
        "model": config.model,
        "messages": messages,
        "temperature": 0.3,
    }
    # MiniMax-M3 默认把思维链写进 content；写作通道关掉，避免正文脏掉。
    if (config.provider or "").lower() in ("minimax", "minimax_openai"):
        payload["thinking"] = {"type": "disabled"}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"LLM HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LLM 网络失败: {exc.reason}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("LLM 响应不是 JSON") from exc
    return _extract_content(payload)


def call_llm(
    prompt: str,
    node_type: str = "default",
    system: Optional[str] = None,
) -> str:
    """统一 LLM 调用。

    provider=mock 返回占位。其他 provider 走 OpenAI 兼容 Chat Completions。
    """
    config = router.get_config(node_type)
    if config.provider == "mock":
        return _MOCK_TEXT.get(node_type, _MOCK_TEXT["default"])
    return _chat_completions(config, prompt, system)

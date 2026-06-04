"""LLM client with ProviderPreset abstraction.

Based on Aegis-Manim methodology:
- ProviderPreset frozen dataclass for unified provider description
- api_type protocol separation (openai-compatible / anthropic-compatible)
- normalize_base_url for URL sanitization
- attempts tuple for fallback chain
- Error classification: auth / quota / request
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request
from urllib.parse import urlparse

DEFAULT_PROVIDER = "openrouter"
DEFAULT_TIMEOUT = 120


@dataclass(frozen=True)
class ProviderPreset:
    id: str
    name: str
    api_type: str  # "openai-compatible" | "anthropic-compatible"
    base_url: str
    default_model: str
    models: tuple[str, ...]
    api_key_env: str
    doc: str = ""
    requires_api_key: bool = True


PROVIDER_PRESETS: dict[str, ProviderPreset] = {
    "openrouter": ProviderPreset(
        id="openrouter",
        name="OpenRouter",
        api_type="openai-compatible",
        base_url="https://openrouter.ai/api/v1",
        default_model="anthropic/claude-sonnet-4-6",
        models=(
            "anthropic/claude-sonnet-4-6",
            "anthropic/claude-opus-4-6",
            "anthropic/claude-haiku-4-5-20251001",
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "google/gemini-2.5-flash",
            "deepseek/deepseek-chat",
        ),
        api_key_env="OPENROUTER_API_KEY",
        doc="https://openrouter.ai/docs",
    ),
    "kimi-code": ProviderPreset(
        id="kimi-code",
        name="Kimi Code",
        api_type="anthropic-compatible",
        base_url="https://api.kimi.com/coding/v1",
        default_model="kimi-for-coding",
        models=("kimi-for-coding",),
        api_key_env="KIMI_CODE_API_KEY",
        doc="https://www.kimi.com/code/docs",
    ),
    "kimi-code-anthropic-token": ProviderPreset(
        id="kimi-code-anthropic-token",
        name="Kimi Code (Anthropic Token)",
        api_type="anthropic-compatible",
        base_url="https://api.kimi.com/coding/v1",
        default_model="kimi-for-coding",
        models=("kimi-for-coding",),
        api_key_env="ANTHROPIC_AUTH_TOKEN",
        doc="Kimi Code via ANTHROPIC_AUTH_TOKEN env var",
    ),
    "moonshot-kimi": ProviderPreset(
        id="moonshot-kimi",
        name="Moonshot Kimi",
        api_type="openai-compatible",
        base_url="https://api.moonshot.cn/v1",
        default_model="kimi-k2-0711-preview",
        models=("kimi-k2-0711-preview", "kimi-latest", "kimi-thinking-preview"),
        api_key_env="MOONSHOT_API_KEY",
        doc="https://platform.kimi.ai/docs",
    ),
    "custom-openai": ProviderPreset(
        id="custom-openai",
        name="Custom OpenAI-Compatible",
        api_type="openai-compatible",
        base_url="",
        default_model="",
        models=(),
        api_key_env="",
        requires_api_key=False,
        doc="Custom endpoint",
    ),
    "minimax": ProviderPreset(
        id="minimax",
        name="MiniMax Token Plan",
        api_type="anthropic-compatible",
        base_url="https://api.minimaxi.com/anthropic",
        default_model="MiniMax-M3",
        models=("MiniMax-M3", "MiniMax-M2.7", "MiniMax-M2.5"),
        api_key_env="MINIMAX_TOKEN_PLAN_KEY",
        doc=(
            "MiniMax Token Plan via Anthropic-compatible protocol. "
            "Reference: ~/Desktop/AI组件工作流库/components/minimax-token-plan-real-service/WORKFLOW.md"
        ),
    ),
}


class LLMError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def resolve_provider(provider_id: str | None) -> ProviderPreset:
    key = (provider_id or DEFAULT_PROVIDER).strip() or DEFAULT_PROVIDER
    return PROVIDER_PRESETS.get(key, PROVIDER_PRESETS[DEFAULT_PROVIDER])


def normalize_base_url(raw_base_url: str | None, *, api_type: str, fallback: str = "") -> str:
    value = (raw_base_url or fallback or "").strip()
    if not value:
        raise ValueError("Base URL is required for this provider.")

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Base URL must be a valid http(s) URL: {value}")

    cleaned = value.rstrip("/")
    lower = cleaned.lower()

    if api_type == "openai-compatible":
        for suffix in ("/chat/completions",):
            if lower.endswith(suffix):
                return cleaned[: -len(suffix)].rstrip("/")
    if api_type == "anthropic-compatible" and lower.endswith("/messages"):
        return cleaned[: -len("/messages")].rstrip("/")

    return cleaned


def _read_response_json(req: request.Request, *, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except error.HTTPError:
        raise
    except error.URLError as exc:
        raise LLMError("network_error", f"Cannot reach model provider: {exc}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise LLMError("invalid_response", f"Provider returned non-JSON: {body[:300]}") from exc
    if not isinstance(parsed, dict):
        raise LLMError("invalid_response", f"Provider returned unexpected response: {parsed}")
    return parsed


def _extract_openai_text(response_json: dict[str, Any]) -> str:
    choices = response_json.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMError("invalid_response", f"Missing choices: {response_json}")

    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise LLMError("invalid_response", f"Missing message: {response_json}")

    content = message.get("content")
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        if parts:
            return "\n".join(parts)

    raise LLMError("invalid_response", f"Missing text content: {response_json}")


def _extract_anthropic_text(response_json: dict[str, Any]) -> str:
    content = response_json.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
        if parts:
            return "\n".join(parts)
    raise LLMError("invalid_response", f"Missing text content: {response_json}")


def _sanitize_error(exc: Exception) -> tuple[str, str]:
    text = str(exc)
    if "401" in text or "403" in text or "invalid" in text.lower() or "auth" in text.lower():
        return "auth", text
    if "402" in text or "429" in text or "quota" in text.lower() or "rate" in text.lower() or "insufficient" in text.lower() or "credits" in text.lower():
        return "quota", text
    if "network" in text.lower() or "cannot reach" in text.lower():
        return "network", text
    return "request", text


def _call_openai_compatible(
    *,
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    provider_name: str,
) -> tuple[str, dict[str, int]]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "EmpiricalPaperWorkbench/1.0",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        parsed = _read_response_json(req)
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError("provider_error", f"{provider_name} HTTP {exc.code}: {detail}") from exc

    if "error" in parsed:
        raise LLMError("provider_error", f"{provider_name}: {parsed['error']}")

    text = _extract_openai_text(parsed)
    usage = parsed.get("usage", {})
    return text, {
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
    }


def _call_anthropic_compatible(
    *,
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    provider_name: str,
) -> tuple[str, dict[str, int]]:
    system_msg = ""
    user_messages: list[dict[str, str]] = []
    for msg in messages:
        if msg.get("role") == "system":
            system_msg = msg.get("content", "")
        else:
            user_messages.append(msg)

    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": 4096,
        "messages": user_messages or [{"role": "user", "content": "Hello"}],
        "temperature": temperature,
    }
    if system_msg:
        payload["system"] = system_msg

    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    if api_key:
        headers["x-api-key"] = api_key

    req = request.Request(
        f"{base_url.rstrip('/')}/messages",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        parsed = _read_response_json(req)
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError("provider_error", f"{provider_name} HTTP {exc.code}: {detail}") from exc

    if "error" in parsed:
        raise LLMError("provider_error", f"{provider_name}: {parsed['error']}")

    text = _extract_anthropic_text(parsed)
    usage = parsed.get("usage", {})
    return text, {
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
    }


# ── Public API ───────────────────────────────────────────────────────────────


def chat_completion(
    messages: list[dict[str, str]],
    *,
    provider_id: str | None = None,
    model: str | None = None,
    temperature: float = 0.3,
    api_key: str | None = None,
    base_url: str | None = None,
) -> tuple[str, dict[str, int]]:
    """Call LLM with unified interface.

    Args:
        messages: List of {"role": "system"|"user"|"assistant", "content": str}
        provider_id: Provider preset ID (e.g., "openrouter", "kimi-code")
        model: Model name override
        temperature: Sampling temperature
        api_key: API key override (falls back to env var)
        base_url: Base URL override

    Returns:
        (generated_text, usage) where usage contains input_tokens and output_tokens.

    Raises:
        LLMError: On provider error, auth failure, or network issue.
    """
    preset = resolve_provider(provider_id)

    # Resolve API key: explicit > env var > empty
    resolved_key = (api_key or "").strip()
    if not resolved_key and preset.api_key_env:
        resolved_key = os.getenv(preset.api_key_env, "").strip()

    if preset.requires_api_key and not resolved_key:
        raise LLMError("missing_api_key", f"{preset.name} requires API key. Set env var {preset.api_key_env} or pass api_key.")

    # Resolve model
    selected_model = (model or preset.default_model).strip()
    if not selected_model:
        raise LLMError("missing_model", f"{preset.name} model is required.")

    # Resolve base URL
    if preset.api_type == "openai-compatible":
        normalized_base = normalize_base_url(
            base_url, api_type=preset.api_type, fallback=preset.base_url
        )
        return _call_openai_compatible(
            api_key=resolved_key,
            base_url=normalized_base,
            model=selected_model,
            messages=messages,
            temperature=temperature,
            provider_name=preset.name,
        )

    if preset.api_type == "anthropic-compatible":
        normalized_base = normalize_base_url(
            base_url, api_type=preset.api_type, fallback=preset.base_url
        )
        return _call_anthropic_compatible(
            api_key=resolved_key,
            base_url=normalized_base,
            model=selected_model,
            messages=messages,
            temperature=temperature,
            provider_name=preset.name,
        )

    raise LLMError("unsupported_api_type", f"Unsupported protocol: {preset.api_type}")


def chat_completion_with_fallback(
    messages: list[dict[str, str]],
    *,
    attempts: tuple[dict[str, Any], ...] | None = None,
    temperature: float = 0.3,
) -> tuple[str, dict[str, Any]]:
    """Call LLM with automatic fallback chain.

    Args:
        messages: Chat messages
        attempts: Ordered tuple of attempt configs.
            Defaults to [{"provider_id": "openrouter", "model": None}]
        temperature: Sampling temperature

    Returns:
        (text, metadata) where metadata contains provider_id, model, endpoint used.
    """
    if attempts is None:
        attempts = (
            {"provider_id": "openrouter", "model": None},
        )

    last_error = ""
    for attempt in attempts:
        provider_id = attempt.get("provider_id", "openrouter")
        model = attempt.get("model")
        env_var = attempt.get("env")

        # Skip if env var required but not set
        if env_var and not os.getenv(env_var, "").strip():
            continue

        try:
            text, usage = chat_completion(
                messages,
                provider_id=provider_id,
                model=model,
                temperature=temperature,
            )
            preset = resolve_provider(provider_id)
            metadata = {
                "provider_id": provider_id,
                "provider_name": preset.name,
                "model": model or preset.default_model,
                "api_type": preset.api_type,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
            }
            return text, metadata
        except LLMError as exc:
            error_code, _ = _sanitize_error(exc)
            last_error = f"{provider_id}: {exc.code}"
            # Auth errors: don't retry same provider
            # Quota errors: try next provider
            # Network errors: try next provider
            if error_code == "auth":
                continue
            continue
        except Exception as exc:
            last_error = f"{provider_id}: {exc}"
            continue

    raise LLMError("all_attempts_failed", f"All providers failed. Last: {last_error}")


def get_available_providers() -> dict[str, Any]:
    """Return provider config for UI display."""
    return {
        "defaultProvider": DEFAULT_PROVIDER,
        "providers": {
            provider_id: {
                "id": preset.id,
                "name": preset.name,
                "apiType": preset.api_type,
                "baseURL": preset.base_url,
                "defaultModel": preset.default_model,
                "models": list(preset.models),
                "requiresApiKey": preset.requires_api_key,
                "apiKeyEnv": preset.api_key_env,
            }
            for provider_id, preset in PROVIDER_PRESETS.items()
        },
    }

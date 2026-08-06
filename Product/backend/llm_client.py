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
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator
from urllib import error, request
from urllib.parse import urlparse

# Product + local dev default: Grok 4.5 (xAI Grok CLI session or XAI_API_KEY).
DEFAULT_PROVIDER = "grok"
DEFAULT_GROK_MODEL = "grok-4.5"
DEFAULT_TIMEOUT = 120
DEFAULT_GROK_CLI_PROXY = "https://cli-chat-proxy.grok.com/v1"
DEFAULT_XAI_API = "https://api.x.ai/v1"


@dataclass(frozen=True)
class ProviderPreset:
    id: str
    name: str
    api_type: str  # "openai-compatible" | "anthropic-compatible" | "codex-cli"
    base_url: str
    default_model: str
    models: tuple[str, ...]
    api_key_env: str
    doc: str = ""
    requires_api_key: bool = True


PROVIDER_PRESETS: dict[str, ProviderPreset] = {
    "openai": ProviderPreset(
        id="openai",
        name="OpenAI",
        api_type="openai-compatible",
        base_url="https://api.openai.com/v1",
        default_model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        models=("gpt-5.5", "gpt-5", "gpt-4.1"),
        api_key_env="OPENAI_API_KEY",
        doc="https://platform.openai.com/docs",
    ),
    "stepfun": ProviderPreset(
        id="stepfun",
        name="StepFun",
        api_type="openai-compatible",
        base_url=os.getenv("STEPFUN_BASE_URL", "https://api.stepfun.com/v1"),
        default_model=os.getenv("STEPFUN_MODEL", "step-2"),
        models=("step-2", "step-1"),
        api_key_env="STEPFUN_API_KEY",
        doc="OpenAI-compatible StepFun endpoint",
    ),
    "deepseek": ProviderPreset(
        id="deepseek",
        name="DeepSeek",
        api_type="openai-compatible",
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        default_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        models=("deepseek-chat", "deepseek-reasoner"),
        api_key_env="DEEPSEEK_API_KEY",
        doc="https://api-docs.deepseek.com/",
    ),
    "mimo": ProviderPreset(
        id="mimo",
        name="Mimo",
        api_type="openai-compatible",
        base_url=os.getenv("MIMO_BASE_URL", ""),
        default_model=os.getenv("MIMO_MODEL", ""),
        models=(),
        api_key_env="MIMO_API_KEY",
        doc="Local/private OpenAI-compatible Mimo endpoint",
    ),
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
    "codex-cli": ProviderPreset(
        id="codex-cli",
        name="Codex CLI",
        api_type="codex-cli",
        base_url="",
        default_model=os.getenv("CODEX_LOCAL_MODEL", "gpt-5.5"),
        models=("gpt-5.5", "gpt-5.4", "gpt-5.4-mini"),
        api_key_env="",
        requires_api_key=False,
        doc="Local Codex CLI login session via codex exec",
    ),
    "minimax": ProviderPreset(
        id="minimax",
        name="MiniMax Token Plan",
        api_type="anthropic-compatible",
        # base_url 真相：用户现有 sk-cp-* key 实测在 api.minimaxi.com 上 200，在
        # api.minimax.io 上 401。官方文档说后者是 current host，但 key 平台是旧的。
        # 用 env MINIMAX_BASE_URL 可以 override（推荐在 .env.local 里设）。
        # base_url 必须含 /v1 段（项目 _call_anthropic_compatible 拼 /messages）
        base_url="https://api.minimaxi.com/anthropic/v1",
        # 模型默认 MiniMax-M2.7 (用户 ai组件工作流 验证: 同一个 sk-cp-* key, M2.7
        # 支持 streaming 200 OK, M3 stream=True 返 401). 用 env MINIMAX_MODEL 可 override.
        default_model=os.getenv("MINIMAX_MODEL", "MiniMax-M2.7"),
        models=("MiniMax-M2.7", "MiniMax-M2.5", "MiniMax-M3"),
        api_key_env="MINIMAX_API_KEY",
        # 兼容旧名 MINIMAX_TOKEN_PLAN_KEY：见 chat_completion() 中的 fallback 逻辑
        doc=(
            "MiniMax Token Plan via Anthropic-compatible protocol. "
            "Env var: MINIMAX_API_KEY (Token Plan keys use sk-cp-* prefix). "
            "Falls back to MINIMAX_TOKEN_PLAN_KEY for backward compat. "
            "Default base_url=https://api.minimaxi.com/anthropic/v1 (verified with this key). "
            "Override via env MINIMAX_BASE_URL if you have a key bound to api.minimax.io. "
            "Default model=MiniMax-M2.7 (MiniMax-M3 doesn't support streaming with Token Plan keys, "
            "see ai组件工作流/.env.local for pattern). Override via env MINIMAX_MODEL. "
            "Official docs: https://platform.minimax.io/docs/api-reference/text-anthropic-api"
        ),
    ),
    "grok": ProviderPreset(
        id="grok",
        name="Grok 4.5 (xAI Grok CLI session / proxy)",
        api_type="openai-compatible",
        # Local Grok Build / Grok CLI session token → cli-chat-proxy (model id grok-4.5).
        # Requires x-grok-client-version header (see _grok_extra_headers).
        base_url=os.getenv("GROK_BASE_URL", DEFAULT_GROK_CLI_PROXY),
        default_model=os.getenv("GROK_MODEL", DEFAULT_GROK_MODEL),
        models=(DEFAULT_GROK_MODEL, "grok-4.5-build", "grok-4", "grok-3"),
        api_key_env="GROK_API_KEY",
        doc=(
            "Preferred product + dev LLM. OpenAI-compatible chat/completions. "
            "Auth: GROK_API_KEY or XAI_API_KEY, else auto-load ~/.grok/auth.json session key. "
            "Default base: https://cli-chat-proxy.grok.com/v1 (Grok CLI proxy). "
            "Default model: grok-4.5. Client version header from ~/.grok/version.json."
        ),
    ),
    "xai": ProviderPreset(
        id="xai",
        name="xAI API (official)",
        api_type="openai-compatible",
        base_url=os.getenv("XAI_BASE_URL", DEFAULT_XAI_API),
        default_model=os.getenv("XAI_MODEL", DEFAULT_GROK_MODEL),
        models=(DEFAULT_GROK_MODEL, "grok-4", "grok-3", "grok-3-mini"),
        api_key_env="XAI_API_KEY",
        doc="Official xAI API https://api.x.ai/v1. Prefer provider_id=grok for Grok CLI session.",
    ),
}

MODEL_ENV_BY_PROVIDER = {
    "openai": "OPENAI_MODEL",
    "stepfun": "STEPFUN_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
    "mimo": "MIMO_MODEL",
    "minimax": "MINIMAX_MODEL",
    "grok": "GROK_MODEL",
    "xai": "XAI_MODEL",
    "openrouter": "OPENROUTER_MODEL",
    "moonshot-kimi": "MOONSHOT_MODEL",
    "kimi-code": "KIMI_CODE_MODEL",
    "kimi-code-anthropic-token": "KIMI_CODE_MODEL",
    "codex-cli": "CODEX_LOCAL_MODEL",
}

BASE_URL_ENV_BY_PROVIDER = {
    "openai": "OPENAI_BASE_URL",
    "stepfun": "STEPFUN_BASE_URL",
    "deepseek": "DEEPSEEK_BASE_URL",
    "mimo": "MIMO_BASE_URL",
    "minimax": "MINIMAX_BASE_URL",
    "grok": "GROK_BASE_URL",
    "xai": "XAI_BASE_URL",
    "openrouter": "OPENROUTER_BASE_URL",
    "moonshot-kimi": "MOONSHOT_BASE_URL",
    "kimi-code": "KIMI_CODE_BASE_URL",
    "kimi-code-anthropic-token": "KIMI_CODE_BASE_URL",
}

PROVIDER_ATTEMPT_ORDER = (
    "grok",
    "xai",
    "codex-cli",
    "openai",
    "stepfun",
    "mimo",
    "deepseek",
    "minimax",
    "kimi-code-anthropic-token",
    "kimi-code",
    "moonshot-kimi",
    "openrouter",
)


class LLMError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def resolve_provider(provider_id: str | None) -> ProviderPreset:
    raw = (provider_id or os.getenv("EMPIRICAL_LLM_PROVIDER") or DEFAULT_PROVIDER).strip()
    key = raw or DEFAULT_PROVIDER
    # Aliases
    if key in {"grok-4.5", "grok45", "grok4.5"}:
        key = "grok"
    return PROVIDER_PRESETS.get(key, PROVIDER_PRESETS[DEFAULT_PROVIDER])


def _grok_client_version() -> str:
    env_v = os.getenv("GROK_CLIENT_VERSION", "").strip()
    if env_v:
        return env_v
    version_path = Path.home() / ".grok" / "version.json"
    if version_path.exists():
        try:
            data = json.loads(version_path.read_text(encoding="utf-8"))
            v = str(data.get("version") or "").strip()
            if v:
                return v
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return "0.2.118"


def load_grok_session_key() -> str | None:
    """Load Grok CLI OAuth session token from ~/.grok/auth.json (no secret logging)."""
    auth_path = Path(os.getenv("GROK_AUTH_PATH", "").strip() or Path.home() / ".grok" / "auth.json").expanduser()
    if not auth_path.exists():
        return None
    try:
        data = json.loads(auth_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    # Prefer non-expired entries if expires_at present
    candidates: list[tuple[str, str]] = []
    for _k, v in data.items():
        if not isinstance(v, dict):
            continue
        key = str(v.get("key") or "").strip()
        if not key:
            continue
        expires = str(v.get("expires_at") or "")
        candidates.append((expires, key))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def resolve_grok_api_key(explicit: str | None = None) -> str:
    """GROK_API_KEY / XAI_API_KEY / ~/.grok/auth.json session."""
    for value in (
        (explicit or "").strip(),
        os.getenv("GROK_API_KEY", "").strip(),
        os.getenv("XAI_API_KEY", "").strip(),
    ):
        if value:
            return value
    session = load_grok_session_key()
    return session or ""


def _grok_extra_headers() -> dict[str, str]:
    """cli-chat-proxy requires x-grok-client-version or returns HTTP 426."""
    ver = _grok_client_version()
    return {
        "User-Agent": f"GrokCLI/{ver}",
        "x-grok-client-version": ver,
        "x-grok-client-mode": os.getenv("GROK_CLIENT_MODE", "chat").strip() or "chat",
    }


def load_local_env_if_present(start: Path | None = None) -> None:
    """Load `.env.local` values for local Agent execution without overriding env."""
    candidates: list[Path] = []
    base = (start or Path.cwd()).resolve()
    candidates.extend(parent / ".env.local" for parent in (base, *base.parents))
    candidates.extend(
        [
            Path(__file__).resolve().parents[2] / ".env.local",
            Path(__file__).resolve().parents[1] / ".env.local",
        ]
    )

    seen: set[Path] = set()
    for path in candidates:
        if path in seen or not path.exists() or not path.is_file():
            continue
        seen.add(path)
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not key or key in os.environ:
                continue
            cleaned = value.strip().strip('"').strip("'")
            os.environ[key] = cleaned


def _provider_model_env(preset: ProviderPreset) -> str:
    return MODEL_ENV_BY_PROVIDER.get(preset.id, f"{preset.id.upper().replace('-', '_')}_MODEL")


def _provider_base_url_env(preset: ProviderPreset) -> str:
    return BASE_URL_ENV_BY_PROVIDER.get(preset.id, f"{preset.id.upper().replace('-', '_')}_BASE_URL")


def _provider_default_model(preset: ProviderPreset) -> str:
    env_var = _provider_model_env(preset)
    return os.getenv(env_var, "").strip() or preset.default_model


def _provider_default_base_url(preset: ProviderPreset) -> str:
    env_var = _provider_base_url_env(preset)
    return os.getenv(env_var, "").strip() or preset.base_url


def _provider_has_key(provider_id: str, preset: ProviderPreset) -> bool:
    if provider_id == "codex-cli":
        return os.getenv("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC") == "1" and bool(probe_codex_login().get("ready"))
    if provider_id in {"grok", "xai"}:
        return bool(resolve_grok_api_key())
    if not preset.requires_api_key:
        return True
    if preset.api_key_env and os.getenv(preset.api_key_env, "").strip():
        return True
    if provider_id == "minimax" and bool(os.getenv("MINIMAX_TOKEN_PLAN_KEY", "").strip()):
        return True
    if provider_id == "xai" and bool(os.getenv("GROK_API_KEY", "").strip()):
        return True
    return False


def _codex_bin() -> str:
    return os.getenv("CODEX_BIN", "").strip() or shutil.which("codex") or ""


def _codex_auth_path() -> Path:
    return Path(os.getenv("CODEX_AUTH_PATH", "").strip() or Path.home() / ".codex" / "auth.json").expanduser()


def probe_codex_login() -> dict[str, Any]:
    """Probe local Codex CLI without reading or exposing auth contents."""
    codex_bin = _codex_bin()
    auth_path = _codex_auth_path()
    status: dict[str, Any] = {
        "provider_id": "codex-cli",
        "available": bool(codex_bin),
        "path": codex_bin,
        "auth_path": str(auth_path),
        "auth_ready": auth_path.exists(),
        "version": None,
        "ready": False,
        "reason": "",
        "action": "",
    }
    if not codex_bin:
        status["reason"] = "未找到 codex CLI。"
        status["action"] = "安装 codex CLI，或设置 CODEX_BIN 指向本机 codex 可执行文件。"
        return status
    if not status["auth_ready"]:
        status["reason"] = "codex CLI 尚未登录。"
        status["action"] = "在终端运行 codex login，完成 OAuth 后重启本地服务。"
        return status
    try:
        result = subprocess.run(
            [codex_bin, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        status["reason"] = f"codex CLI 无法执行：{exc}"
        status["action"] = "检查 CODEX_BIN、PATH 和本机 codex 安装状态。"
        return status

    output = (result.stdout or result.stderr).strip()
    status["version"] = output.splitlines()[-1] if output else None
    if result.returncode != 0:
        status["reason"] = f"codex --version 退出码 {result.returncode}。"
        status["action"] = "先在终端确认 codex --version 可以正常运行。"
        return status
    status["ready"] = True
    return status


def _provider_attempt_env(preset: ProviderPreset) -> str | None:
    if preset.id == "codex-cli":
        return "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"
    return preset.api_key_env or None


def build_default_llm_attempts() -> tuple[dict[str, Any], ...]:
    """Build local-first fallback attempts for Agent experiments.

    The product should use the user's configured local/cloud providers before
    falling back to OpenRouter. Missing keys are skipped so a broken provider
    does not block the whole chain.
    """
    load_local_env_if_present()

    attempts: list[dict[str, Any]] = []
    preferred_provider = os.getenv("EMPIRICAL_LLM_PROVIDER", "").strip()
    if preferred_provider:
        preferred = resolve_provider(preferred_provider)
        attempts.append(
            {
                "provider_id": preferred.id,
                "model": os.getenv("EMPIRICAL_LLM_MODEL", "").strip() or _provider_default_model(preferred) or None,
                "env": _provider_attempt_env(preferred),
            }
        )

    for provider_id in PROVIDER_ATTEMPT_ORDER:
        preset = resolve_provider(provider_id)
        if not _provider_has_key(provider_id, preset):
            continue
        attempt = {
            "provider_id": provider_id,
            "model": _provider_default_model(preset) or None,
            "env": _provider_attempt_env(preset),
        }
        if attempt not in attempts:
            attempts.append(attempt)

    if not attempts:
        attempts.append({"provider_id": "openrouter", "model": None, "env": "OPENROUTER_API_KEY"})

    return tuple(attempts)


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
    timeout_seconds: int = DEFAULT_TIMEOUT,
    extra_headers: dict[str, str] | None = None,
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
    if extra_headers:
        headers.update(extra_headers)

    req = request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        parsed = _read_response_json(req, timeout=timeout_seconds)
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
    timeout_seconds: int = DEFAULT_TIMEOUT,
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
        parsed = _read_response_json(req, timeout=timeout_seconds)
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


# ── Streaming helpers (SSE parsers) ──────────────────────────────────────────


def _build_anthropic_stream_request(
    *,
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> request.Request:
    system_msg = ""
    user_messages: list[dict[str, str]] = []
    for msg in messages:
        if msg.get("role") == "system":
            system_msg = msg.get("content", "")
        else:
            user_messages.append(msg)

    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": user_messages or [{"role": "user", "content": "Hello"}],
        "temperature": temperature,
        "stream": True,
    }
    if system_msg:
        payload["system"] = system_msg

    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    if api_key:
        headers["x-api-key"] = api_key

    return request.Request(
        f"{base_url.rstrip('/')}/messages",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )


def _build_openai_stream_request(
    *,
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    extra_headers: dict[str, str] | None = None,
) -> request.Request:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "EmpiricalPaperWorkbench/1.0",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra_headers:
        headers.update(extra_headers)

    return request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )


def _iter_sse_lines(req: request.Request, *, timeout: int = DEFAULT_TIMEOUT) -> Iterator[str]:
    """Yield decoded SSE `data: ...` payload strings from a streaming response.

    Skips event-name / comment / blank lines. Stops at `[DONE]`.
    """
    with request.urlopen(req, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").rstrip("\n").rstrip("\r")
            if not line.startswith("data: "):
                continue
            payload = line[len("data: "):]
            if payload.strip() == "[DONE]":
                break
            yield payload


def _stream_anthropic_compatible(req: request.Request) -> Iterator[str]:
    """Parse Anthropic SSE: `content_block_delta` → `text_delta.text`."""
    for payload in _iter_sse_lines(req):
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "content_block_delta":
            delta = event.get("delta") or {}
            if delta.get("type") == "text_delta":
                text = delta.get("text", "")
                if text:
                    yield text


def _stream_openai_compatible(req: request.Request) -> Iterator[str]:
    """Parse OpenAI SSE: `choices[].delta.content`."""
    for payload in _iter_sse_lines(req):
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            continue
        for choice in event.get("choices", []) or []:
            delta = choice.get("delta") or {}
            content = delta.get("content", "")
            if content:
                yield content


def _format_codex_prompt(messages: list[dict[str, str]]) -> str:
    parts: list[str] = []
    for message in messages:
        role = str(message.get("role") or "user").strip() or "user"
        content = str(message.get("content") or "").strip()
        if content:
            parts.append(f"[{role}]\n{content}")
    return "\n\n".join(parts).strip() or "请返回 JSON：{\"status\":\"ok\"}"


def _call_codex_cli(
    *,
    model: str,
    messages: list[dict[str, str]],
    timeout_seconds: int = DEFAULT_TIMEOUT,
) -> tuple[str, dict[str, int]]:
    if os.getenv("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC") != "1":
        raise LLMError("codex_exec_disabled", "Set EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1 to allow Codex CLI execution.")

    codex_bin = _codex_bin()
    if not codex_bin:
        raise LLMError("codex_cli_not_found", "Codex CLI executable was not found. Set CODEX_BIN or install codex.")

    project_root = Path(os.getenv("CODEX_LOCAL_PROJECT_ROOT", "") or Path.cwd()).resolve()
    prompt = _format_codex_prompt(messages)

    with tempfile.NamedTemporaryFile(prefix="empirical-codex-", suffix=".md", delete=False) as output_file:
        output_path = Path(output_file.name)

    command = [
        codex_bin,
        "-a",
        "never",
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--output-last-message",
        str(output_path),
        "--model",
        model,
        "-C",
        str(project_root),
        "-",
    ]
    try:
        result = subprocess.run(
            command,
            input=prompt,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise LLMError("codex_cli_timeout", f"Codex CLI timed out after {timeout_seconds}s.") from exc
    except OSError as exc:
        raise LLMError("codex_cli_error", f"Cannot start Codex CLI: {exc}") from exc

    output_text = output_path.read_text(encoding="utf-8").strip() if output_path.exists() else ""
    try:
        output_path.unlink(missing_ok=True)
    except OSError:
        pass
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "Codex CLI failed.").strip()
        raise LLMError("codex_cli_failed", detail[:1000])
    if not output_text:
        output_text = (result.stdout or "").strip()
    if not output_text:
        raise LLMError("codex_cli_empty_response", "Codex CLI returned no final response.")

    return output_text, {
        "input_tokens": max(1, len(prompt) // 4),
        "output_tokens": max(1, len(output_text) // 4),
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
    timeout_seconds: int = DEFAULT_TIMEOUT,
) -> tuple[str, dict[str, int]]:
    """Call LLM with unified interface.

    Args:
        messages: List of {"role": "system"|"user"|"assistant", "content": str}
        provider_id: Provider preset ID (e.g., "openrouter", "kimi-code")
        model: Model name override
        temperature: Sampling temperature
        api_key: API key override (falls back to env var)
        base_url: Base URL override
        timeout_seconds: Request timeout for non-streaming supervisor calls

    Returns:
        (generated_text, usage) where usage contains input_tokens and output_tokens.

    Raises:
        LLMError: On provider error, auth failure, or network issue.
    """
    load_local_env_if_present()
    # Default product model preference when caller omits provider
    if not provider_id:
        provider_id = os.getenv("EMPIRICAL_LLM_PROVIDER") or DEFAULT_PROVIDER
    if not model:
        model = os.getenv("EMPIRICAL_LLM_MODEL") or None
    preset = resolve_provider(provider_id)

    # Resolve API key: explicit > primary env var > alias env vars > empty
    resolved_key = (api_key or "").strip()
    if not resolved_key and preset.id in {"grok", "xai"}:
        resolved_key = resolve_grok_api_key()
    if not resolved_key and preset.api_key_env:
        resolved_key = os.getenv(preset.api_key_env, "").strip()
    # Backward-compat alias: MINIMAX_TOKEN_PLAN_KEY (old name) → MINIMAX_API_KEY (new)
    if not resolved_key and preset.id == "minimax":
        resolved_key = os.getenv("MINIMAX_TOKEN_PLAN_KEY", "").strip()

    if preset.requires_api_key and not resolved_key:
        if preset.id in {"grok", "xai"}:
            raise LLMError(
                "missing_api_key",
                f"{preset.name} requires GROK_API_KEY / XAI_API_KEY or a logged-in Grok CLI session (~/.grok/auth.json). "
                "Run `grok login` if using session auth.",
            )
        raise LLMError("missing_api_key", f"{preset.name} requires API key. Set env var {preset.api_key_env} or pass api_key.")

    # Resolve model
    selected_model = (model or _provider_default_model(preset)).strip()
    if not selected_model:
        raise LLMError("missing_model", f"{preset.name} model is required.")
    # Prefer grok-4.5 naming for product tests when env sets EMPIRICAL_LLM_MODEL
    if selected_model in {"grok4.5", "grok-4.5-build"} and preset.id in {"grok", "xai"}:
        # Keep grok-4.5 for proxy; build variant still accepted by proxy as model id sometimes
        pass

    # Resolve base URL: explicit > per-provider env var > preset default
    effective_base_url = base_url
    if not effective_base_url:
        effective_base_url = _provider_default_base_url(preset) or None

    extra_headers: dict[str, str] | None = None
    if preset.id == "grok" or (
        preset.id == "xai"
        and "cli-chat-proxy.grok.com" in (effective_base_url or _provider_default_base_url(preset) or "")
    ):
        extra_headers = _grok_extra_headers()

    # Resolve base URL
    if preset.api_type == "openai-compatible":
        normalized_base = normalize_base_url(
            effective_base_url, api_type=preset.api_type, fallback=_provider_default_base_url(preset)
        )
        return _call_openai_compatible(
            api_key=resolved_key,
            base_url=normalized_base,
            model=selected_model,
            messages=messages,
            temperature=temperature,
            provider_name=preset.name,
            timeout_seconds=timeout_seconds,
            extra_headers=extra_headers,
        )

    if preset.api_type == "anthropic-compatible":
        normalized_base = normalize_base_url(
            effective_base_url, api_type=preset.api_type, fallback=_provider_default_base_url(preset)
        )
        return _call_anthropic_compatible(
            api_key=resolved_key,
            base_url=normalized_base,
            model=selected_model,
            messages=messages,
            temperature=temperature,
            provider_name=preset.name,
            timeout_seconds=timeout_seconds,
        )

    if preset.api_type == "codex-cli":
        return _call_codex_cli(
            model=selected_model,
            messages=messages,
            timeout_seconds=timeout_seconds,
        )

    raise LLMError("unsupported_api_type", f"Unsupported protocol: {preset.api_type}")


def chat_completion_with_fallback(
    messages: list[dict[str, str]],
    *,
    attempts: tuple[dict[str, Any], ...] | None = None,
    temperature: float = 0.3,
    timeout_seconds: int = DEFAULT_TIMEOUT,
) -> tuple[str, dict[str, Any]]:
    """Call LLM with automatic fallback chain.

    Args:
        messages: Chat messages
        attempts: Ordered tuple of attempt configs.
            Defaults to the local-first provider chain from build_default_llm_attempts().
        temperature: Sampling temperature
        timeout_seconds: Request timeout applied to each provider attempt

    Returns:
        (text, metadata) where metadata contains provider_id, model, endpoint used.
    """
    if attempts is None:
        attempts = build_default_llm_attempts()

    last_error = ""
    for attempt in attempts:
        provider_id = attempt.get("provider_id", DEFAULT_PROVIDER)
        model = attempt.get("model")
        env_var = attempt.get("env")

        # Skip if env var required but not set (Grok may use ~/.grok/auth.json instead)
        if env_var and not os.getenv(env_var, "").strip():
            if provider_id in {"grok", "xai"} and resolve_grok_api_key():
                pass
            else:
                continue

        try:
            text, usage = chat_completion(
                messages,
                provider_id=provider_id,
                model=model,
                temperature=temperature,
                timeout_seconds=timeout_seconds,
            )
            preset = resolve_provider(provider_id)
            metadata = {
                "provider_id": provider_id,
                "provider_name": preset.name,
                "model": model or _provider_default_model(preset),
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


def chat_completion_stream(
    messages: list[dict[str, str]],
    *,
    provider_id: str | None = None,
    model: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 4096,
    api_key: str | None = None,
    base_url: str | None = None,
) -> Iterator[str]:
    """Stream text chunks from LLM. Yields incremental text (str).

    LLM 单一入口 (用户要求). 内部走 _stream_anthropic_compatible /
    _stream_openai_compatible 分支, 自动重试 3 次 (指数退避, 与 chat_completion 一致).

    Args:
        messages: List of {"role": "system"|"user"|"assistant", "content": str}
        provider_id: Provider preset ID (默认 grok / EMPIRICAL_LLM_PROVIDER).
        model: Model name override (默认 EMPIRICAL_LLM_MODEL 或 grok-4.5).
        temperature: Sampling temperature.
        max_tokens: Max tokens for response.
        api_key: API key override (falls back to env var / Grok session).
        base_url: Base URL override.

    Yields:
        Incremental text chunks (str) from the streaming response.

    Raises:
        LLMError: On provider error, auth failure, or network issue after retries.
    """
    load_local_env_if_present()
    if not provider_id:
        provider_id = os.getenv("EMPIRICAL_LLM_PROVIDER") or DEFAULT_PROVIDER
    if not model:
        model = os.getenv("EMPIRICAL_LLM_MODEL") or None
    preset = resolve_provider(provider_id)

    # Resolve API key (mirrors chat_completion logic)
    resolved_key = (api_key or "").strip()
    if not resolved_key and preset.id in {"grok", "xai"}:
        resolved_key = resolve_grok_api_key()
    if not resolved_key and preset.api_key_env:
        resolved_key = os.getenv(preset.api_key_env, "").strip()
    if not resolved_key and preset.id == "minimax":
        resolved_key = os.getenv("MINIMAX_TOKEN_PLAN_KEY", "").strip()

    if preset.requires_api_key and not resolved_key:
        raise LLMError(
            "missing_api_key",
            f"{preset.name} requires API key (or Grok session for provider=grok).",
        )

    selected_model = (model or _provider_default_model(preset)).strip()
    if not selected_model:
        raise LLMError("missing_model", f"{preset.name} model is required.")

    effective_base_url = base_url
    if not effective_base_url:
        effective_base_url = _provider_default_base_url(preset) or None

    extra_headers: dict[str, str] | None = None
    if preset.id == "grok" or (
        preset.id == "xai"
        and "cli-chat-proxy.grok.com" in (effective_base_url or "")
    ):
        extra_headers = _grok_extra_headers()

    if preset.api_type == "anthropic-compatible":
        normalized_base = normalize_base_url(
            effective_base_url, api_type=preset.api_type, fallback=preset.base_url
        )
        req = _build_anthropic_stream_request(
            api_key=resolved_key,
            base_url=normalized_base,
            model=selected_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        stream_fn = _stream_anthropic_compatible
    else:
        normalized_base = normalize_base_url(
            effective_base_url, api_type=preset.api_type, fallback=preset.base_url
        )
        req = _build_openai_stream_request(
            api_key=resolved_key,
            base_url=normalized_base,
            model=selected_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=extra_headers,
        )
        stream_fn = _stream_openai_compatible

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            yield from stream_fn(req)
            return
        except error.HTTPError as exc:
            last_error = LLMError(
                "provider_error",
                f"{preset.name} HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')[:300]}",
            )
        except error.URLError as exc:
            last_error = LLMError("network_error", f"Cannot reach model provider: {exc}")
        if attempt < 2:
            time.sleep(0.5 * (2 ** attempt))

    # All retries exhausted
    if isinstance(last_error, LLMError):
        raise last_error
    raise LLMError("stream_failed", f"stream failed after 3 attempts: {last_error}")


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

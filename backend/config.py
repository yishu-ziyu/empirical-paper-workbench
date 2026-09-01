"""Application configuration.

Centralized config loaded from environment variables.
"""

from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

_DEFAULT_JWT = "dev-secret-key-do-not-use-in-production"
_PLACEHOLDER_JWT = "change-this-to-a-random-secret-in-production"
_LOCAL_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
PRODUCT_ROOT = Path(__file__).resolve().parents[1]


def _resolve_local_state_root(raw: str | None = None) -> Path:
    configured = raw if raw is not None else os.getenv("ECONPAPER_LOCAL_STATE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (PRODUCT_ROOT / ".local").resolve()


LOCAL_STATE_ROOT = _resolve_local_state_root()


def _state_path(env_name: str, *parts: str) -> Path:
    configured = os.getenv(env_name)
    if configured:
        return Path(configured).expanduser().resolve()
    return LOCAL_STATE_ROOT.joinpath(*parts)


def ensure_private_directory(path: Path) -> Path:
    """Create a local-state directory and repair it to owner-only access."""
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)
    return path


def ensure_private_file(path: Path) -> Path:
    """Repair an existing local-state file to owner read/write access."""
    if path.exists():
        path.chmod(0o600)
    return path


def _cors_origin_regex() -> str | None:
    """Localhost-any-port regex is DEBUG-only. Production needs an explicit env."""
    raw = os.getenv("CORS_ORIGIN_REGEX")
    if raw is not None:
        return raw.strip() or None
    if os.getenv("DEBUG", "false").lower() == "true":
        return _LOCAL_ORIGIN_REGEX
    return None


class Settings:
    """Runtime settings for the econpaper backend."""

    # --- App ---
    APP_NAME: str = "econpaper-backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:5174,http://127.0.0.1:5174",
        ).split(",")
        if origin.strip()
    ]
    # Same-origin /api covers Vite :5174. Do not default a credentials-friendly
    # localhost-any-port regex when DEBUG=false.
    CORS_ORIGIN_REGEX: str | None = _cors_origin_regex()

    # --- Uploads ---
    UPLOAD_DIR: Path = _state_path("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    # --- Run 工件目录（trace/checkpoints/outputs，"每一步可查"的磁盘载体）---
    RUNS_DIR: str = str(_state_path("RUNS_DIR", "runs"))

    # --- 会话存储持久化文件（P1-3：重启后恢复 session/state/owner）---
    SESSIONS_PATH: str = str(
        _state_path("SESSIONS_PATH", "sessions", "sessions.json")
    )

    # --- LangGraph checkpointing (PostgreSQL) ---
    CHECKPOINT_DB_URL: str = os.getenv("CHECKPOINT_DB_URL", "")

    # --- Database (user auth) ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{_state_path('ECONPAPER_DATABASE_PATH', 'db', 'econpaper.db')}",
    )

    # --- JWT ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    # Access tokens are short-lived; renewal goes through the rotating
    # refresh cookie. ACCESS_TOKEN_EXPIRE_HOURS is kept only so existing
    # env files still parse — it is no longer read.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )
    # Enumeration guard for POST /auth/register; flip on together with the
    # email-verification flow so legitimate signups still get feedback.
    HIDE_REGISTRATION_EXISTENCE: bool = os.getenv(
        "HIDE_REGISTRATION_EXISTENCE", "false"
    ).lower() == "true"

    # --- LLM ---
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # --- S3 / Object Storage ---
    S3_ENDPOINT_URL: str | None = os.getenv("S3_ENDPOINT_URL")
    S3_ACCESS_KEY_ID: str = os.getenv("S3_ACCESS_KEY_ID", "")
    S3_SECRET_ACCESS_KEY: str = os.getenv("S3_SECRET_ACCESS_KEY", "")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "econpaper-uploads")
    S3_PATH_PREFIX: str = os.getenv("S3_PATH_PREFIX", "uploads/")
    S3_CACHE_DIR: Path = _state_path("S3_CACHE_DIR", "cache", "s3")

    # --- HTTP client ---
    HTTPX_TIMEOUT_SECONDS: float = float(os.getenv("HTTPX_TIMEOUT_SECONDS", "30.0"))


settings = Settings()


def ensure_local_state_dirs() -> None:
    """Prepare the host-local state layout before database/app startup."""
    for path in (
        LOCAL_STATE_ROOT,
        LOCAL_STATE_ROOT / "db",
        settings.UPLOAD_DIR,
        Path(settings.RUNS_DIR),
        Path(settings.SESSIONS_PATH).parent,
        settings.S3_CACHE_DIR,
        LOCAL_STATE_ROOT / "learning",
    ):
        ensure_private_directory(path)


ensure_local_state_dirs()


def _is_insecure_jwt(secret: str) -> bool:
    stripped = (secret or "").strip()
    return (
        not stripped
        or stripped in {_DEFAULT_JWT, _PLACEHOLDER_JWT}
        or len(stripped) < 32
    )


def _validate_llm_providers() -> None:
    """P1-8 fail-closed：生产拒绝 mock 生成/评审，拒绝"无 key 必落 mock"的部署。

    agent/llm/router.py 的兜底链最后一级是 mock；健康检查看不出它，
    服务绿灯但论文是占位内容。这里在启动期把这类部署直接判死。
    """
    if os.getenv("ECONPAPER_LLM", "").strip().lower() == "mock":
        print(
            "FATAL: ECONPAPER_LLM=mock is not allowed when DEBUG=false. "
            "Configure a real provider instead.",
            file=sys.stderr,
        )
        sys.exit(1)

    for prefix in ("GENERATE", "REVIEW"):
        provider = (os.getenv(f"{prefix}_LLM_PROVIDER") or "").strip().lower()
        if provider == "mock":
            print(
                f"FATAL: {prefix}_LLM_PROVIDER=mock is not allowed when DEBUG=false. "
                "Set it to a real provider (e.g. minimax / openai).",
                file=sys.stderr,
            )
            sys.exit(1)
        has_key = any(
            (os.getenv(name) or "").strip()
            for name in (
                f"{prefix}_LLM_API_KEY",
                "MINIMAX_API_KEY",
                "MINIMAX_TOKEN_PLAN_KEY",
                "OPENAI_API_KEY",
            )
        )
        if not has_key:
            print(
                f"FATAL: no API key for the {prefix} LLM. Set {prefix}_LLM_API_KEY, "
                "MINIMAX_API_KEY, or OPENAI_API_KEY. Without a key the router "
                "silently falls back to mock generation/review.",
                file=sys.stderr,
            )
            sys.exit(1)


def validate_runtime_secrets() -> None:
    """Refuse known-insecure defaults outside local debug."""
    if settings.DEBUG:
        if _is_insecure_jwt(settings.JWT_SECRET_KEY):
            settings.JWT_SECRET_KEY = secrets.token_urlsafe(48)
            print("⚠ DEBUG: generated ephemeral JWT_SECRET_KEY for this process")
        return

    if _is_insecure_jwt(settings.JWT_SECRET_KEY):
        print(
            "FATAL: JWT_SECRET_KEY is missing, too short, or a published default. "
            "Set a random secret of at least 32 characters.",
            file=sys.stderr,
        )
        sys.exit(1)

    if "*" in settings.CORS_ORIGINS:
        print("FATAL: CORS_ORIGINS=* is not allowed when DEBUG=false.", file=sys.stderr)
        sys.exit(1)

    _validate_llm_providers()


validate_runtime_secrets()


def ensure_upload_dir() -> None:
    """Create the upload directory if it does not exist."""
    ensure_private_directory(settings.UPLOAD_DIR)

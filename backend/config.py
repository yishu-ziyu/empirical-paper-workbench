"""Application configuration.

Centralized config loaded from environment variables. All values are
placeholders for now; subsequent tickets will fill in real defaults and
wire them into services.
"""

from __future__ import annotations

import os
from pathlib import Path


class Settings:
    """Runtime settings for the econpaper backend.

    Reads from environment variables with sensible placeholders so the
    app can boot before real secrets/config are provided.
    """

    # --- App ---
    APP_NAME: str = "econpaper-backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # --- CORS ---
    # Frontend dev server origin. Comma-separated list is allowed.
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ]

    # --- Uploads ---
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "./uploads"))

    # --- Run 工件目录（trace/checkpoints/outputs，"每一步可查"的磁盘载体）---
    RUNS_DIR: str = os.getenv("RUNS_DIR", "./runs")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    # --- LangGraph checkpointing (PostgreSQL) ---
    # Connection string for the PostgresSaver checkpointer.
    # Default points at localhost PostgreSQL with peer auth.
    CHECKPOINT_DB_URL: str = os.getenv(
        "CHECKPOINT_DB_URL",
        "postgresql://mahaoxuan@localhost:5432/econpaper",
    )

    # --- Database (user auth) ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./econpaper.db",
    )

    # --- JWT ---
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "dev-secret-key-do-not-use-in-production",
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_HOURS: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24")
    )

    # --- LLM (placeholders, filled by later tickets) ---
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # --- S3 / Object Storage ---
    S3_ENDPOINT_URL: str | None = os.getenv("S3_ENDPOINT_URL")
    S3_ACCESS_KEY_ID: str = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
    S3_SECRET_ACCESS_KEY: str = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "econpaper-uploads")
    S3_PATH_PREFIX: str = os.getenv("S3_PATH_PREFIX", "uploads/")
    # 本地缓存目录（用于兼容下游本地文件读取）
    S3_CACHE_DIR: Path = Path(os.getenv("S3_CACHE_DIR", "./uploads/.s3_cache"))

    # --- HTTP client ---
    HTTPX_TIMEOUT_SECONDS: float = float(os.getenv("HTTPX_TIMEOUT_SECONDS", "30.0"))


settings = Settings()


def ensure_upload_dir() -> None:
    """Create the upload directory if it does not exist."""
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

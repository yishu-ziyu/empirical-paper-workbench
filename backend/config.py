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
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    # --- LangGraph checkpointing ---
    # Placeholder connection string for a SQLite/Postgres checkpoint store.
    CHECKPOINT_DB_URL: str = os.getenv(
        "CHECKPOINT_DB_URL", "sqlite:///./checkpoints.sqlite"
    )

    # --- LLM (placeholders, filled by later tickets) ---
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # --- HTTP client ---
    HTTPX_TIMEOUT_SECONDS: float = float(os.getenv("HTTPX_TIMEOUT_SECONDS", "30.0"))


settings = Settings()


def ensure_upload_dir() -> None:
    """Create the upload directory if it does not exist."""
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

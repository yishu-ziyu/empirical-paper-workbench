"""Local acceptance server for the real brief stream.

Run: PYTHONPATH=. python demo_server.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def _strip_inline_comment(value: str) -> str:
    if " #" in value:
        value = value.split(" #", 1)[0]
    return value.strip().strip('"').strip("'")


def _load_local_env(env_path: Path = REPO_ROOT / ".env.local") -> None:
    if not env_path.is_file():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue

        os.environ[key] = _strip_inline_comment(value)


_load_local_env()
sys.path.insert(0, str(REPO_ROOT))

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Demo server: real brief stream")
    print("Local env loaded from .env.local when present")
    print("Open http://localhost:8765/docs to see OpenAPI")
    print("=" * 60)
    uvicorn.run(
        "Product.app:app",
        host="127.0.0.1",
        port=8765,
        log_level="info",
    )

"""Load ~/.config/ai-providers/env.local into the process env.

Does not overwrite keys already set. Does not log values.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

SSOT_ENV = Path.home() / ".config" / "ai-providers" / "env.local"

_LOADED = False


def in_pytest() -> bool:
    return "pytest" in sys.modules or bool(os.environ.get("PYTEST_CURRENT_TEST"))


def load_ssot() -> None:
    """Fill missing os.environ keys from the machine SSOT file."""
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    if not SSOT_ENV.is_file():
        return
    try:
        text = SSOT_ENV.read_text(encoding="utf-8")
    except OSError:
        return
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value

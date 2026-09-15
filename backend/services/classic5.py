"""classic-5 catalog loader for formal TITLE/TOPIC attach.

Binds catalog bytes from ``fixtures/classic-5/`` or ``ECONPAPER_CLASSIC5_*``.
Does not rank entries (DC-BE-suggest) and does not boot Card.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi import HTTPException

from config import PRODUCT_ROOT


CATALOG_ID = "classic-5"
_ENTRY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SUFFIXES = (".csv", ".dta", ".xlsx")
_ROOT_ENV_KEYS = frozenset({"ECONPAPER_CLASSIC5_ROOT", "ECONPAPER_CLASSIC5_DIR"})


def classic5_root() -> Path:
    """Reserved catalog tree, overridable by ``ECONPAPER_CLASSIC5_ROOT`` / ``_DIR``."""
    raw = (
        os.getenv("ECONPAPER_CLASSIC5_ROOT") or os.getenv("ECONPAPER_CLASSIC5_DIR") or ""
    ).strip()
    if raw:
        return Path(raw).expanduser()
    return PRODUCT_ROOT / "fixtures" / "classic-5"


def _entry_env_key(entry_id: str) -> str:
    return "ECONPAPER_CLASSIC5_" + re.sub(r"[^A-Za-z0-9]", "_", entry_id).upper()


def resolve_classic5_entry(entry_id: str) -> Path:
    """Resolve one catalog entry. Rejects path traversal and Card boot paths."""
    if not _ENTRY_RE.fullmatch(entry_id):
        raise HTTPException(status_code=400, detail="invalid_classic5_entry")

    env_key = _entry_env_key(entry_id)
    if env_key not in _ROOT_ENV_KEYS:
        env_path = (os.getenv(env_key) or "").strip()
        if env_path:
            path = Path(env_path).expanduser()
            if path.is_file():
                return path
            raise HTTPException(status_code=400, detail="classic5_entry_not_found")

    root = classic5_root()
    try:
        root_resolved = root.resolve()
    except OSError as exc:
        raise HTTPException(status_code=400, detail="classic5_entry_not_found") from exc

    for suffix in _SUFFIXES:
        candidate = (root / f"{entry_id}{suffix}").resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail="classic5_entry_not_found"
            ) from exc
        if candidate.is_file():
            return candidate

    raise HTTPException(status_code=400, detail="classic5_entry_not_found")


def classic5_candidate(entry_id: str) -> dict[str, object]:
    return {
        "source": CATALOG_ID,
        "catalog": CATALOG_ID,
        "entry_id": entry_id,
        "catalog_data": True,
    }

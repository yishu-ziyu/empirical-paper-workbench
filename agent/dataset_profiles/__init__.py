"""Dataset profile registry (T-11).

Each profile is a YAML file in this directory describing how to identify
and map a known survey dataset (CHARLS / CFPS / CGSS / ...). The registry
exposes a single function ``load_profile(name)`` that returns the parsed
YAML as a dict (or ``None`` if no profile matches ``name``).

Profiles are looked up by stem: ``charls.yaml`` → ``load_profile("charls")``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

_PROFILES_DIR = Path(__file__).resolve().parent


def load_profile(name: str) -> Optional[dict]:
    """Load a dataset profile by stem name.

    Parameters
    ----------
    name : str
        Profile stem (case-insensitive). ``"charls"`` resolves to
        ``charls.yaml`` in this directory.

    Returns
    -------
    dict or None
        Parsed YAML content, or ``None`` if no matching file exists.
    """
    if not name:
        return None
    candidate = _PROFILES_DIR / f"{name.lower()}.yaml"
    if not candidate.is_file():
        return None
    with candidate.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


__all__ = ["load_profile"]

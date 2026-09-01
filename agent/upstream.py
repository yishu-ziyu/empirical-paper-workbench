"""Local dependency contract for econpaper.

``econpaper`` is the only product in this workspace. Source checkouts that
the product imports live under one configurable dependency root; historical
research repositories are not runtime dependencies.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import unquote, urlparse


PRODUCT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PRODUCT_ROOT.parent


def _resolve_dependency_root(raw: str | None = None) -> Path:
    """Resolve the dependency root without relying on the process CWD."""
    configured = raw if raw is not None else os.environ.get("ECONPAPER_DEPENDENCY_ROOT")
    if configured:
        candidate = Path(configured).expanduser()
        if not candidate.is_absolute():
            candidate = WORKSPACE_ROOT / candidate
        return candidate.resolve()
    return (WORKSPACE_ROOT / "dependencies").resolve()


DEPENDENCY_ROOT = _resolve_dependency_root()

# StatsPAI is the only checkout currently imported by production paths.
STATSPAI_REPO_PATH = DEPENDENCY_ROOT / "StatsPAI"
STATSPAI_IMPORT_NAME = "statspai"
STATSPAI_EXPECTED_VERSION = "1.22.0"


def _env_flag(name: str, default: bool = False) -> bool:
    """Read a conventional boolean environment variable."""
    value = (os.environ.get(name) or "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on")


# Default false: estimation keeps deterministic StatsPAI dispatch unless the
# experimental Pydantic AI arm is explicitly enabled.
ESTIMATE_AGENT_ENABLED = _env_flag("ECONPAPER_ESTIMATE_AGENT", False)


def _editable_source(distribution_name: str) -> Path | None:
    """Return an editable distribution's source directory, when recorded."""
    try:
        distribution = importlib.metadata.distribution(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return None

    direct_url = Path(distribution._path) / "direct_url.json"
    try:
        payload = json.loads(direct_url.read_text(encoding="utf-8"))
    except (AttributeError, OSError, TypeError, ValueError):
        return None
    if not payload.get("dir_info", {}).get("editable"):
        return None

    parsed = urlparse(payload.get("url", ""))
    if parsed.scheme != "file":
        return None
    return Path(unquote(parsed.path)).resolve()


def get_dependency_status() -> dict:
    """Return truthful checkout and editable-install status for diagnostics."""
    spec = importlib.util.find_spec(STATSPAI_IMPORT_NAME)
    editable_source = _editable_source("StatsPAI")
    expected_source = STATSPAI_REPO_PATH.resolve()
    source_matches = editable_source == expected_source

    return {
        "dependency_root": str(DEPENDENCY_ROOT),
        "statspai": {
            "repo_path": str(STATSPAI_REPO_PATH),
            "repo_exists": STATSPAI_REPO_PATH.is_dir(),
            "installed": spec is not None,
            "editable_source": str(editable_source) if editable_source else None,
            "source_matches_repo": source_matches,
            "import_name": STATSPAI_IMPORT_NAME,
            "expected_version": STATSPAI_EXPECTED_VERSION,
            "diagnostic": (
                None
                if source_matches
                else "Run `python -m pip install -e ../dependencies/StatsPAI` "
                "from econpaper with the target virtual environment active."
            ),
        },
    }


__all__ = [
    "PRODUCT_ROOT",
    "WORKSPACE_ROOT",
    "DEPENDENCY_ROOT",
    "STATSPAI_REPO_PATH",
    "STATSPAI_IMPORT_NAME",
    "STATSPAI_EXPECTED_VERSION",
    "ESTIMATE_AGENT_ENABLED",
    "get_dependency_status",
]

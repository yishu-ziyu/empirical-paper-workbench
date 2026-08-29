"""Upstream dependency paths for econpaper.

Three upstream repos are referenced (private-fork policy: read-only, never
modify upstream code):

  1. StatsPAI     — Python package, `pip install -e` into backend venv
  2. AERS         — skill library (markdown), referenced as prompt resource
  3. stata-code   — code-translation engine, `pip install -e` if Python package

Paths are absolute so backend (FastAPI) and agent (LangGraph) can both import
this module without CWD ambiguity.
"""

from pathlib import Path

import os

# Workspace root: /Users/mahaoxuan/Desktop/经济学论文
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# 1. StatsPAI — Python package (src/statspai/, pyproject.toml, v1.22.0)
# ---------------------------------------------------------------------------
# Repo:    /Users/mahaoxuan/Desktop/经济学论文/StatsPAI
# Import:  `import statspai as sp`
# Install: `pip install -e /Users/mahaoxuan/Desktop/经济学论文/StatsPAI`
#          (run inside econpaper/backend/.venv once that venv exists)
# Status:  PENDING — backend venv not yet created (see ticket 01).
#          Once `python -m venv econpaper/backend/.venv` is done, run the
#          editable install and flip STATSPAI_INSTALLED to True.
STATSPAI_REPO_PATH = WORKSPACE_ROOT / "StatsPAI"
STATSPAI_INSTALLED = False
STATSPAI_IMPORT_NAME = "statspai"
STATSPAI_EXPECTED_VERSION = "1.22.0"

# ---------------------------------------------------------------------------
# 2. AERS — Auto-Empirical-Research-Skills (skill library, NOT a Python pkg)
# ---------------------------------------------------------------------------
# AERS is a catalog of SKILL.md files (1,150 skills across 69 collections).
# It is loaded as a prompt/resource by LangGraph nodes, not pip-installed.
#
# Canonical copy is `_refs/AERS-ref/` (read-only upstream mirror).
# The old root clone `Auto-Empirical-Research-Skills/` was removed 2026-08-13.
AERS_SKILLS_PATH = WORKSPACE_ROOT / "_refs" / "AERS-ref" / "skills"
AERS_SKILLS_PATH_FALLBACK = WORKSPACE_ROOT / "_refs" / "AERS-ref" / "skills"
AERS_CATALOG_JSON = WORKSPACE_ROOT / "_refs" / "AERS-ref" / "catalog" / "skills.json"

# ---------------------------------------------------------------------------
# 3. stata-code — code-translation engine (Python → Stata/R/EViews)
# ---------------------------------------------------------------------------
# Per spec (econpaper/docs/specs/copaper-pivot-v1.md §6) the graph's
# `translate_code` node should call `stata_code.translate(python_ast, target="stata")`.
#
# Repo expected at: /Users/mahaoxuan/Desktop/经济学论文/stata-code
# Status: MISSING — the `stata-code/` repo has NOT been cloned into the
#          workspace yet. Neither `stata-code/`, `stata_code/`, nor
#          `_refs/stata-code-ref/` exists.
# TODO:  Once the repo is cloned:
#          - if it has pyproject.toml/setup.py → `pip install -e` into backend venv
#          - if it is a CLI tool / pure scripts  → set STATA_CODE_PATH to its
#            executable and flip STATA_CODE_INSTALLED to True
STATA_CODE_REPO_PATH = WORKSPACE_ROOT / "stata-code"  # expected, not yet present
STATA_CODE_INSTALLED = False
STATA_CODE_IMPORT_NAME = "stata_code"  # try this first, then "stata-code"


# ---------------------------------------------------------------------------
# 4. Phase A：估计 Agent 开关（LLM + 沙箱执行器，见 engine/estimate_agent.py）
# ---------------------------------------------------------------------------
def _env_flag(name: str, default: bool = False) -> bool:
    """读布尔环境变量：1/true/yes/on 开，其余关。"""
    value = (os.environ.get(name) or "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on")


# 默认 false：estimate 节点维持固定分派（StatsPAI），开启后先试 Pydantic AI
# 估计 Agent，任何异常回退固定分派。env 可覆盖：ECONPAPER_ESTIMATE_AGENT=1。
ESTIMATE_AGENT_ENABLED = _env_flag("ECONPAPER_ESTIMATE_AGENT", False)


def _resolve_aers_path() -> Path:
    """Return the first AERS skills path that exists on disk."""
    if AERS_SKILLS_PATH.is_dir():
        return AERS_SKILLS_PATH
    if AERS_SKILLS_PATH_FALLBACK.is_dir():
        return AERS_SKILLS_PATH_FALLBACK
    raise FileNotFoundError(
        f"AERS skills directory not found. Tried:\n"
        f"  {AERS_SKILLS_PATH}\n  {AERS_SKILLS_PATH_FALLBACK}"
    )


def get_dependency_status() -> dict:
    """Return a snapshot of all upstream dependency paths and install state.

    Useful for a future `GET /dependencies` debug endpoint on the backend.
    """
    aers_ok = False
    aers_resolved = None
    try:
        aers_resolved = _resolve_aers_path()
        aers_ok = True
    except FileNotFoundError:
        pass

    return {
        "statspai": {
            "repo_path": str(STATSPAI_REPO_PATH),
            "repo_exists": STATSPAI_REPO_PATH.is_dir(),
            "installed": STATSPAI_INSTALLED,
            "import_name": STATSPAI_IMPORT_NAME,
            "expected_version": STATSPAI_EXPECTED_VERSION,
            "todo": (
                "Run `pip install -e "
                f"{STATSPAI_REPO_PATH}` inside econpaper/backend/.venv "
                "once that venv is created."
            ),
        },
        "aers": {
            "primary_path": str(AERS_SKILLS_PATH),
            "fallback_path": str(AERS_SKILLS_PATH_FALLBACK),
            "resolved_path": str(aers_resolved) if aers_resolved else None,
            "available": aers_ok,
            "catalog_json": str(AERS_CATALOG_JSON),
            "catalog_exists": AERS_CATALOG_JSON.is_file(),
        },
        "stata_code": {
            "repo_path": str(STATA_CODE_REPO_PATH),
            "repo_exists": STATA_CODE_REPO_PATH.is_dir(),
            "installed": STATA_CODE_INSTALLED,
            "import_name": STATA_CODE_IMPORT_NAME,
            "todo": (
                "Clone the `stata-code` repo into the workspace root, then "
                "either `pip install -e` it (if Python pkg) or set "
                "STATA_CODE_PATH to its CLI executable."
            ),
        },
    }


__all__ = [
    "WORKSPACE_ROOT",
    "STATSPAI_REPO_PATH",
    "STATSPAI_INSTALLED",
    "STATSPAI_IMPORT_NAME",
    "STATSPAI_EXPECTED_VERSION",
    "AERS_SKILLS_PATH",
    "AERS_SKILLS_PATH_FALLBACK",
    "AERS_CATALOG_JSON",
    "STATA_CODE_REPO_PATH",
    "STATA_CODE_INSTALLED",
    "STATA_CODE_IMPORT_NAME",
    "ESTIMATE_AGENT_ENABLED",
    "get_dependency_status",
]

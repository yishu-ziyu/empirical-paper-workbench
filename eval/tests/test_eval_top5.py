"""EVAL-top5 scaffold: optional, offline, never catalog gold."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

EVAL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = EVAL_DIR.parent
HARNESS_PATH = EVAL_DIR / "harness.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("eval_top5_harness", HARNESS_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


harness = _load_harness()

CATALOG_AND_FARM_IDS = (
    "classic-5",
    "ck1994",
    "ck1994_long",
    "barro1991_growth",
    "schooling-wages",
    "undergrad_did_01",
    "card_1995",
)


def test_default_run_skips_without_flag():
    result = harness.run(environ={})
    assert result["status"] == "skipped"
    assert result["product_runtime"] is False
    assert result["catalog_answer_key"] is False


def test_offline_without_submodule_is_set_absent_not_product_failure():
    result = harness.run(offline=True, environ={})
    assert result["status"] == "set_absent"
    assert result["pointer"] == "eval/top5-set.submodule"
    assert not harness.set_present()


def _env_without_flag() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("ECONPAPER_EVAL_TOP5", None)
    return env


def test_cli_default_exits_zero_and_skips():
    proc = subprocess.run(
        [sys.executable, str(HARNESS_PATH)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=_env_without_flag(),
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["status"] == "skipped"


def test_flag_without_set_exits_zero():
    env = _env_without_flag()
    env["ECONPAPER_EVAL_TOP5"] = "1"
    proc = subprocess.run(
        [sys.executable, str(HARNESS_PATH), "--offline"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["status"] == "set_absent"


@pytest.mark.parametrize("identity", CATALOG_AND_FARM_IDS)
def test_catalog_and_farm_ids_are_not_gold(identity: str):
    with pytest.raises(harness.CatalogGoldError):
        harness.refuse_catalog_gold(identity)


def test_present_set_ok_when_five_opaque_slots(tmp_path: Path):
    set_dir = tmp_path / "top5-set"
    set_dir.mkdir()
    (set_dir / "manifest.json").write_text(
        json.dumps(
            {
                "eval_id": "EVAL-top5",
                "slots": ["slot-01", "slot-02", "slot-03", "slot-04", "slot-05"],
            }
        ),
        encoding="utf-8",
    )
    result = harness.run(offline=True, environ={}, set_dir=set_dir)
    assert result == {
        "status": "ok",
        "eval_id": "EVAL-top5",
        "slots": 5,
        "gold_body_reads": False,
        "catalog_answer_key": False,
        "product_runtime": False,
    }


def test_manifest_rejects_catalog_id_as_slot(tmp_path: Path):
    set_dir = tmp_path / "top5-set"
    set_dir.mkdir()
    (set_dir / "manifest.json").write_text(
        json.dumps({"eval_id": "EVAL-top5", "slots": ["ck1994_long"]}),
        encoding="utf-8",
    )
    with pytest.raises(harness.CatalogGoldError):
        harness.load_set_manifest(set_dir)


def test_manifest_rejects_gold_body_and_out_surfaces(tmp_path: Path):
    set_dir = tmp_path / "top5-set"
    set_dir.mkdir()
    (set_dir / "manifest.json").write_text(
        json.dumps(
            {
                "eval_id": "EVAL-top5",
                "slots": ["slot-01"],
                "gold_body": "chapter text",
                "ppt": True,
                "xhs": True,
                "p_hack": True,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(harness.ScopeError):
        harness.load_set_manifest(set_dir)


def test_manifest_rejects_farm_size(tmp_path: Path):
    set_dir = tmp_path / "top5-set"
    set_dir.mkdir()
    (set_dir / "manifest.json").write_text(
        json.dumps({"eval_id": "EVAL-top5", "slots": [f"slot-{i:02d}" for i in range(1, 8)]}),
        encoding="utf-8",
    )
    with pytest.raises(harness.ScopeError):
        harness.load_set_manifest(set_dir)


def test_scaffold_slots_are_five_and_not_catalog():
    data = harness.load_slots()
    assert data["slots"] == ["slot-01", "slot-02", "slot-03", "slot-04", "slot-05"]
    assert set(data["slots"]).isdisjoint(CATALOG_AND_FARM_IDS)


def test_not_on_agent_eval_farm_path():
    assert not (REPO_ROOT / "agent" / "eval" / "tasks" / "EVAL-top5").exists()
    assert (EVAL_DIR / "harness.py").is_file()
    assert not (REPO_ROOT / "fixtures" / "classic-5" / "eval-top5").exists()


def _product_sources(root: Path):
    """Product source files under ``root``, skipping vendored trees.

    ``agent/.venv`` and ``frontend/node_modules`` live inside the scanned roots
    on a working checkout; they ship fixtures that are not UTF-8 (e.g. joblib's
    big5-encoded sample), which would crash the read below. Isolation is about
    first-party product sources, so those trees are pruned.
    """
    skip_dirs = {".venv", "node_modules", "__pycache__", ".git", ".mypy_cache"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in skip_dirs)
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix not in {".py", ".ts", ".tsx"}:
                continue
            if "eval/tests" in path.as_posix():
                continue
            yield path


def test_product_sources_do_not_import_this_harness():
    needles = ("eval.harness", "from eval ", "import eval.")
    roots = (REPO_ROOT / "agent", REPO_ROOT / "backend", REPO_ROOT / "frontend" / "src")
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in _product_sources(root):
            text = path.read_text(encoding="utf-8")
            if any(needle in text for needle in needles):
                hits.append(str(path.relative_to(REPO_ROOT)))
    assert hits == []


def test_harness_is_stdlib_only():
    source = HARNESS_PATH.read_text(encoding="utf-8")
    for banned in ("import agent", "import backend", "classic5", "pywinsor", "find_lit"):
        assert banned not in source


def test_default_pytest_testpaths_exclude_eval():
    ini = (REPO_ROOT / "pytest.ini").read_text(encoding="utf-8")
    assert "testpaths = agent/tests backend/tests" in ini
    assert "eval/tests" not in ini


def test_optional_submodule_is_pointer_not_product_gitmodules():
    gitmodules = REPO_ROOT / ".gitmodules"
    if gitmodules.is_file():
        assert "eval/top5-set" not in gitmodules.read_text(encoding="utf-8")
    pointer = (EVAL_DIR / "top5-set.submodule").read_text(encoding="utf-8")
    assert "path = eval/top5-set" in pointer
    assert "REPLACE_WITH_EVAL_TOP5_REMOTE" in pointer

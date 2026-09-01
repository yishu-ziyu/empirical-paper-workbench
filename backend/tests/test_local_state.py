import os
import subprocess
import sys
from pathlib import Path

import facade.session_store as session_store_module
from config import (
    PRODUCT_ROOT,
    ensure_private_directory,
    ensure_private_file,
    _resolve_local_state_root,
)

SessionStore = session_store_module.SessionStore


def test_default_local_state_root_is_product_owned(monkeypatch):
    monkeypatch.delenv("ECONPAPER_LOCAL_STATE_ROOT", raising=False)
    assert _resolve_local_state_root() == PRODUCT_ROOT / ".local"


def test_local_state_root_can_be_overridden(tmp_path):
    target = tmp_path / "private state"
    assert _resolve_local_state_root(str(target)) == target.resolve()


def test_private_directory_repairs_permissions(tmp_path):
    target = tmp_path / "state"
    target.mkdir(mode=0o755)
    ensure_private_directory(target)
    assert target.stat().st_mode & 0o777 == 0o700


def test_private_file_repairs_permissions(tmp_path):
    target = tmp_path / "state.json"
    target.write_text("{}", encoding="utf-8")
    target.chmod(0o644)
    ensure_private_file(target)
    assert target.stat().st_mode & 0o777 == 0o600


def test_conftest_overrides_inherited_user_state_path(tmp_path):
    sentinel = tmp_path / "must-not-be-used.json"
    env = os.environ.copy()
    env["SESSIONS_PATH"] = str(sentinel)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import os, conftest; print(os.environ['SESSIONS_PATH'])",
        ],
        cwd=PRODUCT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    isolated_path = Path(result.stdout.strip())
    assert isolated_path != sentinel
    assert "ep-test-state-" in str(isolated_path)
    assert not sentinel.exists()


def test_session_store_recovers_state_after_restart(tmp_path, monkeypatch):
    session_path = tmp_path / "sessions.json"
    monkeypatch.setattr(session_store_module.settings, "SESSIONS_PATH", str(session_path))

    first = SessionStore()
    first.create("session-1", user_id=7)
    first.save_state("session-1", {"stage": "outline"})

    restarted = SessionStore()
    assert restarted.get_owner("session-1") == 7
    assert restarted.get_state("session-1") == {"stage": "outline"}


def test_session_store_backs_up_corrupt_file(tmp_path, monkeypatch):
    session_path = tmp_path / "sessions.json"
    session_path.write_text("not-json", encoding="utf-8")
    monkeypatch.setattr(session_store_module.settings, "SESSIONS_PATH", str(session_path))

    store = SessionStore()

    assert store.sessions == {}
    assert store.degradations == {}
    assert session_path.with_suffix(".json.corrupt").read_text(encoding="utf-8") == "not-json"


def test_session_store_failed_replace_keeps_memory_state(
    tmp_path, monkeypatch, capsys
):
    session_path = tmp_path / "sessions.json"
    monkeypatch.setattr(session_store_module.settings, "SESSIONS_PATH", str(session_path))
    store = SessionStore()
    store.sessions["session-1"] = {"user_id": 7}

    def fail_replace(*_args):
        raise OSError("disk unavailable")

    monkeypatch.setattr(session_store_module.os, "replace", fail_replace)
    store.flush()

    assert store.sessions["session-1"] == {"user_id": 7}
    assert "flush failed: disk unavailable" in capsys.readouterr().err

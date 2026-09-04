import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import facade.session_store as session_store_module
import storage.s3 as s3_module
from sqlalchemy import delete
from config import (
    PRODUCT_ROOT,
    ensure_private_directory,
    ensure_private_file,
    _resolve_local_state_root,
)
from database import create_tables, session_factory, sync_session_factory
from models.research_session import DataMigration, ResearchSession, SessionDegradation
from session_migration import _MIGRATION_NAME, migrate_legacy_sessions

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


def test_session_store_recovers_state_after_restart():
    first = SessionStore()
    session_id = "session-store-restart"
    first.drop(session_id)
    first.create(session_id, user_id=7)
    first.save_state(session_id, {"stage": "outline"})

    restarted = SessionStore()
    try:
        assert restarted.get_owner(session_id) == 7
        assert restarted.get_state(session_id) == {"stage": "outline"}
    finally:
        first.drop(session_id)


def test_session_store_instances_share_live_database_state():
    writer = SessionStore()
    reader = SessionStore()
    session_id = "session-store-cross-process"

    writer.drop(session_id)
    try:
        writer.create(session_id, user_id=7)
        writer.save_state(
            session_id,
            {"stage": "outline", "csv_path": "/tmp/shared.csv"},
        )

        assert reader.get_owner(session_id) == 7
        assert reader.get_state(session_id) == {
            "stage": "outline",
            "csv_path": "/tmp/shared.csv",
        }
        with sync_session_factory()() as db:
            stored = db.get(ResearchSession, session_id)
            assert stored is not None
            assert stored.csv_path == "/tmp/shared.csv"
            assert "csv_path" not in stored.state
    finally:
        writer.drop(session_id)


def test_csv_path_recovery_does_not_mutate_database(tmp_path, monkeypatch):
    store = SessionStore()
    session_id = "session-read-only-path-recovery"
    original_path = str(tmp_path / "missing.csv")
    cache_dir = tmp_path / "cache"
    store.drop(session_id)
    store.seed(session_id, {"csv_path": original_path})
    monkeypatch.setattr(session_store_module.settings, "S3_ENDPOINT_URL", "http://s3")
    monkeypatch.setattr(session_store_module.settings, "S3_CACHE_DIR", str(cache_dir))
    monkeypatch.setattr(s3_module.s3_fs, "exists", lambda _remote: True)

    def download(_remote, local_path):
        Path(local_path).write_text("x\n1\n", encoding="utf-8")

    monkeypatch.setattr(s3_module.s3_fs, "download_to_file", download)
    try:
        assert store.get_csv_path(session_id) == str(cache_dir / f"{session_id}.csv")
        with sync_session_factory()() as db:
            stored = db.get(ResearchSession, session_id)
            assert stored is not None
            assert stored.csv_path == original_path
    finally:
        store.drop(session_id)


def test_legacy_json_sessions_are_imported_once(tmp_path, monkeypatch):
    session_path = tmp_path / "sessions.json"
    session_id = "legacy-json-session"
    legacy_data = {
        "sessions": {
            session_id: {
                "user_id": 7,
                "csv_path": "/tmp/legacy.csv",
                "state": {
                    "stage": "outline",
                    "csv_path": "/tmp/stale-state-copy.csv",
                },
                "custom": "preserved",
            }
        },
        "degradations": {
            session_id: [
                {"node": "legacy", "reason": "old", "fallback": "safe"}
            ]
        },
    }
    monkeypatch.setattr(session_store_module.settings, "SESSIONS_PATH", str(session_path))

    async def scenario():
        async with session_factory()() as db:
            async with db.begin():
                await db.execute(
                    delete(SessionDegradation).where(
                        SessionDegradation.session_id == session_id
                    )
                )
                await db.execute(
                    delete(ResearchSession).where(
                        ResearchSession.session_id == session_id
                    )
                )
                await db.execute(
                    delete(DataMigration).where(DataMigration.name == _MIGRATION_NAME)
                )
        session_path.write_text(json.dumps(legacy_data), encoding="utf-8")
        # Exercise the real API/runner bootstrap entrypoint, not the migration
        # helper in isolation.
        await create_tables()
        session_path.write_text(
            json.dumps(
                {
                    "sessions": {
                        session_id: {"state": {"stage": "must-not-overwrite"}}
                    }
                }
            ),
            encoding="utf-8",
        )
        await create_tables()

    asyncio.run(scenario())
    store = SessionStore()
    try:
        assert store.get_owner(session_id) == 7
        assert store.get_state(session_id) == {
            "stage": "outline",
            "csv_path": "/tmp/legacy.csv",
        }
        with sync_session_factory()() as db:
            stored = db.get(ResearchSession, session_id)
            assert stored is not None
            assert stored.csv_path == "/tmp/legacy.csv"
            assert "csv_path" not in stored.state
        assert store.get_entry(session_id)["custom"] == "preserved"
        assert store.get_degradations(session_id)[0]["node"] == "legacy"
        assert session_path.exists()
        assert session_path.with_suffix(".json.migrated").exists()
    finally:
        store.drop(session_id)


def test_concurrent_sqlite_startup_imports_legacy_data_once(tmp_path, monkeypatch):
    session_path = tmp_path / "sessions.json"
    session_id = "legacy-concurrent-session"
    monkeypatch.setattr(session_store_module.settings, "SESSIONS_PATH", str(session_path))

    async def scenario():
        async with session_factory()() as db:
            async with db.begin():
                await db.execute(
                    delete(SessionDegradation).where(
                        SessionDegradation.session_id == session_id
                    )
                )
                await db.execute(
                    delete(ResearchSession).where(
                        ResearchSession.session_id == session_id
                    )
                )
                await db.execute(
                    delete(DataMigration).where(DataMigration.name == _MIGRATION_NAME)
                )
        session_path.write_text(
            json.dumps(
                {
                    "sessions": {session_id: {"state": {"stage": "outline"}}},
                    "degradations": {
                        session_id: [
                            {"node": "legacy", "reason": "old", "fallback": "safe"}
                        ]
                    },
                }
            ),
            encoding="utf-8",
        )
        await asyncio.gather(migrate_legacy_sessions(), migrate_legacy_sessions())

    asyncio.run(scenario())
    store = SessionStore()
    try:
        assert store.get_state(session_id) == {"stage": "outline"}
        assert len(store.get_degradations(session_id)) == 1
    finally:
        store.drop(session_id)


def test_legacy_degradations_merge_with_existing_history(tmp_path, monkeypatch):
    session_path = tmp_path / "sessions.json"
    session_id = "legacy-degradation-merge"
    monkeypatch.setattr(session_store_module.settings, "SESSIONS_PATH", str(session_path))

    store = SessionStore()
    store.drop(session_id)
    store.create(session_id, user_id=7)
    store.record_degradation(session_id, "current", "new", "keep")

    async def scenario():
        async with session_factory()() as db:
            async with db.begin():
                await db.execute(
                    delete(DataMigration).where(DataMigration.name == _MIGRATION_NAME)
                )
        session_path.write_text(
            json.dumps(
                {
                    "degradations": {
                        session_id: [
                            {"node": "legacy", "reason": "old", "fallback": "safe"}
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )
        await migrate_legacy_sessions()

    asyncio.run(scenario())
    try:
        assert [item["node"] for item in store.get_degradations(session_id)] == [
            "current",
            "legacy",
        ]
    finally:
        store.drop(session_id)


def test_corrupt_legacy_json_is_backed_up_without_blocking_startup(
    tmp_path, monkeypatch, capsys
):
    session_path = tmp_path / "sessions.json"
    monkeypatch.setattr(session_store_module.settings, "SESSIONS_PATH", str(session_path))

    async def scenario():
        await create_tables()
        async with session_factory()() as db:
            async with db.begin():
                await db.execute(
                    delete(DataMigration).where(DataMigration.name == _MIGRATION_NAME)
                )
        session_path.write_text("not-json", encoding="utf-8")
        await migrate_legacy_sessions()

    asyncio.run(scenario())
    assert session_path.with_suffix(".json.corrupt").read_text(encoding="utf-8") == "not-json"
    assert "failed to read" in capsys.readouterr().err

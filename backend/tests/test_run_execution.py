"""Durable run execution contracts for long pre-write work."""

from __future__ import annotations

import asyncio
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from functools import partial
from pathlib import Path

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from database import Base, _ensure_run_lifecycle_constraints
from facade import facade
from models.research_session import ResearchSession
from models.run import Run, RunEvent
from prewrite_supervisor import execute_prewrite_supervised, execute_upload_supervised
from run_repository import (
    IdempotencyConflict,
    LeaseLost,
    QueueFull,
    RunRepository,
    SessionNotFound,
    upload_fingerprint,
)
from runner import _heartbeat, process_one_run
from tests.spawn_helpers import (
    blocking_upload_with_descendant,
    blocking_prewrite_with_descendant,
    fail_upload_with_sensitive_text,
    fail_with_sensitive_text,
    return_unreadable_upload_result,
    return_requested_state,
    write_upload_result,
)


def _direction() -> dict:
    return {
        "question": "年龄与收入",
        "dv": "income",
        "iv": "age",
        "controls": [],
        "method": "OLS",
        "template": "cn_journal",
    }


def _wait_for_path(path: Path, *, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return True
        time.sleep(0.01)
    return path.exists()


def _use_child_executor(monkeypatch, executor) -> None:
    monkeypatch.setattr(
        "runner.execute_prewrite_supervised",
        partial(execute_prewrite_supervised, child_executor=executor),
    )


def _use_upload_child_executor(monkeypatch, executor) -> None:
    monkeypatch.setattr(
        "runner.execute_upload_supervised",
        partial(execute_upload_supervised, child_executor=executor),
    )


async def _admit_upload(
    *,
    session_id: str,
    csv_path: Path,
    initial_state: dict | None = None,
):
    state = {
        "csv_path": str(csv_path),
        "uploaded_datasets": [{"path": str(csv_path), "format": "csv"}],
        **(initial_state or {}),
    }
    return await RunRepository().admit_upload(
        session_id=session_id,
        user_id=None,
        csv_path=str(csv_path),
        dataset_meta={"columns": ["x", "y"], "rows": 1},
        initial_state=state,
        idempotency_key=f"{session_id}-key",
        input_fingerprint=upload_fingerprint(csv_path.read_bytes(), csv_path.name),
    )


def test_direction_returns_202_without_running_prewrite(client, monkeypatch):
    sid = "test-run-accepted"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    called = False

    def should_not_run(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("prewrite must not execute in the API request")

    monkeypatch.setattr(facade, "execute_prewrite", should_not_run)
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-accepted-1"},
        )
        assert response.status_code == 202, response.text
        payload = response.json()
        assert payload["status"] == "PENDING"
        assert payload["run_id"]
        assert payload["events_url"] == f"/api/runs/{payload['run_id']}/events"
        assert called is False

        status = client.get(f"/runs/{payload['run_id']}")
        assert status.status_code == 200, status.text
        assert status.json()["status"] == "PENDING"
    finally:
        facade.drop_session(sid)


def test_direction_idempotency_returns_the_original_run(client):
    sid = "test-run-idempotency"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        headers = {"Idempotency-Key": "direction-idempotency-1"}
        first = client.post(f"/sessions/{sid}/direction", json=_direction(), headers=headers)
        second = client.post(f"/sessions/{sid}/direction", json=_direction(), headers=headers)
        assert first.status_code == second.status_code == 202
        assert first.json()["run_id"] == second.json()["run_id"]
    finally:
        facade.drop_session(sid)


def test_direction_requires_an_idempotency_key(client):
    sid = "test-run-idempotency-required"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        response = client.post(f"/sessions/{sid}/direction", json=_direction())
        assert response.status_code == 422
    finally:
        facade.drop_session(sid)


def test_direction_returns_404_if_session_disappears_during_admission(
    client, monkeypatch
):
    sid = "test-run-admission-delete-race"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})

    def delete_after_ownership_check(_session_id: str) -> dict:
        facade.drop_session(sid)
        return {"csv_path": "/tmp/input.csv"}

    monkeypatch.setattr(facade, "prepare_prewrite_state", delete_after_ownership_check)
    response = client.post(
        f"/sessions/{sid}/direction",
        json=_direction(),
        headers={"Idempotency-Key": "direction-delete-race-1"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test_direction_busy_returns_the_active_run_id(client):
    sid = "test-run-session-busy"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        first = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-busy-first"},
        )
        second = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-busy-second"},
        )
        assert first.status_code == 202
        assert second.status_code == 409
        assert second.json() == {
            "error": {
                "code": "session_busy",
                "run_id": first.json()["run_id"],
            },
            "detail": {
                "code": "session_busy",
                "run_id": first.json()["run_id"],
            },
            "code": 409,
            "degraded": False,
        }
    finally:
        facade.drop_session(sid)


def test_direction_queue_full_returns_retry_after(client, monkeypatch):
    sid = "test-run-queue-full-contract"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})

    async def queue_full(*_args, **_kwargs):
        raise QueueFull("run queue is full")

    monkeypatch.setattr(RunRepository, "enqueue", queue_full)
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-queue-full"},
        )
        assert response.status_code == 429
        assert response.headers["Retry-After"] == "5"
        assert response.json() == {
            "error": "run queue is full",
            "detail": "run queue is full",
            "code": 429,
            "degraded": False,
        }
    finally:
        facade.drop_session(sid)


def test_queue_capacity_rejects_before_creating_work():
    sid = "test-run-queue-full"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})

    async def scenario():
        with pytest.raises(QueueFull):
            await RunRepository(queue_capacity=0).enqueue(
                session_id=sid,
                kind="prewrite",
                payload=_direction(),
                idempotency_key="queue-full-1",
            )

    try:
        asyncio.run(scenario())
    finally:
        facade.drop_session(sid)


def test_upload_admission_is_atomic_and_idempotent():
    async def scenario():
        repo = RunRepository()
        fingerprint = upload_fingerprint(b"x,y\n1,2\n", "sample.csv")
        values = {
            "user_id": 7,
            "csv_path": "/tmp/admitted.csv",
            "dataset_meta": {"columns": ["x", "y"], "rows": 1},
            "initial_state": {"upload_readiness": "PROCESSING"},
            "idempotency_key": "upload-admission-atomic-1",
            "input_fingerprint": fingerprint,
        }
        first = await repo.admit_upload(session_id="upload-admission-a", **values)
        second = await repo.admit_upload(session_id="upload-admission-b", **values)

        assert first.replayed is False
        assert second.replayed is True
        assert second.session.session_id == first.session.session_id
        assert second.run.run_id == first.run.run_id
        assert first.session.csv_path == "/tmp/admitted.csv"
        assert first.session.state["upload_readiness"] == "PROCESSING"
        events = await repo.events_after(first.run.run_id, 0)
        assert [(event.seq, event.event_type) for event in events] == [
            (1, "run.accepted")
        ]

        async with repo._factory() as db:
            assert await db.scalar(
                select(func.count()).select_from(ResearchSession).where(
                    ResearchSession.session_id.in_(
                        ("upload-admission-a", "upload-admission-b")
                    )
                )
            ) == 1
            assert await db.scalar(
                select(func.count()).select_from(Run).where(
                    Run.idempotency_key == "upload-admission-atomic-1"
                )
            ) == 1

        await repo.purge_session(first.session.session_id)
        async with repo._factory() as db:
            async with db.begin():
                row = await db.get(ResearchSession, first.session.session_id)
                if row is not None:
                    await db.delete(row)

    asyncio.run(scenario())


def test_upload_fingerprint_binds_bytes_and_normalized_leaf_filename():
    baseline = upload_fingerprint(b"x\n1\n", " Sample.CSV ")
    assert baseline == upload_fingerprint(b"x\n1\n", r"folder\sample.csv")
    assert baseline != upload_fingerprint(b"x\n2\n", "sample.csv")
    assert baseline != upload_fingerprint(b"x\n1\n", "other.csv")


def test_upload_admission_key_conflict_does_not_disclose_existing_ids():
    async def scenario():
        repo = RunRepository()
        first = await repo.admit_upload(
            session_id="upload-conflict-owner",
            user_id=11,
            csv_path="/tmp/owner.csv",
            dataset_meta={"columns": ["x"], "rows": 1},
            initial_state={"upload_readiness": "PROCESSING"},
            idempotency_key="upload-conflict-global-key",
            input_fingerprint=upload_fingerprint(b"x\n1\n", "owner.csv"),
        )
        try:
            with pytest.raises(IdempotencyConflict) as wrong_file:
                await repo.admit_upload(
                    session_id="upload-conflict-file",
                    user_id=11,
                    csv_path="/tmp/other.csv",
                    dataset_meta={"columns": ["x"], "rows": 1},
                    initial_state={"upload_readiness": "PROCESSING"},
                    idempotency_key="upload-conflict-global-key",
                    input_fingerprint=upload_fingerprint(b"x\n2\n", "owner.csv"),
                )
            with pytest.raises(IdempotencyConflict) as wrong_owner:
                await repo.admit_upload(
                    session_id="upload-conflict-other-owner",
                    user_id=12,
                    csv_path="/tmp/other-owner.csv",
                    dataset_meta={"columns": ["x"], "rows": 1},
                    initial_state={"upload_readiness": "PROCESSING"},
                    idempotency_key="upload-conflict-global-key",
                    input_fingerprint=upload_fingerprint(b"x\n1\n", "owner.csv"),
                )
            for caught in (wrong_file.value, wrong_owner.value):
                assert first.session.session_id not in str(caught)
                assert first.run.run_id not in str(caught)
            assert not facade.has_session("upload-conflict-file")
            assert not facade.has_session("upload-conflict-other-owner")
        finally:
            await repo.purge_session(first.session.session_id)
            facade.drop_session(first.session.session_id)

    asyncio.run(scenario())


def test_concurrent_upload_admission_creates_one_session_run_and_event(tmp_path):
    async def scenario():
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'concurrent-upload-admission.db'}"
        )
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            first_repo = RunRepository()
            second_repo = RunRepository()
            first_repo._factory = factory
            second_repo._factory = factory
            values = {
                "user_id": 21,
                "csv_path": "/tmp/concurrent.csv",
                "dataset_meta": {"columns": ["x"], "rows": 1},
                "initial_state": {"upload_readiness": "PROCESSING"},
                "idempotency_key": "concurrent-upload-key",
                "input_fingerprint": upload_fingerprint(
                    b"x\n1\n", "concurrent.csv"
                ),
            }
            first, second = await asyncio.gather(
                first_repo.admit_upload(session_id="concurrent-upload-a", **values),
                second_repo.admit_upload(session_id="concurrent-upload-b", **values),
            )
            assert {first.replayed, second.replayed} == {False, True}
            assert first.session.session_id == second.session.session_id
            assert first.run.run_id == second.run.run_id
            async with factory() as db:
                assert await db.scalar(
                    select(func.count()).select_from(ResearchSession)
                ) == 1
                assert await db.scalar(select(func.count()).select_from(Run)) == 1
                assert await db.scalar(
                    select(func.count()).select_from(RunEvent)
                ) == 1
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_upload_admission_capacity_and_event_failure_leave_no_rows(
    tmp_path, monkeypatch
):
    async def scenario():
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'failed-upload-admission.db'}"
        )
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            common = {
                "user_id": None,
                "csv_path": "/tmp/rejected.csv",
                "dataset_meta": {"columns": ["x"], "rows": 1},
                "initial_state": {},
                "input_fingerprint": upload_fingerprint(b"x\n1\n", "rejected.csv"),
            }
            full_repo = RunRepository(queue_capacity=0)
            full_repo._factory = factory
            with pytest.raises(QueueFull):
                await full_repo.admit_upload(
                    session_id="queue-full-upload",
                    idempotency_key="queue-full-upload-key",
                    **common,
                )

            failing_repo = RunRepository()
            failing_repo._factory = factory

            async def fail_event(*_args, **_kwargs):
                raise RuntimeError("accepted event write failed")

            monkeypatch.setattr(failing_repo, "_append_locked", fail_event)
            with pytest.raises(RuntimeError, match="accepted event write failed"):
                await failing_repo.admit_upload(
                    session_id="event-failed-upload",
                    idempotency_key="event-failed-upload-key",
                    **common,
                )

            async with factory() as db:
                assert await db.scalar(
                    select(func.count()).select_from(ResearchSession)
                ) == 0
                assert await db.scalar(select(func.count()).select_from(Run)) == 0
                assert await db.scalar(
                    select(func.count()).select_from(RunEvent)
                ) == 0
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_fresh_schema_accepts_supported_run_kinds_and_rejects_unknown(tmp_path):
    async def scenario():
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'fresh-run-kinds.db'}"
        )
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            async with factory.begin() as db:
                db.add_all(
                    [
                        ResearchSession(session_id="fresh-prewrite"),
                        ResearchSession(session_id="fresh-upload"),
                        ResearchSession(session_id="fresh-unknown"),
                    ]
                )
                db.add_all(
                    [
                        Run(
                            run_id="fresh-prewrite-run",
                            session_id="fresh-prewrite",
                            kind="prewrite",
                            payload={},
                        ),
                        Run(
                            run_id="fresh-upload-run",
                            session_id="fresh-upload",
                            kind="upload_pipeline",
                            payload={},
                        ),
                    ]
                )
            async with factory() as db:
                async with db.begin():
                    db.add(
                        Run(
                            run_id="fresh-unknown-run",
                            session_id="fresh-unknown",
                            kind="unknown",
                            payload={},
                        )
                    )
                    with pytest.raises(IntegrityError):
                        await db.flush()
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_enqueue_rejects_a_deleted_session_without_creating_an_orphan():
    sid = "test-run-admission-after-delete"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    facade.drop_session(sid)

    async def scenario():
        repo = RunRepository()
        with pytest.raises(SessionNotFound, match=f"session {sid} no longer exists"):
            await repo.enqueue(
                session_id=sid,
                kind="prewrite",
                payload=_direction(),
                idempotency_key="admission-after-delete-1",
            )

    asyncio.run(scenario())


def test_atomic_session_delete_cascades_runs_and_events():
    sid = "test-run-session-cascade"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})

    async def scenario():
        repo = RunRepository()
        run = await repo.enqueue(
            session_id=sid,
            kind="prewrite",
            payload=_direction(),
            idempotency_key="session-cascade-1",
        )
        assert await repo.events_after(run.run_id, 0)

        assert await asyncio.to_thread(facade.delete_session, sid) is True
        assert await repo.get(run.run_id) is None
        assert await repo.events_after(run.run_id, 0) == []

    asyncio.run(scenario())


def test_concurrent_admission_and_delete_leave_no_orphan():
    sid = "test-run-session-delete-interleaving"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})

    async def scenario():
        admission_repo = RunRepository()
        start = asyncio.Event()

        async def admit():
            await start.wait()
            try:
                return await admission_repo.enqueue(
                    session_id=sid,
                    kind="prewrite",
                    payload=_direction(),
                    idempotency_key="session-delete-interleaving-1",
                )
            except SessionNotFound:
                return None

        async def delete_session():
            await start.wait()
            return await asyncio.to_thread(facade.delete_session, sid)

        admission = asyncio.create_task(admit())
        deletion = asyncio.create_task(delete_session())
        start.set()
        run, deleted = await asyncio.gather(admission, deletion)

        assert deleted is True
        if run is not None:
            assert await admission_repo.get(run.run_id) is None

    asyncio.run(scenario())


def test_cross_process_admission_and_delete_leave_no_orphan(tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    database_path = tmp_path / "cross-process.db"
    state_root = tmp_path / "state"
    sid = "test-run-cross-process-delete"
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": f"sqlite+aiosqlite:///{database_path}",
            "ECONPAPER_LOCAL_STATE_ROOT": str(state_root),
            "SESSIONS_PATH": str(state_root / "sessions" / "sessions.json"),
            "RUNS_DIR": str(state_root / "runs"),
            "DEBUG": "true",
            "JWT_SECRET_KEY": "test-only-jwt-secret-key-32chars-min",
            "PYTHONPATH": os.pathsep.join(
                [
                    str(repo_root),
                    str(repo_root / "backend"),
                    str(repo_root / "agent"),
                    env.get("PYTHONPATH", ""),
                ]
            ),
        }
    )
    setup = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import asyncio; "
                "from database import create_tables; "
                "from facade import facade; "
                "asyncio.run(create_tables()); "
                f"facade.seed_state({sid!r}, {{'csv_path': '/tmp/input.csv'}})"
            ),
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert setup.returncode == 0, setup.stderr

    start = tmp_path / "start"
    worker = """
import asyncio
import sys
import time
from pathlib import Path

from facade import facade
from run_repository import RunRepository, SessionNotFound

action, session_id, start_path = sys.argv[1:4]
while not Path(start_path).exists():
    time.sleep(0.005)

if action == "delete":
    print("deleted" if facade.delete_session(session_id) else "missing")
else:
    async def admit():
        try:
            run = await RunRepository().enqueue(
                session_id=session_id,
                kind="prewrite",
                payload={"research_direction": {}, "initial_state": {}},
                idempotency_key="cross-process-1",
            )
        except SessionNotFound:
            print("rejected")
        else:
            print(f"accepted:{run.run_id}")

    asyncio.run(admit())
"""
    admission = subprocess.Popen(
        [sys.executable, "-c", worker, "admit", sid, str(start)],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deletion = subprocess.Popen(
        [sys.executable, "-c", worker, "delete", sid, str(start)],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    start.write_text("go", encoding="utf-8")
    admission_out, admission_err = admission.communicate(timeout=20)
    deletion_out, deletion_err = deletion.communicate(timeout=20)

    assert admission.returncode == 0, admission_err
    assert deletion.returncode == 0, deletion_err
    assert "deleted" in deletion_out
    assert "accepted:" in admission_out or "rejected" in admission_out
    with sqlite3.connect(database_path) as db:
        assert db.execute("SELECT count(*) FROM research_sessions").fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM runs").fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM run_events").fetchone() == (0,)


async def _create_legacy_run_schema(conn, *, constrained: bool) -> None:
    check = ", CHECK (kind = 'prewrite')" if constrained else ""
    await conn.execute(
        text("CREATE TABLE research_sessions (session_id VARCHAR(64) PRIMARY KEY)")
    )
    await conn.execute(
        text(
            "CREATE TABLE runs ("
            "run_id VARCHAR(36) PRIMARY KEY, session_id VARCHAR(64) NOT NULL, "
            "kind VARCHAR(64) NOT NULL, status VARCHAR(24) NOT NULL, "
            "payload JSON NOT NULL, result JSON, error TEXT, "
            "idempotency_key VARCHAR(200), attempt INTEGER NOT NULL DEFAULT 0, "
            "lease_owner VARCHAR(200), lease_expires_at DATETIME, "
            "lease_epoch INTEGER NOT NULL DEFAULT 0, "
            "next_event_seq INTEGER NOT NULL DEFAULT 0, "
            "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "
            f"updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP{check})"
        )
    )
    await conn.execute(
        text(
            "CREATE TABLE run_events ("
            "run_id VARCHAR(36) NOT NULL, seq INTEGER NOT NULL, "
            "event_type VARCHAR(80) NOT NULL, payload JSON NOT NULL, "
            "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "
            "PRIMARY KEY (run_id, seq))"
        )
    )
    await conn.execute(text("CREATE INDEX ix_legacy_runs_error ON runs(error)"))
    await conn.execute(
        text(
            "CREATE TRIGGER trg_sessions_delete_runs "
            "AFTER DELETE ON research_sessions FOR EACH ROW "
            "BEGIN DELETE FROM runs WHERE session_id = OLD.session_id; END"
        )
    )


@pytest.mark.parametrize("constrained", [True, False])
def test_legacy_sqlite_run_schema_upgrade_preserves_events_and_constraints(
    tmp_path, constrained
):
    async def scenario():
        database_path = tmp_path / f"legacy-run-schema-{constrained}.db"
        engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
        try:
            async with engine.begin() as conn:
                await _create_legacy_run_schema(conn, constrained=constrained)
                await conn.execute(
                    text("INSERT INTO research_sessions VALUES ('legacy-session')")
                )
                await conn.execute(
                    text("INSERT INTO research_sessions VALUES ('upload-session')")
                )
                await conn.execute(
                    text(
                        "INSERT INTO runs "
                        "(run_id, session_id, kind, status, payload, "
                        "idempotency_key, next_event_seq) VALUES "
                        "('legacy-run', 'legacy-session', 'prewrite', "
                        "'SUCCEEDED', '{}', 'legacy-key', 1)"
                    )
                )
                await conn.execute(
                    text(
                        "INSERT INTO run_events "
                        "(run_id, seq, event_type, payload) VALUES "
                        "('legacy-run', 1, 'run.succeeded', '{\"kept\": true}')"
                    )
                )
                await _ensure_run_lifecycle_constraints(conn)

            async with engine.begin() as conn:
                assert await conn.scalar(text("SELECT count(*) FROM runs")) == 1
                assert await conn.scalar(text("SELECT count(*) FROM run_events")) == 1
                assert await conn.scalar(
                    text(
                        "SELECT count(*) FROM data_migrations "
                        "WHERE name='run-upload-pipeline-v1'"
                    )
                ) == 1
                assert await conn.scalar(
                    text("SELECT event_type FROM run_events WHERE run_id='legacy-run'")
                ) == "run.succeeded"
                indexes = {
                    str(row[1])
                    for row in await conn.execute(text("PRAGMA index_list(runs)"))
                }
                assert {
                    "ix_legacy_runs_error",
                    "uq_runs_session_active",
                    "uq_runs_upload_idempotency",
                }.issubset(indexes)
                await conn.execute(
                    text(
                        "INSERT INTO runs "
                        "(run_id, session_id, kind, status, payload, "
                        "idempotency_key, attempt, lease_epoch, next_event_seq, "
                        "created_at, updated_at) VALUES "
                        "('upload-run', 'upload-session', 'upload_pipeline', "
                        "'PENDING', '{}', 'upload-global-key', 0, 0, 0, "
                        "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                    )
                )

            async with engine.connect() as conn:
                transaction = await conn.begin()
                with pytest.raises(IntegrityError):
                    await conn.execute(
                        text(
                            "INSERT INTO runs "
                            "(run_id, session_id, kind, status, payload, attempt, "
                            "lease_epoch, next_event_seq, created_at, updated_at) "
                            "VALUES ('unknown-run', 'legacy-session', 'unknown', "
                            "'FAILED', '{}', 0, 0, 0, CURRENT_TIMESTAMP, "
                            "CURRENT_TIMESTAMP)"
                        )
                    )
                await transaction.rollback()

            # Repeating the migration is an idempotent no-op.
            async with engine.begin() as conn:
                await _ensure_run_lifecycle_constraints(conn)
                assert await conn.scalar(text("SELECT count(*) FROM runs")) == 2
                assert await conn.scalar(text("SELECT count(*) FROM run_events")) == 1
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_concurrent_sqlite_run_schema_upgrade_is_safe(tmp_path):
    async def scenario():
        database_path = tmp_path / "concurrent-run-schema.db"
        setup_engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
        async with setup_engine.begin() as conn:
            await _create_legacy_run_schema(conn, constrained=True)
            await conn.execute(
                text("INSERT INTO research_sessions VALUES ('legacy-session')")
            )
            await conn.execute(
                text(
                    "INSERT INTO runs "
                    "(run_id, session_id, kind, status, payload, next_event_seq) "
                    "VALUES ('legacy-run', 'legacy-session', 'prewrite', "
                    "'SUCCEEDED', '{}', 1)"
                )
            )
            await conn.execute(
                text(
                    "INSERT INTO run_events (run_id, seq, event_type, payload) "
                    "VALUES ('legacy-run', 1, 'legacy.event', '{}')"
                )
            )
        await setup_engine.dispose()

        engines = [
            create_async_engine(f"sqlite+aiosqlite:///{database_path}")
            for _ in range(2)
        ]

        async def migrate(engine):
            async with engine.begin() as conn:
                await _ensure_run_lifecycle_constraints(conn)

        try:
            await asyncio.gather(*(migrate(engine) for engine in engines))
            async with engines[0].connect() as conn:
                assert await conn.scalar(text("SELECT count(*) FROM runs")) == 1
                assert await conn.scalar(text("SELECT count(*) FROM run_events")) == 1
                assert "upload_pipeline" in str(
                    await conn.scalar(
                        text(
                            "SELECT sql FROM sqlite_master "
                            "WHERE type='table' AND name='runs'"
                        )
                    )
                )
        finally:
            await asyncio.gather(*(engine.dispose() for engine in engines))

    asyncio.run(scenario())


def test_sqlite_run_schema_conflict_rolls_back_without_data_loss(tmp_path):
    async def scenario():
        database_path = tmp_path / "conflicting-run-schema.db"
        engine = create_async_engine(f"sqlite+aiosqlite:///{database_path}")
        try:
            async with engine.begin() as conn:
                await _create_legacy_run_schema(conn, constrained=False)
                await conn.execute(
                    text("INSERT INTO research_sessions VALUES ('conflict-session')")
                )
                for run_id in ("conflict-run-a", "conflict-run-b"):
                    await conn.execute(
                        text(
                            "INSERT INTO runs "
                            "(run_id, session_id, kind, status, payload) VALUES "
                            f"('{run_id}', 'conflict-session', 'prewrite', "
                            "'PENDING', '{}')"
                        )
                    )

            with pytest.raises(RuntimeError, match="historical uniqueness conflicts"):
                async with engine.begin() as conn:
                    await _ensure_run_lifecycle_constraints(conn)

            async with engine.connect() as conn:
                assert await conn.scalar(text("SELECT count(*) FROM runs")) == 2
                run_sql = str(
                    await conn.scalar(
                        text(
                            "SELECT sql FROM sqlite_master "
                            "WHERE type='table' AND name='runs'"
                        )
                    )
                )
                assert "upload_pipeline" not in run_sql
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_legacy_sqlite_lifecycle_triggers_enforce_parents_and_cascade(tmp_path):
    async def scenario():
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'legacy-lifecycle.db'}"
        )
        try:
            async with engine.begin() as conn:
                await conn.execute(
                    text(
                        "CREATE TABLE research_sessions "
                        "(session_id VARCHAR(64) PRIMARY KEY)"
                    )
                )
                await conn.execute(
                    text(
                        "CREATE TABLE runs "
                        "(run_id VARCHAR(36) PRIMARY KEY, "
                        "session_id VARCHAR(64) NOT NULL)"
                    )
                )
                await conn.execute(
                    text(
                        "CREATE TABLE run_events "
                        "(run_id VARCHAR(36), seq INTEGER, "
                        "PRIMARY KEY (run_id, seq))"
                    )
                )
                await _ensure_run_lifecycle_constraints(conn)
                await conn.execute(
                    text("INSERT INTO research_sessions VALUES ('session-1')")
                )
                await conn.execute(
                    text(
                        "INSERT INTO runs "
                        "(run_id, session_id, kind, status, payload, attempt, "
                        "lease_epoch, next_event_seq, created_at, updated_at) "
                        "VALUES ('run-1', 'session-1', 'prewrite', 'PENDING', "
                        "'{}', 0, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                    )
                )
                await conn.execute(
                    text(
                        "INSERT INTO run_events "
                        "(run_id, seq, event_type, payload, created_at) "
                        "VALUES ('run-1', 1, 'legacy.event', '{}', CURRENT_TIMESTAMP)"
                    )
                )

            async with engine.connect() as conn:
                transaction = await conn.begin()
                with pytest.raises(IntegrityError):
                    await conn.execute(
                        text(
                            "INSERT INTO runs "
                            "(run_id, session_id, kind, status, payload, attempt, "
                            "lease_epoch, next_event_seq, created_at, updated_at) "
                            "VALUES ('orphan-run', 'missing-session', 'prewrite', "
                            "'PENDING', '{}', 0, 0, 0, CURRENT_TIMESTAMP, "
                            "CURRENT_TIMESTAMP)"
                        )
                    )
                await transaction.rollback()

            async with engine.connect() as conn:
                transaction = await conn.begin()
                with pytest.raises(IntegrityError):
                    await conn.execute(
                        text(
                            "INSERT INTO run_events "
                            "(run_id, seq, event_type, payload, created_at) "
                            "VALUES ('missing-run', 2, 'legacy.event', '{}', "
                            "CURRENT_TIMESTAMP)"
                        )
                    )
                await transaction.rollback()

            async with engine.connect() as conn:
                transaction = await conn.begin()
                with pytest.raises(IntegrityError):
                    await conn.execute(
                        text(
                            "UPDATE run_events SET run_id = 'missing-run' "
                            "WHERE run_id = 'run-1'"
                        )
                    )
                await transaction.rollback()

            async with engine.begin() as conn:
                await conn.execute(
                    text(
                        "DELETE FROM research_sessions "
                        "WHERE session_id = 'session-1'"
                    )
                )
                assert await conn.scalar(text("SELECT count(*) FROM runs")) == 0
                assert (
                    await conn.scalar(text("SELECT count(*) FROM run_events"))
                    == 0
                )
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_claim_skips_a_legacy_orphan_run(tmp_path):
    async def scenario():
        engine = create_async_engine(
            f"sqlite+aiosqlite:///{tmp_path / 'legacy-orphan-claim.db'}"
        )
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            # This standalone legacy engine deliberately leaves SQLite foreign
            # key enforcement off, reproducing a pre-upgrade orphan row.
            async with factory.begin() as db:
                db.add(
                    Run(
                        run_id="legacy-orphan-run",
                        session_id="missing-session",
                        kind="prewrite",
                        status="PENDING",
                        payload={
                            "research_direction": _direction(),
                            "initial_state": {},
                        },
                    )
                )

            repo = RunRepository()
            repo._factory = factory
            assert (
                await repo.claim(
                    "legacy-orphan-run", "legacy-worker", lease_seconds=60
                )
                is None
            )
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_upload_runner_atomically_publishes_readable_result_and_degradation(
    tmp_path, monkeypatch
):
    from config import settings

    sid = "test-upload-runner-success"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    source = upload_dir / f"{sid}.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    monkeypatch.setattr(settings, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    _use_upload_child_executor(monkeypatch, write_upload_result)
    admission = asyncio.run(_admit_upload(session_id=sid, csv_path=source))

    try:
        assert asyncio.run(
            process_one_run(owner="upload-success", run_id=admission.run.run_id)
        ) is True
        durable = asyncio.run(RunRepository().get(admission.run.run_id))
        assert durable is not None
        assert durable.status == "SUCCEEDED"
        assert durable.error is None
        assert durable.result["cleaning_report"]["steps"][0]["status"] == "failed"

        entry = facade.get_session_entry(sid)
        expected_workspace = (
            tmp_path
            / "runs"
            / sid
            / "attempts"
            / admission.run.run_id
            / "epoch-1"
        )
        assert entry["state"]["upload_readiness"] == "READY"
        assert Path(entry["csv_path"]) == expected_workspace / "cleaned.csv"
        assert Path(entry["csv_path"]).read_text(encoding="utf-8") == "x,y\n1,2\n"
    finally:
        facade.delete_session(sid)


@pytest.mark.parametrize(
    ("executor", "expected_error"),
    [
        (
            fail_upload_with_sensitive_text,
            "RuntimeError: upload_pipeline executor failed",
        ),
        (
            return_unreadable_upload_result,
            "UnreadableOutput: upload_pipeline output_validation failed",
        ),
    ],
)
def test_upload_runner_marks_fatal_or_unreadable_result_failed(
    tmp_path, monkeypatch, executor, expected_error
):
    from config import settings

    sid = f"test-upload-runner-failed-{executor.__name__}"
    source = tmp_path / f"{sid}.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    _use_upload_child_executor(monkeypatch, executor)
    admission = asyncio.run(_admit_upload(session_id=sid, csv_path=source))

    try:
        assert asyncio.run(
            process_one_run(owner="upload-failure", run_id=admission.run.run_id)
        ) is True
        durable = asyncio.run(RunRepository().get(admission.run.run_id))
        assert durable is not None
        assert durable.status == "FAILED"
        assert durable.error == expected_error
        assert "secret-token" not in durable.error
        assert "/private/" not in durable.error
        assert facade.get_state(sid)["upload_readiness"] == "FAILED"
    finally:
        facade.delete_session(sid)


def test_reclaimed_upload_runner_fences_stale_progress_result_and_readiness(
    tmp_path,
):
    sid = "test-upload-runner-reclaim"
    source = tmp_path / "source.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    cleaned = tmp_path / "cleaned.csv"
    cleaned.write_text("x,y\n1,2\n", encoding="utf-8")
    admission = asyncio.run(_admit_upload(session_id=sid, csv_path=source))

    async def scenario():
        repo = RunRepository()
        stale = await repo.claim(
            admission.run.run_id, "upload-stale", lease_seconds=-1
        )
        fresh = await repo.claim(
            admission.run.run_id, "upload-fresh", lease_seconds=60
        )
        assert stale is not None and fresh is not None
        assert fresh.lease_epoch == stale.lease_epoch + 1
        with pytest.raises(LeaseLost):
            await repo.append_worker_event(
                admission.run.run_id,
                "run.progress",
                {"node": "clean_data", "status": "completed"},
                owner="upload-stale",
                lease_epoch=stale.lease_epoch,
            )
        with pytest.raises(LeaseLost):
            await repo.complete(
                admission.run.run_id,
                owner="upload-stale",
                lease_epoch=stale.lease_epoch,
                result={"csv_path": str(tmp_path / "stale.csv")},
            )
        with pytest.raises(LeaseLost):
            await repo.fail(
                admission.run.run_id,
                owner="upload-stale",
                lease_epoch=stale.lease_epoch,
                error="stale failure",
            )
        assert facade.get_state(sid)["upload_readiness"] == "PROCESSING"
        await repo.complete(
            admission.run.run_id,
            owner="upload-fresh",
            lease_epoch=fresh.lease_epoch,
            result={"csv_path": str(cleaned), "cleaning_report": {"steps": []}},
        )

    try:
        asyncio.run(scenario())
        entry = facade.get_session_entry(sid)
        assert entry["state"]["upload_readiness"] == "READY"
        assert entry["csv_path"] == str(cleaned)
    finally:
        facade.delete_session(sid)


def test_upload_runner_reclaims_expired_attempt_into_a_new_epoch_workspace(
    tmp_path, monkeypatch
):
    from config import settings

    sid = "test-upload-runner-restart"
    source = tmp_path / "source.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    _use_upload_child_executor(monkeypatch, write_upload_result)
    admission = asyncio.run(_admit_upload(session_id=sid, csv_path=source))

    async def expire_first_attempt():
        claimed = await RunRepository().claim(
            admission.run.run_id,
            "runner-that-exited",
            lease_seconds=-1,
        )
        assert claimed is not None
        assert claimed.lease_epoch == 1

    try:
        asyncio.run(expire_first_attempt())
        assert asyncio.run(
            process_one_run(owner="replacement-runner", run_id=admission.run.run_id)
        ) is True
        durable = asyncio.run(RunRepository().get(admission.run.run_id))
        assert durable is not None
        assert durable.status == "SUCCEEDED"
        assert durable.attempt == 2
        assert durable.lease_epoch == 2
        expected_workspace = (
            tmp_path
            / "runs"
            / sid
            / "attempts"
            / admission.run.run_id
            / "epoch-2"
        )
        assert facade.get_session_entry(sid)["csv_path"] == str(
            expected_workspace / "cleaned.csv"
        )
    finally:
        facade.delete_session(sid)


def test_upload_terminal_commit_outage_leaves_run_reclaimable(tmp_path, monkeypatch):
    from config import settings

    sid = "test-upload-terminal-commit-outage"
    source = tmp_path / "source.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    _use_upload_child_executor(monkeypatch, write_upload_result)
    admission = asyncio.run(_admit_upload(session_id=sid, csv_path=source))
    completion_attempts = 0
    failure_called = False

    async def completion_outage(*_args, **_kwargs):
        nonlocal completion_attempts
        completion_attempts += 1
        raise RuntimeError("database unavailable")

    async def must_not_fail(*_args, **_kwargs):
        nonlocal failure_called
        failure_called = True

    monkeypatch.setattr(RunRepository, "complete", completion_outage)
    monkeypatch.setattr(RunRepository, "fail", must_not_fail)
    try:
        assert asyncio.run(
            process_one_run(owner="upload-outage", run_id=admission.run.run_id)
        ) is True
        assert completion_attempts == 3
        assert failure_called is False
        durable = asyncio.run(RunRepository().get(admission.run.run_id))
        assert durable is not None
        assert durable.status == "RUNNING"
        assert facade.get_state(sid)["upload_readiness"] == "PROCESSING"
    finally:
        monkeypatch.undo()
        facade.delete_session(sid)


def test_delete_session_cancels_upload_tree_and_cleans_only_owned_artifacts(
    tmp_path, monkeypatch
):
    from config import settings
    from run_store import run_dir
    from storage.s3 import s3_fs

    sid = "test-upload-delete-running"
    other_sid = "test-upload-delete-other"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    cache_dir = tmp_path / "s3-cache"
    cache_dir.mkdir()
    source = upload_dir / f"{sid}.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    other_source = upload_dir / f"{other_sid}.csv"
    other_source.write_text("x,y\n9,9\n", encoding="utf-8")
    cached_source = cache_dir / f"{sid}.csv"
    cached_source.write_text("x,y\n1,2\n", encoding="utf-8")
    other_cached_source = cache_dir / f"{other_sid}.csv"
    other_cached_source.write_text("x,y\n9,9\n", encoding="utf-8")
    started = tmp_path / "upload-started"
    descendant_finished = tmp_path / "descendant-finished"
    monkeypatch.setattr(settings, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(settings, "S3_CACHE_DIR", cache_dir)
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setattr(settings, "S3_ENDPOINT_URL", "http://configured-s3")
    deleted_remote: list[str] = []
    monkeypatch.setattr(
        s3_fs,
        "delete",
        lambda remote_path: deleted_remote.append(remote_path) or True,
    )
    _use_upload_child_executor(monkeypatch, blocking_upload_with_descendant)
    admission = asyncio.run(
        _admit_upload(
            session_id=sid,
            csv_path=source,
            initial_state={
                "_test_started_path": str(started),
                "_test_finished_path": str(descendant_finished),
            },
        )
    )
    other_run_dir = run_dir(other_sid)
    other_run_dir.mkdir(parents=True)
    (other_run_dir / "keep.txt").write_text("keep", encoding="utf-8")

    async def scenario():
        worker = asyncio.create_task(
            process_one_run(owner="upload-delete", run_id=admission.run.run_id)
        )
        assert await asyncio.to_thread(_wait_for_path, started, timeout=2)
        cancellation_started = time.monotonic()
        assert await asyncio.to_thread(facade.delete_session, sid) is True
        await asyncio.wait_for(worker, timeout=1)
        assert time.monotonic() - cancellation_started < 1

    try:
        asyncio.run(scenario())
        time.sleep(1.8)
        assert not descendant_finished.exists()
        assert not source.exists()
        assert not cached_source.exists()
        assert not run_dir(sid).exists()
        assert other_source.exists()
        assert other_cached_source.exists()
        assert (other_run_dir / "keep.txt").exists()
        assert deleted_remote == [f"{sid}/data.csv"]
        assert asyncio.run(RunRepository().get(admission.run.run_id)) is None
    finally:
        facade.delete_session(sid)
        shutil.rmtree(other_run_dir, ignore_errors=True)


def test_upload_runner_removes_attempt_recreated_after_session_revocation(
    tmp_path, monkeypatch
):
    import runner as runner_module
    from config import settings
    from run_store import run_dir

    sid = "test-upload-delete-before-workspace"
    source = tmp_path / "source.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    _use_upload_child_executor(monkeypatch, write_upload_result)
    admission = asyncio.run(_admit_upload(session_id=sid, csv_path=source))
    real_workspace = runner_module._upload_attempt_workspace

    def revoke_then_create(session_id: str, run_id: str, lease_epoch: int) -> str:
        assert facade.delete_session(session_id) is True
        return real_workspace(session_id, run_id, lease_epoch)

    monkeypatch.setattr(
        runner_module,
        "_upload_attempt_workspace",
        revoke_then_create,
    )

    assert asyncio.run(
        process_one_run(owner="revoked-before-workspace", run_id=admission.run.run_id)
    ) is True
    assert not run_dir(sid).exists()
    assert asyncio.run(RunRepository().get(admission.run.run_id)) is None


def test_upload_runner_removes_attempt_after_business_failure(tmp_path, monkeypatch):
    import runner as runner_module
    from config import settings
    from run_store import run_dir

    sid = "test-upload-failed-attempt-cleanup"
    source = tmp_path / "source.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))

    def fail_after_partial_output(_session_id, initial_state, **_kwargs):
        workspace = Path(initial_state["workspace"])
        (workspace / "partial.csv").write_text("partial", encoding="utf-8")
        raise ValueError("invalid row")

    monkeypatch.setattr(
        runner_module,
        "execute_upload_supervised",
        fail_after_partial_output,
    )
    admission = asyncio.run(_admit_upload(session_id=sid, csv_path=source))

    assert asyncio.run(
        process_one_run(owner="failed-upload", run_id=admission.run.run_id)
    ) is True
    terminal = asyncio.run(RunRepository().get(admission.run.run_id))
    assert terminal is not None
    assert terminal.status == "FAILED"
    assert not (run_dir(sid) / "attempts").exists()

    facade.delete_session(sid)


def test_runner_completion_persists_session_before_status_read(client, monkeypatch):
    sid = "test-run-completes"
    completed_state = {
        "csv_path": "/tmp/input.csv",
        "research_direction": _direction(),
        "claim": "association",
        "outline": [{"type": "intro", "title": "引言"}],
    }
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/input.csv",
            "_test_child_result": completed_state,
        },
    )
    _use_child_executor(monkeypatch, return_requested_state)
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-complete-1"},
        )
        run_id = accepted.json()["run_id"]

        # This edit lands after admission and must survive the worker's merge.
        facade.update_state(
            sid,
            body_chapters=[{"type": "methods", "content": "edited while running"}],
        )
        assert asyncio.run(
            process_one_run(
                owner="test-runner",
                run_id=run_id,
            )
        ) is True

        persisted = facade.get_state(sid)
        assert persisted["claim"] == "association"
        assert persisted["body_chapters"][0]["content"] == "edited while running"

        monkeypatch.setattr(
            facade,
            "save_state",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                AssertionError("GET /runs must be read-only")
            ),
        )

        status = client.get(f"/runs/{run_id}")
        assert status.status_code == 200, status.text
        assert status.json()["status"] == "SUCCEEDED"
        assert status.json()["result"]["outline"][0]["type"] == "intro"
        assert client.get(f"/runs/{run_id}").status_code == 200

        session = client.get(f"/sessions/{sid}")
        assert session.status_code == 200, session.text
        assert session.json()["claim"] == "association"
        assert session.json()["body_chapters"][0]["content"] == "edited while running"
    finally:
        facade.drop_session(sid)


def test_runner_completion_preserves_concurrent_same_field_edit(client, monkeypatch):
    sid = "test-run-same-field-conflict"
    initial_outline = [{"type": "intro", "title": "initial"}]
    user_outline = [{"type": "intro", "title": "edited by user"}]
    generated_outline = [{"type": "intro", "title": "generated by run"}]
    facade.seed_state(
        sid,
        {"csv_path": "/tmp/input.csv", "outline": initial_outline},
    )
    monkeypatch.setattr(
        facade,
        "execute_prewrite",
        lambda *_args, **_kwargs: {
            "csv_path": "/tmp/input.csv",
            "research_direction": _direction(),
            "outline": generated_outline,
            "claim": "association",
        },
    )
    monkeypatch.setattr(
        "runner.execute_prewrite_supervised",
        facade.execute_prewrite,
    )
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-same-field-conflict"},
        )
        run_id = accepted.json()["run_id"]
        facade.update_state(sid, outline=user_outline)

        assert asyncio.run(
            process_one_run(
                owner="same-field",
                run_id=run_id,
            )
        ) is True

        persisted = facade.get_state(sid)
        assert persisted["outline"] == user_outline
        assert persisted["claim"] == "association"
    finally:
        asyncio.run(RunRepository().purge_session(sid))
        facade.drop_session(sid)


def test_completion_transaction_rolls_back_session_and_run(client, monkeypatch):
    sid = "test-run-completion-rollback"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv", "stage": "initial"})
    accepted = client.post(
        f"/sessions/{sid}/direction",
        json=_direction(),
        headers={"Idempotency-Key": "direction-completion-rollback"},
    )
    run_id = accepted.json()["run_id"]

    async def scenario():
        repo = RunRepository()
        claimed = await repo.claim(run_id, "rollback-worker", lease_seconds=60)
        assert claimed is not None
        original_append = repo._append_locked

        async def fail_terminal_event(db, run, event_type, payload):
            if event_type == "run.succeeded":
                raise RuntimeError("terminal event write failed")
            return await original_append(db, run, event_type, payload)

        monkeypatch.setattr(repo, "_append_locked", fail_terminal_event)
        with pytest.raises(RuntimeError, match="terminal event write failed"):
            await repo.complete(
                run_id,
                owner="rollback-worker",
                lease_epoch=claimed.lease_epoch,
                result={"stage": "completed", "claim": "must-roll-back"},
            )
        durable = await repo.get(run_id)
        assert durable is not None
        assert durable.status == "RUNNING"
        assert durable.result is None
        assert all(
            event.event_type != "run.succeeded"
            for event in await repo.events_after(run_id, 0)
        )

    try:
        asyncio.run(scenario())
        assert facade.get_state(sid)["stage"] == "initial"
        assert "claim" not in facade.get_state(sid)
    finally:
        asyncio.run(RunRepository().purge_session(sid))
        facade.drop_session(sid)


def test_completion_store_outage_does_not_report_business_failure(
    client, monkeypatch
):
    sid = "test-run-completion-outage"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    monkeypatch.setattr(
        facade,
        "execute_prewrite",
        lambda *_args, **_kwargs: {"claim": "computed"},
    )
    monkeypatch.setattr(
        "runner.execute_prewrite_supervised",
        facade.execute_prewrite,
    )
    failed = False
    completion_attempts = 0

    async def completion_outage(*_args, **_kwargs):
        nonlocal completion_attempts
        completion_attempts += 1
        raise RuntimeError("database unavailable")

    async def must_not_fail(*_args, **_kwargs):
        nonlocal failed
        failed = True

    monkeypatch.setattr(RunRepository, "complete", completion_outage)
    monkeypatch.setattr(RunRepository, "fail", must_not_fail)
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-completion-outage"},
        )
        run_id = accepted.json()["run_id"]
        assert asyncio.run(
            process_one_run(
                owner="outage-worker",
                run_id=run_id,
            )
        ) is True
        assert failed is False
        assert completion_attempts == 3
        durable = asyncio.run(RunRepository().get(run_id))
        assert durable is not None
        assert durable.status == "RUNNING"
        assert durable.result is None
    finally:
        # Restore the real class methods before using purge_session.
        monkeypatch.undo()
        asyncio.run(RunRepository().purge_session(sid))
        facade.drop_session(sid)


def test_runner_failure_does_not_expose_exception_text(client, monkeypatch):
    sid = "test-run-error-redaction"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    _use_child_executor(monkeypatch, fail_with_sensitive_text)
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-redacted-error"},
        )
        run_id = accepted.json()["run_id"]
        assert asyncio.run(
            process_one_run(
                owner="redaction-test",
                run_id=run_id,
            )
        ) is True

        status = client.get(f"/runs/{run_id}")
        assert status.status_code == 200
        assert status.json()["status"] == "FAILED"
        assert status.json()["error"] == "RuntimeError: prewrite execution failed"
        assert "secret-token" not in status.text
    finally:
        facade.drop_session(sid)


def test_expired_lease_is_reclaimed_and_stale_worker_is_fenced(client):
    sid = "test-run-fencing"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-fencing-1"},
        )
        run_id = accepted.json()["run_id"]

        async def scenario():
            repo = RunRepository()
            first = await repo.claim(run_id, "runner-old", lease_seconds=-1)
            assert first and first.run_id == run_id
            second = await repo.claim(run_id, "runner-new", lease_seconds=60)
            assert second and second.run_id == run_id
            assert second.lease_epoch == first.lease_epoch + 1
            with pytest.raises(LeaseLost):
                await repo.complete(
                    run_id,
                    owner="runner-old",
                    lease_epoch=first.lease_epoch,
                    result={"stale": True},
                )
            await repo.complete(
                run_id,
                owner="runner-new",
                lease_epoch=second.lease_epoch,
                result={"fresh": True},
            )
            return await repo.get(run_id)

        durable = asyncio.run(scenario())
        assert durable is not None
        assert durable.result == {"fresh": True}
        status = client.get(f"/runs/{run_id}").json()
        assert status["status"] == "SUCCEEDED"
    finally:
        facade.drop_session(sid)


def test_expired_lease_cannot_commit_before_reclaim(client):
    sid = "test-run-expired-lease"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-expired-lease-1"},
        )
        run_id = accepted.json()["run_id"]

        async def scenario():
            repo = RunRepository()
            claimed = await repo.claim(run_id, "runner-expired", lease_seconds=-1)
            assert claimed is not None
            assert not await repo.lease_is_current(
                run_id,
                owner="runner-expired",
                lease_epoch=claimed.lease_epoch,
            )
            with pytest.raises(LeaseLost):
                await repo.complete(
                    run_id,
                    owner="runner-expired",
                    lease_epoch=claimed.lease_epoch,
                    result={"stale": True},
                )

        asyncio.run(scenario())
    finally:
        facade.drop_session(sid)


def test_completion_rolls_back_if_session_was_deleted(client):
    sid = "test-run-missing-session"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    accepted = client.post(
        f"/sessions/{sid}/direction",
        json=_direction(),
        headers={"Idempotency-Key": "direction-missing-session-1"},
    )
    run_id = accepted.json()["run_id"]

    async def scenario():
        repo = RunRepository()
        claimed = await repo.claim(run_id, "runner-missing-session", lease_seconds=60)
        assert claimed is not None
        facade.drop_session(sid)
        with pytest.raises(LeaseLost):
            await repo.complete(
                run_id,
                owner="runner-missing-session",
                lease_epoch=claimed.lease_epoch,
                result={"claim": "must-not-commit"},
            )
        durable = await repo.get(run_id)
        assert durable is None

    asyncio.run(scenario())


def test_reclaimed_worker_fences_stale_progress(client):
    sid = "test-run-progress-fencing"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-progress-fencing-1"},
        )
        run_id = accepted.json()["run_id"]

        async def scenario():
            repo = RunRepository()
            stale = await repo.claim(run_id, "runner-stale", lease_seconds=-1)
            fresh = await repo.claim(run_id, "runner-fresh", lease_seconds=60)
            assert stale is not None and fresh is not None
            with pytest.raises(LeaseLost):
                await repo.append_worker_event(
                    run_id,
                    "run.progress",
                    {"node": "estimate", "status": "completed"},
                    owner="runner-stale",
                    lease_epoch=stale.lease_epoch,
                )

        asyncio.run(scenario())
    finally:
        facade.drop_session(sid)


def test_purge_session_deletes_runs_and_fences_active_worker(client):
    sid = "test-run-session-purge"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-session-purge-1"},
        )
        run_id = accepted.json()["run_id"]

        async def scenario():
            repo = RunRepository()
            claimed = await repo.claim(run_id, "runner-purged", lease_seconds=60)
            assert claimed is not None
            assert await repo.purge_session(sid) == 1
            assert await repo.get(run_id) is None
            with pytest.raises(LeaseLost):
                await repo.complete(
                    run_id,
                    owner="runner-purged",
                    lease_epoch=claimed.lease_epoch,
                    result={"should_not_commit": True},
                )

        asyncio.run(scenario())
    finally:
        facade.drop_session(sid)


def test_delete_session_stops_a_running_worker_within_one_second(client, monkeypatch):
    sid = "test-run-cancel-on-session-delete"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    started = threading.Event()
    release_request = threading.Event()
    http_request_cancelled = threading.Event()

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "late response"}}]}

    class SlowAsyncClient:
        def __init__(self, *_args, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return False

        async def post(self, *_args, **_kwargs):
            started.set()
            try:
                while not release_request.is_set():
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                http_request_cancelled.set()
                raise
            return FakeResponse()

    from agent.llm.call_llm import call_llm
    from agent.llm.router import LLMConfig

    def slow_llm_node(_state):
        return {"llm_result": call_llm("cancel me", node_type="title")}

    monkeypatch.setattr(
        "agent.engine.prewrite.PRWRITE_SEQUENCE",
        (("slow_llm", ("unused", "unused"), ()),),
    )
    monkeypatch.setattr(
        "agent.engine.prewrite._node_callable", lambda _node_id: slow_llm_node
    )
    monkeypatch.setattr(
        "agent.llm.call_llm.router.get_config",
        lambda _node: LLMConfig(
            provider="minimax",
            model="MiniMax-M3",
            api_key="sk-test",
            base_url="https://api.minimaxi.com/v1",
        ),
    )
    monkeypatch.setattr("httpx.AsyncClient", SlowAsyncClient)
    monkeypatch.setattr(
        "runner.execute_prewrite_supervised",
        facade.execute_prewrite,
    )
    accepted = client.post(
        f"/sessions/{sid}/direction",
        json=_direction(),
        headers={"Idempotency-Key": "direction-cancel-on-delete"},
    )
    run_id = accepted.json()["run_id"]

    async def scenario():
        worker = asyncio.create_task(
            process_one_run(
                owner="cancel-on-delete",
                run_id=run_id,
            )
        )
        assert await asyncio.to_thread(started.wait, 1)
        cancel_started = time.monotonic()
        assert await asyncio.to_thread(facade.delete_session, sid) is True
        timed_out = False
        try:
            await asyncio.wait_for(asyncio.shield(worker), timeout=1)
        except asyncio.TimeoutError:
            timed_out = True
            release_request.set()
            await worker
        assert timed_out is False
        assert http_request_cancelled.is_set()
        assert time.monotonic() - cancel_started < 1
        from run_store import run_dir

        assert not run_dir(sid).exists()

    try:
        asyncio.run(scenario())
    finally:
        release_request.set()
        facade.drop_session(sid)


def test_delete_session_kills_blocking_prewrite_and_its_descendant(
    client, tmp_path, monkeypatch
):
    sid = "test-run-kills-blocking-process-tree"
    started_path = tmp_path / "blocking-started"
    finished_path = tmp_path / "descendant-finished"
    facade.seed_state(
        sid,
        {
            "csv_path": "/tmp/input.csv",
            "_test_started_path": str(started_path),
            "_test_finished_path": str(finished_path),
        },
    )
    accepted = client.post(
        f"/sessions/{sid}/direction",
        json=_direction(),
        headers={"Idempotency-Key": "direction-kill-process-tree"},
    )
    run_id = accepted.json()["run_id"]
    _use_child_executor(monkeypatch, blocking_prewrite_with_descendant)

    async def scenario():
        worker = asyncio.create_task(
            process_one_run(
                owner="kill-process-tree",
                run_id=run_id,
            )
        )
        assert await asyncio.to_thread(
            lambda: _wait_for_path(started_path, timeout=2)
        )
        cancel_started = time.monotonic()
        assert await asyncio.to_thread(facade.delete_session, sid) is True
        await asyncio.wait_for(worker, timeout=1)
        assert time.monotonic() - cancel_started < 1

    try:
        asyncio.run(scenario())
        time.sleep(1.8)
        assert not finished_path.exists()
    finally:
        facade.drop_session(sid)


def test_authority_probe_outage_cancels_within_one_second():
    lease_lost = threading.Event()

    class UnavailableRepository:
        async def lease_is_current(self, *_args, **_kwargs):
            raise RuntimeError("database unavailable")

    async def scenario():
        started = time.monotonic()
        await asyncio.wait_for(
            _heartbeat(
                UnavailableRepository(),
                "run-without-authority",
                "worker",
                1,
                lease_lost,
            ),
            timeout=1,
        )
        assert lease_lost.is_set()
        assert time.monotonic() - started < 1

    asyncio.run(scenario())


def test_single_authority_probe_failure_does_not_cancel_the_run():
    lease_lost = threading.Event()

    class RecoveringRepository:
        def __init__(self):
            self.calls = 0

        async def lease_is_current(self, *_args, **_kwargs):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("transient database error")
            return True

    async def scenario():
        heartbeat = asyncio.create_task(
            _heartbeat(
                RecoveringRepository(),
                "run-with-transient-error",
                "worker",
                1,
                lease_lost,
            )
        )
        await asyncio.sleep(0.8)
        assert not lease_lost.is_set()
        heartbeat.cancel()
        with pytest.raises(asyncio.CancelledError):
            await heartbeat

    asyncio.run(scenario())


def test_stuck_authority_probe_cancels_within_one_second():
    lease_lost = threading.Event()

    class StuckRepository:
        async def lease_is_current(self, *_args, **_kwargs):
            await asyncio.Event().wait()

    async def scenario():
        started = time.monotonic()
        await asyncio.wait_for(
            _heartbeat(
                StuckRepository(),
                "run-with-stuck-authority",
                "worker",
                1,
                lease_lost,
            ),
            timeout=1,
        )
        assert lease_lost.is_set()
        assert time.monotonic() - started < 1

    asyncio.run(scenario())


def test_durable_prewrite_does_not_recreate_deleted_workspace(monkeypatch):
    sid = "test-run-no-workspace-recreation"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    assert facade.delete_session(sid) is True

    monkeypatch.setattr(
        "agent.engine.prewrite.run_prewrite",
        lambda state, **_kwargs: state,
    )

    result = facade.execute_prewrite(
        sid,
        _direction(),
        {"csv_path": "/tmp/input.csv"},
        cancellation_check=lambda: False,
    )

    from run_store import run_dir

    assert "workspace" not in result
    assert not run_dir(sid).exists()


def test_sse_resumes_after_last_event_id(client):
    sid = "test-run-sse-resume"
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv"})
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": "direction-sse-1"},
        )
        run_id = accepted.json()["run_id"]

        async def finish():
            repo = RunRepository()
            claimed = await repo.claim(run_id, "sse-runner", lease_seconds=60)
            assert claimed and claimed.run_id == run_id
            await repo.complete(
                run_id,
                owner="sse-runner",
                lease_epoch=claimed.lease_epoch,
                result={"ok": True},
            )

        asyncio.run(finish())
        response = client.get(
            f"/runs/{run_id}/events",
            headers={"Last-Event-ID": "1"},
        )
        assert response.status_code == 200, response.text
        assert "id: 1\n" not in response.text
        assert '"status":"SUCCEEDED"' in response.text
    finally:
        facade.drop_session(sid)

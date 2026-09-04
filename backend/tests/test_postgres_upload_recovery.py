"""PostgreSQL-only acceptance for durable upload queue semantics."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest
from sqlalchemy import func, select, text

from database import (
    _engine,
    _ensure_run_lifecycle_constraints,
    create_tables,
    session_factory,
)
from facade import facade
from models.research_session import ResearchSession
from models.run import Run, RunEvent
from run_repository import LeaseLost, RunRepository, upload_fingerprint


pytestmark = pytest.mark.skipif(
    not os.getenv("TEST_POSTGRES_DATABASE_URL"),
    reason="requires an isolated PostgreSQL test database",
)


def test_postgres_upgrade_admission_reclaim_and_fencing(tmp_path: Path) -> None:
    """Exercise PostgreSQL DDL, concurrency, lease reclaim, and stale fencing."""

    async def scenario() -> None:
        await create_tables()
        factory = session_factory()
        async with factory() as db:
            assert db.bind is not None
            assert db.bind.dialect.name == "postgresql"

        # Recreate the previous prewrite-only shape, then exercise the real
        # PostgreSQL upgrade path instead of accepting fresh-schema proof.
        async with _engine.begin() as conn:
            await conn.execute(
                text(
                    "ALTER TABLE runs DROP CONSTRAINT IF EXISTS "
                    "ck_runs_supported_kind"
                )
            )
            await conn.execute(
                text(
                    "ALTER TABLE runs ADD CONSTRAINT ck_runs_supported_kind "
                    "CHECK (kind = 'prewrite')"
                )
            )
            await conn.execute(
                text("DROP INDEX IF EXISTS uq_runs_upload_idempotency")
            )
            await _ensure_run_lifecycle_constraints(conn)

            check_definition = await conn.scalar(
                text(
                    "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                    "WHERE conname = 'ck_runs_supported_kind' "
                    "AND conrelid = 'runs'::regclass"
                )
            )
            assert "upload_pipeline" in str(check_definition)

        input_path = tmp_path / "input.csv"
        input_path.write_text("x,y\n1,2\n", encoding="utf-8")
        fingerprint = upload_fingerprint(input_path.read_bytes(), input_path.name)
        values = {
            "user_id": 17,
            "csv_path": str(input_path),
            "dataset_meta": {"columns": ["x", "y"], "rows": 1},
            "initial_state": {
                "csv_path": str(input_path),
                "uploaded_datasets": [
                    {"path": str(input_path), "format": "csv"}
                ],
            },
            "idempotency_key": "5e19246d-3591-40d0-a24e-0e286a0809d2",
            "input_fingerprint": fingerprint,
        }
        first_repo = RunRepository()
        second_repo = RunRepository()
        first, second = await asyncio.gather(
            first_repo.admit_upload(session_id="pg-upload-a", **values),
            second_repo.admit_upload(session_id="pg-upload-b", **values),
        )

        assert {first.replayed, second.replayed} == {False, True}
        assert first.session.session_id == second.session.session_id
        assert first.run.run_id == second.run.run_id
        run_id = first.run.run_id
        session_id = first.session.session_id

        async with factory() as db:
            assert await db.scalar(select(func.count()).select_from(Run)) == 1
            assert await db.scalar(select(func.count()).select_from(RunEvent)) == 1

        epoch_one = await first_repo.claim(run_id, "worker-one", lease_seconds=1)
        assert epoch_one is not None
        await asyncio.sleep(1.1)
        epoch_two = await second_repo.claim(run_id, "worker-two", lease_seconds=30)
        assert epoch_two is not None
        assert epoch_two.lease_epoch == epoch_one.lease_epoch + 1

        with pytest.raises(LeaseLost):
            await first_repo.append_worker_event(
                run_id,
                "run.progress",
                {"node": "stale", "status": "completed"},
                owner="worker-one",
                lease_epoch=epoch_one.lease_epoch,
            )

        output_path = tmp_path / "cleaned.csv"
        output_path.write_text("x,y\n1,2\n", encoding="utf-8")
        await second_repo.complete(
            run_id,
            owner="worker-two",
            lease_epoch=epoch_two.lease_epoch,
            result={
                "csv_path": str(output_path),
                "cleaning_report": {"steps": []},
            },
        )

        terminal = await second_repo.get(run_id)
        assert terminal is not None
        assert terminal.status == "SUCCEEDED"
        async with factory() as db:
            session = await db.get(ResearchSession, session_id)
            assert session is not None
            assert session.csv_path == str(output_path)
            assert session.state["upload_readiness"] == "READY"

        assert (
            await second_repo.resolve_upload(
                values["idempotency_key"],
                user_id=999,
                allow_anonymous_capability=False,
            )
            is None
        )
        resolved = await second_repo.resolve_upload(
            values["idempotency_key"],
            user_id=17,
            allow_anonymous_capability=False,
        )
        assert resolved is not None
        assert resolved.run.run_id == run_id

        assert await asyncio.to_thread(facade.delete_session, session_id) is True
        assert await second_repo.get(run_id) is None
        assert await second_repo.events_after(run_id, 0) == []

    asyncio.run(scenario())

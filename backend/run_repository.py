"""PostgreSQL-backed run queue with leases, fencing, and ordered events."""

from __future__ import annotations

import hashlib
import json
import unicodedata
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

from sqlalchemy import delete, func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import session_factory
from models.research_session import ResearchSession
from models.run import Run, RunEvent
from services.research_lab import merge_spec_run_lab, strip_spec_run_result


ACTIVE_STATUSES = ("PENDING", "RUNNING", "RECONCILING")
TERMINAL_STATUSES = ("SUCCEEDED", "FAILED", "CANCELLED")
RunStatus = Literal[
    "PENDING",
    "RUNNING",
    "RECONCILING",
    "SUCCEEDED",
    "FAILED",
    "CANCELLED",
]
RunKind = Literal["prewrite", "upload_pipeline", "spec_run"]
SUPPORTED_RUN_KINDS = ("prewrite", "upload_pipeline", "spec_run")


class LeaseLost(RuntimeError):
    """Raised when an expired worker attempts to commit an authoritative effect."""


class QueueFull(RuntimeError):
    """Raised when the bounded pending queue has reached capacity."""


class SessionNotFound(RuntimeError):
    """Raised when durable work is admitted after its session disappeared."""


class IdempotencyConflict(RuntimeError):
    """Raised when an upload key cannot be safely replayed."""

    def __init__(self) -> None:
        super().__init__("idempotency key cannot be replayed")


class UploadResultInvalid(RuntimeError):
    """Raised when upload computation did not produce a readable CSV."""

    def __init__(self) -> None:
        super().__init__("upload result is not readable")


class SessionBusy(RuntimeError):
    def __init__(self, run_id: str):
        super().__init__(f"session already has active run {run_id}")
        self.run_id = run_id


@dataclass(frozen=True)
class ClaimedRun:
    run_id: str
    session_id: str
    kind: str
    payload: dict[str, Any]
    attempt: int
    lease_epoch: int


@dataclass(frozen=True)
class UploadAdmission:
    session: ResearchSession
    run: Run
    replayed: bool


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _json_safe(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def _normalized_upload_filename(filename: str) -> bytes:
    normalized_name = unicodedata.normalize("NFKC", filename)
    normalized_name = normalized_name.replace("\\", "/").rsplit("/", 1)[-1]
    normalized_name = normalized_name.strip().casefold()
    return normalized_name.encode("utf-8")


def finalize_upload_fingerprint(digest: Any, filename: str) -> str:
    """Finish a streaming SHA-256 fingerprint with the normalized filename."""
    finished = digest.copy()
    finished.update(b"\0")
    finished.update(_normalized_upload_filename(filename))
    return finished.hexdigest()


def upload_fingerprint(raw_bytes: bytes, filename: str) -> str:
    """Bind an upload retry to its exact bytes and normalized leaf filename."""
    digest = hashlib.sha256()
    digest.update(raw_bytes)
    return finalize_upload_fingerprint(digest, filename)


@asynccontextmanager
async def _write_transaction(db: AsyncSession):
    """Serialize SQLite writers; use ordinary row transactions elsewhere."""
    dialect = db.bind.dialect.name if db.bind is not None else ""
    if dialect != "sqlite":
        async with db.begin():
            yield
        return

    # SQLite ignores SELECT ... FOR UPDATE. Reserving its single writer before
    # any lifecycle read prevents two processes from both reading a live
    # session and then racing to upgrade their transactions.
    await db.execute(text("BEGIN IMMEDIATE"))
    try:
        yield
    except Exception:
        await db.rollback()
        raise
    else:
        await db.commit()


class RunRepository:
    def __init__(self, *, queue_capacity: int = 20) -> None:
        self.queue_capacity = queue_capacity
        self._factory = session_factory()

    async def enqueue(
        self,
        *,
        session_id: str,
        kind: RunKind,
        payload: dict[str, Any],
        idempotency_key: str | None,
    ) -> Run:
        if kind not in SUPPORTED_RUN_KINDS:
            raise ValueError(f"unsupported run kind: {kind}")
        try:
            async with self._factory() as db:
                async with _write_transaction(db):
                    locked_session_id = await db.scalar(
                        select(ResearchSession.session_id)
                        .where(ResearchSession.session_id == session_id)
                        .with_for_update()
                    )
                    if locked_session_id is None:
                        raise SessionNotFound(
                            f"session {session_id} no longer exists"
                        )
                    await self._lock_admission(db)
                    if idempotency_key:
                        existing = await self._idempotent_run(
                            db, session_id, kind, idempotency_key
                        )
                        if existing is not None:
                            return existing

                    active = await self._active_run(db, session_id)
                    if active is not None:
                        raise SessionBusy(active.run_id)

                    pending = await db.scalar(
                        select(func.count())
                        .select_from(Run)
                        .where(Run.status == "PENDING")
                    )
                    if int(pending or 0) >= self.queue_capacity:
                        raise QueueFull("run queue is full")

                    run = Run(
                        run_id=str(uuid.uuid4()),
                        session_id=session_id,
                        kind=kind,
                        status="PENDING",
                        payload=_json_safe(payload),
                        idempotency_key=idempotency_key,
                    )
                    db.add(run)
                    await db.flush()
                    await self._append_locked(
                        db, run, "run.accepted", {"status": "PENDING", "kind": kind}
                    )
                return run
        except IntegrityError:
            async with self._factory() as db:
                if idempotency_key:
                    existing = await self._idempotent_run(
                        db, session_id, kind, idempotency_key
                    )
                    if existing is not None:
                        return existing
                active = await self._active_run(db, session_id)
                if active is not None:
                    raise SessionBusy(active.run_id)
                session = await db.get(ResearchSession, session_id)
                if session is None:
                    raise SessionNotFound(
                        f"session {session_id} no longer exists"
                    )
            raise

    async def admit_upload(
        self,
        *,
        session_id: str,
        user_id: int | None,
        csv_path: str,
        dataset_meta: dict[str, Any],
        initial_state: dict[str, Any],
        idempotency_key: str,
        input_fingerprint: str,
    ) -> UploadAdmission:
        """Atomically create or replay one durable upload Session and Run."""
        if not idempotency_key:
            raise ValueError("idempotency key is required")
        if not input_fingerprint:
            raise ValueError("input fingerprint is required")
        try:
            async with self._factory() as db:
                async with _write_transaction(db):
                    await self._lock_admission(db)
                    existing = await self._upload_by_key(db, idempotency_key)
                    if existing is not None:
                        return await self._validate_upload_replay(
                            db,
                            existing,
                            user_id=user_id,
                            input_fingerprint=input_fingerprint,
                        )

                    pending = await db.scalar(
                        select(func.count())
                        .select_from(Run)
                        .where(Run.status == "PENDING")
                    )
                    if int(pending or 0) >= self.queue_capacity:
                        raise QueueFull("run queue is full")

                    state = _json_safe(initial_state)
                    state["upload_readiness"] = "PROCESSING"
                    session = ResearchSession(
                        session_id=session_id,
                        user_id=user_id,
                        state=state,
                        csv_path=csv_path,
                        metadata_json=_json_safe(dataset_meta),
                    )
                    run = Run(
                        run_id=str(uuid.uuid4()),
                        session_id=session_id,
                        kind="upload_pipeline",
                        status="PENDING",
                        payload={
                            "initial_state": {**state, "csv_path": csv_path},
                            "dataset_meta": _json_safe(dataset_meta),
                            "input_fingerprint": input_fingerprint,
                        },
                        idempotency_key=idempotency_key,
                    )
                    db.add(session)
                    db.add(run)
                    await db.flush()
                    await self._append_locked(
                        db,
                        run,
                        "run.accepted",
                        {"status": "PENDING", "kind": "upload_pipeline"},
                    )
                return UploadAdmission(session=session, run=run, replayed=False)
        except IntegrityError:
            # A globally unique key resolves a concurrent winner from the
            # primary database. Mismatched owner/input never receives IDs.
            async with self._factory() as db:
                existing = await self._upload_by_key(db, idempotency_key)
                if existing is not None:
                    return await self._validate_upload_replay(
                        db,
                        existing,
                        user_id=user_id,
                        input_fingerprint=input_fingerprint,
                    )
            raise

    @staticmethod
    async def _lock_admission(db: AsyncSession) -> None:
        if db.bind is not None and db.bind.dialect.name == "postgresql":
            await db.execute(
                text("SELECT pg_advisory_xact_lock(:lock_id)"),
                {"lock_id": 7302194501},
            )

    @staticmethod
    async def _upload_by_key(db: AsyncSession, idempotency_key: str) -> Run | None:
        return await db.scalar(
            select(Run).where(
                Run.kind == "upload_pipeline",
                Run.idempotency_key == idempotency_key,
            )
        )

    @staticmethod
    async def _validate_upload_replay(
        db: AsyncSession,
        run: Run,
        *,
        user_id: int | None,
        input_fingerprint: str,
    ) -> UploadAdmission:
        session = await db.get(ResearchSession, run.session_id)
        payload = dict(run.payload or {})
        if (
            session is None
            or session.user_id != user_id
            or payload.get("input_fingerprint") != input_fingerprint
        ):
            raise IdempotencyConflict()
        return UploadAdmission(session=session, run=run, replayed=True)

    @staticmethod
    async def _idempotent_run(
        db: AsyncSession,
        session_id: str,
        kind: str,
        idempotency_key: str,
    ) -> Run | None:
        return await db.scalar(
            select(Run).where(
                Run.session_id == session_id,
                Run.kind == kind,
                Run.idempotency_key == idempotency_key,
            )
        )

    @staticmethod
    async def _active_run(db: AsyncSession, session_id: str) -> Run | None:
        return await db.scalar(
            select(Run)
            .where(
                Run.session_id == session_id,
                Run.status.in_(ACTIVE_STATUSES),
            )
            .order_by(Run.created_at.desc())
            .limit(1)
        )

    async def get(self, run_id: str) -> Run | None:
        async with self._factory() as db:
            return await db.get(Run, run_id)

    async def active_run(self, session_id: str) -> Run | None:
        """Public projection of the in-flight run a client can reattach to."""
        async with self._factory() as db:
            return await self._active_run(db, session_id)

    async def latest_run(self, session_id: str, kind: str | None = None) -> Run | None:
        """Most recent run for a session, optionally restricted to one kind."""
        async with self._factory() as db:
            query = select(Run).where(Run.session_id == session_id)
            if kind is not None:
                query = query.where(Run.kind == kind)
            return await db.scalar(query.order_by(Run.created_at.desc()).limit(1))

    async def resolve_upload(
        self,
        idempotency_key: str,
        *,
        user_id: int | None,
        allow_anonymous_capability: bool,
    ) -> UploadAdmission | None:
        """Resolve accepted upload work without disclosing another owner.

        Anonymous DEBUG sessions use possession of the high-entropy header key
        as their capability. Production-owned sessions require an exact owner.
        """
        async with self._factory() as db:
            run = await self._upload_by_key(db, idempotency_key)
            if run is None:
                return None
            session = await db.get(ResearchSession, run.session_id)
            if session is None:
                return None
            if session.user_id is None:
                if not allow_anonymous_capability:
                    return None
            elif user_id != session.user_id:
                return None
            return UploadAdmission(session=session, run=run, replayed=True)

    async def lease_is_current(
        self,
        run_id: str,
        *,
        owner: str,
        lease_epoch: int,
    ) -> bool:
        """Return whether a worker still owns an executable run."""
        async with self._factory() as db:
            current = await db.scalar(
                select(Run.run_id).where(
                    Run.run_id == run_id,
                    Run.status.in_(("RUNNING", "RECONCILING")),
                    Run.lease_owner == owner,
                    Run.lease_epoch == lease_epoch,
                    Run.lease_expires_at > _now(),
                )
            )
            return current is not None

    async def events_after(self, run_id: str, seq: int) -> list[RunEvent]:
        async with self._factory() as db:
            rows = await db.scalars(
                select(RunEvent)
                .where(RunEvent.run_id == run_id, RunEvent.seq > seq)
                .order_by(RunEvent.seq)
                .limit(1000)
            )
            return list(rows)

    async def append_event(
        self, run_id: str, event_type: str, payload: dict[str, Any]
    ) -> RunEvent:
        async with self._factory() as db:
            async with _write_transaction(db):
                run = await self._locked_run(db, run_id)
                return await self._append_locked(db, run, event_type, payload)

    async def append_worker_event(
        self,
        run_id: str,
        event_type: str,
        payload: dict[str, Any],
        *,
        owner: str,
        lease_epoch: int,
    ) -> RunEvent:
        async with self._factory() as db:
            async with _write_transaction(db):
                run = await self._locked_run(db, run_id)
                self._require_lease(run, owner, lease_epoch)
                return await self._append_locked(db, run, event_type, payload)

    async def purge_session(self, session_id: str) -> int:
        """Delete all durable work for a deleted session and fence its workers."""
        async with self._factory() as db:
            async with _write_transaction(db):
                deleted = await db.execute(
                    delete(Run).where(Run.session_id == session_id)
                )
                return int(deleted.rowcount or 0)

    async def claim_next(self, owner: str, *, lease_seconds: int = 60) -> ClaimedRun | None:
        return await self._claim(owner, lease_seconds=lease_seconds)

    async def claim(
        self, run_id: str, owner: str, *, lease_seconds: int = 60
    ) -> ClaimedRun | None:
        """Claim one known run, used by explicit recovery and deterministic workers."""
        return await self._claim(owner, lease_seconds=lease_seconds, run_id=run_id)

    async def _claim(
        self,
        owner: str,
        *,
        lease_seconds: int,
        run_id: str | None = None,
    ) -> ClaimedRun | None:
        async with self._factory() as db:
            async with _write_transaction(db):
                now = _now()
                claimable = or_(
                    Run.status == "PENDING",
                    (
                        Run.status.in_(("RUNNING", "RECONCILING"))
                        & (Run.lease_expires_at < now)
                    ),
                )
                session_exists = (
                    select(ResearchSession.session_id)
                    .where(ResearchSession.session_id == Run.session_id)
                    .exists()
                )
                stmt = select(Run).where(claimable, session_exists)
                if run_id is not None:
                    stmt = stmt.where(Run.run_id == run_id)
                stmt = (
                    stmt.order_by(Run.created_at)
                    .limit(1)
                    .with_for_update(skip_locked=True)
                )
                run = await db.scalar(stmt)
                if run is None:
                    return None
                run.status = "RUNNING"
                run.attempt += 1
                run.lease_epoch += 1
                run.lease_owner = owner
                run.lease_expires_at = now + timedelta(seconds=lease_seconds)
                run.updated_at = now
                await self._append_locked(
                    db,
                    run,
                    "run.claimed",
                    {
                        "status": "RUNNING",
                        "attempt": run.attempt,
                        "lease_epoch": run.lease_epoch,
                    },
                )
                return ClaimedRun(
                    run_id=run.run_id,
                    session_id=run.session_id,
                    kind=run.kind,
                    payload=dict(run.payload or {}),
                    attempt=run.attempt,
                    lease_epoch=run.lease_epoch,
                )

    async def heartbeat(
        self,
        run_id: str,
        *,
        owner: str,
        lease_epoch: int,
        lease_seconds: int = 60,
    ) -> None:
        async with self._factory() as db:
            async with _write_transaction(db):
                run = await self._locked_run(db, run_id)
                self._require_lease(run, owner, lease_epoch)
                run.lease_expires_at = _now() + timedelta(seconds=lease_seconds)
                run.updated_at = _now()

    async def complete(
        self,
        run_id: str,
        *,
        owner: str,
        lease_epoch: int,
        result: dict[str, Any],
    ) -> None:
        async with self._factory() as db:
            async with _write_transaction(db):
                session_id = await db.scalar(
                    select(Run.session_id).where(Run.run_id == run_id)
                )
                if session_id is None:
                    raise LeaseLost(f"run {run_id} no longer exists")
                session = await db.scalar(
                    select(ResearchSession)
                    .where(ResearchSession.session_id == session_id)
                    .with_for_update()
                )
                if session is None:
                    raise LeaseLost(f"session {session_id} no longer exists")
                # Lifecycle mutations always lock Session before Run. Keeping
                # this order avoids a delete-vs-complete deadlock in PostgreSQL.
                run = await self._locked_run(db, run_id)
                self._require_lease(run, owner, lease_epoch)
                if run.session_id != session_id:
                    raise LeaseLost(f"run {run_id} moved to another session")
                safe_result = _json_safe(result)
                if run.kind == "spec_run":
                    safe_result = strip_spec_run_result(safe_result)
                if run.kind == "upload_pipeline":
                    csv_path = safe_result.get("csv_path")
                    if not isinstance(csv_path, str) or not _is_readable_file(csv_path):
                        raise UploadResultInvalid()

                initial_state = dict((run.payload or {}).get("initial_state") or {})
                missing = object()
                current_state = dict(session.state or {})
                changed: dict[str, Any] = {}
                if run.kind == "spec_run":
                    incoming_lab = safe_result.get("research_lab")
                    if isinstance(incoming_lab, dict):
                        current_lab = current_state.get("research_lab")
                        base = dict(current_lab) if isinstance(current_lab, dict) else {}
                        changed["research_lab"] = merge_spec_run_lab(base, incoming_lab)
                    incoming_deg = safe_result.get("degradations")
                    if isinstance(incoming_deg, list) and incoming_deg:
                        changed["degradations"] = list(
                            current_state.get("degradations") or []
                        ) + incoming_deg
                else:
                    for key, value in safe_result.items():
                        if key == "_source_run_id":
                            changed[key] = value
                            continue
                        initial_value = initial_state.get(key, missing)
                        if initial_value == value:
                            continue
                        current_value = (
                            session.csv_path
                            if key == "csv_path"
                            else current_state.get(key, missing)
                        )
                        if current_value == initial_value:
                            changed[key] = value
                    if "csv_path" in changed:
                        csv_path = changed.pop("csv_path")
                        session.csv_path = str(csv_path) if csv_path else None
                    if run.kind == "upload_pipeline":
                        changed["upload_readiness"] = "READY"
                session.state = {**current_state, **changed}
                run.result = safe_result
                run.status = "SUCCEEDED"
                run.error = None
                run.lease_owner = None
                run.lease_expires_at = None
                run.updated_at = _now()
                await self._append_locked(
                    db, run, "run.succeeded", {"status": "SUCCEEDED"}
                )

    async def fail(
        self,
        run_id: str,
        *,
        owner: str,
        lease_epoch: int,
        error: str,
    ) -> None:
        async with self._factory() as db:
            async with _write_transaction(db):
                session_id = await db.scalar(
                    select(Run.session_id).where(Run.run_id == run_id)
                )
                if session_id is None:
                    raise LeaseLost(f"run {run_id} no longer exists")
                session = await db.scalar(
                    select(ResearchSession)
                    .where(ResearchSession.session_id == session_id)
                    .with_for_update()
                )
                if session is None:
                    raise LeaseLost(f"session {session_id} no longer exists")
                run = await self._locked_run(db, run_id)
                self._require_lease(run, owner, lease_epoch)
                if run.session_id != session_id:
                    raise LeaseLost(f"run {run_id} moved to another session")
                if run.kind == "upload_pipeline":
                    session.state = {
                        **dict(session.state or {}),
                        "upload_readiness": "FAILED",
                    }
                run.status = "FAILED"
                run.error = error[:4000]
                run.lease_owner = None
                run.lease_expires_at = None
                run.updated_at = _now()
                await self._append_locked(
                    db,
                    run,
                    "run.failed",
                    {"status": "FAILED", "error": error[:500]},
                )

    async def _locked_run(self, db: AsyncSession, run_id: str) -> Run:
        run = await db.scalar(
            select(Run).where(Run.run_id == run_id).with_for_update()
        )
        if run is None:
            raise LeaseLost(f"run {run_id} no longer exists")
        return run

    async def _append_locked(
        self,
        db: AsyncSession,
        run: Run,
        event_type: str,
        payload: dict[str, Any],
    ) -> RunEvent:
        run.next_event_seq += 1
        event = RunEvent(
            run_id=run.run_id,
            seq=run.next_event_seq,
            event_type=event_type,
            payload=_json_safe(payload),
        )
        db.add(event)
        await db.flush()
        return event

    @staticmethod
    def _require_lease(run: Run, owner: str, lease_epoch: int) -> None:
        now = _now()
        lease_expires_at = run.lease_expires_at
        if lease_expires_at is not None and lease_expires_at.tzinfo is None:
            now = now.replace(tzinfo=None)
        if (
            run.status != "RUNNING"
            or run.lease_owner != owner
            or run.lease_epoch != lease_epoch
            or lease_expires_at is None
            or lease_expires_at <= now
        ):
            raise LeaseLost(
                f"run {run.run_id} lease moved to epoch {run.lease_epoch}"
            )


def _is_readable_file(raw_path: str) -> bool:
    try:
        path = Path(raw_path)
        if not path.is_file():
            return False
        with path.open("rb") as handle:
            handle.read(1)
        return True
    except (OSError, ValueError):
        return False

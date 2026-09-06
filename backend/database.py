"""SQLAlchemy async engine factory and session dependency.

Uses :attr:`config.settings.DATABASE_URL`. Defaults to SQLite for local
development; switch to ``postgresql+asyncpg://...`` for production.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import ensure_private_file, settings

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    hide_parameters=True,
    pool_pre_ping=True,
)

_async_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def _sync_database_url() -> str:
    """Return the synchronous driver URL for facade calls and agent nodes."""
    url = make_url(settings.DATABASE_URL)
    drivers = {
        "sqlite+aiosqlite": "sqlite+pysqlite",
        "postgresql+asyncpg": "postgresql+psycopg",
    }
    drivername = drivers.get(url.drivername)
    if drivername is None:
        raise RuntimeError(
            f"DATABASE_URL driver {url.drivername!r} has no synchronous companion"
        )
    return url.set(drivername=drivername).render_as_string(hide_password=False)


_sync_engine = create_engine(
    _sync_database_url(),
    echo=settings.DEBUG,
    hide_parameters=True,
    pool_pre_ping=True,
)


def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


if make_url(settings.DATABASE_URL).get_backend_name() == "sqlite":
    # Async SQLite exposes its DBAPI connection through the sync-engine event.
    # Both engines must enforce the same lifecycle constraints because the
    # facade is synchronous while run admission/deletion is asynchronous.
    event.listen(_engine.sync_engine, "connect", _enable_sqlite_foreign_keys)
    event.listen(_sync_engine, "connect", _enable_sqlite_foreign_keys)
_sync_session_factory = sessionmaker(
    _sync_engine,
    expire_on_commit=False,
    class_=Session,
)


def session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared async session factory for background processes."""
    return _async_session_factory


def sync_session_factory() -> sessionmaker[Session]:
    """Return the shared sync factory used by the synchronous facade API."""
    return _sync_session_factory


class Base(DeclarativeBase):
    """Base class for all ORM models."""


_RUN_SCHEMA_MIGRATION = "run-upload-pipeline-v1"


async def _ensure_run_lifecycle_constraints(conn) -> None:
    """Upgrade every legacy Run shape without discarding lifecycle data."""
    if conn.dialect.name == "postgresql":
        await _upgrade_postgres_run_schema(conn)
        return
    if conn.dialect.name == "sqlite":
        await _upgrade_sqlite_run_schema(conn)


async def _upgrade_postgres_run_schema(conn) -> None:
    unsupported = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM runs "
                "WHERE kind NOT IN ('prewrite', 'upload_pipeline', 'spec_run')"
            )
        )
        or 0
    )
    if unsupported:
        raise RuntimeError(
            "run schema upgrade aborted: unsupported historical run kinds exist"
        )
    duplicate_upload_keys = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM ("
                "SELECT idempotency_key FROM runs "
                "WHERE kind = 'upload_pipeline' AND idempotency_key IS NOT NULL "
                "GROUP BY idempotency_key HAVING count(*) > 1"
                ") conflicts"
            )
        )
        or 0
    )
    if duplicate_upload_keys:
        raise RuntimeError(
            "run schema upgrade aborted: duplicate upload idempotency keys exist"
        )
    duplicate_idempotency = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM ("
                "SELECT session_id, kind, idempotency_key FROM runs "
                "WHERE idempotency_key IS NOT NULL "
                "GROUP BY session_id, kind, idempotency_key HAVING count(*) > 1"
                ") conflicts"
            )
        )
        or 0
    )
    duplicate_active = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM ("
                "SELECT session_id FROM runs "
                "WHERE status IN ('PENDING', 'RUNNING', 'RECONCILING') "
                "GROUP BY session_id HAVING count(*) > 1"
                ") conflicts"
            )
        )
        or 0
    )
    if duplicate_idempotency or duplicate_active:
        raise RuntimeError(
            "run schema upgrade aborted: historical uniqueness conflicts exist"
        )

    check_definition = await conn.scalar(
        text(
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
            "WHERE conname = 'ck_runs_supported_kind' "
            "AND conrelid = 'runs'::regclass"
        )
    )
    if check_definition is None or "spec_run" not in str(check_definition):
        await conn.execute(
            text("ALTER TABLE runs DROP CONSTRAINT IF EXISTS ck_runs_supported_kind")
        )
        await conn.execute(
            text(
                "ALTER TABLE runs ADD CONSTRAINT ck_runs_supported_kind "
                "CHECK (kind IN ('prewrite', 'upload_pipeline', 'spec_run'))"
            )
        )

    await conn.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_runs_upload_idempotency "
            "ON runs (idempotency_key) "
            "WHERE kind = 'upload_pipeline' AND idempotency_key IS NOT NULL"
        )
    )
    await conn.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_runs_session_active "
            "ON runs (session_id) "
            "WHERE status IN ('PENDING', 'RUNNING', 'RECONCILING')"
        )
    )

    idempotency_constraint = await conn.scalar(
        text(
            "SELECT 1 FROM pg_constraint "
            "WHERE conname = 'uq_runs_idempotency' "
            "AND conrelid = 'runs'::regclass"
        )
    )
    if idempotency_constraint is None:
        await conn.execute(
            text(
                "ALTER TABLE runs ADD CONSTRAINT uq_runs_idempotency "
                "UNIQUE (session_id, kind, idempotency_key)"
            )
        )

    run_fk_validated = await conn.scalar(
        text(
            "SELECT convalidated FROM pg_constraint "
            "WHERE conname = 'fk_runs_session' "
            "AND conrelid = 'runs'::regclass"
        )
    )
    event_fk_validated = await conn.scalar(
        text(
            "SELECT convalidated FROM pg_constraint "
            "WHERE conname = 'fk_run_events_run' "
            "AND conrelid = 'run_events'::regclass"
        )
    )
    if run_fk_validated is None:
        await conn.execute(
            text(
                "ALTER TABLE runs ADD CONSTRAINT fk_runs_session "
                "FOREIGN KEY (session_id) REFERENCES research_sessions(session_id) "
                "ON DELETE CASCADE NOT VALID"
            )
        )
        run_fk_validated = False
    if event_fk_validated is None:
        await conn.execute(
            text(
                "ALTER TABLE run_events ADD CONSTRAINT fk_run_events_run "
                "FOREIGN KEY (run_id) REFERENCES runs(run_id) "
                "ON DELETE CASCADE NOT VALID"
            )
        )
        event_fk_validated = False

    validations = (
        (
            "fk_runs_session",
            run_fk_validated,
            "SELECT count(*) FROM runs r WHERE NOT EXISTS "
            "(SELECT 1 FROM research_sessions s WHERE s.session_id = r.session_id)",
            "runs",
        ),
        (
            "fk_run_events_run",
            event_fk_validated,
            "SELECT count(*) FROM run_events e WHERE NOT EXISTS "
            "(SELECT 1 FROM runs r WHERE r.run_id = e.run_id)",
            "run_events",
        ),
    )
    for constraint, validated, orphan_query, table in validations:
        if validated:
            continue
        orphan_count = int(await conn.scalar(text(orphan_query)) or 0)
        if orphan_count:
            raise RuntimeError(
                f"run schema upgrade aborted: {table} contains orphan rows"
            )
        await conn.execute(
            text(f"ALTER TABLE {table} VALIDATE CONSTRAINT {constraint}")
        )

    await conn.execute(
        text(
            "INSERT INTO data_migrations (name, applied_at) "
            "VALUES (:name, CURRENT_TIMESTAMP) ON CONFLICT (name) DO NOTHING"
        ),
        {"name": _RUN_SCHEMA_MIGRATION},
    )


async def _sqlite_columns(conn, table: str) -> set[str]:
    rows = await conn.execute(text(f"PRAGMA table_info({table})"))
    return {str(row[1]) for row in rows}


async def _sqlite_has_unique_columns(conn, table: str, columns: tuple[str, ...]) -> bool:
    for row in await conn.execute(text(f"PRAGMA index_list({table})")):
        if not bool(row[2]):
            continue
        index_name = str(row[1]).replace("'", "''")
        index_columns = tuple(
            str(column[2])
            for column in await conn.execute(
                text(f"PRAGMA index_info('{index_name}')")
            )
        )
        if index_columns == columns:
            return True
    return False


def _sqlite_copy_expression(columns: set[str], name: str, fallback: str) -> str:
    return name if name in columns else fallback


async def _upgrade_sqlite_run_schema(conn) -> None:
    # The first write serializes concurrent API/Runner startup migrations.
    await conn.execute(
        text(
            "CREATE TABLE IF NOT EXISTS data_migrations ("
            "name VARCHAR(120) PRIMARY KEY, "
            "applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
    )
    await conn.execute(text("UPDATE data_migrations SET name = name WHERE 0"))

    run_sql = str(
        await conn.scalar(
            text("SELECT sql FROM sqlite_master WHERE type='table' AND name='runs'")
        )
        or ""
    )
    if not run_sql:
        return
    run_indexes = {
        str(row[1]) for row in await conn.execute(text("PRAGMA index_list(runs)"))
    }
    run_fks = await conn.execute(text("PRAGMA foreign_key_list(runs)"))
    event_fks = await conn.execute(text("PRAGMA foreign_key_list(run_events)"))
    current = (
        "upload_pipeline" in run_sql
        and "spec_run" in run_sql
        and "uq_runs_upload_idempotency" in run_indexes
        and "uq_runs_session_active" in run_indexes
        and await _sqlite_has_unique_columns(
            conn, "runs", ("session_id", "kind", "idempotency_key")
        )
        and any(row[2] == "research_sessions" for row in run_fks)
        and any(row[2] == "runs" for row in event_fks)
    )
    if current:
        await conn.execute(
            text(
                "INSERT OR IGNORE INTO data_migrations (name, applied_at) "
                "VALUES (:name, CURRENT_TIMESTAMP)"
            ),
            {"name": _RUN_SCHEMA_MIGRATION},
        )
        return

    run_columns = await _sqlite_columns(conn, "runs")
    event_columns = await _sqlite_columns(conn, "run_events")
    required_run_columns = {"run_id", "session_id"}
    required_event_columns = {"run_id", "seq"}
    if not required_run_columns.issubset(run_columns) or not required_event_columns.issubset(
        event_columns
    ):
        raise RuntimeError(
            "run schema upgrade aborted: legacy lifecycle tables lack identity columns"
        )

    kind_expr = _sqlite_copy_expression(run_columns, "kind", "'prewrite'")
    unsupported = int(
        await conn.scalar(
            text(
                f"SELECT count(*) FROM runs WHERE {kind_expr} "
                "NOT IN ('prewrite', 'upload_pipeline', 'spec_run')"
            )
        )
        or 0
    )
    if unsupported:
        raise RuntimeError(
            "run schema upgrade aborted: unsupported historical run kinds exist"
        )
    orphan_runs = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM runs r WHERE NOT EXISTS "
                "(SELECT 1 FROM research_sessions s WHERE s.session_id = r.session_id)"
            )
        )
        or 0
    )
    orphan_events = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM run_events e WHERE NOT EXISTS "
                "(SELECT 1 FROM runs r WHERE r.run_id = e.run_id)"
            )
        )
        or 0
    )
    if orphan_runs or orphan_events:
        raise RuntimeError(
            "run schema upgrade aborted: orphan lifecycle rows require repair"
        )

    idempotency_expr = _sqlite_copy_expression(
        run_columns, "idempotency_key", "NULL"
    )
    duplicate_upload_keys = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM ("
                f"SELECT {idempotency_expr} FROM runs "
                f"WHERE {kind_expr} = 'upload_pipeline' "
                f"AND {idempotency_expr} IS NOT NULL "
                f"GROUP BY {idempotency_expr} HAVING count(*) > 1) conflicts"
            )
        )
        or 0
    )
    duplicate_idempotency = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM ("
                f"SELECT session_id, {kind_expr}, {idempotency_expr} FROM runs "
                f"WHERE {idempotency_expr} IS NOT NULL "
                f"GROUP BY session_id, {kind_expr}, {idempotency_expr} "
                "HAVING count(*) > 1) conflicts"
            )
        )
        or 0
    )
    status_expr = _sqlite_copy_expression(run_columns, "status", "'PENDING'")
    duplicate_active = int(
        await conn.scalar(
            text(
                "SELECT count(*) FROM ("
                "SELECT session_id FROM runs "
                f"WHERE {status_expr} IN ('PENDING', 'RUNNING', 'RECONCILING') "
                "GROUP BY session_id HAVING count(*) > 1) conflicts"
            )
        )
        or 0
    )
    if duplicate_upload_keys or duplicate_idempotency or duplicate_active:
        raise RuntimeError(
            "run schema upgrade aborted: historical uniqueness conflicts exist"
        )

    preserved_objects = list(
        await conn.execute(
            text(
                "SELECT type, name, sql FROM sqlite_master "
                "WHERE tbl_name IN ('runs', 'run_events') "
                "AND type IN ('index', 'trigger') AND sql IS NOT NULL"
            )
        )
    )
    managed_names = {
        "ix_runs_claim",
        "ix_runs_session_created",
        "uq_runs_upload_idempotency",
        "uq_runs_session_active",
        "trg_runs_session_insert",
        "trg_runs_session_update",
        "trg_run_events_run_insert",
        "trg_run_events_run_update",
        "trg_runs_delete_events",
        "trg_sessions_delete_runs",
    }

    await conn.execute(text("DROP TABLE IF EXISTS _run_events_upgrade_v1"))
    await conn.execute(text("DROP TABLE IF EXISTS _runs_upgrade_v1"))
    await conn.execute(
        text(
            "CREATE TABLE _runs_upgrade_v1 ("
            "run_id VARCHAR(36) PRIMARY KEY, "
            "session_id VARCHAR(64) NOT NULL, "
            "kind VARCHAR(64) NOT NULL, "
            "status VARCHAR(24) NOT NULL, "
            "payload JSON NOT NULL, result JSON, error TEXT, "
            "idempotency_key VARCHAR(200), attempt INTEGER NOT NULL, "
            "lease_owner VARCHAR(200), lease_expires_at DATETIME, "
            "lease_epoch INTEGER NOT NULL, next_event_seq INTEGER NOT NULL, "
            "created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL, "
            "CONSTRAINT ck_runs_supported_kind "
            "CHECK (kind IN ('prewrite', 'upload_pipeline', 'spec_run')), "
            "CONSTRAINT uq_runs_idempotency "
            "UNIQUE (session_id, kind, idempotency_key), "
            "CONSTRAINT fk_runs_session FOREIGN KEY(session_id) "
            "REFERENCES research_sessions(session_id) ON DELETE CASCADE)"
        )
    )
    await conn.execute(
        text(
            "CREATE TABLE _run_events_upgrade_v1 ("
            "run_id VARCHAR(36) NOT NULL, seq INTEGER NOT NULL, "
            "event_type VARCHAR(80) NOT NULL, payload JSON NOT NULL, "
            "created_at DATETIME NOT NULL, PRIMARY KEY (run_id, seq), "
            "CONSTRAINT fk_run_events_run FOREIGN KEY(run_id) "
            "REFERENCES _runs_upgrade_v1(run_id) ON DELETE CASCADE)"
        )
    )

    run_values = {
        "run_id": "run_id",
        "session_id": "session_id",
        "kind": kind_expr,
        "status": status_expr,
        "payload": _sqlite_copy_expression(run_columns, "payload", "'{}'"),
        "result": _sqlite_copy_expression(run_columns, "result", "NULL"),
        "error": _sqlite_copy_expression(run_columns, "error", "NULL"),
        "idempotency_key": idempotency_expr,
        "attempt": _sqlite_copy_expression(run_columns, "attempt", "0"),
        "lease_owner": _sqlite_copy_expression(run_columns, "lease_owner", "NULL"),
        "lease_expires_at": _sqlite_copy_expression(
            run_columns, "lease_expires_at", "NULL"
        ),
        "lease_epoch": _sqlite_copy_expression(run_columns, "lease_epoch", "0"),
        "next_event_seq": (
            "MAX(COALESCE(next_event_seq, 0), COALESCE((SELECT MAX(seq) "
            "FROM run_events WHERE run_events.run_id = runs.run_id), 0))"
            if "next_event_seq" in run_columns
            else "COALESCE((SELECT MAX(seq) FROM run_events "
            "WHERE run_events.run_id = runs.run_id), 0)"
        ),
        "created_at": _sqlite_copy_expression(
            run_columns, "created_at", "CURRENT_TIMESTAMP"
        ),
        "updated_at": _sqlite_copy_expression(
            run_columns, "updated_at", "CURRENT_TIMESTAMP"
        ),
    }
    run_column_names = ", ".join(run_values)
    await conn.execute(
        text(
            f"INSERT INTO _runs_upgrade_v1 ({run_column_names}) "
            f"SELECT {', '.join(run_values.values())} FROM runs"
        )
    )
    event_values = {
        "run_id": "run_id",
        "seq": "seq",
        "event_type": _sqlite_copy_expression(
            event_columns, "event_type", "'legacy.event'"
        ),
        "payload": _sqlite_copy_expression(event_columns, "payload", "'{}'"),
        "created_at": _sqlite_copy_expression(
            event_columns, "created_at", "CURRENT_TIMESTAMP"
        ),
    }
    event_column_names = ", ".join(event_values)
    await conn.execute(
        text(
            f"INSERT INTO _run_events_upgrade_v1 ({event_column_names}) "
            f"SELECT {', '.join(event_values.values())} FROM run_events"
        )
    )
    old_run_count = int(await conn.scalar(text("SELECT count(*) FROM runs")) or 0)
    old_event_count = int(
        await conn.scalar(text("SELECT count(*) FROM run_events")) or 0
    )
    if old_run_count != int(
        await conn.scalar(text("SELECT count(*) FROM _runs_upgrade_v1")) or 0
    ) or old_event_count != int(
        await conn.scalar(text("SELECT count(*) FROM _run_events_upgrade_v1")) or 0
    ):
        raise RuntimeError("run schema upgrade aborted: lifecycle row count mismatch")

    for trigger_name in (
        "trg_runs_session_insert",
        "trg_runs_session_update",
        "trg_run_events_run_insert",
        "trg_run_events_run_update",
        "trg_runs_delete_events",
        "trg_sessions_delete_runs",
    ):
        await conn.execute(text(f"DROP TRIGGER IF EXISTS {trigger_name}"))
    await conn.execute(text("DROP TABLE run_events"))
    await conn.execute(text("DROP TABLE runs"))
    await conn.execute(text("ALTER TABLE _runs_upgrade_v1 RENAME TO runs"))
    await conn.execute(
        text("ALTER TABLE _run_events_upgrade_v1 RENAME TO run_events")
    )
    await conn.execute(
        text("CREATE INDEX ix_runs_claim ON runs(status, lease_expires_at, created_at)")
    )
    await conn.execute(
        text("CREATE INDEX ix_runs_session_created ON runs(session_id, created_at)")
    )
    await conn.execute(
        text(
            "CREATE UNIQUE INDEX uq_runs_session_active ON runs(session_id) "
            "WHERE status IN ('PENDING', 'RUNNING', 'RECONCILING')"
        )
    )
    await conn.execute(
        text(
            "CREATE UNIQUE INDEX uq_runs_upload_idempotency "
            "ON runs(idempotency_key) "
            "WHERE kind = 'upload_pipeline' AND idempotency_key IS NOT NULL"
        )
    )
    await conn.execute(
        text(
            "CREATE TRIGGER trg_runs_session_insert "
            "BEFORE INSERT ON runs FOR EACH ROW "
            "WHEN NOT EXISTS (SELECT 1 FROM research_sessions "
            "WHERE session_id = NEW.session_id) "
            "BEGIN SELECT RAISE(ABORT, 'run session does not exist'); END"
        )
    )
    await conn.execute(
        text(
            "CREATE TRIGGER trg_runs_session_update "
            "BEFORE UPDATE OF session_id ON runs FOR EACH ROW "
            "WHEN NOT EXISTS (SELECT 1 FROM research_sessions "
            "WHERE session_id = NEW.session_id) "
            "BEGIN SELECT RAISE(ABORT, 'run session does not exist'); END"
        )
    )
    await conn.execute(
        text(
            "CREATE TRIGGER trg_run_events_run_insert "
            "BEFORE INSERT ON run_events FOR EACH ROW "
            "WHEN NOT EXISTS (SELECT 1 FROM runs WHERE run_id = NEW.run_id) "
            "BEGIN SELECT RAISE(ABORT, 'run event parent does not exist'); END"
        )
    )
    await conn.execute(
        text(
            "CREATE TRIGGER trg_run_events_run_update "
            "BEFORE UPDATE OF run_id ON run_events FOR EACH ROW "
            "WHEN NOT EXISTS (SELECT 1 FROM runs WHERE run_id = NEW.run_id) "
            "BEGIN SELECT RAISE(ABORT, 'run event parent does not exist'); END"
        )
    )
    await conn.execute(
        text(
            "CREATE TRIGGER trg_runs_delete_events "
            "AFTER DELETE ON runs FOR EACH ROW "
            "BEGIN DELETE FROM run_events WHERE run_id = OLD.run_id; END"
        )
    )
    await conn.execute(
        text(
            "CREATE TRIGGER trg_sessions_delete_runs "
            "AFTER DELETE ON research_sessions FOR EACH ROW "
            "BEGIN DELETE FROM runs WHERE session_id = OLD.session_id; END"
        )
    )
    for _type, name, sql in preserved_objects:
        if str(name) not in managed_names:
            await conn.execute(text(str(sql)))

    foreign_key_issues = list(await conn.execute(text("PRAGMA foreign_key_check")))
    if foreign_key_issues:
        raise RuntimeError(
            "run schema upgrade aborted: rebuilt lifecycle foreign keys are invalid"
        )
    await conn.execute(
        text(
            "INSERT OR IGNORE INTO data_migrations (name, applied_at) "
            "VALUES (:name, CURRENT_TIMESTAMP)"
        ),
        {"name": _RUN_SCHEMA_MIGRATION},
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Create all tables defined by ``Base`` subclasses.

    Called during application startup (lifespan).
    """
    import models  # noqa: F401 -- register every ORM table before create_all

    async with _engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            await conn.execute(
                text("SELECT pg_advisory_xact_lock(:lock_id)"),
                {"lock_id": 7302194502},
            )
        await conn.run_sync(Base.metadata.create_all)
    from session_migration import migrate_legacy_sessions

    await migrate_legacy_sessions()
    # Import legacy sessions before validating Run -> Session references. A
    # run whose parent still exists in sessions.json must not be misclassified
    # as a legacy orphan during the schema upgrade.
    async with _engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            await conn.execute(
                text("SELECT pg_advisory_xact_lock(:lock_id)"),
                {"lock_id": 7302194502},
            )
        await _ensure_run_lifecycle_constraints(conn)
    url = make_url(settings.DATABASE_URL)
    if url.get_backend_name() == "sqlite" and url.database:
        ensure_private_file(Path(url.database))


async def drop_tables() -> None:
    """Drop all tables (used in tests)."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

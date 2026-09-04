"""One-time import of the legacy JSON session store into the database."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy import select, text

from config import settings
from database import session_factory
from models.research_session import DataMigration, ResearchSession, SessionDegradation


_MIGRATION_NAME = "legacy-json-sessions-v1"
_RESERVED_ENTRY_FIELDS = {"state", "csv_path", "user_id"}


async def migrate_legacy_sessions() -> None:
    """Import legacy JSON once; PostgreSQL/SQLite remains authoritative after it."""
    path = Path(settings.SESSIONS_PATH)

    async with session_factory()() as db:
        if await db.get(DataMigration, _MIGRATION_NAME) is not None:
            return

    data: dict = {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded
    except FileNotFoundError:
        pass
    except (json.JSONDecodeError, UnicodeError) as exc:
        print(
            f"⚠ Session migration: failed to read {path} ({exc}); "
            "backing it up and continuing with the database",
            file=sys.stderr,
        )
        try:
            path.rename(path.with_suffix(path.suffix + ".corrupt"))
        except FileNotFoundError:
            pass

    async with session_factory()() as db:
        dialect = db.bind.dialect.name if db.bind is not None else ""
        if dialect == "sqlite":
            # Reserve SQLite's single writer before rechecking the marker so
            # concurrent API/runner startup cannot both import the same file.
            await db.execute(text("BEGIN IMMEDIATE"))
        else:
            await db.begin()
        try:
            if dialect == "postgresql":
                await db.execute(
                    text("SELECT pg_advisory_xact_lock(:lock_id)"),
                    {"lock_id": 7302194503},
                )
            if await db.get(DataMigration, _MIGRATION_NAME) is not None:
                await db.rollback()
                return

            sessions = data.get("sessions") or {}
            if isinstance(sessions, dict):
                existing_session_ids: set[str] = set()
                if sessions:
                    existing_session_ids = set(
                        await db.scalars(
                            select(ResearchSession.session_id).where(
                                ResearchSession.session_id.in_(list(sessions))
                            )
                        )
                    )
                for session_id, raw_entry in sessions.items():
                    if not isinstance(session_id, str) or not isinstance(raw_entry, dict):
                        continue
                    if session_id in existing_session_ids:
                        continue
                    state = dict(raw_entry.get("state") or {})
                    state_csv_path = state.pop("csv_path", None)
                    csv_path = raw_entry.get("csv_path") or state_csv_path
                    metadata = {
                        key: value
                        for key, value in raw_entry.items()
                        if key not in _RESERVED_ENTRY_FIELDS
                    }
                    db.add(
                        ResearchSession(
                            session_id=session_id,
                            user_id=raw_entry.get("user_id"),
                            state=state,
                            csv_path=csv_path,
                            metadata_json=metadata,
                        )
                    )

            degradations = data.get("degradations") or {}
            if isinstance(degradations, dict):
                for session_id, records in degradations.items():
                    if not isinstance(session_id, str) or not isinstance(records, list):
                        continue
                    for payload in records:
                        if isinstance(payload, dict):
                            db.add(
                                SessionDegradation(
                                    session_id=session_id,
                                    payload=payload,
                                )
                            )

            db.add(DataMigration(name=_MIGRATION_NAME))
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    try:
        path.rename(path.with_suffix(path.suffix + ".migrated"))
    except FileNotFoundError:
        pass

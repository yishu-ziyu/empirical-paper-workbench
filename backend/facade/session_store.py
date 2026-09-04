"""Database-backed session state used by the synchronous agent facade.

Every call reads or writes the shared SQL database. There is deliberately no
process cache: API workers and the independent run worker must observe the same
session state without a hydration request or sticky routing.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import delete, select, text

from config import settings
from database import sync_session_factory
from models.research_session import ResearchSession, SessionDegradation


class SessionStore:
    """Synchronous facade over durable session and degradation tables."""

    def __init__(self) -> None:
        self._factory = sync_session_factory()

    @staticmethod
    def _project_state(row: ResearchSession) -> dict:
        state = dict(row.state or {})
        if row.csv_path:
            state["csv_path"] = row.csv_path
        return state

    @staticmethod
    def _write_state(row: ResearchSession, state: dict) -> None:
        stored = dict(state)
        if "csv_path" in stored:
            csv_path = stored.pop("csv_path")
            row.csv_path = str(csv_path) if csv_path else None
        row.state = stored

    @staticmethod
    def _entry(row: ResearchSession) -> dict:
        state = dict(row.state or {})
        entry = {
            **dict(row.metadata_json or {}),
            "state": state,
            "csv_path": row.csv_path,
            "user_id": row.user_id,
        }
        if "charls_config" in state:
            entry["charls_config"] = state["charls_config"]
        return entry

    def _locked_row(self, db, session_id: str) -> ResearchSession:
        row = db.scalar(
            select(ResearchSession)
            .where(ResearchSession.session_id == session_id)
            .with_for_update()
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return row

    def _locked_row_or_create(self, db, session_id: str) -> ResearchSession:
        row = db.scalar(
            select(ResearchSession)
            .where(ResearchSession.session_id == session_id)
            .with_for_update()
        )
        if row is None:
            row = ResearchSession(session_id=session_id)
            db.add(row)
        return row

    def has(self, session_id: str) -> bool:
        with self._factory() as db:
            return db.get(ResearchSession, session_id) is not None

    def create(self, session_id: str, user_id: Optional[int]) -> str:
        with self._factory.begin() as db:
            row = db.get(ResearchSession, session_id)
            if row is None:
                db.add(ResearchSession(session_id=session_id, user_id=user_id))
            else:
                row.user_id = user_id
                row.state = {}
                row.csv_path = None
                row.metadata_json = {}
        return session_id

    def get_owner(self, session_id: str) -> Optional[int]:
        with self._factory() as db:
            row = db.get(ResearchSession, session_id)
            return None if row is None else row.user_id

    def list_by_user(self, user_id: int) -> list[str]:
        with self._factory() as db:
            return list(
                db.scalars(
                    select(ResearchSession.session_id)
                    .where(ResearchSession.user_id == user_id)
                    .order_by(ResearchSession.created_at)
                )
            )

    def list_summaries_by_user(self, user_id: int) -> list[tuple[str, bool]]:
        """Return list-view fields in one query without path recovery I/O."""
        with self._factory() as db:
            rows = db.execute(
                select(ResearchSession.session_id, ResearchSession.csv_path)
                .where(ResearchSession.user_id == user_id)
                .order_by(ResearchSession.created_at)
            )
            return [(session_id, bool(csv_path)) for session_id, csv_path in rows]

    def delete(self, session_id: str) -> bool:
        with self._factory() as db:
            if db.bind is not None and db.bind.dialect.name == "sqlite":
                # Match RunRepository's BEGIN IMMEDIATE admission lock. SQLite
                # otherwise lets both processes read the live session before
                # one fails while upgrading its deferred write transaction.
                db.execute(text("BEGIN IMMEDIATE"))
            try:
                row = db.get(ResearchSession, session_id)
                if row is None:
                    db.rollback()
                    return False
                db.delete(row)
                db.execute(
                    delete(SessionDegradation).where(
                        SessionDegradation.session_id == session_id
                    )
                )
                db.commit()
                return True
            except Exception:
                db.rollback()
                raise

    def get_state(self, session_id: str) -> dict:
        with self._factory() as db:
            row = db.get(ResearchSession, session_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Session not found")
            return self._project_state(row)

    def save_state(self, session_id: str, state: dict) -> None:
        with self._factory.begin() as db:
            self._write_state(self._locked_row(db, session_id), state)

    def update_state(self, session_id: str, **fields) -> dict:
        with self._factory.begin() as db:
            row = self._locked_row(db, session_id)
            state = {**self._project_state(row), **fields}
            self._write_state(row, state)
            return self._project_state(row)

    def save_entry(self, session_id: str, *, state: dict, csv_path: str) -> dict:
        """Atomically persist upload output and its dataset path."""
        with self._factory.begin() as db:
            row = self._locked_row_or_create(db, session_id)
            self._write_state(row, state)
            row.csv_path = csv_path
            return self._project_state(row)

    def get_entry(self, session_id: str) -> dict:
        with self._factory() as db:
            row = db.get(ResearchSession, session_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Session not found")
            return self._entry(row)

    def get_csv_path(self, session_id: str) -> str:
        entry = self.get_entry(session_id)
        csv_path = entry.get("csv_path")
        if not csv_path:
            datasets = (entry.get("state") or {}).get("uploaded_datasets", []) or []
            if datasets and datasets[0].get("path"):
                csv_path = datasets[0]["path"]
        if not csv_path:
            raise HTTPException(status_code=400, detail="No dataset path in session")

        if not os.path.exists(csv_path) and settings.S3_ENDPOINT_URL:
            try:
                from storage.s3 import s3_fs as _s3_fs

                remote = f"{session_id}/data.csv"
                if _s3_fs.exists(remote):
                    cache_dir = Path(settings.S3_CACHE_DIR)
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    local_cache = cache_dir / f"{session_id}.csv"
                    _s3_fs.download_to_file(remote, local_cache)
                    csv_path = str(local_cache)
            except Exception:
                pass
        return csv_path

    def set_csv_path(self, session_id: str, csv_path: str) -> None:
        with self._factory.begin() as db:
            self._locked_row_or_create(db, session_id).csv_path = csv_path

    def get_datasets(self, session_id: str) -> list:
        entry = self.get_entry(session_id)
        if entry.get("csv_path"):
            return [{"path": entry["csv_path"]}]
        return list((entry.get("state") or {}).get("uploaded_datasets", []) or [])

    def save_datasets(self, session_id: str, datasets: list) -> None:
        self.update_state(session_id, uploaded_datasets=datasets)

    def record_degradation(
        self,
        session_id: str,
        node: str,
        reason: str,
        fallback: str,
        visible: bool = False,
    ) -> None:
        payload = {
            "node": node,
            "reason": reason,
            "fallback": fallback,
            "visible": visible,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._factory.begin() as db:
            db.add(SessionDegradation(session_id=session_id, payload=payload))

    def get_degradations(self, session_id: str) -> list[dict]:
        with self._factory() as db:
            rows = db.scalars(
                select(SessionDegradation)
                .where(SessionDegradation.session_id == session_id)
                .order_by(SessionDegradation.id)
            )
            return [dict(row.payload or {}) for row in rows]

    def clear_degradations(self, session_id: str) -> None:
        with self._factory.begin() as db:
            db.execute(
                delete(SessionDegradation).where(
                    SessionDegradation.session_id == session_id
                )
            )

    def seed(self, session_id: str, state: dict) -> None:
        with self._factory.begin() as db:
            row = db.get(ResearchSession, session_id)
            if row is None:
                row = ResearchSession(session_id=session_id)
                db.add(row)
            else:
                row.user_id = None
                row.csv_path = None
                row.metadata_json = {}
            self._write_state(row, state)

    def drop(self, session_id: str) -> None:
        self.delete(session_id)

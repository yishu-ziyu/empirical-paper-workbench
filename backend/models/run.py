"""Durable execution records for long-running research work."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('prewrite', 'upload_pipeline', 'spec_run')",
            name="ck_runs_supported_kind",
        ),
        Index("ix_runs_claim", "status", "lease_expires_at", "created_at"),
        Index("ix_runs_session_created", "session_id", "created_at"),
        UniqueConstraint(
            "session_id",
            "kind",
            "idempotency_key",
            name="uq_runs_idempotency",
        ),
        Index(
            "uq_runs_upload_idempotency",
            "idempotency_key",
            unique=True,
            postgresql_where=text(
                "kind = 'upload_pipeline' AND idempotency_key IS NOT NULL"
            ),
            sqlite_where=text(
                "kind = 'upload_pipeline' AND idempotency_key IS NOT NULL"
            ),
        ),
        Index(
            "uq_runs_session_active",
            "session_id",
            unique=True,
            postgresql_where=text(
                "status IN ('PENDING', 'RUNNING', 'RECONCILING')"
            ),
            sqlite_where=text("status IN ('PENDING', 'RUNNING', 'RECONCILING')"),
        ),
    )

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "research_sessions.session_id",
            name="fk_runs_session",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="PENDING")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(200), nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lease_owner: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lease_epoch: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_event_seq: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class RunEvent(Base):
    __tablename__ = "run_events"

    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("runs.run_id", name="fk_run_events_run", ondelete="CASCADE"),
        primary_key=True,
    )
    seq: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

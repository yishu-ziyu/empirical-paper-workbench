"""User ORM model for authentication and session ownership."""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from database import Base


def _utc_naive() -> datetime:
    # Existing user columns are TIMESTAMP WITHOUT TIME ZONE. asyncpg rejects
    # aware values for that schema; store UTC consistently without a migration.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    """Registered user of the econpaper application."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(
        String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime,
        default=_utc_naive,
    )
    updated_at = Column(
        DateTime,
        default=_utc_naive,
        onupdate=_utc_naive,
    )
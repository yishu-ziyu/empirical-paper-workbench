"""SQLAlchemy async engine factory and session dependency.

Uses :attr:`config.settings.DATABASE_URL`. Defaults to SQLite for local
development; switch to ``postgresql+asyncpg://...`` for production.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import AsyncIterator

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import ensure_private_file, settings

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

_async_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


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
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    url = make_url(settings.DATABASE_URL)
    if url.get_backend_name() == "sqlite" and url.database:
        ensure_private_file(Path(url.database))


async def drop_tables() -> None:
    """Drop all tables (used in tests)."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

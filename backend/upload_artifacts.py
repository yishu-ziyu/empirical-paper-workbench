"""Crash-convergent local storage for normalized upload inputs."""

from __future__ import annotations

import asyncio
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from config import ensure_private_directory, ensure_private_file, settings
from database import session_factory
from models.research_session import ResearchSession


RECONCILE_INTERVAL_SECONDS = 15 * 60
RECONCILE_GRACE_SECONDS = 15 * 60
_UUID_CSV = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\.csv$",
    re.IGNORECASE,
)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def publish_normalized_upload(
    csv_bytes: bytes,
    *,
    session_id: str,
    upload_dir: Path | None = None,
) -> Path:
    """Durably publish bytes before database admission.

    A private attempt is flushed first, then atomically promoted to the
    canonical Session filename. The caller owns cleanup until admission wins.
    """
    root = Path(upload_dir or settings.UPLOAD_DIR)
    ensure_private_directory(root)
    staging = root / ".staging"
    ensure_private_directory(staging)
    attempt = staging / f"{uuid.uuid4()}.csv"
    target = root / f"{session_id}.csv"
    promoted = False

    try:
        with attempt.open("xb") as handle:
            handle.write(csv_bytes)
            handle.flush()
            os.fsync(handle.fileno())
        ensure_private_file(attempt)
        # link(2) publishes a complete inode atomically and refuses to clobber
        # even in the practically impossible event of a Session UUID collision.
        os.link(attempt, target)
        promoted = True
        attempt.unlink()
        ensure_private_file(target)
        _fsync_directory(root)
        return target
    except Exception:
        remove_owned_upload(attempt, upload_dir=root)
        if promoted:
            remove_owned_upload(target, upload_dir=root)
        raise


def remove_owned_upload(path: Path, *, upload_dir: Path | None = None) -> bool:
    """Remove only a managed CSV contained by UPLOAD_DIR."""
    root = Path(upload_dir or settings.UPLOAD_DIR).resolve()
    try:
        resolved = path.resolve(strict=False)
        if not resolved.is_relative_to(root):
            return False
        relative = resolved.relative_to(root)
        if len(relative.parts) == 1:
            managed = bool(_UUID_CSV.fullmatch(relative.name))
        else:
            managed = (
                len(relative.parts) == 2
                and relative.parts[0] == ".staging"
                and bool(_UUID_CSV.fullmatch(relative.name))
            )
        if not managed or path.is_symlink():
            return False
        path.unlink(missing_ok=True)
        return True
    except (OSError, RuntimeError, ValueError):
        return False


async def referenced_upload_paths() -> set[Path]:
    """Read authoritative Session references from the primary database."""
    factory = session_factory()
    async with factory() as db:
        rows = await db.execute(
            select(ResearchSession.csv_path, ResearchSession.state)
        )
        referenced: set[Path] = set()
        for csv_path, state in rows:
            raw_paths: list[object] = [csv_path]
            if isinstance(state, dict):
                raw_paths.append(state.get("csv_path"))
                raw_paths.extend(
                    item.get("path")
                    for item in (state.get("uploaded_datasets") or [])
                    if isinstance(item, dict)
                )
            referenced.update(
                Path(raw).resolve(strict=False)
                for raw in raw_paths
                if isinstance(raw, str) and raw
            )
        return referenced


def reconcile_upload_files(
    referenced: set[Path],
    *,
    upload_dir: Path | None = None,
    now: datetime | None = None,
    grace_seconds: float = RECONCILE_GRACE_SECONDS,
) -> list[Path]:
    """Delete old, unreferenced managed files without crossing UPLOAD_DIR."""
    root = Path(upload_dir or settings.UPLOAD_DIR)
    if not root.exists():
        return []
    root_resolved = root.resolve()
    cutoff = (now or datetime.now(timezone.utc)).timestamp() - grace_seconds
    normalized_refs = {path.resolve(strict=False) for path in referenced}
    candidates = list(root.glob("*.csv")) + list((root / ".staging").glob("*.csv"))
    removed: list[Path] = []
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=False)
            if not resolved.is_relative_to(root_resolved):
                continue
            if resolved in normalized_refs or candidate.stat().st_mtime > cutoff:
                continue
        except (OSError, RuntimeError, ValueError):
            continue
        if remove_owned_upload(candidate, upload_dir=root):
            removed.append(candidate)
    return removed


async def reconcile_upload_artifacts(
    *,
    upload_dir: Path | None = None,
    now: datetime | None = None,
    grace_seconds: float = RECONCILE_GRACE_SECONDS,
) -> list[Path]:
    referenced = await referenced_upload_paths()
    return await asyncio.to_thread(
        reconcile_upload_files,
        referenced,
        upload_dir=upload_dir,
        now=now,
        grace_seconds=grace_seconds,
    )


async def reconcile_upload_artifacts_forever() -> None:
    while True:
        await asyncio.sleep(RECONCILE_INTERVAL_SECONDS)
        try:
            await reconcile_upload_artifacts()
        except Exception:
            # Reconciliation is convergent maintenance; the next pass retries.
            continue

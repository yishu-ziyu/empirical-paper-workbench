"""TITLE/TOPIC attach + confirm-attach (DC-BE-attach).

Attach binds a user file or classic-5 entry and stamps ingest readiness.
Confirm-attach is the only transition that sets ``data_attached``.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from config import settings
from facade import facade
from run_repository import (
    IdempotencyConflict,
    QueueFull,
    RunRepository,
    SessionBusy,
    SessionNotFound,
    UploadAdmission,
    finalize_upload_fingerprint,
)
from schemas.responses import DatasetMetaResponse
from services.classic5 import classic5_candidate, resolve_classic5_entry
from upload_artifacts import publish_normalized_upload, remove_owned_upload


BLOCKED_READINESS = frozenset({"PROCESSING", "FAILED", "CANCELLED"})


def user_file_candidate() -> dict[str, object]:
    return {"source": "user_file"}


def replace_normalized_upload(
    csv_bytes: bytes,
    *,
    session_id: str,
    upload_dir: Path | None = None,
) -> Path:
    """Publish canonical bytes, replacing a prior session CSV if present."""
    root = Path(upload_dir or settings.UPLOAD_DIR)
    target = root / f"{session_id}.csv"
    if target.exists():
        remove_owned_upload(target, upload_dir=root)
    return publish_normalized_upload(
        csv_bytes,
        session_id=session_id,
        upload_dir=root,
    )


def _upload_not_ready(readiness: object) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={
            "code": "upload_not_ready",
            "upload_readiness": readiness,
        },
    )


def _session_busy(run_id: str) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={"code": "session_busy", "run_id": run_id},
    )


def _no_candidate() -> HTTPException:
    return HTTPException(status_code=409, detail={"code": "no_candidate"})


def require_ingest_ready(state: dict[str, Any], *, has_dataset: bool) -> None:
    """Fail closed unless upload-era/classic-5-era ingest is READY + bound."""
    readiness = state.get("upload_readiness")
    if readiness in BLOCKED_READINESS or readiness != "READY" or not has_dataset:
        raise _upload_not_ready(readiness)


async def _active_run_id(session_id: str) -> str | None:
    run = await RunRepository().active_run(session_id)
    return None if run is None else run.run_id


async def stamp_user_file_candidate(session_id: str) -> dict[str, Any]:
    """Record the existing upload as the candidate. Never sets dataAttached."""
    try:
        csv_path = await run_in_threadpool(facade.get_csv_path, session_id)
    except Exception:
        csv_path = None
    if not csv_path:
        raise _no_candidate()
    active = await _active_run_id(session_id)
    if active is not None:
        # Re-bind while a run is in flight is refused; client reattaches to it.
        raise _session_busy(active)
    state = await run_in_threadpool(facade.get_state, session_id)
    readiness = state.get("upload_readiness")
    if readiness in {"FAILED", "CANCELLED"}:
        raise _upload_not_ready(readiness)
    updated = await run_in_threadpool(
        facade.update_state,
        session_id,
        data_attached=False,
        attach_candidate=user_file_candidate(),
    )
    return updated


async def admit_bound_bytes(
    *,
    session_id: str,
    user_id: int | None,
    csv_bytes: bytes,
    dataset_meta: DatasetMetaResponse,
    filename: str,
    candidate: dict[str, Any],
    idempotency_key: str,
) -> tuple[UploadAdmission, bytes]:
    """Bind normalized bytes onto an existing session via upload_pipeline."""
    fingerprint = finalize_upload_fingerprint(hashlib.sha256(csv_bytes), filename)
    csv_path: Path | None = None
    try:
        csv_path = await run_in_threadpool(
            replace_normalized_upload,
            csv_bytes,
            session_id=session_id,
            upload_dir=Path(settings.UPLOAD_DIR),
        )
        admission = await RunRepository().admit_session_upload(
            session_id=session_id,
            user_id=user_id,
            csv_path=str(csv_path),
            dataset_meta=dataset_meta.model_dump(),
            extra_state={
                "attach_candidate": candidate,
                "data_attached": False,
            },
            idempotency_key=idempotency_key,
            input_fingerprint=fingerprint,
        )
    except IdempotencyConflict as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise HTTPException(status_code=409, detail="upload_request_conflict") from exc
    except QueueFull as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise HTTPException(
            status_code=429,
            detail="run queue is full",
            headers={"Retry-After": "5"},
        ) from exc
    except SessionBusy as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise _session_busy(exc.run_id) from exc
    except SessionNotFound as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise HTTPException(status_code=404, detail="Session not found") from exc
    except HTTPException:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise
    except Exception as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise HTTPException(status_code=500, detail="upload_admission_failed") from exc

    if admission.replayed and csv_path is not None:
        remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
    return admission, csv_bytes


async def attach_classic5(
    *,
    session_id: str,
    user_id: int | None,
    entry_id: str,
    idempotency_key: str,
) -> UploadAdmission:
    from routers.sessions import _normalize_dataframe, _read_tabular_upload

    path = resolve_classic5_entry(entry_id)

    def _load() -> tuple[bytes, DatasetMetaResponse]:
        with path.open("rb") as handle:
            df = _read_tabular_upload(handle, path.name)
        if len(df.columns) == 0:
            raise HTTPException(status_code=400, detail="No columns detected in file")
        return _normalize_dataframe(df, path.name)

    try:
        csv_bytes, dataset_meta = await run_in_threadpool(_load)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unsupported or corrupted data file",
        ) from exc

    admission, _ = await admit_bound_bytes(
        session_id=session_id,
        user_id=user_id,
        csv_bytes=csv_bytes,
        dataset_meta=dataset_meta,
        filename=path.name,
        candidate=classic5_candidate(entry_id),
        idempotency_key=idempotency_key,
    )
    return admission


async def attach_user_file_bytes(
    *,
    session_id: str,
    user_id: int | None,
    file: UploadFile,
    idempotency_key: str,
    request,
) -> UploadAdmission:
    from routers.sessions import (
        _max_upload_bytes,
        _normalize_dataframe,
        _read_tabular_upload,
        _reject_if_content_length_too_large,
        _scan_upload,
    )

    max_bytes = _max_upload_bytes()
    _reject_if_content_length_too_large(request, max_bytes)
    size, _fingerprint = await _scan_upload(file, max_bytes)
    if not size:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        df = await run_in_threadpool(
            _read_tabular_upload,
            file.file,
            file.filename or "",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unsupported or corrupted data file",
        ) from exc
    if len(df.columns) == 0:
        raise HTTPException(status_code=400, detail="No columns detected in file")
    csv_bytes, dataset_meta = await run_in_threadpool(
        _normalize_dataframe, df, file.filename or ""
    )
    admission, _ = await admit_bound_bytes(
        session_id=session_id,
        user_id=user_id,
        csv_bytes=csv_bytes,
        dataset_meta=dataset_meta,
        filename=file.filename or "upload.csv",
        candidate=user_file_candidate(),
        idempotency_key=idempotency_key,
    )
    return admission


async def confirm_attach(session_id: str) -> dict[str, Any]:
    """Set dataAttached only when ingest is READY and a dataset is bound."""
    active = await _active_run_id(session_id)
    if active is not None:
        raise _session_busy(active)
    try:
        csv_path = await run_in_threadpool(facade.get_csv_path, session_id)
    except Exception:
        csv_path = None
    has_dataset = bool(csv_path)
    state = await run_in_threadpool(facade.get_state, session_id)
    if not has_dataset:
        raise _no_candidate()
    require_ingest_ready(state, has_dataset=True)
    return await run_in_threadpool(
        facade.update_state,
        session_id,
        data_attached=True,
    )

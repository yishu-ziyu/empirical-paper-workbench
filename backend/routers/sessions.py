"""REST endpoints for sessions.

T-02 backend layer: multipart CSV upload, session creation, and tex export.
Session metadata and state are persisted through the facade into the shared
application database.

F10: Session ownership is tracked via user_id. Authenticated endpoints
check that the requesting user owns the session.
"""
from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import BinaryIO, List, Optional

import pandas as pd
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Header,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import PlainTextResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool

from auth import (
    get_optional_user,
    get_current_user,
    require_auth_unless_debug,
    require_session_ownership,
)
from config import settings
from facade import facade
from models.user import User
from run_repository import (
    IdempotencyConflict,
    QueueFull,
    RunRepository,
    finalize_upload_fingerprint,
)
from routers.run_execution import public_degradations, public_instrument_fields
from storage.s3 import s3_fs
from schemas.responses import (
    CreateSessionResponse,
    DatasetMetaResponse,
    SessionInfoResponse,
    UploadResponse,
)
from upload_artifacts import publish_normalized_upload, remove_owned_upload

router = APIRouter()


def _max_upload_bytes() -> int:
    return settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def _read_tabular_upload(source: BinaryIO, filename: str) -> pd.DataFrame:
    """按文件内容识别格式并读成 DataFrame（CSV / Stata .dta / Excel .xlsx）。

    内容嗅探优先、文件名兜底：xlsx 是 zip 容器（PK 头），Stata 117+ 有
    ``<stata_dta>`` 文本头，旧版 dta（≤115）只能靠后缀兜底；其余按 CSV
    处理并做 GBK 回退（中文 Excel 导出的 CSV 默认 GBK）。
    """
    source.seek(0)
    header = source.read(11)
    source.seek(0)
    if header[:2] == b"PK":
        return pd.read_excel(source, sheet_name=0)
    if header == b"<stata_dta>":
        return pd.read_stata(source)
    if filename.lower().endswith(".dta"):
        return pd.read_stata(source)
    last_exc: Exception | None = None
    for enc in ("utf-8-sig", "gb18030"):
        try:
            source.seek(0)
            return pd.read_csv(source, encoding=enc)
        except UnicodeDecodeError as exc:
            last_exc = exc
    raise ValueError(f"unrecognized or corrupted data file: {last_exc}") from last_exc


def _reject_if_content_length_too_large(request: Request, max_bytes: int) -> None:
    """Reject oversized bodies from Content-Length before reading the file."""
    raw = request.headers.get("content-length")
    if not raw:
        return
    try:
        length = int(raw)
    except ValueError:
        return
    if length > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB upload limit",
        )


async def _scan_upload(file: UploadFile, max_bytes: int) -> tuple[int, str]:
    """Bound upload memory while counting bytes and hashing the spooled body."""
    digest = hashlib.sha256()
    size = 0
    while chunk := await file.read(1024 * 1024):
        size += len(chunk)
        if size > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB upload limit",
            )
        digest.update(chunk)
    await file.seek(0)
    return size, finalize_upload_fingerprint(digest, file.filename or "")


# ---------------------------------------------------------------------------
# Upload (creates a session)
# ---------------------------------------------------------------------------


def _validated_upload_key(raw: str | None) -> str:
    if raw is None:
        raise HTTPException(status_code=422, detail="invalid_idempotency_key")
    try:
        parsed = uuid.UUID(raw)
    except (ValueError, AttributeError) as exc:
        raise HTTPException(status_code=422, detail="invalid_idempotency_key") from exc
    if parsed.version != 4 or parsed.variant != uuid.RFC_4122:
        raise HTTPException(status_code=422, detail="invalid_idempotency_key")
    return str(parsed)


def _dataset_meta(df: pd.DataFrame) -> DatasetMetaResponse:
    return DatasetMetaResponse(
        columns=[str(column) for column in df.columns],
        rows=int(len(df)),
        dtypes={str(column): str(dtype) for column, dtype in df.dtypes.items()},
        missing_count=int(df.isna().sum().sum()),
    )


def _normalize_dataframe(df: pd.DataFrame) -> tuple[bytes, DatasetMetaResponse]:
    """Serialize and profile a parsed table away from the API event loop."""
    return df.to_csv(index=False).encode("utf-8"), _dataset_meta(df)


def _upload_response(admission) -> UploadResponse:
    metadata = dict(admission.session.metadata_json or {})
    return UploadResponse(
        session_id=admission.session.session_id,
        run_id=admission.run.run_id,
        status="PENDING",
        events_url=f"/api/runs/{admission.run.run_id}/events",
        dataset_meta=DatasetMetaResponse(
            columns=[str(item) for item in metadata.get("columns") or []],
            rows=metadata.get("rows"),
            dtypes=dict(metadata.get("dtypes") or {}),
            missing_count=metadata.get("missing_count"),
        ),
    )


def _sync_upload_to_s3(session_id: str, csv_bytes: bytes) -> None:
    remote_path = f"{session_id}/data.csv"
    try:
        s3_fs.upload_bytes(csv_bytes, remote_path)
    except Exception:
        # The Session foreign key is authoritative. If deletion wins this
        # race, do not recreate any lifecycle residue for the dead Session.
        try:
            if facade.has_session(session_id):
                facade.record_degradation(
                    session_id,
                    "upload",
                    "remote_storage_unavailable",
                    "local_fs",
                    visible=True,
                )
        except Exception:
            pass
        return

    # Deletion may have completed while put_object was in flight. A second,
    # idempotent delete closes that publication race.
    if not facade.has_session(session_id):
        try:
            s3_fs.delete(remote_path)
        except Exception:
            pass


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=202,
    responses={
        409: {"description": "Idempotency key was reused for different input"},
        429: {
            "description": "The durable run queue is full",
            "headers": {
                "Retry-After": {
                    "description": "Seconds before retrying admission",
                    "schema": {"type": "string"},
                }
            },
        },
    },
)
async def upload(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    current_user: Optional[User] = Depends(get_optional_user),
) -> UploadResponse:
    """Persist an upload command and return before cleaning begins."""
    key = _validated_upload_key(idempotency_key)
    require_auth_unless_debug(current_user)
    max_bytes = _max_upload_bytes()
    _reject_if_content_length_too_large(request, max_bytes)

    # 1. Scan the framework's spooled upload in bounded chunks before parsing.
    size, fingerprint = await _scan_upload(file, max_bytes)
    if not size:
        raise HTTPException(status_code=400, detail="Empty file")

    # 2. Parse by content sniffing (CSV / .dta / .xlsx, GBK fallback for CSV).
    try:
        df = await run_in_threadpool(
            _read_tabular_upload,
            file.file,
            file.filename or "",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unsupported or corrupted data file",
        )
    if len(df.columns) == 0:
        raise HTTPException(status_code=400, detail="No columns detected in file")

    # 2b. Normalize to a canonical in-house CSV so every downstream stage
    #     (profiling, cleaning, code export) only ever faces a CSV.
    csv_bytes, dataset_meta = await run_in_threadpool(_normalize_dataframe, df)
    session_id = str(uuid.uuid4())
    user_id = current_user.id if current_user else None
    csv_path: Path | None = None
    try:
        csv_path = await run_in_threadpool(
            publish_normalized_upload,
            csv_bytes,
            session_id=session_id,
            upload_dir=Path(settings.UPLOAD_DIR),
        )
        initial_state = {
            "session_id": session_id,
            "csv_path": str(csv_path),
            "uploaded_datasets": [{"path": str(csv_path), "format": "csv"}],
        }
        admission = await RunRepository().admit_upload(
            session_id=session_id,
            user_id=user_id,
            csv_path=str(csv_path),
            dataset_meta=dataset_meta.model_dump(),
            initial_state=initial_state,
            idempotency_key=key,
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
    except Exception as exc:
        if csv_path is not None:
            remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
        raise HTTPException(status_code=500, detail="upload_admission_failed") from exc

    if admission.replayed:
        remove_owned_upload(csv_path, upload_dir=Path(settings.UPLOAD_DIR))
    elif settings.S3_ENDPOINT_URL:
        background_tasks.add_task(
            _sync_upload_to_s3,
            admission.session.session_id,
            csv_bytes,
        )
    return _upload_response(admission)


@router.post(
    "/upload/resolve",
    response_model=UploadResponse,
    status_code=202,
    responses={
        404: {"description": "No upload is visible for this capability"},
        503: {"description": "Upload resolution is temporarily unavailable"},
    },
)
async def resolve_upload(
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    current_user: Optional[User] = Depends(get_optional_user),
) -> UploadResponse:
    """Resolve a committed upload after the accepting response was lost."""
    key = _validated_upload_key(idempotency_key)
    if current_user is None and not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Upload not found")
    try:
        admission = await RunRepository().resolve_upload(
            key,
            user_id=current_user.id if current_user else None,
            allow_anonymous_capability=settings.DEBUG,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="upload_resolution_unavailable") from exc
    if admission is None:
        raise HTTPException(status_code=404, detail="Upload not found")
    return _upload_response(admission)


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    current_user: Optional[User] = Depends(get_optional_user),
) -> CreateSessionResponse:
    """Create an empty session (no upload).

    If the user is authenticated, the session is owned by that user.
    """
    user_id = current_user.id if current_user else None
    session_id = await run_in_threadpool(facade.create_session, user_id=user_id)
    return CreateSessionResponse(session_id=session_id)


@router.get("/sessions", response_model=List[SessionInfoResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
) -> list[SessionInfoResponse]:
    """Return all sessions owned by the current user."""
    summaries = await run_in_threadpool(
        facade.list_session_summaries_by_user,
        current_user.id,
    )
    return [
        SessionInfoResponse(
            session_id=session_id,
            exists=True,
            has_dataset=has_dataset,
        )
        for session_id, has_dataset in summaries
    ]


@router.get("/sessions/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionInfoResponse:
    """Return session existence and basic info.

    Used by the frontend to verify a saved sessionId is still valid
    after a page refresh (localStorage recovery flow).
    """
    await run_in_threadpool(require_session_ownership, session_id, current_user)
    has_dataset = False
    extra: dict = {}
    try:
        csv_path = await run_in_threadpool(facade.get_csv_path, session_id)
        has_dataset = bool(csv_path)
    except Exception:
        has_dataset = False
    try:
        state = await run_in_threadpool(facade.get_state, session_id)
        extra = public_instrument_fields(state)
        readiness = state.get("upload_readiness")
        if readiness in {"PROCESSING", "READY", "FAILED", "CANCELLED"}:
            extra["upload_readiness"] = readiness
    except Exception:
        extra = {}
    return SessionInfoResponse(
        session_id=session_id,
        exists=True,
        has_dataset=has_dataset,
        **extra,
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete a session owned by the current user."""
    await run_in_threadpool(require_session_ownership, session_id, current_user)
    deleted = await run_in_threadpool(facade.delete_session, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True, "session_id": session_id}


# ---------------------------------------------------------------------------
# Session data
# ---------------------------------------------------------------------------


@router.get("/sessions/{session_id}/degradation")
async def get_degradation(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> dict:
    """Return degradation records for a session."""
    await run_in_threadpool(require_session_ownership, session_id, current_user)
    raw_degradations = await run_in_threadpool(facade.get_degradations, session_id)
    degradations = public_degradations(raw_degradations)
    return {"session_id": session_id, "degradations": degradations}


@router.get("/sessions/{session_id}/export")
async def export(
    session_id: str,
    format: str = "tex",
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Export a session's paper in the requested format.

    When S3 is configured, the export file is uploaded to S3 and the response
    redirects to a presigned download URL.  Without S3, returns the content
    inline as ``PlainTextResponse`` (Stage D 文件下载端点豁免）。
    """
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    state = await run_in_threadpool(facade.get_state, session_id)

    if format == "tex":
        title_chapter = state.get("title_chapter") or {}
        title_content = (
            title_chapter.get("content") or "\\title{Untitled}"
        )
        tex = f"{title_content}\n\\author{{}}\n\\date{{}}\n"
        content_bytes = tex.encode("utf-8")
        filename = f"{session_id}.tex"

        # Upload to S3 if configured, then redirect to presigned URL.
        if settings.S3_ENDPOINT_URL:
            try:
                s3_remote = f"{session_id}/export/{filename}"
                s3_fs.upload_bytes(content_bytes, s3_remote)
                presigned = s3_fs.presigned_url(s3_remote)
                return RedirectResponse(url=presigned)
            except Exception:
                pass  # 降级：直接返回内容

        return PlainTextResponse(content=tex, media_type="application/x-tex")

    raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

"""REST endpoints for sessions.

T-02 backend layer: multipart CSV upload, session creation, and tex export.
Session state is held in the facade's in-memory dict for the dev stage;
production will swap to PostgresSaver (see spec decision 2).

F10: Session ownership is tracked via user_id. Authenticated endpoints
check that the requesting user owns the session.
"""
from __future__ import annotations

import io
import uuid
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse, RedirectResponse

from auth import get_optional_user, get_current_user
from config import settings
from facade import facade
from models.user import User
from storage.s3 import s3_fs
from schemas.responses import (
    CreateSessionResponse,
    DatasetMetaResponse,
    SessionInfoResponse,
    UploadResponse,
)

router = APIRouter()


def _require_session_ownership(session_id: str, user: Optional[User]) -> None:
    """Check that the session exists and the user owns it.

    Anonymous sessions (no user_id) are accessible without authentication
    for backward compatibility. User-owned sessions require the owner to
    be authenticated.
    """
    if not facade.has_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    owner_id = facade.get_session_owner(session_id)
    if owner_id is not None:
        # Session is owned — require authentication + matching user
        if user is None:
            raise HTTPException(
                status_code=401, detail="Authentication required for this session"
            )
        if user.id != owner_id:
            raise HTTPException(
                status_code=403, detail="You do not own this session"
            )


# ---------------------------------------------------------------------------
# Upload (creates a session)
# ---------------------------------------------------------------------------


@router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_user),
) -> UploadResponse:
    """Accept a CSV upload, parse dataset meta, run the graph, store state."""
    # 1. Validate CSV by filename suffix.
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files supported")

    # 2. Read and parse the CSV with pandas.
    content = await file.read()

    # Enforce max upload size before parsing.
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"CSV exceeds {settings.MAX_UPLOAD_SIZE_MB}MB upload limit",
        )
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {exc}")

    # 3. Compute dataset meta directly from the dataframe (independent of the
    #    agent layer, so the upload contract holds even with placeholder nodes).
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    missing_count = int(df.isna().sum().sum())

    # 4. Create a session id (owned by the authenticated user if any).
    session_id = str(uuid.uuid4())
    user_id = current_user.id if current_user else None
    facade.create_session(session_id=session_id, user_id=user_id)

    # 5. Persist the uploaded CSV to the upload dir.
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    csv_path = upload_dir / f"{session_id}.csv"
    csv_path.write_bytes(content)

    # 5b. Sync to S3 (only if S3_ENDPOINT_URL is configured).
    if settings.S3_ENDPOINT_URL:
        s3_remote_path = f"{session_id}/data.csv"
        try:
            s3_fs.upload_bytes(content, s3_remote_path)
        except Exception:
            # S3 不可用时降级到本地存储（F7 降级模式）
            facade.record_degradation(
                session_id, "upload", "S3 upload failed, using local storage", "local_fs"
            )

    # 6. Run the LangGraph pipeline via the facade (dev stage: synchronous).
    #    The facade owns the session store and persists final state + csv_path.
    facade.run_upload_pipeline(session_id, str(csv_path))

    # 7. Return the upload contract.
    dataset_meta = DatasetMetaResponse(
        columns=list(df.columns),
        rows=int(len(df)),
        dtypes=dtypes,
        missing_count=missing_count,
    )
    return UploadResponse(
        session_id=session_id,
        dataset_meta=dataset_meta,
    )


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
    session_id = facade.create_session(user_id=user_id)
    return CreateSessionResponse(session_id=session_id)


@router.get("/sessions", response_model=List[SessionInfoResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
) -> list[SessionInfoResponse]:
    """Return all sessions owned by the current user."""
    session_ids = facade.list_sessions_by_user(current_user.id)
    results: list[SessionInfoResponse] = []
    for sid in session_ids:
        has_dataset = False
        try:
            csv_path = facade.get_csv_path(sid)
            has_dataset = bool(csv_path)
        except Exception:
            has_dataset = False
        results.append(
            SessionInfoResponse(
                session_id=sid,
                exists=True,
                has_dataset=has_dataset,
            )
        )
    return results


@router.get("/sessions/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionInfoResponse:
    """Return session existence and basic info.

    Used by the frontend to verify a saved sessionId is still valid
    after a page refresh (localStorage recovery flow).
    """
    exists = facade.has_session(session_id)
    has_dataset = False
    if exists:
        try:
            csv_path = facade.get_csv_path(session_id)
            has_dataset = bool(csv_path)
        except Exception:
            has_dataset = False
    return SessionInfoResponse(
        session_id=session_id,
        exists=exists,
        has_dataset=has_dataset,
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Delete a session owned by the current user."""
    _require_session_ownership(session_id, current_user)
    facade.delete_session(session_id)
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
    if not facade.has_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    degradations = facade.get_degradations(session_id)
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
    inline as ``PlainTextResponse`` (Stage D 文件下载端点豁免)。
    """
    if not facade.has_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    state = facade.get_state(session_id)

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
"""REST endpoints for sessions.

T-02 backend layer: multipart CSV upload, session creation, and tex export.
Session state is held in the facade's in-memory dict for the dev stage;
production will swap to PostgresSaver (see spec decision 2).
"""
from __future__ import annotations

import io
import uuid
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from config import settings
from facade import facade
from schemas.responses import (
    CreateSessionResponse,
    DatasetMetaResponse,
    UploadResponse,
)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
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

    # 4. Create a session id.
    session_id = str(uuid.uuid4())

    # 5. Persist the uploaded CSV to the upload dir.
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    csv_path = upload_dir / f"{session_id}.csv"
    csv_path.write_bytes(content)

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


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session() -> CreateSessionResponse:
    """Create an empty session (no upload)."""
    session_id = facade.create_session()
    return CreateSessionResponse(session_id=session_id)


@router.get("/sessions/{session_id}/export")
async def export(session_id: str, format: str = "tex"):
    """Export a session's paper in the requested format.

    Note: returns ``PlainTextResponse`` (non-JSON), so no ``response_model``
    is declared (Stage D 文件下载端点豁免)。
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
        return PlainTextResponse(content=tex, media_type="application/x-tex")

    raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

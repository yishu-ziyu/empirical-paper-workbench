"""Formal attach + confirm-attach (DC-BE-attach).

POST /sessions/{id}/attach binds a user file or classic-5 entry.
POST /sessions/{id}/confirm-attach is the only transition that sets
``dataAttached``. Neither ranks catalog rows, confirms design, nor
writes chapters.
"""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

from auth import get_optional_user, require_auth_unless_debug, require_session_ownership
from models.user import User
from routers.sessions import _upload_response, _validated_upload_key, build_session_info
from schemas.responses import AttachResponse, SessionInfoResponse
from services.data_attach import (
    attach_classic5,
    attach_user_file_bytes,
    confirm_attach,
    stamp_user_file_candidate,
)

router = APIRouter()


class AttachRequest(BaseModel):
    source: Literal["classic-5", "user_file"]
    entry_id: Optional[str] = Field(default=None, min_length=1, max_length=64)


def _attach_from_admission(admission, *, source: str, entry_id: str | None) -> AttachResponse:
    uploaded = _upload_response(admission)
    return AttachResponse(
        session_id=uploaded.session_id,
        dataAttached=False,
        source=source,  # type: ignore[arg-type]
        entry_id=entry_id,
        upload_readiness="PROCESSING",
        run_id=uploaded.run_id,
        events_url=uploaded.events_url,
        dataset_meta=uploaded.dataset_meta,
    )


@router.post(
    "/sessions/{session_id}/attach",
    response_model=AttachResponse,
    responses={
        409: {"description": "Session busy, ingest not ready, or no candidate"},
        429: {"description": "The durable run queue is full"},
    },
)
async def attach_dataset(
    session_id: str,
    request: Request,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: Optional[User] = Depends(get_optional_user),
) -> AttachResponse | JSONResponse:
    """Bind a user file or classic-5 entry. Does not set dataAttached."""
    await run_in_threadpool(require_session_ownership, session_id, current_user)
    require_auth_unless_debug(current_user)
    user_id = current_user.id if current_user else None
    content_type = request.headers.get("content-type", "")
    file: Optional[UploadFile] = None

    if "multipart/form-data" in content_type:
        form = await request.form()
        source = str(form.get("source") or "user_file")
        raw_entry = form.get("entry_id")
        entry_id = str(raw_entry) if raw_entry not in (None, "") else None
        upload = form.get("file")
        if hasattr(upload, "filename"):
            file = upload  # type: ignore[assignment]
    else:
        try:
            payload = AttachRequest.model_validate(await request.json())
        except Exception as exc:
            raise HTTPException(status_code=422, detail="invalid_attach_request") from exc
        source = payload.source
        entry_id = payload.entry_id

    if source == "classic-5":
        if not entry_id:
            raise HTTPException(status_code=422, detail="classic5_entry_required")
        key = _validated_upload_key(idempotency_key)
        admission = await attach_classic5(
            session_id=session_id,
            user_id=user_id,
            entry_id=entry_id,
            idempotency_key=key,
        )
        body = _attach_from_admission(
            admission, source="classic-5", entry_id=entry_id
        )
        return JSONResponse(status_code=202, content=body.model_dump())

    if source != "user_file":
        raise HTTPException(status_code=422, detail="invalid_attach_source")

    if file is not None:
        key = _validated_upload_key(idempotency_key)
        admission = await attach_user_file_bytes(
            session_id=session_id,
            user_id=user_id,
            file=file,
            idempotency_key=key,
            request=request,
        )
        body = _attach_from_admission(
            admission, source="user_file", entry_id=None
        )
        return JSONResponse(status_code=202, content=body.model_dump())

    state = await stamp_user_file_candidate(session_id)
    readiness = state.get("upload_readiness")
    return AttachResponse(
        session_id=session_id,
        dataAttached=False,
        source="user_file",
        upload_readiness=readiness
        if readiness in {"PROCESSING", "READY", "FAILED", "CANCELLED"}
        else None,
    )


@router.post(
    "/sessions/{session_id}/confirm-attach",
    response_model=SessionInfoResponse,
    responses={
        409: {"description": "Ingest not ready, no candidate, or session busy"},
    },
)
async def confirm_attach_dataset(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SessionInfoResponse:
    """Confirm-attach is the only transition that sets dataAttached."""
    await run_in_threadpool(require_session_ownership, session_id, current_user)
    require_auth_unless_debug(current_user)
    await confirm_attach(session_id)
    return await build_session_info(session_id)

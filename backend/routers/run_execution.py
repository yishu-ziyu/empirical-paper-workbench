"""Durable run status and resumable server-sent events."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Literal, Optional, Union

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from run_repository import RunRepository, RunStatus, TERMINAL_STATUSES
from schemas.responses import DirectionResponse, SpecRunResultResponse


router = APIRouter()
_MAX_SSE_CONNECTIONS_PER_RUN = 4
_sse_connections: dict[str, int] = {}
_sse_connections_lock = asyncio.Lock()


class UploadRunResultResponse(BaseModel):
    cleaning_report: dict[str, Any]
    upload_readiness: Literal["READY"] = "READY"


class RunStatusResponse(BaseModel):
    run_id: str
    session_id: str
    kind: Literal["prewrite", "upload_pipeline", "spec_run"]
    status: RunStatus
    attempt: int
    lease_epoch: int
    result: Union[DirectionResponse, UploadRunResultResponse, SpecRunResultResponse] | None = None
    error: str | None = None


_PRIVATE_KEY_PARTS = (
    "path",
    "file",
    "workspace",
    "credential",
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "traceback",
    "raw_error",
    "provider_error",
)
_STABLE_LABEL = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
_STABLE_ERROR = re.compile(
    r"^[A-Za-z][A-Za-z0-9_]{0,63}: "
    r"(?:prewrite execution|upload_pipeline (?:execution|output_validation|[A-Za-z0-9_.-]+)|spec_run execution) failed$"
)
_PRIVATE_TEXT_MARKERS = (
    "/users/",
    "/private/",
    "/tmp/",
    "file://",
    "s3://",
    "secret",
    "credential",
    "password",
    "bearer ",
    "api_key",
    "api-key",
)


def _public_text(value: str) -> str:
    folded = value.casefold()
    if any(marker in folded for marker in _PRIVATE_TEXT_MARKERS):
        return "[redacted]"
    return value


def _public_value(value: Any) -> Any:
    if isinstance(value, dict):
        projected: dict[str, Any] = {}
        for raw_key, item in value.items():
            key = str(raw_key)
            normalized = key.casefold().replace("-", "_")
            if normalized == "error" or any(
                part in normalized for part in _PRIVATE_KEY_PARTS
            ):
                continue
            projected[key] = _public_value(item)
        return projected
    if isinstance(value, list):
        return [_public_value(item) for item in value]
    if isinstance(value, tuple):
        return [_public_value(item) for item in value]
    if isinstance(value, str):
        return _public_text(value)
    return value


def public_cleaning_report(value: Any) -> dict[str, Any]:
    """Allowlist the upload result used by the browser."""
    source = value if isinstance(value, dict) else {}
    steps: list[dict[str, Any]] = []
    for raw_step in source.get("steps") or []:
        if not isinstance(raw_step, dict):
            continue
        step: dict[str, Any] = {}
        for key in ("name", "status", "duration"):
            if key not in raw_step:
                continue
            item = raw_step.get(key)
            if isinstance(item, (str, int, float, bool)) or item is None:
                step[key] = item
        steps.append(step)
    return {"steps": steps}


def public_degradations(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in value if isinstance(value, list) else []:
        if not isinstance(raw, dict):
            continue
        row: dict[str, Any] = {}
        for key in ("node", "reason", "fallback"):
            item = raw.get(key)
            if isinstance(item, str):
                projected = _public_text(item)
                row[key] = projected[:200]
        if isinstance(raw.get("visible"), bool):
            row["visible"] = raw["visible"]
        rows.append(row)
    return rows


def public_instrument_fields(state: dict) -> dict[str, Any]:
    fields = _public_value(facade.instrument_fields(state))
    if state.get("cleaning_report") is not None:
        fields["cleaning_report"] = public_cleaning_report(
            state.get("cleaning_report")
        )
    return fields


def _public_result(
    kind: str, state: dict | None
) -> DirectionResponse | UploadRunResultResponse | SpecRunResultResponse | None:
    if not isinstance(state, dict):
        return None
    if kind == "upload_pipeline":
        return UploadRunResultResponse(
            cleaning_report=public_cleaning_report(state.get("cleaning_report")),
        )
    if kind == "spec_run":
        lab = state.get("research_lab") if isinstance(state.get("research_lab"), dict) else {}
        runs = lab.get("specification_runs") if isinstance(lab, dict) else []
        count = len(runs) if isinstance(runs, list) else 0
        return SpecRunResultResponse(ok=True, specification_run_count=count)
    fields = public_instrument_fields(state)
    return DirectionResponse(
        **fields,
        degradations=public_degradations(state.get("degradations")),
    )


def _public_error(kind: str, error: str | None) -> str | None:
    if not error:
        return None
    if _STABLE_ERROR.fullmatch(error):
        return error
    if kind == "upload_pipeline":
        return "upload_pipeline_failed"
    if kind == "spec_run":
        return "spec_run_failed"
    return "prewrite_failed"


def _public_event(event, *, kind: str) -> dict[str, Any]:
    payload = dict(event.payload or {})
    public = {
        "seq": event.seq,
        "type": event.event_type,
        "kind": kind,
    }
    # spec_id rides spec_run progress events so the browser can show real
    # per-specification progress ("Running k/12"); the label is a stable id.
    for key in ("status", "node", "attempt", "lease_epoch", "spec_id"):
        value = payload.get(key)
        if isinstance(value, str) and _STABLE_LABEL.fullmatch(value):
            public[key] = value
        elif isinstance(value, int):
            public[key] = value
    return public


def _response(run) -> RunStatusResponse:
    return RunStatusResponse(
        run_id=run.run_id,
        session_id=run.session_id,
        kind=run.kind,
        status=run.status,
        attempt=run.attempt,
        lease_epoch=run.lease_epoch,
        result=_public_result(run.kind, run.result),
        error=_public_error(run.kind, run.error),
    )


@router.get("/runs/{run_id}", response_model=RunStatusResponse)
async def get_run(
    run_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> RunStatusResponse:
    run = await RunRepository().get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    require_session_ownership(run.session_id, current_user)
    return _response(run)


@router.get(
    "/runs/{run_id}/events",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {
                "text/event-stream": {
                    "schema": {"type": "string"},
                }
            },
            "description": "Ordered run events; resume with Last-Event-ID.",
        }
    },
)
async def stream_run_events(
    request: Request,
    run_id: str,
    last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    current_user: Optional[User] = Depends(get_optional_user),
):
    repo = RunRepository()
    run = await repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    require_session_ownership(run.session_id, current_user)
    async with _sse_connections_lock:
        connections = _sse_connections.get(run_id, 0)
        if connections >= _MAX_SSE_CONNECTIONS_PER_RUN:
            raise HTTPException(
                status_code=429,
                detail="too many event streams for this run",
                headers={"Retry-After": "5"},
            )
        _sse_connections[run_id] = connections + 1
    try:
        cursor = max(0, int(last_event_id or "0"))
    except ValueError:
        cursor = 0

    async def generate():
        nonlocal cursor
        idle_ticks = 0
        try:
            while True:
                if await request.is_disconnected():
                    return
                events = await repo.events_after(run_id, cursor)
                terminal_event = False
                for event in events:
                    cursor = event.seq
                    data = json.dumps(
                        _public_event(event, kind=run.kind),
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    yield f"id: {event.seq}\ndata: {data}\n\n"
                    terminal_event = terminal_event or event.event_type in {
                        "run.succeeded",
                        "run.failed",
                        "run.cancelled",
                    }
                if terminal_event:
                    return
                idle_ticks += 1
                if idle_ticks % 30 == 0:
                    latest = await repo.get(run_id)
                    if latest is None or latest.status in TERMINAL_STATUSES:
                        return
                    yield ": heartbeat\n\n"
                await asyncio.sleep(0.5)
        finally:
            async with _sse_connections_lock:
                remaining = _sse_connections.get(run_id, 1) - 1
                if remaining > 0:
                    _sse_connections[run_id] = remaining
                else:
                    _sse_connections.pop(run_id, None)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

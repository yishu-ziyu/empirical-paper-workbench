"""REST endpoints for T-06: research direction + HITL outline resume.

- POST /sessions/{id}/direction: 接受 {question, dv, iv, controls, method, template}
  → 写入 state.research_direction → set_direction → 识别验真
  → 非 0 星写入 Table 1 + 主设定方程并停下，不自动跑 estimate
- POST /sessions/{id}/prewrite/confirm: 客户端确认后继续 estimate → robustness → outline
- POST /sessions/{id}/resume: 接受用户调整后的 outline → 写入 state.user_adjusted_outline
  → 重跑 generate_outline (采用调整版) → 返回 {ok, outline}

HITL 简化 (同 T-04): 不走 LangGraph interrupt()。outline router 通过
``AgentFacade`` 调用 set_direction / generate_outline 节点，session 状态
由 facade 持有。graph.py 集成 (把两节点加进 StateGraph) 留给后续 ticket。
"""
from __future__ import annotations

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from agent.engine.did_spec import DID_MISSING_INTERACTION, can_form_did_main_term
from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from services.allow_did import confirmed_did_method
from services.formal_binding import align_direction, run_binding, require_observed_target
from services.formal_chain import require_confirm_attached, require_design_confirmed
from run_repository import QueueFull, RunRepository, SessionBusy, SessionNotFound
from schemas.responses import (
    ConfirmationTarget,
    PrewriteConfirmRequest,
    PrewriteGateResponse,
    QueueFullResponse,
    ResumeResponse,
    RunAcceptedResponse,
    SessionBusyResponse,
)

router = APIRouter()


class DirectionRequest(BaseModel):
    """POST /sessions/{id}/direction 请求体。

    方法列（time_col / instrument / running 等）必须能进门。
    extra=allow：未列名的别名键也保留，交给 set_direction 投影。
    """

    question: str
    expectedTarget: Optional[ConfirmationTarget] = None
    dv: str
    iv: str
    controls: List[str] = Field(default_factory=list)
    method: str
    template: str = "cn_journal"
    claim: Optional[str] = None
    time_col: Optional[str] = None
    id_col: Optional[str] = None
    first_treat_col: Optional[str] = None
    instrument: Optional[str] = None
    instrument_col: Optional[str] = None
    instruments: Optional[List[str]] = None
    endogenous_col: Optional[str] = None
    running: Optional[str] = None
    running_var: Optional[str] = None
    cutoff: Optional[float] = None
    unit_col: Optional[str] = None
    treated_unit: Optional[Any] = None
    treatment_time: Optional[Any] = None
    cluster: Optional[str] = None
    cluster_levels: List[str] = Field(default_factory=list)
    heterogeneity_groups: List[str] = Field(default_factory=list)
    qType: Optional[str] = None
    specMode: Optional[str] = None
    model_config = {"extra": "allow"}


class ResumeRequest(BaseModel):
    """POST /sessions/{id}/resume 请求体。"""

    outline: List[Any]


@router.post(
    "/sessions/{session_id}/direction",
    response_model=RunAcceptedResponse,
    status_code=202,
    responses={
        409: {
            "model": SessionBusyResponse,
            "description": "The session already has an active run; attach to it.",
        },
        429: {
            "model": QueueFullResponse,
            "description": "The durable run queue is full.",
            "headers": {
                "Retry-After": {
                    "description": "Seconds before retrying admission.",
                    "schema": {"type": "integer"},
                }
            },
        },
    },
)
async def set_direction_endpoint(
    session_id: str,
    payload: DirectionRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=200,
    ),
    current_user: Optional[User] = Depends(get_optional_user),
) -> RunAcceptedResponse:
    """Persist a pre-write command and return before research work begins."""
    require_session_ownership(session_id, current_user)
    expected = payload.expectedTarget.model_dump() if payload.expectedTarget else None
    submitted = payload.model_dump(exclude={"expectedTarget"})
    intent = {"action": "direction", "input": submitted, "target": expected}

    def prepare(current: dict) -> dict:
        # All preconditions and the inserted payload use the same locked state.
        readiness = current.get("upload_readiness")
        if readiness in {"PROCESSING", "FAILED", "CANCELLED"}:
            raise HTTPException(409, detail={"code": "upload_not_ready", "upload_readiness": readiness})
        require_confirm_attached(current)
        require_design_confirmed(current)
        require_observed_target(current, expected, ("design", "dataset"))
        direction = align_direction(current, submitted)
        if confirmed_did_method(current) and not can_form_did_main_term({**current, "research_direction": direction}, direction):
            raise HTTPException(409, detail={"code": DID_MISSING_INTERACTION})
        return {"research_direction": direction,
                "initial_state": {**current, "prewrite_phase": "direction"},
                "phase": "direction", "binding": run_binding(current)}

    try:
        run = await RunRepository().enqueue(
            session_id=session_id,
            kind="prewrite",
            payload={"intent": intent},
            prepare=prepare,
            idempotency_key=idempotency_key,
        )
    except SessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    except SessionBusy as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "session_busy", "run_id": exc.run_id},
        ) from exc
    except QueueFull as exc:
        raise HTTPException(
            status_code=429,
            detail="run queue is full",
            headers={"Retry-After": "5"},
        ) from exc
    return RunAcceptedResponse(
        run_id=run.run_id,
        session_id=run.session_id,
        status="PENDING",
        events_url=f"/api/runs/{run.run_id}/events",
    )


@router.post(
    "/sessions/{session_id}/prewrite/confirm",
    response_model=RunAcceptedResponse | PrewriteGateResponse,
    responses={
        200: {
            "model": PrewriteGateResponse,
            "description": "Table 1 / spec confirms recorded; estimate not started.",
        },
        202: {
            "model": RunAcceptedResponse,
            "description": "Both confirms accepted; estimate run enqueued.",
        },
        409: {
            "model": SessionBusyResponse,
            "description": "Session busy, confirms incomplete, identification blocked, or hetero hard-block.",
        },
        429: {
            "model": QueueFullResponse,
            "description": "The durable run queue is full.",
            "headers": {
                "Retry-After": {
                    "description": "Seconds before retrying admission.",
                    "schema": {"type": "integer"},
                }
            },
        },
    },
)
async def confirm_prewrite_endpoint(
    session_id: str,
    payload: PrewriteConfirmRequest = PrewriteConfirmRequest(),
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=200,
    ),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Record FE confirm flags, or continue estimate after both CTAs."""
    require_session_ownership(session_id, current_user)
    confirms = payload.model_dump()
    intent = {"action": payload.action, "input": confirms}
    if payload.action == "record_confirms":
        # The facade validates the target, checks idle and writes atomically.
        recorded = await run_in_threadpool(facade.record_prewrite_confirms,
            session_id, confirms, idempotency_key=idempotency_key
        )
        return JSONResponse(
            status_code=200,
            content=PrewriteGateResponse(**recorded).model_dump(mode="json"),
        )
    if payload.action != "continue_estimate":
        raise HTTPException(status_code=422, detail="unsupported confirm action")
    def prepare(current: dict) -> dict:
        direction, initial = facade.prepare_prewrite_confirm(session_id, confirms, state=current)
        return {"research_direction": direction, "initial_state": initial,
                "phase": "estimate", "binding": run_binding(current)}

    try:
        run = await RunRepository().enqueue(
            session_id=session_id,
            kind="prewrite",
            payload={"intent": intent},
            prepare=prepare,
            idempotency_key=idempotency_key,
        )
    except SessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    except SessionBusy as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "session_busy", "run_id": exc.run_id},
        ) from exc
    except QueueFull as exc:
        raise HTTPException(
            status_code=429,
            detail="run queue is full",
            headers={"Retry-After": "5"},
        ) from exc
    return JSONResponse(
        status_code=202,
        content=RunAcceptedResponse(
            run_id=run.run_id,
            session_id=run.session_id,
            status="PENDING",
            events_url=f"/api/runs/{run.run_id}/events",
        ).model_dump(mode="json"),
    )


@router.post(
    "/sessions/{session_id}/resume",
    response_model=ResumeResponse,
)
async def resume_endpoint(
    session_id: str,
    payload: ResumeRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResumeResponse:
    """接受用户调整后的 outline → 写入 user_adjusted_outline → 重跑 generate_outline。"""
    require_session_ownership(session_id, current_user)
    state = facade.resume_outline(session_id, payload.outline)
    return ResumeResponse(
        ok=True,
        outline=state.get("outline", []),
    )

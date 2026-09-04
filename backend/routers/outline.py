"""REST endpoints for T-06: research direction + HITL outline resume.

- POST /sessions/{id}/direction: 接受 {question, dv, iv, controls, method, template}
  → 写入 state.research_direction → set_direction → 识别验真
  → 非 0 星再 generate_outline → 返回 outline + 识别报告
- POST /sessions/{id}/resume: 接受用户调整后的 outline → 写入 state.user_adjusted_outline
  → 重跑 generate_outline (采用调整版) → 返回 {ok, outline}

HITL 简化 (同 T-04): 不走 LangGraph interrupt()。outline router 通过
``AgentFacade`` 调用 set_direction / generate_outline 节点，session 状态
由 facade 持有。graph.py 集成 (把两节点加进 StateGraph) 留给后续 ticket。
"""
from __future__ import annotations

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from run_repository import QueueFull, RunRepository, SessionBusy, SessionNotFound
from schemas.responses import (
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
    upload_readiness = facade.get_state(session_id).get("upload_readiness")
    if upload_readiness in {"PROCESSING", "FAILED", "CANCELLED"}:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "upload_not_ready",
                "upload_readiness": upload_readiness,
            },
        )
    rd = payload.model_dump()
    try:
        run = await RunRepository().enqueue(
            session_id=session_id,
            kind="prewrite",
            payload={
                "research_direction": rd,
                "initial_state": facade.prepare_prewrite_state(session_id),
            },
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

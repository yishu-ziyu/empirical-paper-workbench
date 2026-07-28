"""REST endpoints for T-06: research direction + HITL outline resume.

- POST /sessions/{id}/direction: 接受 {question, dv, iv, controls, method, template}
  → 写入 state.research_direction → 跑 set_direction + generate_outline → 返回 6 章 outline
- POST /sessions/{id}/resume: 接受用户调整后的 outline → 写入 state.user_adjusted_outline
  → 重跑 generate_outline (采用调整版) → 返回 {ok, outline}

HITL 简化 (同 T-04): 不走 LangGraph interrupt()。outline router 通过
``AgentFacade`` 调用 set_direction / generate_outline 节点，session 状态
由 facade 持有。graph.py 集成 (把两节点加进 StateGraph) 留给后续 ticket。
"""
from __future__ import annotations

from typing import Any, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from facade import facade
from schemas.responses import DirectionResponse, ResumeResponse

router = APIRouter()


class DirectionRequest(BaseModel):
    """POST /sessions/{id}/direction 请求体。"""

    question: str
    dv: str
    iv: str
    controls: List[str] = Field(default_factory=list)
    method: str
    template: str = "cn_journal"


class ResumeRequest(BaseModel):
    """POST /sessions/{id}/resume 请求体。"""

    outline: List[Any]


@router.post(
    "/sessions/{session_id}/direction",
    response_model=DirectionResponse,
)
async def set_direction_endpoint(
    session_id: str, payload: DirectionRequest
) -> DirectionResponse:
    """接受研究方向 → set_direction → generate_outline → 返回 outline。"""
    rd = payload.model_dump()
    state = facade.set_direction_and_outline(session_id, rd)
    return DirectionResponse(
        outline=state.get("outline", []),
        research_direction=rd,
    )


@router.post(
    "/sessions/{session_id}/resume",
    response_model=ResumeResponse,
)
async def resume_endpoint(
    session_id: str, payload: ResumeRequest
) -> ResumeResponse:
    """接受用户调整后的 outline → 写入 user_adjusted_outline → 重跑 generate_outline。"""
    state = facade.resume_outline(session_id, payload.outline)
    return ResumeResponse(
        ok=True,
        outline=state.get("outline", []),
    )

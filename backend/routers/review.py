"""ADR-0007 Stage 1: HITL 人工评审 REST 端点。

- GET /sessions/{id}/review
    返回当前 review_chapter 的最新评审结果（feedback / suggestions / score /
    5 维 rubric / iteration / auto_decision）
- POST /sessions/{id}/review/decision
    接收人工决策（accept / reject / force_pass），写入 state，reject 时触发
    重生成

HITL 是 ADR 0004 自动评审的叠加层（hitl_review_enabled 默认 False），
不修改 review_chapter 节点逻辑。Router 只调 facade，不直调节点
（遵循 ADR 0003 Facade 契约）。
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.review import (
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    ReviewInfoResponse,
    ReviewRubricResponse,
)

router = APIRouter()


@router.get(
    "/sessions/{session_id}/review",
    response_model=ReviewInfoResponse,
)
async def get_review(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ReviewInfoResponse:
    """返回当前章的评审信息。

    Response: ``{chapter_index, feedback, suggestions, score, rubric,
                 review_iteration, max_review_iterations, auto_decision,
                 review_source, review_degraded, grounding_failures}``

    无评审数据时返回 200 + 空字段（非 404），让前端渲染空态。
    """
    require_session_ownership(session_id, current_user)
    info = facade.get_review(session_id)
    return ReviewInfoResponse(
        chapter_index=info["chapter_index"],
        feedback=info["feedback"],
        suggestions=info["suggestions"],
        score=info["score"],
        rubric=ReviewRubricResponse(**info["rubric"]),
        review_iteration=info["review_iteration"],
        max_review_iterations=info["max_review_iterations"],
        auto_decision=info["auto_decision"],
        review_source=info.get("review_source") or "",
        review_degraded=bool(info.get("review_degraded")),
        grounding_failures=list(info.get("grounding_failures") or []),
    )


@router.post(
    "/sessions/{session_id}/review/decision",
    response_model=ReviewDecisionResponse,
)
async def submit_review_decision(
    session_id: str,
    payload: ReviewDecisionRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ReviewDecisionResponse:
    """接收人工评审决策，写入 state。

    Request:  ``{decision: "accept"|"reject"|"force_pass", reviewer?, comment?}``
    Response: ``{ok, decision, chapter_index, next_action}``

    - ``accept`` / ``force_pass`` → ``next_action="proceed"``
    - ``reject`` → 触发 ``facade.regenerate_chapter``，``next_action="regenerate"``
    """
    require_session_ownership(session_id, current_user)
    result = facade.submit_review_decision(
        session_id,
        decision=payload.decision,
        reviewer=payload.reviewer,
        comment=payload.comment,
    )
    return ReviewDecisionResponse(
        ok=result["ok"],
        decision=result["decision"],
        chapter_index=result["chapter_index"],
        next_action=result["next_action"],
    )


# 路由注册统一在 main.py include_router，不再 import 侧自注册。

"""REST endpoints for T-07: chapter generation + HITL approval.

- POST /sessions/{id}/generate-chapter
    接受 {chapter: {type, title, ...}} → 写入 state.current_chapter
    → 跑 generate_chapter 节点 → 返回生成的章节
- POST /sessions/{id}/approve-chapter
    用户审批后继续 → 标记当前章节 status="approved" → 返回 {ok}
    （graph resume 由后续集成阶段在 graph 层加 interrupt() 后实现）

HITL 简化 (同 T-04 / T-06): 不走 LangGraph interrupt()。chapter router 通过
``AgentFacade`` 调用 generate_chapter / rollback_chapter 节点，session 状态
由 facade 持有。graph.py 集成 (在 generate_chapter 后加 interrupt()) 留给
后续 ticket。

Router self-registration: the integration phase will move the
``app.include_router`` call into ``main.py``. For now, importing this
module attaches the router to ``main.app`` so tests and dev runs reach
the endpoint without touching ``main.py`` (per T-07 file boundaries).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import (
    ApproveChapterResponse,
    ChapterResponse,
    GenerateChapterResponse,
    RegenerateResponse,
    RollbackResponse,
    VersionsResponse,
)

router = APIRouter()
_REGISTERED = False

# 评审通过阈值：与 agent/nodes/review_chapter.REVIEW_SCORE_THRESHOLD 同源。
# agent 模块缺失时退回默认值，保持与 facade 的 try/except 导入风格一致。
try:
    from nodes.review_chapter import (
        REVIEW_SCORE_THRESHOLD as _REVIEW_SCORE_THRESHOLD,
    )
except Exception:  # pragma: no cover
    _REVIEW_SCORE_THRESHOLD = 0.7

# 合法 chapter type（与 agent/graph.py CHAPTER_TYPES 一致）
# 端点校验：未知 type 直接 400，避免 generate_chapter 索引流默默走 outline 忽略请求
_VALID_CHAPTER_TYPES = {
    "intro",
    "lit_review",
    "data_desc",
    "methods",
    "results",
    "conclusion",
}


# ---------------------------------------------------------------------------
# 请求 / 响应 models
# ---------------------------------------------------------------------------
class ChapterSpec(BaseModel):
    """章节定义（用户选择要生成哪一章）。"""

    type: str
    title: str = ""
    # 章节特化的字段（method / research_question 等）可透传到模板 render
    method: Optional[str] = None
    research_question: Optional[str] = None


class GenerateChapterRequest(BaseModel):
    """POST /sessions/{id}/generate-chapter 请求体。"""

    chapter: ChapterSpec
    # 也可从 state 透传 render kwargs（research_question / data_summary 等）
    # 若未提供则从 state 取
    render_kwargs: Dict[str, Any] = Field(default_factory=dict)


class ApproveChapterRequest(BaseModel):
    """POST /sessions/{id}/approve-chapter 请求体。"""

    # 可选：指定要 approve 的章节 type；缺省为最后生成的章节
    chapter_type: Optional[str] = None
    # 显式强制放行：评审未通过（分数不达标或接地失败）时必须置 True,
    # 章节会带上 approved_forced 标记留在产物里（可查）。
    force: bool = False


class RollbackRequest(BaseModel):
    """POST /sessions/{id}/rollback 请求体。"""

    chapter_index: int = 0
    version_index: int = 0


class RegenerateRequest(BaseModel):
    """POST /sessions/{id}/regenerate 请求体。"""

    chapter_index: int = 0


# ---------------------------------------------------------------------------
# endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/sessions/{session_id}/generate-chapter",
    response_model=GenerateChapterResponse,
)
async def generate_chapter_endpoint(
    session_id: str,
    payload: GenerateChapterRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> GenerateChapterResponse:
    """触发 generate_chapter 节点：写入 current_chapter → 跑节点 → 返回章节。

    返回体：
    {
      "chapter": {type, title, content, status: "generated", ...},
      "body_chapters": [...],  # 全部正文章节
    }
    """
    require_session_ownership(session_id, current_user)
    # 校验 chapter.type 合法性（未知 type 直接 400，不进 generate_chapter）
    if payload.chapter.type not in _VALID_CHAPTER_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown chapter_type: {payload.chapter.type!r}; "
                f"expected one of {sorted(_VALID_CHAPTER_TYPES)}"
            ),
        )

    chapter_dict = payload.chapter.model_dump(exclude_none=True)
    state = facade.generate_chapter(
        session_id, chapter_dict, payload.render_kwargs
    )

    body_chapters: List[Any] = state.get("body_chapters", []) or []
    # 评审可能回退 current_chapter_index。按请求 type 取刚写的那一章。
    chapter = _chapter_with_type(body_chapters, payload.chapter.type)
    if not chapter:
        idx = state.get("current_chapter_index")
        if isinstance(idx, int) and 0 < idx <= len(body_chapters):
            chapter = body_chapters[idx - 1]
        elif body_chapters:
            chapter = body_chapters[-1]
        else:
            chapter = {}
    return GenerateChapterResponse(
        chapter=_to_chapter_response(chapter),
        body_chapters=[_to_chapter_response(c) for c in body_chapters],
        **_review_response_fields(state),
    )


@router.post(
    "/sessions/{session_id}/approve-chapter",
    response_model=ApproveChapterResponse,
)
async def approve_chapter_endpoint(
    session_id: str,
    payload: ApproveChapterRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ApproveChapterResponse:
    """用户审批章节 → 标记 status="approved"。

    graph resume 由后续集成阶段在 graph 层加 interrupt() 后实现；此处只
    更新 session 状态。
    """
    require_session_ownership(session_id, current_user)
    state = facade.get_state(session_id)
    body_chapters: List[Any] = list(state.get("body_chapters", []) or [])

    target_idx: Optional[int] = None
    if payload.chapter_type:
        for i, ch in enumerate(body_chapters):
            if isinstance(ch, dict) and ch.get("type") == payload.chapter_type:
                target_idx = i
                break
        if target_idx is None:
            raise HTTPException(
                status_code=404,
                detail=f"No chapter of type {payload.chapter_type!r} to approve",
            )
    else:
        if not body_chapters:
            raise HTTPException(status_code=404, detail="No chapter to approve")
        # 默认 approve 最后一篇已写成的章（评审回退 idx 时不能落到空槽）
        target_idx = _last_written_index(body_chapters)
        if target_idx is None:
            idx = state.get("current_chapter_index")
            if isinstance(idx, int) and 0 < idx <= len(body_chapters):
                target_idx = idx - 1
            else:
                target_idx = len(body_chapters) - 1

    # 硬证据门（北极星：未经核对的内容不得静默进入论文）：
    # - 无评审记录 → 视为未核对，不得直接 approve
    # - score < REVIEW_SCORE_THRESHOLD → 评审未通过
    # - force=True 是唯一旁路，且章节会带上 approved_forced 标记
    review_scores = list(state.get("review_scores") or [])
    if target_idx < len(review_scores):
        score = float(review_scores[target_idx])
    else:
        score = None
    passed = score is not None and score >= _REVIEW_SCORE_THRESHOLD
    if not passed and not payload.force:
        raise HTTPException(
            status_code=409,
            detail={
                "review_gate": True,
                "chapter_index": target_idx,
                "score": score,
                "threshold": _REVIEW_SCORE_THRESHOLD,
                "needs_force": True,
            },
        )

    approved_chapter = {
        **body_chapters[target_idx],
        "status": "approved",
    }
    if not passed:
        approved_chapter["approved_forced"] = True
    body_chapters[target_idx] = approved_chapter
    facade.update_state(session_id, body_chapters=body_chapters)

    # 审批动作落 trace：normal 通过 / force 旁路一目了然（"可查"磁盘件）
    facade.record_event(
        session_id,
        "approve_chapter",
        status="forced" if not passed else "ok",
        detail={
            "chapter_index": target_idx,
            "score": score,
            "threshold": _REVIEW_SCORE_THRESHOLD,
            "reviewer_bypassed_review": (not passed) or None,
        },
    )

    return ApproveChapterResponse(
        ok=True,
        chapter=_to_chapter_response(body_chapters[target_idx]),
        body_chapters=[_to_chapter_response(c) for c in body_chapters],
    )


# ---------------------------------------------------------------------------
# T-08b: rollback / regenerate / versions 端点
# ---------------------------------------------------------------------------
@router.post(
    "/sessions/{session_id}/rollback",
    response_model=RollbackResponse,
)
async def rollback_chapter_endpoint(
    session_id: str,
    payload: RollbackRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> RollbackResponse:
    """回滚到指定版本。

    Request:  ``{"chapter_index": int, "version_index": int}``
    Response: ``{"chapter": {...}, "body_chapters": [...]}``

    把 chapter_index / version_index 写入 state 后调
    ``rollback_chapter(state)`` 节点（T-08a），节点返回
    ``{"body_chapters": [...]}``，合并回 session 状态。
    """
    require_session_ownership(session_id, current_user)
    chapter_index = payload.chapter_index
    version_index = payload.version_index
    state = facade.rollback_chapter(session_id, chapter_index, version_index)

    body_chapters: List[Any] = state.get("body_chapters", []) or []
    idx = (
        chapter_index
        if isinstance(chapter_index, int) and 0 <= chapter_index < len(body_chapters)
        else (len(body_chapters) - 1)
    )
    chapter = body_chapters[idx] if body_chapters else {}
    return RollbackResponse(
        chapter=_to_chapter_response(chapter),
        body_chapters=[_to_chapter_response(c) for c in body_chapters],
    )


@router.post(
    "/sessions/{session_id}/regenerate",
    response_model=RegenerateResponse,
)
async def regenerate_chapter_endpoint(
    session_id: str,
    payload: RegenerateRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> RegenerateResponse:
    """重新生成当前章。

    Request:  ``{"chapter_index": int}``
    Response: ``{"chapter": {...含新版本...}, "body_chapters": [...]}``

    设置 ``state['current_chapter_index']``，调 ``generate_chapter(state)``
    节点，合并结果。
    """
    require_session_ownership(session_id, current_user)
    chapter_index = payload.chapter_index
    state = facade.regenerate_chapter(session_id, chapter_index)

    body_chapters = state.get("body_chapters", []) or []
    idx = (
        chapter_index
        if isinstance(chapter_index, int) and 0 <= chapter_index < len(body_chapters)
        else (len(body_chapters) - 1)
    )
    chapter = body_chapters[idx] if body_chapters else {}
    return RegenerateResponse(
        chapter=_to_chapter_response(chapter),
        body_chapters=[_to_chapter_response(c) for c in body_chapters],
        **_review_response_fields(state),
    )


@router.get(
    "/sessions/{session_id}/chapters/{chapter_index}/versions",
    response_model=VersionsResponse,
)
async def get_versions(
    session_id: str,
    chapter_index: int,
    current_user: Optional[User] = Depends(get_optional_user),
) -> VersionsResponse:
    """获取指定章节的所有版本。

    Response: ``{"chapter_index": int, "count": int,
                  "versions": [{"index": int, "preview": str}]}``

    每个版本的 ``preview`` 截断到前 50 字。章节无 ``versions`` 列表时，
    降级用 ``content`` 作为唯一版本。
    """
    require_session_ownership(session_id, current_user)
    state = facade.get_state(session_id)
    body_chapters = state.get("body_chapters", []) or []
    if chapter_index < 0 or chapter_index >= len(body_chapters):
        raise HTTPException(status_code=404, detail="Chapter index out of range")
    chapter = body_chapters[chapter_index]
    if not isinstance(chapter, dict):
        chapter = {}
    raw_versions = chapter.get("versions")
    if raw_versions is None:
        content = chapter.get("content", "")
        raw_versions = [content] if content else []

    from schemas.responses import ChapterVersionItem

    versions = []
    for i, v in enumerate(raw_versions):
        text = v if isinstance(v, str) else str(v)
        versions.append(ChapterVersionItem(index=i, preview=text[:50]))
    return VersionsResponse(
        chapter_index=chapter_index,
        count=len(versions),
        versions=versions,
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _review_response_fields(state: dict) -> dict:
    """写章响应上的评审可见字段。回退 idx 时用分数判 fail，不拿空槽。"""
    scores = state.get("review_scores") or []
    idx = state.get("review_chapter_index")
    score = 0.0
    if isinstance(idx, int) and 0 <= idx < len(scores):
        try:
            score = float(scores[idx])
        except (TypeError, ValueError):
            score = 0.0
    return {
        "score": score,
        "auto_decision": "pass" if score >= 0.7 else "fail",
        "review_source": state.get("review_source") or "",
        "review_degraded": bool(state.get("review_degraded")),
        "grounding_failures": list(state.get("grounding_failures") or []),
    }


def _chapter_with_type(body_chapters: List[Any], chapter_type: str) -> dict:
    for ch in body_chapters:
        if (
            isinstance(ch, dict)
            and ch.get("type") == chapter_type
            and ch.get("content")
        ):
            return ch
    return {}


def _last_written_index(body_chapters: List[Any]) -> Optional[int]:
    last = None
    for i, ch in enumerate(body_chapters):
        if isinstance(ch, dict) and ch.get("type") and ch.get("content"):
            last = i
    return last


def _to_chapter_response(chapter: Any) -> ChapterResponse:
    """把 state 里的 dict 章节转成 ``ChapterResponse``。

    容错：非 dict / None → 空 ``ChapterResponse``。
    ``model_config = {"extra": "allow"}`` 保留额外字段（versions / chapter_index 等）。
    """
    if not isinstance(chapter, dict):
        return ChapterResponse()
    return ChapterResponse(**chapter)


# ---------------------------------------------------------------------------
# self-registration（与 eda.py 模式一致）
# ---------------------------------------------------------------------------
def _self_register() -> None:
    """Attach this router to the FastAPI app on import.

    The integration phase will move ``app.include_router`` into ``main.py``
    explicitly. Self-registering here lets tests (which import this module)
    and dev runs reach the endpoint without modifying ``main.py`` (T-07
    file-boundary constraint). Idempotent via the ``_REGISTERED`` flag.
    """
    global _REGISTERED
    if _REGISTERED:
        return
    try:
        from main import app  # noqa: PLC0415

        app.include_router(router)
        _REGISTERED = True
    except Exception:
        # main not importable yet (e.g. during partial builds) — skip silently.
        pass


_self_register()

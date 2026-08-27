"""整体进度端点 (T-08b).

GET /sessions/{session_id}/progress 返回 6 章完成进度：

    {
      "total": 6,
      "completed": <status=="approved" 的章节数>,
      "current": <state['current_chapter_index']，缺省取 len(body_chapters)>,
      "body_chapters": [{"type":..., "title":..., "status":...}, ...]
    }

Router self-registration: 与 eda.py / chapter.py 一致，import 时自动 attach
到 ``main.app``，不改 ``main.py``（T-08b file-boundary 约束）。
"""
from __future__ import annotations

from typing import Any, List, Optional

from fastapi import APIRouter, Depends

from auth import get_optional_user, require_session_ownership
from facade import facade
from models.user import User
from schemas.responses import (
    JourneyResponse,
    JourneyStageItem,
    ProgressChapterSummary,
    ProgressResponse,
)

router = APIRouter()
_REGISTERED = False

_TOTAL_CHAPTERS = 6

# 8 阶段研究旅程（0-index，收敛版：去掉无节点的"表格图形"站）。
# canIntervene=True 表示核心可介入站。
# 注：等"图表/写作"功能真正实现后，再补回第 9 站（表格图形）。
_JOURNEY_STAGES = [
    {"name": "选题", "canIntervene": True},
    {"name": "文献", "canIntervene": False},
    {"name": "数据清洗", "canIntervene": True},
    {"name": "识别策略", "canIntervene": True},
    {"name": "估计建模", "canIntervene": False},
    {"name": "稳健性审计", "canIntervene": True},
    {"name": "写作评审", "canIntervene": True},
    {"name": "降AIGC导出", "canIntervene": False},
]


@router.get(
    "/sessions/{session_id}/progress",
    response_model=ProgressResponse,
)
async def get_progress(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ProgressResponse:
    """返回 6 章完成进度。"""
    require_session_ownership(session_id, current_user)
    state = facade.get_state(session_id)
    body_chapters: List[Any] = list(state.get("body_chapters", []) or [])

    completed = sum(
        1
        for c in body_chapters
        if isinstance(c, dict) and c.get("status") == "approved"
    )

    current = state.get("current_chapter_index")
    if current is None:
        current = len(body_chapters)

    summary = [
        ProgressChapterSummary(
            type=c.get("type") if isinstance(c, dict) else None,
            title=c.get("title") if isinstance(c, dict) else None,
            status=c.get("status") if isinstance(c, dict) else None,
        )
        for c in body_chapters
    ]
    return ProgressResponse(
        total=_TOTAL_CHAPTERS,
        completed=completed,
        current=current,
        body_chapters=summary,
    )


def _has_field(state: dict, key: str, *, is_dict: bool = False) -> bool:
    """Query 一个 state 字段是否存在（非空）。

    ``is_dict=True`` 时要求它是一个非空 dict（用于 research_direction /
    identification_diag 这类结构化字段）。空集合（空 list/dict/str）视为
    无产物，返回 False。
    """
    value = state.get(key)
    if value is None:
        return False
    if is_dict:
        return isinstance(value, dict) and bool(value)
    if isinstance(value, (list, dict, str, tuple)):
        return len(value) > 0
    return True


def _infer_journey(state: dict) -> tuple[int, bool]:
    """从 LangGraph state 推断处于哪个阶段。

    返回 ``(current_stage, identification_failed)``。current_stage 是
    "正在进行的阶段"（已完成的最后一个阶段 + 1）。依据 state 真实字段而非
    硬编码节点名，逐级累加。收敛版 8 站（去掉了无节点的"表格图形"站）：
    - 0 选题 / 1 文献：research_direction 已读
    - 2 数据清洗：已产生 cleaning 相关产物
    - 3 识别策略：identification_diag 已产生
    - 4 估计建模：estimate.produced_by
    - 5 稳健性审计：robustness_results 已产生
    - 6 写作评审：body_chapters 已产生
    - 7 降AIGC导出：latex_source / pdf_path / docx_path / export_formats 存在
    """
    current = 0
    ident_failed = bool(state.get("identification_failed"))

    # 0 选题 / 1 文献：研究方向已确定
    if _has_field(state, "research_direction", is_dict=True):
        current = 2

    # 2 数据清洗。只有「已选题 + 已有数据」才进入识别站。
    # 只上传、还没选题时停在选题（0），不能假装已经在验识别。
    has_data = (
        _has_field(state, "cleaning_report")
        or _has_field(state, "cleaned_datasets")
        or _has_field(state, "uploaded_datasets")
    )
    if has_data and current >= 2:
        current = 3

    # 3 识别策略：诊断已产生
    if _has_field(state, "identification_diag", is_dict=True):
        current = 4

    # 4 估计建模：估计器已跑（不是正文出现）
    estimate = state.get("estimate") or {}
    if isinstance(estimate, dict) and estimate.get("produced_by") == "estimate":
        current = 5

    # 5 稳健性审计
    robustness = state.get("robustness_results")
    if isinstance(robustness, dict) and (
        robustness.get("produced_by") == "robustness_check"
        or "diagnostics" in robustness
        or robustness
    ):
        current = 6
    elif _has_field(state, "robustness_results"):
        current = 6

    # 6 写作评审：正文章节已生成
    if _has_field(state, "body_chapters") or _has_field(state, "writing_report") or _has_field(state, "review_report"):
        current = 7

    # 7 降AIGC导出：存在任一导出产物
    if (
        _has_field(state, "latex_source")
        or _has_field(state, "pdf_path")
        or _has_field(state, "docx_path")
        or _has_field(state, "export_formats")
    ):
        current = 8

    # 识别阶段失败 → 停在识别阶段（index 3），标记 interrupt
    if ident_failed and current == 4:
        current = 3

    return current, ident_failed


@router.get(
    "/sessions/{session_id}/journey",
    response_model=JourneyResponse,
)
async def get_journey(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> JourneyResponse:
    """返回 8 阶段研究旅程进度（收敛版，去掉了无节点的"表格图形"站）。

    每个阶段状态：``pending`` / ``active`` / ``completed`` / ``interrupt``。
    currentStage 为正在进行的阶段；若 state 为空，降级为第 0 站 active、
    其余 pending，不抛错。
    """
    require_session_ownership(session_id, current_user)
    try:
        state = facade.get_state(session_id)
    except Exception:
        # 未知 session：get_state 已抛 404，直接透传。
        raise

    if not state:
        stages = [
            JourneyStageItem(
                status="active" if i == 0 else "pending",
                canIntervene=bool(s["canIntervene"]),
            )
            for i, s in enumerate(_JOURNEY_STAGES)
        ]
        return JourneyResponse(currentStage=0, stages=stages)

    current, ident_failed = _infer_journey(state)
    got_interrupt = ident_failed and current == 3

    stages = []
    for i, s in enumerate(_JOURNEY_STAGES):
        if i < current:
            status = "completed"
        elif i == current:
            status = "interrupt" if got_interrupt else "active"
        else:
            status = "pending"
        stages.append(
            JourneyStageItem(status=status, canIntervene=bool(s["canIntervene"]))
        )

    return JourneyResponse(currentStage=current, stages=stages)


def _self_register() -> None:
    """Attach this router to the FastAPI app on import.

    与 eda.py / chapter.py 模式一致：idempotent via ``_REGISTERED`` flag。
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

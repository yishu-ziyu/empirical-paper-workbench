"""ADR-0004 Stage 1: review_chapter 后的条件边路由。

route_after_review 接在 review_chapter 节点之后。

路由逻辑（修订版：删除"达上限即放行"）：
- review_enabled == False → 委托 route_after_chapter(state)（评审整体关闭，无门可守）
- 无评审分数 / 无 review_chapter_index / 索引越界 → 委托 route_after_chapter(state)
- score >= threshold → 委托 route_after_chapter(state)（真正通过）
- score < threshold 且 iteration < max → "generate_chapter"（重生成当前章）
- score < threshold 且 iteration >= max → **"hitl_pause"**

最后一条是北极星硬规则："评审未通过的章节不许静默进入论文"。预算耗尽时
不再自动推进到下一章 / 导出，而是把裁决权交还给人（HITL）。章节要出文，
要么过审，要么人在审批端点上显式 force（并留下 approved_forced 标记）。
"""
from __future__ import annotations

from state import EconPaperState

# 与 review_chapter.REVIEW_SCORE_THRESHOLD 保持一致
_REVIEW_SCORE_THRESHOLD = 0.7


def route_after_review(state: EconPaperState) -> str:
    """review_chapter 后的条件边路由。

    返回值与 route_after_chapter 兼容（"generate_chapter" / "translate_code"）。
    """
    from graph import route_after_chapter

    review_enabled = state.get("review_enabled", True)
    if not review_enabled:
        return route_after_chapter(state)

    review_scores = state.get("review_scores", [])
    review_chapter_index = state.get("review_chapter_index")
    review_iteration = state.get("review_iteration", 0)
    max_iterations = min(state.get("max_review_iterations", 2), 3)

    # 没有评审分数或评审章节索引 → 委托原路由
    if not review_scores or review_chapter_index is None:
        return route_after_chapter(state)

    # 越界保护
    if review_chapter_index >= len(review_scores):
        return route_after_chapter(state)

    score = review_scores[review_chapter_index]

    # 真正通过 → 委托原路由
    if score >= _REVIEW_SCORE_THRESHOLD:
        return route_after_chapter(state)

    # 不通过且未达上限 → 重生成（review_chapter 已回退 current_chapter_index）
    if review_iteration < max_iterations:
        return "generate_chapter"

    # 预算耗尽仍不合格 → 不许静默放行，交给人裁决
    return "hitl_pause"

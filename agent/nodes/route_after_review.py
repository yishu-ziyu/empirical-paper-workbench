"""ADR-0004 Stage 1: review_chapter 后的条件边路由。

route_after_review 接在 review_chapter 节点之后，返回值与 route_after_chapter
兼容（"generate_chapter" / "translate_code"）。

路由逻辑：
- review_enabled == False → 委托 route_after_chapter(state)
- review_scores[review_chapter_index] >= threshold
  或 review_iteration >= max_review_iterations → 委托 route_after_chapter(state)
- 否则 → "generate_chapter"（重生成当前章，review_chapter 已回退 idx）
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

    # 通过或达上限 → 委托原路由
    if score >= _REVIEW_SCORE_THRESHOLD or review_iteration >= max_iterations:
        return route_after_chapter(state)

    # 不通过且未达上限 → 重生成（review_chapter 已回退 current_chapter_index）
    return "generate_chapter"

"""ADR-0004 Stage 1: review_chapter 后的条件边路由。

route_after_review 接在 review_chapter 节点之后。

路由逻辑（修订版：删除"达上限即放行"）：
- review_enabled == False → 委托 `_advance`（评审整体关闭，无门可守）
- 无评审分数 / 无 review_chapter_index / 索引越界 → 委托 `_advance`
- score >= threshold → 委托 `_advance`（真正通过）
- score < threshold 且 iteration < max → "generate_chapter"（重生成当前章）
- score < threshold 且 iteration >= max → **"hitl_pause"**

最后一条是北极星硬规则："评审未通过的章节不许静默进入论文"。预算耗尽时
不再自动推进到下一章 / 导出，而是把裁决权交还给人（HITL）。章节要出文，
要么过审，要么人在审批端点上显式 force（并留下 approved_forced 标记）。

注：本章节循环路由为 Facade HITL 单点调用驱动的附加逻辑（不在预写图中）。
原先委托的 ``agent.graph.route_after_chapter`` 已随预写图收敛删除，其"6 章
推进"判定在此内联为 ``_advance``，避免残留对已删 GRAPH 函数的引用。
"""
from __future__ import annotations

from ..state import EconPaperState

# 与 review_chapter.REVIEW_SCORE_THRESHOLD 保持一致
_REVIEW_SCORE_THRESHOLD = 0.7

# 6 章类型数（intro / lit_review / data_desc / methods / results / conclusion）
_CHAPTER_COUNT = 6


def _advance(state: EconPaperState) -> str:
    """章节通过后的推进判定（原 route_after_chapter 内联）。

    - 无 outline 或无 current_chapter_index（legacy 流）→ translate_code（不循环）
    - ``current_chapter_index`` < 6 → ``generate_chapter``（生成下一章）
    - ``current_chapter_index`` >= 6 → ``translate_code``（6 章全部完成）
    """
    outline = state.get("outline")
    idx = state.get("current_chapter_index")
    if not outline or idx is None:
        return "translate_code"
    if idx < _CHAPTER_COUNT:
        return "generate_chapter"
    return "translate_code"


def route_after_review(state: EconPaperState) -> str:
    """review_chapter 后的条件边路由。

    返回值与预写图的章节推进逻辑兼容（"generate_chapter" / "translate_code"）。
    """
    review_enabled = state.get("review_enabled", True)
    if not review_enabled:
        return _advance(state)

    review_scores = state.get("review_scores", [])
    review_chapter_index = state.get("review_chapter_index")
    review_iteration = state.get("review_iteration", 0)
    max_iterations = min(state.get("max_review_iterations", 2), 3)

    # 没有评审分数或评审章节索引 → 委托原推进路由
    if not review_scores or review_chapter_index is None:
        return _advance(state)

    # 越界保护
    if review_chapter_index >= len(review_scores):
        return _advance(state)

    score = review_scores[review_chapter_index]

    # 真正通过 → 委托原推进路由
    if score >= _REVIEW_SCORE_THRESHOLD:
        return _advance(state)

    # 不通过且未达上限 → 重生成（review_chapter 已回退 current_chapter_index）
    if review_iteration < max_iterations:
        return "generate_chapter"

    # 预算耗尽仍不合格 → 不许静默放行，交给人裁决
    return "hitl_pause"

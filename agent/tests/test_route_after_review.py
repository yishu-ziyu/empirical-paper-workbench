"""ADR-0004 Stage 1: route_after_review 条件边测试。

契约（修订：删除"达上限即放行"）：
1. review_enabled=False → 委托 route_after_chapter
2. 评审通过（score >= 0.7）→ 委托 route_after_chapter
3. 评审不通过且未达上限 → "generate_chapter"（重生成）
4. 评审不通过但达上限 → "hitl_pause"（交人裁决，不许静默放行）
5. 无评审分数或 review_chapter_index → 委托 route_after_chapter
6. 返回值 ∈ {"generate_chapter", "translate_code", "hitl_pause"}
"""
from __future__ import annotations

import pytest

from nodes.route_after_review import route_after_review

from conftest import make_state


def _review_state(
    score: float = 0.5,
    review_iteration: int = 0,
    max_review_iterations: int = 2,
    review_chapter_index: int = 0,
    review_enabled: bool = True,
    current_chapter_index: int = 1,
) -> dict:
    """构造带评审字段的 state。"""
    return make_state(
        review_enabled=review_enabled,
        current_chapter_index=current_chapter_index,
        outline=[{"type": "intro"}] * 6,
        review_scores=[score],
        review_iteration=review_iteration,
        max_review_iterations=max_review_iterations,
        review_chapter_index=review_chapter_index,
    )


# ---------------------------------------------------------------------------
# review_enabled=False → 委托 route_after_chapter
# ---------------------------------------------------------------------------
def test_review_disabled_delegates_to_route_after_chapter():
    """review_enabled=False 时委托 route_after_chapter。"""
    state = _review_state(review_enabled=False, current_chapter_index=3)
    result = route_after_review(state)
    assert result in ("generate_chapter", "translate_code")


def test_review_disabled_current_below_six_returns_generate_chapter():
    """review_enabled=False 且 current < 6 → 委托返回 generate_chapter。"""
    state = _review_state(review_enabled=False, current_chapter_index=3)
    result = route_after_review(state)
    assert result == "generate_chapter"


def test_review_disabled_current_at_six_returns_translate_code():
    """review_enabled=False 且 current >= 6 → 委托返回 translate_code。"""
    state = _review_state(review_enabled=False, current_chapter_index=6)
    result = route_after_review(state)
    assert result == "translate_code"


# ---------------------------------------------------------------------------
# 评审通过（score >= 0.7）→ 委托 route_after_chapter
# ---------------------------------------------------------------------------
def test_review_score_above_threshold_delegates():
    """评审通过（score >= 0.7）委托 route_after_chapter。"""
    state = _review_state(score=0.9, current_chapter_index=3)
    result = route_after_review(state)
    # current=3 < 6 → route_after_chapter 返回 generate_chapter
    assert result == "generate_chapter"


def test_review_score_above_threshold_at_six_returns_translate():
    """评审通过且 6 章完成 → translate_code。"""
    state = _review_state(score=0.9, current_chapter_index=6)
    result = route_after_review(state)
    assert result == "translate_code"


def test_review_score_exactly_threshold_delegates():
    """score == 0.7（恰好阈值）→ 委托 route_after_chapter。"""
    state = _review_state(score=0.7, current_chapter_index=3)
    result = route_after_review(state)
    assert result == "generate_chapter"


# ---------------------------------------------------------------------------
# 评审不通过且未达上限 → "generate_chapter"（重生成）
# ---------------------------------------------------------------------------
def test_review_score_below_threshold_and_iteration_below_max_returns_generate_chapter():
    """评审不通过且未达上限 → 重生成。"""
    state = _review_state(
        score=0.5,
        review_iteration=0,
        max_review_iterations=2,
        current_chapter_index=1,
    )
    result = route_after_review(state)
    assert result == "generate_chapter"


def test_review_low_score_iteration_one_returns_generate_chapter():
    """低分 + iteration=1 < max=2 → 重生成。"""
    state = _review_state(
        score=0.3,
        review_iteration=1,
        max_review_iterations=2,
    )
    result = route_after_review(state)
    assert result == "generate_chapter"


# ---------------------------------------------------------------------------
# 评审不通过但达上限 → 委托 route_after_chapter
# ---------------------------------------------------------------------------
def test_review_score_below_threshold_but_iteration_at_max_goes_to_hitl():
    """评审不通过且预算耗尽 → hitl_pause，不许静默推进到下一章。"""
    state = _review_state(
        score=0.5,
        review_iteration=2,
        max_review_iterations=2,
        current_chapter_index=3,
    )
    result = route_after_review(state)
    assert result == "hitl_pause"


def test_review_score_below_threshold_iteration_at_max_six_chapters_done_hitl():
    """低分 + 达上限 + 即使 6 章全部写完 → hitl_pause，不许进导出。"""
    state = _review_state(
        score=0.5,
        review_iteration=2,
        max_review_iterations=2,
        current_chapter_index=6,
    )
    result = route_after_review(state)
    assert result == "hitl_pause"


# ---------------------------------------------------------------------------
# 无评审数据 → 委托 route_after_chapter
# ---------------------------------------------------------------------------
def test_no_review_scores_delegates():
    """无 review_scores → 委托 route_after_chapter。"""
    state = make_state(
        review_enabled=True,
        current_chapter_index=3,
        outline=[{"type": "intro"}] * 6,
        review_iteration=0,
        max_review_iterations=2,
        review_chapter_index=0,
        # 故意不设 review_scores
    )
    result = route_after_review(state)
    assert result == "generate_chapter"


def test_no_review_chapter_index_delegates():
    """无 review_chapter_index → 委托 route_after_chapter。"""
    state = make_state(
        review_enabled=True,
        current_chapter_index=3,
        outline=[{"type": "intro"}] * 6,
        review_scores=[0.5],
        review_iteration=0,
        max_review_iterations=2,
        # 故意不设 review_chapter_index
    )
    result = route_after_review(state)
    assert result == "generate_chapter"


def test_review_chapter_index_out_of_range_delegates():
    """review_chapter_index 越界 → 委托 route_after_chapter。"""
    state = _review_state(
        score=0.5,
        review_chapter_index=5,  # 越界（review_scores 只有 1 个元素）
        current_chapter_index=3,
    )
    result = route_after_review(state)
    assert result == "generate_chapter"


# ---------------------------------------------------------------------------
# 硬上限 3
# ---------------------------------------------------------------------------
def test_route_after_review_max_iterations_hard_cap_3():
    """max_review_iterations=5 时硬上限截断为 3，iteration=3 即视为达上限。"""
    state = _review_state(
        score=0.5,
        review_iteration=3,
        max_review_iterations=5,  # 用户设 5，硬上限 3
        current_chapter_index=3,
    )
    result = route_after_review(state)
    # iteration=3 >= 硬上限 3 且未过审 → hitl_pause
    assert result == "hitl_pause"


# ---------------------------------------------------------------------------
# 返回值兼容性
# ---------------------------------------------------------------------------
def test_route_after_review_always_returns_valid_target():
    """route_after_review 返回值必须是 'generate_chapter' 或 'translate_code'。"""
    for current_idx in range(0, 8):
        state = _review_state(
            score=0.9,
            current_chapter_index=current_idx,
        )
        result = route_after_review(state)
        assert result in ("generate_chapter", "translate_code"), (
            f"current={current_idx} 时返回非法值 {result!r}"
        )

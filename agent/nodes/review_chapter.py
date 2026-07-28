"""ADR-0004 Stage 3: 章节自动评审节点。

对当前刚生成的章节（review_chapter_index = current_chapter_index - 1）评审，
产出 5 维 rubric 评分 + 反馈 + 修改建议。评审不通过且未达迭代上限时，
回退 current_chapter_index 触发重生成。

设计要点（ADR 0004 §5、§11.2）：
- 评审节点只读 body_chapters，绝不写 body_chapters（Fitness Function 强制）
- call_review_llm 是模块级函数，便于 monkeypatch（与 generate_chapter.call_llm 同模式）；
  Stage 3 默认接 mock_review_llm（nodes.review_sources.mock_review），
  生产环境可通过 monkeypatch 替换为真实 LLM
- max_review_iterations 硬上限 3（即使用户设 5，也截断为 3）
- 空章节不触发回退（避免无限循环）
- 强制通过（iteration >= max）时不重置 review_iteration，让 route_after_review
  能据此委托 route_after_chapter；新章节检测到 review_chapter_index 变化时重置
"""
from __future__ import annotations

from typing import Any, List

from protocols import ReviewOutput, ReviewRubric
from state import EconPaperState

# 评审通过阈值（运行时常量，不入 state）
REVIEW_SCORE_THRESHOLD = 0.7

# 综合分加权公式
# 0.3*endogeneity + 0.25*identification + 0.2*robustness + 0.15*contribution + 0.1*readability
RUBRIC_WEIGHTS = {
    "endogeneity": 0.3,
    "identification": 0.25,
    "robustness": 0.2,
    "contribution": 0.15,
    "readability": 0.1,
}


def call_review_llm(
    chapter_content: str,
    rubric_template: ReviewRubric,
    research_direction: str,
    literature_entries: List[Any],
) -> dict:
    """模块级 LLM 调用函数（与 generate_chapter.call_llm 同一 monkeypatch 模式）。

    ADR-0008: 通过 LLMRouter 调用评审 LLM。
    - provider == "mock"（默认）→ 调 mock_review_llm（开发/测试）
    - provider == "anthropic" / "openai" → Stage 2 接真实 LLM；当前占位仍调 mock

    通过 monkeypatch 可替换为真实 LLM 或其他 mock（测试接缝不变）。
    """
    from llm.router import router
    from nodes.review_sources.mock_review import mock_review_llm

    config = router.get_config("review")

    if config.provider == "mock":
        # 开发/测试：用 mock_review_llm（确定性规则评分）
        return mock_review_llm(
            chapter_content, rubric_template, research_direction, literature_entries
        )

    # 生产环境：调真实 LLM（通过统一入口）
    # 当前占位：仍用 mock（Stage 2 接 langchain-anthropic / openai）
    return mock_review_llm(
        chapter_content, rubric_template, research_direction, literature_entries
    )


def _compute_composite_score(rubric: ReviewRubric) -> float:
    """加权综合分：0.3*endo + 0.25*ident + 0.2*rob + 0.15*contrib + 0.1*read。"""
    total = 0.0
    for dim, weight in RUBRIC_WEIGHTS.items():
        total += rubric.get(dim, 0.0) * weight
    return total


def review_chapter(state: EconPaperState) -> ReviewOutput:
    """对当前刚生成的章节评审。

    1. review_enabled == False → 返回 {} (no-op)
    2. 计算 idx = current_chapter_index - 1（generate_chapter 已自增）
    3. idx < 0 或 body_chapters 为空 → 返回 {}
    4. 检测新章节：若 state['review_chapter_index'] != idx，说明换了章节，重置 review_iteration = 0
    5. 读 body_chapters[idx].content + research_direction + literature_entries
    6. 调 call_review_llm 得 rubric + feedback + suggestions
    7. 加权算综合分
    8. 写 review_feedback[idx] / revision_suggestions[idx] / review_scores[idx] / review_rubrics[idx]
    9. 若综合分 < threshold 且 review_iteration < max_review_iterations:
       - 写 current_chapter_index = idx（回退）
       - 写 review_iteration += 1
       若综合分 >= threshold（真正通过）:
       - 写 review_iteration = 0（重置，为下一章准备）
       否则（强制通过，iteration >= max）:
       - 不重置 review_iteration（保留 max 值，让 route_after_review 据此委托）
    10. 写 review_chapter_index = idx
    11. 返回 ReviewOutput（不含 body_chapters）
    """
    review_enabled = state.get("review_enabled", True)
    if not review_enabled:
        return {}

    current_idx = state.get("current_chapter_index", 0)
    idx = current_idx - 1
    if idx < 0:
        return {}

    body_chapters = state.get("body_chapters", [])
    if idx >= len(body_chapters):
        return {}

    # 读现有评审列表（可能为空或部分填充），复制为可变列表
    review_feedback: List[str] = list(state.get("review_feedback", []) or [])
    revision_suggestions: List[str] = list(state.get("revision_suggestions", []) or [])
    review_scores: List[float] = list(state.get("review_scores", []) or [])
    review_rubrics: List[Any] = list(state.get("review_rubrics", []) or [])

    # 扩展列表到 idx+1（用占位符填充）
    while len(review_feedback) <= idx:
        review_feedback.append("")
    while len(revision_suggestions) <= idx:
        revision_suggestions.append("")
    while len(review_scores) <= idx:
        review_scores.append(0.0)
    while len(review_rubrics) <= idx:
        review_rubrics.append({})

    chapter = body_chapters[idx]
    chapter_content = chapter.get("content", "") if isinstance(chapter, dict) else ""

    # 空章节：评分 0，但不触发回退（避免空章节无限重生成）
    if not chapter_content:
        review_feedback[idx] = "章节内容为空，跳过评审"
        revision_suggestions[idx] = ""
        review_scores[idx] = 0.0
        review_rubrics[idx] = {
            "endogeneity": 0.0, "identification": 0.0,
            "robustness": 0.0, "contribution": 0.0, "readability": 0.0,
        }
        return {
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "review_scores": review_scores,
            "review_rubrics": review_rubrics,
            "review_iteration": 0,
            "review_chapter_index": idx,
        }

    # 新章节检测：若上一轮 review_chapter_index != idx，说明换了章节，重置迭代
    prev_review_idx = state.get("review_chapter_index")
    if prev_review_idx is not None and prev_review_idx != idx:
        review_iteration = 0
    else:
        review_iteration = state.get("review_iteration", 0)

    research_direction = state.get("research_direction", "")
    literature_entries = state.get("literature_entries", [])
    max_iterations = min(state.get("max_review_iterations", 2), 3)

    rubric_template = ReviewRubric()
    llm_result = call_review_llm(
        chapter_content, rubric_template, research_direction, literature_entries,
    )
    rubric = llm_result["rubric"]
    feedback = llm_result["feedback"]
    suggestions = llm_result["suggestions"]
    score = _compute_composite_score(rubric)

    review_feedback[idx] = feedback
    revision_suggestions[idx] = suggestions
    review_scores[idx] = score
    review_rubrics[idx] = rubric

    if score < REVIEW_SCORE_THRESHOLD and review_iteration < max_iterations:
        # 回退：重生成当前章
        return {
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "review_scores": review_scores,
            "review_rubrics": review_rubrics,
            "review_iteration": review_iteration + 1,
            "review_chapter_index": idx,
            "current_chapter_index": idx,  # 回退
        }
    elif score >= REVIEW_SCORE_THRESHOLD:
        # 真正通过：重置迭代，为下一章准备
        return {
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "review_scores": review_scores,
            "review_rubrics": review_rubrics,
            "review_iteration": 0,
            "review_chapter_index": idx,
        }
    else:
        # 强制通过（iteration >= max）：保留 review_iteration，让 route_after_review
        # 能据此委托 route_after_chapter；下一章评审时由新章节检测重置
        return {
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "review_scores": review_scores,
            "review_rubrics": review_rubrics,
            "review_iteration": review_iteration,
            "review_chapter_index": idx,
        }

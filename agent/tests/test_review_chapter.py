"""ADR-0004 Stage 1: review_chapter 节点测试。

契约：
1. review_enabled=False → 返回 {}
2. current_chapter_index=0（idx=-1）→ 返回 {}
3. 正常评审，分数 >= threshold → 通过，review_iteration=0，不写 current_chapter_index
4. 低分触发回退，current_chapter_index 回退，review_iteration +1
5. 达 max_review_iterations 时强制通过（不回退），review_iteration 保留
6. 空章节不触发回退
7. review_chapter 返回值不含 body_chapters（Fitness Function）
8. 综合分加权公式正确
9. 新章节检测：review_chapter_index 变化时重置 review_iteration
10. max_review_iterations 硬上限 3
"""
from __future__ import annotations

import pytest

from nodes.review_chapter import (
    REVIEW_SCORE_THRESHOLD,
    apply_association_review_guard,
    _compute_composite_score,
    call_review_llm,
    invoke_review_llm,
    review_chapter,
)
from protocols import ReviewRubric

from conftest import make_state, make_write_ready_state


def _make_chapter(content: str = "章节内容") -> dict:
    """构造一个带 content 的章节。"""
    return {
        "type": "intro",
        "title": "引言",
        "content": content,
        "status": "generated",
        "versions": [content],
        "chapter_index": 0,
    }


def _mock_llm_return(rubric: dict, feedback: str = "反馈", suggestions: str = "建议"):
    """构造 call_review_llm 的返回值。"""
    return {"rubric": rubric, "feedback": feedback, "suggestions": suggestions}


HIGH_SCORE_RUBRIC = {
    "endogeneity": 0.9, "identification": 0.9,
    "robustness": 0.9, "contribution": 0.9, "readability": 0.9,
}
LOW_SCORE_RUBRIC = {
    "endogeneity": 0.1, "identification": 0.1,
    "robustness": 0.1, "contribution": 0.1, "readability": 0.1,
}


# ---------------------------------------------------------------------------
# no-op 分支
# ---------------------------------------------------------------------------
def test_review_disabled_returns_empty():
    """review_enabled=False 时返回 {}。"""
    state = make_state(
        review_enabled=False,
        current_chapter_index=1,
        body_chapters=[_make_chapter()],
    )
    result = review_chapter(state)
    assert result == {}


def test_review_first_chapter_no_idx():
    """current_chapter_index=0 时 idx=-1，返回 {}。"""
    state = make_state(
        review_enabled=True,
        current_chapter_index=0,
    )
    result = review_chapter(state)
    assert result == {}


def test_review_idx_out_of_range_returns_empty():
    """idx >= len(body_chapters) 时返回 {}。"""
    state = make_state(
        review_enabled=True,
        current_chapter_index=2,
        body_chapters=[_make_chapter()],  # 只有 1 章，idx=1 越界
    )
    result = review_chapter(state)
    assert result == {}


# ---------------------------------------------------------------------------
# 正常评审 - 通过
# ---------------------------------------------------------------------------
def test_review_normal_pass(monkeypatch):
    """正常评审，分数 >= threshold，通过。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_make_chapter()],
        research_direction="test",
        max_review_iterations=2,
    )
    result = review_chapter(state)

    assert "review_feedback" in result
    assert result["review_feedback"][0] == "反馈"
    assert result["review_scores"][0] == _compute_composite_score(HIGH_SCORE_RUBRIC)
    assert result["review_iteration"] == 0
    assert result["review_chapter_index"] == 0
    # 通过时不写 current_chapter_index（不回退）
    assert "current_chapter_index" not in result


# ---------------------------------------------------------------------------
# 低分触发回退
# ---------------------------------------------------------------------------
def test_review_low_score_triggers_rollback(monkeypatch):
    """低分触发回退，current_chapter_index 回退，review_iteration +1。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(LOW_SCORE_RUBRIC),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_make_chapter()],
        research_direction="test",
        max_review_iterations=2,
        review_iteration=0,
    )
    result = review_chapter(state)

    assert result["review_scores"][0] < REVIEW_SCORE_THRESHOLD
    assert result["review_iteration"] == 1
    assert result["current_chapter_index"] == 0  # 回退到 idx=0
    assert result["review_chapter_index"] == 0


def test_review_low_score_second_iteration(monkeypatch):
    """第二次低分回退，review_iteration 从 1 → 2。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(LOW_SCORE_RUBRIC),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_make_chapter()],
        research_direction="test",
        max_review_iterations=2,
        review_iteration=1,
        review_chapter_index=0,
    )
    result = review_chapter(state)

    assert result["review_iteration"] == 2
    assert result["current_chapter_index"] == 0  # 仍回退


# ---------------------------------------------------------------------------
# 达上限强制通过
# ---------------------------------------------------------------------------
def test_review_max_iteration_forced_pass(monkeypatch):
    """达 max_review_iterations 时强制通过（不回退）。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(LOW_SCORE_RUBRIC),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_make_chapter()],
        research_direction="test",
        max_review_iterations=2,
        review_iteration=2,  # 已达上限
        review_chapter_index=0,
    )
    result = review_chapter(state)

    # 强制通过：不回退
    assert "current_chapter_index" not in result
    # review_iteration 保留（不重置为 0），让 route_after_review 据此委托
    assert result["review_iteration"] == 2
    assert result["review_scores"][0] < REVIEW_SCORE_THRESHOLD


def test_review_max_iteration_hard_cap_3(monkeypatch):
    """max_review_iterations=5 时硬上限截断为 3。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(LOW_SCORE_RUBRIC),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_make_chapter()],
        research_direction="test",
        max_review_iterations=5,  # 用户设 5
        review_iteration=3,       # 已达硬上限 3
        review_chapter_index=0,
    )
    result = review_chapter(state)

    # iteration=3 >= 硬上限 3 → 强制通过
    assert "current_chapter_index" not in result
    assert result["review_iteration"] == 3


# ---------------------------------------------------------------------------
# 空章节
# ---------------------------------------------------------------------------
def test_review_empty_chapter_no_rollback():
    """空章节不触发回退（避免空章节无限重生成）。"""
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_make_chapter(content="")],  # 空内容
        research_direction="test",
        max_review_iterations=2,
    )
    result = review_chapter(state)

    assert result["review_scores"][0] == 0.0
    assert result["review_feedback"][0] == "章节内容为空，跳过评审"
    assert result["review_iteration"] == 0
    # 空章节不回退
    assert "current_chapter_index" not in result


# ---------------------------------------------------------------------------
# Fitness Function
# ---------------------------------------------------------------------------
def test_review_does_not_write_body_chapters():
    """Fitness Function: review_chapter 返回值不含 body_chapters 键。"""
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_make_chapter()],
        research_direction="test",
        max_review_iterations=2,
    )
    result = review_chapter(state)
    assert "body_chapters" not in result, "review_chapter 不得写 body_chapters"


def test_review_does_not_write_body_chapters_empty():
    """Fitness Function: 空章节分支也不写 body_chapters。"""
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_make_chapter(content="")],
    )
    result = review_chapter(state)
    assert "body_chapters" not in result


def test_review_does_not_write_body_chapters_disabled():
    """Fitness Function: review_enabled=False 分支也不写 body_chapters。"""
    state = make_state(
        review_enabled=False,
        current_chapter_index=1,
        body_chapters=[_make_chapter()],
    )
    result = review_chapter(state)
    assert "body_chapters" not in result


# ---------------------------------------------------------------------------
# 综合分加权公式
# ---------------------------------------------------------------------------
def test_composite_score_weighted():
    """综合分加权公式正确：全 1.0 应得 1.0。"""
    rubric = {"endogeneity": 1.0, "identification": 1.0,
              "robustness": 1.0, "contribution": 1.0, "readability": 1.0}
    score = _compute_composite_score(rubric)
    assert score == pytest.approx(1.0)


def test_composite_score_zero():
    """全 0.0 应得 0.0。"""
    rubric = {"endogeneity": 0.0, "identification": 0.0,
              "robustness": 0.0, "contribution": 0.0, "readability": 0.0}
    score = _compute_composite_score(rubric)
    assert score == pytest.approx(0.0)


def test_composite_score_weighted_partial():
    """加权公式：只 endogeneity=1.0，其余 0 → 0.3。"""
    rubric = {"endogeneity": 1.0, "identification": 0.0,
              "robustness": 0.0, "contribution": 0.0, "readability": 0.0}
    score = _compute_composite_score(rubric)
    assert score == pytest.approx(0.3)


def test_composite_score_placeholder_0_5():
    """占位 LLM 返回全 0.5 → 综合分 0.5。"""
    rubric = {"endogeneity": 0.5, "identification": 0.5,
              "robustness": 0.5, "contribution": 0.5, "readability": 0.5}
    score = _compute_composite_score(rubric)
    assert score == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# 新章节检测
# ---------------------------------------------------------------------------
def test_review_new_chapter_resets_iteration(monkeypatch):
    """新章节检测：review_chapter_index != idx 时重置 review_iteration=0。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=2,  # idx=1，新章节
        body_chapters=[_make_chapter(), _make_chapter()],
        research_direction="test",
        max_review_iterations=2,
        review_iteration=2,            # 上一章的残留迭代
        review_chapter_index=0,        # 上一章是 0，现在是 1 → 新章节
    )
    result = review_chapter(state)

    # 新章节重置 iteration=0，且高分通过
    assert result["review_iteration"] == 0
    assert result["review_chapter_index"] == 1


def test_review_same_chapter_keeps_iteration(monkeypatch):
    """同一章节重评审：review_chapter_index == idx 时保留 review_iteration。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(LOW_SCORE_RUBRIC),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,  # idx=0
        body_chapters=[_make_chapter()],
        research_direction="test",
        max_review_iterations=2,
        review_iteration=1,            # 已迭代 1 次
        review_chapter_index=0,        # 同一章
    )
    result = review_chapter(state)

    # 同一章，iteration 从 1 → 2
    assert result["review_iteration"] == 2


# ---------------------------------------------------------------------------
# 列表按 idx 对齐
# ---------------------------------------------------------------------------
def test_review_writes_to_correct_index(monkeypatch):
    """评审结果写到正确的 idx 位置（第 2 章 → index 1）。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC, feedback="第2章反馈"),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=2,  # idx=1
        body_chapters=[_make_chapter(), _make_chapter()],
        research_direction="test",
    )
    result = review_chapter(state)

    assert result["review_feedback"][1] == "第2章反馈"
    assert result["review_scores"][1] == _compute_composite_score(HIGH_SCORE_RUBRIC)
    # idx=0 未被本轮评审动过（保持占位）
    assert result["review_feedback"][0] == ""


def test_review_preserves_existing_review_lists(monkeypatch):
    """评审新章节时保留已有章节的评审结果。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC, feedback="第2章反馈"),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=2,  # idx=1
        body_chapters=[_make_chapter(), _make_chapter()],
        research_direction="test",
        review_feedback=["第1章反馈"],       # 已有第 1 章评审
        review_scores=[0.95],
        review_rubrics=[HIGH_SCORE_RUBRIC],
        revision_suggestions=["第1章建议"],
    )
    result = review_chapter(state)

    # 第 1 章保留
    assert result["review_feedback"][0] == "第1章反馈"
    assert result["review_scores"][0] == 0.95
    # 第 2 章新增
    assert result["review_feedback"][1] == "第2章反馈"


# ---------------------------------------------------------------------------
# 关联主张检查（rubric 之前）
# ---------------------------------------------------------------------------
def test_association_forbidden_claim_caps_score_and_rolls_back(monkeypatch):
    """命中禁用主张：grounding_failures 含码，综合分封顶 0.50 并回炉。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    content = (
        "本文识别了因果。"
        r"$y_i=\alpha+\beta D_i+u_i$ "
        "外生性 sutva。"
        + ("论" * 200)
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[{
            "type": "methods",
            "title": "方法",
            "content": content,
            "status": "generated",
            "versions": [content],
            "chapter_index": 0,
            "method": "ols",
        }],
        claim="association",
        research_direction={"method": "ols", "claim": "association"},
        max_review_iterations=2,
        review_iteration=0,
    )
    result = review_chapter(state)
    assert "causal_claim_forbidden" in result["grounding_failures"]
    assert result["review_scores"][0] <= 0.50
    assert result["current_chapter_index"] == 0


def test_allowed_causal_phrases_do_not_trigger_forbidden(monkeypatch):
    """允许句不记 causal_claim_forbidden。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    content = (
        "无法做因果识别，仅解释为相关。"
        r"$y_i=\alpha+\beta D_i+u_i$ "
        "外生性 sutva。"
        + ("论" * 200)
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[{
            "type": "methods",
            "title": "方法",
            "content": content,
            "status": "generated",
            "versions": [content],
            "chapter_index": 0,
            "method": "ols",
        }],
        claim="association",
        research_direction={"method": "ols", "claim": "association"},
        max_review_iterations=2,
    )
    result = review_chapter(state)
    assert "causal_claim_forbidden" not in result.get("grounding_failures", [])
    assert result["review_scores"][0] >= 0.7
    assert "current_chapter_index" not in result


def test_causal_claim_other_forbidden_substrings(monkeypatch):
    """因果效应显著 / 识别策略成立 / 解决内生性 同样回炉。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    for phrase in ("因果效应显著", "识别策略成立", "解决内生性"):
        content = phrase + r" $y_i=\alpha+\beta D_i+u_i$ 外生性 sutva。" + ("论" * 200)
        state = make_state(
            review_enabled=True,
            current_chapter_index=1,
            body_chapters=[{
                "type": "methods",
                "content": content,
                "status": "generated",
            }],
            claim="association",
            max_review_iterations=2,
        )
        result = review_chapter(state)
        assert "causal_claim_forbidden" in result["grounding_failures"], phrase
        assert result["review_scores"][0] <= 0.50, phrase
        assert result.get("current_chapter_index") == 0, phrase


def test_association_methods_fixture_passes_without_rollback():
    """硬条 6：关联方法章走 mock 真路径，综合分 >= 0.7 且不回退。"""
    content = (
        "本节给出条件关联的计量模型。本文用普通最小二乘描述收入与处理变量"
        "之间的条件关联，系数读作相关强度。\n\n"
        "## 模型设定\n"
        "在控制可观测协变量后，本文估计条件均值上的线性关联。"
        "该系数应读作相关，而不是处理带来的平均效应。\n\n"
        "## 计量模型\n"
        "主回归写为 $y_i=\\alpha+\\beta D_i+u_i$。其中 $y_i$ 是结果变量，"
        "$D_i$ 是关注的解释变量，$\\alpha$ 是截距，$\\beta$ 是条件关联系数，"
        "$u_i$ 是误差项。下标 $i$ 表示个体。\n\n"
        "## 解释边界\n"
        "若遗漏不可观测因素，该系数不能当成处理效应。"
        "后文稳健性部分更换控制变量，检查相关方向是否保持。"
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[{
            "type": "methods",
            "title": "方法",
            "content": content,
            "status": "generated",
            "versions": [content],
            "chapter_index": 0,
            "method": "ols",
        }],
        claim="association",
        research_direction={"method": "ols", "claim": "association"},
        star_rating=None,
        max_review_iterations=2,
    )
    result = review_chapter(state)
    assert result["review_rubrics"][0]["endogeneity"] == 0.7
    assert result["review_rubrics"][0]["identification"] == 0.7
    assert result["review_scores"][0] >= 0.7
    assert "current_chapter_index" not in result
    assert "missing_ident_assumptions" not in (
        result.get("revision_suggestions") or [""]
    )[0]


def test_association_live_llm_cannot_fail_for_missing_iv(monkeypatch):
    """现场 LLM 按缺 IV/RDD 打低分时，相关引言不得自动不通过。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(
            {
                "endogeneity": 0.1,
                "identification": 0.1,
                "robustness": 0.2,
                "contribution": 0.3,
                "readability": 0.4,
            },
            feedback="缺少识别策略，应使用 IV 或 RDD。",
            suggestions="补双重差分或工具变量。",
        ),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[{
            "type": "intro",
            "title": "引言",
            "content": "本文描述年龄与收入的条件相关，不识别因果。" + ("论" * 80),
            "status": "generated",
            "versions": [],
            "chapter_index": 0,
            "method": "ols",
        }],
        claim="association",
        research_direction={"method": "ols", "claim": "association"},
        max_review_iterations=2,
        review_iteration=0,
    )
    result = review_chapter(state)
    assert result["review_scores"][0] >= 0.7
    assert "current_chapter_index" not in result
    assert "IV" not in (result.get("revision_suggestions") or [""])[0]
    assert "RDD" not in (result.get("revision_suggestions") or [""])[0]


def test_association_intro_low_contribution_does_not_auto_fail(monkeypatch):
    """相关引言贡献分偏低、但未写成因果时，不得自动不通过。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(
            {
                "endogeneity": 0.9,
                "identification": 0.85,
                "robustness": 0.55,
                "contribution": 0.45,
                "readability": 0.75,
            },
            feedback="定位为条件相关是对的，但贡献三条偏满。",
            suggestions="收束贡献表述。",
        ),
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[{
            "type": "intro",
            "title": "引言",
            "content": "本文描述年龄与收入的条件相关，不识别因果。" + ("论" * 80),
            "status": "generated",
            "chapter_index": 0,
            "method": "ols",
        }],
        claim="association",
        research_direction={"method": "ols", "claim": "association"},
        max_review_iterations=2,
        review_iteration=0,
    )
    result = review_chapter(state)
    assert result["review_scores"][0] >= 0.7
    assert "current_chapter_index" not in result


def test_association_guard_rewrites_causal_demand():
    rubric, feedback, suggestions = apply_association_review_guard(
        {
            "endogeneity": 0.1,
            "identification": 0.1,
            "robustness": 0.2,
            "contribution": 0.3,
            "readability": 0.4,
        },
        "必须补充 IV 与 RDD。文献覆盖不足。",
        "否则识别失败。收束贡献表述。",
        "association",
        "年龄与收入的相关。",
    )
    assert rubric["identification"] >= 0.7
    assert rubric["contribution"] >= 0.7
    assert "IV" not in suggestions
    assert "相关" in feedback
    assert "文献覆盖不足" in feedback
    assert "收束贡献" in suggestions


def test_invoke_review_prompt_states_association(monkeypatch):
    seen = {}

    def fake_call(prompt, node_type="review"):
        seen["prompt"] = prompt
        return (
            '{"rubric":{"endogeneity":0.8,"identification":0.8,'
            '"robustness":0.8,"contribution":0.8,"readability":0.8},'
            '"feedback":"ok","suggestions":"ok"}'
        )

    monkeypatch.setattr("llm.call_llm.call_llm", fake_call)
    invoke_review_llm(None, "正文", ReviewRubric(), "dir", [], claim="association")
    assert "association" in seen["prompt"]
    assert "不得因为没有" in seen["prompt"]
    assert "课程论文" in seen["prompt"]
    assert "边际贡献" in seen["prompt"]


# ---------------------------------------------------------------------------
# 结果章接地（批次 4）
# ---------------------------------------------------------------------------
_TREATMENT_ROW = "| age | 0.1234 | 0.0456 | 0.0078 |"


def _results_chapter(content: str) -> dict:
    return {
        "type": "results",
        "title": "结果",
        "content": content,
        "status": "generated",
        "versions": [content],
        "chapter_index": 0,
        "method": "ols",
    }


def _results_ready(content: str, **overrides) -> dict:
    return make_write_ready_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_results_chapter(content)],
        max_review_iterations=2,
        review_iteration=0,
        **overrides,
    )


def test_results_grounding_pass_does_not_rollback(monkeypatch):
    """真 treatment_row、无另造处理行：不因接地失败回退。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    content = (
        "本节报告 OLS 主估计。"
        f"{_TREATMENT_ROW}"
        " | N | 1200 |  | 常数项 | 1.2300 |"
        "系数方向与预期一致。"
        + ("论" * 80)
    )
    result = review_chapter(_results_ready(content))
    failures = result.get("grounding_failures") or []
    assert "invented_number" not in failures
    assert "missing_estimate_number" not in failures
    assert result["review_scores"][0] > 0.50
    assert "current_chapter_index" not in result


def test_results_invented_number_caps_and_rolls_back(monkeypatch):
    """另造 | age | 0.9999 | 或 | treat | 0.9999 |：invented_number，封顶回炉。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    for fake in ("| age | 0.9999 |", "| treat | 0.9999 |"):
        content = (
            "本节报告 OLS 主估计。"
            f"{_TREATMENT_ROW} {fake} "
            + ("论" * 80)
        )
        result = review_chapter(_results_ready(content))
        assert "invented_number" in result["grounding_failures"], fake
        assert result["review_scores"][0] <= 0.50, fake
        assert result["current_chapter_index"] == 0, fake


def test_results_missing_treatment_row_caps_and_rolls_back(monkeypatch):
    """缺 treatment_row 子串：missing_estimate_number，封顶回炉。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    content = "本节报告 OLS 主估计，但没有贴出主表。" + ("论" * 80)
    result = review_chapter(_results_ready(content))
    assert "missing_estimate_number" in result["grounding_failures"]
    assert result["review_scores"][0] <= 0.50
    assert result["current_chapter_index"] == 0


def test_intro_and_methods_do_not_require_estimate_table(monkeypatch):
    """引言 / 方法章：不因没表而报 missing_estimate_number。"""
    monkeypatch.setattr(
        "nodes.review_chapter.call_review_llm",
        lambda *a, **k: _mock_llm_return(HIGH_SCORE_RUBRIC),
    )
    methods_content = (
        "本节给出条件关联的计量模型。"
        r"$y_i=\alpha+\beta D_i+u_i$"
        "外生性 sutva。"
        + ("论" * 200)
    )
    for chapter_type, content in (
        ("intro", "本文讨论年龄与收入的条件关联。" + ("论" * 80)),
        ("methods", methods_content),
    ):
        state = make_write_ready_state(
            review_enabled=True,
            current_chapter_index=1,
            body_chapters=[{
                "type": chapter_type,
                "title": chapter_type,
                "content": content,
                "status": "generated",
                "versions": [content],
                "chapter_index": 0,
                "method": "ols",
            }],
            max_review_iterations=2,
        )
        result = review_chapter(state)
        assert "missing_estimate_number" not in (result.get("grounding_failures") or []), chapter_type

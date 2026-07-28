"""ADR-0004 Stage 3: mock 评审 LLM 测试。

契约：
1. 高质量内容（IV/DID/稳健/政策等关键词齐全）→ 高分（>= 0.7）
2. 低质量内容（短文本 + 无关键词）→ 低分（< 0.5）
3. 返回值含 rubric / feedback / suggestions 三键
4. 评分规则确定性（同输入同输出）
5. 5 维 rubric 字段齐全
"""
from __future__ import annotations

import pytest

from nodes.review_sources.mock_review import mock_review_llm
from protocols import ReviewRubric


# ---------------------------------------------------------------------------
# 返回值结构
# ---------------------------------------------------------------------------
def test_review_returns_required_keys():
    """返回值含 rubric / feedback / suggestions 三键。"""
    result = mock_review_llm("test content", ReviewRubric(), "", [])
    assert "rubric" in result
    assert "feedback" in result
    assert "suggestions" in result


def test_review_rubric_has_5_dimensions():
    """rubric 含 5 维：endogeneity/identification/robustness/contribution/readability。"""
    result = mock_review_llm("test", ReviewRubric(), "", [])
    rubric = result["rubric"]
    for dim in (
        "endogeneity",
        "identification",
        "robustness",
        "contribution",
        "readability",
    ):
        assert dim in rubric, f"rubric 缺失维度: {dim}"
        assert 0.0 <= rubric[dim] <= 1.0


def test_review_feedback_and_suggestions_are_strings():
    """feedback / suggestions 都是字符串。"""
    result = mock_review_llm("test", ReviewRubric(), "", [])
    assert isinstance(result["feedback"], str)
    assert isinstance(result["feedback"], str) and len(result["feedback"]) > 0
    assert isinstance(result["suggestions"], str)
    assert len(result["suggestions"]) > 0


# ---------------------------------------------------------------------------
# 评分规则
# ---------------------------------------------------------------------------
def test_review_high_quality_content():
    """高质量内容（IV/DID/稳健/政策）→ 高分。"""
    content = (
        "本文采用 IV 工具变量法处理内生性问题，使用 DID 双重差分设计，"
        "包含稳健性检验与安慰剂检验，政策贡献显著。"
    )
    result = mock_review_llm(content, ReviewRubric(), "labor econ", [])
    assert result["rubric"]["endogeneity"] >= 0.7
    assert result["rubric"]["identification"] >= 0.7
    assert result["rubric"]["robustness"] >= 0.7
    assert result["rubric"]["contribution"] >= 0.7


def test_review_low_quality_content():
    """低质量内容（短文本 + 无关键词）→ 低分。"""
    content = "这是一段很短的文字。"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["readability"] < 0.5
    assert result["rubric"]["endogeneity"] < 0.5
    assert result["rubric"]["identification"] < 0.5
    assert result["rubric"]["robustness"] < 0.5


# ---------------------------------------------------------------------------
# 各维度独立触发
# ---------------------------------------------------------------------------
def test_endogeneity_high_when_iv_mentioned():
    """提及 IV / 工具变量 → endogeneity 高分。"""
    content = "本文使用 IV 工具变量法识别因果效应。"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["endogeneity"] >= 0.7


def test_endogeneity_high_when_endogeneity_mentioned():
    """提及内生性 → endogeneity 高分。"""
    content = "本文处理了内生性问题，使用工具变量法。"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["endogeneity"] >= 0.7


def test_endogeneity_low_when_no_iv():
    """未提及内生性关键词 → endogeneity 低分（0.4）。"""
    content = "本文研究劳动市场工资差异。" * 5  # 加长避免 readability 低分干扰
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["endogeneity"] == 0.4


def test_identification_high_when_did_mentioned():
    """提及 DID / 双重差分 → identification 高分。"""
    content = "采用 DID 双重差分方法识别政策效应。"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["identification"] >= 0.7


def test_identification_high_when_rdd_mentioned():
    """提及 RDD / 断点回归 → identification 高分。"""
    content = "使用 RDD 断点回归设计估计政策效果。"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["identification"] >= 0.7


def test_identification_low_when_no_method():
    """未提及识别策略关键词 → identification 低分（0.4）。"""
    content = "本文研究劳动市场工资差异。" * 5
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["identification"] == 0.4


def test_robustness_high_when_placebo_mentioned():
    """提及安慰剂 / placebo → robustness 高分。"""
    content = "本文包含安慰剂检验 placebo test 验证稳健性。"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["robustness"] >= 0.7


def test_robustness_low_when_no_check():
    """未提及稳健性关键词 → robustness 低分（0.4）。"""
    content = "本文研究劳动市场工资差异。" * 5
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["robustness"] == 0.4


def test_contribution_high_when_policy_mentioned():
    """提及政策 / policy → contribution 高分。"""
    content = "本文政策贡献显著，对政策制定有参考价值。"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["contribution"] >= 0.7


def test_contribution_default_0_5():
    """未提及贡献关键词 → contribution 默认 0.5。"""
    content = "本文研究劳动市场工资差异。" * 5
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["contribution"] == 0.5


# ---------------------------------------------------------------------------
# readability 长度规则
# ---------------------------------------------------------------------------
def test_readability_long_content():
    """内容长度 > 200 字 → readability 高分（0.8）。"""
    content = "研究内容" * 60  # 240 字
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["readability"] == 0.8


def test_readability_medium_content():
    """内容长度 > 100 字 → readability 中分（0.6）。"""
    content = "研究内容" * 30  # 120 字
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["readability"] == 0.6


def test_readability_short_content():
    """内容长度 <= 100 字 → readability 低分（0.3）。"""
    content = "短文本"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert result["rubric"]["readability"] == 0.3


# ---------------------------------------------------------------------------
# 边界情况
# ---------------------------------------------------------------------------
def test_review_empty_content():
    """空内容：所有维度低分，readability=0.3。"""
    result = mock_review_llm("", ReviewRubric(), "", [])
    assert result["rubric"]["readability"] == 0.3
    assert result["rubric"]["endogeneity"] == 0.4
    assert result["rubric"]["identification"] == 0.4
    assert result["rubric"]["robustness"] == 0.4
    assert result["rubric"]["contribution"] == 0.5


def test_review_none_content():
    """None 内容：不报错，readability=0.3。"""
    result = mock_review_llm(None, ReviewRubric(), "", [])  # type: ignore[arg-type]
    assert result["rubric"]["readability"] == 0.3


def test_review_deterministic():
    """评分确定性：同输入同输出（可复现）。"""
    content = "本文使用 IV 工具变量法处理内生性，DID 识别，包含稳健性检验。"
    r1 = mock_review_llm(content, ReviewRubric(), "test", [])
    r2 = mock_review_llm(content, ReviewRubric(), "test", [])
    assert r1 == r2


# ---------------------------------------------------------------------------
# feedback / suggestions 内容
# ---------------------------------------------------------------------------
def test_feedback_mentions_low_dims():
    """低分时 feedback 提及低分维度。"""
    content = "短文本"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    feedback = result["feedback"]
    # 短文本所有维度都低（除 contribution=0.5），feedback 应提及低分维度
    assert "评审反馈" in feedback


def test_suggestions_provides_actionable_advice():
    """低分时 suggestions 提供建议。"""
    content = "短文本"
    result = mock_review_llm(content, ReviewRubric(), "", [])
    assert "建议" in result["suggestions"]


def test_high_quality_feedback_says_passing():
    """全高质内容时 feedback 表示达标。"""
    content = (
        "本文采用 IV 工具变量法处理内生性问题，使用 DID 双重差分设计，"
        "包含稳健性检验与安慰剂检验，政策贡献显著。" * 5  # 加长确保 readability 高分
    )
    result = mock_review_llm(content, ReviewRubric(), "", [])
    # 所有维度都达标
    low_dims = [d for d, s in result["rubric"].items() if s < 0.5]
    assert len(low_dims) == 0
    assert "良好" in result["feedback"] or "达标" in result["feedback"]

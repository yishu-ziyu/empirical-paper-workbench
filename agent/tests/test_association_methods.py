"""硬条 6 的 prompt / 结构 / mock 部分。

review_chapter 综合分与不回退 idx 由执行 1 覆盖。
本文件不 import、不改 review_chapter.py。
"""
from __future__ import annotations

from agent.engine.bind import bind_chapter_kwargs
from agent.nodes.review_sources.mock_review import mock_review_llm
from agent.nodes.review_sources.structure_checks import check_structure
from agent.prompts import get_prompt
from agent.protocols import ReviewRubric

from conftest import make_write_ready_state

ASSOCIATION_METHODS_FIXTURE = (
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


def test_association_methods_system_omits_endogeneity_fix():
    system, _ = get_prompt("methods").render(
        method="ols",
        research_question="年龄与收入",
        claim="association",
    )
    assert "解决内生性" not in system


def test_lit_review_prompt_forbids_invented_author_year():
    system = get_prompt("lit_review").SYSTEM_PROMPT
    assert "仍使用 (Author, Year)" not in system
    assert "不得编造篇名与年份" in system


def test_results_system_only_interprets_end_table():
    system = get_prompt("results").SYSTEM_PROMPT
    assert "主表已在文末" in system
    assert "禁止再画表" in system
    _, user = get_prompt("results").render(
        results="MAIN", method="ols", robustness_table="ROB"
    )
    assert "MAIN" in user
    assert "ROB" in user


def test_fixture_methods_structure_and_mock():
    content = ASSOCIATION_METHODS_FIXTURE
    assert len(content) >= 200
    assert "$y_i=\\alpha+\\beta D_i+u_i$" in content
    for banned in ("因果", "识别策略", "解决内生性"):
        assert banned not in content
    assert check_structure("methods", content, claim="association") == []
    scored = mock_review_llm(
        content, ReviewRubric(), "", [], claim="association"
    )
    assert scored["rubric"]["endogeneity"] == 0.7
    assert scored["rubric"]["identification"] == 0.7
    assert scored["rubric"]["robustness"] == 0.7
    assert scored["rubric"]["contribution"] == 0.7
    assert scored["rubric"]["readability"] == 0.8


def test_bind_chapter_kwargs_is_truth_source():
    state = make_write_ready_state(research_question="", method="")
    bound = bind_chapter_kwargs(
        state, {"type": "methods", "method": ""}
    )
    assert bound["research_question"] == "年龄与收入"
    assert bound["method"] == "ols"
    assert bound["claim"] == "association"
    assert "T" in bound["key_references"]
    assert bound["results"]
    assert bound["robustness_table"] == "# 稳健性"
    assert bound["identification_report"]
    assert bound["star_rating"] is None
    assert bound["data_summary"] == ""
    assert bound["eda_results"] == ""

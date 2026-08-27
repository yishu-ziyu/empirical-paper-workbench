"""#6: 结构层纯函数。关键词不够过 0.7。"""
from __future__ import annotations

from nodes.review_chapter import REVIEW_SCORE_THRESHOLD, review_chapter
from nodes.review_sources.mock_review import mock_review_llm
from nodes.review_sources.structure_checks import (
    STRUCTURE_SCORE_CAP,
    apply_structure_cap,
    check_structure,
)
from protocols import ReviewRubric

from conftest import make_state


def test_keyword_stuffing_methods_fails_structure():
    """只堆 DID / 工具变量 / 稳健 / 贡献，没有方程没有假设。"""
    content = "本文采用 DID 工具变量处理内生性，包含稳健性检验，政策贡献显著。"
    failures = check_structure("methods", content, method="DID")
    assert "missing_equation" in failures
    assert "missing_ident_assumptions" in failures


def test_methods_with_equation_and_assumptions_passes():
    """有方程 + 两条识别假设 → 结构过。"""
    content = (
        "采用 DID。主回归 $y_{it}=\\alpha+\\beta D_{it}+\\varepsilon_{it}$。"
        "识别依赖平行趋势与 SUTVA。"
    )
    assert check_structure("methods", content, method="DID") == []


def test_association_methods_equation_only_passes():
    """association 只要方程，不要识别假设菜单。"""
    content = "条件关联模型为 $y_i=\\alpha+\\beta D_i+u_i$。系数读作相关。"
    assert check_structure("methods", content, claim="association") == []


def test_star_none_did_skips_parallel_trends():
    """star is None 的 DiD 按 association，不逼平行趋势词。"""
    content = "主回归 $y_i=\\alpha+\\beta D_i+u_i$。本文报告条件关联。"
    assert (
        check_structure(
            "methods", content, method="DID", star_rating=None
        )
        == []
    )


def test_lit_review_invented_citation_fails():
    """编造 [99] 结构失败。"""
    failures = check_structure(
        "lit_review",
        "Smith (2020) [1] 指出，Jones [99] 反对。",
        citation_indices={"10.1/a": 1},
    )
    assert "invented_citation" in failures


def test_lit_review_empty_index_author_year_fails():
    """编号表为空、正文 Smith (2020) 且无 [N] → invented_citation。"""
    text = "Smith (2020) 指出……"
    for indices in ({}, None):
        failures = check_structure(
            "lit_review", text, citation_indices=indices
        )
        assert "invented_citation" in failures


def test_lit_review_empty_index_parenthetical_author_year_fails():
    """空表时 (Author, 2020) / （张三, 2020） / Name and Name (2020) 也算编造。"""
    for text in (
        "(Author, 2020) 认为……",
        "（张三, 2020）认为……",
        "Name and Name (2020) 指出。",
    ):
        failures = check_structure("lit_review", text, citation_indices={})
        assert "invented_citation" in failures, text


def test_lit_review_empty_index_no_author_year_ok():
    """空表且无作者-年份、无 [N] → 不报 invented_citation。"""
    text = "现有研究尚未回答该问题。"
    assert "invented_citation" not in check_structure(
        "lit_review", text, citation_indices={}
    )
    assert "invented_citation" not in check_structure(
        "lit_review", text, citation_indices=None
    )


def test_lit_review_year_mention_is_not_citation():
    """「2020 年」不是作者-年份引用。"""
    failures = check_structure(
        "lit_review",
        "2020 年以来该问题仍未解决。",
        citation_indices={},
    )
    assert "invented_citation" not in failures


def test_lit_review_author_year_with_valid_bracket_ok():
    """表有编号时 Smith (2020) [1] 不要误杀。"""
    failures = check_structure(
        "lit_review",
        "Smith (2020) [1] 指出……",
        citation_indices={"10.1/a": 1},
    )
    assert "invented_citation" not in failures


def test_lit_review_empty_index_bracket_still_fails():
    """空表但正文有 [1] → 仍 invented_citation。"""
    failures = check_structure(
        "lit_review",
        "已有研究 [1] 指出。",
        citation_indices={},
    )
    assert "invented_citation" in failures


# ---------------------------------------------------------------------------
# 引用可回溯（北极星：综述每条引用必须指回真实条目）
# ---------------------------------------------------------------------------

def _traceback_entries():
    """两级条目：[1]=Smith 2019 (doi 10.1/a)，[2]=Lee 2021 (doi 10.1/b)。"""
    return [
        {"title": "Minimum Wages", "authors": ["Smith"], "year": 2019, "doi": "10.1/a"},
        {"title": "Education Returns", "authors": ["Lee"], "year": 2021, "doi": "10.1/b"},
    ]


def test_lit_review_citation_year_mismatch_fails():
    """[N] 在表内，但叙述年份与条目元数据不符 → 张冠李戴，必须拦下。"""
    failures = check_structure(
        "lit_review",
        "Smith (2020) [1] 指出最低工资的就业效应显著为负。",
        citation_indices={"10.1/a": 1},
        literature_entries=_traceback_entries(),
    )
    assert "citation_year_mismatch" in failures


def test_lit_review_citation_matching_entry_passes():
    """[N]、作者、年份与条目一致 → 不新增任何结构失败。"""
    failures = check_structure(
        "lit_review",
        "Smith (2019) [1] 指出最低工资的就业效应存在争议。",
        citation_indices={"10.1/a": 1},
        literature_entries=_traceback_entries(),
    )
    assert "citation_year_mismatch" not in failures
    assert "invented_citation" not in failures


def test_lit_review_bracket_without_author_year_still_ok():
    """只有 [N] 无作者-年份叙述（如「已有研究 [1]」）→ 无从比对，不误杀。"""
    failures = check_structure(
        "lit_review",
        "关于该问题，已有研究 [1] 给出了不同估计。",
        citation_indices={"10.1/a": 1},
        literature_entries=_traceback_entries(),
    )
    assert "citation_year_mismatch" not in failures


def test_lit_review_multi_marker_second_sentence_mismatch_fails():
    """同段多引用：第二句的 [2] 叙述 2019，但条目是 2021 → 失败。"""
    text = (
        "Smith (2019) [1] 指出就业效应存在争议。"
        "Lee (2019) [2] 则发现教育回报显著。"
    )
    failures = check_structure(
        "lit_review",
        text,
        citation_indices={"10.1/a": 1, "10.1/b": 2},
        literature_entries=_traceback_entries(),
    )
    assert "citation_year_mismatch" in failures


def test_lit_review_nonempty_table_unattributed_author_year_fails():
    """表非空时，作者-年份出现在没有任何合法 [N] 的句子里 → 无从核对。"""
    text = (
        "Wong (2015) 认为数字化冲击被低估。"      # 该句无任何 [N]
        "Smith (2019) [1] 则持相反意见。"
    )
    failures = check_structure(
        "lit_review",
        text,
        citation_indices={"10.1/a": 1},
        literature_entries=_traceback_entries(),
    )
    assert "invented_citation" in failures


def test_results_checks_ignore_literature_kwarg():
    """其他章节类型不受新参数影响。"""
    failures = check_structure(
        "results",
        "income ~ age 的 OLS 结果见表 2。",
        method="OLS",
        methods_method="OLS",
        citation_indices={"10.1/a": 1},
        literature_entries=_traceback_entries(),
    )
    assert "citation_year_mismatch" not in failures


def test_results_method_must_match_methods_chapter():
    """results 另起一个 method 词 → 失败。"""
    failures = check_structure(
        "results",
        "基准回归使用 IV 工具变量。",
        method="IV",
        methods_method="DID",
    )
    assert "method_mismatch" in failures


def test_structure_cap_blocks_threshold():
    """结构失败后综合分 ≤ 0.65，漂不过 0.7。"""
    stuffed = (
        "本文采用 IV 工具变量法处理内生性问题，使用 DID 双重差分设计，"
        "包含稳健性检验与安慰剂检验，政策贡献显著。" * 4
    )
    mock = mock_review_llm(stuffed, ReviewRubric(), "", [])
    raw = (
        0.3 * mock["rubric"]["endogeneity"]
        + 0.25 * mock["rubric"]["identification"]
        + 0.2 * mock["rubric"]["robustness"]
        + 0.15 * mock["rubric"]["contribution"]
        + 0.1 * mock["rubric"]["readability"]
    )
    assert raw >= REVIEW_SCORE_THRESHOLD
    capped = apply_structure_cap(raw, ["missing_equation"])
    assert capped <= STRUCTURE_SCORE_CAP
    assert capped < REVIEW_SCORE_THRESHOLD


def test_review_chapter_caps_keyword_only_methods():
    """节点层：堆词 methods 章走回炉。"""
    content = (
        "本文采用 IV 工具变量法处理内生性问题，使用 DID 双重差分设计，"
        "包含稳健性检验与安慰剂检验，政策贡献显著。" * 4
    )
    chapter = {
        "type": "methods",
        "title": "方法",
        "content": content,
        "status": "generated",
        "versions": [content],
        "chapter_index": 0,
        "method": "DID",
    }
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[chapter],
        outline=[{"type": "methods", "title": "方法", "method": "DID"}],
        research_direction="test",
        max_review_iterations=2,
        review_iteration=0,
    )
    result = review_chapter(state)
    assert result["review_scores"][0] <= STRUCTURE_SCORE_CAP
    assert result["current_chapter_index"] == 0
    assert "结构层失败" in result["revision_suggestions"][0]

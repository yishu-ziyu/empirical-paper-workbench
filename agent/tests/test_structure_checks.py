"""#6: 结构层纯函数。关键词不够过 0.7。"""
from __future__ import annotations

from agent.nodes.review_chapter import REVIEW_SCORE_THRESHOLD, review_chapter
from agent.nodes.review_sources.mock_review import mock_review_llm
from agent.nodes.review_sources.structure_checks import (
    STRUCTURE_SCORE_CAP,
    apply_structure_cap,
    check_structure,
)
from agent.protocols import ReviewRubric

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


def test_intro_keyword_stuffing_fails_structure():
    """intro 只堆 DID/IV/RDD 与识别词，没有处理组/对照 → keyword_stuffed。"""
    content = (
        "本文使用 DID IV RDD 三重差分合成控制断点回归因果识别。"
        "内生性稳健性异质性安慰剂平行趋势弱工具变量均已考虑。"
        "城乡医保整合显著降低农村中老年住院自付支出，贡献巨大。"
        "没写谁被处理、什么时候开始、跟谁比，也没写 CHARLS 流失。"
    )
    failures = check_structure("intro", content)
    assert "keyword_stuffed" in failures


def test_intro_with_design_not_stuffed():
    """intro 提 DID/IV，但写了处理组/对照和 Callaway → 不算堆词。"""
    content = (
        "本文使用 DID 与 IV。"
        "处理组为新农合参保人，对照为城镇职工医保。"
        "主规格采用 Callaway 交错 DID。"
    )
    failures = check_structure("intro", content)
    assert "keyword_stuffed" not in failures


def test_results_overclaim_fails_structure():
    """results 先写不显著/安慰剂未通过，再写显著降低与政策效果稳健。"""
    content = (
        "表 3 首选规格 M5 系数为 +0.081，标准误 0.053，不显著。"
        "2015 安慰剂未通过。据此我们得出：城乡医保整合显著降低了"
        "农村中老年人住院自付支出，政策效果稳健。"
    )
    failures = check_structure("results", content)
    assert "overclaim" in failures


def test_results_hedged_not_overclaim():
    """不显著且对显著结论加了不能写/不支持 → 不算 overclaim。"""
    content = (
        "表 3 首选规格系数为 +0.081，不显著。"
        "不能写显著降低，也不支持显著下降。"
    )
    failures = check_structure("results", content)
    assert "overclaim" not in failures


def test_review_chapter_caps_stuffed_intro():
    """节点层：堆词 intro 章走回炉，建议点出 keyword_stuffed。"""
    content = (
        "本文使用 DID IV RDD 三重差分合成控制断点回归因果识别。"
        "内生性稳健性异质性安慰剂平行趋势弱工具变量均已考虑。"
        "城乡医保整合显著降低农村中老年住院自付支出，贡献巨大。"
        "没写谁被处理、什么时候开始、跟谁比，也没写 CHARLS 流失。" * 4
    )
    chapter = {
        "type": "intro",
        "title": "引言",
        "content": content,
        "status": "generated",
        "versions": [content],
        "chapter_index": 0,
    }
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[chapter],
        outline=[{"type": "intro", "title": "引言"}],
        research_direction="test",
        max_review_iterations=2,
        review_iteration=0,
    )
    result = review_chapter(state)
    assert result["review_scores"][0] <= STRUCTURE_SCORE_CAP
    assert result["current_chapter_index"] == 0
    assert "结构层失败" in result["revision_suggestions"][0]
    assert "keyword_stuffed" in result["revision_suggestions"][0]


def test_review_chapter_caps_overclaim_results():
    """节点层：overclaim results 章走回炉，建议点出 overclaim。"""
    content = (
        "表 3 首选规格 M5 系数为 +0.081，标准误 0.053，不显著。"
        "2015 安慰剂未通过。据此我们得出：城乡医保整合显著降低了"
        "农村中老年人住院自付支出，政策效果稳健。DID 内生。" * 4
    )
    chapter = {
        "type": "results",
        "title": "结果",
        "content": content,
        "status": "generated",
        "versions": [content],
        "chapter_index": 0,
    }
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[chapter],
        outline=[{"type": "results", "title": "结果"}],
        research_direction="test",
        max_review_iterations=2,
        review_iteration=0,
    )
    result = review_chapter(state)
    assert result["review_scores"][0] <= STRUCTURE_SCORE_CAP
    assert result["current_chapter_index"] == 0
    assert "结构层失败" in result["revision_suggestions"][0]
    assert "overclaim" in result["revision_suggestions"][0]

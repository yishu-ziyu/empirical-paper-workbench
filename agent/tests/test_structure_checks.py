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


def test_lit_review_invented_citation_fails():
    """编造 [99] 结构失败。"""
    failures = check_structure(
        "lit_review",
        "Smith (2020) [1] 指出，Jones [99] 反对。",
        citation_indices={"10.1/a": 1},
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

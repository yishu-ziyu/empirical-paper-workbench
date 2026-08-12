"""#7: CHARLS 威胁卡。两期禁用交错 DID。"""
from __future__ import annotations

from nodes.generate_chapter import generate_chapter
from nodes.review_chapter import review_chapter
from nodes.review_sources.threat_cards import (
    active_threat_cards,
    apply_threat_caps,
    load_threat_cards,
    resolve_n_waves,
)

from conftest import make_state


def test_five_seed_cards_exist():
    cards = load_threat_cards()
    ids = {card["id"] for card in cards}
    assert ids == {
        "attrition",
        "hukou_selection",
        "insurance_endo",
        "recall_oopc",
        "staggered_did",
    }


def test_staggered_disabled_on_two_waves():
    """默认两期：交错 DID 卡不激活。"""
    state = make_state(
        dataset_profile="charls",
        data_summary="CHARLS 2018/2020",
        selected_waves=[2018, 2020],
    )
    assert resolve_n_waves(state) == 2
    ids = {card["id"] for card in active_threat_cards(state)}
    assert "staggered_did" not in ids
    assert "attrition" in ids
    assert "hukou_selection" in ids


def test_staggered_enabled_on_three_waves():
    state = make_state(
        dataset_profile="charls",
        selected_waves=[2015, 2018, 2020],
    )
    ids = {card["id"] for card in active_threat_cards(state)}
    assert "staggered_did" in ids


def test_non_charls_has_no_cards():
    state = make_state(data_summary="某市行政数据", research_direction="最低工资")
    assert active_threat_cards(state) == []


def test_unhandled_threat_caps_dimension():
    rubric = {"endogeneity": 0.9, "identification": 0.9,
              "robustness": 0.9, "contribution": 0.9, "readability": 0.9}
    cards = [
        {
            "id": "hukou_selection",
            "dims": ["endogeneity"],
            "check": ["户口", "hukou"],
        }
    ]
    triggered = apply_threat_caps(rubric, "本文使用 CHARLS 研究医保。", cards)
    assert "hukou_selection" in triggered
    assert rubric["endogeneity"] <= 0.4


def test_generate_chapter_injects_charls_constraints(mock_llm_for):
    recorder = mock_llm_for("generate_chapter", return_value="M")
    state = make_state(
        current_chapter_index=0,
        outline=[{"type": "methods", "title": "方法", "method": "DID"}],
        method="DID",
        research_question="医保",
        data_summary="CHARLS 2018 与 2020",
        dataset_profile="charls",
        selected_waves=[2018, 2020],
    )
    generate_chapter(state)
    _, user = recorder.calls[0]["args"]
    assert "识别威胁约束" in user
    assert "户口" in user or "hukou" in user.lower()
    assert "交错 DID" not in user


def test_review_presses_unhandled_charls_threat():
    content = (
        "本文采用 IV 工具变量法处理内生性问题，使用 DID 双重差分设计，"
        "平行趋势与 SUTVA 成立。主回归 $y_{it}=\\beta D_{it}$。"
        "包含稳健性检验与安慰剂检验，政策贡献显著。" * 3
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
        outline=[{"type": "methods", "method": "DID"}],
        data_summary="CHARLS",
        dataset_profile="charls",
        selected_waves=[2018, 2020],
        research_direction="CHARLS 医保",
    )
    result = review_chapter(state)
    assert result["review_rubrics"][0]["endogeneity"] <= 0.4
    assert "未处理识别威胁" in result["revision_suggestions"][0]

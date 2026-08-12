"""#4 真通道 + #5 按章权重。"""
from __future__ import annotations

from types import SimpleNamespace

from nodes.generate_chapter import call_llm as generate_call_llm
from nodes.review_chapter import (
    _compute_composite_score,
    call_review_llm,
    weights_for_chapter,
)
from protocols import ReviewRubric


def test_intro_weights_zero_out_endogeneity():
    """引言不按内生 0.3 打分。"""
    weights = weights_for_chapter("intro")
    assert weights["endogeneity"] == 0.0
    assert weights["contribution"] >= 0.4
    rubric = {
        "endogeneity": 1.0,
        "identification": 0.0,
        "robustness": 0.0,
        "contribution": 0.0,
        "readability": 0.0,
    }
    assert _compute_composite_score(rubric, "intro") == 0.0
    assert _compute_composite_score(rubric, "methods") == 0.3


def test_lit_review_weights_prefer_contribution():
    weights = weights_for_chapter("lit_review")
    assert weights["endogeneity"] == 0.0
    assert weights["contribution"] >= weights["identification"]


def test_default_weights_unchanged_for_methods():
    """既有加权公式：只 endogeneity=1 → 0.3。"""
    rubric = {
        "endogeneity": 1.0,
        "identification": 0.0,
        "robustness": 0.0,
        "contribution": 0.0,
        "readability": 0.0,
    }
    assert _compute_composite_score(rubric) == 0.3


def test_generate_call_llm_mock_keeps_placeholder():
    """provider=mock 仍返回原占位，现有单测语义不变。"""
    assert generate_call_llm("sys", "user") == "Placeholder chapter content from LLM"


def test_generate_non_mock_uses_invoke(monkeypatch):
    """非 mock 走 invoke_generate_llm，而不是直接返回占位。"""
    seen = {}

    def fake_invoke(config, system, user):
        seen["called"] = True
        seen["system"] = system
        return "REAL-GENERATE"

    monkeypatch.setattr(
        "nodes.generate_chapter.invoke_generate_llm", fake_invoke
    )
    monkeypatch.setattr(
        "llm.router.router.get_config",
        lambda node: SimpleNamespace(provider="anthropic", model="claude"),
    )
    assert generate_call_llm("S", "U") == "REAL-GENERATE"
    assert seen.get("called") is True


def test_review_non_mock_uses_invoke(monkeypatch):
    """非 mock 走 invoke_review_llm，不直接调 mock_review_llm。"""
    seen = {}

    def fake_invoke(config, content, rubric, direction, literature):
        seen["called"] = True
        return {
            "rubric": {
                "endogeneity": 0.6,
                "identification": 0.6,
                "robustness": 0.6,
                "contribution": 0.6,
                "readability": 0.6,
            },
            "feedback": "from-real",
            "suggestions": "from-real",
        }

    monkeypatch.setattr("nodes.review_chapter.invoke_review_llm", fake_invoke)
    monkeypatch.setattr(
        "llm.router.router.get_config",
        lambda node: SimpleNamespace(provider="openai", model="gpt-4"),
    )
    result = call_review_llm("正文", ReviewRubric(), "dir", [])
    assert seen.get("called") is True
    assert result["feedback"] == "from-real"


def test_review_bad_json_falls_back_to_mock(monkeypatch):
    """评审 JSON 坏掉时降级 mock，不把 graph 打费。"""

    def boom(config, content, rubric, direction, literature):
        raise ValueError("bad json")

    monkeypatch.setattr("nodes.review_chapter.invoke_review_llm", boom)
    monkeypatch.setattr(
        "llm.router.router.get_config",
        lambda node: SimpleNamespace(provider="anthropic", model="claude"),
    )
    result = call_review_llm("短文本", ReviewRubric(), "", [])
    assert "rubric" in result
    assert "feedback" in result
    assert result["rubric"]["endogeneity"] == 0.4

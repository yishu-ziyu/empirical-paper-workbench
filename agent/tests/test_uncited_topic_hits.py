"""#8 下游监督：命中主题词但 lit_review 没写 [N]，relevance 给负分。"""
from __future__ import annotations

from agent.nodes.review_chapter import (
    UNCITED_TOPIC_PENALTY,
    apply_uncited_topic_penalty,
    review_chapter,
)


def test_penalty_when_topic_hit_but_not_cited():
    entries = [
        {
            "title": "Returns to Education",
            "abstract": "劳动 教育",
            "doi": "10.1/a",
            "relevance_score": 0.8,
        },
        {
            "title": "Unrelated Macro",
            "abstract": "通胀",
            "doi": "10.1/b",
            "relevance_score": 0.4,
        },
    ]
    out = apply_uncited_topic_penalty(
        entries,
        content="本文回顾已有研究，但没有引用标记。",
        citation_indices={"10.1/a": 1, "10.1/b": 2},
        query="劳动 教育",
    )
    by_doi = {e["doi"]: e["relevance_score"] for e in out}
    assert by_doi["10.1/a"] == UNCITED_TOPIC_PENALTY
    assert by_doi["10.1/a"] < 0
    assert by_doi["10.1/b"] == 0.4


def test_no_penalty_when_cited_in_lit_review():
    entries = [
        {
            "title": "Returns to Education",
            "abstract": "劳动 教育",
            "doi": "10.1/a",
            "relevance_score": 0.8,
        }
    ]
    out = apply_uncited_topic_penalty(
        entries,
        content="Zhang (2023) [1] 指出教育回报稳定。",
        citation_indices={"10.1/a": 1},
        query="劳动 教育",
    )
    assert out[0]["relevance_score"] == 0.8


def test_review_lit_review_writes_penalized_entries(monkeypatch):
    """评审文献综述章时，把负分写回 literature_entries。"""
    monkeypatch.setattr(
        "agent.nodes.review_chapter.call_review_llm",
        lambda *args, **kwargs: {
            "rubric": {
                "endogeneity": 0.9,
                "identification": 0.9,
                "robustness": 0.9,
                "contribution": 0.9,
                "readability": 0.9,
            },
            "feedback": "ok",
            "suggestions": "ok",
            "review_source": "mock",
            "review_degraded": False,
        },
    )

    state = {
        "current_chapter_index": 1,
        "body_chapters": [
            {
                "type": "lit_review",
                "content": "文献回顾。研究空白。本文定位。没有引用编号。",
            }
        ],
        "literature_query": "劳动 教育",
        "literature_entries": [
            {
                "title": "Returns to Education",
                "abstract": "劳动 教育",
                "doi": "10.1/a",
                "relevance_score": 0.8,
            }
        ],
        "citation_indices": {"10.1/a": 1},
        "review_enabled": True,
        "max_review_iterations": 2,
    }
    result = review_chapter(state)
    assert "literature_entries" in result
    assert result["literature_entries"][0]["relevance_score"] == UNCITED_TOPIC_PENALTY

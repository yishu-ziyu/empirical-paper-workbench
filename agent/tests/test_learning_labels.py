"""#11: 学习标签只从真事件收，禁止把 mock 综合分当奖励。"""
from __future__ import annotations

from agent.nodes.citation_graph import build_citation_graph
from agent.nodes.learning_labels import (
    CITATION_GROUNDED,
    CITATION_UNGROUNDED,
    DEGRADATION,
    HITL_ACCEPT,
    HITL_REJECT,
    REVIEW_CAPPED_FAIL,
    assert_no_mock_score,
    collect_learning_labels,
    _label,
)
from agent.nodes.literature_sources import semantic_scholar
from agent.nodes.review_chapter import review_chapter
from agent.nodes.search_literature import search_literature

from conftest import make_state


def _sources(labels):
    return [item["source"] for item in labels]


def test_label_helper_strips_score_keys():
    item = _label("x", "negative", score=0.91, reward=1.0, review_score=0.4)
    assert_no_mock_score([item])
    assert "score" not in item
    assert "reward" not in item
    assert "review_score" not in item


def test_mock_composite_score_never_enters_labels():
    labels = collect_learning_labels(
        {
            "review_scores": [0.91, 0.12],
            "review_iteration": 0,
            "max_review_iterations": 2,
            "review_chapter_index": 0,
            "hitl_decision": "accept",
        }
    )
    assert_no_mock_score(labels)
    for item in labels:
        assert "score" not in item
        assert "reward" not in item
        assert "review_score" not in item


def test_hitl_reject_writes_negative_label():
    labels = collect_learning_labels(
        {"hitl_decision": "reject", "review_chapter_index": 2}
    )
    assert_no_mock_score(labels)
    assert any(
        item["source"] == HITL_REJECT
        and item["polarity"] == "negative"
        and item["chapter_index"] == 2
        for item in labels
    )


def test_hitl_accept_writes_positive_label():
    labels = collect_learning_labels(
        {"hitl_decision": "accept", "review_chapter_index": 1}
    )
    assert_no_mock_score(labels)
    assert any(
        item["source"] == HITL_ACCEPT and item["polarity"] == "positive"
        for item in labels
    )


def test_force_pass_is_not_true_accept():
    labels = collect_learning_labels(
        {"hitl_decision": "force_pass", "review_chapter_index": 0}
    )
    assert HITL_ACCEPT not in _sources(labels)
    assert HITL_REJECT not in _sources(labels)


def test_capped_fail_emits_negative_without_score():
    labels = collect_learning_labels(
        {
            "review_chapter_index": 0,
            "review_scores": [0.4],
            "review_iteration": 2,
            "max_review_iterations": 2,
        }
    )
    assert_no_mock_score(labels)
    hits = [item for item in labels if item["source"] == REVIEW_CAPPED_FAIL]
    assert len(hits) == 1
    assert hits[0]["polarity"] == "negative"
    assert "score" not in hits[0]


def test_capped_fail_not_emitted_while_retries_remain():
    labels = collect_learning_labels(
        {
            "review_chapter_index": 0,
            "review_scores": [0.4],
            "review_iteration": 1,
            "max_review_iterations": 2,
        }
    )
    assert REVIEW_CAPPED_FAIL not in _sources(labels)


def test_degradation_from_charls_and_search():
    labels = collect_learning_labels(
        {
            "degradations": [{"node": "detect_charls"}],
            "literature_source": "mock_degraded",
            "estimate": {"status": "degraded"},
        }
    )
    assert_no_mock_score(labels)
    nodes = {item.get("node") for item in labels if item["source"] == DEGRADATION}
    assert "detect_charls" in nodes
    assert "search_literature" in nodes
    assert "estimate" in nodes
    assert all(item["polarity"] == "negative" for item in labels if item["source"] == DEGRADATION)


def test_invented_citation_is_negative():
    labels = collect_learning_labels(
        {
            "body_chapters": [
                {
                    "type": "lit_review",
                    "content": "先前研究见 [99]。",
                    "chapter_index": 1,
                }
            ],
            "citation_indices": {"10.1/a": 1},
            "literature_entries": [{"doi": "10.1/a"}],
        }
    )
    assert_no_mock_score(labels)
    assert any(
        item["source"] == CITATION_UNGROUNDED and item["polarity"] == "negative"
        for item in labels
    )
    assert CITATION_GROUNDED not in _sources(labels)


def test_grounded_citation_with_doi_is_positive():
    labels = collect_learning_labels(
        {
            "body_chapters": [
                {
                    "type": "lit_review",
                    "content": "Callaway [1] 处理交错处理。",
                    "chapter_index": 1,
                }
            ],
            "citation_indices": {"10.1/a": 1},
            "literature_entries": [{"doi": "10.1/a"}],
        }
    )
    assert_no_mock_score(labels)
    assert any(
        item["source"] == CITATION_GROUNDED and item["polarity"] == "positive"
        for item in labels
    )
    assert CITATION_UNGROUNDED not in _sources(labels)


def test_did_search_logs_method_anchor(monkeypatch):
    monkeypatch.setattr(
        "agent.nodes.search_literature._mock_search",
        lambda query: [
            {
                "title": "Unrelated",
                "authors": ["A"],
                "year": 2020,
                "abstract": "unrelated",
                "doi": "10.1/u0",
                "source": "mock",
                "relevance_score": 0.5,
            }
        ],
    )
    result = search_literature(
        {"research_direction": {"question": "养老金", "method": "DID"}}
    )
    assert "keyword" in result["literature_actions"]
    assert "method_anchor" in result["literature_actions"]


def test_citation_hop_logs_action(monkeypatch):
    def _fake(doi, api_key=None, max_results=20):
        return ["10.99/external"]

    monkeypatch.setattr(semantic_scholar, "semantic_scholar_references", _fake)
    result = build_citation_graph(
        {
            "literature_entries": [
                {"title": "A", "year": 2020, "doi": "10.1/a", "citation_count": 9}
            ],
            "literature_actions": ["keyword"],
        }
    )
    assert "citation_hop" in result["literature_actions"]
    assert "keyword" in result["literature_actions"]


LOW_SCORE_RUBRIC = {
    "endogeneity": 0.1,
    "identification": 0.1,
    "robustness": 0.1,
    "contribution": 0.1,
    "readability": 0.1,
}


def _chapter():
    return {
        "type": "intro",
        "title": "引言",
        "content": "章节内容",
        "status": "generated",
        "versions": ["章节内容"],
        "chapter_index": 0,
    }


def test_review_retry_does_not_count_as_capped_fail(monkeypatch):
    monkeypatch.setattr(
        "agent.nodes.review_chapter.call_review_llm",
        lambda *a, **k: {
            "rubric": LOW_SCORE_RUBRIC,
            "feedback": "差",
            "suggestions": "改",
            "review_source": "mock",
            "review_degraded": False,
        },
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_chapter()],
        review_iteration=1,
        max_review_iterations=2,
        review_chapter_index=0,
    )
    result = review_chapter(state)
    assert result["review_iteration"] == 2
    assert REVIEW_CAPPED_FAIL not in _sources(result.get("learning_labels") or [])
    assert_no_mock_score(result.get("learning_labels") or [])


def test_review_at_cap_emits_capped_fail_without_score(monkeypatch):
    monkeypatch.setattr(
        "agent.nodes.review_chapter.call_review_llm",
        lambda *a, **k: {
            "rubric": LOW_SCORE_RUBRIC,
            "feedback": "差",
            "suggestions": "改",
            "review_source": "mock",
            "review_degraded": False,
        },
    )
    state = make_state(
        review_enabled=True,
        current_chapter_index=1,
        body_chapters=[_chapter()],
        review_iteration=2,
        max_review_iterations=2,
        review_chapter_index=0,
    )
    result = review_chapter(state)
    labels = result.get("learning_labels") or []
    assert_no_mock_score(labels)
    assert any(item["source"] == REVIEW_CAPPED_FAIL for item in labels)
    for item in labels:
        assert "score" not in item
        assert "reward" not in item

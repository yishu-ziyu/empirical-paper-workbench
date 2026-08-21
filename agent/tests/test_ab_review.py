"""三位审稿代理对照：看得见机器分 vs 看不见。"""
from __future__ import annotations

from eval.ab_review import run_ab
from eval.judge import judge, rule_judge
from eval.packets import (
    packet_good_methods,
    packet_invented_cite,
    packet_keyword_intro,
    packet_overclaim_results,
    packet_weak_iv,
)
from eval.personas import persona_ids
from nodes.label_store import append_event, event_from_decision, read_events
from nodes.learning_labels import assert_no_mock_score


def test_three_personas_exist():
    assert set(persona_ids()) == {
        "applied_micro",
        "econometrician",
        "journal_referee",
    }


def test_good_methods_accepted_even_when_blind():
    for persona in persona_ids():
        verdict = rule_judge(persona, packet_good_methods(), see_auto=False)
        assert verdict["decision"] == "accept", persona


def test_invented_citation_rejected_in_both_arms():
    state = packet_invented_cite()
    for persona in persona_ids():
        for see_auto in (False, True):
            verdict = rule_judge(persona, state, see_auto=see_auto)
            assert verdict["decision"] == "reject", (persona, see_auto)


def test_keyword_intro_blind_rejects_see_auto_accepts():
    """机器说通过时，看得见分的人会放过堆词；看不见的人会否决。"""
    state = packet_keyword_intro()
    for persona in persona_ids():
        blind = rule_judge(persona, state, see_auto=False)
        seen = rule_judge(persona, state, see_auto=True)
        assert blind["decision"] == "reject", persona
        assert seen["decision"] == "accept", persona


def test_overclaim_splits_by_persona_when_blind():
    state = packet_overclaim_results()
    assert rule_judge("applied_micro", state, see_auto=False)["decision"] == "reject"
    assert rule_judge("journal_referee", state, see_auto=False)["decision"] == "reject"
    assert rule_judge("econometrician", state, see_auto=False)["decision"] == "accept"


def test_weak_iv_rejected_by_econometrician():
    state = packet_weak_iv()
    assert rule_judge("econometrician", state, see_auto=False)["decision"] == "reject"
    assert rule_judge("econometrician", state, see_auto=True)["decision"] == "reject"


def test_run_ab_writes_labels_without_scores(tmp_path, monkeypatch):
    path = tmp_path / "labels.jsonl"
    monkeypatch.setenv("LEARNING_LABELS_PATH", str(path))
    report = run_ab(allow_llm=False, persist=True)
    assert report["n"] == 30  # 5 稿 × 3 人 × 2 组
    events = read_events()
    assert len(events) == 30
    for event in events:
        assert_no_mock_score(event["labels"])
        assert "score" not in event
        assert event["reviewer_kind"] == "persona_agent"
        assert event["persona"] in persona_ids()
    see = report["by_arm"]["see_auto"]["agree_with_auto"]
    blind = report["by_arm"]["blind"]["agree_with_auto"]
    assert see is not None and blind is not None
    assert see > blind
    assert report["rubber_stamp"] > 0


def test_event_from_human_decision_persists(tmp_path, monkeypatch):
    path = tmp_path / "human.jsonl"
    monkeypatch.setenv("LEARNING_LABELS_PATH", str(path))
    state = {
        "session_id": "s1",
        "hitl_decision": "reject",
        "review_chapter_index": 0,
        "review_scores": [0.9],
        "body_chapters": [{"type": "intro", "content": "x", "chapter_index": 0}],
    }
    event = event_from_decision(
        state,
        decision="reject",
        reviewer="alice",
        reviewer_kind="human",
        ab_arm="human",
    )
    append_event(event)
    loaded = read_events(session_id="s1")
    assert len(loaded) == 1
    assert loaded[0]["reviewer"] == "alice"
    assert any(item["source"] == "hitl_reject" for item in loaded[0]["labels"])
    assert_no_mock_score(loaded[0]["labels"])


def test_judge_rules_path_does_not_need_llm():
    verdict = judge(
        "applied_micro",
        packet_keyword_intro(),
        see_auto=False,
        allow_llm=False,
    )
    assert verdict["judge_source"] == "rules"
    assert verdict["decision"] == "reject"

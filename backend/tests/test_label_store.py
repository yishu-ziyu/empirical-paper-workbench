"""点通过/否决后，标签要写到文件，重启还能读。"""
from __future__ import annotations

import uuid

import routers.labels  # noqa: F401
import routers.review  # noqa: F401
from facade import facade
from agent.nodes.label_store import read_events
from agent.nodes.learning_labels import assert_no_mock_score

from conftest import make_state


HIGH_RUBRIC = {
    "endogeneity": 0.9,
    "identification": 0.85,
    "robustness": 0.8,
    "contribution": 0.9,
    "readability": 0.85,
}


def _seed_reviewed(tmp_path, monkeypatch) -> str:
    path = tmp_path / "learning_labels.jsonl"
    monkeypatch.setenv("LEARNING_LABELS_PATH", str(path))
    sid = f"test-labels-{uuid.uuid4()}"
    score = 0.86
    facade.seed_state(
        sid,
        make_state(
            session_id=sid,
            current_chapter_index=1,
            review_chapter_index=0,
            review_feedback=["ok"],
            revision_suggestions=["x"],
            review_scores=[score],
            review_rubrics=[HIGH_RUBRIC],
            review_iteration=1,
            max_review_iterations=2,
            body_chapters=[{"type": "intro", "content": "正文", "chapter_index": 0}],
        ),
    )
    return sid


def test_post_decision_survives_in_label_file(client, tmp_path, monkeypatch):
    sid = _seed_reviewed(tmp_path, monkeypatch)

    def _fake_regenerate(self_inner, session_id, chapter_index):
        return self_inner.get_state(session_id)

    monkeypatch.setattr("facade.AgentFacade.regenerate_chapter", _fake_regenerate)
    resp = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "reject", "reviewer": "alice", "comment": "识别没写清"},
    )
    assert resp.status_code == 200, resp.text
    events = read_events(session_id=sid)
    assert len(events) == 1
    event = events[0]
    assert event["reviewer"] == "alice"
    assert event["reviewer_kind"] == "human"
    assert event["decision"] == "reject"
    assert event["ab_arm"] == "human"
    assert_no_mock_score(event["labels"])
    assert any(item["source"] == "hitl_reject" for item in event["labels"])


def test_get_labels_exports_persisted_events(client, tmp_path, monkeypatch):
    sid = _seed_reviewed(tmp_path, monkeypatch)
    posted = client.post(
        f"/sessions/{sid}/review/decision",
        json={"decision": "accept", "reviewer": "bob"},
    )
    assert posted.status_code == 200, posted.text
    resp = client.get("/labels", params={"session_id": sid})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["n"] == 1
    assert data["events"][0]["reviewer"] == "bob"
    assert data["events"][0]["decision"] == "accept"
    assert "by_arm" in data["summary"]

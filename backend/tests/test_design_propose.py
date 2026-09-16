"""INF-BE-propose endpoint: title → session.design draft. No confirm / attach."""
from __future__ import annotations

import uuid

from facade import facade


def _new_session(client) -> str:
    resp = client.post("/sessions")
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


def _propose(client, session_id: str, title: str, question: str = ""):
    return client.post(
        f"/sessions/{session_id}/design/propose",
        json={"title": title, "question": question},
    )


def _did_term(design: dict) -> bool:
    return any(
        isinstance(item, dict)
        and item.get("kind") == "did"
        and item.get("term") == "treated:period"
        for item in (design.get("interactions") or [])
    )


def test_ck_title_proposes_did_before_any_attach(client):
    sid = _new_session(client)
    resp = _propose(client, sid, "最低工资对就业的影响")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["method"] == "did"
    assert data["status"] == "draft"
    assert data["confirmed"] is False
    assert data["confirmed_at"] is None
    assert data["catalog_entry_id"] is None
    assert _did_term(data)
    assert data["outcome"] == "employment"
    assert data["treatment"] == "min_wage"

    state = facade.get_state(sid)
    assert state["design"]["method"] == "did"
    assert state["design"]["status"] == "draft"
    assert "dataAttached" not in state
    assert state.get("dataAttached") is not True
    assert "allow_did" not in state
    assert "allow_did" not in (state.get("design") or {})
    assert "research_direction" not in state
    assert "main_specification" not in state
    assert "body_chapters" not in state
    assert not state.get("csv_path")


def test_level_ols_title_does_not_open_did(client):
    sid = _new_session(client)
    resp = _propose(client, sid, "教育对工资的影响")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["method"] == "ols"
    assert not _did_term(data)
    state = facade.get_state(sid)
    assert state["design"]["method"] == "ols"
    assert state.get("dataAttached") is not True


def test_barro_title_proposes_ols(client):
    sid = _new_session(client)
    resp = _propose(client, sid, "经济增长的决定因素")
    assert resp.status_code == 200, resp.text
    assert resp.json()["method"] == "ols"
    assert not _did_term(resp.json())


def test_catalog_id_alone_cannot_open_did(client):
    sid = _new_session(client)
    resp = _propose(client, sid, "ck1994_long")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["method"] == "ols"
    assert not _did_term(data)
    assert data["catalog_entry_id"] is None


def test_catalog_token_minimum_wage_employment_cannot_open_did(client):
    sid = _new_session(client)
    resp = _propose(client, sid, "minimum-wage-employment")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["method"] == "ols"
    assert not _did_term(data)


def test_repropose_overwrites_confirmed_with_new_draft(client):
    sid = _new_session(client)
    facade.seed_state(
        sid,
        {
            "design": {
                "status": "confirmed",
                "confirmed": True,
                "confirmed_at": "2026-01-01T00:00:00Z",
                "method": "ols",
                "catalog_entry_id": "ck1994_long",
            }
        },
    )
    resp = _propose(client, sid, "最低工资对就业的影响")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "draft"
    assert data["confirmed"] is False
    assert data["confirmed_at"] is None
    assert data["catalog_entry_id"] is None
    assert data["method"] == "did"
    stored = facade.get_state(sid)["design"]
    assert stored["status"] == "draft"
    assert stored["confirmed"] is False


def test_propose_does_not_set_data_attached_even_if_absent(client):
    sid = _new_session(client)
    _propose(client, sid, "最低工资对就业的影响")
    state = facade.get_state(sid)
    assert "dataAttached" not in state
    assert "table1Confirmed" not in state
    assert "specConfirmed" not in state


def test_propose_leaves_existing_data_attached_untouched(client):
    sid = f"propose-keep-attach-{uuid.uuid4().hex[:8]}"
    facade.seed_state(sid, {"dataAttached": True})
    try:
        resp = _propose(client, sid, "教育对工资的影响")
        assert resp.status_code == 200, resp.text
        state = facade.get_state(sid)
        assert state["dataAttached"] is True
        assert state["design"]["method"] == "ols"
    finally:
        facade.drop_session(sid)


def test_missing_session_is_404(client):
    resp = _propose(client, "no-such-session", "最低工资对就业的影响")
    assert resp.status_code == 404


def test_empty_title_is_400(client):
    sid = _new_session(client)
    resp = _propose(client, sid, "   ")
    assert resp.status_code == 400

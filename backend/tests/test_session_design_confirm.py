"""INF-BE-confirm: human confirm locks session.design (DECIDE-6).

Does not cover propose, suggest, attach, DID allow_did, or chapter write.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from facade import facade
from .confirmation_helpers import confirm_seen_design
from services.session_design import (
    DESIGN_NOT_PROPOSED,
    DesignNotProposed,
    is_design_confirmed,
    lock_confirmed_design,
    locked_design,
)


def _draft(**overrides) -> dict:
    design = {
        "status": "draft",
        "confirmed": False,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": None,
        "source": {"title": "最低工资对就业的影响", "question": ""},
        "method": "did",
        "outcome": "employment",
        "treatment": "min_wage",
        "controls": [],
        "group": "treated",
        "treated": "treated",
        "period": "post",
        "time_col": "",
        "id_col": "",
        "first_treat_col": "",
        "interactions": [
            {
                "kind": "did",
                "left": "treated",
                "right": "period",
                "term": "treated:period",
            }
        ],
        "qType": "causal",
        "heterogeneity_groups": [],
        "catalog_entry_id": None,
    }
    design.update(overrides)
    return design


def _seed(sid: str, design=None, **extra) -> str:
    state = dict(extra)
    if design is not None:
        state["design"] = design
    facade.seed_state(sid, state)
    return sid


# ---------------------------------------------------------------------------
# Service: lock transition
# ---------------------------------------------------------------------------


def test_lock_requires_draft():
    with pytest.raises(DesignNotProposed) as exc:
        lock_confirmed_design(None)
    assert exc.value.code == DESIGN_NOT_PROPOSED
    with pytest.raises(DesignNotProposed):
        lock_confirmed_design({})
    with pytest.raises(DesignNotProposed):
        lock_confirmed_design({"status": "confirmed", "confirmed": False})


def test_lock_stamps_confirmed_and_keeps_fields():
    now = datetime(2026, 9, 15, 13, tzinfo=timezone.utc)
    locked = lock_confirmed_design(_draft(), now=now)
    assert locked["status"] == "confirmed"
    assert locked["confirmed"] is True
    assert locked["confirmed_at"] == "2026-09-15T13:00:00Z"
    assert locked["proposed_at"] == "2026-09-15T12:00:00Z"
    assert locked["method"] == "did"
    assert locked["outcome"] == "employment"
    assert locked["interactions"][0]["term"] == "treated:period"
    assert locked["catalog_entry_id"] is None


def test_lock_clears_catalog_entry_id():
    locked = lock_confirmed_design(_draft(catalog_entry_id="ck1994_long"))
    assert locked["catalog_entry_id"] is None


def test_lock_idempotent_when_already_confirmed():
    first = lock_confirmed_design(_draft())
    again = lock_confirmed_design(first)
    assert again["status"] == "confirmed"
    assert again["confirmed_at"] == first["confirmed_at"]


def test_unconfirmed_cannot_unlock_spec():
    """DECIDE-6 accept bullet 4 hook: missing/draft is not a locked spec."""
    assert locked_design({}) is None
    assert locked_design({"design": None}) is None
    assert locked_design({"design": _draft()}) is None
    assert locked_design({"design": _draft(catalog_entry_id="ck1994")}) is None
    assert is_design_confirmed({"design": _draft()}) is False
    assert is_design_confirmed({}) is False

    locked = lock_confirmed_design(_draft())
    state = {"design": locked}
    assert is_design_confirmed(state) is True
    assert locked_design(state)["method"] == "did"
    assert locked_design(state)["catalog_entry_id"] is None


# ---------------------------------------------------------------------------
# Facade + HTTP
# ---------------------------------------------------------------------------


def test_confirm_endpoint_locks_draft(client):
    sid = _seed("confirm-locks-draft", _draft())
    try:
        resp = confirm_seen_design(client, sid)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["ok"] is True
        design = body["design"]
        assert design["status"] == "confirmed"
        assert design["confirmed"] is True
        assert design["confirmed_at"]
        assert design["confirmed_at"].endswith("Z")
        assert design["catalog_entry_id"] is None
        assert design["method"] == "did"
        stored = facade.get_state(sid)["design"]
        assert stored["status"] == "confirmed"
        assert stored["confirmed"] is True
        assert is_design_confirmed(facade.get_state(sid)) is True
    finally:
        facade.drop_session(sid)


@pytest.mark.parametrize(
    "state",
    [{}, {"design": None}, {"design": "draft"}, {"design": {"method": "did"}}],
)
def test_confirm_rejects_missing_draft(client, state):
    sid = f"confirm-no-draft-{id(state)}"
    facade.seed_state(sid, state)
    try:
        resp = client.post(f"/sessions/{sid}/design/confirm")
        assert resp.status_code == 409, resp.text
        assert resp.json()["detail"] == {"code": DESIGN_NOT_PROPOSED}
        assert "design" not in facade.get_state(sid) or facade.get_state(sid).get(
            "design"
        ) == state.get("design")
        assert is_design_confirmed(facade.get_state(sid)) is False
        assert locked_design(facade.get_state(sid)) is None
    finally:
        facade.drop_session(sid)


def test_confirm_unknown_session_404(client):
    resp = client.post("/sessions/no-such-session/design/confirm")
    assert resp.status_code == 404


def test_confirm_idempotent_http(client):
    sid = _seed("confirm-idempotent", _draft())
    try:
        first = confirm_seen_design(client, sid)
        assert first.status_code == 200
        stamp = first.json()["design"]["confirmed_at"]
        second = confirm_seen_design(client, sid)
        assert second.status_code == 200
        assert second.json()["design"]["status"] == "confirmed"
        assert second.json()["design"]["confirmed_at"] == stamp
    finally:
        facade.drop_session(sid)


def test_confirm_does_not_write_downstream_gates(client):
    sid = _seed(
        "confirm-no-side-effects",
        _draft(),
        dataAttached=False,
        allow_did=False,
        table1Confirmed=False,
        specConfirmed=False,
        body_chapters=[],
        main_specification=None,
        research_direction=None,
    )
    try:
        resp = confirm_seen_design(client, sid)
        assert resp.status_code == 200, resp.text
        state = facade.get_state(sid)
        assert state["dataAttached"] is False
        assert state["allow_did"] is False
        assert state["table1Confirmed"] is False
        assert state["specConfirmed"] is False
        assert state["body_chapters"] == []
        assert state["main_specification"] is None
        assert state["research_direction"] is None
        # Bullet 5 hook: lock is visible so later suggest/attach may proceed.
        assert locked_design(state) is not None
        assert locked_design(state)["status"] == "confirmed"
    finally:
        facade.drop_session(sid)


def test_snapshot_projects_draft_and_confirmed(client):
    sid = _seed("confirm-snapshot", _draft())
    try:
        before = client.get(f"/sessions/{sid}")
        assert before.status_code == 200
        assert before.json()["design"]["status"] == "draft"
        assert before.json()["design"]["confirmed"] is False
        confirm_seen_design(client, sid)
        after = client.get(f"/sessions/{sid}")
        assert after.json()["design"]["status"] == "confirmed"
        assert after.json()["design"]["confirmed"] is True
    finally:
        facade.drop_session(sid)


def test_snapshot_missing_design_is_null(client):
    sid = _seed("confirm-snapshot-empty")
    try:
        data = client.get(f"/sessions/{sid}").json()
        assert data["design"] is None
    finally:
        facade.drop_session(sid)


def test_facade_confirm_design_raises_409():
    sid = _seed("confirm-facade-409")
    try:
        with pytest.raises(HTTPException) as exc:
            facade.confirm_design(sid)
        assert exc.value.status_code == 409
        assert exc.value.detail == {"code": DESIGN_NOT_PROPOSED}
    finally:
        facade.drop_session(sid)

"""FD-BE-plan endpoint: confirmed design → session.find_data plan. No attach."""
from __future__ import annotations

import uuid

from facade import facade


def _new_session(client) -> str:
    resp = client.post("/sessions")
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


def _confirmed(**overrides):
    design = {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": "2026-09-15T12:01:00Z",
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


def _plan(client, session_id: str):
    return client.post(f"/sessions/{session_id}/find-data/plan")


def test_missing_session_is_404(client):
    resp = _plan(client, "no-such-session")
    assert resp.status_code == 404


def test_unconfirmed_design_is_409(client):
    sid = _new_session(client)
    resp = _plan(client, sid)
    assert resp.status_code == 409, resp.text
    assert "unconfirmed" in resp.json()["detail"]
    state = facade.get_state(sid)
    assert "find_data" not in state or state.get("find_data") in (None, {})
    assert state.get("dataAttached") is not True

    facade.seed_state(
        sid,
        {"design": _confirmed(status="draft", confirmed=False, confirmed_at=None)},
    )
    resp = _plan(client, sid)
    assert resp.status_code == 409, resp.text
    get = client.get(f"/sessions/{sid}/find-data")
    assert get.status_code == 200, get.text
    body = get.json()
    assert body["status"] == "missing"
    assert body["plan"] is None
    assert body["candidates"] == []


def test_confirmed_minwage_returns_where_how_plan_stub(client):
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed()})
    resp = _plan(client, sid)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "planned"
    assert data["route_family"] == "minwage"
    assert data["primary_venue"] == "ck fixture + Card zip"
    assert "ck fixture" in data["plan"]["where"]
    assert "Card zip" in data["plan"]["where"]
    assert "Dataverse" in data["plan"]["how"]
    assert data["plan"]["venues"][0] == "captain-local-real"
    assert "captain-local-real" in data["plan"]["how"]
    assert "teaching toys" in data["plan"]["how"]
    assert data["plan"]["search_facets"]["outcome"] == "employment"
    assert data["plan"]["search_facets"]["treatment"] == "min_wage"
    assert data["plan"]["search_facets"]["method"] == "did"
    assert "treated:period" in data["plan"]["search_facets"]["interactions"]
    ids = [item["source_id"] for item in data["candidates"]]
    assert ids[0] == "captain-local-real"
    local = next(item for item in data["candidates"] if item["source_id"] == "captain-local-real")
    assert local["acquire"] is True
    assert local["found"] is False
    assert local["url_or_fixture"] == "/upload"
    assert "card-zip:njmin" in ids
    assert "classic-5:ck1994_long" in ids
    assert all(
        item.get("found") is not False
        for item in data["candidates"]
        if item["source_id"] != "captain-local-real"
    )
    assert all(not item.get("teaching_fixture") for item in data["candidates"])
    ck = next(item for item in data["candidates"] if item["source_id"] == "classic-5:ck1994_long")
    assert ck["n_rows"] >= 200
    assert "wage1" not in ids

    state = facade.get_state(sid)
    assert state["find_data"]["status"] == "planned"
    assert state.get("dataAttached") is not True
    assert "dataAttached" not in state
    assert "allow_did" not in state
    assert state["design"]["status"] == "confirmed"
    assert "body_chapters" not in state
    assert not state.get("csv_path")

    stored = client.get(f"/sessions/{sid}/find-data")
    assert stored.status_code == 200
    assert stored.json()["route_family"] == "minwage"
    stored_ids = [item["source_id"] for item in stored.json()["candidates"]]
    assert "card-zip:njmin" in stored_ids
    assert "classic-5:ck1994_long" in stored_ids


def test_educ_wage_and_growth_routes(client):
    sid = _new_session(client)
    facade.seed_state(
        sid,
        {
            "design": _confirmed(
                source={"title": "教育对工资的影响", "question": ""},
                method="ols",
                outcome="wages",
                treatment="schooling",
                interactions=[],
                qType="average",
                treated="",
                period="",
                group="",
            )
        },
    )
    resp = _plan(client, sid)
    assert resp.status_code == 200, resp.text
    assert resp.json()["route_family"] == "educ_wage"
    assert resp.json()["primary_venue"] == "IPUMS"
    assert "wage1" not in resp.json()["plan"]["where"]

    facade.seed_state(
        sid,
        {
            "design": _confirmed(
                source={"title": "经济增长的决定因素", "question": ""},
                method="ols",
                outcome="growth",
                treatment="",
                interactions=[],
                qType="average",
                treated="",
                period="",
                group="",
            )
        },
    )
    resp = _plan(client, sid)
    assert resp.status_code == 200, resp.text
    assert resp.json()["route_family"] == "growth"
    assert resp.json()["primary_venue"] == "WDI"
    assert "barro" not in resp.json()["plan"]["where"]


def test_plan_does_not_clear_or_set_data_attached(client):
    sid = f"find-data-keep-attach-{uuid.uuid4().hex[:8]}"
    facade.seed_state(sid, {"design": _confirmed(), "dataAttached": True})
    try:
        resp = _plan(client, sid)
        assert resp.status_code == 200, resp.text
        state = facade.get_state(sid)
        assert state["dataAttached"] is True
        assert state["find_data"]["status"] == "planned"
        assert state["find_data"]["candidates"]
        assert "table1Confirmed" not in state
        assert "specConfirmed" not in state
    finally:
        facade.drop_session(sid)


def test_plan_is_not_catalog_prefill(client):
    sid = _new_session(client)
    facade.seed_state(
        sid,
        {
            "design": _confirmed(
                catalog_entry_id=None,
                source={"title": "教育对工资的影响", "question": ""},
                method="ols",
                outcome="wages",
                treatment="schooling",
                interactions=[],
                qType="average",
                treated="",
                period="",
                group="",
            )
        },
    )
    resp = _plan(client, sid)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    dumped = str(data)
    assert "ck1994" not in dumped
    assert "schooling-wages" not in dumped
    ids = [item["source_id"] for item in data["candidates"]]
    assert ids[0] == "captain-local-real"
    assert "ipums:cps" in ids
    assert "wage1" not in ids
    assert any(sid.startswith("dataverse:") for sid in ids)
    state = facade.get_state(sid)
    assert state["design"]["catalog_entry_id"] is None

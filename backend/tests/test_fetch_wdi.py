"""FD-BE-fetch-wdi endpoint: confirmed growth → WDI download or honest link."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from facade import facade
from run_store import run_dir

from agent.find_data.fetch_wdi import DEFAULT_INDICATOR


def _new_session(client) -> str:
    resp = client.post("/sessions")
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


def _confirmed_growth(**overrides):
    design = {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": "2026-09-15T12:01:00Z",
        "source": {
            "title": "Barro growth: determinants of economic growth",
            "question": "",
        },
        "method": "ols",
        "outcome": "growth",
        "treatment": "sec_enroll",
        "controls": [],
        "group": "",
        "treated": "",
        "period": "",
        "time_col": "",
        "id_col": "",
        "first_treat_col": "",
        "interactions": [],
        "qType": "average",
        "heterogeneity_groups": [],
        "catalog_entry_id": None,
    }
    design.update(overrides)
    return design


def _confirmed_minwage():
    return {
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


def _wb_bytes() -> bytes:
    """Synthetic World Bank v2 JSON — test double, not found data."""
    payload = [
        {
            "page": 1,
            "pages": 1,
            "per_page": 2,
            "total": 2,
            "sourceid": "2",
            "lastupdated": "2024-01-01",
        },
        [
            {
                "indicator": {
                    "id": DEFAULT_INDICATOR,
                    "value": "GDP per capita growth (annual %)",
                },
                "country": {"id": "US", "value": "United States"},
                "countryiso3code": "USA",
                "date": "2020",
                "value": 1.2,
            },
            {
                "indicator": {
                    "id": DEFAULT_INDICATOR,
                    "value": "GDP per capita growth (annual %)",
                },
                "country": {"id": "US", "value": "United States"},
                "countryiso3code": "USA",
                "date": "2021",
                "value": 2.3,
            },
        ],
    ]
    return json.dumps(payload).encode("utf-8")


def _fetch(client, session_id: str):
    return client.post(f"/sessions/{session_id}/find-data/fetch-wdi")


def test_missing_session_is_404(client):
    resp = _fetch(client, "no-such-session")
    assert resp.status_code == 404


def test_unconfirmed_design_is_409(client):
    sid = _new_session(client)
    resp = _fetch(client, sid)
    assert resp.status_code == 409, resp.text
    assert "unconfirmed" in resp.json()["detail"]
    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    fetch_dir = run_dir(sid) / "workspace" / "fetch"
    assert not fetch_dir.exists() or not list(fetch_dir.glob("*.csv"))


def test_minwage_design_is_409_not_barro_and_not_attached(client):
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed_minwage()})
    resp = _fetch(client, sid)
    assert resp.status_code == 409, resp.text
    assert "growth" in resp.json()["detail"]
    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    assert state["design"]["status"] == "confirmed"
    fetch_dir = run_dir(sid) / "workspace" / "fetch"
    assert not fetch_dir.exists() or not list(fetch_dir.glob("*.csv"))


def test_growth_download_into_session_is_not_barro(client):
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed_growth(), "dataAttached": False})
    with patch(
        "agent.find_data.fetch_wdi._default_http_get",
        return_value=_wb_bytes(),
    ):
        resp = _fetch(client, sid)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["source_id"] == f"wdi:{DEFAULT_INDICATOR}"
    assert data["source_kind"] == "fetched"
    assert data["fetch"]["status"] == "into_session"
    assert data["fetch"]["session_path"]
    assert "barro1991_growth" not in json.dumps(data)
    assert "classic-5" not in json.dumps(data)
    assert data["url_or_fixture"].startswith("https://data.worldbank.org/indicator/")

    dest = Path(facade._workspace_dir(sid)) / "fetch" / f"wdi_{DEFAULT_INDICATOR}.csv"
    assert dest.is_file()
    text = dest.read_text(encoding="utf-8")
    assert "United States" in text
    assert DEFAULT_INDICATOR in text
    assert "enrollment" not in text

    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    assert "allow_did" not in state
    assert state["find_data"]["wdi_fetch"]["source_kind"] == "fetched"
    assert state["design"]["status"] == "confirmed"


def test_growth_http_failure_is_link_plus_upload(client):
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed_growth()})
    with patch(
        "agent.find_data.fetch_wdi._default_http_get",
        side_effect=OSError("down"),
    ):
        resp = _fetch(client, sid)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["source_kind"] == "external_link"
    assert data["fetch"]["status"] == "link_only"
    assert data["fetch"]["session_path"] is None
    assert data["fetch"]["reason"] == "http_error"
    assert "upload" in data["design_fit"]["notes"].lower()
    assert "barro1991_growth" not in json.dumps(data)
    assert data["url_or_fixture"].startswith("https://data.worldbank.org/indicator/")
    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    assert not list((Path(facade._workspace_dir(sid)) / "fetch").glob("*.csv"))


def test_fetch_does_not_clear_existing_attach_flag(client):
    sid = _new_session(client)
    facade.seed_state(
        sid,
        {
            "design": _confirmed_growth(),
            "dataAttached": True,
            "find_data": {"status": "planned", "candidates": []},
        },
    )
    with patch(
        "agent.find_data.fetch_wdi._default_http_get",
        side_effect=OSError("down"),
    ):
        resp = _fetch(client, sid)
    assert resp.status_code == 200, resp.text
    state = facade.get_state(sid)
    assert state["dataAttached"] is True
    assert state["find_data"]["wdi_fetch"]["source_kind"] == "external_link"
    assert state["find_data"]["status"] == "planned"

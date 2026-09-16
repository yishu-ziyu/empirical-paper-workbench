"""FD-BE-fetch-dataverse endpoint: confirmed design → Dataverse fetch or link."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

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


def _hit():
    return {
        "source_id": "dataverse:doi:10.7910/DVN/TEST01",
        "title": "Replication package (synthetic test double)",
        "url_or_fixture": "https://doi.org/10.7910/DVN/TEST01",
        "license": "CC0 1.0",
        "suggested_cols": [],
    }


def _fetch(client, session_id: str, **body):
    return client.post(
        f"/sessions/{session_id}/find-data/fetch-dataverse",
        json=body,
    )


def test_unconfirmed_design_is_409(client):
    sid = _new_session(client)
    resp = _fetch(client, sid)
    assert resp.status_code == 409, resp.text
    assert "unconfirmed" in resp.json()["detail"]
    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    assert "find_data" not in state or state.get("find_data") in (None, {})


def test_public_download_into_session_does_not_attach(client, monkeypatch):
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed()})
    body = b"employment,treated,period\n1,1,0\n"  # synthetic test double

    def _search(_q: str):
        return [_hit()]

    def _files(_pid: str):
        return [
            {
                "id": "4242",
                "filename": "panel.csv",
                "contentType": "text/csv",
                "restricted": False,
            }
        ]

    def _download(_fid: str):
        return body, "text/csv", "panel.csv"

    monkeypatch.setattr(
        "agent.find_data.dataverse.search_dataverse",
        _search,
    )
    with patch(
        "agent.find_data.dataverse.list_dataset_files",
        _files,
    ), patch(
        "agent.find_data.dataverse.download_datafile",
        _download,
    ):
        resp = _fetch(client, sid)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "planned"
    candidates = data["candidates"]
    assert candidates
    fetched = next(c for c in candidates if c["source_kind"] == "fetched")
    assert fetched["fetch"]["status"] == "into_session"
    rel = fetched["fetch"]["session_path"]
    written = Path(facade._workspace_dir(sid)) / rel
    assert written.is_file()
    assert written.read_bytes() == body

    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    assert "dataAttached" not in state
    assert "allow_did" not in state
    assert not state.get("csv_path")
    assert "classic-5" not in str(candidates)
    assert "ck1994" not in str(candidates)

    stored = client.get(f"/sessions/{sid}/find-data")
    assert stored.status_code == 200
    assert stored.json()["candidates"][0]["source_kind"] in {"discovered", "fetched"}


def test_search_miss_returns_dataverse_link_not_fixture(client):
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed(catalog_entry_id="ck1994_long")})
    with patch(
        "agent.find_data.dataverse.search_dataverse",
        return_value=[],
    ):
        resp = _fetch(client, sid)
    assert resp.status_code == 200, resp.text
    rows = resp.json()["candidates"]
    assert rows
    assert rows[0]["source_id"] == "dataverse:search"
    assert rows[0]["source_kind"] == "external_link"
    assert rows[0]["fetch"]["status"] == "link_only"
    assert "dataverse.harvard.edu" in rows[0]["url_or_fixture"]
    dumped = str(rows)
    assert "classic-5" not in dumped
    assert "ck1994_long.csv" not in dumped
    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True

"""FD-BE-fetch-card endpoint: confirmed minwage zip staging. No attach."""
from __future__ import annotations

import io
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

from config import settings
from facade import facade

from agent.find_data.card_zip import (
    CARD_ZIP_LANDING_URL,
    CARD_ZIP_POSTED_URL,
    CARD_ZIP_SOURCE_ID,
    SESSION_RELATIVE_PATH,
)


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


def _synthetic_zip() -> bytes:
    """Labeled synthetic archive for tests/ only — not product found data."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("public.dat", "synthetic test double; not found data\n")
    return buf.getvalue()


def _fetch(client, session_id: str):
    return client.post(f"/sessions/{session_id}/find-data/fetch-card")


def test_missing_session_is_404(client):
    resp = _fetch(client, "no-such-session")
    assert resp.status_code == 404


def test_unconfirmed_design_is_409(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    sid = _new_session(client)
    resp = _fetch(client, sid)
    assert resp.status_code == 409, resp.text
    assert "unconfirmed" in resp.json()["detail"]
    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    assert not list((tmp_path / "runs").rglob("njmin.zip"))


def test_confirmed_minwage_downloads_zip_into_session(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed()})
    zip_bytes = _synthetic_zip()

    def _read(url: str) -> bytes:
        if url == CARD_ZIP_POSTED_URL:
            return zip_bytes
        if url == CARD_ZIP_LANDING_URL:
            return (
                b'<html><a href="data_sets/njmin.zip">data set</a></html>'
            )
        raise OSError(url)

    with patch("agent.find_data.card_zip.read_url_bytes", _read):
        resp = _fetch(client, sid)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "planned"
    assert data["route_family"] == "minwage"
    assert data["candidates"], data
    card = next(c for c in data["candidates"] if c["source_id"] == CARD_ZIP_SOURCE_ID)
    assert card["source_kind"] == "fetched"
    assert card["fetch"]["status"] == "into_session"
    assert card["fetch"]["session_path"] == SESSION_RELATIVE_PATH
    assert card["url_or_fixture"] == CARD_ZIP_LANDING_URL
    assert "ck1994" not in card["source_id"]
    assert "/demos/card" not in str(data)

    written = tmp_path / "runs" / sid / "workspace" / SESSION_RELATIVE_PATH
    assert written.is_file()
    assert written.read_bytes() == zip_bytes
    assert written.read_bytes().startswith(b"PK")

    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    assert "dataAttached" not in state
    assert "allow_did" not in state
    assert not state.get("csv_path")
    stored = client.get(f"/sessions/{sid}/find-data")
    assert stored.status_code == 200
    assert stored.json()["candidates"][0]["fetch"]["status"] == "into_session"


def test_failed_download_keeps_link_and_honest_upload(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed()})

    def _read(_url: str) -> bytes:
        raise OSError("network down")

    with patch("agent.find_data.card_zip.read_url_bytes", _read):
        resp = _fetch(client, sid)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    card = next(c for c in data["candidates"] if c["source_id"] == CARD_ZIP_SOURCE_ID)
    assert card["source_kind"] == "external_link"
    assert card["fetch"]["status"] == "link_only"
    assert card["fetch"]["session_path"] is None
    assert card["url_or_fixture"] == CARD_ZIP_LANDING_URL
    assert "honest upload" in card["fetch"]["reason"]
    assert "ck1994" not in card["source_id"]
    assert not list((tmp_path / "runs" / sid / "workspace").rglob("*.zip"))
    assert facade.get_state(sid).get("dataAttached") is not True


def test_fixture_csv_bytes_are_not_the_zip(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed()})
    csv = b"employment,treated,period\n1,1,0\n"

    def _read(_url: str) -> bytes:
        return csv

    with patch("agent.find_data.card_zip.read_url_bytes", _read):
        resp = _fetch(client, sid)
    assert resp.status_code == 200, resp.text
    card = resp.json()["candidates"][0]
    assert card["source_kind"] == "external_link"
    assert card["fetch"]["status"] == "link_only"
    workspace = tmp_path / "runs" / sid / "workspace"
    if workspace.exists():
        for path in workspace.rglob("*"):
            if path.is_file():
                assert path.read_bytes() != csv
                assert not path.name.endswith(".csv")


def test_growth_design_is_409(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    sid = _new_session(client)
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
    with patch(
        "agent.find_data.card_zip.read_url_bytes",
        side_effect=AssertionError("must not fetch"),
    ):
        resp = _fetch(client, sid)
    assert resp.status_code == 409, resp.text
    assert "not_minwage" in resp.json()["detail"]
    assert facade.get_state(sid).get("dataAttached") is not True


def test_fetch_does_not_clear_existing_data_attached(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    sid = f"fetch-card-keep-attach-{uuid.uuid4().hex[:8]}"
    facade.seed_state(sid, {"design": _confirmed(), "dataAttached": True})
    try:
        with patch("agent.find_data.card_zip.read_url_bytes", lambda _url: _synthetic_zip()):
            resp = _fetch(client, sid)
        assert resp.status_code == 200, resp.text
        state = facade.get_state(sid)
        assert state["dataAttached"] is True
        assert "allow_did" not in state
        assert "table1Confirmed" not in state
        assert "specConfirmed" not in state
        card = next(
            c for c in state["find_data"]["candidates"] if c["source_id"] == CARD_ZIP_SOURCE_ID
        )
        assert card["fetch"]["status"] == "into_session"
        assert Path(tmp_path / "runs" / sid / "workspace" / SESSION_RELATIVE_PATH).is_file()
    finally:
        facade.drop_session(sid)

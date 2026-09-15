"""FD-BE-honesty HTTP: suggest labels source_kind + teaching shelf. No attach."""
from __future__ import annotations

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


def test_suggest_unconfirmed_is_409(client, monkeypatch):
    monkeypatch.setattr(
        "agent.find_data.candidates.search_dataverse",
        lambda _q: [],
    )
    sid = _new_session(client)
    resp = client.post(f"/sessions/{sid}/find-data/suggest")
    assert resp.status_code == 409, resp.text
    assert client.get(f"/sessions/{sid}/find-data").json()["status"] == "missing"


def test_suggest_labels_external_link_and_optional_shelf(client, monkeypatch, tmp_path):
    monkeypatch.setattr(
        "agent.find_data.candidates.search_dataverse",
        lambda _q: [
            {
                "name": "Replication data",
                "global_id": "doi:10.7910/DVN/TEST01",
                "url": "https://doi.org/10.7910/DVN/TEST01",
                "license": "CC0 1.0",
                "type": "dataset",
            }
        ],
    )
    (tmp_path / "ck1994_long.csv").write_text("employment,treated,period\n1,1,0\n")
    monkeypatch.setattr(
        "agent.find_data.candidates._DEFAULT_CLASSIC5",
        tmp_path,
    )
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed()})
    planned = client.post(f"/sessions/{sid}/find-data/plan")
    assert planned.status_code == 200, planned.text
    assert planned.json()["candidates"] == []

    resp = client.post(f"/sessions/{sid}/find-data/suggest")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "planned"
    assert data["plan"]["where"] == "Card zip"
    kinds = {c["source_id"]: c["source_kind"] for c in data["candidates"]}
    assert kinds["card-zip:njmin"] == "external_link"
    assert kinds["dataverse:doi:10.7910/DVN/TEST01"] == "discovered"
    assert "classic-5:ck1994_long" not in kinds
    dumped = str(data)
    assert "找到了 ck1994" not in dumped
    shelf = data["teaching_shelf"]
    assert shelf is not None
    assert "teaching-known" in shelf["label"]
    assert "教学已知样本" in shelf["label"]
    fixture = shelf["candidates"][0]
    assert fixture["source_kind"] == "teaching_fixture"
    assert fixture["source_id"] == "classic-5:ck1994_long"
    assert fixture["fetch"]["status"] == "not_applicable"
    state = facade.get_state(sid)
    assert state.get("dataAttached") is not True
    assert "allow_did" not in state

    stored = client.get(f"/sessions/{sid}/find-data")
    assert stored.status_code == 200
    assert stored.json()["teaching_shelf"]["candidates"][0]["source_kind"] == "teaching_fixture"


def test_suggest_does_not_pad_with_classic5_when_catalog_empty(client, monkeypatch, tmp_path):
    monkeypatch.setattr(
        "agent.find_data.candidates.search_dataverse",
        lambda _q: [],
    )
    monkeypatch.setattr(
        "agent.find_data.candidates._DEFAULT_CLASSIC5",
        tmp_path,
    )
    sid = _new_session(client)
    facade.seed_state(sid, {"design": _confirmed()})
    resp = client.post(f"/sessions/{sid}/find-data/suggest")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    ids = [c["source_id"] for c in data["candidates"]]
    assert "card-zip:njmin" in ids
    assert any(sid.startswith("dataverse:") for sid in ids)
    assert not any(sid.startswith("classic-5:") for sid in ids)
    assert data.get("teaching_shelf") is None
    assert all(c["source_kind"] in {"discovered", "external_link"} for c in data["candidates"])

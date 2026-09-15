"""Contract tests for confirmed-design → classic-5 suggest (DC-BE-suggest recut).

Pins DECIDE-6 accept bullet 5: after confirm, suggest matches design facets
(method/vars); fixtures are candidates only. Without confirm, catalog is
not a success path and must not prefill spec or open DiD.
"""
from __future__ import annotations

import json
from pathlib import Path

import routers.classic5 as classic5_router
import services.classic5_catalog as catalog
from facade import facade
from services.classic5_catalog import (
    design_is_confirmed,
    rank_entries_for_design,
    read_catalog,
    suggest_candidates,
)

_FORBIDDEN_SUCCESS_KEYS = {
    "allow_did",
    "selected",
    "spec",
    "main_specification",
    "formula",
    "gold",
    "body",
    "chapters",
    "dataAttached",
    "data_attached",
    "table1Confirmed",
    "specConfirmed",
    "teaching_case",
}

_DEFAULT_ENTRY_IDS = [
    "schooling-wages",
    "ck1994_long",
    "trade-local-labor",
    "fiscal-output",
    "health-labor-supply",
    "barro1991_growth",
]


def _write_catalog(path: Path, entries: list[dict]) -> Path:
    path.write_text(
        json.dumps({"catalog_id": "classic-5", "entries": entries}, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def _confirmed_design(**fields) -> dict:
    design = {
        "status": "confirmed",
        "confirmed": True,
        "method": "ols",
        "outcome": "",
        "treatment": "",
        "catalog_entry_id": None,
        "source": {"title": "", "question": ""},
    }
    source = fields.pop("source", None)
    design.update(fields)
    if source is not None:
        design["source"] = source
    return design


def _assert_candidates_only(payload: dict) -> None:
    assert payload["catalog_id"] == "classic-5"
    assert payload["attached"] is False
    assert payload["own_file"] == {"action": "upload_own_file", "catalog": False}
    for key in _FORBIDDEN_SUCCESS_KEYS:
        assert key not in payload
    for item in payload["candidates"]:
        assert item["source"] == "classic-5"
        assert item["catalog_id"] == "classic-5"
        assert item["attached"] is False
        for key in _FORBIDDEN_SUCCESS_KEYS:
            assert key not in item


def test_default_catalog_has_ranking_stubs_with_matching_facets():
    entries = read_catalog()
    assert [item.entry_id for item in entries] == _DEFAULT_ENTRY_IDS
    by_id = {item.entry_id: item for item in entries}
    assert by_id["ck1994_long"].method == "did"
    assert by_id["barro1991_growth"].method == "ols"
    assert by_id["ck1994_long"].outcome
    assert by_id["barro1991_growth"].treatment
    assert all(item.title for item in entries)


def test_unconfirmed_design_is_not_a_catalog_success():
    assert design_is_confirmed(None) is False
    assert design_is_confirmed({}) is False
    assert design_is_confirmed({"status": "draft", "method": "did"}) is False
    assert design_is_confirmed({"confirmed": False, "method": "did"}) is False
    payload = suggest_candidates("最低工资对就业的影响", design={"status": "draft", "method": "did"})
    _assert_candidates_only(payload)
    assert payload["design_confirmed"] is False
    assert payload["candidates"] == []


def test_title_only_does_not_rank_classic_as_success():
    payload = suggest_candidates("最低工资对就业的影响")
    _assert_candidates_only(payload)
    assert payload["design_confirmed"] is False
    assert payload["candidates"] == []
    ids = [item["entry_id"] for item in payload["candidates"]]
    assert "ck1994_long" not in ids


def test_confirmed_flag_without_status_fails_closed():
    design = {"confirmed": True, "method": "did", "outcome": "employment", "treatment": "min_wage"}
    assert design_is_confirmed(design) is False
    payload = suggest_candidates(design=design)
    _assert_candidates_only(payload)
    assert payload["design_confirmed"] is False
    assert payload["candidates"] == []


def test_confirmed_did_minwage_lists_ck1994_as_candidate():
    design = _confirmed_design(
        method="did",
        outcome="employment",
        treatment="min_wage",
        source={"title": "最低工资对就业的影响", "question": ""},
    )
    payload = suggest_candidates(design=design)
    _assert_candidates_only(payload)
    assert payload["design_confirmed"] is True
    ids = [item["entry_id"] for item in payload["candidates"]]
    assert ids[0] == "ck1994_long"
    assert "barro1991_growth" not in ids
    assert payload["candidates"][0]["method"] == "did"
    assert payload["candidates"][0]["score"] > 0


def test_confirmed_ols_growth_lists_barro_as_candidate():
    design = _confirmed_design(
        method="ols",
        outcome="growth",
        treatment="sec_enroll",
        source={"title": "Barro growth and schooling", "question": ""},
    )
    payload = suggest_candidates(design=design)
    _assert_candidates_only(payload)
    ids = [item["entry_id"] for item in payload["candidates"]]
    assert ids[0] == "barro1991_growth"
    assert "ck1994_long" not in ids


def test_confirmed_ols_schooling_does_not_open_did_fixture():
    design = _confirmed_design(
        method="ols",
        outcome="wages",
        treatment="schooling",
        source={"title": "returns to schooling and wages", "question": ""},
    )
    ranked = rank_entries_for_design(read_catalog(), design)
    ids = [item.entry_id for item, _score in ranked]
    assert ids[0] == "schooling-wages"
    assert "ck1994_long" not in ids
    payload = suggest_candidates(design=design)
    assert all(item["method"] != "did" for item in payload["candidates"])


def test_catalog_id_alone_does_not_lock_spec_or_did():
    payload = suggest_candidates("ck1994_long")
    _assert_candidates_only(payload)
    assert payload["design_confirmed"] is False
    assert payload["candidates"] == []


def test_suggest_payload_never_attaches_or_prefills():
    payload = suggest_candidates(
        design=_confirmed_design(
            method="ols",
            outcome="employment",
            treatment="import",
            source={"title": "import competition and manufacturing", "question": ""},
        )
    )
    _assert_candidates_only(payload)
    assert payload["candidates"][0]["entry_id"] == "trade-local-labor"


def test_suggest_endpoint_without_confirm_returns_empty_candidates(client):
    resp = client.post(
        "/classic-5/suggest",
        json={"title": "Health and hours of work", "topic": ""},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    _assert_candidates_only(data)
    assert data["design_confirmed"] is False
    assert data["candidates"] == []


def test_suggest_endpoint_after_confirm_matches_design(client):
    sid = client.post("/sessions").json()["session_id"]
    facade.update_state(
        sid,
        design=_confirmed_design(
            method="difference-in-differences",
            outcome="employment",
            treatment="min_wage",
            source={"title": "最低工资对就业的影响", "question": ""},
        ),
    )
    snap_before = client.get(f"/sessions/{sid}").json()

    resp = client.post("/classic-5/suggest", json={"session_id": sid})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    _assert_candidates_only(data)
    assert data["design_confirmed"] is True
    assert data["candidates"][0]["entry_id"] == "ck1994_long"
    assert data["title"] == "最低工资对就业的影响"

    snap_after = client.get(f"/sessions/{sid}").json()
    assert snap_after == snap_before
    state = facade.get_state(sid)
    assert state.get("research_direction") is None
    assert state.get("main_specification") is None
    assert (state.get("design") or {}).get("catalog_entry_id") is None
    assert "allow_did" not in state


def test_suggest_endpoint_draft_design_is_not_success(client):
    sid = client.post("/sessions").json()["session_id"]
    facade.update_state(
        sid,
        design={
            "status": "draft",
            "confirmed": False,
            "method": "did",
            "outcome": "employment",
            "treatment": "min_wage",
            "source": {"title": "最低工资对就业的影响", "question": ""},
        },
    )
    resp = client.post("/classic-5/suggest", json={"session_id": sid})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["design_confirmed"] is False
    assert data["candidates"] == []
    assert data["own_file"]["action"] == "upload_own_file"


def test_suggest_rejects_empty_request(client):
    resp = client.post("/classic-5/suggest", json={"title": "  ", "topic": ""})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "session_id or title or topic is required"


def test_suggest_missing_session_404(client):
    resp = client.post("/classic-5/suggest", json={"session_id": "missing-session"})
    assert resp.status_code == 404


def test_suggest_does_not_create_or_mutate_session(client):
    before = client.post("/sessions")
    assert before.status_code == 200
    sid = before.json()["session_id"]
    snap_before = client.get(f"/sessions/{sid}")
    assert snap_before.status_code == 200
    body_before = snap_before.json()

    resp = client.post(
        "/classic-5/suggest",
        json={"title": "财政乘数与政府支出", "topic": "local output"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["design_confirmed"] is False
    assert data["candidates"] == []
    assert "session_id" not in data
    assert "run_id" not in data
    assert "events_url" not in data
    assert "dataset_meta" not in data

    snap_after = client.get(f"/sessions/{sid}")
    assert snap_after.status_code == 200
    body_after = snap_after.json()
    assert body_after == body_before
    assert body_after["has_dataset"] is False
    assert body_after.get("upload_readiness") in {None, "FAILED", "CANCELLED"}


def test_suggest_env_catalog_override_uses_confirmed_design(client, tmp_path, monkeypatch):
    catalog_file = _write_catalog(
        tmp_path / "catalog.json",
        [
            {
                "id": "alpha-trade",
                "title": "Alpha trade panel",
                "topic": "import shock",
                "method": "ols",
                "outcome": "employment",
                "treatment": "import",
                "tags": ["trade", "import"],
            },
            {
                "id": "beta-health",
                "title": "Beta health hours",
                "topic": "labor supply",
                "method": "ols",
                "outcome": "hours",
                "treatment": "health",
                "tags": ["health"],
            },
        ],
    )
    monkeypatch.setenv("ECONPAPER_CLASSIC5_CATALOG", str(catalog_file))
    sid = client.post("/sessions").json()["session_id"]
    facade.update_state(
        sid,
        design=_confirmed_design(
            method="ols",
            outcome="employment",
            treatment="import",
            source={"title": "import shock trade", "question": ""},
        ),
    )
    resp = client.post("/classic-5/suggest", json={"session_id": sid})
    assert resp.status_code == 200, resp.text
    ids = [item["entry_id"] for item in resp.json()["candidates"]]
    assert ids[0] == "alpha-trade"
    assert ids == ["alpha-trade", "beta-health"]
    assert resp.json()["candidates"][0]["score"] > resp.json()["candidates"][1]["score"]


def test_suggest_empty_catalog_still_returns_own_file(client, tmp_path, monkeypatch):
    missing = tmp_path / "missing-catalog.json"
    monkeypatch.setenv("ECONPAPER_CLASSIC5_CATALOG", str(missing))
    sid = client.post("/sessions").json()["session_id"]
    facade.update_state(sid, design=_confirmed_design(method="ols", outcome="y"))
    resp = client.post("/classic-5/suggest", json={"session_id": sid})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["design_confirmed"] is True
    assert data["candidates"] == []
    assert data["own_file"]["action"] == "upload_own_file"
    assert data["attached"] is False


def test_suggest_modules_have_no_attach_or_did_lock():
    forbidden = {
        "admit_upload",
        "card_demo",
        "RunRepository",
        "dataAttached",
        "table1Confirmed",
        "specConfirmed",
        "allow_did",
        "load_entry_bytes",
        "admit_classic5",
    }
    assert forbidden.isdisjoint(classic5_router.__dict__)
    assert forbidden.isdisjoint(catalog.__dict__)
    assert "facade" not in catalog.__dict__
    assert not hasattr(catalog, "load_entry_bytes")
    assert not hasattr(catalog, "admit_classic5")
    assert not hasattr(catalog, "allow_did")

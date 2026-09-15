"""Contract tests for TITLE/TOPIC → classic-5 suggest (DC-BE-suggest).

Pins: ranked catalog candidates + own-file action; suggest must not
attach or write dataAttached; formal path only (not /demos/card).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import routers.classic5 as classic5_router
import services.classic5_catalog as catalog
from config import PRODUCT_ROOT
from facade import facade
from services.classic5_catalog import rank_entries, read_catalog, suggest_candidates

_CLASSIC5_DIR = PRODUCT_ROOT / "fixtures" / "classic-5"


def _write_catalog(path: Path, entries: list[dict]) -> Path:
    path.write_text(
        json.dumps({"catalog_id": "classic-5", "entries": entries}, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


_DEFAULT_ENTRY_IDS = [
    "schooling-wages",
    "ck1994_long",
    "trade-local-labor",
    "fiscal-output",
    "health-labor-supply",
    "barro1991_growth",
]


def test_default_catalog_includes_ck1994_and_barro_entries():
    entries = read_catalog()
    assert [item.entry_id for item in entries] == _DEFAULT_ENTRY_IDS
    assert all(item.title for item in entries)


def test_rank_schooling_query_beats_fiscal():
    entries = read_catalog()
    ranked = rank_entries(entries, "returns to schooling and wages")
    order = [item.entry_id for item, _score in ranked]
    assert order[0] == "schooling-wages"
    assert order.index("schooling-wages") < order.index("fiscal-output")
    assert ranked[0][1] > ranked[order.index("fiscal-output")][1]


def test_rank_chinese_minimum_wage_query():
    ranked = rank_entries(read_catalog(), "最低工资对就业的影响")
    assert ranked[0][0].entry_id == "ck1994_long"
    assert ranked[0][1] > 0


def test_rank_min_wage_and_card_krueger_hit_ck1994():
    for query in ("min wage", "Card Krueger"):
        ranked = rank_entries(read_catalog(), query)
        assert ranked[0][0].entry_id == "ck1994_long", query
        assert ranked[0][1] > 0


def test_rank_growth_and_barro_hit_barro1991():
    for query in ("growth", "Barro"):
        ranked = rank_entries(read_catalog(), query)
        assert ranked[0][0].entry_id == "barro1991_growth", query
        assert ranked[0][1] > 0


def test_suggest_endpoint_hits_ck1994_and_barro_keywords(client):
    cases = (
        ({"title": "min wage"}, "ck1994_long"),
        ({"title": "Card Krueger"}, "ck1994_long"),
        ({"topic": "growth"}, "barro1991_growth"),
        ({"title": "Barro"}, "barro1991_growth"),
    )
    for body, entry_id in cases:
        resp = client.post("/classic-5/suggest", json=body)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["candidates"][0]["entry_id"] == entry_id
        assert data["attached"] is False


def test_classic5_fixture_csvs_have_required_columns():
    required = {
        "ck1994_long.csv": [
            "store_id",
            "state",
            "treated",
            "period",
            "fte",
            "wage",
            "chain",
        ],
        "barro1991_growth.csv": [
            "country",
            "gdp_pc_initial",
            "growth",
            "sec_enroll",
            "prim_enroll",
            "inv_share",
            "gov_share",
            "pop_growth",
        ],
    }
    for name, columns in required.items():
        path = _CLASSIC5_DIR / name
        assert path.is_file(), name
        with path.open(encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))
        assert header == columns
    assert (_CLASSIC5_DIR / "SOURCE.txt").is_file()


def test_suggest_payload_never_attaches():
    payload = suggest_candidates("import competition and manufacturing")
    assert payload["catalog_id"] == "classic-5"
    assert payload["attached"] is False
    assert "dataAttached" not in payload
    assert "data_attached" not in payload
    assert payload["own_file"] == {"action": "upload_own_file", "catalog": False}
    assert payload["candidates"][0]["entry_id"] == "trade-local-labor"
    for item in payload["candidates"]:
        assert item["source"] == "classic-5"
        assert item["catalog_id"] == "classic-5"
        assert item["attached"] is False
        assert "teaching_case" not in item


def test_suggest_endpoint_ranks_and_keeps_own_file(client):
    resp = client.post(
        "/classic-5/suggest",
        json={"title": "Health and hours of work", "topic": ""},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["catalog_id"] == "classic-5"
    assert data["attached"] is False
    assert data["own_file"]["action"] == "upload_own_file"
    assert data["own_file"]["catalog"] is False
    assert data["candidates"][0]["entry_id"] == "health-labor-supply"
    ids = [item["entry_id"] for item in data["candidates"]]
    assert ids.count("ck1994_long") == 1
    assert ids.count("barro1991_growth") == 1
    assert set(ids) == set(_DEFAULT_ENTRY_IDS)


def test_suggest_rejects_empty_title_and_topic(client):
    resp = client.post("/classic-5/suggest", json={"title": "  ", "topic": ""})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "title or topic is required"


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
    assert data["candidates"][0]["entry_id"] == "fiscal-output"
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
    # Snapshot always projects the confirm-attach gate after DC-BE-attach.
    # Suggest must not flip it or write state; false is the unattached default.
    assert body_after["dataAttached"] is False
    assert "data_attached" not in body_after
    assert facade.get_state(sid).get("dataAttached") is None
    assert facade.get_state(sid).get("data_attached") is not True


def test_suggest_env_catalog_override(client, tmp_path, monkeypatch):
    catalog_file = _write_catalog(
        tmp_path / "catalog.json",
        [
            {
                "id": "alpha-trade",
                "title": "Alpha trade panel",
                "topic": "import shock",
                "tags": ["trade", "import"],
            },
            {
                "id": "beta-health",
                "title": "Beta health hours",
                "topic": "labor supply",
                "tags": ["health"],
            },
        ],
    )
    monkeypatch.setenv("ECONPAPER_CLASSIC5_CATALOG", str(catalog_file))
    resp = client.post("/classic-5/suggest", json={"topic": "import shock trade"})
    assert resp.status_code == 200, resp.text
    ids = [item["entry_id"] for item in resp.json()["candidates"]]
    assert ids == ["alpha-trade", "beta-health"]
    assert resp.json()["candidates"][0]["score"] > resp.json()["candidates"][1]["score"]


def test_suggest_empty_catalog_still_returns_own_file(client, tmp_path, monkeypatch):
    missing = tmp_path / "missing-catalog.json"
    monkeypatch.setenv("ECONPAPER_CLASSIC5_CATALOG", str(missing))
    resp = client.post("/classic-5/suggest", json={"title": "any topic"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["candidates"] == []
    assert data["own_file"]["action"] == "upload_own_file"
    assert data["attached"] is False


def test_suggest_modules_have_no_attach_imports():
    forbidden = {
        "admit_upload",
        "card_demo",
        "facade",
        "RunRepository",
        "dataAttached",
        "table1Confirmed",
        "specConfirmed",
    }
    assert forbidden.isdisjoint(classic5_router.__dict__)
    assert forbidden.isdisjoint(catalog.__dict__)
    assert not hasattr(catalog, "load_entry_bytes")
    assert not hasattr(catalog, "admit_classic5")

"""FD-BE-fetch-dataverse: live search/download or honest link. Never fixture-as-found."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent.find_data import apply_dataverse_fetch, search_and_fetch_dataverse
from agent.find_data.dataverse import (
    DesignUnconfirmed,
    SESSION_FETCH_DIR,
    list_dataset_files,
    persistent_id_from_source_id,
)
from agent.find_data.candidates import is_real_candidate


def _confirmed(**overrides) -> dict:
    design = {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": "2026-09-15T12:05:00Z",
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
    if "source" in overrides and isinstance(overrides["source"], dict):
        source = {"title": "", "question": ""}
        source.update(overrides["source"])
        design["source"] = source
    return design


def _hit(**overrides) -> dict:
    item = {
        "source_id": "dataverse:doi:10.7910/DVN/TEST01",
        "title": "Replication package (synthetic test double)",
        "url_or_fixture": "https://doi.org/10.7910/DVN/TEST01",
        "license": "CC0 1.0",
        "suggested_cols": [],
    }
    item.update(overrides)
    return item


def _public_csv() -> dict:
    return {
        "id": "4242",
        "filename": "panel.csv",
        "contentType": "text/csv",
        "restricted": False,
    }


def _assert_dataverse_only(rows: list) -> None:
    assert rows, "expected ≥1 Dataverse path (hit or search URL)"
    for item in rows:
        assert is_real_candidate(item), item
        assert str(item["source_id"]).startswith("dataverse:")
        assert item["source_kind"] in {"discovered", "fetched", "external_link"}
        assert not str(item["url_or_fixture"]).startswith("fixtures/")
        assert "classic-5:" not in str(item["source_id"])
        assert "ck1994" not in str(item["source_id"])
        assert item.get("attached") is not True
        assert "dataAttached" not in item
        assert "allow_did" not in item
        fetch = item["fetch"]
        assert fetch["status"] in {"into_session", "link_only"}
        if item["source_kind"] == "fetched":
            assert fetch["status"] == "into_session"
            assert fetch["session_path"]
        else:
            assert fetch["status"] == "link_only"
            assert fetch["session_path"] is None


def test_unconfirmed_design_returns_no_candidates(tmp_path: Path):
    (tmp_path / "ck1994_long.csv").write_text("employment,treated,period\n1,1,0\n")
    for design in (
        None,
        {},
        {"status": "missing"},
        {"status": "draft", "confirmed": False, "source": {"title": "最低工资对就业的影响"}},
        {"status": "confirmed"},
        _confirmed(status="draft", confirmed=False, confirmed_at=None),
    ):
        rows = search_and_fetch_dataverse(
            design or {},
            workspace=tmp_path,
            search=lambda _q: [_hit()],
            list_files=lambda _pid: [_public_csv()],
            download_file=lambda _fid: (b"employment,treated\n1,1\n", "text/csv", "panel.csv"),
        )
        assert rows == [], design


def test_unconfirmed_apply_raises(tmp_path: Path):
    with pytest.raises(DesignUnconfirmed):
        apply_dataverse_fetch(
            {"design": _confirmed(status="draft", confirmed=False)},
            workspace=tmp_path,
        )


def test_public_file_downloads_into_session(tmp_path: Path):
    body = b"employment,treated,period\n1,1,0\n"  # synthetic test double
    rows = search_and_fetch_dataverse(
        _confirmed(),
        workspace=tmp_path,
        search=lambda _q: [_hit()],
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (body, "text/csv", "panel.csv"),
    )
    _assert_dataverse_only(rows)
    fetched = next(c for c in rows if c["source_kind"] == "fetched")
    rel = fetched["fetch"]["session_path"]
    assert rel == f"{SESSION_FETCH_DIR}/panel.csv"
    written = tmp_path / rel
    assert written.is_file()
    assert written.read_bytes() == body
    assert fetched["fetch"]["status"] == "into_session"
    assert "not attached" in fetched["design_fit"]["notes"]
    blob = json.dumps(rows)
    assert "classic-5" not in blob
    assert "ck1994_long" not in blob


def test_restricted_file_stays_link_only(tmp_path: Path):
    calls = {"download": 0}

    def _download(_fid: str):
        calls["download"] += 1
        return b"secret", "text/csv", "secret.csv"

    rows = search_and_fetch_dataverse(
        _confirmed(),
        workspace=tmp_path,
        search=lambda _q: [_hit()],
        list_files=lambda _pid: [
            {
                "id": "9",
                "filename": "secret.csv",
                "contentType": "text/csv",
                "restricted": True,
            }
        ],
        download_file=_download,
    )
    _assert_dataverse_only(rows)
    assert all(c["source_kind"] == "discovered" for c in rows)
    assert all(c["fetch"]["status"] == "link_only" for c in rows)
    assert "restricted" in rows[0]["fetch"]["reason"]
    assert calls["download"] == 0
    assert not (tmp_path / SESSION_FETCH_DIR).exists()
    assert rows[0]["url_or_fixture"].startswith("https://")


def test_html_landing_is_not_a_fetched_table(tmp_path: Path):
    html = b"<!DOCTYPE html><html><body>dataset page</body></html>"
    rows = search_and_fetch_dataverse(
        _confirmed(),
        workspace=tmp_path,
        search=lambda _q: [_hit()],
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (html, "text/html; charset=utf-8", "dataset.html"),
    )
    _assert_dataverse_only(rows)
    assert rows[0]["source_kind"] == "discovered"
    assert rows[0]["fetch"]["status"] == "link_only"
    assert "HTML" in rows[0]["fetch"]["reason"]
    assert list(tmp_path.glob("**/*.html")) == []
    assert list(tmp_path.glob("**/*.csv")) == []


def test_search_miss_still_shows_dataverse_not_fixture(tmp_path: Path):
    (tmp_path / "ck1994_long.csv").write_text("employment,treated,period\n1,1,0\n")
    rows = search_and_fetch_dataverse(
        _confirmed(catalog_entry_id="ck1994_long"),
        workspace=tmp_path,
        search=lambda _q: [],
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (b"x", "text/csv", "x.csv"),
    )
    _assert_dataverse_only(rows)
    assert len(rows) == 1
    assert rows[0]["source_id"] == "dataverse:search"
    assert rows[0]["source_kind"] == "external_link"
    assert "dataverse.harvard.edu" in rows[0]["url_or_fixture"]
    assert "fixture" in rows[0]["design_fit"]["notes"]
    assert "ck1994" not in json.dumps(rows)


def test_search_error_still_shows_dataverse_path(tmp_path: Path):
    def _boom(_q: str):
        raise RuntimeError("network down")

    rows = search_and_fetch_dataverse(
        _confirmed(),
        workspace=tmp_path,
        search=_boom,
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (b"x", "text/csv", "x.csv"),
    )
    _assert_dataverse_only(rows)
    assert rows[0]["source_kind"] == "external_link"
    assert rows[0]["url_or_fixture"].startswith("http")


def test_fixture_source_id_is_ignored(tmp_path: Path):
    fixture = tmp_path / "ck1994_long.csv"
    fixture.write_text("employment,treated,period\n1,1,0\n")
    rows = search_and_fetch_dataverse(
        _confirmed(),
        workspace=tmp_path,
        source_id="classic-5:ck1994_long",
        search=lambda _q: [_hit()],
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (b"employment,treated\n1,0\n", "text/csv", "panel.csv"),
    )
    _assert_dataverse_only(rows)
    assert all(not str(c["source_id"]).startswith("classic-5:") for c in rows)
    fetched = [c for c in rows if c["source_kind"] == "fetched"]
    assert fetched
    written = (tmp_path / fetched[0]["fetch"]["session_path"]).read_bytes()
    assert written != fixture.read_bytes()


def test_fixture_search_hit_is_dropped(tmp_path: Path):
    rows = search_and_fetch_dataverse(
        _confirmed(),
        workspace=tmp_path,
        search=lambda _q: [
            {
                "source_id": "classic-5:ck1994_long",
                "title": "Card and Krueger minimum wage",
                "url_or_fixture": "fixtures/classic-5/ck1994_long.csv",
                "license": "public-reproduction",
                "suggested_cols": ["employment"],
            }
        ],
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (b"x", "text/csv", "x.csv"),
    )
    _assert_dataverse_only(rows)
    assert rows[0]["source_kind"] == "external_link"
    assert "classic-5" not in json.dumps(rows)


def test_catalog_id_does_not_hide_dataverse(tmp_path: Path):
    rows = search_and_fetch_dataverse(
        _confirmed(catalog_entry_id="ck1994_long"),
        workspace=tmp_path,
        search=lambda _q: [_hit()],
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (b"a,b\n1,2\n", "text/csv", "panel.csv"),
    )
    _assert_dataverse_only(rows)
    ids = [c["source_id"] for c in rows]
    assert "dataverse:doi:10.7910/DVN/TEST01" in ids
    assert not any(sid.startswith("classic-5:") for sid in ids)


def test_apply_does_not_set_attach_or_did(tmp_path: Path):
    record = apply_dataverse_fetch(
        {"design": _confirmed(), "dataAttached": False},
        workspace=tmp_path,
        search=lambda _q: [_hit()],
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (b"a,b\n1,2\n", "text/csv", "panel.csv"),
    )
    assert record["status"] == "planned"
    assert record.get("dataAttached") is None
    blob = json.dumps(record)
    assert "allow_did" not in blob
    _assert_dataverse_only(record["candidates"])


def test_apply_keeps_existing_plan_and_puts_dataverse_first(tmp_path: Path):
    prior = {
        "status": "planned",
        "planned_at": "2026-09-15T12:02:00Z",
        "route_family": "minwage",
        "primary_venue": "ck fixture + Card zip",
        "plan": {"where": "ck fixture + Card zip", "how": "x", "venues": [], "search_facets": {}},
        "candidates": [
            {
                "source_id": "classic-5:ck1994_long",
                "title": "Card and Krueger minimum wage",
                "url_or_fixture": "fixtures/classic-5/ck1994_long.csv",
                "license": "public-reproduction",
                "suggested_cols": ["employment"],
                "design_fit": {"method": "did", "notes": "candidate only"},
            }
        ],
    }
    record = apply_dataverse_fetch(
        {"design": _confirmed(), "find_data": prior},
        workspace=tmp_path,
        search=lambda _q: [_hit()],
        list_files=lambda _pid: [_public_csv()],
        download_file=lambda _fid: (b"a,b\n1,2\n", "text/csv", "panel.csv"),
    )
    assert record["plan"]["where"] == "ck fixture + Card zip"
    ids = [c["source_id"] for c in record["candidates"]]
    assert ids[0].startswith("dataverse:")
    assert record["candidates"][0]["source_kind"] in {"discovered", "fetched"}
    fixture = next(c for c in record["candidates"] if c["source_id"].startswith("classic-5:"))
    assert fixture.get("source_kind") not in {"discovered", "fetched"}


def test_persistent_id_from_source_id():
    assert persistent_id_from_source_id("dataverse:doi:10.7910/DVN/ABC") == "doi:10.7910/DVN/ABC"
    assert persistent_id_from_source_id("dataverse:search") is None
    assert persistent_id_from_source_id("classic-5:ck1994_long") is None
    assert persistent_id_from_source_id("https://doi.org/10.7910/DVN/ABC") == "doi:10.7910/DVN/ABC"


def test_list_dataset_files_maps_ok_payload():
    payload = {
        "status": "OK",
        "data": [
            {
                "label": "panel.dta",
                "restricted": False,
                "dataFile": {
                    "id": 77,
                    "filename": "panel.dta",
                    "contentType": "application/x-stata-13",
                    "restricted": False,
                },
            }
        ],
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(payload).encode("utf-8")
    mock_resp.__enter__ = lambda self: self
    mock_resp.__exit__ = lambda *args: None
    with patch("agent.find_data.dataverse.urllib.request.urlopen", return_value=mock_resp):
        files = list_dataset_files("doi:10.7910/DVN/ABC")
    assert files == [
        {
            "id": "77",
            "filename": "panel.dta",
            "contentType": "application/x-stata-13",
            "restricted": False,
        }
    ]


def test_list_dataset_files_error_is_empty():
    with patch(
        "agent.find_data.dataverse.urllib.request.urlopen",
        side_effect=OSError("down"),
    ):
        assert list_dataset_files("doi:10.7910/DVN/ABC") == []

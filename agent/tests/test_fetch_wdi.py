"""FD-BE-fetch-wdi: WDI public download or honest link. Not Barro-as-found.

HTTP payloads below are synthetic World Bank JSON test doubles — not found data.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent.find_data.candidates import is_real_candidate
from agent.find_data.fetch_wdi import (
    DEFAULT_INDICATOR,
    DesignUnconfirmed,
    WdiFetchNotApplicable,
    fetch_wdi,
    wdi_page_url,
)
from agent.find_data.plan import classify_route_family


def _confirmed_growth(**overrides) -> dict:
    design = {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": "2026-09-15T12:05:00Z",
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
    if "source" in overrides and isinstance(overrides["source"], dict):
        source = {"title": "", "question": ""}
        source.update(overrides["source"])
        design["source"] = source
    return design


def _confirmed_minwage() -> dict:
    return {
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


def _wb_payload(n: int = 3) -> list:
    """Synthetic World Bank v2 envelope — test double, not found data."""
    items = []
    for i in range(n):
        items.append(
            {
                "indicator": {
                    "id": DEFAULT_INDICATOR,
                    "value": "GDP per capita growth (annual %)",
                },
                "country": {"id": "US", "value": "United States"},
                "countryiso3code": "USA",
                "date": str(2018 + i),
                "value": 1.0 + i * 0.1,
            }
        )
    return [
        {
            "page": 1,
            "pages": 1,
            "per_page": n,
            "total": n,
            "sourceid": "2",
            "lastupdated": "2024-01-01",
        },
        items,
    ]


def _http_json(payload) -> callable:
    blob = json.dumps(payload).encode("utf-8")

    def _get(_url: str) -> bytes:
        return blob

    return _get


def _assert_wdi_row(row: dict, *, fetched: bool) -> None:
    assert is_real_candidate(row), row
    assert row["source_id"] == f"wdi:{DEFAULT_INDICATOR}"
    assert row["url_or_fixture"] == wdi_page_url(DEFAULT_INDICATOR)
    assert "barro1991_growth" not in json.dumps(row)
    assert "classic-5" not in json.dumps(row)
    assert "dataAttached" not in row
    assert "allow_did" not in row
    assert row.get("attached") is not True
    fetch = row["fetch"]
    if fetched:
        assert row["source_kind"] == "fetched"
        assert fetch["status"] == "into_session"
        assert fetch["session_path"]
        assert "barro1991_growth" not in fetch["session_path"]
        assert "classic-5" not in fetch["session_path"]
        assert "not a barro" in row["design_fit"]["notes"].lower()
    else:
        assert row["source_kind"] == "external_link"
        assert fetch["status"] == "link_only"
        assert fetch["session_path"] is None
        assert fetch["reason"]
        notes = row["design_fit"]["notes"].lower()
        assert "upload" in notes
        assert "barro" in notes


def test_unconfirmed_design_refuses_fetch(tmp_path: Path):
    for design in (
        None,
        {},
        {"status": "missing"},
        {"status": "draft", "confirmed": False},
        _confirmed_growth(status="draft", confirmed=False, confirmed_at=None),
    ):
        with pytest.raises(DesignUnconfirmed):
            fetch_wdi(design, workspace=tmp_path / "workspace")
        staging = tmp_path / "workspace" / "fetch"
        assert not staging.exists() or not any(staging.iterdir())


def test_non_growth_design_is_not_wdi_fetch(tmp_path: Path):
    design = _confirmed_minwage()
    assert classify_route_family(design) == "minwage"
    with pytest.raises(WdiFetchNotApplicable):
        fetch_wdi(
            design,
            workspace=tmp_path / "workspace",
            http_get=_http_json(_wb_payload()),
        )
    assert not (tmp_path / "workspace" / "fetch").exists()


def test_growth_api_success_writes_session_csv_not_barro(tmp_path: Path):
    workspace = tmp_path / "workspace"
    barro = tmp_path / "barro1991_growth.csv"
    barro.write_text("growth,enrollment\n0.1,50\n", encoding="utf-8")
    classic = tmp_path / "fixtures" / "classic-5"
    classic.mkdir(parents=True)
    (classic / "barro1991_growth.csv").write_text(
        "growth,enrollment\n0.1,50\n", encoding="utf-8"
    )

    row = fetch_wdi(
        _confirmed_growth(),
        workspace=workspace,
        http_get=_http_json(_wb_payload()),
    )
    _assert_wdi_row(row, fetched=True)

    dest = workspace / "fetch" / f"wdi_{DEFAULT_INDICATOR}.csv"
    assert dest.is_file()
    text = dest.read_text(encoding="utf-8")
    assert DEFAULT_INDICATOR in text
    assert "United States" in text
    assert "2018" in text
    assert "enrollment" not in text
    assert dest.read_bytes() != barro.read_bytes()
    assert "barro1991_growth" not in row["fetch"]["session_path"]
    assert row["fetch"]["session_path"] == f"workspace/fetch/wdi_{DEFAULT_INDICATOR}.csv"


def test_http_error_is_honest_link_not_barro(tmp_path: Path):
    workspace = tmp_path / "workspace"
    (tmp_path / "barro1991_growth.csv").write_text("growth,enrollment\n")

    def _boom(_url: str) -> bytes:
        raise OSError("network down")

    row = fetch_wdi(_confirmed_growth(), workspace=workspace, http_get=_boom)
    _assert_wdi_row(row, fetched=False)
    assert row["fetch"]["reason"] == "http_error"
    assert row["url_or_fixture"].startswith("https://data.worldbank.org/indicator/")
    assert not (workspace / "fetch").exists() or not any(
        (workspace / "fetch").glob("*.csv")
    )


def test_html_landing_is_link_only(tmp_path: Path):
    html = b"<!doctype html><html><body>WDI</body></html>"

    def _get(_url: str) -> bytes:
        return html

    row = fetch_wdi(
        _confirmed_growth(),
        workspace=tmp_path / "workspace",
        http_get=_get,
    )
    _assert_wdi_row(row, fetched=False)
    assert row["fetch"]["reason"] == "html_landing"


def test_empty_json_is_link_only(tmp_path: Path):
    row = fetch_wdi(
        _confirmed_growth(),
        workspace=tmp_path / "workspace",
        http_get=_http_json(
            [{"page": 1, "pages": 1, "total": 0}, []]
        ),
    )
    _assert_wdi_row(row, fetched=False)
    assert row["fetch"]["reason"] == "empty_or_unparseable"


def test_null_values_only_is_link_only(tmp_path: Path):
    payload = _wb_payload(2)
    for item in payload[1]:
        item["value"] = None
    row = fetch_wdi(
        _confirmed_growth(),
        workspace=tmp_path / "workspace",
        http_get=_http_json(payload),
    )
    _assert_wdi_row(row, fetched=False)


def test_fetch_does_not_set_attach_or_did(tmp_path: Path):
    row = fetch_wdi(
        _confirmed_growth(),
        workspace=tmp_path / "workspace",
        http_get=_http_json(_wb_payload()),
    )
    blob = json.dumps(row)
    assert "dataAttached" not in blob
    assert "allow_did" not in blob
    assert "classic-5:barro1991_growth" not in blob
    assert row["source_kind"] != "teaching_fixture"
    assert row["source_kind"] != "discovered"

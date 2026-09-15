"""FD-BE-suggest: confirmed design → real data candidates (DECIDE-7 §9.1 bullets 1–2)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.find_data import is_real_candidate, search_dataverse, suggest_data_candidates
from agent.find_data import candidates as fd


def _confirmed(**overrides) -> dict:
    design = {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": "2026-09-15T12:05:00Z",
        "source": {
            "title": "最低工资对就业的影响",
            "question": "",
        },
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


def _write_found_scale_csv(path: Path, header: str = "employment,treated,period") -> None:
    lines = [header]
    for i in range(200):
        lines.append(f"{i % 17},1,{i % 2}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _silent_dataverse(_query: str) -> list:
    return []


def _hit_dataverse(query: str) -> list:
    return [
        {
            "name": f"Replication data ({query[:24]})",
            "global_id": "doi:10.7910/DVN/TEST01",
            "url": "https://doi.org/10.7910/DVN/TEST01",
            "license": "CC0 1.0",
            "type": "dataset",
        }
    ]


def _assert_real(items: list) -> None:
    assert items, "expected ≥1 real candidate"
    for item in items:
        assert is_real_candidate(item), item
        assert item["url_or_fixture"].strip()
        assert item["url_or_fixture"] not in {
            "ck1994",
            "ck1994_long",
            "minimum-wage-employment",
            "barro1991_growth",
            "schooling-wages",
        }
        assert "dataAttached" not in item
        assert "allow_did" not in item
        assert item.get("attached") is not True
        fit = item["design_fit"]
        assert "method" in fit
        assert "outcome" in fit
        assert "treatment" in fit


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
        items = suggest_data_candidates(
            design,
            dataverse_search=_hit_dataverse,
            catalog_dir=tmp_path,
        )
        assert items == [], design


def test_captain_local_real_is_first_class_acquire_not_found(tmp_path: Path):
    items = suggest_data_candidates(
        _confirmed(),
        dataverse_search=_silent_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    assert items[0]["source_id"] == "captain-local-real"
    local = items[0]
    assert local["acquire"] is True
    assert local["found"] is False
    assert local["teaching_fixture"] is False
    assert local["url_or_fixture"] == "/upload"
    assert local["license"] == "user-owned"
    assert "Desktop/经济学论文" in local["design_fit"]["notes"]
    assert "source=captain-local-real" in local["design_fit"]["notes"]
    assert "teaching toys" in local["design_fit"]["notes"]


def test_minwage_without_fixture_still_has_card_zip_and_dataverse(tmp_path: Path):
    items = suggest_data_candidates(
        _confirmed(),
        dataverse_search=_silent_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "card-zip:njmin" in ids
    assert any(sid.startswith("dataverse:") for sid in ids)
    assert not any(sid.startswith("classic-5:") for sid in ids)
    card = next(c for c in items if c["source_id"] == "card-zip:njmin")
    assert card["url_or_fixture"] == fd.CARD_ZIP_URL
    assert card["license"] == "author-posted"


def test_minwage_tiny_fixture_is_not_found(tmp_path: Path):
    (tmp_path / "ck1994_long.csv").write_text("employment,treated,period\n1,1,0\n")
    (tmp_path / "catalog.json").write_text(
        json.dumps(
            {
                "catalog_id": "classic-5",
                "entries": [
                    {
                        "id": "ck1994_long",
                        "title": "Card and Krueger minimum wage",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    items = suggest_data_candidates(
        _confirmed(),
        dataverse_search=_hit_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "classic-5:ck1994_long" not in ids
    assert "card-zip:njmin" in ids


def test_minwage_fixture_may_appear_but_is_not_the_only_candidate(tmp_path: Path):
    _write_found_scale_csv(tmp_path / "ck1994_long.csv")
    (tmp_path / "catalog.json").write_text(
        json.dumps(
            {
                "catalog_id": "classic-5",
                "entries": [
                    {
                        "id": "ck1994_long",
                        "title": "Card and Krueger minimum wage",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    items = suggest_data_candidates(
        _confirmed(),
        dataverse_search=_hit_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "classic-5:ck1994_long" in ids
    assert "card-zip:njmin" in ids
    assert "dataverse:doi:10.7910/DVN/TEST01" in ids
    fixture = next(c for c in items if c["source_id"] == "classic-5:ck1994_long")
    assert fixture["url_or_fixture"].endswith("ck1994_long.csv")
    assert fixture["license"] == "public-reproduction"
    assert fixture["found"] is True
    assert fixture["n_rows"] >= 200
    assert "employment" in fixture["suggested_cols"]
    assert "candidate only" in fixture["design_fit"]["notes"]


def test_catalog_id_without_file_is_not_a_candidate(tmp_path: Path):
    (tmp_path / "catalog.json").write_text(
        json.dumps(
            {
                "catalog_id": "classic-5",
                "entries": [{"id": "ck1994_long", "title": "Card and Krueger minimum wage"}],
            }
        ),
        encoding="utf-8",
    )
    items = suggest_data_candidates(
        _confirmed(),
        dataverse_search=_silent_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "classic-5:ck1994_long" not in ids
    assert "ck1994_long" not in ids
    assert "card-zip:njmin" in ids


def test_growth_route_lists_wdi_and_optional_barro(tmp_path: Path):
    design = _confirmed(
        method="ols",
        outcome="growth",
        treatment="",
        treated="",
        period="",
        qType="average",
        interactions=[],
        source={"title": "Barro growth: determinants of economic growth", "question": ""},
    )
    items = suggest_data_candidates(
        design,
        dataverse_search=_silent_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "wdi:NY.GDP.PCAP.KD.ZG" in ids
    assert any(sid.startswith("dataverse:") for sid in ids)
    assert "classic-5:barro1991_growth" not in ids

    (tmp_path / "barro1991_growth.csv").write_text("growth,enrollment\n0.01,0.1\n")
    with_barro = suggest_data_candidates(
        design,
        dataverse_search=_hit_dataverse,
        catalog_dir=tmp_path,
    )
    barro_ids = [c["source_id"] for c in with_barro]
    assert "classic-5:barro1991_growth" not in barro_ids
    assert "wdi:NY.GDP.PCAP.KD.ZG" in barro_ids

    _write_found_scale_csv(tmp_path / "barro1991_growth.csv", "growth,enrollment")
    found_barro = suggest_data_candidates(
        design,
        dataverse_search=_hit_dataverse,
        catalog_dir=tmp_path,
    )
    found_ids = [c["source_id"] for c in found_barro]
    assert "classic-5:barro1991_growth" in found_ids
    assert "wdi:NY.GDP.PCAP.KD.ZG" in found_ids


def test_educ_wage_route_lists_ipums(tmp_path: Path):
    design = _confirmed(
        method="ols",
        outcome="wages",
        treatment="schooling",
        treated="",
        period="",
        qType="average",
        interactions=[],
        source={"title": "教育对工资的影响", "question": ""},
    )
    (tmp_path / "wage1.csv").write_text("wage,educ\n1,12\n")
    items = suggest_data_candidates(
        design,
        dataverse_search=_silent_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "ipums:cps" in ids
    assert "wage1" not in ids
    assert any(sid.startswith("dataverse:") for sid in ids)
    ipums = next(c for c in items if c["source_id"] == "ipums:cps")
    assert ipums["license"] == "registration-required"


def test_macro_route_lists_fred(tmp_path: Path):
    design = _confirmed(
        method="ols",
        outcome="unemployment_rate",
        treatment="",
        treated="",
        period="",
        qType="average",
        interactions=[],
        source={"title": "FRED unemployment rate dynamics", "question": ""},
    )
    items = suggest_data_candidates(
        design,
        dataverse_search=_silent_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "fred:UNRATE" in ids
    assert any(sid.startswith("dataverse:") for sid in ids)


def test_else_route_requires_dataverse(tmp_path: Path):
    design = _confirmed(
        method="ols",
        outcome="happiness",
        treatment="sunshine",
        treated="",
        period="",
        qType="average",
        interactions=[],
        source={"title": "Does sunshine affect happiness?", "question": ""},
    )
    (tmp_path / "ck1994_long.csv").write_text("employment,treated,period\n")
    items = suggest_data_candidates(
        design,
        dataverse_search=_hit_dataverse,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "dataverse:doi:10.7910/DVN/TEST01" in ids
    assert "classic-5:ck1994_long" not in ids
    assert "card-zip:njmin" not in ids


def test_dataverse_failure_still_returns_external_path(tmp_path: Path):
    def _boom(_query: str):
        raise RuntimeError("network down")

    items = suggest_data_candidates(
        _confirmed(),
        dataverse_search=_boom,
        catalog_dir=tmp_path,
    )
    _assert_real(items)
    ids = [c["source_id"] for c in items]
    assert "card-zip:njmin" in ids
    assert any(sid.startswith("dataverse:") for sid in ids)


def test_is_real_candidate_rejects_id_only():
    assert not is_real_candidate("ck1994_long")
    assert not is_real_candidate({"entry_id": "ck1994_long"})
    assert not is_real_candidate(
        {
            "source_id": "classic-5:ck1994_long",
            "title": "Card and Krueger minimum wage",
            "url_or_fixture": "",
            "license": "public-reproduction",
            "suggested_cols": [],
            "design_fit": {"method": "did", "outcome": "employment", "treatment": "min_wage"},
        }
    )
    assert not is_real_candidate(
        {
            "source_id": "ck1994_long",
            "title": "Card and Krueger minimum wage",
            "url_or_fixture": "ck1994_long",
            "license": "public-reproduction",
            "suggested_cols": [],
            "design_fit": {"method": "did"},
        }
    )


def test_suggest_does_not_set_attach_or_did_unlock():
    items = suggest_data_candidates(
        _confirmed(),
        dataverse_search=_silent_dataverse,
        catalog_dir=Path("/no/such/classic-5"),
    )
    blob = json.dumps(items)
    assert "dataAttached" not in blob
    assert "allow_did" not in blob
    assert "catalog_entry_id" not in blob


def test_search_dataverse_maps_ok_payload():
    payload = {
        "status": "OK",
        "data": {
            "items": [
                {
                    "name": "NJ minwage files",
                    "type": "dataset",
                    "global_id": "doi:10.7910/DVN/ABC",
                    "url": "https://doi.org/10.7910/DVN/ABC",
                    "license": {"name": "CC BY 4.0"},
                }
            ]
        },
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(payload).encode("utf-8")
    mock_resp.__enter__ = lambda self: self
    mock_resp.__exit__ = lambda *args: None
    with patch("agent.find_data.candidates.urllib.request.urlopen", return_value=mock_resp):
        hits = search_dataverse("minimum wage employment")
    assert len(hits) == 1
    assert hits[0]["source_id"] == "dataverse:doi:10.7910/DVN/ABC"
    assert hits[0]["url_or_fixture"] == "https://doi.org/10.7910/DVN/ABC"
    assert hits[0]["license"] == "CC BY 4.0"


def test_search_dataverse_empty_or_error_is_empty():
    assert search_dataverse("") == []
    with patch(
        "agent.find_data.candidates.urllib.request.urlopen",
        side_effect=OSError("down"),
    ):
        assert search_dataverse("minimum wage") == []

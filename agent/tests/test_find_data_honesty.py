"""FD-BE-honesty: source_kind, teaching shelf, toy ban, fail-closed copy."""
from __future__ import annotations

from pathlib import Path

from agent.find_data.honesty import (
    CAPTAIN_LOCAL_REAL_SOURCE,
    N_DEMO_CLAIM_MIN,
    TEACHING_SHELF_LABEL,
    captain_local_real_candidate,
    demo_claim_allowed,
    demo_claim_warning,
    honest_candidate,
    is_banned_toy,
    is_find_success_candidate,
    is_real_candidate,
    project_honest_find_data,
)
from agent.find_data.plan import build_find_data_plan
from agent.tests.test_find_data_candidates import _confirmed
from agent.find_data import suggest_find_data


def _shape(**overrides) -> dict:
    item = {
        "source_id": "dataverse:doi:10.7910/DVN/TEST01",
        "source_kind": "discovered",
        "title": "Replication data",
        "url_or_fixture": "https://doi.org/10.7910/DVN/TEST01",
        "license": "CC0",
        "suggested_cols": [],
        "design_fit": {
            "method": "did",
            "outcome": "employment",
            "treatment": "min_wage",
            "notes": "检索到 / Dataverse 命中",
        },
    }
    item.update(overrides)
    return item


def test_banned_toys_by_name_and_path():
    assert is_banned_toy("minimum_wage.csv")
    assert is_banned_toy("frontend/public/samples/course-panel.csv")
    assert is_banned_toy("fixtures/cfps_association/sanitized_sample.csv")
    assert is_banned_toy("agent/spike/fixtures/minimum_wage.csv")
    assert not is_banned_toy("fixtures/classic-5/ck1994_long.csv")


def test_fixture_cannot_wear_discovered_or_fetched():
    fixture = _shape(
        source_id="classic-5:ck1994_long",
        source_kind="discovered",
        url_or_fixture="fixtures/classic-5/ck1994_long.csv",
        design_fit={
            "method": "did",
            "outcome": "employment",
            "treatment": "min_wage",
            "notes": "找到了 ck1994",
        },
    )
    assert honest_candidate(fixture) is None
    fixture["source_kind"] = "fetched"
    assert honest_candidate(fixture) is None
    fixture["source_kind"] = "captain_local_real"
    fixture["design_fit"] = {
        "method": "did",
        "outcome": "employment",
        "treatment": "min_wage",
        "notes": "captain-local-real acquire; not a find result; not a toy",
    }
    assert honest_candidate(fixture) is None


def test_teaching_fixture_is_real_but_not_find_success():
    item = _shape(
        source_id="classic-5:ck1994_long",
        source_kind="teaching_fixture",
        url_or_fixture="fixtures/classic-5/ck1994_long.csv",
        license="public-reproduction",
        design_fit={
            "method": "did",
            "outcome": "employment",
            "treatment": "min_wage",
            "notes": TEACHING_SHELF_LABEL,
        },
    )
    honest = honest_candidate(item)
    assert honest is not None
    assert is_real_candidate(honest)
    assert not is_find_success_candidate(honest)
    assert honest["fetch"]["status"] == "not_applicable"
    assert "找到了" not in honest["honesty_label"]
    assert "检索结果" not in honest["honesty_label"]


def test_missing_source_kind_fails_closed():
    item = _shape()
    item.pop("source_kind")
    assert not is_real_candidate(item)
    assert honest_candidate(item) is None


def test_toys_never_found_or_captain_local_real():
    for path in (
        "agent/spike/fixtures/minimum_wage.csv",
        "frontend/public/samples/course-panel.csv",
        "fixtures/cfps_association/sanitized_sample.csv",
    ):
        toy = _shape(
            source_id="toy:cfps",
            source_kind="discovered",
            title="CFPS sample",
            url_or_fixture=path,
        )
        assert honest_candidate(toy) is None
        assert (
            captain_local_real_candidate(
                path=path,
                design=_confirmed(),
            )
            is None
        )


def test_data_rigor_quarantine_is_skipped():
    item = _shape(quarantined=True)
    assert honest_candidate(item) is None
    item = _shape(data_rigor="quarantined")
    assert honest_candidate(item) is None


def test_captain_local_real_emits_source_and_is_not_find_success():
    item = captain_local_real_candidate(
        path="workspace/uploads/captain-local-real.dta",
        design=_confirmed(),
        session_path="workspace/uploads/captain-local-real.dta",
        row_count=3010,
    )
    assert item is not None
    assert item["source_kind"] == "captain_local_real"
    assert item["source"] == CAPTAIN_LOCAL_REAL_SOURCE
    assert not is_find_success_candidate(item)
    assert "找到了" not in item["honesty_label"]
    assert "discovered" not in item["honesty_label"]


def test_n_demo_claim_fail_closed():
    assert N_DEMO_CLAIM_MIN == 200
    assert demo_claim_allowed(None) is False
    assert demo_claim_allowed(24) is False
    assert demo_claim_allowed(199) is False
    assert demo_claim_allowed(200) is True
    assert "not a demo success" in demo_claim_warning(24)
    small = captain_local_real_candidate(
        path="workspace/uploads/panel.dta",
        design=_confirmed(),
        row_count=24,
    )
    assert small is not None
    assert "not a demo success" in small["design_fit"]["notes"]


def test_project_moves_fixture_out_of_find_list():
    record = {
        "status": "planned",
        "candidates": [
            _shape(
                source_id="classic-5:ck1994_long",
                url_or_fixture="fixtures/classic-5/ck1994_long.csv",
                license="public-reproduction",
            ),
            _shape(),
        ],
        "teaching_shelf": None,
    }
    projected = project_honest_find_data(record)
    ids = [c["source_id"] for c in projected["candidates"]]
    assert "classic-5:ck1994_long" not in ids
    assert "dataverse:doi:10.7910/DVN/TEST01" in ids
    shelf_ids = [c["source_id"] for c in projected["teaching_shelf"]["candidates"]]
    assert "classic-5:ck1994_long" in shelf_ids
    assert projected["teaching_shelf"]["label"] == TEACHING_SHELF_LABEL


def test_suggest_does_not_pad_empty_fetch_with_classic5(tmp_path: Path):
    (tmp_path / "ck1994_long.csv").write_text("employment,treated,period\n1,1,0\n")
    payload = suggest_find_data(
        _confirmed(),
        dataverse_search=lambda _q: [],
        catalog_dir=tmp_path,
    )
    ids = [c["source_id"] for c in payload["candidates"]]
    assert "classic-5:ck1994_long" not in ids
    assert "card-zip:njmin" in ids
    assert any(sid.startswith("dataverse:") for sid in ids)
    assert payload["teaching_shelf"] is not None
    assert "classic-5:ck1994_long" in [
        c["source_id"] for c in payload["teaching_shelf"]["candidates"]
    ]


def test_cfps_synthetic_not_on_shelf_or_find_list(tmp_path: Path):
    (tmp_path / "sanitized_sample.csv").write_text("a,b\n1,2\n")
    (tmp_path / "catalog.json").write_text(
        '{"catalog_id":"classic-5","entries":[{"id":"ck1994_long","title":"x"}]}',
        encoding="utf-8",
    )
    payload = suggest_find_data(
        _confirmed(),
        dataverse_search=lambda _q: [
            {
                "name": "CFPS sanitized",
                "global_id": "doi:10.7910/DVN/CFPS",
                "url": "fixtures/cfps_association/sanitized_sample.csv",
                "license": "CC0",
                "type": "dataset",
            }
        ],
        catalog_dir=tmp_path,
    )
    blob = str(payload)
    assert "sanitized_sample" not in blob
    assert all(c["source_kind"] != "discovered" or "cfps" not in c["url_or_fixture"].lower() for c in payload["candidates"])


def test_plan_copy_does_not_present_fixture_as_found():
    record = build_find_data_plan(_confirmed())
    dumped = str(record).lower()
    assert "找到了" not in dumped
    assert "discovered dataset" not in dumped
    assert "ck fixture" not in dumped
    assert "teaching-known" in record["plan"]["how"]
    assert record["primary_venue"] == "Card zip"

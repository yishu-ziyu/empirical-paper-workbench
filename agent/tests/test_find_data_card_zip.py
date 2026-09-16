"""FD-BE-fetch-card: confirmed minwage → author zip into session, else link+upload.

Synthetic zip/HTML bytes below are test doubles, not found data.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from agent.find_data import is_real_candidate
from agent.find_data.card_zip import (
    CARD_ZIP_LANDING_URL,
    CARD_ZIP_POSTED_URL,
    CARD_ZIP_SOURCE_ID,
    HONEST_UPLOAD_REASON,
    SESSION_RELATIVE_PATH,
    CardZipNotApplicable,
    fetch_card_zip,
    is_posted_zip,
    merge_card_zip_candidate,
    zip_urls_from_html,
)
from agent.find_data.plan import DesignUnconfirmed


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


def _synthetic_zip() -> bytes:
    """Labeled synthetic archive for tests/ only — not product found data."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("public.dat", "synthetic test double; not found data\n")
        archive.writestr("codebook", "synthetic test double\n")
    return buf.getvalue()


def _fixture_csv() -> bytes:
    return b"employment,treated,period\n1,1,0\n"


def _landing_html() -> bytes:
    return (
        b'<html><a href="readme/njmin-readme.txt">Readme</a> '
        b'for the associated <a href="data_sets/njmin.zip">data set</a></html>'
    )


def _assert_card_row(item: dict) -> None:
    assert is_real_candidate(item)
    assert item["source_id"] == CARD_ZIP_SOURCE_ID
    assert item["url_or_fixture"] == CARD_ZIP_LANDING_URL
    assert item["license"] == "author-posted"
    assert item["url_or_fixture"] not in {
        "ck1994",
        "ck1994_long",
        "minimum-wage-employment",
        "/demos/card",
    }
    assert "ck1994" not in item["source_id"]
    assert "dataAttached" not in item
    assert "allow_did" not in item
    fetch = item["fetch"]
    assert fetch["status"] in {"into_session", "link_only"}
    if fetch["status"] == "into_session":
        assert item["source_kind"] == "fetched"
        assert fetch["session_path"] == SESSION_RELATIVE_PATH
    else:
        assert item["source_kind"] == "external_link"
        assert fetch["session_path"] is None
        assert "honest upload" in fetch["reason"]


def test_unconfirmed_design_does_not_fetch(tmp_path: Path):
    zip_bytes = _synthetic_zip()

    def _read(_url: str) -> bytes:
        return zip_bytes

    for design in (
        None,
        {},
        {"status": "missing"},
        {"status": "draft", "confirmed": False, "source": {"title": "最低工资对就业的影响"}},
        _confirmed(status="draft", confirmed=False, confirmed_at=None),
    ):
        with pytest.raises(DesignUnconfirmed):
            fetch_card_zip(design, tmp_path, read_url=_read)
        assert list(tmp_path.rglob("*.zip")) == []


def test_non_minwage_confirmed_design_does_not_fetch(tmp_path: Path):
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

    def _read(_url: str) -> bytes:
        raise AssertionError("must not download Card zip for growth")

    with pytest.raises(CardZipNotApplicable, match="not_minwage"):
        fetch_card_zip(design, tmp_path, read_url=_read)
    assert list(tmp_path.rglob("*.zip")) == []


def test_retrievable_posted_zip_writes_into_session(tmp_path: Path):
    zip_bytes = _synthetic_zip()
    requested: list[str] = []

    def _read(url: str) -> bytes:
        requested.append(url)
        if url == CARD_ZIP_LANDING_URL:
            return _landing_html()
        if url == CARD_ZIP_POSTED_URL:
            return zip_bytes
        raise AssertionError(f"unexpected url {url}")

    item = fetch_card_zip(_confirmed(), tmp_path, read_url=_read)
    _assert_card_row(item)
    assert item["source_kind"] == "fetched"
    assert item["fetch"]["status"] == "into_session"
    written = tmp_path / SESSION_RELATIVE_PATH
    assert written.is_file()
    assert written.read_bytes() == zip_bytes
    assert is_posted_zip(written.read_bytes())
    assert written.read_bytes() != _fixture_csv()
    assert CARD_ZIP_POSTED_URL in requested
    assert "/demos/card" not in "".join(requested)
    assert "ck1994" not in str(written)
    assert "fixtures/classic-5" not in str(written)


def test_landing_html_resolves_njmin_zip_when_posted_url_fails(tmp_path: Path):
    zip_bytes = _synthetic_zip()
    resolved = "https://davidcard.berkeley.edu/njmin.zip"

    def _read(url: str) -> bytes:
        if url == CARD_ZIP_POSTED_URL:
            raise OSError("posted url down")
        if url == CARD_ZIP_LANDING_URL:
            return b'<html><a href="njmin.zip">data set</a></html>'
        if url == resolved:
            return zip_bytes
        raise OSError(url)

    item = fetch_card_zip(_confirmed(), tmp_path, read_url=_read)
    _assert_card_row(item)
    assert item["source_kind"] == "fetched"
    assert (tmp_path / SESSION_RELATIVE_PATH).read_bytes() == zip_bytes
    assert resolved in item["fetch"]["reason"]


def test_http_failure_is_link_plus_honest_upload(tmp_path: Path):
    def _read(_url: str) -> bytes:
        raise OSError("network down")

    item = fetch_card_zip(_confirmed(), tmp_path, read_url=_read)
    _assert_card_row(item)
    assert item["source_kind"] == "external_link"
    assert item["fetch"]["status"] == "link_only"
    assert item["url_or_fixture"] == CARD_ZIP_LANDING_URL
    assert HONEST_UPLOAD_REASON in item["fetch"]["reason"]
    assert list(tmp_path.rglob("*")) == []


def test_html_or_fixture_csv_is_not_a_fetch(tmp_path: Path):
    (tmp_path / "ck1994_long.csv").write_bytes(_fixture_csv())

    def _html(_url: str) -> bytes:
        return b"<html>data_sets</html>"

    html_item = fetch_card_zip(_confirmed(), tmp_path, read_url=_html)
    assert html_item["source_kind"] == "external_link"
    assert html_item["fetch"]["status"] == "link_only"
    assert not (tmp_path / SESSION_RELATIVE_PATH).exists()

    def _csv(_url: str) -> bytes:
        return _fixture_csv()

    csv_item = fetch_card_zip(_confirmed(), tmp_path / "ws", read_url=_csv)
    assert csv_item["source_kind"] == "external_link"
    assert csv_item["fetch"]["session_path"] is None
    ws = tmp_path / "ws"
    if ws.exists():
        assert list(ws.rglob("*.zip")) == []


def test_zip_urls_from_html_prefer_njmin():
    html = (
        '<a href="data_sets/proximity.zip">schooling</a>'
        '<a href="data_sets/njmin.zip">data set</a>'
    )
    urls = zip_urls_from_html(html, CARD_ZIP_LANDING_URL)
    assert urls == [CARD_ZIP_POSTED_URL]


def test_merge_puts_card_zip_first_without_fixture_padding():
    candidate = fetch_card_zip(
        _confirmed(),
        Path("/tmp/unused"),
        read_url=lambda _url: (_ for _ in ()).throw(OSError("down")),
    )
    record = merge_card_zip_candidate(
        {
            "status": "planned",
            "candidates": [
                {
                    "source_id": "classic-5:ck1994_long",
                    "title": "teaching",
                    "url_or_fixture": "fixtures/classic-5/ck1994_long.csv",
                    "license": "public-reproduction",
                    "suggested_cols": [],
                    "design_fit": {},
                }
            ],
        },
        candidate,
    )
    ids = [item["source_id"] for item in record["candidates"]]
    assert ids[0] == CARD_ZIP_SOURCE_ID
    assert ids.count(CARD_ZIP_SOURCE_ID) == 1
    assert record["candidates"][0]["source_kind"] == "external_link"


def test_fetch_return_is_not_attach_or_did_unlock(tmp_path: Path):
    item = fetch_card_zip(
        _confirmed(),
        tmp_path,
        read_url=lambda _url: _synthetic_zip(),
    )
    blob = str(item)
    assert "dataAttached" not in blob
    assert "allow_did" not in blob
    assert "/demos/card" not in blob
    assert item["source_id"] != "ck1994"
    assert item["source_id"] != "classic-5:ck1994_long"

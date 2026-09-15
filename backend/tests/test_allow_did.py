"""DID-BE-gate: title/catalog sets allow_did; method=did does not.

Pins docs/did-narrow-exception-contract.md §1. Default false. Only classic
Card–Krueger / minwage TITLE/TOPIC or catalog identity may set true.
"""
from __future__ import annotations

import asyncio
import json
import uuid

import pytest

from facade import facade
from runner import process_one_run
from services.allow_did import (
    MINWAGE_ENTRY_IDS,
    allow_did_for,
    catalog_identity_allows,
    session_allow_did,
    title_topic_allows,
)


def _key() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid.uuid4())}


def _create_session(client) -> str:
    resp = client.post("/sessions")
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


def _finish_upload_run(run_id: str) -> None:
    assert asyncio.run(process_one_run(owner="did-be-gate", run_id=run_id)) is True


def _write_entry(root, entry_id: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{entry_id}.csv").write_text("y,x\n1,0\n2,1\n", encoding="utf-8")


@pytest.mark.parametrize(
    "title,topic,expected",
    [
        ("Minimum wage and employment", "", True),
        ("最低工资对就业的影响", "", True),
        ("Card–Krueger 1994 New Jersey", "", True),
        ("Card and Krueger minimum wage", "", True),
        ("ck1994 replication", "", True),
        ("Education and wages", "", False),
        ("returns to schooling and earnings", "", False),
        ("Trade and local labor markets", "", False),
        ("I want difference-in-differences", "", False),
        ("panel TWFE event study", "", False),
        ("Card 1995 college proximity", "", False),
        ("", "", False),
    ],
)
def test_title_topic_matcher(title, topic, expected):
    assert title_topic_allows(title, topic) is expected
    assert allow_did_for(title=title, topic=topic, method="did") is expected


@pytest.mark.parametrize("entry_id", sorted(MINWAGE_ENTRY_IDS))
def test_known_catalog_tokens_allow(entry_id):
    assert allow_did_for(entry_id=entry_id, method="ols") is True


@pytest.mark.parametrize(
    "entry_id",
    [
        "schooling-wages",
        "trade-local-labor",
        "fiscal-output",
        "health-labor-supply",
        "barro1991_growth",
        "min-wage",
        "",
    ],
)
def test_other_catalog_tokens_deny(entry_id):
    assert allow_did_for(title="crime and policing", entry_id=entry_id, method="did") is False
    assert catalog_identity_allows(entry_id) is False


def test_method_is_never_the_setter():
    assert allow_did_for(title="crime", method="did") is False
    assert allow_did_for(title="crime", method="twfe") is False
    assert allow_did_for(title="crime", method="panel") is False
    assert allow_did_for(title="Minimum wage and employment", method="ols") is True


def test_new_session_projects_allow_did_false(client):
    sid = _create_session(client)
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["allow_did"] is False
    assert snap["dataAttached"] is False
    assert facade.get_state(sid).get("allow_did") is not True


def test_title_topic_minwage_sets_allow_did(client):
    sid = _create_session(client)
    resp = client.post(
        f"/sessions/{sid}/title-topic",
        json={"title": "最低工资对就业的影响", "topic": ""},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["allow_did"] is True
    assert resp.json()["dataAttached"] is False
    assert client.get(f"/sessions/{sid}").json()["allow_did"] is True
    state = facade.get_state(sid)
    assert state["allow_did"] is True
    assert state["title_topic"]["title"] == "最低工资对就业的影响"


def test_title_topic_schooling_stays_false(client):
    sid = _create_session(client)
    resp = client.post(
        f"/sessions/{sid}/title-topic",
        json={"title": "Education and wages", "topic": "returns to schooling"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["allow_did"] is False


def test_catalog_identity_without_bytes_sets_allow_did(client):
    sid = _create_session(client)
    resp = client.post(
        f"/sessions/{sid}/title-topic",
        json={"entry_id": "minimum-wage-employment"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["allow_did"] is True
    assert body["dataAttached"] is False
    assert body["has_dataset"] is False
    state = facade.get_state(sid)
    assert state["catalog_identity"]["entry_id"] == "minimum-wage-employment"
    assert "csv_path" not in state or not state.get("csv_path")


def test_ck1994_token_sets_allow_did(client):
    sid = _create_session(client)
    resp = client.post(f"/sessions/{sid}/title-topic", json={"entry_id": "ck1994"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["allow_did"] is True


def test_landed_ck1994_long_identity_sets_allow_did(client):
    sid = _create_session(client)
    resp = client.post(f"/sessions/{sid}/title-topic", json={"entry_id": "ck1994_long"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["allow_did"] is True
    assert resp.json()["dataAttached"] is False


def test_barro1991_growth_identity_stays_false(client):
    sid = _create_session(client)
    resp = client.post(
        f"/sessions/{sid}/title-topic",
        json={"title": "Barro cross-country growth", "entry_id": "barro1991_growth"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["allow_did"] is False


def test_schooling_catalog_identity_stays_false(client):
    sid = _create_session(client)
    resp = client.post(
        f"/sessions/{sid}/title-topic",
        json={"title": "Education and wages", "entry_id": "schooling-wages"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["allow_did"] is False


def test_direction_method_did_does_not_set_allow_did(client):
    sid = _create_session(client)
    facade.update_state(
        sid,
        research_direction={
            "question": "Does policing reduce crime?",
            "dv": "crime",
            "iv": "police",
            "method": "did",
        },
    )
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["allow_did"] is False
    assert snap["research_direction"]["method"] == "did"


def test_direction_question_minwage_sets_allow_did(client):
    sid = _create_session(client)
    facade.update_state(
        sid,
        research_direction={
            "question": "Minimum wage and employment in New Jersey",
            "dv": "emp",
            "iv": "treat",
            "method": "ols",
        },
    )
    assert client.get(f"/sessions/{sid}").json()["allow_did"] is True


def test_card_teaching_case_is_never_allow_did():
    state = {
        "research_lab": {"teaching_case": "card_1995"},
        "title_topic": {"title": "Minimum wage and employment", "topic": ""},
        "catalog_identity": {"catalog_id": "classic-5", "entry_id": "minimum-wage-employment"},
        "research_direction": {"method": "did", "question": "ck1994"},
    }
    assert session_allow_did(state) is False


def test_confirm_attach_does_not_set_allow_did(client, sample_csv_path):
    with open(sample_csv_path, "rb") as handle:
        accepted = client.post(
            "/upload",
            files={"file": ("sample.csv", handle, "text/csv")},
            headers=_key(),
        )
    sid = accepted.json()["session_id"]
    _finish_upload_run(accepted.json()["run_id"])
    assert client.get(f"/sessions/{sid}").json()["allow_did"] is False
    confirmed = client.post(f"/sessions/{sid}/confirm-attach")
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["dataAttached"] is True
    assert confirmed.json()["allow_did"] is False


def test_classic5_minwage_attach_sets_allow_did(client, tmp_path, monkeypatch):
    catalog = tmp_path / "classic-5"
    _write_entry(catalog, "minimum-wage-employment")
    _write_entry(catalog, "schooling-wages")
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(catalog))

    sid = _create_session(client)
    accepted = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "minimum-wage-employment"},
        headers=_key(),
    )
    assert accepted.status_code == 202, accepted.text
    assert accepted.json()["dataAttached"] is False
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["allow_did"] is True
    assert snap["dataAttached"] is False

    _finish_upload_run(accepted.json()["run_id"])
    assert client.post(f"/sessions/{sid}/confirm-attach").json()["dataAttached"] is True
    after = client.get(f"/sessions/{sid}").json()
    assert after["allow_did"] is True
    assert after["dataAttached"] is True

    rebound = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "schooling-wages"},
        headers=_key(),
    )
    assert rebound.status_code == 202, rebound.text
    assert client.get(f"/sessions/{sid}").json()["allow_did"] is False


def test_non_minwage_classic5_attach_stays_false(client, tmp_path, monkeypatch):
    catalog = tmp_path / "classic-5"
    _write_entry(catalog, "min-wage")
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(catalog))
    sid = _create_session(client)
    accepted = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "min-wage"},
        headers=_key(),
    )
    assert accepted.status_code == 202, accepted.text
    assert client.get(f"/sessions/{sid}").json()["allow_did"] is False


def test_suggest_does_not_write_allow_did(client):
    sid = _create_session(client)
    before = client.get(f"/sessions/{sid}").json()
    resp = client.post(
        "/classic-5/suggest",
        json={"title": "Minimum wage and employment", "topic": ""},
    )
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert "allow_did" not in payload
    after = client.get(f"/sessions/{sid}").json()
    assert after == before
    assert after["allow_did"] is False


def test_title_topic_rejects_empty(client):
    sid = _create_session(client)
    resp = client.post(f"/sessions/{sid}/title-topic", json={"title": "  ", "topic": ""})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "title or topic is required"


def test_title_topic_rejects_invalid_entry_id(client):
    sid = _create_session(client)
    resp = client.post(
        f"/sessions/{sid}/title-topic",
        json={"entry_id": "../card_1995"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "invalid_classic5_entry"


def test_soft_read_expected_tokens_only(tmp_path, monkeypatch):
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        json.dumps(
            {
                "catalog_id": "classic-5",
                "entries": [
                    {
                        "id": "ck1994_long",
                        "title": "Card and Krueger minimum wage",
                        "topic": "Min wage and employment",
                    },
                    {
                        "id": "barro1991_growth",
                        "title": "Barro cross-country growth",
                        "topic": "Growth and schooling",
                        "allow_did": True,
                    },
                    {
                        "id": "minimum-wage-employment",
                        "title": "Minimum wage and employment",
                        "allow_did": False,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ECONPAPER_CLASSIC5_CATALOG", str(catalog))
    assert catalog_identity_allows("ck1994_long") is True
    assert catalog_identity_allows("minimum-wage-employment") is False
    assert catalog_identity_allows("barro1991_growth") is False
    assert allow_did_for(entry_id="barro1991_growth", method="did") is False


def test_landed_ck1994_long_attach_sets_allow_did(client, tmp_path, monkeypatch):
    root = tmp_path / "classic-5"
    _write_entry(root, "ck1994_long")
    _write_entry(root, "barro1991_growth")
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(root))
    sid = _create_session(client)
    accepted = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "ck1994_long"},
        headers=_key(),
    )
    assert accepted.status_code == 202, accepted.text
    assert client.get(f"/sessions/{sid}").json()["allow_did"] is True
    _finish_upload_run(accepted.json()["run_id"])
    rebound = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "barro1991_growth"},
        headers=_key(),
    )
    assert rebound.status_code == 202, rebound.text
    assert client.get(f"/sessions/{sid}").json()["allow_did"] is False

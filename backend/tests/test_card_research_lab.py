"""M1 Card canonical research lab: demo boot, expectation, freeze, snapshot."""
from __future__ import annotations

import asyncio
import uuid

import pytest

from facade import facade
from models.run import Run
from run_repository import RunRepository
from services.research_lab import REQUIRED_CARD_COLUMNS


def _headers(key: str | None = None) -> dict[str, str]:
    return {"Idempotency-Key": key or str(uuid.uuid4())}


@pytest.fixture(autouse=True)
def _cleanup_card_sessions(client):
    from sqlalchemy import select
    from models.research_session import ResearchSession

    async def ids() -> set[str]:
        repo = RunRepository()
        async with repo._factory() as db:
            return set(await db.scalars(select(ResearchSession.session_id)))

    before = asyncio.run(ids())
    yield
    for session_id in asyncio.run(ids()) - before:
        facade.delete_session(session_id)


def _boot(client) -> dict:
    resp = client.post("/demos/card", headers=_headers())
    assert resp.status_code == 202, resp.text
    data = resp.json()
    assert data["session_id"]
    assert data["run_id"]
    assert data["events_url"] == f"/api/runs/{data['run_id']}/events"
    return data


def test_card_demo_boots_3010_rows_required_columns_and_provenance(client):
    data = _boot(client)
    sid = data["session_id"]
    snapshot = client.get(f"/sessions/{sid}").json()
    research = snapshot["research"]
    dataset = snapshot["dataset"]
    assert research["teaching_case"] == "card_1995"
    assert dataset["rows"] == 3010
    for col in REQUIRED_CARD_COLUMNS:
        assert col in dataset["columns"], col
    provenance = research["provenance"]
    assert provenance["citation"].startswith("Card, D. (1995)")
    assert provenance["checksum"]
    assert "StatsPAI" in provenance["redistribution"]
    assert provenance["extract_kind"] in {"wooldridge_card_34", "statspai_card_9"}
    assert provenance["source"]
    space = research["specification_space"]
    defs = space["definitions"]
    assert 6 <= len(defs) <= 12
    for item in defs:
        assert item["id"]
        assert item["label"]
        assert item["rationale"]
        assert item["dimension"]
        assert item["value"]
        assert isinstance(item["admissible"], bool)
        assert item["user_decision"]


def test_nine_col_path_marks_region_specs_unavailable(client, monkeypatch):
    monkeypatch.setenv("ECONPAPER_CARD_EXTRACT", "statspai_card_9")
    data = _boot(client)
    sid = data["session_id"]
    lab = client.get(f"/sessions/{sid}/research").json()
    assert lab["provenance"]["extract_kind"] == "statspai_card_9"
    by_id = {item["id"]: item for item in lab["specification_space"]["definitions"]}
    for spec_id in ("ols_region_dummies", "iv_region_dummies"):
        assert by_id[spec_id]["admissible"] is False
        assert by_id[spec_id]["user_decision"] == "unavailable"
        assert by_id[spec_id]["unavailable_reason"] == "missing_columns"
    assert by_id["iv_nearc4_linear"]["admissible"] is True


def test_expectation_put_round_trips_and_is_not_a_chat_message(client):
    sid = _boot(client)["session_id"]
    body = {
        "text": "OLS positive; IV may be smaller if ability biases upward.",
        "confidence": "high",
        "locale": "en",
    }
    put = client.put(f"/sessions/{sid}/research/expectation", json=body)
    assert put.status_code == 200, put.text
    lab = put.json()
    expect = lab["expectation"]
    assert expect["text"] == body["text"]
    assert expect["confidence"] == "high"
    assert expect["version"] == 2
    assert len(expect["history"]) >= 2
    snapshot = client.get(f"/sessions/{sid}").json()["research"]
    assert snapshot["expectation"]["text"] == body["text"]
    assert snapshot["expectation"]["confidence"] == "high"
    research = client.get(f"/sessions/{sid}/research").json()
    assert research["expectation"] == snapshot["expectation"]
    assert snapshot.get("claim") in (None, {})
    # Not a desk/chat transcript.
    state = facade.get_state(sid)
    assert "desk" not in (state.get("research_lab") or {})
    assert expect["history"][-1]["kind"] == "edit"


def test_freeze_persists_before_results(client):
    sid = _boot(client)["session_id"]
    frozen = client.post(f"/sessions/{sid}/research/specification-space/freeze")
    assert frozen.status_code == 200, frozen.text
    space = frozen.json()["specification_space"]
    assert space["frozen_at"]
    assert space["frozen_before_results"] is True
    assert space["status"] == "frozen"
    again = client.get(f"/sessions/{sid}").json()["research"]["specification_space"]
    assert again["frozen_at"] == space["frozen_at"]
    research = client.get(f"/sessions/{sid}/research").json()
    assert research["specification_space"]["frozen_at"] == space["frozen_at"]


def test_snapshot_research_matches_research_read_model(client):
    sid = _boot(client)["session_id"]
    snapshot = client.get(f"/sessions/{sid}").json()["research"]
    research = client.get(f"/sessions/{sid}/research").json()
    assert snapshot == research


def test_server_state_survives_without_client_storage(client):
    sid = _boot(client)["session_id"]
    client.put(
        f"/sessions/{sid}/research/expectation",
        json={"text": "Keep this on the server.", "confidence": "low"},
    )
    client.post(f"/sessions/{sid}/research/specification-space/freeze")
    later = client.get(f"/sessions/{sid}").json()["research"]
    assert later["expectation"]["text"] == "Keep this on the server."
    assert later["expectation"]["confidence"] == "low"
    assert later["specification_space"]["frozen_at"]
    assert later["teaching_case"] == "card_1995"


def test_research_lab_reattached_if_upload_drops_unknown_keys(client, monkeypatch):
    import runner as runner_mod

    def dropping(session_id, initial_state, **_kwargs):
        result = dict(initial_state)
        result.pop("research_lab", None)
        result["cleaning_report"] = {"steps": []}
        return result

    monkeypatch.setattr(runner_mod, "execute_upload_supervised", dropping)
    accepted = _boot(client)
    assert asyncio.run(
        runner_mod.process_one_run(
            owner="card-lab-reattach",
            run_id=accepted["run_id"],
        )
    )
    sid = accepted["session_id"]
    lab = facade.get_state(sid).get("research_lab") or {}
    assert lab.get("teaching_case") == "card_1995"

    async def stored_result() -> dict:
        repo = RunRepository()
        async with repo._factory() as db:
            run = await db.get(Run, accepted["run_id"])
            assert run is not None
            return dict(run.result or {})

    result = asyncio.run(stored_result())
    assert (result.get("research_lab") or {}).get("teaching_case") == "card_1995"

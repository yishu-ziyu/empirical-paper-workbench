"""DC-BE-attach: bind user file / classic-5; only confirm-attach sets dataAttached."""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

import pytest

from facade import facade
from run_repository import RunRepository
from runner import process_one_run


def _key() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid.uuid4())}


@pytest.fixture(autouse=True)
def _cleanup_attach_sessions(client):
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


def _create_session(client) -> str:
    resp = client.post("/sessions")
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


def _finish_upload_run(run_id: str) -> None:
    assert asyncio.run(process_one_run(owner="dc-be-attach", run_id=run_id)) is True


def _write_catalog(root: Path, entry_id: str = "min-wage") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{entry_id}.csv"
    path.write_text("wage,educ\n10,12\n20,16\n30,14\n", encoding="utf-8")
    return path


def test_upload_does_not_set_data_attached(client, sample_csv_path):
    with open(sample_csv_path, "rb") as handle:
        accepted = client.post(
            "/upload",
            files={"file": ("sample.csv", handle, "text/csv")},
            headers=_key(),
        )
    assert accepted.status_code == 202, accepted.text
    sid = accepted.json()["session_id"]
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["dataAttached"] is False
    assert snap["upload_readiness"] == "PROCESSING"

    _finish_upload_run(accepted.json()["run_id"])
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["upload_readiness"] == "READY"
    assert snap["has_dataset"] is True
    assert snap["dataset"]["columns"]
    assert snap["dataAttached"] is False

    confirmed = client.post(f"/sessions/{sid}/confirm-attach")
    assert confirmed.status_code == 200, confirmed.text
    body = confirmed.json()
    assert body["dataAttached"] is True
    assert body["upload_readiness"] == "READY"
    assert body["has_dataset"] is True
    assert client.get(f"/sessions/{sid}").json()["dataAttached"] is True


def test_selecting_user_file_candidate_does_not_set_data_attached(
    client, sample_csv_path
):
    with open(sample_csv_path, "rb") as handle:
        accepted = client.post(
            "/upload",
            files={"file": ("sample.csv", handle, "text/csv")},
            headers=_key(),
        )
    sid = accepted.json()["session_id"]
    _finish_upload_run(accepted.json()["run_id"])
    bound = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "user_file"},
    )
    assert bound.status_code == 200, bound.text
    assert bound.json()["dataAttached"] is False
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["dataAttached"] is False
    assert snap["upload_readiness"] == "READY"


def test_classic5_attach_then_confirm_sets_data_attached(client, tmp_path, monkeypatch):
    catalog = tmp_path / "classic-5"
    _write_catalog(catalog)
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(catalog))

    sid = _create_session(client)
    accepted = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "min-wage"},
        headers=_key(),
    )
    assert accepted.status_code == 202, accepted.text
    body = accepted.json()
    assert body["dataAttached"] is False
    assert body["source"] == "classic-5"
    assert body["entry_id"] == "min-wage"
    assert body["run_id"]
    assert body["events_url"] == f"/api/runs/{body['run_id']}/events"

    snap = client.get(f"/sessions/{sid}").json()
    assert snap["dataAttached"] is False
    assert snap["upload_readiness"] == "PROCESSING"
    assert snap.get("research") is None

    _finish_upload_run(body["run_id"])
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["upload_readiness"] == "READY"
    assert snap["has_dataset"] is True
    assert "wage" in snap["dataset"]["columns"]
    assert snap["dataAttached"] is False
    assert snap.get("research") is None

    confirmed = client.post(f"/sessions/{sid}/confirm-attach")
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["dataAttached"] is True
    assert confirmed.json()["upload_readiness"] == "READY"
    assert confirmed.json().get("research") is None
    state = facade.get_state(sid)
    assert state["data_attached"] is True
    assert state["attach_candidate"]["source"] == "classic-5"
    assert state["attach_candidate"]["entry_id"] == "min-wage"
    assert "teaching_case" not in state
    assert "research_lab" not in state


def test_classic5_env_entry_override(client, tmp_path, monkeypatch):
    csv = tmp_path / "from-env.csv"
    csv.write_text("y,x\n1,2\n3,4\n", encoding="utf-8")
    monkeypatch.setenv("ECONPAPER_CLASSIC5_WAGE_PANEL", str(csv))
    sid = _create_session(client)
    accepted = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "wage-panel"},
        headers=_key(),
    )
    assert accepted.status_code == 202, accepted.text
    _finish_upload_run(accepted.json()["run_id"])
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["dataAttached"] is False
    assert "y" in snap["dataset"]["columns"]
    assert client.post(f"/sessions/{sid}/confirm-attach").json()["dataAttached"] is True


def test_user_file_attach_to_existing_session(client):
    sid = _create_session(client)
    accepted = client.post(
        f"/sessions/{sid}/attach",
        data={"source": "user_file"},
        files={"file": ("own.csv", b"income,age\n100,30\n200,25\n", "text/csv")},
        headers=_key(),
    )
    assert accepted.status_code == 202, accepted.text
    assert accepted.json()["dataAttached"] is False
    assert accepted.json()["source"] == "user_file"
    _finish_upload_run(accepted.json()["run_id"])
    snap = client.get(f"/sessions/{sid}").json()
    assert snap["dataAttached"] is False
    assert snap["upload_readiness"] == "READY"
    assert "income" in snap["dataset"]["columns"]
    assert client.post(f"/sessions/{sid}/confirm-attach").json()["dataAttached"] is True


@pytest.mark.parametrize("readiness", ["PROCESSING", "FAILED", "CANCELLED"])
def test_confirm_attach_fails_closed_when_not_ready(client, tmp_path, readiness):
    csv = tmp_path / "ready.csv"
    csv.write_text("a\n1\n", encoding="utf-8")
    sid = f"confirm-closed-{readiness.lower()}-{uuid.uuid4().hex[:8]}"
    facade.seed_state(
        sid,
        {"csv_path": str(csv), "upload_readiness": readiness},
    )
    try:
        response = client.post(f"/sessions/{sid}/confirm-attach")
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "upload_not_ready"
        assert response.json()["detail"]["upload_readiness"] == readiness
        assert client.get(f"/sessions/{sid}").json()["dataAttached"] is False
    finally:
        facade.drop_session(sid)


def test_confirm_attach_fails_closed_without_readiness(client, tmp_path):
    csv = tmp_path / "legacy.csv"
    csv.write_text("a\n1\n", encoding="utf-8")
    sid = f"confirm-legacy-{uuid.uuid4().hex[:8]}"
    facade.seed_state(sid, {"csv_path": str(csv)})
    try:
        response = client.post(f"/sessions/{sid}/confirm-attach")
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "upload_not_ready"
        assert client.get(f"/sessions/{sid}").json()["dataAttached"] is False
    finally:
        facade.drop_session(sid)


def test_confirm_attach_no_candidate(client):
    sid = _create_session(client)
    response = client.post(f"/sessions/{sid}/confirm-attach")
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "no_candidate"
    assert client.get(f"/sessions/{sid}").json()["dataAttached"] is False


def test_confirm_attach_session_busy_while_ingest_in_flight(
    client, tmp_path, monkeypatch
):
    catalog = tmp_path / "classic-5"
    _write_catalog(catalog)
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(catalog))
    sid = _create_session(client)
    accepted = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "min-wage"},
        headers=_key(),
    )
    assert accepted.status_code == 202
    blocked = client.post(f"/sessions/{sid}/confirm-attach")
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["code"] in {"session_busy", "upload_not_ready"}
    assert client.get(f"/sessions/{sid}").json()["dataAttached"] is False


def test_second_attach_while_in_flight_is_session_busy(client, tmp_path, monkeypatch):
    catalog = tmp_path / "classic-5"
    _write_catalog(catalog, "min-wage")
    _write_catalog(catalog, "other")
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(catalog))
    sid = _create_session(client)
    first = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "min-wage"},
        headers=_key(),
    )
    assert first.status_code == 202
    second = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "other"},
        headers=_key(),
    )
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "session_busy"
    assert second.json()["detail"]["run_id"] == first.json()["run_id"]


def test_new_classic5_candidate_clears_data_attached(client, tmp_path, monkeypatch):
    catalog = tmp_path / "classic-5"
    _write_catalog(catalog, "min-wage")
    _write_catalog(catalog, "other")
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(catalog))
    sid = _create_session(client)
    first = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "min-wage"},
        headers=_key(),
    )
    _finish_upload_run(first.json()["run_id"])
    assert client.post(f"/sessions/{sid}/confirm-attach").json()["dataAttached"] is True

    rebound = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "other"},
        headers=_key(),
    )
    assert rebound.status_code == 202
    assert rebound.json()["dataAttached"] is False
    assert client.get(f"/sessions/{sid}").json()["dataAttached"] is False
    _finish_upload_run(rebound.json()["run_id"])
    assert client.get(f"/sessions/{sid}").json()["dataAttached"] is False
    assert client.post(f"/sessions/{sid}/confirm-attach").json()["dataAttached"] is True


def test_unknown_classic5_entry_is_rejected(client, tmp_path, monkeypatch):
    catalog = tmp_path / "empty-classic-5"
    catalog.mkdir()
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(catalog))
    sid = _create_session(client)
    response = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "missing"},
        headers=_key(),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "classic5_entry_not_found"


def test_classic5_rejects_path_traversal_entry(client):
    sid = _create_session(client)
    response = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "../card_1995"},
        headers=_key(),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid_classic5_entry"


def test_confirm_attach_is_idempotent_when_already_attached(client, sample_csv_path):
    with open(sample_csv_path, "rb") as handle:
        accepted = client.post(
            "/upload",
            files={"file": ("sample.csv", handle, "text/csv")},
            headers=_key(),
        )
    sid = accepted.json()["session_id"]
    _finish_upload_run(accepted.json()["run_id"])
    first = client.post(f"/sessions/{sid}/confirm-attach")
    second = client.post(f"/sessions/{sid}/confirm-attach")
    assert first.status_code == second.status_code == 200
    assert first.json()["dataAttached"] is True
    assert second.json()["dataAttached"] is True


def test_classic5_does_not_use_card_demo(client, tmp_path, monkeypatch):
    catalog = tmp_path / "classic-5"
    _write_catalog(catalog)
    monkeypatch.setenv("ECONPAPER_CLASSIC5_ROOT", str(catalog))
    monkeypatch.setenv("ECONPAPER_CARD_CSV", str(catalog / "min-wage.csv"))

    def should_not_boot(*_args, **_kwargs):
        raise AssertionError("classic-5 attach must not boot Card")

    monkeypatch.setattr("services.card_demo.admit_card_upload", should_not_boot)
    sid = _create_session(client)
    accepted = client.post(
        f"/sessions/{sid}/attach",
        json={"source": "classic-5", "entry_id": "min-wage"},
        headers=_key(),
    )
    assert accepted.status_code == 202, accepted.text
    _finish_upload_run(accepted.json()["run_id"])
    snap = client.get(f"/sessions/{sid}").json()
    assert snap.get("research") is None

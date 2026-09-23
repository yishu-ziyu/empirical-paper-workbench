"""DID-BE-spec: POST /direction refuses estimate when confirmed DiD lacks 2×2 term."""
from __future__ import annotations

import uuid

from facade import facade
from .confirmation_helpers import observed


def _key() -> dict[str, str]:
    return {"Idempotency-Key": str(uuid.uuid4())}


def _did_term(
    term: str = "treated:period",
    left: str = "treated",
    right: str = "period",
) -> dict[str, str]:
    return {"kind": "did", "left": left, "right": right, "term": term}


def _confirmed_did(
    *,
    interactions: list | None = None,
    method: str = "did",
    outcome: str = "emp",
    treatment: str = "treat",
) -> dict:
    return {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": "2026-09-15T13:00:00Z",
        "method": method,
        "outcome": outcome,
        "treatment": treatment,
        "treated": "treat",
        "period": "post",
        "interactions": [] if interactions is None else interactions,
        "catalog_entry_id": None,
    }


def _create_session(client) -> str:
    resp = client.post("/sessions")
    assert resp.status_code == 200, resp.text
    return resp.json()["session_id"]


def test_direction_refuses_confirmed_did_without_interaction(client, tmp_path):
    csv = tmp_path / "treat_only.csv"
    csv.write_text("emp,treat,id,year\n1,0,1,1992\n2,1,2,1992\n", encoding="utf-8")
    sid = _create_session(client)
    facade.update_state(
        sid,
        csv_path=str(csv),
        # Match the approved panel columns so this case specifically reaches
        # the missing-interaction gate, rather than the parameter-mismatch gate.
        design={**_confirmed_did(interactions=[]), "id_col": "id", "time_col": "year"},
        allow_did=True,
    )
    resp = client.post(
        f"/sessions/{sid}/direction",
        json={
            "question": "Minimum wage and employment",
            **observed(client, sid),
            "dv": "emp",
            "iv": "treat",
            "controls": [],
            "method": "did",
            "id_col": "id",
            "time_col": "year",
        },
        headers=_key(),
    )
    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "did_missing_interaction"
    assert facade.get_state(sid).get("estimate") is None


def test_direction_allows_confirmed_did_when_post_column_present(client, tmp_path):
    csv = tmp_path / "ck.csv"
    csv.write_text(
        "emp,treat,post\n1.0,0,0\n1.2,0,1\n2.0,1,0\n2.4,1,1\n",
        encoding="utf-8",
    )
    sid = _create_session(client)
    facade.update_state(
        sid,
        csv_path=str(csv),
        design=_confirmed_did(interactions=[_did_term("treat * post", "treat", "post")]),
    )
    resp = client.post(
        f"/sessions/{sid}/direction",
        json={
            "question": "Minimum wage and employment",
            **observed(client, sid),
            "dv": "emp",
            "iv": "treat",
            "controls": [],
            "method": "did",
        },
        headers=_key(),
    )
    assert resp.status_code == 202, resp.text
    assert "run_id" in resp.json()


def test_direction_allows_treat_post_dummy_in_payload(client):
    """The payload's treat_post dummy is the executed term; the confirmed
    design is the version it belongs to (CHAIN-2 R3)."""
    sid = _create_session(client)
    facade.update_state(
        sid, design=_confirmed_did(interactions=[], treatment="treat_post")
    )
    resp = client.post(
        f"/sessions/{sid}/direction",
        json={
            "question": "Card–Krueger 1994 New Jersey",
            **observed(client, sid),
            "dv": "emp",
            "iv": "treat_post",
            "controls": [],
            "method": "did",
        },
        headers=_key(),
    )
    assert resp.status_code == 202, resp.text


def test_direction_method_did_without_confirmed_design_still_enqueues(client, tmp_path):
    """Legacy boundary (CHAIN-2 R1): an explicitly legacy session without a
    design keeps KTD-era behavior. A session the new flow created is gated —
    see ``test_direction_formal_session_without_confirmed_design_is_refused``.
    """
    csv = tmp_path / "panel.csv"
    csv.write_text("y,treat,year,id\n1,0,2000,1\n", encoding="utf-8")
    sid = f"did-legacy-{uuid.uuid4().hex[:8]}"
    facade.seed_state(
        sid,
        {
            "session_kind": "legacy",
            "csv_path": str(csv),
            "allow_did": True,
            "catalog_identity": {"entry_id": "ck1994"},
            "title_topic": {"title": "最低工资对就业的影响", "topic": ""},
        },
    )
    try:
        resp = client.post(
            f"/sessions/{sid}/direction",
            json={
                "question": "Does policing reduce crime?",
                "dv": "y",
                "iv": "treat",
                "controls": [],
                "method": "did",
                "time_col": "year",
                "id_col": "id",
            },
            headers=_key(),
        )
        assert resp.status_code == 202, resp.text
    finally:
        facade.drop_session(sid)


def test_direction_formal_session_without_confirmed_design_is_refused(client, tmp_path):
    """CHAIN-2 R1: a formal session never executes a direction on the strength
    of a missing design."""
    csv = tmp_path / "panel.csv"
    csv.write_text("y,treat,year,id\n1,0,2000,1\n", encoding="utf-8")
    sid = _create_session(client)
    facade.update_state(sid, csv_path=str(csv), allow_did=True)
    import asyncio

    from run_repository import RunRepository

    resp = client.post(
        f"/sessions/{sid}/direction",
        json={
            "question": "Does policing reduce crime?",
            "dv": "y",
            "iv": "treat",
            "controls": [],
            "method": "did",
            "time_col": "year",
            "id_col": "id",
        },
        headers=_key(),
    )
    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"]["code"] == "design_unconfirmed"
    assert asyncio.run(RunRepository().active_run(sid)) is None


def test_direction_confirmed_ols_untouched(client, tmp_path):
    csv = tmp_path / "ols.csv"
    csv.write_text("y,x\n1,0\n2,1\n", encoding="utf-8")
    sid = _create_session(client)
    facade.update_state(
        sid,
        csv_path=str(csv),
        design=_confirmed_did(
            method="ols", interactions=[], outcome="y", treatment="x"
        ),
    )
    resp = client.post(
        f"/sessions/{sid}/direction",
        json={
            "question": "schooling and wages",
            **observed(client, sid),
            "dv": "y",
            "iv": "x",
            "controls": [],
            "method": "ols",
        },
        headers=_key(),
    )
    assert resp.status_code == 202, resp.text
    assert facade.get_state(sid).get("estimate") is None

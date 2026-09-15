"""DID-BE-gate recut: confirmed design.method=did + treated×period.

Catalog identity and TITLE/TOPIC are not unlock paths. Form method=did
is not the setter. DID-BE-spec owns force + 409; this file only pins the
gate booleans.
"""
from __future__ import annotations

import uuid

import pytest

from facade import facade
from services import allow_did as allow_did_mod
from services.allow_did import (
    confirmed_did_method,
    did_interaction_missing,
    has_treated_period_interaction,
    session_allow_did,
)


def _did_term(
    term: str = "treated:period",
    left: str = "treated",
    right: str = "period",
) -> dict[str, str]:
    return {"kind": "did", "left": left, "right": right, "term": term}


def _design(
    *,
    status: str = "confirmed",
    confirmed: bool = True,
    method: str = "did",
    interactions: list | None = None,
    **extra,
) -> dict:
    payload = {
        "status": status,
        "confirmed": confirmed,
        "proposed_at": "2026-09-15T12:00:00Z",
        "confirmed_at": "2026-09-15T13:00:00Z" if status == "confirmed" and confirmed else None,
        "source": {"title": "最低工资对就业的影响", "question": ""},
        "method": method,
        "outcome": "employment",
        "treatment": "min_wage",
        "treated": "treated",
        "period": "period",
        "interactions": [] if interactions is None else interactions,
        "catalog_entry_id": None,
    }
    payload.update(extra)
    return payload


def _snapshot(client, sid: str) -> dict:
    resp = client.get(f"/sessions/{sid}")
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_catalog_unlock_helpers_are_gone():
    assert not hasattr(allow_did_mod, "catalog_identity_allows")
    assert not hasattr(allow_did_mod, "MINWAGE_ENTRY_IDS")
    assert not hasattr(allow_did_mod, "title_topic_allows")
    assert not hasattr(allow_did_mod, "allow_did_for")


@pytest.mark.parametrize(
    "entry_id",
    ["ck1994", "ck1994_long", "minimum-wage-employment", "barro1991_growth"],
)
def test_catalog_id_alone_cannot_open_did(entry_id):
    state = {
        "catalog_identity": {"catalog_id": "classic-5", "entry_id": entry_id},
        "attach_candidate": {"source": "classic-5", "entry_id": entry_id},
        "allow_did": True,
        "title_topic": {"title": "最低工资对就业的影响", "topic": ""},
        "research_direction": {"method": "did", "question": "ck1994"},
    }
    assert session_allow_did(state) is False
    assert confirmed_did_method(state) is False


def test_title_topic_is_not_the_gate():
    state = {
        "title_topic": {
            "title": "Card–Krueger 1994 minimum wage",
            "topic": "最低工资对就业的影响",
        }
    }
    assert session_allow_did(state) is False
    assert confirmed_did_method(state) is False


def test_form_method_did_is_not_the_setter():
    state = {
        "research_direction": {
            "question": "Does policing reduce crime?",
            "method": "did",
        },
        "main_specification": {"method": "did", "formula": "y ~ treated:period"},
    }
    assert session_allow_did(state) is False
    assert confirmed_did_method(state) is False


def test_draft_design_cannot_open_did():
    state = {"design": _design(status="draft", confirmed=False, interactions=[_did_term()])}
    assert session_allow_did(state) is False
    assert confirmed_did_method(state) is False


def test_confirmed_ols_cannot_open_did():
    state = {
        "design": _design(method="ols", interactions=[_did_term()]),
        "catalog_identity": {"entry_id": "ck1994_long"},
    }
    assert session_allow_did(state) is False
    assert confirmed_did_method(state) is False


def test_confirmed_did_without_interaction_is_hook_not_permission():
    state = {"design": _design(interactions=[])}
    assert confirmed_did_method(state) is True
    assert did_interaction_missing(state) is True
    assert session_allow_did(state) is False


def test_id_col_time_col_is_not_the_interaction():
    state = {
        "design": _design(
            interactions=[],
            id_col="store",
            time_col="year",
            first_treat_col="first_treat",
        )
    }
    assert has_treated_period_interaction(state["design"]) is False
    assert confirmed_did_method(state) is True
    assert session_allow_did(state) is False


def test_het_interaction_is_not_did_permission():
    state = {
        "design": _design(
            interactions=[
                {"kind": "het", "left": "educ", "right": "region", "term": "educ:region"}
            ]
        )
    }
    assert session_allow_did(state) is False
    assert did_interaction_missing(state) is True


@pytest.mark.parametrize(
    "term,left,right",
    [
        ("treated:period", "treated", "period"),
        ("treat * post", "treat", "post"),
        ("treat × post", "treat", "post"),
        ("treat#post", "treat", "post"),
        ("treat_post", "treat", "post"),
        ("did", "treated", "period"),
    ],
)
def test_confirmed_did_with_main_term_allows(term, left, right):
    state = {"design": _design(interactions=[_did_term(term, left, right)])}
    assert session_allow_did(state) is True
    assert did_interaction_missing(state) is False


def test_constructed_dummy_alone_allows():
    state = {
        "design": _design(
            interactions=[{"kind": "did", "left": "", "right": "", "term": "treat_post"}]
        )
    }
    assert has_treated_period_interaction(state["design"]) is True
    assert session_allow_did(state) is True


def test_method_alias_difference_in_differences_counts():
    state = {
        "design": _design(
            method="difference-in-differences",
            interactions=[_did_term()],
        )
    }
    assert confirmed_did_method(state) is True
    assert session_allow_did(state) is True


def test_status_confirmed_mismatch_fails_closed():
    state = {"design": _design(status="confirmed", confirmed=False, interactions=[_did_term()])}
    assert session_allow_did(state) is False
    state = {"design": _design(status="draft", confirmed=True, interactions=[_did_term()])}
    assert session_allow_did(state) is False


def test_card_teaching_case_never_allows():
    state = {
        "research_lab": {"teaching_case": "card_1995"},
        "design": _design(interactions=[_did_term()]),
        "catalog_identity": {"entry_id": "ck1994"},
        "allow_did": True,
    }
    assert session_allow_did(state) is False
    assert confirmed_did_method(state) is False


def test_stamped_allow_did_without_confirmed_design_is_ignored():
    assert session_allow_did({"allow_did": True}) is False
    assert session_allow_did(None) is False
    assert session_allow_did({}) is False


def test_new_session_projects_allow_did_false(client):
    resp = client.post("/sessions")
    assert resp.status_code == 200, resp.text
    sid = resp.json()["session_id"]
    snap = _snapshot(client, sid)
    assert snap["allow_did"] is False
    assert facade.get_state(sid).get("allow_did") is not True


def test_snapshot_true_only_for_confirmed_did_with_term(client):
    sid = f"did-gate-{uuid.uuid4()}"
    facade.seed_state(sid, {"design": _design(interactions=[_did_term()])})
    assert _snapshot(client, sid)["allow_did"] is True


def test_snapshot_false_for_catalog_identity(client):
    sid = f"did-gate-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        {
            "catalog_identity": {"catalog_id": "classic-5", "entry_id": "ck1994"},
            "title_topic": {"title": "最低工资对就业的影响", "topic": ""},
            "allow_did": True,
        },
    )
    assert _snapshot(client, sid)["allow_did"] is False


def test_snapshot_false_when_confirmed_did_missing_term(client):
    sid = f"did-gate-{uuid.uuid4()}"
    facade.seed_state(sid, {"design": _design(interactions=[])})
    assert _snapshot(client, sid)["allow_did"] is False
    assert confirmed_did_method(facade.get_state(sid)) is True
    assert did_interaction_missing(facade.get_state(sid)) is True

"""Formal confirmation chain gates (FORMAL-CONFIRMATION-CHAIN-1, C4/C5 backend half).

Direct API calls must not skip the frozen business dependencies on the formal
path:

- confirm-attach (``dataAttached``) before direction / Table 1 / spec confirm /
  estimate (``docs/contracts/data-completion-contract.md`` §2 / §2a);
- a confirmed ``session.design`` before downstream gates treat the design as
  locked (``docs/contracts/infer-design-contract.md`` §5.2).

Boundary (frozen): sessions with an explicit ``upload_readiness`` or an explicit
``session_kind=formal`` are the new formal path; sessions without any explicit
marker are legacy (KTD7 keeps working); Card teaching sessions
(``research_lab.teaching_case``) are another product line and are not gated
here. New formal sessions never fall back to legacy by omission (R1): a
missing/null/malformed/draft design is refused, not waved through.
"""
from __future__ import annotations

import asyncio
import uuid

import pytest

from facade import facade
from .confirmation_helpers import observed
from run_repository import RunRepository


def _direction() -> dict:
    return {
        "question": "年龄与收入",
        "dv": "income",
        "iv": "age",
        "controls": [],
        "method": "OLS",
        "template": "cn_journal",
    }


def _sid(label: str) -> str:
    return f"fcc1-{label}-{uuid.uuid4().hex[:8]}"


def _seed(label: str, state: dict) -> str:
    sid = _sid(label)
    facade.seed_state(sid, {"csv_path": "/tmp/input.csv", **state})
    return sid


def _confirmed_design(method: str = "ols") -> dict:
    return {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-17T00:00:00Z",
        "confirmed_at": "2026-09-17T00:05:00Z",
        "source": {"title": "年龄与收入", "question": ""},
        "method": method,
        "outcome": "income",
        "treatment": "age",
        "controls": [],
        "interactions": [],
        "qType": "average",
        "heterogeneity_groups": [],
        "catalog_entry_id": None,
    }


def _draft_design() -> dict:
    design = _confirmed_design()
    design.update(
        {"status": "draft", "confirmed": False, "confirmed_at": None}
    )
    return design


@pytest.mark.parametrize("readiness", ["READY"])
def test_direction_rejects_upload_era_session_without_confirm_attach(
    client, readiness
):
    """READY means ingest-ready only; dataAttached still requires the human
    confirm-attach. 409 and no run may be enqueued."""
    sid = _seed("dir-no-attach", {"upload_readiness": readiness})
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "data_not_attached"
        import asyncio

        assert asyncio.run(RunRepository().active_run(sid)) is None
    finally:
        facade.drop_session(sid)


def test_direction_rejects_draft_design_on_formal_path(client):
    """A draft (unconfirmed) session.design must not unlock direction."""
    sid = _seed(
        "dir-draft-design",
        {
            "upload_readiness": "READY",
            "dataAttached": True,
            "data_attached": True,
            "design": _draft_design(),
        },
    )
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "design_unconfirmed"
    finally:
        facade.drop_session(sid)


def test_direction_allows_confirmed_design_with_attach(client):
    sid = _seed(
        "dir-ok",
        {
            "upload_readiness": "READY",
            "dataAttached": True,
            "data_attached": True,
            "design": _confirmed_design(),
        },
    )
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json={**_direction(), **observed(client, sid)},
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 202, response.text
    finally:
        facade.drop_session(sid)


def test_direction_legacy_session_without_readiness_still_allowed(client):
    """Legacy boundary: no explicit upload_readiness, no design → KTD-era
    behavior is unchanged (this batch must not narrow the legacy path)."""
    sid = _seed("dir-legacy", {})
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 202, response.text
    finally:
        facade.drop_session(sid)


def test_direction_card_teaching_session_not_gated(client):
    """Card 1995 is a separate product line; confirm-attach does not apply."""
    sid = _seed(
        "dir-card",
        {
            "upload_readiness": "READY",
            "research_lab": {"teaching_case": "card_1995"},
        },
    )
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 202, response.text
    finally:
        facade.drop_session(sid)


def test_prewrite_confirm_continue_rejects_unattached_formal_session(client):
    """Estimate must not run without dataAttached even with both flags set
    (fail closed; data-completion §2a rule 4)."""
    sid = _seed(
        "est-no-attach",
        {
            "upload_readiness": "READY",
            "research_direction": _direction(),
            "identification_diag": {"passed": True, "diagnostics": []},
            "table1Confirmed": True,
            "specConfirmed": True,
            "design": _confirmed_design(),
        },
    )
    try:
        response = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={
                "action": "continue_estimate",
                "table1Confirmed": True,
                "specConfirmed": True,
            },
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "data_not_attached"
    finally:
        facade.drop_session(sid)


def test_prewrite_confirm_record_rejects_unattached_formal_session(client):
    """PREWRITE-PAUSE flags must not become true without dataAttached."""
    sid = _seed(
        "rec-no-attach",
        {
            "upload_readiness": "READY",
            "research_direction": _direction(),
            "identification_diag": {"passed": True, "diagnostics": []},
        },
    )
    try:
        response = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": "record_confirms", "table1Confirmed": True},
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "data_not_attached"
        state = facade.get_state(sid)
        assert state.get("table1Confirmed") is not True
    finally:
        facade.drop_session(sid)


def test_prewrite_confirm_rejects_draft_design(client):
    sid = _seed(
        "est-draft-design",
        {
            "upload_readiness": "READY",
            "dataAttached": True,
            "data_attached": True,
            "research_direction": _direction(),
            "identification_diag": {"passed": True, "diagnostics": []},
            "table1Confirmed": True,
            "specConfirmed": True,
            "design": _draft_design(),
        },
    )
    try:
        response = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": "continue_estimate"},
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "design_unconfirmed"
    finally:
        facade.drop_session(sid)


# ---------------------------------------------------------------------------
# R1: the four missing-design shapes must not be inferred as legacy
# ---------------------------------------------------------------------------

_MISSING_DESIGN_SHAPES = ("missing", "null", "malformed", "draft")


def _with_design_shape(state: dict, shape: str) -> dict:
    if shape == "missing":
        return state
    if shape == "null":
        return {**state, "design": None}
    if shape == "malformed":
        # Truthy but not the locked shape: status set, confirmed not ``True``.
        return {**state, "design": {"status": "confirmed", "confirmed": "yes", "method": "ols"}}
    if shape == "draft":
        return {**state, "design": _draft_design()}
    raise AssertionError(f"unknown shape {shape}")


@pytest.mark.parametrize("shape", _MISSING_DESIGN_SHAPES)
def test_direction_rejects_formal_session_without_confirmed_design(client, shape):
    """R1: an explicitly formal session cannot reach direction by never
    proposing a design. All four missing shapes are refused and nothing is
    enqueued."""
    sid = _seed(
        f"dir-formal-{shape}",
        _with_design_shape(
            {
                "session_kind": "formal",
                "upload_readiness": "READY",
                "dataAttached": True,
                "data_attached": True,
            },
            shape,
        ),
    )
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "design_unconfirmed"
        assert asyncio.run(RunRepository().active_run(sid)) is None
    finally:
        facade.drop_session(sid)


@pytest.mark.parametrize("shape", _MISSING_DESIGN_SHAPES)
@pytest.mark.parametrize("action", ["record_confirms", "continue_estimate"])
def test_prewrite_confirm_rejects_formal_session_without_confirmed_design(
    client, shape, action
):
    """R1: the same four shapes are refused on both confirm actions, even when
    both FE flags are already set and an estimate run would be admitted."""
    sid = _seed(
        f"est-formal-{shape}-{action}",
        _with_design_shape(
            {
                "session_kind": "formal",
                "upload_readiness": "READY",
                "dataAttached": True,
                "data_attached": True,
                "research_direction": _direction(),
                "identification_diag": {"passed": True, "diagnostics": []},
                "table1Confirmed": True,
                "specConfirmed": True,
            },
            shape,
        ),
    )
    try:
        response = client.post(
            f"/sessions/{sid}/prewrite/confirm",
            json={"action": action, "table1Confirmed": True, "specConfirmed": True},
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "design_unconfirmed"
        assert asyncio.run(RunRepository().active_run(sid)) is None
    finally:
        facade.drop_session(sid)


def test_new_session_from_sessions_endpoint_is_formal_and_gated(client):
    """R1 root cause: a brand-new formal session that never proposed a design
    used to be admitted (202). The session's category is now an explicit
    marker, so omission can no longer mean legacy."""
    sid = client.post("/sessions").json()["session_id"]
    try:
        assert facade.get_state(sid).get("session_kind") == "formal"
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "design_unconfirmed"
    finally:
        facade.drop_session(sid)


def test_bare_legacy_session_with_null_design_still_allowed(client):
    """Legacy boundary: no category marker, no upload era, no design object."""
    sid = _seed("dir-legacy-null-design", {"design": None})
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 202, response.text
    finally:
        facade.drop_session(sid)


@pytest.mark.parametrize(
    "state",
    [
        # Legacy marker wins over the missing design.
        {"session_kind": "legacy", "design": None},
        # Card teaching, by explicit category.
        {"session_kind": "card_teaching", "design": None},
        # Card teaching, by research_lab marker (unchanged rule).
        {"research_lab": {"teaching_case": "card_1995"}, "design": None},
    ],
)
def test_non_formal_sessions_are_not_design_gated(client, state):
    """Boundary: legacy and Card teaching sessions keep their own path."""
    sid = _seed(f"dir-boundary-{uuid.uuid4().hex[:6]}", state)
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert response.status_code == 202, response.text
    finally:
        facade.drop_session(sid)


def test_data_access_and_structure_checks_are_not_design_gated(client, tmp_path):
    """The design gate covers formal execution, not looking at data: a formal
    session with no design can still attach a file and run structural checks."""
    csv = tmp_path / "structural.csv"
    csv.write_text("income,age\n1,20\n2,30\n", encoding="utf-8")
    sid = client.post("/sessions").json()["session_id"]
    try:
        attached = client.post(
            f"/sessions/{sid}/attach",
            data={"source": "user_file"},
            files={"file": ("structural.csv", csv.read_bytes(), "text/csv")},
            headers={"Idempotency-Key": str(uuid.uuid4())},
        )
        assert attached.status_code == 202, attached.text

        import asyncio
        from runner import process_one_run
        from .confirmation_helpers import confirm_seen_attach
        assert asyncio.run(process_one_run(owner="structure-test", run_id=attached.json()["run_id"]))
        assert confirm_seen_attach(client, sid).status_code == 200
        describe = client.post(
            f"/sessions/{sid}/eda",
            json={"action": "describe"},
        )
        assert describe.status_code == 200, describe.text

        # The same session still cannot execute a formal analysis.
        blocked = client.post(
            f"/sessions/{sid}/direction",
            json=_direction(),
            headers={"Idempotency-Key": f"{sid}-key"},
        )
        assert blocked.status_code == 409, blocked.text
        assert blocked.json()["detail"]["code"] == "design_unconfirmed"
    finally:
        facade.drop_session(sid)

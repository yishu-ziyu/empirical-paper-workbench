"""Formal confirmation chain version binding (CHAIN-2 R2/R3/R6 + idempotency).

An approval must name the objects it approved. These tests pin, from the
server side only (direct API calls, no front-end button state):

- R2: a confirm is bound to the preview actually on the screen (real Table 1
  and equation), no conflicting active run, sample before setting;
- R3: a design revision / dataset revision / preview identity binds confirms
  and runs, atomic changes revoke the affected approvals while keeping
  history, and the executed direction must match the approved version;
- R6: the #40 tri-state permission (allow / confirm / forbid) is consumed by
  the estimate entry, and a ``confirm`` permission needs a risk decision bound
  to the diagnosis and the design;
- idempotency: replaying one intention with the same Idempotency-Key returns
  the same result and never writes a second run or a second confirmation.

Legacy sessions (no explicit category marker) keep their own path and are not
bound by these rules; see ``test_formal_chain_gates.py``.
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

import pytest

from agent.engine.prewrite_preview import build_prewrite_preview
from facade import facade
from .confirmation_helpers import observed, confirm_seen_design
from models.run import Run
from run_repository import RunRepository
from sqlalchemy import select


CSV_TEXT = "income,age\n1,20\n2,30\n3,40\n"

_PASS_DIAG = {
    "passed": True,
    "diagnostics": [{"name": "ols_sanity", "status": "pass"}],
}
# ``fail`` without ``star_rating == 0``: #40 asks the user to decide (confirm),
# it does not hard-block the flow.
_RISK_DIAG = {
    "passed": False,
    "star_rating": 1,
    "diagnostics": [
        {"name": "ols_sanity", "status": "pass"},
        {"name": "pre_trend", "status": "fail"},
    ],
}
# Nothing could be assessed: unknown is neither pass nor forbid.
_UNKNOWN_DIAG = {
    "passed": None,
    "diagnostics": [{"name": "did_parallel_trends", "status": "skipped"}],
}


def _sid(label: str) -> str:
    return f"fcc2-{label}-{uuid.uuid4().hex[:8]}"


def _design(
    *,
    method: str = "ols",
    outcome: str = "income",
    treatment: str = "age",
    controls: list[str] | None = None,
    **extra,
) -> dict:
    design = {
        "status": "confirmed",
        "confirmed": True,
        "proposed_at": "2026-09-17T00:00:00Z",
        "confirmed_at": "2026-09-17T00:05:00Z",
        "source": {"title": "年龄与收入", "question": ""},
        "method": method,
        "outcome": outcome,
        "treatment": treatment,
        "controls": list(controls or []),
        "interactions": [],
        "qType": "average",
        "heterogeneity_groups": [],
        "catalog_entry_id": None,
    }
    design.update(extra)
    return design


def _direction(
    *,
    dv: str = "income",
    iv: str = "age",
    method: str = "OLS",
    controls: list[str] | None = None,
    **extra,
) -> dict:
    return {
        "question": "年龄与收入",
        "dv": dv,
        "iv": iv,
        "controls": list(controls or []),
        "method": method,
        "template": "cn_journal",
        **extra,
    }


def _main_spec(
    *,
    outcome: str = "income",
    treatment: str = "age",
    method: str = "ols",
    controls: list[str] | None = None,
) -> dict:
    return {
        "method": method,
        "outcome": outcome,
        "treatment": treatment,
        "controls": list(controls or []),
        "formula": f"{outcome} ~ {treatment}",
        "produced_by": "set_direction",
    }


def _formal_state(
    tmp_path: Path,
    *,
    design: dict | None = None,
    direction: dict | None = None,
    diag: dict | None = None,
    star: int | None = 3,
    main_spec: dict | None = None,
    with_preview: bool = True,
    csv_text: str = CSV_TEXT,
    **extra,
) -> dict:
    csv = tmp_path / "sample.csv"
    csv.write_text(csv_text, encoding="utf-8")
    state = {
        "session_kind": "formal",
        "csv_path": str(csv),
        "upload_readiness": "READY",
        "dataAttached": True,
        "data_attached": True,
        "design": design if design is not None else _design(),
        "research_direction": direction if direction is not None else _direction(),
        "main_specification": main_spec if main_spec is not None else _main_spec(),
        "identification_diag": diag if diag is not None else dict(_PASS_DIAG),
        "star_rating": star,
        **extra,
    }
    if with_preview:
        state.update(build_prewrite_preview(state))
    return state


def _seed(label: str, state: dict) -> str:
    sid = _sid(label)
    facade.seed_state(sid, state)
    return sid


def _chain(state: dict) -> dict:
    block = state.get("formal_chain")
    return block if isinstance(block, dict) else {}


def _confirmations(state: dict) -> dict:
    records = _chain(state).get("confirmations")
    return records if isinstance(records, dict) else {}


def _post(client, sid: str, body: dict, key: str):
    return client.post(
        f"/sessions/{sid}/prewrite/confirm",
        json={**observed(client, sid), **body},
        headers={"Idempotency-Key": key},
    )


def _bind_confirm_attached(sid: str) -> None:
    facade.update_state(sid, dataAttached=True, data_attached=True)


def _active_run(sid: str):
    return asyncio.run(RunRepository().active_run(sid))


# ---------------------------------------------------------------------------
# R2: confirms must name the preview they were given
# ---------------------------------------------------------------------------


def test_record_sample_rejects_session_without_preview(client, tmp_path):
    """No generated preview (no Table 1 / equation) → no confirmation, no flag."""
    sid = _seed(
        "rec-no-preview",
        _formal_state(tmp_path, with_preview=False),
    )
    try:
        response = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "preview_not_ready"
        state = facade.get_state(sid)
        assert state.get("table1Confirmed") is not True
        assert _confirmations(state) == {}
    finally:
        facade.drop_session(sid)


def test_record_setting_rejects_before_sample_confirmed(client, tmp_path):
    """Sample (Table 1) confirmation comes first; setting cannot jump ahead."""
    sid = _seed("rec-order", _formal_state(tmp_path))
    try:
        response = _post(
            client, sid, {"action": "record_confirms", "specConfirmed": True}, "k1"
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "sample_confirmation_required"
        state = facade.get_state(sid)
        assert state.get("specConfirmed") is not True
        assert "spec" not in _confirmations(state)
    finally:
        facade.drop_session(sid)


def test_record_confirms_rejects_while_a_run_is_active(client, tmp_path):
    """A conflicting in-flight run refuses the confirmation (no parallel write)."""
    sid = _seed("rec-busy", _formal_state(tmp_path))
    try:
        asyncio.run(
            RunRepository().enqueue(
                session_id=sid,
                kind="prewrite",
                payload={"research_direction": _direction(), "initial_state": {}},
                idempotency_key=None,
            )
        )
        response = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "session_busy"
        assert facade.get_state(sid).get("table1Confirmed") is not True
    finally:
        facade.drop_session(sid)


def test_sample_then_setting_records_bound_confirmations(client, tmp_path):
    """The real two-step flow: both confirms bind the same preview identity."""
    sid = _seed("rec-ok", _formal_state(tmp_path))
    try:
        table1 = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
        )
        assert table1.status_code == 200, table1.text
        assert table1.json()["table1Confirmed"] is True
        assert table1.json()["table1"]

        spec = _post(
            client, sid, {"action": "record_confirms", "specConfirmed": True}, "k2"
        )
        assert spec.status_code == 200, spec.text
        assert spec.json()["specConfirmed"] is True

        state = facade.get_state(sid)
        records = _confirmations(state)
        assert records["sample"]["preview"]
        assert records["sample"]["preview"] == records["spec"]["preview"]
        assert records["sample"]["design"] == records["spec"]["design"]

        accepted = _post(client, sid, {"action": "continue_estimate"}, "k3")
        assert accepted.status_code == 202, accepted.text
    finally:
        facade.drop_session(sid)


def test_continue_estimate_rejects_unbound_legacy_flags(client, tmp_path):
    """Flags without a version-bound record never start the estimate: an old
    preview's ``table1Confirmed/specConfirmed`` must not survive as approval."""
    state = _formal_state(tmp_path)
    state.update({"table1Confirmed": True, "specConfirmed": True})
    sid = _seed("rec-unbound-flags", state)
    try:
        response = _post(client, sid, {"action": "continue_estimate"}, "k1")
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "confirmations_stale"
        assert _active_run(sid) is None
    finally:
        facade.drop_session(sid)


def test_setting_confirm_rejected_when_sample_confirmation_went_stale(client, tmp_path):
    """After the preview moves, the earlier sample confirmation no longer
    counts, so the setting confirmation is refused."""
    sid = _seed("rec-preview-moved", _formal_state(tmp_path))
    try:
        first = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
        )
        assert first.status_code == 200, first.text

        # A new preview is generated for the same session (the data moved).
        moved = _formal_state(tmp_path, csv_text=CSV_TEXT + "4,50\n")
        facade.update_state(
            sid,
            table1=moved["table1"],
            specification_equation=moved["specification_equation"],
            main_specification=moved["main_specification"],
            blocking_decision=moved["blocking_decision"],
        )

        response = _post(
            client, sid, {"action": "record_confirms", "specConfirmed": True}, "k2"
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] in {
            "confirmations_stale",
            "sample_confirmation_required",
        }
        assert facade.get_state(sid).get("specConfirmed") is not True
    finally:
        facade.drop_session(sid)


# ---------------------------------------------------------------------------
# R3: design / dataset / preview revisions bind confirms and runs
# ---------------------------------------------------------------------------


def test_direction_rejects_content_that_differs_from_confirmed_design(client, tmp_path):
    """Locked treatment=age cannot be executed as schooling."""
    sid = _seed("dir-mismatch", _formal_state(tmp_path))
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json={**_direction(iv="schooling"), **observed(client, sid)},
            headers={"Idempotency-Key": "k1"},
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "design_execution_mismatch"
        assert response.json()["detail"]["field"] == "iv"
        assert _active_run(sid) is None
    finally:
        facade.drop_session(sid)


def test_direction_executes_the_confirmed_design_content(client, tmp_path):
    """The approved version is what runs: the payload is aligned to it."""
    sid = _seed("dir-aligned", _formal_state(tmp_path))
    try:
        response = client.post(
            f"/sessions/{sid}/direction",
            json={**_direction(), **observed(client, sid)},
            headers={"Idempotency-Key": "k1"},
        )
        assert response.status_code == 202, response.text
        run = asyncio.run(RunRepository().get(response.json()["run_id"]))
        assert run is not None
        payload = dict(run.payload or {})
        assert payload["research_direction"]["iv"] == "age"
        assert payload["research_direction"]["dv"] == "income"
        assert payload["binding"]["design"]
    finally:
        facade.drop_session(sid)


def test_reproposed_design_revokes_old_confirmation_and_preview(client, tmp_path):
    """Re-proposing a design must not keep the previous approval, preview or
    direction projection; the archived version stays readable in history."""
    sid = _seed("design-repropose", _formal_state(tmp_path))
    try:
        recorded = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
        )
        assert recorded.status_code == 200, recorded.text
        before = facade.get_state(sid)
        assert before.get("table1") and before.get("table1Confirmed") is True

        proposed = client.post(
            f"/sessions/{sid}/design/propose",
            json={"title": "教育年限对工资的影响", "question": ""},
        )
        assert proposed.status_code == 200, proposed.text

        after = facade.get_state(sid)
        assert after["design"]["status"] == "draft"
        assert after.get("table1") is None
        assert after.get("specification_equation") is None
        assert after.get("prewrite_gate") is None
        assert after.get("table1Confirmed") is False
        assert after.get("specConfirmed") is False
        assert after.get("research_direction") is None
        assert after.get("main_specification") is None
        assert _confirmations(after) == {}
        history = _chain(after).get("history") or []
        assert any(entry.get("kind") == "design_superseded" for entry in history)
        archived = [
            entry for entry in history if entry.get("kind") == "design_superseded"
        ][-1]
        assert archived.get("design", {}).get("treatment") == "age"
        assert archived.get("table1")
    finally:
        facade.drop_session(sid)


def test_old_direction_refused_after_design_reproposed_as_schooling(client, tmp_path):
    """The reviewer's counterexample: re-propose as schooling, confirm it, then
    try to start with the previous age direction."""
    sid = _seed("design-swap", _formal_state(tmp_path))
    try:
        proposed = client.post(
            f"/sessions/{sid}/design/propose",
            json={"title": "教育年限对工资的影响", "question": ""},
        )
        assert proposed.status_code == 200, proposed.text
        facade.update_state(
            sid,
            design={
                **proposed.json(),
                "method": "ols",
                "outcome": "income",
                "treatment": "schooling",
            },
        )
        confirmed = confirm_seen_design(client, sid)
        assert confirmed.status_code == 200, confirmed.text
        assert confirmed.json()["design"]["treatment"] == "schooling"

        stale = client.post(
            f"/sessions/{sid}/direction",
            json={**_direction(iv="age"), **observed(client, sid)},
            headers={"Idempotency-Key": "k1"},
        )
        assert stale.status_code == 409, stale.text
        assert stale.json()["detail"]["code"] == "design_execution_mismatch"

        fresh = client.post(
            f"/sessions/{sid}/direction",
            json={**_direction(iv="schooling"), **observed(client, sid)},
            headers={"Idempotency-Key": "k2"},
        )
        assert fresh.status_code == 202, fresh.text
    finally:
        facade.drop_session(sid)


def test_wording_change_keeps_the_approved_version(client, tmp_path):
    """Display wording is not a research change: the same executable projection
    keeps its approvals."""
    sid = _seed("wording", _formal_state(tmp_path))
    try:
        assert (
            _post(
                client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
            ).status_code
            == 200
        )
        assert (
            _post(
                client, sid, {"action": "record_confirms", "specConfirmed": True}, "k2"
            ).status_code
            == 200
        )
        records_before = dict(_confirmations(facade.get_state(sid)))

        design = facade.get_state(sid)["design"]
        facade.update_state(
            sid,
            design={
                **design,
                "source": {"title": "年龄与收入（草稿标题）", "question": "工资随年龄变化吗"},
            },
        )

        records_after = dict(_confirmations(facade.get_state(sid)))
        assert records_after == records_before

        accepted = _post(client, sid, {"action": "continue_estimate"}, "k3")
        assert accepted.status_code == 202, accepted.text
    finally:
        facade.drop_session(sid)


def test_continue_estimate_refused_after_design_changes(client, tmp_path):
    """Confirms made for design A do not start an estimate for design B."""
    sid = _seed("design-stale-confirms", _formal_state(tmp_path))
    try:
        assert (
            _post(
                client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
            ).status_code
            == 200
        )
        assert (
            _post(
                client, sid, {"action": "record_confirms", "specConfirmed": True}, "k2"
            ).status_code
            == 200
        )
        facade.update_state(
            sid, design={**_design(treatment="schooling"), "confirmed_at": "2026-09-17T01:00:00Z"}
        )
        response = _post(client, sid, {"action": "continue_estimate"}, "k3")
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "confirmations_stale"
        assert _active_run(sid) is None
    finally:
        facade.drop_session(sid)


def test_dataset_change_clears_old_preview_and_approvals(client, tmp_path):
    """Changing the bound data must not leave the previous Table 1, the two
    true flags or ``awaiting_estimate`` behind."""
    sid = _seed("dataset-swap", _formal_state(tmp_path))
    try:
        recorded = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
        )
        assert recorded.status_code == 200, recorded.text
        before = facade.get_state(sid)
        assert before.get("table1")
        assert before.get("prewrite_gate") == "awaiting_estimate"

        admission = asyncio.run(
            RunRepository().admit_session_upload(
                session_id=sid,
                user_id=None,
                csv_path=str(tmp_path / "sample.csv"),
                dataset_meta={"columns": ["income", "age"], "rows": 3},
                extra_state={},
                idempotency_key="dataset-swap-key",
                input_fingerprint="fingerprint-new",
            )
        )

        after = facade.get_state(sid)
        assert after.get("table1") is None
        assert after.get("specification_equation") is None
        assert after.get("prewrite_gate") is None
        assert after.get("table1Confirmed") is False
        assert after.get("specConfirmed") is False
        assert after.get("dataAttached") is False
        assert after.get("upload_readiness") == "PROCESSING"
        assert _confirmations(after) == {}
        history = _chain(after).get("history") or []
        assert any(entry.get("kind") == "dataset_superseded" for entry in history)
        assert _chain(after).get("dataset_revision") == 1

        # Finish the upload before testing the missing-preview gate; a queued
        # upload is intentionally session_busy under the atomic admission lock.
        from runner import process_one_run
        assert asyncio.run(process_one_run(owner="swap-test", run_id=admission.run.run_id))
        assert facade.get_state(sid)["upload_readiness"] == "READY"
        # Re-attaching the new data is not enough: approvals described old data.
        _bind_confirm_attached(sid)
        stale = _post(client, sid, {"action": "continue_estimate"}, "k2")
        assert stale.status_code == 409, stale.text
        # Replacing data now revokes its old diagnosis as well as approvals.
        # The user must regenerate the preview, not merely re-click old flags.
        assert stale.json()["detail"]["code"] == "prewrite_not_ready"
        assert stale.json()["detail"]["reason"] == "no_identification"
    finally:
        facade.drop_session(sid)


def test_sample_rule_change_revokes_bound_approvals(client, tmp_path):
    """Changing the cleaning / sample rules moves the sample identity: the
    previous Table 1 and its confirmation cannot stand (spec §5)."""
    sid = _seed("sample-rules", _formal_state(tmp_path))
    try:
        recorded = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
        )
        assert recorded.status_code == 200, recorded.text

        filtered = client.post(
            f"/sessions/{sid}/filter",
            json={"conditions": [{"col": "age", "op": ">=", "val": 30}]},
        )
        assert filtered.status_code == 200, filtered.text

        state = facade.get_state(sid)
        assert state.get("table1") is None
        assert state.get("prewrite_gate") is None
        assert state.get("table1Confirmed") is False
        assert _confirmations(state) == {}
        history = _chain(state).get("history") or []
        assert any(entry.get("kind") == "sample_superseded" for entry in history)

        stale = _post(client, sid, {"action": "continue_estimate"}, "k2")
        assert stale.status_code == 409, stale.text
    finally:
        facade.drop_session(sid)


def test_stale_run_result_does_not_overwrite_the_current_version(client, tmp_path):
    """A run admitted for version A that finishes after version B is in place
    writes its own history, not the current preview."""
    sid = _seed("stale-run", _formal_state(tmp_path))
    try:
        accepted = client.post(
            f"/sessions/{sid}/direction",
            json={**_direction(), **observed(client, sid)},
            headers={"Idempotency-Key": "k1"},
        )
        assert accepted.status_code == 202, accepted.text
        run_id = accepted.json()["run_id"]
        stale_result = {
            "table1": {"produced_by": "prewrite_preview", "columns": [], "rows": [{"variable": "age"}]},
            "specification_equation": "income = β₀ + β₁ age + ε",
            "prewrite_gate": "awaiting_estimate",
            "table1Confirmed": True,
            "specConfirmed": True,
            "main_specification": {"method": "ols", "outcome": "income", "treatment": "age"},
        }

        # Version B arrives while the run works: a new design draft revokes the
        # version A preview and approvals.
        proposed = client.post(
            f"/sessions/{sid}/design/propose",
            json={"title": "教育年限对工资的影响", "question": ""},
        )
        assert proposed.status_code == 200, proposed.text
        before = facade.get_state(sid)
        assert before.get("table1") is None

        repo = RunRepository()

        async def finish():
            claimed = await repo.claim(run_id, "stale-runner", lease_seconds=60)
            assert claimed is not None
            await repo.complete(
                run_id,
                owner="stale-runner",
                lease_epoch=claimed.lease_epoch,
                result=stale_result,
            )

        asyncio.run(finish())

        state = facade.get_state(sid)
        assert state.get("table1") is None
        assert state.get("table1Confirmed") is False
        assert state.get("specConfirmed") is False
        assert state.get("prewrite_gate") is None
        assert state.get("specification_equation") is None
        assert state["design"]["status"] == "draft"
        history = _chain(state).get("history") or []
        assert any(entry.get("kind") == "stale_run_result" for entry in history)
    finally:
        facade.drop_session(sid)


# ---------------------------------------------------------------------------
# R6: #40 tri-state permission is consumed at the estimate entry
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "diag,star,expected",
    [
        (_PASS_DIAG, 3, 202),
        (_UNKNOWN_DIAG, None, 202),
    ],
)
def test_estimate_allowed_for_allow_permission(client, tmp_path, diag, star, expected):
    """``allow`` (clean, and unknown which must not add a gate) proceeds once
    both real confirms are made."""
    sid = _seed(f"r6-allow-{star}", _formal_state(tmp_path, diag=diag, star=star))
    try:
        assert (
            _post(
                client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
            ).status_code
            == 200
        )
        assert (
            _post(
                client, sid, {"action": "record_confirms", "specConfirmed": True}, "k2"
            ).status_code
            == 200
        )
        accepted = _post(client, sid, {"action": "continue_estimate"}, "k3")
        assert accepted.status_code == expected, accepted.text
    finally:
        facade.drop_session(sid)


def test_estimate_requires_risk_decision_when_permission_is_confirm(client, tmp_path):
    """A risk the user must decide on cannot be waved through by confirming the
    sample and the setting; the decision names diagnosis and design."""
    sid = _seed("r6-confirm", _formal_state(tmp_path, diag=dict(_RISK_DIAG), star=1))
    try:
        assert (
            _post(
                client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
            ).status_code
            == 200
        )
        assert (
            _post(
                client, sid, {"action": "record_confirms", "specConfirmed": True}, "k2"
            ).status_code
            == 200
        )
        blocked = _post(client, sid, {"action": "continue_estimate"}, "k3")
        assert blocked.status_code == 409, blocked.text
        assert blocked.json()["detail"]["code"] == "risk_confirmation_required"
        assert _active_run(sid) is None

        decided = _post(
            client, sid, {"action": "record_confirms", "riskConfirmed": True}, "k4"
        )
        assert decided.status_code == 200, decided.text
        record = _confirmations(facade.get_state(sid))["risk"]
        assert record["design"]
        assert record["diagnosis"]

        accepted = _post(client, sid, {"action": "continue_estimate"}, "k5")
        assert accepted.status_code == 202, accepted.text
    finally:
        facade.drop_session(sid)


def test_risk_decision_expires_when_the_diagnosis_changes(client, tmp_path):
    """A decision about one diagnosis does not cover a later one."""
    sid = _seed("r6-risk-diag", _formal_state(tmp_path, diag=dict(_RISK_DIAG), star=1))
    try:
        for key, body in (
            ("k1", {"action": "record_confirms", "table1Confirmed": True}),
            ("k2", {"action": "record_confirms", "specConfirmed": True}),
            ("k3", {"action": "record_confirms", "riskConfirmed": True}),
        ):
            assert _post(client, sid, body, key).status_code == 200

        facade.update_state(
            sid,
            identification_diag={
                "passed": False,
                "star_rating": 1,
                "diagnostics": [
                    {"name": "ols_sanity", "status": "pass"},
                    {"name": "pre_trend", "status": "fail"},
                    {"name": "weak_instrument", "status": "fail"},
                ],
            },
        )
        response = _post(client, sid, {"action": "continue_estimate"}, "k4")
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "risk_confirmation_required"
        assert _active_run(sid) is None
    finally:
        facade.drop_session(sid)


def test_risk_decision_expires_when_the_design_changes(client, tmp_path):
    sid = _seed("r6-risk-stale", _formal_state(tmp_path, diag=dict(_RISK_DIAG), star=1))
    try:
        for key, body in (
            ("k1", {"action": "record_confirms", "table1Confirmed": True}),
            ("k2", {"action": "record_confirms", "specConfirmed": True}),
            ("k3", {"action": "record_confirms", "riskConfirmed": True}),
        ):
            assert _post(client, sid, body, key).status_code == 200

        facade.update_state(
            sid,
            design={
                **_design(treatment="schooling"),
                "confirmed_at": "2026-09-17T03:00:00Z",
            },
        )
        response = _post(client, sid, {"action": "continue_estimate"}, "k4")
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] in {
            "risk_confirmation_required",
            "confirmations_stale",
        }
    finally:
        facade.drop_session(sid)


def test_estimate_forbidden_permission_never_opens(client, tmp_path):
    """``forbid`` (hard block) is not overridable by any confirmation."""
    sid = _seed(
        "r6-forbid",
        _formal_state(
            tmp_path,
            diag={"passed": False, "failed": True, "star_rating": 0, "diagnostics": []},
            star=0,
        ),
    )
    try:
        response = _post(
            client,
            sid,
            {
                "action": "continue_estimate",
                "table1Confirmed": True,
                "specConfirmed": True,
                "riskConfirmed": True,
            },
            "k1",
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"]["code"] == "identification_blocked"
        assert _active_run(sid) is None
    finally:
        facade.drop_session(sid)


# ---------------------------------------------------------------------------
# Idempotency: one intention, one run, one confirmation
# ---------------------------------------------------------------------------


def test_direction_replay_returns_the_same_run(client, tmp_path):
    sid = _seed("idem-direction", _formal_state(tmp_path))
    try:
        first = client.post(
            f"/sessions/{sid}/direction",
            json={**_direction(), **observed(client, sid)},
            headers={"Idempotency-Key": "same-intention"},
        )
        second = client.post(
            f"/sessions/{sid}/direction",
            json={**_direction(), **observed(client, sid)},
            headers={"Idempotency-Key": "same-intention"},
        )
        assert first.status_code == 202, first.text
        assert second.status_code == 202, second.text
        assert first.json()["run_id"] == second.json()["run_id"]
    finally:
        facade.drop_session(sid)


def test_estimate_replay_returns_the_same_run(client, tmp_path):
    sid = _seed("idem-estimate", _formal_state(tmp_path))
    try:
        assert (
            _post(
                client, sid, {"action": "record_confirms", "table1Confirmed": True}, "k1"
            ).status_code
            == 200
        )
        assert (
            _post(
                client, sid, {"action": "record_confirms", "specConfirmed": True}, "k2"
            ).status_code
            == 200
        )
        first = _post(client, sid, {"action": "continue_estimate"}, "same-estimate")
        second = _post(client, sid, {"action": "continue_estimate"}, "same-estimate")
        assert first.status_code == 202, first.text
        assert second.status_code == 202, second.text
        assert first.json()["run_id"] == second.json()["run_id"]

        runs = asyncio.run(_runs_for_session(sid))
        assert len(runs) == 1
    finally:
        facade.drop_session(sid)


def test_confirm_replay_returns_the_same_result_without_second_record(client, tmp_path):
    sid = _seed("idem-confirm", _formal_state(tmp_path))
    try:
        first = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "same-record"
        )
        second = _post(
            client, sid, {"action": "record_confirms", "table1Confirmed": True}, "same-record"
        )
        assert first.status_code == second.status_code == 200
        assert first.json() == second.json()

        state = facade.get_state(sid)
        records = _confirmations(state)
        assert list(records).count("sample") == 1
        requests = _chain(state).get("requests") or {}
        assert sum(1 for item in requests.values() if item.get("action") == "record_confirms") == 1
    finally:
        facade.drop_session(sid)


async def _runs_for_session(session_id: str):
    repo = RunRepository()
    async with repo._factory() as db:  # noqa: SLF001 - test-only introspection
        rows = await db.scalars(
            select(Run).where(Run.session_id == session_id).order_by(Run.created_at)
        )
        return list(rows)

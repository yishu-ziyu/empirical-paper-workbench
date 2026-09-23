"""The user approves the observed object, not whatever is current on arrival."""
from __future__ import annotations

import asyncio
import uuid

import pytest

from facade import facade
from run_repository import RunRepository
from services.formal_binding import preview_identity, supersede_dataset
from .test_formal_chain_binding import _design, _direction, _formal_state, _seed


def target(client, sid):
    return client.get(f"/sessions/{sid}").json().get("confirmation_targets", {})


def post(client, sid, action, **fields):
    return client.post(f"/sessions/{sid}/prewrite/confirm", json={
        "action": action, "expectedTarget": target(client, sid), **fields,
    }, headers={"Idempotency-Key": uuid.uuid4().hex})


def test_old_preview_does_not_approve_new_preview(client, tmp_path):
    sid = _seed("observed-preview", _formal_state(tmp_path))
    observed = target(client, sid)
    state = facade.get_state(sid)
    state["table1"]["n"] += 10
    facade.save_state(sid, state)
    response = post(client, sid, "record_confirms", table1Confirmed=True,
                    expectedTarget=observed)
    assert response.status_code == 409, response.text
    assert not client.get(f"/sessions/{sid}").json()["table1Confirmed"]


def test_missing_observed_target_cannot_confirm_formal_preview(client, tmp_path):
    sid = _seed("missing-target", _formal_state(tmp_path))
    response = client.post(f"/sessions/{sid}/prewrite/confirm",
        json={"action": "record_confirms", "table1Confirmed": True},
        headers={"Idempotency-Key": uuid.uuid4().hex})
    assert response.status_code == 409, response.text


def test_old_diagnosis_cannot_be_approved_as_new_risk(client, tmp_path):
    sid = _seed("observed-diagnosis", _formal_state(tmp_path))
    observed = target(client, sid)
    facade.update_state(sid, identification_diag={"passed": False, "star_rating": 1,
        "diagnostics": [{"name": "new-risk", "status": "fail"}]}, star_rating=1)
    response = post(client, sid, "record_confirms", riskConfirmed=True,
                    expectedTarget=observed)
    assert response.status_code == 409, response.text


def test_attach_confirmation_names_dataset_bytes(client, tmp_path):
    sid = _seed("observed-data", _formal_state(tmp_path))
    observed = target(client, sid)
    state = supersede_dataset(facade.get_state(sid), fingerprint="different-bytes")
    facade.save_state(sid, {**state, "dataAttached": False, "data_attached": False})
    response = client.post(f"/sessions/{sid}/confirm-attach", json={"expectedTarget": observed})
    assert response.status_code == 409, response.text


def test_two_drafts_at_same_time_have_distinct_revisions(client, monkeypatch):
    monkeypatch.setattr("agent.design.propose._utc_now", lambda: "2026-09-18T00:00:00Z")
    sid = client.post("/sessions").json()["session_id"]
    a = client.post(f"/sessions/{sid}/design/propose", json={"title": "教育与工资"}).json()
    b = client.post(f"/sessions/{sid}/design/propose", json={"title": "最低工资与就业"}).json()
    assert a["proposed_at"] == b["proposed_at"]
    assert a.get("revision") and a["revision"] != b.get("revision")
    response = client.post(f"/sessions/{sid}/design/confirm", json={"expectedRevision": a["revision"]})
    assert response.status_code == 409, response.text


def test_new_design_confirmation_requires_seen_revision(client):
    sid = client.post("/sessions").json()["session_id"]
    client.post(f"/sessions/{sid}/design/propose", json={"title": "教育与工资"})
    assert client.post(f"/sessions/{sid}/design/confirm").status_code == 409


@pytest.mark.parametrize("method,approved,submitted", [
    ("rd", {"running_var": "age", "cutoff": 0}, {"running_var": "age", "cutoff": 20}),
    ("iv", {"instruments": ["z1"]}, {"instrument": "z2"}),
    ("ols", {"cluster": "school"}, {"cluster": "region"}),
    ("did", {"time_col": "year"}, {"time_col": "month"}),
    ("ols", {"interactions": []}, {"interactions": ["age:group"]}),
])
def test_execution_fields_cannot_differ_from_approved_design(client, tmp_path, method, approved, submitted):
    sid = _seed("method-field", _formal_state(tmp_path, design=_design(method=method, **approved)))
    response = client.post(f"/sessions/{sid}/direction", json={
        **_direction(method=method, **submitted), "expectedTarget": target(client, sid),
    }, headers={"Idempotency-Key": uuid.uuid4().hex})
    assert response.status_code == 409, response.text
    assert asyncio.run(RunRepository().active_run(sid)) is None


def test_supersede_keeps_evidence_history_not_current_result(tmp_path):
    state = _formal_state(tmp_path, estimate={"coef": 77, "status": "ok"},
        results="coefficient 77", robustness_results={"produced_by": "robustness_check"})
    out = supersede_dataset(state, fingerprint="new-file")
    assert not out.get("estimate") and not out.get("results")
    assert not out.get("identification_diag") and not out.get("robustness_results")
    assert any(entry.get("estimate", {}).get("coef") == 77
               for entry in out["formal_chain"]["history"])


def test_same_key_different_phase_is_conflict(client, tmp_path):
    sid = _seed("phase-conflict", _formal_state(tmp_path))
    seen = target(client, sid)
    headers = {"Idempotency-Key": uuid.uuid4().hex}
    a = client.post(f"/sessions/{sid}/direction", json={**_direction(), "expectedTarget": seen}, headers=headers)
    assert a.status_code == 202, a.text
    b = client.post(f"/sessions/{sid}/prewrite/confirm", json={"action": "continue_estimate", "expectedTarget": seen}, headers=headers)
    assert b.status_code == 409, b.text


def test_confirmation_key_cannot_change_meaning(client, tmp_path):
    sid = _seed("confirm-conflict", _formal_state(tmp_path))
    seen = target(client, sid)
    headers = {"Idempotency-Key": uuid.uuid4().hex}
    a = client.post(f"/sessions/{sid}/prewrite/confirm", json={"action": "record_confirms", "table1Confirmed": True, "expectedTarget": seen}, headers=headers)
    assert a.status_code == 200, a.text
    b = client.post(f"/sessions/{sid}/prewrite/confirm", json={"action": "record_confirms", "specConfirmed": True, "expectedTarget": seen}, headers=headers)
    assert b.status_code == 409, b.text


def test_design_compare_and_lock_cannot_approve_concurrent_replacement(client, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    import services.session_design as service

    sid = client.post("/sessions").json()["session_id"]
    first = client.post(f"/sessions/{sid}/design/propose", json={"title": "教育与工资"}).json()
    entered, release = threading.Event(), threading.Event()
    original = service.lock_confirmed_design

    def pause_inside_lock(design, **kwargs):
        entered.set()
        assert release.wait(10)
        return original(design, **kwargs)

    monkeypatch.setattr(service, "lock_confirmed_design", pause_inside_lock)
    with ThreadPoolExecutor(max_workers=2) as pool:
        confirming = pool.submit(client.post, f"/sessions/{sid}/design/confirm",
                                 json={"expectedRevision": first["revision"]})
        assert entered.wait(10)
        replacing = pool.submit(client.post, f"/sessions/{sid}/design/propose",
                                json={"title": "最低工资与就业"})
        release.set()
        confirmed = confirming.result(timeout=15)
        replacement = replacing.result(timeout=15)
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["design"]["revision"] == first["revision"]
    assert replacement.status_code == 200, replacement.text
    current = client.get(f"/sessions/{sid}").json()["design"]
    assert current["revision"] == replacement.json()["revision"]
    assert current["status"] == "draft"


def test_equivalent_method_aliases_use_approved_parameters(client, tmp_path):
    sid = _seed("equivalent-aliases", _formal_state(tmp_path,
        design=_design(method="iv", instruments=["z"], cluster="school")))
    body = {**_direction(method="2sls", instrument_col="z", cluster_col="school"),
            "expectedTarget": target(client, sid)}
    response = client.post(f"/sessions/{sid}/direction", json=body,
                           headers={"Idempotency-Key": uuid.uuid4().hex})
    assert response.status_code == 202, response.text
    run = asyncio.run(RunRepository().get(response.json()["run_id"]))
    assert run.payload["research_direction"]["instruments"] == ["z"]
    assert run.payload["research_direction"]["cluster"] == "school"


def test_empty_approved_variables_are_not_permission_to_supply_arbitrary_columns(client, tmp_path):
    sid = _seed("empty-design-columns", _formal_state(tmp_path,
        design=_design(outcome="", treatment="")))
    response = client.post(f"/sessions/{sid}/direction",
        json={**_direction(), "expectedTarget": target(client, sid)},
        headers={"Idempotency-Key": uuid.uuid4().hex})
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "design_execution_mismatch"


def test_replay_of_accepted_intent_survives_new_draft(client, tmp_path):
    sid = _seed("replay-old-target", _formal_state(tmp_path))
    body = {**_direction(), "expectedTarget": target(client, sid)}
    headers = {"Idempotency-Key": uuid.uuid4().hex}
    first = client.post(f"/sessions/{sid}/direction", json=body, headers=headers)
    assert first.status_code == 202, first.text
    client.post(f"/sessions/{sid}/design/propose", json={"title": "教育与工资"})
    again = client.post(f"/sessions/{sid}/direction", json=body, headers=headers)
    assert again.status_code == 202, again.text
    assert again.json()["run_id"] == first.json()["run_id"]
    changed = {**body, "controls": ["new-control"]}
    conflict = client.post(f"/sessions/{sid}/direction", json=changed, headers=headers)
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["code"] == "idempotency_conflict"


def test_public_evidence_has_history_without_old_current_numbers(client, tmp_path):
    sid = _seed("history-read-model", _formal_state(tmp_path,
        estimate={"coef": 77, "n": 3, "status": "ok", "produced_by": "estimate"},
        results="old result"))
    facade.save_state(sid, supersede_dataset(facade.get_state(sid), fingerprint="new-bytes"))
    result = client.get(f"/sessions/{sid}/evidence").json()
    assert result["available"] is False and result["estimate"] is None
    assert result["evidence_stale"] is True
    assert result["history"][0]["coef"] == 77
    assert "csv_path" not in str(result["history"])


@pytest.mark.parametrize("override", [
    {"qType": "average"}, {"specMode": "interaction"}, {"hasInteraction": True},
])
def test_confirmation_cannot_rewrite_the_analysis_to_bypass_a_gate(client, tmp_path, override):
    sid = _seed("confirm-is-not-edit", _formal_state(tmp_path,
        design=_design(qType="heterogeneity"), qType="heterogeneity", specMode="level"))
    sample = post(client, sid, "record_confirms", table1Confirmed=True)
    assert sample.status_code == 200, sample.text
    response = post(client, sid, "record_confirms", specConfirmed=True, **override)
    assert response.status_code == 409, response.text
    assert client.get(f"/sessions/{sid}").json()["specConfirmed"] is False

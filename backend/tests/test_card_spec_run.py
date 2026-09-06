"""M2 Card specification runs: real OLS/IV, preview isolation, surprise, challenge."""
from __future__ import annotations

import asyncio
import uuid

import pandas as pd
import pytest

from facade import facade
from models.run import Run
from run_repository import RunRepository
from runner import process_one_run
from services.research_lab import (
    evaluate_surprise,
    formula_for_choices,
    temporary_spec,
)


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
    return resp.json()


def _finish(run_id: str, owner: str) -> None:
    assert asyncio.run(process_one_run(owner=owner, run_id=run_id))


def _ready(client) -> str:
    accepted = _boot(client)
    _finish(accepted["run_id"], "card-m2-upload")
    sid = accepted["session_id"]
    frozen = client.post(f"/sessions/{sid}/research/specification-space/freeze")
    assert frozen.status_code == 200, frozen.text
    return sid


def _run_space(client, sid: str) -> dict:
    resp = client.post(
        f"/sessions/{sid}/research/specification-space/run",
        headers=_headers(),
    )
    assert resp.status_code == 202, resp.text
    _finish(resp.json()["run_id"], "card-m2-space")
    return client.get(f"/sessions/{sid}/research").json()


def test_space_run_requires_freeze(client):
    accepted = _boot(client)
    _finish(accepted["run_id"], "card-m2-upload-unfrozen")
    sid = accepted["session_id"]
    resp = client.post(
        f"/sessions/{sid}/research/specification-space/run",
        headers=_headers(),
    )
    assert resp.status_code == 409


def test_card_ols_and_iv_runs_are_real(client):
    sid = _ready(client)
    lab = _run_space(client, sid)
    runs = lab["specification_runs"]
    assert len(runs) >= 2
    by_spec = {run["spec_id"]: run for run in runs}
    extract = lab["provenance"]["extract_kind"]
    if extract == "wooldridge_card_34":
        ols_id, iv_id = "ols_region_dummies", "iv_region_dummies"
    else:
        ols_id, iv_id = "ols_full_controls", "iv_nearc4_full"
        assert "ols_region_dummies" not in by_spec
        assert "iv_region_dummies" not in by_spec
    ols = by_spec[ols_id]
    iv = by_spec[iv_id]
    required = (
        "spec_id",
        "choices",
        "estimator",
        "formula",
        "covariance",
        "analysis_dataset",
        "producer_run_id",
        "coef",
        "se",
        "p",
        "n",
        "status",
        "provenance",
        "created_at",
        "relation",
    )
    for run in (ols, iv):
        for field in required:
            assert run.get(field) not in (None, "", []), field
    state = facade.get_state(sid)
    lab_state = state.get("research_lab") or {}
    extract_path = lab_state.get("extract_csv_path") or state["csv_path"]
    df = pd.read_csv(extract_path)
    columns = [str(col) for col in df.columns]
    from agent.nodes.estimate import _estimate_iv, _estimate_ols

    defs = {item["id"]: item for item in lab["specification_space"]["definitions"]}
    ols_spec = temporary_spec(defs[ols_id], columns)
    iv_spec = temporary_spec(defs[iv_id], columns)
    ols_out = _estimate_ols(df, ols_spec, ols_spec["formula"])["estimate"]
    iv_out = _estimate_iv(df, iv_spec, iv_spec["formula"])["estimate"]
    assert ols["coef"] == pytest.approx(ols_out["coef"], rel=1e-6, abs=1e-8)
    assert iv["coef"] == pytest.approx(iv_out["coef"], rel=1e-6, abs=1e-8)
    assert "educ" in ols["formula"]
    assert "nearc4" in iv["formula"]
    if extract == "wooldridge_card_34":
        assert "smsa66" in ols["formula"]
        assert "reg668" in ols["formula"]
        assert "reg669" not in ols["formula"]
        assert "05_filter" not in str(extract_path)
        assert ols["coef"] == pytest.approx(0.0747, abs=0.002)
        assert iv["coef"] == pytest.approx(0.1315, abs=0.003)


def test_preview_does_not_change_canonical_estimate(client):
    sid = _ready(client)
    seeded = {
        "status": "ok",
        "produced_by": "estimate",
        "coef": 0.1111,
        "se": 0.01,
        "p": 0.0,
        "n": 3010,
        "formula": "seeded canonical",
        "source_run_id": "canonical-seed",
    }
    facade.update_state(sid, estimate=seeded)
    spec_id = "ols_linear_exper"
    resp = client.post(
        f"/sessions/{sid}/research/specs/{spec_id}/run",
        json={"mode": "preview"},
        headers=_headers(),
    )
    assert resp.status_code == 202, resp.text
    _finish(resp.json()["run_id"], "card-m2-preview")
    snapshot = client.get(f"/sessions/{sid}").json()
    estimate = snapshot["estimate"]
    assert estimate["coef"] == seeded["coef"]
    assert estimate["formula"] == seeded["formula"]
    assert estimate["source_run_id"] == "canonical-seed"
    runs = snapshot["research"]["specification_runs"]
    assert any(run["spec_id"] == spec_id and run["relation"] == "preview" for run in runs)


def test_spec_run_result_cannot_cas_overwrite_estimate(client, monkeypatch):
    sid = _ready(client)
    seeded = {
        "status": "ok",
        "produced_by": "estimate",
        "coef": 0.2222,
        "formula": "keep me",
        "source_run_id": "seed-keep",
    }
    facade.update_state(sid, estimate=seeded)

    import runner as runner_mod

    def poisoned(session_id, run_id, payload, progress_callback=None):
        return {
            "estimate": {
                "coef": 9.999,
                "formula": "poison",
                "source_run_id": "poison",
                "produced_by": "estimate",
            },
            "results": "poison table",
            "main_specification": {"method": "iv"},
            "body_chapters": [{"type": "results", "content": "nope"}],
            "claim": "poison claim",
            "outline": [{"type": "results"}],
            "research_lab": facade.get_state(session_id).get("research_lab"),
        }

    monkeypatch.setattr(runner_mod, "execute_spec_run", poisoned)
    resp = client.post(
        f"/sessions/{sid}/research/specs/ols_linear_exper/run",
        json={"mode": "preview"},
        headers=_headers(),
    )
    _finish(resp.json()["run_id"], "card-m2-poison")
    estimate = client.get(f"/sessions/{sid}").json()["estimate"]
    assert estimate["coef"] == 0.2222
    assert estimate["source_run_id"] == "seed-keep"
    stored = asyncio.run(_stored_result(resp.json()["run_id"]))
    assert "estimate" not in stored
    assert "results" not in stored
    assert "claim" not in stored


async def _stored_result(run_id: str) -> dict:
    repo = RunRepository()
    async with repo._factory() as db:
        run = await db.get(Run, run_id)
        assert run is not None
        return dict(run.result or {})


def test_promote_updates_canonical_and_revert_restores(client):
    sid = _ready(client)
    seeded = {
        "status": "ok",
        "produced_by": "estimate",
        "coef": 0.05,
        "formula": "before",
        "source_run_id": "before-run",
    }
    facade.update_state(sid, estimate=seeded)
    resp = client.post(
        f"/sessions/{sid}/research/specs/ols_linear_exper/run",
        json={"mode": "preview"},
        headers=_headers(),
    )
    _finish(resp.json()["run_id"], "card-m2-promote-preview")
    lab = client.get(f"/sessions/{sid}/research").json()
    preview = next(run for run in lab["specification_runs"] if run["spec_id"] == "ols_linear_exper")
    promoted = client.post(
        f"/sessions/{sid}/research/preview/promote",
        json={"run_id": preview["id"]},
    )
    assert promoted.status_code == 200, promoted.text
    snapshot = client.get(f"/sessions/{sid}").json()
    assert snapshot["estimate"]["coef"] == pytest.approx(preview["coef"])
    assert snapshot["estimate"]["source_run_id"] == preview["producer_run_id"]
    assert snapshot["estimate"]["produced_by"] == "estimate"
    assert snapshot["research"]["canonical_spec_id"] == "ols_linear_exper"
    reverted = client.post(f"/sessions/{sid}/research/preview/revert")
    assert reverted.status_code == 200, reverted.text
    after = client.get(f"/sessions/{sid}").json()
    assert after["estimate"]["coef"] == seeded["coef"]
    assert after["estimate"]["source_run_id"] == "before-run"


def test_compare_ols_iv_names_identification(client):
    sid = _ready(client)
    lab = _run_space(client, sid)
    extract = lab["provenance"]["extract_kind"]
    ols_id, iv_id = (
        ("ols_region_dummies", "iv_region_dummies")
        if extract == "wooldridge_card_34"
        else ("ols_full_controls", "iv_nearc4_full")
    )
    compared = client.post(
        f"/sessions/{sid}/research/compare",
        json={"a": ols_id, "b": iv_id},
    )
    assert compared.status_code == 200, compared.text
    body = compared.json()
    changed_dims = {item["dimension"] for item in body["changed"]}
    assert "estimator" in changed_dims or "identification" in changed_dims
    assert "identification" in (body.get("intent") or "").casefold() or "identification" in (
        body.get("why_moved") or ""
    ).casefold()
    assert body["coef_a"] is not None
    assert body["coef_b"] is not None


def _seed_criterion() -> dict:
    return {
        "id": "criterion.seed.iv-below-ols",
        "kind": "ordering",
        "operator": "lt",
        "left": {"metric": "estimate.coef", "estimator": "iv", "label": "IV estimate"},
        "right": {"metric": "estimate.coef", "estimator": "ols", "label": "OLS estimate"},
        "label": "IV estimate < OLS estimate",
        "source": "seed",
    }


def test_surprise_ordering_mismatch_on_real_magnitudes():
    expectation = {
        "text": "I expect OLS to be positive. If ability creates upward bias, IV may be smaller.",
        "criteria": [_seed_criterion()],
    }
    surprise = evaluate_surprise(
        expectation,
        [
            {"spec_id": "ols_region_dummies", "method": "ols", "coef": 0.0747, "status": "ok"},
            {"spec_id": "iv_region_dummies", "method": "iv", "coef": 0.1315, "status": "ok"},
        ],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    assert surprise is not None
    assert surprise["status"] == "Unexpected"
    assert surprise["kind"] == "ordering_mismatch"
    assert "ordering_mismatch" in surprise["kinds"]
    assert surprise["expected"] == "IV estimate < OLS estimate"
    # Observed must carry the actual numbers and express IV > OLS.
    assert "0.1315" in surprise["observed"]
    assert "0.0747" in surprise["observed"]
    assert ">" in surprise["observed"]


def test_surprise_expected_when_criterion_holds():
    expectation = {
        "text": "IV below OLS.",
        "criteria": [_seed_criterion()],
    }
    surprise = evaluate_surprise(
        expectation,
        [
            {"spec_id": "ols_region_dummies", "method": "ols", "coef": 0.13, "status": "ok"},
            {"spec_id": "iv_region_dummies", "method": "iv", "coef": 0.09, "status": "ok"},
        ],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    assert surprise is not None
    assert surprise["status"] == "Expected"
    assert surprise["kind"] is None
    assert surprise["kinds"] == []


def test_surprise_sign_operator_deterministic():
    positive = {
        "id": "criterion.iv-positive",
        "kind": "sign",
        "operator": "positive",
        "left": {"metric": "estimate.coef", "estimator": "iv", "label": "IV estimate"},
        "label": "IV estimate is positive",
        "source": "user",
    }
    violated = evaluate_surprise(
        {"text": "IV positive.", "criteria": [positive]},
        [{"spec_id": "iv_region_dummies", "method": "iv", "coef": -0.2, "status": "ok"}],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    assert violated["status"] == "Unexpected"
    assert violated["kind"] == "direction_mismatch"
    satisfied = evaluate_surprise(
        {"text": "IV positive.", "criteria": [positive]},
        [{"spec_id": "iv_region_dummies", "method": "iv", "coef": 0.2, "status": "ok"}],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    assert satisfied["status"] == "Expected"


def test_surprise_distance_operator_with_tolerance():
    approx = {
        "id": "criterion.iv-approx-ols",
        "kind": "distance",
        "operator": "approx",
        "left": {"metric": "estimate.coef", "estimator": "iv", "label": "IV estimate"},
        "right": {"metric": "estimate.coef", "estimator": "ols", "label": "OLS estimate"},
        "tolerance": {"rel": 0.05},
        "label": "IV ≈ OLS",
        "source": "user",
    }
    violated = evaluate_surprise(
        {"text": "similar.", "criteria": [approx]},
        [
            {"spec_id": "ols_region_dummies", "method": "ols", "coef": 0.08, "status": "ok"},
            {"spec_id": "iv_region_dummies", "method": "iv", "coef": 0.13, "status": "ok"},
        ],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    assert violated["status"] == "Unexpected"
    assert violated["kind"] == "magnitude"
    satisfied = evaluate_surprise(
        {"text": "similar.", "criteria": [approx]},
        [
            {"spec_id": "ols_region_dummies", "method": "ols", "coef": 0.08, "status": "ok"},
            {"spec_id": "iv_region_dummies", "method": "iv", "coef": 0.0805, "status": "ok"},
        ],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    assert satisfied["status"] == "Expected"


def test_surprise_without_criteria_stays_expected():
    surprise = evaluate_surprise(
        {"text": "Free-form text with the words iv smaller similar positive."},
        [
            {"spec_id": "ols_region_dummies", "method": "ols", "coef": 0.07, "status": "ok"},
            {"spec_id": "iv_region_dummies", "method": "iv", "coef": 0.13, "status": "ok"},
        ],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    assert surprise is not None
    assert surprise["status"] == "Expected"
    assert surprise["kind"] is None


def test_surprise_unresolvable_metric_stays_silent():
    criterion = {
        "id": "criterion.future-att",
        "kind": "sign",
        "operator": "positive",
        "left": {"metric": "att", "estimator": "did", "label": "ATT"},
        "label": "ATT positive",
        "source": "user",
    }
    surprise = evaluate_surprise(
        {"text": "text", "criteria": [criterion]},
        [{"spec_id": "ols_region_dummies", "method": "ols", "coef": 0.07, "status": "ok"}],
        ols_spec_id="ols_region_dummies",
        iv_spec_id="iv_region_dummies",
    )
    assert surprise is not None
    assert surprise["status"] == "Expected"


def test_card_default_expectation_is_unexpected_after_runs(client):
    sid = _ready(client)
    lab = _run_space(client, sid)
    surprise = lab["surprise"]
    assert surprise["status"] == "Unexpected"
    assert surprise["kind"] == "ordering_mismatch"
    assert lab["next_challenge"]
    assert lab["next_challenge"]["id"]


def test_accept_challenge_creates_preview_run(client):
    sid = _ready(client)
    lab = _run_space(client, sid)
    challenge = lab["next_challenge"]
    before = len(lab["specification_runs"])
    resp = client.post(
        f"/sessions/{sid}/research/challenges/{challenge['id']}/accept",
        headers=_headers(),
    )
    assert resp.status_code == 202, resp.text
    _finish(resp.json()["run_id"], "card-m2-challenge")
    later = client.get(f"/sessions/{sid}/research").json()
    assert len(later["specification_runs"]) > before
    assert any(run["relation"] == "preview" for run in later["specification_runs"])
    assert later["next_challenge"]["status"] == "accepted"


def test_iv_diagnostic_f_comes_from_controlled_spec(client):
    sid = _ready(client)
    lab = _run_space(client, sid)
    extract = lab["provenance"]["extract_kind"]
    iv_id = "iv_region_dummies" if extract == "wooldridge_card_34" else "iv_nearc4_full"
    iv = next(run for run in lab["specification_runs"] if run["spec_id"] == iv_id)
    diag = iv["diagnostics"]
    f_stat = diag.get("F_eff") or diag.get("first_stage_F")
    assert f_stat is not None
    assert f_stat < 40
    if extract == "wooldridge_card_34":
        assert 8 < f_stat < 25
        assert "smsa66" in (diag.get("controls") or []) or "smsa66" in iv["formula"]


def test_nine_col_path_does_not_fake_region_runs(client, monkeypatch):
    monkeypatch.setenv("ECONPAPER_CARD_EXTRACT", "statspai_card_9")
    sid = _ready(client)
    lab = _run_space(client, sid)
    assert lab["provenance"]["extract_kind"] == "statspai_card_9"
    spec_ids = {run["spec_id"] for run in lab["specification_runs"]}
    assert "ols_region_dummies" not in spec_ids
    assert "iv_region_dummies" not in spec_ids
    assert "ols_full_controls" in spec_ids
    assert "iv_nearc4_full" in spec_ids
    iv = next(run for run in lab["specification_runs"] if run["spec_id"] == "iv_nearc4_full")
    assert "smsa66" not in (iv.get("formula") or "")
    f_stat = (iv.get("diagnostics") or {}).get("F_eff") or (iv.get("diagnostics") or {}).get(
        "first_stage_F"
    )
    assert f_stat is not None
    assert f_stat < 50


def test_formula_mapping_drops_reg669():
    choices = {
        "estimator": "iv",
        "identification": "nearc4",
        "experience": "quadratic",
        "demographics": "black",
        "region": "reg66",
    }
    columns = [
        "lwage",
        "educ",
        "nearc4",
        "exper",
        "expersq",
        "black",
        "smsa",
        "south",
        "smsa66",
        *[f"reg66{i}" for i in range(1, 10)],
    ]
    formula = formula_for_choices(choices, columns)
    assert "reg668" in formula
    assert "reg669" not in formula
    assert "(educ ~ nearc4)" in formula


def test_execute_spec_run_rejects_empty_admissible_set(tmp_path):
    from services.spec_run import SpecRunRejected, execute_spec_run

    csv_path = tmp_path / "empty-admissible.csv"
    csv_path.write_text("lwage,educ,nearc4\n1,12,1\n", encoding="utf-8")
    sid = "spec-run-empty-admissible"
    facade.create_session(sid)
    facade.save_state(
        sid,
        {
            "csv_path": str(csv_path),
            "research_lab": {
                "teaching_case": "card_1995",
                "specification_space": {
                    "definitions": [],
                    "frozen_at": "2026-09-06T00:00:00+00:00",
                },
                "specification_runs": [],
            },
        },
    )
    with pytest.raises(SpecRunRejected) as caught:
        execute_spec_run(sid, "run-empty", {"spec_ids": ["ols_full_controls"]}, None)
    assert caught.value.code == "no_admissible_specifications"
    facade.delete_session(sid)


def test_merge_spec_run_does_not_clobber_newer_claim_or_canonical():
    from services.research_lab import merge_spec_run_lab

    current = {
        "canonical_spec_id": "iv_region_dummies",
        "evidence_revision": 3,
        "current_claim_id": "claim.card.education-earnings",
        "claim": {
            "id": "claim.card.education-earnings",
            "version": 4,
            "approved_by_user": True,
            "stale": False,
            "based_on_evidence_revision": 3,
            "claim_text": "keep me",
        },
        "claims": [
            {
                "id": "claim.card.education-earnings",
                "version": 4,
                "approved_by_user": True,
                "stale": False,
                "based_on_evidence_revision": 3,
                "claim_text": "keep me",
            }
        ],
        "specification_runs": [{"id": "run-ols", "spec_id": "ols_linear_exper", "status": "ok"}],
    }
    incoming = {
        "canonical_spec_id": "ols_linear_exper",
        "evidence_revision": 2,
        "claim": {
            "id": "claim.card.education-earnings",
            "version": 1,
            "approved_by_user": False,
            "stale": True,
            "based_on_evidence_revision": 1,
            "claim_text": "stale worker snapshot",
        },
        "claims": [
            {
                "id": "claim.card.education-earnings",
                "version": 1,
                "claim_text": "stale worker snapshot",
            }
        ],
        "specification_runs": [
            {"id": "run-ols", "spec_id": "ols_linear_exper", "status": "ok"},
            {"id": "run-preview", "spec_id": "iv_region_dummies", "relation": "preview", "status": "ok"},
        ],
    }
    merged = merge_spec_run_lab(current, incoming)
    assert merged["canonical_spec_id"] == "iv_region_dummies"
    assert merged["claim"]["version"] == 4
    assert merged["claim"]["claim_text"] == "keep me"
    assert merged["evidence_revision"] == 4
    assert merged["claim"]["stale"] is True
    assert any(run["id"] == "run-preview" for run in merged["specification_runs"])

"""M4 Claim Ledger: draft from runs, approve gate, stale results, wording bound."""
from __future__ import annotations

import asyncio
import uuid

import pytest

from conftest import make_six_chapter_outline, make_write_ready_state
from facade import facade
from runner import process_one_run
from services.research_lab import (
    CARD_CONDITIONAL_WORDING,
    CARD_SUPPORTED_WORDING,
    CARD_UNSUPPORTED_WORDING,
    promote_run,
    revert_canonical,
)


@pytest.fixture(autouse=True)
def _cleanup_card_sessions(client):
    from sqlalchemy import select
    from models.research_session import ResearchSession
    from run_repository import RunRepository

    async def ids() -> set[str]:
        repo = RunRepository()
        async with repo._factory() as db:
            return set(await db.scalars(select(ResearchSession.session_id)))

    before = asyncio.run(ids())
    yield
    for session_id in asyncio.run(ids()) - before:
        facade.delete_session(session_id)


def _headers(key: str | None = None) -> dict[str, str]:
    return {"Idempotency-Key": key or str(uuid.uuid4())}


def _finish(run_id: str, owner: str) -> None:
    assert asyncio.run(process_one_run(owner=owner, run_id=run_id))


def _boot_frozen(client) -> str:
    accepted = client.post("/demos/card", headers=_headers())
    assert accepted.status_code == 202, accepted.text
    _finish(accepted.json()["run_id"], "card-m4-upload")
    sid = accepted.json()["session_id"]
    frozen = client.post(f"/sessions/{sid}/research/specification-space/freeze")
    assert frozen.status_code == 200, frozen.text
    return sid


def _run_space(client, sid: str) -> dict:
    resp = client.post(
        f"/sessions/{sid}/research/specification-space/run",
        headers=_headers(),
    )
    assert resp.status_code == 202, resp.text
    _finish(resp.json()["run_id"], "card-m4-space")
    return client.get(f"/sessions/{sid}/research").json()


def _seed_write_ready(sid: str, research_lab: dict) -> None:
    lab = dict(research_lab)
    required = ((lab.get("claim") or {}).get("provenance") or {}).get("iv_spec_id")
    if required:
        lab["canonical_spec_id"] = required
    state = make_write_ready_state(
        outline=make_six_chapter_outline(),
        current_chapter_index=4,
        research_lab=lab,
        body_chapters=[
            {},
            {},
            {},
            {},
            {
                "type": "results",
                "title": "结果",
                "content": "旧结果正文。",
                "status": "generated",
                "grounded": True,
            },
            {},
        ],
    )
    facade.save_state(sid, {**facade.get_state(sid), **state, "research_lab": lab})


def test_space_run_auto_drafts_card_claim_fields(client):
    sid = _boot_frozen(client)
    lab = _run_space(client, sid)
    claims = lab["claims"]
    assert len(claims) == 1
    claim = lab["claim"]
    assert claim["id"] == claims[0]["id"]
    assert claim["supported_wording"] == CARD_SUPPORTED_WORDING
    assert claim["conditionally_supported_wording"] == CARD_CONDITIONAL_WORDING
    assert claim["unsupported_wording"] == CARD_UNSUPPORTED_WORDING
    assert claim["claim_text"] == CARD_SUPPORTED_WORDING
    assert claim["claim_type"]
    assert claim["supporting_run_ids"]
    assert claim["unresolved_assumptions"]
    assert claim["version"] == 1
    assert claim["approved_by_user"] is False
    assert claim["provenance"]
    assert any("exclusion" in item.lower() or "exclusion" in item for item in claim["unresolved_assumptions"])
    assert any("late" in item.lower() for item in claim["unresolved_assumptions"])
    snapshot = client.get(f"/sessions/{sid}").json()
    assert snapshot["research"]["claim"]["id"] == claim["id"]
    assert snapshot["research"]["claims"][0]["id"] == claim["id"]


def test_promote_and_revert_do_not_bump_evidence_revision_or_stale_claim():
    claim = {
        "id": "claim.card.education-earnings",
        "approved_by_user": True,
        "stale": False,
        "based_on_evidence_revision": 2,
        "version": 1,
    }
    lab = {
        "evidence_revision": 2,
        "canonical_spec_id": "ols_region_dummies",
        "canonical_history": [],
        "decision_events": [],
        "claims": [claim],
        "current_claim_id": claim["id"],
        "claim": claim,
        "specification_runs": [
            {
                "id": "run-ols",
                "spec_id": "ols_region_dummies",
                "relation": "canonical",
                "status": "ok",
            },
            {
                "id": "run-iv",
                "spec_id": "iv_region_dummies",
                "relation": "exploratory",
                "status": "ok",
            },
        ],
    }
    promoted = promote_run(lab, lab["specification_runs"][1], {"coef": 0.13})
    assert promoted["evidence_revision"] == 2
    assert promoted["canonical_spec_id"] == "iv_region_dummies"
    assert promoted["claim"]["stale"] is not True
    assert promoted["claim"]["approved_by_user"] is True
    assert promoted["claim"]["based_on_evidence_revision"] == 2
    assert any(event.get("kind") == "preview_promote" for event in promoted["decision_events"])
    assert promoted["canonical_history"]
    assert not any(event.get("kind") == "claim_drafted" for event in promoted["decision_events"])

    reverted, restored = revert_canonical(promoted)
    assert reverted["evidence_revision"] == 2
    assert reverted["canonical_spec_id"] == "ols_region_dummies"
    assert reverted["claim"]["stale"] is not True
    assert reverted["claim"]["approved_by_user"] is True
    assert any(event.get("kind") == "preview_revert" for event in reverted["decision_events"])
    assert restored == {"coef": 0.13}


def test_prepare_paper_does_not_implicitly_promote_canonical(client):
    sid = _boot_frozen(client)
    lab = _run_space(client, sid)
    revision_n = lab["evidence_revision"]
    claim = lab["claim"]
    ols = next(run for run in lab["specification_runs"] if run["method"] == "ols")
    iv = next(
        run
        for run in lab["specification_runs"]
        if run["spec_id"] == lab["claim"]["provenance"]["iv_spec_id"]
    )
    approved = client.post(f"/sessions/{sid}/research/claims/{claim['id']}/approve")
    assert approved.status_code == 200, approved.text
    assert approved.json()["claim"]["based_on_evidence_revision"] == revision_n

    promoted = client.post(
        f"/sessions/{sid}/research/preview/promote",
        json={"run_id": ols["id"]},
    )
    assert promoted.status_code == 200, promoted.text
    assert promoted.json()["canonical_spec_id"] == ols["spec_id"]
    after_ols = client.get(f"/sessions/{sid}/research").json()
    assert after_ols["evidence_revision"] == revision_n
    assert after_ols["claim"]["stale"] is not True
    assert after_ols["claim"]["approved_by_user"] is True
    assert after_ols["claim"]["version"] == claim["version"]
    assert after_ols["claim"]["id"] == claim["id"]
    drafted_after_ols = [
        event for event in (after_ols.get("decision_events") or []) if event.get("kind") == "claim_drafted"
    ]

    prepared = client.post(f"/sessions/{sid}/research/prepare-paper")
    assert prepared.status_code == 409, prepared.text
    detail = prepared.json()["detail"]
    assert detail["code"] == "canonical_mismatch"
    mismatch = client.get(f"/sessions/{sid}/research").json()
    assert mismatch["canonical_spec_id"] == ols["spec_id"]
    assert mismatch["evidence_revision"] == revision_n
    assert mismatch["claim"]["stale"] is not True
    assert mismatch["claim"]["approved_by_user"] is True

    explicit = client.post(
        f"/sessions/{sid}/research/preview/promote",
        json={"run_id": iv["id"]},
    )
    assert explicit.status_code == 200, explicit.text
    after_iv = client.get(f"/sessions/{sid}/research").json()
    assert after_iv["canonical_spec_id"] == iv["spec_id"]
    assert after_iv["evidence_revision"] == revision_n
    assert after_iv["claim"]["stale"] is not True
    assert after_iv["claim"]["approved_by_user"] is True
    assert after_iv["claim"]["version"] == claim["version"]
    drafted_after_iv = [
        event for event in (after_iv.get("decision_events") or []) if event.get("kind") == "claim_drafted"
    ]
    assert drafted_after_iv == drafted_after_ols
    approve_events = [
        event for event in (after_iv.get("decision_events") or []) if event.get("kind") == "claim_approved"
    ]
    assert len(approve_events) == 1

    prepared = client.post(f"/sessions/{sid}/research/prepare-paper")
    assert prepared.status_code == 200, prepared.text
    snapshot = client.get(f"/sessions/{sid}").json()
    assert snapshot["research"]["canonical_spec_id"] == iv["spec_id"]
    assert snapshot["research"]["evidence_revision"] == revision_n
    assert snapshot["research"]["claim"]["stale"] is not True
    written = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "results", "title": "结果"}},
    )
    assert written.status_code == 200, written.text
    chapter = written.json()["chapter"]
    assert chapter["grounded"] is True
    assert "educ" in (chapter.get("content") or "")


def test_new_spec_run_stales_approved_claim(client):
    sid = _boot_frozen(client)
    lab = _run_space(client, sid)
    revision = lab["evidence_revision"]
    assert revision >= 1
    claim = lab["claim"]
    assert claim["based_on_evidence_revision"] == revision
    assert claim["stale"] is False
    client.post(f"/sessions/{sid}/research/claims/{claim['id']}/approve")
    preview = client.post(
        f"/sessions/{sid}/research/specs/{lab['claim']['provenance']['iv_spec_id']}/run",
        json={"mode": "preview"},
        headers=_headers(),
    )
    assert preview.status_code == 202, preview.text
    _finish(preview.json()["run_id"], "card-integrity-preview")
    later = client.get(f"/sessions/{sid}/research").json()
    assert later["evidence_revision"] == revision + 1
    assert later["claim"]["stale"] is True
    assert later["claim"]["claim_text"] == claim["claim_text"]
    assert later["claim"]["version"] == claim["version"]
    snapshot = client.get(f"/sessions/{sid}").json()
    assert "claim_stale" in (snapshot.get("write_blockers") or [])
    _seed_write_ready(sid, facade.get_state(sid)["research_lab"])
    blocked = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "results", "title": "结果"}},
    )
    assert blocked.status_code == 409, blocked.text
    assert "claim_stale" in blocked.json()["detail"]["write_blockers"]
    drafted = client.post(f"/sessions/{sid}/research/claims/draft")
    assert drafted.status_code == 200, drafted.text
    v2 = drafted.json()["claim"]
    assert v2["stale"] is False
    assert v2["version"] == claim["version"] + 1
    assert v2["based_on_evidence_revision"] == later["evidence_revision"]
    client.post(f"/sessions/{sid}/research/claims/{v2['id']}/approve")
    assert client.get(f"/sessions/{sid}/research").json()["claim"]["stale"] is False


def test_claim_approve_required_for_results_and_bind_includes_runs(client):
    sid = _boot_frozen(client)
    lab = _run_space(client, sid)
    claim = lab["claim"]
    _seed_write_ready(sid, facade.get_state(sid)["research_lab"])
    blocked = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "results", "title": "结果"}},
    )
    assert blocked.status_code == 409, blocked.text
    detail = blocked.json()["detail"]
    assert detail["write_blocked"] is True
    assert "claim_unapproved" in detail["write_blockers"]

    approved = client.post(f"/sessions/{sid}/research/claims/{claim['id']}/approve")
    assert approved.status_code == 200, approved.text
    assert approved.json()["claim"]["approved_by_user"] is True

    from agent.engine.bind import bind_chapter_kwargs

    bound = bind_chapter_kwargs(facade.get_state(sid), {"type": "results"})
    assert CARD_SUPPORTED_WORDING in bound["claim_supported_wording"]
    assert CARD_CONDITIONAL_WORDING in bound["claim_conditionally_supported_wording"]
    assert CARD_UNSUPPORTED_WORDING in bound["claim_unsupported_wording"]
    assert "coef=" in bound["claim_run_facts"]
    ols_coef = next(
        run["coef"]
        for run in lab["specification_runs"]
        if run["id"] in claim["supporting_run_ids"] and run["method"] == "ols"
    )
    assert str(ols_coef) in bound["claim_run_facts"] or f"{ols_coef}" in bound["claim_run_facts"]

    written = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "results", "title": "结果"}},
    )
    assert written.status_code == 200, written.text
    chapter = written.json()["chapter"]
    assert chapter["grounded"] is True
    assert chapter.get("stale") is not True
    assert CARD_UNSUPPORTED_WORDING not in (chapter.get("content") or "")


def test_unsupported_wording_is_not_grounded(client):
    sid = _boot_frozen(client)
    lab = _run_space(client, sid)
    claim = lab["claim"]
    client.post(f"/sessions/{sid}/research/claims/{claim['id']}/approve")
    research_lab = facade.get_state(sid)["research_lab"]
    state = make_write_ready_state(
        outline=make_six_chapter_outline(),
        research_lab=research_lab,
        body_chapters=[
            {},
            {},
            {},
            {},
            {
                "type": "results",
                "title": "结果",
                "content": f"Grounded-looking prose. {CARD_UNSUPPORTED_WORDING}",
                "status": "generated",
                "grounded": True,
            },
            {},
        ],
    )
    facade.save_state(sid, {**facade.get_state(sid), **state, "research_lab": research_lab})
    snapshot = client.get(f"/sessions/{sid}").json()
    results = next(ch for ch in snapshot["body_chapters"] if ch.get("type") == "results")
    assert results["grounded"] is False


def test_promote_marks_results_stale(client):
    sid = _boot_frozen(client)
    lab = _run_space(client, sid)
    claim = lab["claim"]
    client.post(f"/sessions/{sid}/research/claims/{claim['id']}/approve")
    _seed_write_ready(sid, facade.get_state(sid)["research_lab"])
    written = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "results", "title": "结果"}},
    )
    assert written.status_code == 200, written.text
    preview = next(
        run
        for run in lab["specification_runs"]
        if run["spec_id"] in {"ols_linear_exper", "ols_full_controls", "ols_region_dummies"}
    )
    promoted = client.post(
        f"/sessions/{sid}/research/preview/promote",
        json={"run_id": preview["id"]},
    )
    assert promoted.status_code == 200, promoted.text
    snapshot = client.get(f"/sessions/{sid}").json()
    results = next(ch for ch in snapshot["body_chapters"] if ch.get("type") == "results")
    assert results["stale"] is True
    assert results["needs_regeneration"] is True
    assert results["grounded"] is False
    assert snapshot["research"]["evidence_revision"] == lab["evidence_revision"]
    assert snapshot["research"]["claim"]["stale"] is not True
    assert snapshot["research"]["claim"]["approved_by_user"] is True
    approve = client.post(
        f"/sessions/{sid}/approve-chapter",
        json={"chapter_type": "results", "force": True},
    )
    assert approve.status_code == 200, approve.text


def test_missing_based_on_revision_is_stale_when_lab_has_revision(client):
    sid = _boot_frozen(client)
    lab = _run_space(client, sid)
    claim = dict(lab["claim"])
    claim["approved_by_user"] = True
    claim["stale"] = False
    claim.pop("based_on_evidence_revision", None)
    lab["claim"] = claim
    lab["claims"] = [claim]
    lab["evidence_revision"] = 3
    _seed_write_ready(sid, lab)

    snapshot = client.get(f"/sessions/{sid}").json()
    assert "claim_stale" in (snapshot.get("write_blockers") or [])
    results = next(ch for ch in snapshot["body_chapters"] if ch.get("type") == "results")
    assert results["grounded"] is False

    prepared = client.post(f"/sessions/{sid}/research/prepare-paper")
    assert prepared.status_code == 409, prepared.text
    detail = prepared.json()["detail"]
    code = detail.get("code") if isinstance(detail, dict) else detail
    assert code == "claim_stale"


def test_sessions_without_claims_keep_old_write_gate(client):
    sid = f"course-panel-{uuid.uuid4()}"
    facade.seed_state(
        sid,
        make_write_ready_state(
            outline=make_six_chapter_outline(),
            current_chapter_index=4,
        ),
    )
    resp = client.post(
        f"/sessions/{sid}/generate-chapter",
        json={"chapter": {"type": "results", "title": "结果"}},
    )
    assert resp.status_code == 200, resp.text
    assert "claim_unapproved" not in (resp.json().get("write_blockers") or [])


def test_evidence_contract_unchanged_with_claims(client):
    sid = _boot_frozen(client)
    _run_space(client, sid)
    evidence = client.get(f"/sessions/{sid}/evidence")
    assert evidence.status_code == 200, evidence.text
    body = evidence.json()
    assert "available" in body
    assert "estimate" in body
    assert "provenance" in body
    assert "claims" not in body


def test_claim_presentation_only_review_preserves_version_and_events_stale_bumps(client):
    sid = _boot_frozen(client)
    lab = _run_space(client, sid)
    claim = lab["claim"]
    assert claim["version"] == 1
    events_initial = lab.get("decision_events") or []
    draft_events_initial = [e for e in events_initial if e.get("kind") == "claim_drafted"]
    assert len(draft_events_initial) == 1

    # Presentation-only review: without calling draft endpoint, Claim version remains 1 and events are untouched
    lab_current = client.get(f"/sessions/{sid}/research").json()
    assert lab_current["claim"]["version"] == 1
    draft_events_after = [
        e for e in (lab_current.get("decision_events") or []) if e.get("kind") == "claim_drafted"
    ]
    assert len(draft_events_after) == 1

    # Calling draft endpoint (Review new evidence / redraft) bumps version and appends event
    draft_resp = client.post(
        f"/sessions/{sid}/research/claims/draft",
        headers=_headers(),
    )
    assert draft_resp.status_code == 200, draft_resp.text
    lab_redrafted = draft_resp.json()
    assert lab_redrafted["claim"]["version"] == 2
    draft_events_redrafted = [
        e for e in (lab_redrafted.get("decision_events") or []) if e.get("kind") == "claim_drafted"
    ]
    assert len(draft_events_redrafted) == 2
    assert draft_events_redrafted[-1]["payload"].get("version") == 2


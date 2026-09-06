"""Research lab read model and Card demo boot commands."""
from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from auth import get_optional_user, require_auth_unless_debug, require_session_ownership
from config import settings
from facade import facade
from models.user import User
from run_repository import QueueFull, RunRepository, SessionBusy, SessionNotFound
from schemas.responses import (
    ResearchLabResponse,
    RunAcceptedResponse,
    SpecCompareResponse,
    UploadResponse,
)
from services.card_demo import admit_card_upload
from services.research_lab import (
    approve_card_claim,
    compare_specification_runs,
    definition_by_id,
    draft_card_claim,
    estimate_payload_from_run,
    find_run,
    freeze_specification_space,
    included_spec_ids,
    mark_results_chapters_stale,
    prepare_card_paper_state,
    public_research,
    promote_run,
    require_frozen,
    require_lab,
    revert_canonical,
    update_expectation,
)

router = APIRouter()


class ExpectationUpdateRequest(BaseModel):
    text: str = Field(min_length=1)
    confidence: Literal["low", "medium", "high"]
    locale: Optional[str] = None


class SpecRunRequest(BaseModel):
    mode: Literal["canonical", "preview"] = "preview"


class SpecCompareRequest(BaseModel):
    a: str = Field(min_length=1)
    b: str = Field(min_length=1)


class PromoteRequest(BaseModel):
    run_id: str = Field(min_length=1)


def _lab_response(state: dict) -> ResearchLabResponse:
    return public_research(state)


@router.post(
    "/demos/card",
    response_model=UploadResponse,
    status_code=202,
    responses={
        409: {"description": "Idempotency key was reused for different input"},
        429: {"description": "The durable run queue is full"},
    },
)
async def boot_card_demo(
    background_tasks: BackgroundTasks,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    current_user: Optional[User] = Depends(get_optional_user),
) -> UploadResponse:
    """Empty-desk Card boot: real extract through the existing upload pipeline."""
    from routers.sessions import _sync_upload_to_s3, _upload_response, _validated_upload_key

    key = _validated_upload_key(idempotency_key)
    require_auth_unless_debug(current_user)
    user_id = current_user.id if current_user else None
    admission, csv_bytes = await admit_card_upload(
        user_id=user_id,
        idempotency_key=key,
    )
    if not admission.replayed and settings.S3_ENDPOINT_URL:
        background_tasks.add_task(
            _sync_upload_to_s3,
            admission.session.session_id,
            csv_bytes,
        )
    return _upload_response(admission)


@router.get(
    "/sessions/{session_id}/research",
    response_model=ResearchLabResponse,
)
async def get_research(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResearchLabResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)
    state = await run_in_threadpool(facade.get_state, session_id)
    return _lab_response(state)


@router.put(
    "/sessions/{session_id}/research/expectation",
    response_model=ResearchLabResponse,
)
async def put_expectation(
    session_id: str,
    body: ExpectationUpdateRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResearchLabResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _write() -> dict:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        updated = update_expectation(
            lab,
            text=body.text,
            confidence=body.confidence,
            locale=body.locale,
        )
        return facade.update_state(session_id, research_lab=updated)

    state = await run_in_threadpool(_write)
    return _lab_response(state)


@router.post(
    "/sessions/{session_id}/research/specification-space/freeze",
    response_model=ResearchLabResponse,
)
async def freeze_space(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResearchLabResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _write() -> dict:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        updated = freeze_specification_space(lab)
        return facade.update_state(session_id, research_lab=updated)

    state = await run_in_threadpool(_write)
    return _lab_response(state)


async def _enqueue_spec_run(
    session_id: str,
    *,
    spec_ids: list[str],
    relation: str,
    idempotency_key: str | None,
    challenge_id: str | None = None,
) -> RunAcceptedResponse:
    try:
        run = await RunRepository().enqueue(
            session_id=session_id,
            kind="spec_run",
            payload={
                "spec_ids": spec_ids,
                "relation": relation,
                "challenge_id": challenge_id,
                "initial_state": {},
            },
            idempotency_key=idempotency_key,
        )
    except SessionNotFound as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    except SessionBusy as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "session_busy", "run_id": exc.run_id},
        ) from exc
    except QueueFull as exc:
        raise HTTPException(
            status_code=429,
            detail="run queue is full",
            headers={"Retry-After": "5"},
        ) from exc
    return RunAcceptedResponse(
        run_id=run.run_id,
        session_id=run.session_id,
        status="PENDING",
        events_url=f"/api/runs/{run.run_id}/events",
    )


@router.post(
    "/sessions/{session_id}/research/specification-space/run",
    response_model=RunAcceptedResponse,
    status_code=202,
)
async def run_specification_space(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> RunAcceptedResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _prepare() -> list[str]:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        require_frozen(lab)
        spec_ids = included_spec_ids(lab)
        if not spec_ids:
            raise HTTPException(status_code=409, detail="no admissible specifications to run")
        return spec_ids

    spec_ids = await run_in_threadpool(_prepare)
    return await _enqueue_spec_run(
        session_id,
        spec_ids=spec_ids,
        relation="exploratory",
        idempotency_key=idempotency_key,
    )


@router.post(
    "/sessions/{session_id}/research/specs/{spec_id}/run",
    response_model=RunAcceptedResponse,
    status_code=202,
)
async def run_one_specification(
    session_id: str,
    spec_id: str,
    body: SpecRunRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> RunAcceptedResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _prepare() -> None:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        require_frozen(lab)
        definition = definition_by_id(lab, spec_id)
        if not definition.get("admissible"):
            raise HTTPException(status_code=409, detail="specification is unavailable")

    await run_in_threadpool(_prepare)
    relation = "preview" if body.mode == "preview" else "exploratory"
    return await _enqueue_spec_run(
        session_id,
        spec_ids=[spec_id],
        relation=relation,
        idempotency_key=idempotency_key,
    )


@router.post(
    "/sessions/{session_id}/research/compare",
    response_model=SpecCompareResponse,
)
async def compare_specs(
    session_id: str,
    body: SpecCompareRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> SpecCompareResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _compare() -> dict:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        require_frozen(lab)
        run_a = find_run(lab, body.a)
        run_b = find_run(lab, body.b)
        return compare_specification_runs(run_a, run_b)

    payload = await run_in_threadpool(_compare)
    return SpecCompareResponse.model_validate(payload)


@router.post(
    "/sessions/{session_id}/research/preview/promote",
    response_model=ResearchLabResponse,
)
async def promote_preview(
    session_id: str,
    body: PromoteRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResearchLabResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _write() -> dict:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        run = find_run(lab, body.run_id)
        current_estimate = state.get("estimate") if isinstance(state.get("estimate"), dict) else None
        updated = promote_run(lab, run, current_estimate)
        estimate = estimate_payload_from_run(run)
        chapters = mark_results_chapters_stale(list(state.get("body_chapters") or []))
        return facade.update_state(
            session_id,
            research_lab=updated,
            estimate=estimate,
            body_chapters=chapters,
        )

    state = await run_in_threadpool(_write)
    return _lab_response(state)


@router.post(
    "/sessions/{session_id}/research/preview/revert",
    response_model=ResearchLabResponse,
)
async def revert_preview(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResearchLabResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _write() -> dict:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        updated, restored = revert_canonical(lab)
        fields: dict = {"research_lab": updated}
        if restored is not None:
            fields["estimate"] = restored
        return facade.update_state(session_id, **fields)

    state = await run_in_threadpool(_write)
    return _lab_response(state)


@router.post(
    "/sessions/{session_id}/research/challenges/{challenge_id}/accept",
    response_model=RunAcceptedResponse,
    status_code=202,
)
async def accept_challenge(
    session_id: str,
    challenge_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
) -> RunAcceptedResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _prepare() -> str:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        require_frozen(lab)
        challenge = lab.get("next_challenge") or {}
        if challenge.get("id") != challenge_id:
            raise HTTPException(status_code=404, detail="challenge not found")
        proposed = challenge.get("proposed_specification_change") or {}
        spec_id = proposed.get("spec_id")
        if not spec_id:
            raise HTTPException(status_code=409, detail="challenge has no proposed specification")
        definition_by_id(lab, spec_id)
        return str(spec_id)

    spec_id = await run_in_threadpool(_prepare)
    return await _enqueue_spec_run(
        session_id,
        spec_ids=[spec_id],
        relation="preview",
        idempotency_key=idempotency_key,
        challenge_id=challenge_id,
    )


@router.post(
    "/sessions/{session_id}/research/claims/draft",
    response_model=ResearchLabResponse,
)
async def draft_research_claim(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResearchLabResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _write() -> dict:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        updated = draft_card_claim(lab)
        chapters = mark_results_chapters_stale(list(state.get("body_chapters") or []))
        return facade.update_state(session_id, research_lab=updated, body_chapters=chapters)

    state = await run_in_threadpool(_write)
    return _lab_response(state)


@router.post(
    "/sessions/{session_id}/research/claims/{claim_id}/approve",
    response_model=ResearchLabResponse,
)
async def approve_research_claim(
    session_id: str,
    claim_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResearchLabResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _write() -> dict:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        updated = approve_card_claim(lab, claim_id)
        return facade.update_state(session_id, research_lab=updated)

    state = await run_in_threadpool(_write)
    return _lab_response(state)


@router.post(
    "/sessions/{session_id}/research/prepare-paper",
    response_model=ResearchLabResponse,
)
async def prepare_research_paper(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> ResearchLabResponse:
    await run_in_threadpool(require_session_ownership, session_id, current_user)

    def _write() -> dict:
        state = facade.get_state(session_id)
        lab = require_lab(state)
        prepared = prepare_card_paper_state(state, lab)
        facade.save_state(session_id, prepared)
        return prepared

    state = await run_in_threadpool(_write)
    return _lab_response(state)

"""Development-visible Frame 5 paper draft and claim-evidence endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from auth import get_optional_user, require_session_ownership
from models.user import User
from schemas.responses import PaperClaimEvidenceResponse, PaperDraftResponse
from services.paper_draft import build_paper_draft, get_claim_evidence


router = APIRouter()


@router.post(
    "/sessions/{session_id}/paper-draft",
    response_model=PaperDraftResponse,
)
async def generate_paper_draft_endpoint(
    session_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> PaperDraftResponse:
    """Build the formal short draft on an atomic Facade state copy."""
    require_session_ownership(session_id, current_user)
    return PaperDraftResponse.model_validate(build_paper_draft(session_id))


@router.get(
    "/sessions/{session_id}/paper-draft/claims/{claim_id}",
    response_model=PaperClaimEvidenceResponse,
)
async def get_paper_claim_evidence_endpoint(
    session_id: str,
    claim_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
) -> PaperClaimEvidenceResponse:
    """Read the claim evidence directly from the canonical Facade state."""
    require_session_ownership(session_id, current_user)
    try:
        payload = get_claim_evidence(session_id, claim_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Paper claim not found") from exc
    return PaperClaimEvidenceResponse.model_validate(payload)

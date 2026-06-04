"""/api/design endpoint."""
from pathlib import Path

from fastapi import APIRouter, HTTPException

from Product.backend.wrapper.design_service import run_design
from Product.types.research import DesignRequest, DesignResponse

router = APIRouter()

_TASKS_ROOT = Path(__file__).resolve().parents[2] / "Tasks"


@router.post("/api/design", response_model=DesignResponse)
def post_design(req: DesignRequest) -> DesignResponse:
    try:
        return run_design(req, _TASKS_ROOT)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"design failed: {exc}") from exc

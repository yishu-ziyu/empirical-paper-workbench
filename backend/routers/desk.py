"""空桌讨论：把乱想法收成一个研究问题。"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from facade import facade

router = APIRouter()


class DeskTurn(BaseModel):
    question: str = ""
    answer: str = ""
    id: str = ""


class DeskDiscussRequest(BaseModel):
    notes: str = ""
    turns: List[DeskTurn] = Field(default_factory=list)


class DeskOption(BaseModel):
    id: str
    label: str


class DeskDiscussResponse(BaseModel):
    reflection: str
    title: str
    heard: List[str] = Field(default_factory=list)
    comparison: str
    outcome: str
    question: str = ""
    options: List[DeskOption] = Field(default_factory=list)
    explain: str = ""
    ready: bool = False
    source: str = "heuristic"


@router.post("/desk/discuss", response_model=DeskDiscussResponse)
async def discuss_desk(body: DeskDiscussRequest) -> DeskDiscussResponse:
    result = facade.discuss_desk(
        body.notes,
        [item.model_dump() for item in body.turns],
    )
    return DeskDiscussResponse(
        reflection=result.get("reflection") or "",
        title=result.get("title") or "",
        heard=list(result.get("heard") or []),
        comparison=result.get("comparison") or "还没定",
        outcome=result.get("outcome") or "还没定",
        question=result.get("question") or "",
        explain=result.get("explain") or "",
        options=[
            DeskOption(id=str(item.get("id")), label=str(item.get("label")))
            for item in (result.get("options") or [])
            if isinstance(item, dict) and item.get("label")
        ],
        ready=bool(result.get("ready")),
        source=str(result.get("source") or "heuristic"),
    )


class DeskSpeakRequest(BaseModel):
    text: str = ""


@router.post("/desk/transcribe")
async def transcribe_desk(file: UploadFile = File(...)) -> dict:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty audio")
    try:
        return facade.transcribe_desk(raw, filename=file.filename or "clip.webm")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/desk/speak")
async def speak_desk(body: DeskSpeakRequest) -> Response:
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="empty text")
    try:
        audio = facade.speak_desk(body.text)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return Response(content=audio, media_type="audio/mpeg")

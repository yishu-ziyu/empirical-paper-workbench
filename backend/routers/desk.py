"""空桌讨论：把乱想法收成一个研究问题。"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from auth import get_optional_user, require_auth_unless_debug
from facade import facade
from models.user import User

router = APIRouter()

_MAX_TRANSCRIBE_BYTES = 25 * 1024 * 1024  # 25MB


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


class DeskChatTurn(BaseModel):
    role: str = "user"
    text: str = ""
    id: str = ""


class DeskDesignChatRequest(BaseModel):
    notes: str = ""
    turns: List[DeskChatTurn] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)


class DeskDesignChatResponse(BaseModel):
    reply: str
    design: dict
    need: str = ""
    ready: bool = False
    source: str = "heuristic"


class DeskDiscussResponse(BaseModel):
    intent: str = "research"
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
async def discuss_desk(
    body: DeskDiscussRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> DeskDiscussResponse:
    require_auth_unless_debug(current_user)
    result = facade.discuss_desk(
        body.notes,
        [item.model_dump() for item in body.turns],
    )
    return DeskDiscussResponse(
        intent=str(result.get("intent") or "research"),
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


@router.post("/desk/design-chat", response_model=DeskDesignChatResponse)
async def desk_design_chat(
    body: DeskDesignChatRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> DeskDesignChatResponse:
    """设计对话：把念头聊成研究设定卡（dv/iv/controls/method 逐轮抽齐）。

    与 /desk/discuss 同属会话前的对话阶段，不要求登录（不触任何用户数据）。
    """
    if not body.notes.strip() and not body.turns:
        raise HTTPException(status_code=400, detail="empty notes")
    try:
        result = facade.design_chat_desk(
            body.notes,
            [t.model_dump() for t in body.turns],
            body.columns,
        )
    except HTTPException:
        raise
    except Exception as exc:  # LLM 通道挂了且处于必须解释的追问态
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return DeskDesignChatResponse(**result)


@router.post("/desk/transcribe")
async def transcribe_desk(
    request: Request,
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_user),
) -> dict:
    require_auth_unless_debug(current_user)
    raw_len = request.headers.get("content-length")
    if raw_len:
        try:
            if int(raw_len) > _MAX_TRANSCRIBE_BYTES:
                raise HTTPException(
                    status_code=413, detail="Audio exceeds 25MB upload limit"
                )
        except ValueError:
            pass
    raw = await file.read()
    if len(raw) > _MAX_TRANSCRIBE_BYTES:
        raise HTTPException(status_code=413, detail="Audio exceeds 25MB upload limit")
    if not raw:
        raise HTTPException(status_code=400, detail="empty audio")
    try:
        return facade.transcribe_desk(raw, filename=file.filename or "clip.webm")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/desk/speak")
async def speak_desk(
    body: DeskSpeakRequest,
    current_user: Optional[User] = Depends(get_optional_user),
) -> Response:
    require_auth_unless_debug(current_user)
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="empty text")
    try:
        audio = facade.speak_desk(body.text)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return Response(content=audio, media_type="audio/mpeg")

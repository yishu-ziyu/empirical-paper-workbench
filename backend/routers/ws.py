"""WebSocket endpoint for streaming graph output to the frontend.

T-02 implements "fake streaming": the graph has already run synchronously
during /upload, so this endpoint pushes the stored chapters' content as
streaming_chunk frames. True token-level streaming arrives in a later ticket.

Message ordering contract: the test drain helper breaks on the first
``status == "done"`` frame, so all streaming_chunk frames MUST be sent
before any ``done`` status.
"""
from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_user_from_token, require_session_ownership
from database import get_db
from facade import facade
from models.user import User

router = APIRouter()


def _token_from_websocket(ws: WebSocket) -> Optional[str]:
    """Read a JWT from ``?token=`` or the first WebSocket subprotocol."""
    token = ws.query_params.get("token")
    if token:
        return token
    header = ws.headers.get("sec-websocket-protocol")
    if not header:
        return None
    parts = [p.strip() for p in header.split(",") if p.strip()]
    if not parts:
        return None
    if parts[0].lower() == "bearer" and len(parts) > 1:
        return parts[1]
    return parts[0]


@router.websocket("/sessions/{session_id}/stream")
async def stream(
    ws: WebSocket, session_id: str, db: AsyncSession = Depends(get_db)
):
    """Stream status + chapter chunks for a session over WebSocket.

    Timing contract: the graph runs to completion synchronously inside
    POST /upload before this WS endpoint is ever reached, so the state
    read here is already final — there is no risk of pushing a partial
    final state while the graph is still running.

    TODO (later ticket): when true token-level streaming lands and this
    endpoint switches to graph.stream(), each node step MUST be yielded
    and pushed incrementally (not as a single final dump), and the graph
    call must stay inside the try/except below so failures push an
    ``error`` frame instead of crashing the socket.
    """
    requested = []
    header = ws.headers.get("sec-websocket-protocol")
    if header:
        requested = [p.strip() for p in header.split(",") if p.strip()]
    if requested:
        await ws.accept(subprotocol=requested[0])
    else:
        await ws.accept()
    try:
        token = _token_from_websocket(ws)
        user: Optional[User] = None
        try:
            user = await get_user_from_token(token, db)
            require_session_ownership(session_id, user)
        except HTTPException as exc:
            await ws.send_json({"type": "error", "message": exc.detail})
            return

        state = facade.get_state(session_id)

        title_chapter = state.get("title_chapter") or {}
        title_content = title_chapter.get("content") or ""

        body_chapters = state.get("body_chapters", []) or []
        resumed = state.get("resumed", False)

        # 1. Push "running" status frames for each node.
        await ws.send_json(
            {"type": "status", "node": "upload_data", "status": "running"}
        )
        await ws.send_json(
            {"type": "status", "node": "clean_data", "status": "running"}
        )
        await ws.send_json(
            {"type": "status", "node": "generate_title", "status": "running"}
        )

        # 2. Stream the title chapter content as chunks.
        if title_content:
            chunk_size = 5
            for i in range(0, len(title_content), chunk_size):
                chunk = title_content[i : i + chunk_size]
                await ws.send_json(
                    {
                        "type": "streaming_chunk",
                        "chapter_id": "title",
                        "chunk": chunk,
                    }
                )
                await asyncio.sleep(0.01)

        if resumed:
            # 3a. User already confirmed via HITL → stream chapters.
            has_chapters = any(
                isinstance(ch, dict) and ch.get("content")
                for ch in body_chapters
            )
            if has_chapters:
                await ws.send_json(
                    {"type": "status", "node": "generate_outline", "status": "running"}
                )
                await asyncio.sleep(0.02)
                await ws.send_json(
                    {"type": "status", "node": "generate_outline", "status": "done"}
                )

                for idx, ch in enumerate(body_chapters):
                    if not isinstance(ch, dict):
                        continue
                    chapter_type = ch.get("type", f"chapter_{idx}")
                    chapter_content = ch.get("content", "")
                    if not chapter_content:
                        continue

                    await ws.send_json(
                        {
                            "type": "status",
                            "node": "generate_chapter",
                            "status": "running",
                        }
                    )

                    chunk_size = 5
                    for i in range(0, len(chapter_content), chunk_size):
                        chunk = chapter_content[i : i + chunk_size]
                        await ws.send_json(
                            {
                                "type": "streaming_chunk",
                                "chapter_id": chapter_type,
                                "chunk": chunk,
                            }
                        )
                        await asyncio.sleep(0.01)

                    await ws.send_json(
                        {
                            "type": "status",
                            "node": "generate_chapter",
                            "status": "done",
                        }
                    )

                await ws.send_json(
                    {"type": "status", "node": "export_docx", "status": "done"}
                )
            else:
                await ws.send_json(
                    {"type": "status", "node": "generate_title", "status": "done"}
                )
        else:
            # 3b. First connection → send interrupt (HITL pause).
            await ws.send_json(
                {"type": "status", "node": "generate_title", "status": "done"}
            )
            await ws.send_json(
                {
                    "type": "interrupt",
                    "chapter_id": "title",
                    "content": title_content,
                }
            )
    except Exception as exc:  # pragma: no cover - defensive
        try:
            await ws.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        # Keep the WebSocket alive until the client disconnects.
        # This prevents the frontend from immediately showing "disconnected"
        # before it has processed all streamed messages.
        try:
            while True:
                await ws.receive_text()
        except Exception:
            pass
        try:
            await ws.close()
        except Exception:
            pass

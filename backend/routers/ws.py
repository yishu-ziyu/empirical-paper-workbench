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

from fastapi import APIRouter, WebSocket

from facade import facade

router = APIRouter()


@router.websocket("/sessions/{session_id}/stream")
async def stream(ws: WebSocket, session_id: str):
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
    await ws.accept()
    try:
        if not facade.has_session(session_id):
            await ws.send_json(
                {"type": "error", "message": "Session not found"}
            )
            return

        state = facade.get_state(session_id)

        title_chapter = state.get("title_chapter") or {}
        title_content = title_chapter.get("content") or ""

        # 1. Push "running" status frames for each node (no "done" yet — the
        #    client drain helper breaks on the first done).
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

        # 3. Push the final "done" status (triggers the client drain to stop).
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
        await ws.send_json({"type": "error", "message": str(exc)})
    finally:
        await ws.close()

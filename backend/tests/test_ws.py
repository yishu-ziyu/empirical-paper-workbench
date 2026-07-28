"""Contract tests for WS /sessions/{id}/stream (T-02 red stage).

Pins the WS message schema from spec §12-§14:
- status: {type:"status", node, status:"running"|"paused"|"done"}
- streaming_chunk: {type:"streaming_chunk", chapter_id, chunk}

Uses Starlette TestClient's websocket_connect (backed by the installed
`websockets` library). In the red stage the WS endpoint does not exist,
so the connection is rejected and the drain helper returns an empty list;
every test then fails on the "received at least one matching frame"
assertion.
"""


def _drain_ws(client, session_id, max_messages=20):
    """Connect to /sessions/{id}/stream and collect up to max_messages JSON frames.

    Returns the list of received messages. On any connection error (e.g.
    endpoint missing during the red stage, or the server closing the
    socket), returns an empty list so callers fail on an assertion rather
    than the test erroring out.
    """
    messages = []
    try:
        with client.websocket_connect(f"/sessions/{session_id}/stream") as ws:
            for _ in range(max_messages):
                msg = ws.receive_json()
                messages.append(msg)
                # Stop once the graph signals completion.
                if msg.get("type") == "status" and msg.get("status") == "done":
                    break
    except Exception:
        return []
    return messages


def test_ws_streams_status_messages(uploaded_session, client):
    """WS /sessions/{id}/stream pushes status (running/done) messages."""
    messages = _drain_ws(client, uploaded_session)
    status_msgs = [m for m in messages if m.get("type") == "status"]
    assert len(status_msgs) > 0, "no status messages streamed over WS"
    statuses = {m.get("status") for m in status_msgs}
    assert "running" in statuses or "done" in statuses, (
        f"expected running/done status, got {statuses}"
    )


def test_ws_streams_title_chunks(uploaded_session, client, mock_llm_for):
    """WS streams generate_title tokens as streaming_chunk frames."""
    mock_llm_for("generate_title", return_value="Mocked Title")
    messages = _drain_ws(client, uploaded_session)
    chunks = [m for m in messages if m.get("type") == "streaming_chunk"]
    assert len(chunks) > 0, "no streaming_chunk frames received over WS"
    assembled = "".join(m.get("chunk", "") for m in chunks)
    assert "\\title{" in assembled, (
        f"streamed chunks did not assemble into a \\title{{...}}: {assembled!r}"
    )

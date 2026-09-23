"""Legacy WS compatibility tests while production progress uses SSE.

Pins the WS message schema from spec §12-§14:
- status: {type:"status", node, status:"running"|"paused"|"done"}
- streaming_chunk: {type:"streaming_chunk", chapter_id, chunk}

Uses Starlette TestClient's websocket_connect (backed by the installed
`websockets` library). In the red stage the WS endpoint does not exist,
so the connection is rejected and the drain helper returns an empty list;
every test then fails on the "received at least one matching frame"
assertion.
"""

import asyncio

from facade import facade
from runner import process_one_run
from .confirmation_helpers import observed, confirm_seen_attach


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
    # FORMAL-CONFIRMATION-CHAIN-1：upload-era 会话须先确认挂接，/direction 才受理。
    attached = confirm_seen_attach(client, uploaded_session)
    assert attached.status_code == 200, attached.text
    # FORMAL-CONFIRMATION-CHAIN-2 R1：正式会话还须有已确认设计，方向才可入队。
    facade.update_state(
        uploaded_session,
        design={
            "status": "confirmed",
            "confirmed": True,
            "proposed_at": "2026-09-17T00:00:00Z",
            "confirmed_at": "2026-09-17T00:05:00Z",
            "method": "ols",
            "outcome": "income",
            "treatment": "age",
            "controls": [],
        },
    )
    # PREWRITE-PAUSE：/direction 现在只跑到 identification_verify 就停（Table 1 +
    # 方程要先确认），generate_title 在 prewrite/confirm 之后的 estimate 臂里才跑。
    # 所以这里按产品真实路径走两段：设方向 → 确认 → 跑完预写，再开 WS 才有标题可流。
    direction = client.post(
        f"/sessions/{uploaded_session}/direction",
        headers={"Idempotency-Key": "ws-direction"},
        json={
            **observed(client, uploaded_session),
            "question": "年龄与收入",
            "dv": "income",
            "iv": "age",
            "controls": [],
            "method": "OLS",
            "template": "cn_journal",
        },
    )
    assert direction.status_code == 202, (
        f"set direction failed: {direction.status_code}: {direction.text}"
    )
    run_id = direction.json()["run_id"]
    assert asyncio.run(process_one_run(owner="ws-test", run_id=run_id)) is True

    confirmed = client.post(
        f"/sessions/{uploaded_session}/prewrite/confirm",
        headers={"Idempotency-Key": "ws-record-t1"},
        json={"action": "record_confirms", "table1Confirmed": True, **observed(client, uploaded_session)},
    )
    assert confirmed.status_code == 200, (
        f"table1 confirm failed: {confirmed.status_code}: {confirmed.text}"
    )
    confirmed = client.post(
        f"/sessions/{uploaded_session}/prewrite/confirm",
        headers={"Idempotency-Key": "ws-record-spec"},
        json={"action": "record_confirms", "specConfirmed": True, **observed(client, uploaded_session)},
    )
    assert confirmed.status_code == 200, (
        f"spec confirm failed: {confirmed.status_code}: {confirmed.text}"
    )
    confirmed = client.post(
        f"/sessions/{uploaded_session}/prewrite/confirm",
        headers={"Idempotency-Key": "ws-confirm"},
        json={"action": "continue_estimate", **observed(client, uploaded_session)},
    )
    assert confirmed.status_code == 202, (
        f"prewrite confirm failed: {confirmed.status_code}: {confirmed.text}"
    )
    confirm_run_id = confirmed.json()["run_id"]
    assert (
        asyncio.run(process_one_run(owner="ws-test", run_id=confirm_run_id)) is True
    )
    assert client.get(f"/runs/{confirm_run_id}").json()["status"] == "SUCCEEDED"
    messages = _drain_ws(client, uploaded_session)
    chunks = [m for m in messages if m.get("type") == "streaming_chunk"]
    assert len(chunks) > 0, "no streaming_chunk frames received over WS"
    assembled = "".join(m.get("chunk", "") for m in chunks)
    assert "\\title{" in assembled, (
        f"streamed chunks did not assemble into a \\title{{...}}: {assembled!r}"
    )

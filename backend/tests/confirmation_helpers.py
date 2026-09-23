"""Positive-path clients explicitly read the target before approving it.

No autouse interception: missing/stale-target tests send their raw requests.
"""


def observed(client, session_id):
    snapshot = client.get(f"/sessions/{session_id}")
    assert snapshot.status_code == 200, snapshot.text
    return {"expectedTarget": snapshot.json()["confirmation_targets"]}


def confirm_seen_design(client, session_id):
    snapshot = client.get(f"/sessions/{session_id}").json()
    revision = (snapshot.get("design") or {}).get("revision")
    return client.post(f"/sessions/{session_id}/design/confirm",
                       json={"expectedRevision": revision})


def confirm_seen_attach(client, session_id):
    return client.post(f"/sessions/{session_id}/confirm-attach",
                       json=observed(client, session_id))

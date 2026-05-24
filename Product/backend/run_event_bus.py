"""Run event bus -- bridges sync orchestrator with async SSE."""
from __future__ import annotations

import queue
import threading
import uuid
from datetime import datetime, timezone

# Global registry: run_id -> Queue
_RUN_QUEUES: dict[str, queue.Queue] = {}
_LOCK = threading.Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_queue(run_id: str) -> queue.Queue:
    """Get or create a Queue for the given run_id."""
    with _LOCK:
        if run_id not in _RUN_QUEUES:
            _RUN_QUEUES[run_id] = queue.Queue(maxsize=1000)
        return _RUN_QUEUES[run_id]


def drop_queue(run_id: str) -> None:
    """Remove a Queue after the run is finished."""
    with _LOCK:
        _RUN_QUEUES.pop(run_id, None)


def emit_event(
    run_id: str,
    event_type: str,
    stage: str = "",
    agent_name: str = "",
    payload: dict | None = None,
) -> None:
    """Emit an event to the run's queue. Called from sync orchestrator code."""
    q = ensure_queue(run_id)
    event = {
        "event_id": f"evt_{uuid.uuid4().hex[:8]}",
        "run_id": run_id,
        "timestamp": _utc_now(),
        "type": event_type,
        "stage": stage,
        "agent_name": agent_name,
        "payload": payload or {},
    }
    try:
        q.put_nowait(event)
    except queue.Full:
        try:
            q.get_nowait()
            q.put_nowait(event)
        except queue.Empty:
            pass


def get_queue(run_id: str) -> queue.Queue | None:
    """Get the queue for a run_id, or None if not found."""
    with _LOCK:
        return _RUN_QUEUES.get(run_id)


def list_active_runs() -> list[str]:
    """Return all run_ids that currently have active queues."""
    with _LOCK:
        return list(_RUN_QUEUES.keys())

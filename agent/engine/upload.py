"""Pure upload parsing and cleaning execution.

This module intentionally has no SessionStore or run-persistence dependency.
Durable workers provide an immutable state snapshot and publish the returned
state only after they still own the Run lease.
"""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from agent.nodes.clean_data import clean_data
from agent.nodes.upload_data import upload_data

from .cancellation import cancellation_scope, raise_if_cancelled

ProgressCallback = Callable[[str, str, dict[str, Any]], None]


def run_upload(
    initial_state: dict,
    progress: ProgressCallback | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> dict:
    """Apply the existing ``upload_data -> clean_data`` semantics to a snapshot."""
    state = deepcopy(initial_state)
    with cancellation_scope(should_cancel):
        for node_id, node in (
            ("upload_data", upload_data),
            ("clean_data", clean_data),
        ):
            raise_if_cancelled()
            if progress:
                progress(node_id, "started", {})
            state = {**state, **node(state)}
            raise_if_cancelled()
            if progress:
                progress(node_id, "completed", {})
    return state

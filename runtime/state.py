#!/usr/bin/env python3
"""Workflow state persistence for the empirical paper runtime."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "artifacts" / "pipeline_state.json"


class PipelineState:
    """Persist and query the pipeline's current position and history."""

    def __init__(self) -> None:
        self._state: dict[str, Any] = {}
        self.load()

    # ── persistence ──────────────────────────────────────────────

    def load(self) -> dict[str, Any]:
        if STATE_PATH.exists():
            self._state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        else:
            self._state = self._default()
        return self._state

    def save(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    # ── helpers ──────────────────────────────────────────────────

    @staticmethod
    def _default() -> dict[str, Any]:
        return {
            "version": "0.1",
            "status": "idle",          # idle | running | blocked | done | stopped
            "current_step": None,
            "current_step_index": -1,
            "history": [],
            "failed_count": 0,
            "created_at": _now(),
            "updated_at": _now(),
        }

    # ── query ────────────────────────────────────────────────────

    @property
    def current_step(self) -> str | None:
        return self._state.get("current_step")

    @property
    def current_step_index(self) -> int:
        return self._state.get("current_step_index", -1)

    @property
    def status(self) -> str:
        return self._state.get("status", "idle")

    @property
    def history(self) -> list[dict]:
        return self._state.get("history", [])

    @property
    def failed_count(self) -> int:
        return self._state.get("failed_count", 0)

    # ── mutation ─────────────────────────────────────────────────

    def set_running(self, step_id: str, index: int) -> None:
        self._state["status"] = "running"
        self._state["current_step"] = step_id
        self._state["current_step_index"] = index
        self._state["updated_at"] = _now()

    def set_blocked(self, step_id: str, reason: str) -> None:
        self._state["status"] = "blocked"
        self._state["current_step"] = step_id
        self._state["updated_at"] = _now()
        self._append_history(step_id, "blocked", reason)

    def set_done(self, step_id: str) -> None:
        self._state["status"] = "running"
        self._state["updated_at"] = _now()
        self._append_history(step_id, "done", "")

    def set_stopped(self, reason: str = "") -> None:
        self._state["status"] = "stopped"
        self._state["updated_at"] = _now()
        if self.current_step:
            self._append_history(self.current_step, "stopped", reason)

    def increment_failures(self) -> None:
        self._state["failed_count"] = self._state.get("failed_count", 0) + 1
        self._state["updated_at"] = _now()

    # ── internals ────────────────────────────────────────────────

    def _append_history(self, step_id: str, result: str, note: str) -> None:
        self._state.setdefault("history", []).append({
            "step_id": step_id,
            "result": result,
            "note": note,
            "timestamp": _now(),
        })

    def to_dict(self) -> dict[str, Any]:
        return dict(self._state)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

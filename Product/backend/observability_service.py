from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def observable_root(project_root: Path, run_id: str) -> Path:
    return project_root / "state" / "runs" / run_id


def load_observable_manifest(project_root: Path, run_id: str) -> dict[str, Any]:
    return _load_json(observable_root(project_root, run_id) / "run_manifest.json", run_id)


def load_observable_steps(project_root: Path, run_id: str) -> dict[str, Any]:
    return _load_json(observable_root(project_root, run_id) / "run_steps.json", run_id)


def load_observable_gates(project_root: Path, run_id: str) -> dict[str, Any]:
    return _load_json(observable_root(project_root, run_id) / "gates.json", run_id)


def load_observable_events(project_root: Path, run_id: str) -> dict[str, Any]:
    path = observable_root(project_root, run_id) / "run_events.jsonl"
    if not path.exists():
        raise KeyError(run_id)
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {
        "_meta": {"evidence_level": "local_execution"},
        "run_id": run_id,
        "items": events,
    }


def load_run_observability(project_root: Path, run_id: str) -> dict[str, Any]:
    return {
        "_meta": {"evidence_level": "local_execution"},
        "run_id": run_id,
        "manifest": load_observable_manifest(project_root, run_id),
        "steps": load_observable_steps(project_root, run_id),
        "events": load_observable_events(project_root, run_id),
        "gates": load_observable_gates(project_root, run_id),
    }


def _load_json(path: Path, run_id: str) -> dict[str, Any]:
    if not path.exists():
        raise KeyError(run_id)
    return json.loads(path.read_text(encoding="utf-8"))

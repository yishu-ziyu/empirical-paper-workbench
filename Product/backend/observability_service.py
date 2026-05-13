from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_GATE_ACTIONS = {"confirm", "reject", "adjust"}


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
    manifest = load_observable_manifest(project_root, run_id)
    steps = load_observable_steps(project_root, run_id)
    gates = load_observable_gates(project_root, run_id)
    return {
        "_meta": {"evidence_level": "local_execution"},
        "run_id": run_id,
        "dataset_source": manifest.get("dataset_source"),
        "variable_roles": build_variable_roles(steps, gates),
        "manifest": manifest,
        "steps": steps,
        "events": load_observable_events(project_root, run_id),
        "gates": gates,
    }


def build_variable_roles(steps: dict[str, Any], gates: dict[str, Any]) -> dict[str, Any] | None:
    dataset_step = next((step for step in steps.get("items", []) if step.get("id") == "dataset_intake"), None)
    roles = (dataset_step or {}).get("metadata", {}).get("key_variables")
    if not roles:
        return None

    gate = next((item for item in gates.get("items", []) if item.get("id") == "gate_dataset_fields"), None)
    return {
        "evidence_level": "local_execution",
        "source_step_id": "dataset_intake",
        "roles": {
            "outcome": roles.get("outcome", []),
            "treatment": roles.get("treatment", []),
            "controls": roles.get("controls", []),
            "instruments": roles.get("instruments", []),
        },
        "confirmation_gate_id": gate.get("id") if gate else None,
        "confirmation_status": gate.get("status") if gate else "missing",
    }


def resolve_observable_gate(project_root: Path, run_id: str, gate_id: str, action: str, note: str = "") -> dict[str, Any]:
    if action not in VALID_GATE_ACTIONS:
        raise ValueError(action)

    root = observable_root(project_root, run_id)
    manifest_path = root / "run_manifest.json"
    gates_path = root / "gates.json"
    events_path = root / "run_events.jsonl"
    manifest = _load_json(manifest_path, run_id)
    gates = _load_json(gates_path, run_id)
    if not events_path.exists():
        raise KeyError(run_id)

    gate = next((item for item in gates.get("items", []) if item.get("id") == gate_id), None)
    if gate is None:
        raise KeyError(gate_id)

    now = _utc_timestamp()
    gate["status"] = "resolved"
    gate["resolved_at"] = now
    gate["resolution"] = {
        "action": action,
        "note": note,
        "resolved_at": now,
    }
    _write_json(gates_path, gates)

    open_count = sum(1 for item in gates.get("items", []) if item.get("status") == "open")
    manifest.setdefault("human_in_loop", {})
    manifest["human_in_loop"]["open_gate_count"] = open_count
    manifest["human_in_loop"]["gates_path"] = manifest["human_in_loop"].get("gates_path") or _relative(project_root, gates_path)
    _write_json(manifest_path, manifest)

    event = {
        "sequence": _next_event_sequence(events_path),
        "timestamp": now,
        "run_id": run_id,
        "type": "hitl_gate_resolved",
        "step_id": gate.get("step_id"),
        "actor": "HumanReviewer",
        "message": f"HITL gate {gate_id} resolved with action={action}.",
        "evidence_level": "local_execution",
        "metadata": {
            "gate_id": gate_id,
            "action": action,
            "note": note,
        },
    }
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    return {
        "_meta": {"evidence_level": "local_execution"},
        "run_id": run_id,
        "gate": gate,
        "manifest": manifest,
        "event": event,
    }


def _load_json(path: Path, run_id: str) -> dict[str, Any]:
    if not path.exists():
        raise KeyError(run_id)
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _next_event_sequence(events_path: Path) -> int:
    lines = [line for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return 1
    last_event = json.loads(lines[-1])
    return int(last_event.get("sequence", 0)) + 1


def _relative(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)

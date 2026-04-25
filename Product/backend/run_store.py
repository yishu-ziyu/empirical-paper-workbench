from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def runs_root(project_root: Path) -> Path:
    return project_root / "state" / "runs"


def ensure_runs_root(project_root: Path) -> Path:
    root = runs_root(project_root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def index_path(project_root: Path) -> Path:
    return ensure_runs_root(project_root) / "index.json"


def load_index(project_root: Path) -> dict[str, Any]:
    path = index_path(project_root)
    if not path.exists():
        return {"items": []}
    return json.loads(path.read_text(encoding="utf-8"))


def write_index(project_root: Path, payload: dict[str, Any]) -> None:
    path = index_path(project_root)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def create_run(project_root: Path, project_id: str, mode: str) -> dict[str, Any]:
    run = {
        "id": f"run_{uuid.uuid4().hex[:12]}",
        "project_id": project_id,
        "mode": mode,
        "status": "queued",
        "started_at": utc_now(),
        "finished_at": None,
        "state_path": None,
        "results_index_path": None,
        "artifact_count": 0,
        "artifact_paths": [],
        "state": None,
        "results": None,
        "error": None,
    }
    save_run(project_root, run)
    return run


def run_path(project_root: Path, run_id: str) -> Path:
    return ensure_runs_root(project_root) / f"{run_id}.json"


def save_run(project_root: Path, run: dict[str, Any]) -> None:
    run_path(project_root, run["id"]).write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
    payload = load_index(project_root)
    payload["items"] = [item for item in payload["items"] if item["id"] != run["id"]]
    payload["items"].append(summarize_run(run))
    write_index(project_root, payload)


def summarize_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": run["id"],
        "project_id": run["project_id"],
        "mode": run["mode"],
        "status": run["status"],
        "started_at": run["started_at"],
        "finished_at": run["finished_at"],
        "state_path": run["state_path"],
        "results_index_path": run["results_index_path"],
        "artifact_count": run["artifact_count"],
        "error": run["error"],
    }


def get_run(project_root: Path, run_id: str) -> dict[str, Any]:
    path = run_path(project_root, run_id)
    if not path.exists():
        raise KeyError(run_id)
    return json.loads(path.read_text(encoding="utf-8"))


def list_runs(project_root: Path) -> list[dict[str, Any]]:
    return load_index(project_root)["items"]

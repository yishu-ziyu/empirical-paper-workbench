from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id_or_transient


COST_EVENTS_PATH = Path("state/product/cost_events.jsonl")
COST_SUMMARY_PATH = Path("state/product/cost_summary.json")


def cost_events_path(project_root: Path) -> Path:
    return project_root / COST_EVENTS_PATH


def cost_summary_path(project_root: Path) -> Path:
    return project_root / COST_SUMMARY_PATH


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _update_summary(project_root: Path) -> dict[str, Any]:
    events = _read_jsonl(cost_events_path(project_root))
    total_wall_seconds = 0.0
    total_estimated_usd = 0.0
    succeeded_count = 0
    failed_count = 0
    pending_count = 0
    capability_counts: dict[str, int] = {}
    actor_counts: dict[str, int] = {}

    for event in events:
        status = event.get("status", "pending")
        if status == "succeeded":
            succeeded_count += 1
        elif status == "failed":
            failed_count += 1
        else:
            pending_count += 1
        total_wall_seconds += event.get("wall_seconds", 0.0)
        total_estimated_usd += event.get("estimated_usd", 0.0)
        cap_id = event.get("capability_id", "unknown")
        capability_counts[cap_id] = capability_counts.get(cap_id, 0) + 1
        actor_id = event.get("actor_id", "unknown")
        actor_counts[actor_id] = actor_counts.get(actor_id, 0) + 1

    summary = {
        "id": "cost_summary",
        "version": 1,
        "evidence_level": "local_file",
        "updated_at": utc_now(),
        "total_events": len(events),
        "total_wall_seconds": round(total_wall_seconds, 2),
        "total_estimated_usd": round(total_estimated_usd, 4),
        "status_counts": {
            "succeeded": succeeded_count,
            "failed": failed_count,
            "pending": pending_count,
        },
        "capability_counts": capability_counts,
        "actor_counts": actor_counts,
    }
    path = cost_summary_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def start_cost_event(
    project_root: Path,
    project_id: str,
    workflow_id: str,
    task_id: str,
    actor_id: str,
    capability_id: str,
    event_type: str = "agent_task_run",
) -> str:
    event_id = f"cost_evt_{_next_event_number(project_root)}"
    record = {
        "event_id": event_id,
        "project_id": project_id,
        "workflow_id": workflow_id,
        "task_id": task_id,
        "actor_id": actor_id,
        "capability_id": capability_id,
        "event_type": event_type,
        "started_at": utc_now(),
        "finished_at": "",
        "wall_seconds": 0.0,
        "provider": "",
        "model": "",
        "input_tokens": 0,
        "output_tokens": 0,
        "estimated_usd": 0.0,
        "status": "pending",
    }
    _append_jsonl(cost_events_path(project_root), record)
    return event_id


def _next_event_number(project_root: Path) -> int:
    events = _read_jsonl(cost_events_path(project_root))
    return len(events) + 1


def finish_cost_event(
    project_root: Path,
    event_id: str,
    status: str,
    wall_seconds: float = 0.0,
    provider: str = "",
    model: str = "",
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_usd: float = 0.0,
) -> dict[str, Any]:
    events = _read_jsonl(cost_events_path(project_root))
    for event in events:
        if event.get("event_id") == event_id:
            event["status"] = status
            event["finished_at"] = utc_now()
            event["wall_seconds"] = wall_seconds
            event["provider"] = provider
            event["model"] = model
            event["input_tokens"] = input_tokens
            event["output_tokens"] = output_tokens
            event["estimated_usd"] = estimated_usd
            break
    # Rewrite the entire file (JSONL doesn't support in-place edits)
    path = cost_events_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in events) + ("\n" if events else ""),
        encoding="utf-8",
    )
    summary = _update_summary(project_root)
    return {
        "event_id": event_id,
        "status": status,
        "summary": summary,
    }


def get_project_costs(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id_or_transient(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    events = _read_jsonl(cost_events_path(project_root))
    summary = _update_summary(project_root)
    return {
        "_meta": {
            "evidence_level": "local_file",
            "service": "cost_service",
            "generated_at": utc_now(),
        },
        "project": {
            "id": project["id"],
            "slug": project["slug"],
            "title": project["title"],
        },
        "costs": {
            "events": events,
            "summary": summary,
        },
    }


class CostServiceError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code

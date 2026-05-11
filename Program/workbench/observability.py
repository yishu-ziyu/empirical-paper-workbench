from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STEP_DEFINITIONS = [
    {
        "id": "config_load",
        "title": "Load project configuration",
        "actor": "Runtime",
        "description": "Read paper.yaml and analysis_config.yaml.",
    },
    {
        "id": "dataset_intake",
        "title": "Inspect analysis dataset",
        "actor": "DataAgent",
        "description": "Check whether the configured analysis dataset is available.",
    },
    {
        "id": "topic_confirmation",
        "title": "Confirm research question",
        "actor": "Supervisor",
        "description": "Expose the detected research question and candidate variable roles for user review.",
    },
    {
        "id": "analysis_execution",
        "title": "Execute empirical analysis",
        "actor": "ExecutionAgent",
        "description": "Run the configured empirical engine when live execution is allowed.",
    },
    {
        "id": "draft_generation",
        "title": "Generate research draft",
        "actor": "ManuscriptAgent",
        "description": "Write Markdown and LaTeX drafts from the current analysis context.",
    },
    {
        "id": "state_index",
        "title": "Persist state and index",
        "actor": "ArtifactsAgent",
        "description": "Write project state, result snapshots, and artifact index.",
    },
    {
        "id": "finalization",
        "title": "Finalize observable run",
        "actor": "Supervisor",
        "description": "Close the run and summarize HITL gates for the UI.",
    },
]


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run_{stamp}_{uuid.uuid4().hex[:8]}"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ObservableRun:
    def __init__(self, project_root: Path, run_id: str, mode: str) -> None:
        self.project_root = project_root
        self.run_id = run_id
        self.mode = mode
        self.run_root = project_root / "state" / "runs" / run_id
        self.manifest_path = self.run_root / "run_manifest.json"
        self.steps_path = self.run_root / "run_steps.json"
        self.events_path = self.run_root / "run_events.jsonl"
        self.gates_path = self.run_root / "gates.json"
        self.sequence = 0
        self.manifest: dict[str, Any] = {}
        self.steps: dict[str, Any] = {"items": []}
        self.gates: dict[str, Any] = {"items": []}

    def start_run(self) -> None:
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.events_path.write_text("", encoding="utf-8")
        self.steps = {
            "_meta": {"evidence_level": "local_execution"},
            "run_id": self.run_id,
            "items": [
                {
                    **definition,
                    "status": "queued",
                    "started_at": None,
                    "finished_at": None,
                    "summary": "",
                    "artifacts": [],
                    "metadata": {},
                }
                for definition in STEP_DEFINITIONS
            ],
        }
        self.gates = {
            "_meta": {"evidence_level": "local_execution"},
            "run_id": self.run_id,
            "items": [],
        }
        self.manifest = {
            "_meta": {"evidence_level": "local_execution"},
            "run_id": self.run_id,
            "mode": self.mode,
            "status": "running",
            "project_root": str(self.project_root),
            "started_at": utc_timestamp(),
            "finished_at": None,
            "paths": {
                "manifest": self._relative(self.manifest_path),
                "steps": self._relative(self.steps_path),
                "events": self._relative(self.events_path),
                "gates": self._relative(self.gates_path),
            },
            "human_in_loop": {
                "open_gate_count": 0,
                "gates_path": self._relative(self.gates_path),
            },
        }
        self._write_all()
        self.add_event("run_started", "finalization", "Supervisor", "Observable research run started.")

    def start_step(self, step_id: str, metadata: dict[str, Any] | None = None) -> None:
        step = self._step(step_id)
        step["status"] = "running"
        step["started_at"] = utc_timestamp()
        if metadata:
            step["metadata"].update(metadata)
        self._write_steps()
        self.add_event("step_started", step_id, step["actor"], f"{step['title']} started.", metadata or {})

    def complete_step(
        self,
        step_id: str,
        summary: str,
        artifacts: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        status: str = "completed",
    ) -> None:
        step = self._step(step_id)
        step["status"] = status
        step["finished_at"] = utc_timestamp()
        step["summary"] = summary
        if artifacts:
            step["artifacts"].extend(artifacts)
        if metadata:
            step["metadata"].update(metadata)
        self._write_steps()
        self.add_event(
            "step_completed" if status == "completed" else "step_skipped",
            step_id,
            step["actor"],
            summary,
            {"artifacts": artifacts or [], **(metadata or {})},
        )

    def artifact_written(self, step_id: str, path: Path, description: str) -> None:
        rel_path = self._relative(path)
        self.add_event(
            "artifact_written",
            step_id,
            self._step(step_id)["actor"],
            description,
            {"path": rel_path},
        )

    def open_gate(
        self,
        gate_id: str,
        step_id: str,
        title: str,
        reason: str,
        required_by: str,
        options: list[str],
        metadata: dict[str, Any] | None = None,
        blocking: bool = False,
    ) -> None:
        gate = {
            "id": gate_id,
            "run_id": self.run_id,
            "step_id": step_id,
            "title": title,
            "reason": reason,
            "status": "open",
            "blocking": blocking,
            "required_by": required_by,
            "options": options,
            "created_at": utc_timestamp(),
            "resolved_at": None,
            "metadata": metadata or {},
        }
        self.gates["items"].append(gate)
        self._write_gates()
        self._refresh_hitl_summary()
        self.add_event(
            "hitl_gate_opened",
            step_id,
            self._step(step_id)["actor"],
            title,
            {"gate_id": gate_id, "required_by": required_by, "blocking": blocking},
        )

    def succeed_run(self) -> None:
        self.manifest["status"] = "succeeded"
        self.manifest["finished_at"] = utc_timestamp()
        self._refresh_hitl_summary()
        self.add_event("run_succeeded", "finalization", "Supervisor", "Observable research run finished.")
        self._write_manifest()

    def fail_run(self, message: str) -> None:
        now = utc_timestamp()
        for step in self.steps["items"]:
            if step["status"] == "running":
                step["status"] = "failed"
                step["finished_at"] = now
                step["summary"] = message
        self.manifest["status"] = "failed"
        self.manifest["finished_at"] = now
        self.manifest["error"] = {"message": message}
        self._write_steps()
        self.add_event("run_failed", "finalization", "Supervisor", message, {"error": message})
        self._write_manifest()

    def add_event(
        self,
        event_type: str,
        step_id: str,
        actor: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.sequence += 1
        event = {
            "sequence": self.sequence,
            "timestamp": utc_timestamp(),
            "run_id": self.run_id,
            "type": event_type,
            "step_id": step_id,
            "actor": actor,
            "message": message,
            "evidence_level": "local_execution",
            "metadata": metadata or {},
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _refresh_hitl_summary(self) -> None:
        open_count = len([gate for gate in self.gates["items"] if gate["status"] == "open"])
        self.manifest["human_in_loop"] = {
            "open_gate_count": open_count,
            "gates_path": self._relative(self.gates_path),
        }
        self._write_manifest()

    def _step(self, step_id: str) -> dict[str, Any]:
        for step in self.steps["items"]:
            if step["id"] == step_id:
                return step
        raise KeyError(step_id)

    def _relative(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.project_root))
        except ValueError:
            return str(path)

    def _write_all(self) -> None:
        self._write_manifest()
        self._write_steps()
        self._write_gates()

    def _write_manifest(self) -> None:
        write_json(self.manifest_path, self.manifest)

    def _write_steps(self) -> None:
        write_json(self.steps_path, self.steps)

    def _write_gates(self) -> None:
        write_json(self.gates_path, self.gates)

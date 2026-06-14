"""Shared helpers for the CLI subcommands."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from Product.backend.orchestrator import (  # noqa: E402
    CheckpointStatus,
    load_checkpoints,
    save_checkpoint,
    utc_now,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

# ── 7 canonical agent roles (workbench 7-agent loop) ───────────────────────
AGENT_ROLES = [
    "supervisor",
    "data",
    "design",
    "literature",
    "execution",
    "manuscript",
    "verifier",
]


# ── output helpers ─────────────────────────────────────────────────────────
def print_manifest(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


# ── checkpoint helpers ─────────────────────────────────────────────────────
def save_checkpoint_from_input(project_root: Path, stage: str, status_str: str, note: str = "") -> None:
    """Persist user gray-box decision to checkpoint state (append a new Checkpoint)."""
    try:
        status = CheckpointStatus(status_str)
    except ValueError:
        status = CheckpointStatus.MODIFIED
    cp = {
        "id": f"ckpt_{stage}_cli_{int(time.time())}",
        "stage": stage,
        "agent_name": stage,
        "title": f"Gray-box checkpoint for {stage}",
        "description": note or f"User decision via CLI: {status_str}",
        "payload": {},
        "status": status.value,
        "user_feedback": note or f"cli graybox decision: {status_str}",
        "created_at": utc_now(),
        "resolved_at": utc_now(),
    }
    save_checkpoint(project_root, cp)
    print(f"[graybox] saved checkpoint: stage={stage} status={status.value}")


# ── workspace listing helpers ──────────────────────────────────────────────
def list_runs(workspace_root: Path) -> list[Path]:
    runs_dir = workspace_root / "workspace" / "runs"
    if not runs_dir.exists():
        return []
    return sorted([p for p in runs_dir.iterdir() if p.is_dir()], key=lambda p: p.name)


def list_agents_in_run(run_dir: Path) -> list[tuple[str, Path]]:
    """Map (display_name, dir) for each agent subdir under a run (per workbench 8-segment convention)."""
    mapping = {
        "00_intake": "Supervisor",
        "01_sources": "Data",
        "02_literature": "Literature",
        "03_strategy": "Design",
        "04_modeling": "Execution",
        "05_results": "Manuscript-results",
        "06_writing": "Manuscript-draft",
        "07_review": "Verifier",
        "08_final": "Manuscript-final",
    }
    out = []
    for sub in sorted(run_dir.iterdir()):
        if sub.is_dir() and sub.name in mapping:
            out.append((mapping[sub.name], sub))
    return out


def default_output_files_for_agent(project_root: Path, agent_role: str) -> list[Path]:
    """Map agent role → 灰盒审阅时展示的输出文件 (按 workbench 8-segment 目录约定)."""
    seg = {
        "supervisor": "00_intake",
        "data": "01_sources",
        "literature": "02_literature",
        "design": "03_strategy",
        "execution": "04_modeling",
        "manuscript": "06_writing",
        "verifier": "07_review",
    }[agent_role]
    seg_dir = project_root / seg
    if not seg_dir.exists():
        return []
    return sorted([p for p in seg_dir.iterdir() if p.is_file() and (p.suffix in (".md", ".json", ".tex"))])

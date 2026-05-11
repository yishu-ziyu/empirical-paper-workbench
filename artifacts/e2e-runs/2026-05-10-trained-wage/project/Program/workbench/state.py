from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_project_state(
    paper_config: dict[str, Any],
    paths: dict[str, Path],
    mode: str,
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "project_slug": paper_config["project"]["slug"],
        "project_title": paper_config["project"]["title"],
        "language": paper_config["project"]["language"],
        "final_output": paper_config["project"]["final_output"],
        "internal_formats": paper_config["project"]["internal_formats"],
        "research_question": paper_config["research"]["question"],
        "current_stage": paper_config["research"]["current_stage"],
        "baseline_family": paper_config["methods"]["baseline"]["family"],
        "final_dataset": str(paths["final_dataset"].relative_to(paths["state_file"].parents[1])),
        "dataset_exists": paths["final_dataset"].exists(),
        "last_run_mode": mode,
        "updated_at": utc_timestamp(),
        "artifacts": artifacts,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def resolve_project_paths(
    project_root: Path,
    paper_config: dict[str, Any],
    paper_config_path: Path | None = None,
) -> dict[str, Path]:
    outputs = paper_config["outputs"]
    data = paper_config["data"]
    return {
        "paper_config": paper_config_path or project_root / "paper.yaml",
        "analysis_config": project_root / "Program" / "config" / "analysis_config.yaml",
        "state_file": project_root / outputs["state_file"],
        "results_index": project_root / outputs["results_index"],
        "markdown_draft": project_root / outputs["markdown_draft"],
        "latex_draft": project_root / outputs["latex_draft"],
        "project_snapshot": project_root / outputs.get("project_snapshot", "Results/json/project_snapshot.json"),
        "analysis_result": project_root / outputs.get("analysis_result", "Results/json/analysis_result.json"),
        "run_log": project_root / outputs.get("run_log", "Results/logs/run_paper.log"),
        "final_dataset": project_root / data["final_dataset"],
        "results_json_dir": project_root / "Results" / "json",
        "results_logs_dir": project_root / "Results" / "logs",
        "generated_dir": project_root / "Manuscripts" / "generated",
    }

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


THESIS_PATHS = {
    "data": "01_data",
    "code": "02_code",
    "results": "03_results",
    "manuscript": "04_paper",
    "references": "05_reference",
    "workspace": "06_workspace",
    "literature": "literature",
    "state": "state",
}

GENERIC_PATHS = {
    "data": "Data",
    "code": "Program",
    "results": "Results",
    "manuscript": "Manuscripts",
    "references": "Reference",
    "workspace": "workspace",
    "literature": "Reference",
    "state": "state",
}


def has_paths(root: Path, rels: list[str]) -> bool:
    return all((root / rel).exists() for rel in rels)


def read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def detect_project_profile(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    if has_paths(root, ["01_data", "02_code", "03_results", "04_paper", "05_reference"]):
        state = read_json_if_exists(root / "state" / "project_state.json")
        return {
            "project_root": str(root),
            "layout": "thesis_final",
            "title": state.get("project_title") or state.get("title") or root.name,
            "research_question": state.get("research_question", ""),
            "paths": THESIS_PATHS,
            "known_logic": {
                "topic": "industrial robots and labor reallocation",
                "identification": "Bartik IV",
                "outcome_layer": "CFPS",
                "mechanism_layer": "CLDS",
                "calibration_layer": "CGSS",
                "matching_boundary": "strict matching efficiency is not directly identified",
            },
        }
    if has_paths(root, ["Data", "Program", "Results", "Manuscripts"]):
        paper = read_yaml_if_exists(root / "paper.yaml")
        project = paper.get("project", {})
        research = paper.get("research", {})
        return {
            "project_root": str(root),
            "layout": "generic_aer",
            "title": project.get("title", root.name),
            "research_question": research.get("question", ""),
            "paths": GENERIC_PATHS,
            "known_logic": {},
        }
    raise FileNotFoundError(f"Unsupported empirical project layout: {root}")


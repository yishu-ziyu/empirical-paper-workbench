from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


def render_template(template_path: Path, context: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    return template.render(**context)


def build_draft_context(
    paper_config: dict[str, Any],
    dataset_exists: bool,
    mode: str,
) -> dict[str, Any]:
    return {
        "title": paper_config["project"]["title"],
        "research_question": paper_config["research"]["question"],
        "contribution": paper_config["research"]["contribution"],
        "current_stage": paper_config["research"]["current_stage"],
        "baseline_candidates": paper_config["methods"]["baseline"]["candidates"],
        "robustness_checks": paper_config["methods"]["robustness"],
        "dataset_path": paper_config["data"]["final_dataset"],
        "dataset_exists": dataset_exists,
        "mode": mode,
    }


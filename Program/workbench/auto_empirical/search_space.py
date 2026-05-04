from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ResearchSearchSpace:
    datasets: list[dict[str, Any]]
    outcomes: list[dict[str, Any]]
    designs: list[dict[str, Any]]
    robustness: list[str]
    hard_constraints: list[str]
    scoring_weights: dict[str, float]

    def dataset_keys(self) -> set[str]:
        return {item["key"] for item in self.datasets}

    def outcome_keys(self) -> set[str]:
        return {item["key"] for item in self.outcomes}

    def design_keys(self) -> set[str]:
        return {item["key"] for item in self.designs}


def load_research_search_space(path: Path) -> ResearchSearchSpace:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ResearchSearchSpace(
        datasets=list(payload.get("datasets", [])),
        outcomes=list(payload.get("outcomes", [])),
        designs=list(payload.get("designs", [])),
        robustness=list(payload.get("robustness", [])),
        hard_constraints=list(payload.get("hard_constraints", [])),
        scoring_weights=dict(payload.get("scoring_weights", {})),
    )

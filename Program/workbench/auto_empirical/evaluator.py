from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_WEIGHTS: dict[str, float] = {
    "data_feasibility": 0.25,
    "identification_credibility": 0.25,
    "literature_novelty": 0.15,
    "result_stability": 0.15,
    "mechanism_clarity": 0.10,
    "writing_fit": 0.10,
}


@dataclass(frozen=True)
class CandidateEvaluation:
    score: float
    accepted: bool
    component_scores: dict[str, float]
    violations: list[str]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "accepted": self.accepted,
            "component_scores": self.component_scores,
            "violations": self.violations,
            "notes": self.notes,
        }


def score_candidate(
    component_scores: dict[str, float],
    violations: list[str] | None = None,
    weights: dict[str, float] | None = None,
    notes: list[str] | None = None,
) -> CandidateEvaluation:
    active_weights = weights or DEFAULT_WEIGHTS
    active_violations = violations or []
    normalized_components = {
        key: max(0.0, min(1.0, float(component_scores.get(key, 0.0)))) for key in active_weights
    }
    weighted_score = sum(normalized_components[key] * weight for key, weight in active_weights.items())
    penalty = 1.0 if active_violations else 0.0
    score = max(0.0, round((weighted_score - penalty) * 100, 2))
    return CandidateEvaluation(
        score=score,
        accepted=not active_violations and score >= 70.0,
        component_scores=normalized_components,
        violations=active_violations,
        notes=notes or [],
    )

"""Helpers that turn a research direction into a runnable specification."""

from .spec import (
    DirectionSpec,
    apply_heterogeneity_to_formula,
    build_heterogeneity_ols_formula,
    infer_heterogeneity_groups,
    slug_for_topic,
)

__all__ = [
    "DirectionSpec",
    "apply_heterogeneity_to_formula",
    "build_heterogeneity_ols_formula",
    "infer_heterogeneity_groups",
    "slug_for_topic",
]

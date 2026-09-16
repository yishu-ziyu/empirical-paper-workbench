"""Helpers that turn a research direction into a runnable specification."""

from .propose import propose_design
from .spec import DirectionSpec, slug_for_topic

__all__ = ["DirectionSpec", "propose_design", "slug_for_topic"]

"""One way to read a design field, used by every stage.

Stages used to read the same field with different spellings and different
precedence (``time`` before ``time_col`` in one place, the reverse in
another). ``field(spec, name)`` reads the canonical name first, then its
spelling variants. Only pure spelling variants belong here; method rules such
as "the endogenous variable defaults to the treatment" stay at the call site.

The producers of a specification (``DirectionSpec.to_main_specification`` and
``DirectionSpec.enrich_direction``) write every spelling with the same value,
so the precedence below does not change any value on the product's own paths.
"""
from __future__ import annotations

from typing import Any, Mapping

ALIASES: dict[str, tuple[str, ...]] = {
    "outcome": ("outcome", "outcome_col"),
    "treatment": ("treatment", "treatment_col"),
    "endogenous": ("endogenous", "endogenous_col"),
    "instrument": ("instrument", "instrument_col"),
    "time": ("time", "time_col"),
    "unit": ("unit", "unit_col"),
    "id": ("id_col", "id"),
    "cluster": ("cluster", "cluster_col"),
    "first_treat": ("first_treat_col", "treatment_group_col"),
    "running_var": ("running_var", "running", "running_variable"),
}


def field(spec: Mapping[str, Any] | None, name: str, default: Any = None) -> Any:
    """First non-empty value among the spellings of ``name``."""
    if not isinstance(spec, Mapping):
        return default
    for key in ALIASES.get(name, (name,)):
        value = spec.get(key)
        if value is not None and value != "" and value != []:
            return value
    return default

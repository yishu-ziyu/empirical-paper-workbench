"""Design field accessor, and the premise that makes it behaviour-preserving."""
from __future__ import annotations

import pytest

from agent.design.fields import ALIASES, field
from agent.design.spec import DirectionSpec


def test_canonical_name_wins_and_empty_values_are_skipped():
    assert field({"time": "year", "time_col": "wave"}, "time") == "year"
    assert field({"time": "", "time_col": "wave"}, "time") == "wave"
    assert field({"instrument": None, "instrument_col": "z"}, "instrument") == "z"
    assert field({}, "cluster", "none") == "none"
    assert field(None, "outcome") is None
    assert field({"unknown_key": 1}, "unknown_key") == 1


DIRECTIONS = [
    {"question": "q", "dv": "y", "iv": "d", "method": "did", "time_col": "year", "id_col": "unit", "first_treat_col": "g", "cluster": "unit"},
    {"question": "q", "dv": "lwage", "iv": "educ", "method": "iv", "instrument": "nearc4", "endogenous": "educ", "controls": ["exper"]},
    {"question": "q", "dv": "y", "iv": "x", "method": "rd", "running_var": "x", "cutoff": 0},
    {"question": "q", "dv": "y", "iv": "t", "method": "scm", "unit_col": "unit", "time_col": "year", "treated_unit": "u0", "treatment_time": 2012},
    {"question": "q", "dv": "y", "iv": "d", "method": "ols", "controls": ["a"], "cluster": "c"},
]


@pytest.mark.parametrize("rd", DIRECTIONS, ids=lambda d: d["method"])
def test_producers_write_every_spelling_with_one_value(rd):
    """If this fails, field() precedence could change behaviour: fix the producer."""
    spec = DirectionSpec.from_direction(rd)
    for produced in (spec.to_main_specification(), spec.enrich_direction(rd)):
        for name, spellings in ALIASES.items():
            values = {str(produced[k]) for k in spellings if produced.get(k) not in (None, "", [])}
            assert len(values) <= 1, (rd["method"], name, values)

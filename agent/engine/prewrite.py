"""Shared pre-write path for the graph and the Facade.

Estimate runs before literature so a slow search cannot hide the table.
"""
from __future__ import annotations

from engine.readiness import claim_mode


def run_prewrite(state: dict) -> dict:
    from nodes.set_direction import set_direction
    from nodes.identification_verify import identification_verify
    from nodes.estimate import estimate
    from nodes.robustness_check import robustness_check
    from nodes.search_literature import search_literature
    from nodes.citation_graph import build_citation_graph
    from nodes.generate_title import generate_title
    from nodes.generate_outline import generate_outline

    state = {**state, **set_direction(state)}
    state = {**state, **identification_verify(state)}
    state["claim"] = claim_mode(state)
    if state.get("star_rating") == 0 or state.get("identification_failed"):
        return state
    state = {**state, **estimate(state)}
    state = {**state, **robustness_check(state)}
    state = {**state, **search_literature(state)}
    state = {**state, **build_citation_graph(state)}
    state = {**state, **generate_title(state)}
    state = {**state, **generate_outline(state)}
    return state

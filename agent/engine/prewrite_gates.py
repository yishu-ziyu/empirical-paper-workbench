"""Estimate-prep gates: two human confirms + heterogeneity interaction hard-block.

FE (FM-E-DESIGN-ENTRY-GUIDE-1) requires Table 1 confirm and equation/题型→设定
confirm before estimate. ``qType === heterogeneity`` without an interaction
term (educ×region) is a hard block; ``blockingDecision`` / ``isBlock`` explain why.
"""
from __future__ import annotations

import re
from typing import Any

QTYPE_HETEROGENEITY = "heterogeneity"
QTYPE_AVERAGE = "average"
QTYPE_CAUSAL = "causal"

SPEC_MODE_INTERACTION = "interaction"
SPEC_MODE_LEVEL = "level"

BLOCK_CODE_HETERO_NO_INTERACTION = "heterogeneity_missing_interaction"
BLOCK_REASON_HETERO_NO_INTERACTION = (
    "题型是异质性，但设定没有交互项（educ×region）。请改设定或改题型。"
)

_QTYPE_ALIASES = {
    "heterogeneity": QTYPE_HETEROGENEITY,
    "hetero": QTYPE_HETEROGENEITY,
    "het": QTYPE_HETEROGENEITY,
    "slope": QTYPE_HETEROGENEITY,
    "异质性": QTYPE_HETEROGENEITY,
    "average": QTYPE_AVERAGE,
    "avg": QTYPE_AVERAGE,
    "level": QTYPE_AVERAGE,
    "mean": QTYPE_AVERAGE,
    "平均": QTYPE_AVERAGE,
    "causal": QTYPE_CAUSAL,
    "因果": QTYPE_CAUSAL,
}

_SPEC_MODE_ALIASES = {
    "interaction": SPEC_MODE_INTERACTION,
    "interact": SPEC_MODE_INTERACTION,
    "interacted": SPEC_MODE_INTERACTION,
    "hetero_interact": SPEC_MODE_INTERACTION,
    "level": SPEC_MODE_LEVEL,
    "additive": SPEC_MODE_LEVEL,
    "no_interaction": SPEC_MODE_LEVEL,
    "main_effects": SPEC_MODE_LEVEL,
    "main": SPEC_MODE_LEVEL,
}

# educ*region / educ:region / educ×region / educ x region
_INTERACTION_RE = re.compile(
    r"(\*|×|:)|(?<=\w)\s+[xX×]\s+(?=\w)",
)


def _norm(value: Any) -> str:
    return str(value or "").strip()


def normalize_q_type(value: Any) -> str | None:
    key = _norm(value).lower()
    if not key:
        return None
    return _QTYPE_ALIASES.get(key, key)


def normalize_spec_mode(value: Any) -> str | None:
    key = _norm(value).lower()
    if not key:
        return None
    return _SPEC_MODE_ALIASES.get(key, key)


def _first(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def resolve_q_type(state: dict[str, Any], extra: dict[str, Any] | None = None) -> str | None:
    extra = extra or {}
    rd = state.get("research_direction") if isinstance(state.get("research_direction"), dict) else {}
    return normalize_q_type(
        _first(
            extra.get("qType"),
            extra.get("q_type"),
            state.get("qType"),
            state.get("q_type"),
            rd.get("qType"),
            rd.get("q_type"),
            rd.get("question_type"),
        )
    )


def resolve_spec_mode(state: dict[str, Any], extra: dict[str, Any] | None = None) -> str | None:
    extra = extra or {}
    rd = state.get("research_direction") if isinstance(state.get("research_direction"), dict) else {}
    spec = state.get("main_specification") if isinstance(state.get("main_specification"), dict) else {}
    return normalize_spec_mode(
        _first(
            extra.get("specMode"),
            extra.get("spec_mode"),
            state.get("specMode"),
            state.get("spec_mode"),
            rd.get("specMode"),
            rd.get("spec_mode"),
            spec.get("specMode"),
            spec.get("spec_mode"),
        )
    )


def _formula_blob(state: dict[str, Any], extra: dict[str, Any] | None = None) -> str:
    extra = extra or {}
    spec = state.get("main_specification") if isinstance(state.get("main_specification"), dict) else {}
    parts = [
        extra.get("specification_equation"),
        extra.get("formula"),
        state.get("specification_equation"),
        spec.get("formula"),
        spec.get("iv_formula"),
        spec.get("feols_formula"),
    ]
    controls = spec.get("controls") or extra.get("controls") or []
    if isinstance(controls, (list, tuple)):
        parts.extend(str(item) for item in controls)
    return " ".join(_norm(part) for part in parts if _norm(part))


def spec_has_interaction(
    state: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> bool:
    """True when the setting includes an interaction (educ×region)."""
    extra = extra or {}
    if extra.get("hasInteraction") is True or extra.get("has_interaction") is True:
        return True
    mode = resolve_spec_mode(state, extra)
    if mode == SPEC_MODE_INTERACTION:
        return True
    if mode == SPEC_MODE_LEVEL:
        return False
    return bool(_INTERACTION_RE.search(_formula_blob(state, extra)))


def evaluate_blocking_decision(
    state: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Hard block: heterogeneity question type without an interaction term."""
    extra = extra or {}
    q_type = resolve_q_type(state, extra)
    spec_mode = resolve_spec_mode(state, extra)
    has_interaction = spec_has_interaction(state, extra)
    blocked = q_type == QTYPE_HETEROGENEITY and not has_interaction
    decision: dict[str, Any] = {
        "blocked": blocked,
        "isBlock": blocked,
        "code": BLOCK_CODE_HETERO_NO_INTERACTION if blocked else None,
        "reason": BLOCK_REASON_HETERO_NO_INTERACTION if blocked else None,
        "qType": q_type,
        "specMode": spec_mode,
        "hasInteraction": has_interaction,
    }
    return decision


def read_confirm_flag(source: dict[str, Any] | None, camel: str, snake: str) -> bool:
    if not isinstance(source, dict):
        return False
    if camel in source:
        return bool(source.get(camel))
    if snake in source:
        return bool(source.get(snake))
    return False


def merge_confirm_flags(
    state: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, bool]:
    extra = extra or {}
    table1 = read_confirm_flag(extra, "table1Confirmed", "table1_confirmed")
    if not table1:
        table1 = read_confirm_flag(state, "table1Confirmed", "table1_confirmed")
    spec = read_confirm_flag(extra, "specConfirmed", "spec_confirmed")
    if not spec:
        spec = read_confirm_flag(state, "specConfirmed", "spec_confirmed")
    return {"table1Confirmed": table1, "specConfirmed": spec}


def public_prewrite_gates(
    state: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    extra = extra or {}
    flags = merge_confirm_flags(state, extra)
    q_type = resolve_q_type(state, extra)
    spec_mode = resolve_spec_mode(state, extra)
    decision = evaluate_blocking_decision(state, extra)
    return {
        "table1Confirmed": flags["table1Confirmed"],
        "specConfirmed": flags["specConfirmed"],
        "qType": q_type,
        "specMode": spec_mode,
        "blockingDecision": decision,
    }


def persist_gate_fields(
    state: dict[str, Any],
    extra: dict[str, Any] | None = None,
    *,
    table1_confirmed: bool | None = None,
    spec_confirmed: bool | None = None,
) -> dict[str, Any]:
    """Write confirm flags + live blockingDecision onto state."""
    extra = extra or {}
    out = dict(state)
    q_type = resolve_q_type(out, extra)
    spec_mode = resolve_spec_mode(out, extra)
    if q_type is not None:
        out["q_type"] = q_type
        out["qType"] = q_type
    if spec_mode is not None:
        out["spec_mode"] = spec_mode
        out["specMode"] = spec_mode
    flags = merge_confirm_flags(out, extra)
    if table1_confirmed is not None:
        flags["table1Confirmed"] = bool(table1_confirmed)
    if spec_confirmed is not None:
        flags["specConfirmed"] = bool(spec_confirmed)
    out["table1_confirmed"] = flags["table1Confirmed"]
    out["spec_confirmed"] = flags["specConfirmed"]
    out["table1Confirmed"] = flags["table1Confirmed"]
    out["specConfirmed"] = flags["specConfirmed"]
    out["blocking_decision"] = evaluate_blocking_decision(out, extra)
    return out

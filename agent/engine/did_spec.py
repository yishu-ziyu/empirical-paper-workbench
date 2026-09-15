"""DID-BE-spec: confirmed method=did forces treated×period (or equivalent).

Trigger is confirmed ``session.design.method=did`` (DECIDE-6), not catalog
``allow_did``. If the 2×2 main term is still missing → hard block (no
estimate / no write-as-estimated). Does not emit ``| entity + time`` as a
DiD substitute and does not rewrite the OLS lock.

See docs/infer-design-contract.md §7.3.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from services.allow_did import (
    confirmed_did_method,
    design_from_state,
    has_treated_period_interaction,
)

DID_MISSING_INTERACTION = "did_missing_interaction"

# Constructed 2×2 cell names (the interaction itself).
_DUMMY_NAMES = frozenset(
    {
        "treat_post",
        "treatpost",
        "treatxpost",
        "treat_x_post",
        "treated_period",
        "treated_post",
        "did",
        "nj_after",
        "njxafter",
        "nj_x_after",
    }
)

_TREATED_NAMES = frozenset({"treated", "treat", "nj"})
_PERIOD_NAMES = frozenset({"period", "post", "after"})

# treat:post / treat * post / treat × post / treat#post / treat x post
_INTERACTION_RE = re.compile(
    r"(?i)\b(treated|treat|nj)\s*(?::|\*|×|#|x)\s*(period|post|after)\b"
    r"|\b(period|post|after)\s*(?::|\*|×|#|x)\s*(treated|treat|nj)\b"
)

_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def did_spec_applies(state: Mapping[str, Any] | None) -> bool:
    """True when DID-BE-spec must force or hard-block.

    Confirmed ``design.method=did`` only. Catalog identity, TITLE/TOPIC,
    form ``method=did``, and a stamped ``allow_did`` flag are not triggers.
    """
    return confirmed_did_method(state)


def columns_from_state(state: Mapping[str, Any] | None) -> frozenset[str]:
    names: set[str] = set()
    if not isinstance(state, dict):
        return frozenset()
    for key in ("cleaned_datasets", "uploaded_datasets"):
        for item in state.get(key) or []:
            if not isinstance(item, dict):
                continue
            for col in item.get("columns") or []:
                text = str(col).strip()
                if text:
                    names.add(text)
    csv_path = state.get("csv_path")
    if csv_path:
        try:
            import pandas as pd

            for col in pd.read_csv(str(csv_path), nrows=0).columns:
                text = str(col).strip()
                if text:
                    names.add(text)
        except Exception:
            pass
    return frozenset(names)


def has_did_main_term(
    spec: Mapping[str, Any] | None = None,
    direction: Mapping[str, Any] | None = None,
    columns: Any = (),
    extra_text: str = "",
) -> bool:
    """True when the spec names treated×period or an equivalent 2×2 dummy.

    ``method=did``, ``| entity + time``, and treat/post main effects alone
    do not count.
    """
    haystack = _haystack(spec, direction, extra_text)
    if _INTERACTION_RE.search(haystack):
        return True
    tokens = _tokens(haystack) | {_norm(c) for c in (columns or ()) if str(c).strip()}
    return bool(tokens & _DUMMY_NAMES)


def force_did_main_term(
    spec: Mapping[str, Any] | None,
    *,
    columns: Any = (),
    direction: Mapping[str, Any] | None = None,
    design: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Rewrite spec to name the 2×2 term. None if it cannot be bound.

    Never emits ``| entity + time`` as a substitute.
    """
    base = dict(spec) if isinstance(spec, dict) else {}
    rd = direction if isinstance(direction, dict) else {}
    outcome = (
        _first_str(base, "outcome", "outcome_col", "dv")
        or _first_str(rd, "outcome", "outcome_col", "dv")
        or _first_str(design or {}, "outcome", "outcome_col", "dv")
    )
    if not outcome:
        return None

    names = _candidate_names(base, rd, columns, design)
    dummy = _pick_named(names, _DUMMY_NAMES)
    if dummy:
        return _spec_with_term(base, outcome, dummy, interaction=None)

    treated = _pick_named(names, _TREATED_NAMES)
    period = _pick_named(names, _PERIOD_NAMES)
    if treated and period:
        return _spec_with_term(base, outcome, treated, interaction=period)

    if has_did_main_term(base, rd, columns):
        formula = str(base.get("formula") or "").split("|", 1)[0].strip()
        if formula:
            out = dict(base)
            out["formula"] = formula
            out.pop("feols_formula", None)
            return out
    return None


def can_form_did_main_term(
    state: Mapping[str, Any] | None,
    direction: Mapping[str, Any] | None = None,
) -> bool:
    """True when payload + session columns / confirmed design can name the 2×2 term."""
    spec = None
    design = design_from_state(state)
    if isinstance(state, dict) and isinstance(state.get("main_specification"), dict):
        spec = state.get("main_specification")
    rd = direction
    if rd is None and isinstance(state, dict):
        raw = state.get("research_direction")
        rd = raw if isinstance(raw, dict) else None
    columns = columns_from_state(state)
    if has_treated_period_interaction(design):
        return True
    if has_did_main_term(spec, rd, columns):
        return True
    return force_did_main_term(spec, columns=columns, direction=rd, design=design) is not None


def apply_did_spec(state: Mapping[str, Any] | None) -> dict[str, Any]:
    """When confirmed method=did, force the 2×2 term onto main_specification."""
    if not did_spec_applies(state):
        return {}
    assert isinstance(state, dict)
    spec = state.get("main_specification")
    spec = spec if isinstance(spec, dict) else {}
    rd = state.get("research_direction")
    rd = rd if isinstance(rd, dict) else {}
    design = design_from_state(state)
    columns = columns_from_state(state)
    forced = force_did_main_term(
        spec, columns=columns, direction=rd, design=design
    )
    if forced is None:
        return {}
    return {"main_specification": forced}


def did_spec_block_reason(state: Mapping[str, Any] | None) -> str | None:
    """Hard-block code when confirmed DiD still lacks the 2×2 term on the spec."""
    if not did_spec_applies(state):
        return None
    assert isinstance(state, dict)
    spec = state.get("main_specification")
    spec = spec if isinstance(spec, dict) else {}
    rd = state.get("research_direction")
    rd = rd if isinstance(rd, dict) else {}
    extra = ""
    estimate = state.get("estimate")
    if isinstance(estimate, dict):
        extra = str(estimate.get("formula") or "")
    if has_did_main_term(spec, rd, extra_text=extra):
        return None
    return DID_MISSING_INTERACTION


def _spec_with_term(
    spec: dict[str, Any],
    outcome: str,
    treatment: str,
    *,
    interaction: str | None,
) -> dict[str, Any]:
    controls = [
        c
        for c in _as_str_list(spec.get("controls"))
        if c and c != treatment and c != interaction
    ]
    if interaction:
        rhs = f"{treatment} * {interaction}"
        treatment_name = f"{treatment}:{interaction}"
    else:
        rhs = treatment
        treatment_name = treatment
    extras = [c for c in controls if _norm(c) not in _TREATED_NAMES | _PERIOD_NAMES]
    if extras:
        rhs = f"{rhs} + {' + '.join(extras)}"
    out = dict(spec)
    out["outcome"] = outcome
    out["treatment"] = treatment_name
    out["formula"] = f"{outcome} ~ {rhs}"
    out.pop("feols_formula", None)
    return out


def _candidate_names(
    spec: Mapping[str, Any],
    direction: Mapping[str, Any],
    columns: Any,
    design: Mapping[str, Any] | None = None,
) -> set[str]:
    names: set[str] = set()
    sources: list[Mapping[str, Any]] = []
    if isinstance(spec, dict):
        sources.append(spec)
    if isinstance(direction, dict):
        sources.append(direction)
    if isinstance(design, dict):
        sources.append(design)
    for src in sources:
        for key in (
            "treatment",
            "treatment_col",
            "iv",
            "outcome",
            "outcome_col",
            "dv",
            "treated",
            "period",
        ):
            raw = src.get(key)
            if raw is not None and str(raw).strip():
                names.add(str(raw).strip())
        names.update(_as_str_list(src.get("controls")))
        for text in (src.get("formula"), src.get("feols_formula")):
            names.update(_raw_tokens(str(text or "")))
        raw_interactions = src.get("interactions")
        if isinstance(raw_interactions, list):
            for item in raw_interactions:
                if not isinstance(item, dict):
                    continue
                kind = str(item.get("kind") or "").strip().lower()
                if kind and kind != "did":
                    continue
                for key in ("term", "left", "right"):
                    raw = item.get(key)
                    if raw is not None and str(raw).strip():
                        names.add(str(raw).strip())
    for col in columns or ():
        if str(col).strip():
            names.add(str(col).strip())
    return {n for n in names if n}


def _haystack(
    spec: Mapping[str, Any] | None,
    direction: Mapping[str, Any] | None,
    extra_text: str,
) -> str:
    parts: list[str] = []
    for src in (spec, direction):
        if not isinstance(src, dict):
            continue
        for key in (
            "formula",
            "treatment",
            "treatment_col",
            "iv",
            "controls",
        ):
            raw = src.get(key)
            if raw is None:
                continue
            if key == "formula":
                parts.append(str(raw).split("|", 1)[0])
            elif isinstance(raw, (list, tuple)):
                parts.extend(str(item) for item in raw)
            else:
                parts.append(str(raw))
    if extra_text:
        parts.append(str(extra_text).split("|", 1)[0])
    return " ".join(parts)


def _tokens(text: str) -> set[str]:
    return {_norm(tok) for tok in _TOKEN_RE.findall(text or "")}


def _raw_tokens(text: str) -> set[str]:
    return {tok for tok in _TOKEN_RE.findall(text or "") if tok}


def _norm(name: str) -> str:
    return str(name or "").strip().lower()


def _pick_named(names: set[str], wanted: frozenset[str]) -> str:
    by_norm = {_norm(n): n for n in names if n}
    for token in wanted:
        if token in by_norm:
            return by_norm[token]
    return ""


def _first_str(src: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        raw = src.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if text:
            return text
    return ""


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in re.split(r"[,;]+", value) if part.strip()]
    return [str(item).strip() for item in value if str(item).strip()]

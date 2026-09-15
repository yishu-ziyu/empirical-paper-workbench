"""Direction-phase preview: Table 1 descriptives + main-spec equation text.

Computed after identification accepts a direction and before estimate runs.
Does not call the estimate / StatsPAI path.
"""
from __future__ import annotations

import math
import re
from typing import Any

PREWRITE_GATE_AWAITING_ESTIMATE = "awaiting_estimate"
PREWRITE_GATE_ESTIMATE_COMPLETE = "estimate_complete"

# Keys written by estimate → outline. Cleared when a new direction pauses
# so GET /sessions does not show a stale table from the previous spec.
PREWRITE_DOWNSTREAM_KEYS = (
    "estimate",
    "results",
    "robustness_results",
    "outline",
    "title_chapter",
    "literature_entries",
    "literature_query",
    "literature_source",
    "literature_produced_by",
    "citation_graph",
    "citation_indices",
)

_SPEC_COLUMN_KEYS = (
    "outcome",
    "treatment",
    "endogenous",
    "running_var",
    "id_col",
    "time_col",
    "first_treat_col",
    "unit_col",
    "cluster",
)
_SPEC_LIST_KEYS = ("controls", "instruments", "cluster_levels", "heterogeneity_groups")


def _to_jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def spec_preview_columns(spec: dict[str, Any] | None) -> list[str]:
    """Ordered unique column names implied by the main specification."""
    if not isinstance(spec, dict):
        return []
    seen: set[str] = set()
    columns: list[str] = []

    def add(raw: Any) -> None:
        text = str(raw or "").strip()
        if not text or text in seen:
            return
        seen.add(text)
        columns.append(text)

    for key in _SPEC_COLUMN_KEYS:
        add(spec.get(key))
    for key in _SPEC_LIST_KEYS:
        values = spec.get(key)
        if isinstance(values, str):
            values = [part.strip() for part in values.split(",") if part.strip()]
        if isinstance(values, (list, tuple)):
            for item in values:
                add(item)
    return columns


def specification_equation_text(spec: dict[str, Any] | None) -> str:
    """Human-readable main-specification equation (not an estimate)."""
    if not isinstance(spec, dict) or not spec:
        return ""
    method = str(spec.get("method") or "").strip().lower()
    outcome = str(spec.get("outcome") or "").strip() or "Y"
    if method == "rd":
        running = str(spec.get("running_var") or "").strip() or "R"
        cutoff = spec.get("cutoff")
        cutoff_text = "0" if cutoff is None else str(cutoff)
        return f"{outcome} = f({running}) + τ·1[{running} ≥ {cutoff_text}] + ε"
    if method == "scm":
        unit = (
            str(spec.get("treated_unit") or spec.get("unit_col") or "").strip()
            or "treated"
        )
        return f"{outcome}_{{{unit}}} vs synthetic control"
    formula = (
        spec.get("iv_formula")
        or spec.get("feols_formula")
        or spec.get("formula")
        or ""
    )
    formula = str(formula).strip()
    if formula:
        return _formula_to_equation(formula)
    treatment = str(spec.get("treatment") or "").strip() or "D"
    controls = [
        str(item).strip()
        for item in (spec.get("controls") or [])
        if str(item).strip()
    ]
    terms = [treatment, *[c for c in controls if c != treatment]]
    rhs = " + ".join(f"{_beta(i)} {name}" for i, name in enumerate(terms, start=1))
    return f"{outcome} = {_beta(0)} + {rhs} + ε"


def _formula_to_equation(formula: str) -> str:
    """Turn ``y ~ x + z`` / IV / FE formulas into display equation text."""
    if "~" not in formula:
        return formula
    left, right = formula.split("~", 1)
    outcome = left.strip() or "Y"
    right = right.strip()
    fe = ""
    if "|" in right:
        right, fe = [part.strip() for part in right.split("|", 1)]
        if fe:
            fe = f" | {fe}"
    if right.startswith("(") and ")" in right:
        return f"{outcome} ~ {right}{fe}"
    terms = [part.strip() for part in re.split(r"\s*\+\s*", right) if part.strip()]
    if not terms:
        return f"{outcome} = {_beta(0)} + ε{fe}"
    pieces = [_beta(0)]
    for index, name in enumerate(terms, start=1):
        pieces.append(f"{_beta(index)} {name}")
    return f"{outcome} = {' + '.join(pieces)} + ε{fe}"


_SUBSCRIPTS = "₀₁₂₃₄₅₆₇₈₉"


def _beta(index: int) -> str:
    return "β" + "".join(_SUBSCRIPTS[int(digit)] for digit in str(index))


def compute_table1(
    csv_path: str | None,
    spec: dict[str, Any] | None,
) -> dict[str, Any]:
    """Descriptive Table 1 for specification columns. Never estimates."""
    columns = ["variable", "count", "mean", "std", "min", "max", "missing", "role"]
    wanted = spec_preview_columns(spec)
    payload: dict[str, Any] = {
        "produced_by": "prewrite_preview",
        "columns": columns,
        "rows": [],
        "n": None,
        "variables": wanted,
    }
    if not csv_path:
        payload["reason"] = "no_csv"
        return payload
    try:
        import pandas as pd
    except Exception:
        payload["reason"] = "pandas_unavailable"
        return payload
    try:
        frame = pd.read_csv(csv_path)
    except Exception:
        payload["reason"] = "csv_unreadable"
        return payload
    payload["n"] = int(len(frame))
    present = [name for name in wanted if name in frame.columns]
    if not present:
        payload["reason"] = "no_spec_columns_in_csv"
        return payload

    missing_by_col: dict[str, int] = {}
    try:
        import statspai as sp

        meta = sp.describe(frame[present])
        for _, row in meta.iterrows():
            missing_by_col[str(row["variable"])] = int(row["n_missing"])
    except Exception:
        missing_by_col = {
            str(col): int(frame[col].isna().sum()) for col in present
        }

    roles = _column_roles(spec)
    rows: list[dict[str, Any]] = []
    for col in present:
        series = frame[col]
        is_numeric = pd.api.types.is_numeric_dtype(series)
        has_values = series.count() > 0
        rows.append(
            {
                "variable": str(col),
                "count": int(series.count()),
                "mean": _to_jsonable(
                    float(series.mean()) if is_numeric and has_values else None
                ),
                "std": _to_jsonable(
                    float(series.std()) if is_numeric and series.count() > 1 else None
                ),
                "min": _to_jsonable(
                    float(series.min())
                    if is_numeric and has_values
                    else (series.min() if has_values else None)
                ),
                "max": _to_jsonable(
                    float(series.max())
                    if is_numeric and has_values
                    else (series.max() if has_values else None)
                ),
                "missing": int(
                    missing_by_col.get(str(col), int(series.isna().sum()))
                ),
                "role": roles.get(str(col)),
            }
        )
    payload["rows"] = rows
    return payload


def _column_roles(spec: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(spec, dict):
        return {}
    roles: dict[str, str] = {}

    def mark(raw: Any, role: str) -> None:
        text = str(raw or "").strip()
        if text and text not in roles:
            roles[text] = role

    mark(spec.get("outcome"), "outcome")
    mark(spec.get("treatment"), "treatment")
    mark(spec.get("endogenous"), "endogenous")
    mark(spec.get("running_var"), "running")
    for item in spec.get("instruments") or []:
        mark(item, "instrument")
    for item in spec.get("controls") or []:
        mark(item, "control")
    return roles


def build_prewrite_preview(state: dict[str, Any]) -> dict[str, Any]:
    """Attach Table 1 + equation and mark the estimate confirm gate."""
    spec = state.get("main_specification")
    if not isinstance(spec, dict):
        spec = {}
    table1 = compute_table1(state.get("csv_path"), spec)
    equation = specification_equation_text(spec)
    return {
        "table1": table1,
        "specification_equation": equation,
        "prewrite_gate": PREWRITE_GATE_AWAITING_ESTIMATE,
    }


def clear_prewrite_downstream(state: dict[str, Any]) -> dict[str, Any]:
    """Drop estimate→outline products so a new direction cannot show stale results."""
    out = dict(state)
    for key in PREWRITE_DOWNSTREAM_KEYS:
        out[key] = None
    return out

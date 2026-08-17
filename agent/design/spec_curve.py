"""Run a small set of defensible specs and keep every row.

Explore-arm artifact: every spec stays visible. It does not rewrite
the pre-specified claim on the design card.
"""

from __future__ import annotations

from typing import Any


def build_specs(controls: list[str], columns: list[str]) -> list[dict[str, Any]]:
    """A small, general grid. Not a special case for one paper."""
    controls = [c for c in controls if c in columns]
    specs: list[dict[str, Any]] = [
        {"spec": "bivariate", "controls": [], "subset": None},
    ]
    if controls:
        specs.append(
            {
                "spec": "partial_controls",
                "controls": controls[: max(1, len(controls) - 1)],
                "subset": None,
            }
        )
        specs.append({"spec": "baseline_controls", "controls": controls, "subset": None})
    for split in ("urban", "female"):
        if split in columns:
            rest = [c for c in controls if c != split]
            specs.append({"spec": f"{split}_1", "controls": rest, "subset": (split, 1)})
            specs.append({"spec": f"{split}_0", "controls": rest, "subset": (split, 0)})
    return specs


def _fit_ols(y: Any, X: Any, treatment: str) -> dict[str, float] | None:
    """HC1 OLS via statsmodels; numpy fallback if the extra dep is missing."""
    try:
        import statsmodels.api as sm

        model = sm.OLS(y, X).fit(cov_type="HC1")
        return {
            "nobs": float(model.nobs),
            "coef": float(model.params[treatment]),
            "se": float(model.bse[treatment]),
            "p": float(model.pvalues[treatment]),
            "r2": float(model.rsquared),
        }
    except Exception:
        import numpy as np

        y_arr = np.asarray(y, dtype=float)
        x_arr = np.asarray(X, dtype=float)
        try:
            beta, *_ = np.linalg.lstsq(x_arr, y_arr, rcond=None)
        except Exception:
            return None
        fitted = x_arr @ beta
        resid = y_arr - fitted
        n, k = x_arr.shape
        if n <= k:
            return None
        sst = float(np.sum((y_arr - y_arr.mean()) ** 2))
        r2 = 1.0 - float(np.sum(resid ** 2)) / sst if sst else 0.0
        names = list(getattr(X, "columns", range(k)))
        try:
            idx = names.index(treatment)
        except ValueError:
            idx = 1 if k > 1 else 0
        xtx_inv = np.linalg.pinv(x_arr.T @ x_arr)
        sigma2 = float(np.sum(resid ** 2) / (n - k))
        se = float(np.sqrt(max(sigma2 * xtx_inv[idx, idx], 0.0)))
        return {
            "nobs": float(n),
            "coef": float(beta[idx]),
            "se": se,
            "p": float("nan"),
            "r2": r2,
        }


def run_spec_curve(
    df: Any,
    *,
    outcome: str,
    treatment: str,
    controls: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Estimate the spec grid with OLS. Empty if columns are missing."""
    import pandas as pd

    control_list = list(controls or [])
    columns = list(df.columns)
    rows: list[dict[str, Any]] = []
    for spec in build_specs(control_list, columns):
        needed = [outcome, treatment, *spec["controls"]]
        if any(c not in columns for c in needed):
            continue
        work = df.dropna(subset=needed).copy()
        subset = spec.get("subset")
        if subset:
            col, value = subset
            if col not in work.columns:
                continue
            work = work.loc[work[col] == value]
        if len(work) < 20:
            continue
        y = work[outcome].astype(float)
        x_cols = [treatment, *spec["controls"]]
        x_cols = [c for c in x_cols if work[c].nunique(dropna=True) > 1]
        if treatment not in x_cols:
            continue
        X = pd.concat(
            [pd.Series(1.0, index=work.index, name="const"), work[x_cols].astype(float)],
            axis=1,
        )
        fit = _fit_ols(y, X, treatment)
        if fit is None:
            continue
        rows.append(
            {
                "spec": spec["spec"],
                "nobs": int(fit["nobs"]),
                "treatment": treatment,
                "treatment_coef": fit["coef"],
                "treatment_se": fit["se"],
                "treatment_p": fit["p"],
                "r2": fit["r2"],
                "controls": "+".join(spec["controls"]) or "none",
                "subset": f"{subset[0]}={subset[1]}" if subset else "all",
            }
        )
    return rows


def spec_curve_markdown(rows: list[dict[str, Any]], *, slug: str = "") -> str:
    title = f"# 设定表 · {slug}" if slug else "# 设定表"
    lines = [
        title,
        "",
        "探索臂产物。每一行都保留。主结果仍以用户确认的研究方向为准。",
        "",
        "| spec | n | coef | se | p | controls | subset |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['spec']} | {row['nobs']} | {row['treatment_coef']:.4f} | "
            f"{row['treatment_se']:.4f} | {row['treatment_p']:.4f} | "
            f"{row['controls']} | {row['subset']} |"
        )
    if not rows:
        lines.append("| — | — | — | — | — | — | — |")
    return "\n".join(lines)


def run_spec_curve_from_state(state: dict[str, Any]) -> dict[str, Any] | None:
    """Convenience: read main_specification / csv from state, return payload or None."""
    spec = state.get("main_specification") or {}
    csv_path = state.get("csv_path")
    outcome = spec.get("outcome") if isinstance(spec, dict) else None
    treatment = spec.get("treatment") if isinstance(spec, dict) else None
    controls = spec.get("controls") if isinstance(spec, dict) else []
    direction = state.get("research_direction") or {}
    if (not outcome or not treatment) and isinstance(direction, dict):
        outcome = outcome or direction.get("dv") or direction.get("outcome")
        treatment = treatment or direction.get("iv") or direction.get("treatment")
        controls = controls or direction.get("controls") or []
    if not csv_path or not outcome or not treatment:
        return None
    try:
        import pandas as pd

        df = pd.read_csv(csv_path)
        rows = run_spec_curve(
            df, outcome=outcome, treatment=treatment, controls=list(controls or [])
        )
    except Exception:
        return None
    slug = ""
    if isinstance(direction, dict):
        slug = str(direction.get("question") or "")
    return {
        "slug": slug,
        "n_specs": len(rows),
        "rows": rows,
        "markdown": spec_curve_markdown(rows, slug=slug),
        "note": "Explore arm. Every spec is listed. Do not treat the largest coefficient as the main result.",
    }

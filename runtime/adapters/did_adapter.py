"""
runtime/adapters/did_adapter.py

Generic Difference-in-Differences adapter.

Reads standard tabular data (CSV / parquet), runs:
  1. Event study  (parallel-trends + dynamic treatment effects)
  2. Main DID regression (coefficient + clustered robust SE, progressive specs)
  3. Heterogeneity analysis (by income quantile)

Outputs
-------
  tables/table2_did.csv           — main coefficient table
  figures/event_study.png         — event-study coefficient plot
  model_log.md                    — detailed run log with all results

Usage
-----
  from runtime.adapters.did_adapter import run_did_analysis

  result = run_did_analysis(
      data_path="artifacts/analysis_ready.pkl",
      treatment="high_minwage_growth",
      time="year",
      post="post",
      outcomes=["ln_expense"],
      covariates=["age", "gender", "familysize", "ln_fincome1"],
      cluster="province_code",
      treatment_year=2012,
      project_root=Path("."),
  )

Dependencies: statspai (pip install statspai[fixest]), matplotlib, pandas, numpy.
Falls back to manual OLS with clustered SE if statspai is unavailable.
"""

from __future__ import annotations

import io
import contextlib
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ── optional statspai ─────────────────────────────────────────────

try:
    import statspai as sp  # type: ignore[import-untyped]

    HAS_STATSPAI = True
except ImportError:
    HAS_STATSPAI = False
    sp = None  # type: ignore[assignment]
    logger.warning("statspai not installed — DID adapter will use manual OLS fallback")


# ── helpers ───────────────────────────────────────────────────────

def _load_data(data_path: str | Path) -> pd.DataFrame:
    """Load data from CSV or parquet, auto-detect by extension."""
    p = Path(data_path)
    if not p.exists():
        raise FileNotFoundError(f"data not found: {p}")

    if p.suffix in (".parquet", ".pq"):
        return pd.read_parquet(p)
    elif p.suffix == ".pkl":
        return pd.read_pickle(p)
    else:
        return pd.read_csv(p)


def _ensure_dirs(project_root: Path) -> tuple[Path, Path]:
    """Create tables/ and figures/ under project root if missing."""
    tables = project_root / "tables"
    figures = project_root / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    return tables, figures


def _build_model_formula(
    outcome: str,
    treatment: str,
    time: str,
    covariates: list[str] | None,
    use_interaction: bool = True,
) -> str:
    """Build a feols formula with fixed effects absorbed via | separator."""
    if use_interaction:
        rhs = f"{treatment}:{time}"
    else:
        rhs = treatment

    if covariates:
        rhs += " + " + " + ".join(covariates)

    return f"{outcome} ~ {rhs}"


def _build_fe_part(
    unit_fe: str | None,
    time_fe: str | None,
) -> str:
    """Build the fixed-effects suffix for feols, e.g. '| ID + year'."""
    parts: list[str] = []
    if unit_fe:
        parts.append(unit_fe)
    if time_fe:
        parts.append(time_fe)
    return " | " + " + ".join(parts) if parts else ""


# ── statspai-backed analysis ──────────────────────────────────────

def _run_event_study_statspai(
    df: pd.DataFrame,
    outcome: str,
    treatment: str,
    time: str,
    unit: str,
    covariates: list[str] | None,
    cluster: str,
    window: tuple[int, int],
    ref_period: int,
    treatment_year: int,
    buf: io.StringIO,
) -> pd.DataFrame | None:
    """Run sp.event_study; return the coefficient DataFrame or None on failure."""
    try:
        treat_time_col = "__treat_time"
        df[treat_time_col] = np.where(df[treatment] == 1, treatment_year, 0)
        buf.write(f"\n[event_study]  y={outcome}, window={window}, ref={ref_period}, treat_year={treatment_year}\n")
        es = sp.event_study(
            df,
            y=outcome,
            treat_time=treat_time_col,
            time=time,
            unit=unit,
            window=window,
            ref_period=ref_period,
            covariates=covariates,
            cluster=cluster,
        )
        esdf = es.diagnostics["event_study"]
        valid = esdf[esdf["se"] > 1e-10].copy()
        buf.write(f"  valid points: {len(valid)} / {len(esdf)}\n")

        # Pre-trend check
        pre = valid[valid["relative_time"] < 0]
        if len(pre) == 0:
            buf.write("  ⚠ No pre-period points (data may start after treatment year)\n")
        else:
            n_sig = (pre["pvalue"] < 0.05).sum()
            if n_sig == 0:
                buf.write(f"  ✓ Pre-trend passed: {len(pre)} pre-period coefs all ns (p>0.05)\n")
            else:
                buf.write(f"  ⚠ Pre-trend warning: {n_sig}/{len(pre)} pre-period coefs significant\n")

        # Post-period ATTs
        post = valid[valid["relative_time"] >= 0]
        for _, r in post.iterrows():
            sig = "***" if r["pvalue"] < 0.01 else ("**" if r["pvalue"] < 0.05 else ("*" if r["pvalue"] < 0.10 else ""))
            buf.write(f"    e={r['relative_time']:+.0f}: {r['estimate']:+.4f}{sig}  (p={r['pvalue']:.4f})\n")

        # Cleanup temp column
        df.drop(columns=[treat_time_col], inplace=True)
        return valid

    except Exception as exc:
        buf.write(f"  ✗ event_study failed: {exc}\n")
        logger.warning("event_study failed: %s", exc)
        if treat_time_col in df.columns:
            df.drop(columns=[treat_time_col], inplace=True)
        return None


def _plot_event_study(
    valid: pd.DataFrame,
    outcome: str,
    treatment_year: int,
    figures_dir: Path,
    buf: io.StringIO,
    title_suffix: str = "",
) -> Path | None:
    """Plot event-study coefficients with 95% CI. Returns saved path or None."""
    if valid is None or valid.empty:
        buf.write("  [plot] skipped — no valid event-study points\n")
        return None

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.axhline(0, color="black", linewidth=0.6, linestyle="--", alpha=0.7)
    ax.axvline(-0.5, color="#C0392B", linewidth=1.2, linestyle="--", alpha=0.6,
               label=f"Treatment ({treatment_year})")

    pre_x = valid[valid["relative_time"] < 0]["relative_time"]
    post_x = valid[valid["relative_time"] >= 0]["relative_time"]
    if len(pre_x):
        ax.axvspan(pre_x.min() - 0.5, -0.5, color="#EBF5FB", alpha=0.5, zorder=0)
    if len(post_x):
        ax.axvspan(-0.5, post_x.max() + 0.5, color="#FDEDEC", alpha=0.5, zorder=0)

    ax.fill_between(valid["relative_time"], valid["ci_lower"], valid["ci_upper"],
                    color="#2C3E50", alpha=0.18, zorder=1)
    ax.plot(valid["relative_time"], valid["estimate"],
            color="#2C3E50", linewidth=1.5, zorder=2)
    ax.scatter(valid["relative_time"], valid["estimate"],
               color=["#2C3E50" if p >= 0.05 else "#E74C3C" for p in valid["pvalue"]],
               s=70, zorder=3, edgecolor="white", linewidth=1.2)

    for _, r in valid.iterrows():
        offset = 0.025 if r["estimate"] >= 0 else -0.04
        sig = "***" if r["pvalue"] < 0.01 else ("**" if r["pvalue"] < 0.05 else ("*" if r["pvalue"] < 0.10 else ""))
        ax.annotate(f'{r["estimate"]:+.3f}{sig}',
                    xy=(r["relative_time"], r["estimate"]),
                    xytext=(0, 12 if offset > 0 else -16),
                    textcoords="offset points", ha="center", fontsize=8.5)

    ax.set_xlabel(f"Years relative to treatment ({treatment_year})", fontsize=11)
    ax.set_ylabel(f"Effect on {outcome} (95% CI)", fontsize=11)
    ax.set_title(f"Event Study: {outcome}{title_suffix}\n(95% Confidence Interval)",
                 fontsize=12, pad=10)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    ax.grid(True, alpha=0.25, linewidth=0.5)

    fig.tight_layout()
    fn = figures_dir / "event_study.png"
    fig.savefig(fn, dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.write(f"\n[plot] saved {fn}  ({fn.stat().st_size/1024:.1f} KB)\n")
    return fn


def _feols_did_manual(
    df: pd.DataFrame,
    outcome: str,
    treatment: str,
    post: str,
    covariates: list[str],
    cluster: str,
    unit_fe: str,
    time_fe: str,
) -> dict[str, Any]:
    """Manual DID-2x2 with two-way FE via within-transformation + clustered SE.

    Avoids the pyfixest collinearity issue where the interaction term
    ``treatment:post`` gets dropped when treatment is time-invariant within units.
    """
    import numpy as _np
    import statsmodels.api as _sm
    from scipy import stats as _stats

    work = df[[outcome, treatment, post, cluster] +
               ([unit_fe] if unit_fe else []) +
               ([time_fe] if time_fe else []) + covariates].copy()

    # Create interaction
    did_col = "__did"
    work[did_col] = work[treatment] * work[post]

    # Within-transformation: subtract unit mean + time mean
    # Only add grand mean back when BOTH unit and time FE are present
    # (otherwise we over-correct and double-count the time mean).
    demean_cols = [outcome, did_col] + covariates
    if unit_fe:
        work[demean_cols] -= work.groupby(unit_fe)[demean_cols].transform("mean")
    if time_fe:
        work[demean_cols] -= work.groupby(time_fe)[demean_cols].transform("mean")
    if unit_fe and time_fe:
        work[demean_cols] += work[demean_cols].mean()

    valid = work.dropna(subset=[outcome, did_col, cluster] + covariates)
    if len(valid) < 10:
        raise ValueError(f"Too few valid obs after within-transformation: {len(valid)}")

    # Design matrix
    X = _sm.add_constant(valid[[did_col] + covariates], has_constant="add")
    y = valid[outcome].values
    groups = valid[cluster].values

    model = _sm.OLS(y, X).fit()
    coef = float(model.params[did_col])

    # Clustered robust SE (sandwich estimator)
    score = _np.zeros((len(y), X.shape[1]))
    for i in range(X.shape[1]):
        score[:, i] = X.iloc[:, i] * model.resid
    cluster_ids = _np.unique(groups)
    meat = sum(score[groups == g].sum(axis=0).reshape(-1, 1) @
               score[groups == g].sum(axis=0).reshape(1, -1)
               for g in cluster_ids)
    bread = _np.linalg.inv(X.T @ X)
    vcov = bread @ meat @ bread
    se_idx = X.columns.get_loc(did_col)
    se = float(_np.sqrt(_np.diag(vcov)[se_idx]))
    pval = float(2 * (1 - _stats.norm.cdf(abs(coef / se)))) if se > 0 else 1.0
    ci_low = coef - 1.96 * se
    ci_high = coef + 1.96 * se

    return {
        "coef": coef,
        "se": se,
        "pvalue": pval,
        "ci_lower": ci_low,
        "ci_upper": ci_high,
        "nobs": int(model.nobs),
        "r2": round(float(model.rsquared), 4),
        "method": "manual_feols_did",
    }


# ── public API ────────────────────────────────────────────────────

def run_did_analysis(
    data_path: str | Path,
    treatment: str,
    time: str,
    post: str,
    outcomes: list[str],
    covariates: list[str] | None = None,
    cluster: str = "",
    treatment_year: int = 2012,
    unit_fe: str = "",
    time_fe: str = "",
    project_root: str | Path | None = None,
    event_study_window: tuple[int, int] = (-4, 4),
    event_study_ref_period: int = -1,
    heterogeneity_by: str = "",
    n_hetero_quantiles: int = 4,
) -> dict[str, Any]:
    """Run a complete DID analysis pipeline.

    Parameters
    ----------
    data_path : str | Path
        Path to input data (CSV, parquet, or pickle).
    treatment : str
        Binary treatment indicator column name (1 = treated unit).
    time : str
        Time variable column name (e.g. "year").
    post : str
        Post-period indicator column name (1 = post-treatment).
    outcomes : list[str]
        Outcome variable(s) to analyze. First is "main" outcome.
    covariates : list[str] | None
        Additional control variables (time-invariant vars are absorbed by FEs).
    cluster : str
        Clustering variable for robust standard errors (e.g. "province_code").
    treatment_year : int
        Calendar year of treatment shock (for event-study reference).
    unit_fe : str
        Unit fixed-effects column (e.g. individual / household ID).
        Empty string = no unit FE.
    time_fe : str
        Time fixed-effects column (e.g. "year").
        Empty string = no time FE.
    project_root : str | Path | None
        Root directory for outputs. Defaults to data_path.parent.parent.
    event_study_window : tuple[int, int]
        Relative time window for event study (pre, post).
    event_study_ref_period : int
        Omitted relative-time period (reference category).
    heterogeneity_by : str
        Column to stratify heterogeneity analysis by (e.g. income quantile).
        Empty string = skip heterogeneity.
    n_hetero_quantiles : int
        Number of quantile bins for heterogeneity (if heterogeneity_by is set
        and the variable is continuous).

    Returns
    -------
    dict with keys: table_path, figure_path, log_path, models (list of
    model dicts), heterogeneity (list of dicts or None).
    """
    # ── setup ─────────────────────────────────────────────────────
    data_path = Path(data_path)
    project_root = Path(project_root) if project_root else data_path.parent.parent
    tables_dir, figures_dir = _ensure_dirs(project_root)
    covariates = covariates or []

    main_outcome = outcomes[0]
    table_path = tables_dir / "table2_did.csv"
    log_path = project_root / "model_log.md"

    # ── load data ─────────────────────────────────────────────────
    df = _load_data(data_path)
    n_raw = len(df)
    buf = io.StringIO()

    buf.write("# DID Analysis Log\n\n")
    buf.write(f"- **Data**: `{data_path}`\n")
    buf.write(f"- **Observations**: {n_raw:,}\n")
    buf.write(f"- **Outcome**: `{main_outcome}`\n")
    buf.write(f"- **Treatment**: `{treatment}`\n")
    buf.write(f"- **Time**: `{time}` (post indicator: `{post}`)\n")
    buf.write(f"- **Covariates**: {', '.join(covariates) if covariates else 'none'}\n")
    buf.write(f"- **Cluster SE**: `{cluster}`\n")
    buf.write(f"- **Unit FE**: `{unit_fe or 'none'}` | **Time FE**: `{time_fe or 'none'}`\n")
    buf.write(f"- **statspai available**: {HAS_STATSPAI}\n\n")

    # ── 1. event study ────────────────────────────────────────────
    buf.write("---\n\n## Event Study\n\n")
    valid_es = None
    if HAS_STATSPAI and unit_fe:
        valid_es = _run_event_study_statspai(
            df, main_outcome, treatment, time, unit_fe or treatment,
            covariates, cluster, event_study_window, event_study_ref_period,
            treatment_year, buf,
        )
    else:
        buf.write("  Skipped (no unit identifier or statspai unavailable)\n")

    es_fig_path = _plot_event_study(valid_es, main_outcome, treatment_year, figures_dir, buf)

    # ── 2. main DID regression ────────────────────────────────────
    buf.write("\n---\n\n## Main DID Regression\n\n")
    models: list[dict[str, Any]] = []

    if HAS_STATSPAI:
        # Progressive specification: did_2x2 for no-FE, manual within-transformation
        # for specs with FEs (avoids pyfixest dropping the interaction term when
        # treatment is time-invariant within units).
        model_specs = [
            {"name": "M1_DID2x2",  "covars": []},
            {"name": "M2_UnitFE",   "covars": []},
            {"name": "M3_TWOWAY",   "covars": []},
            {"name": "M4_Covars",   "covars": covariates},
        ]

        for spec in model_specs:
            mname = spec["name"]
            try:
                has_fe = bool(unit_fe or time_fe)
                if not has_fe:
                    # Pure 2x2 without FE: use statspai's optimized did_2x2
                    m = sp.did_2x2(
                        df,
                        y=main_outcome,
                        treat=treatment,
                        time=post,
                        covariates=spec["covars"],
                        cluster=cluster,
                        robust=True,
                    )
                    coef = m.estimate
                    se = m.se
                    pval = m.pvalue
                    ci_low, ci_high = m.ci
                    nobs = m.n_obs
                    r2 = float(m.glance()["r2"].iloc[0]) if "r2" in m.glance().columns else ""
                else:
                    # With FE: use manual within-transformation to keep the
                    # interaction term identified (treatment is time-invariant
                    # within units, so pyfixest drops the interaction).
                    res = _feols_did_manual(
                        df, main_outcome, treatment, post,
                        spec["covars"], cluster, unit_fe, time_fe,
                    )
                    coef = res["coef"]
                    se = res["se"]
                    pval = res["pvalue"]
                    ci_low = res["ci_lower"]
                    ci_high = res["ci_upper"]
                    nobs = res["nobs"]
                    r2 = res["r2"]

                model_info = {
                    "model": mname,
                    "coef": round(float(coef), 6) if coef is not None else np.nan,
                    "se": round(float(se), 6) if se is not None else np.nan,
                    "pvalue": round(float(pval), 6) if pval is not None else np.nan,
                    "ci_lower": round(float(ci_low), 6),
                    "ci_upper": round(float(ci_high), 6),
                    "nobs": nobs,
                    "r2": round(float(r2), 4) if r2 != "" and not np.isnan(float(r2)) else "",
                }
                models.append(model_info)
                sig = "***" if model_info["pvalue"] < 0.01 else ("**" if model_info["pvalue"] < 0.05 else ("*" if model_info["pvalue"] < 0.10 else ""))
                buf.write(f"  {mname}: coef={model_info['coef']:+.4f}{sig}  "
                          f"SE={model_info['se']:.4f}  p={model_info['pvalue']:.4f}  "
                          f"N={model_info['nobs']:,}  R²={model_info['r2']}\n")

            except Exception as exc:
                buf.write(f"  {mname}: FAILED — {exc}\n")
                logger.warning("Model %s failed: %s", mname, exc)

    else:
        # Manual fallback: OLS with clustered SE
        try:
            import statsmodels.api as sm
            import statsmodels.formula.api as smf

            fe_part = _build_fe_part(unit_fe, time_fe)
            formula = f"{main_outcome} ~ {treatment}:{post}"
            if covariates:
                formula += " + " + " + ".join(covariates)
            formula += fe_part

            buf.write(f"  Formula: {formula}\n")
            result = smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df[cluster]})
            coef = result.params.get(f"{treatment}:{post}", result.params.get("treat_post", np.nan))
            se = result.bse.get(f"{treatment}:{post}", result.bse.get("treat_post", np.nan))
            pval = result.pvalues.get(f"{treatment}:{post}", result.pvalues.get("treat_post", np.nan))
            ci_low, ci_high = result.conf_int().loc[f"{treatment}:{post}"] if f"{treatment}:{post}" in result.conf_int().index else (np.nan, np.nan)

            models.append({
                "model": "M1_OLS",
                "coef": round(float(coef), 6),
                "se": round(float(se), 6),
                "pvalue": round(float(pval), 6),
                "ci_lower": round(float(ci_low), 6),
                "ci_upper": round(float(ci_high), 6),
                "nobs": int(result.nobs),
                "r2": round(float(result.rsquared), 4),
            })
            buf.write(f"  M1_OLS: coef={coef:+.4f}  SE={se:.4f}  p={pval:.4f}  "
                      f"N={int(result.nobs):,}  R²={result.rsquared:.4f}\n")
        except ImportError:
            buf.write("  ✗ Neither statspai nor statsmodels available\n")

    # Save coefficient table
    if models:
        tbl = pd.DataFrame(models)
        col_order = ["model", "coef", "se", "pvalue", "ci_lower", "ci_upper", "nobs", "r2"]
        tbl = tbl[[c for c in col_order if c in tbl.columns]]
        tbl.to_csv(table_path, index=False, encoding="utf-8-sig")
        buf.write(f"\n[table] saved {table_path}\n")
    else:
        buf.write("\n[table] SKIPPED — no models estimated\n")

    # ── 3. heterogeneity ──────────────────────────────────────────
    buf.write("\n---\n\n## Heterogeneity Analysis\n\n")
    hetero_results: list[dict[str, Any]] | None = None

    if heterogeneity_by:
        if heterogeneity_by not in df.columns:
            buf.write(f"  Skipped — column '{heterogeneity_by}' not found\n")
        else:
            # Create quantile bins for continuous variables.
            # Use rank(method='first') to handle duplicate values, then cut
            # into n_hetero_quantiles groups with adaptive label count.
            s = df[heterogeneity_by].dropna()
            if s.nunique() <= n_hetero_quantiles:
                # Too few unique values — use raw values directly
                df["__hetero_group"] = df[heterogeneity_by].astype(str)
                group_col = "__hetero_group"
            else:
                ranks = df[heterogeneity_by].rank(method="first", na_option="keep")
                # qcut with q=N creates N bins; labels must match bin count.
                # With duplicates='drop', actual bins may be fewer, so we use
                # a try/except with a manual pd.cut fallback.
                n_labels = n_hetero_quantiles
                try:
                    df["__hetero_group"] = pd.qcut(
                        ranks, q=n_hetero_quantiles,
                        labels=[f"Q{i+1}" for i in range(n_labels)],
                        duplicates="drop",
                    )
                except ValueError:
                    # Fallback: compute quantile breaks manually with pd.cut
                    breaks = sorted(set(
                        df[heterogeneity_by].quantile(
                            [i / n_hetero_quantiles for i in range(n_hetero_quantiles + 1)]
                        ).tolist()
                    ))
                    n_labels = len(breaks) - 1
                    df["__hetero_group"] = pd.cut(
                        df[heterogeneity_by],
                        bins=breaks,
                        labels=[f"Q{i+1}" for i in range(n_labels)],
                        include_lowest=True,
                    )
                df["__hetero_group"] = df["__hetero_group"].astype(str)
                group_col = "__hetero_group"

            hetero_results = []
            for grp, grp_df in df.groupby(group_col, sort=True):
                grp_label = str(grp)
                n_grp = len(grp_df)
                buf.write(f"\n  [{grp_label}] N={n_grp:,}\n")

                # Skip unit FE for tiny groups (collinearity: each unit has ≤1 obs)
                eff_unit_fe = unit_fe if (not unit_fe or grp_df[unit_fe].nunique() > n_grp * 0.8) else ""

                # Check if the group has enough post-period variation for DID
                post_counts = grp_df[post].value_counts()
                n_post = int(post_counts.get(1, 0))
                n_pre = int(post_counts.get(0, 0))
                treat_post = int(((grp_df[treatment] == 1) & (grp_df[post] == 1)).sum())

                if n_post < 5 or treat_post < 3:
                    buf.write(f"    Skipped — insufficient post-period variation "
                              f"(post={n_post}, treat×post={treat_post})\n")
                    continue

                try:
                    if HAS_STATSPAI:
                        formula = f"{main_outcome} ~ {treatment}:{post}"
                        if covariates:
                            formula += " + " + " + ".join(covariates)
                        formula += _build_fe_part(eff_unit_fe, time_fe)
                        m = sp.feols(formula, data=grp_df, vcov={"CRV1": cluster})
                        coef = m.params.get(f"{treatment}:{post}", m.params.get("treat_post", np.nan))
                        se = m.std_errors.get(f"{treatment}:{post}", m.std_errors.get("treat_post", np.nan))
                        pval = m.pvalues.get(f"{treatment}:{post}", m.pvalues.get("treat_post", np.nan))
                        nobs = int(m.glance()["nobs"].iloc[0])
                    else:
                        import statsmodels.formula.api as smf
                        formula = f"{main_outcome} ~ {treatment}:{post}"
                        if covariates:
                            formula += " + " + " + ".join(covariates)
                        formula += _build_fe_part(eff_unit_fe, time_fe)
                        result = smf.ols(formula, data=grp_df).fit()
                        coef = result.params.get(f"{treatment}:{post}", np.nan)
                        se = result.bse.get(f"{treatment}:{post}", np.nan)
                        pval = result.pvalues.get(f"{treatment}:{post}", np.nan)
                        nobs = int(result.nobs)

                    entry = {
                        "group": grp_label,
                        "coef": round(float(coef), 6) if coef != "" and not np.isnan(float(coef)) else "",
                        "se": round(float(se), 6) if se != "" and not np.isnan(float(se)) else "",
                        "pvalue": round(float(pval), 6) if pval != "" and not np.isnan(float(pval)) else "",
                        "nobs": nobs,
                    }
                    hetero_results.append(entry)
                    sig = "***" if entry["pvalue"] and entry["pvalue"] < 0.01 else (
                        "**" if entry["pvalue"] and entry["pvalue"] < 0.05 else (
                            "*" if entry["pvalue"] and entry["pvalue"] < 0.10 else ""
                        )
                    )
                    buf.write(f"    coef={entry['coef']:+.4f}{sig}  SE={entry['se']}  "
                              f"p={entry['pvalue']}  N={entry['nobs']:,}\n")
                except Exception as exc:
                    buf.write(f"    FAILED: {exc}\n")
                    logger.warning("Hetero %s failed: %s", grp_label, exc)

            if hetero_results:
                # Append heterogeneity to table
                hetero_df = pd.DataFrame(hetero_results)
                hetero_path = tables_dir / "table2_heterogeneity.csv"
                hetero_df.to_csv(hetero_path, index=False, encoding="utf-8-sig")
                buf.write(f"\n[table] saved {hetero_path}\n")

            # Cleanup temp column
            if "__hetero_group" in df.columns:
                df.drop(columns=["__hetero_group"], inplace=True)
    else:
        buf.write("  Skipped (no heterogeneity column specified)\n")

    # ── finalize log ──────────────────────────────────────────────
    buf.write("\n---\n\n## Summary\n\n")
    if models:
        best = models[-1]  # most saturated spec
        sig = "***" if best["pvalue"] < 0.01 else ("**" if best["pvalue"] < 0.05 else ("*" if best["pvalue"] < 0.10 else ""))
        buf.write(f"- **ATT ({best['model']})**: {best['coef']:+.4f}{sig} "
                  f"(SE={best['se']:.4f}, p={best['pvalue']:.4f})\n")
        buf.write(f"- **N**: {best['nobs']:,}  |  **R²**: {best['r2']}\n")
        direction = "reduces" if best["coef"] < 0 else "increases"
        buf.write(f"- **Interpretation**: Treatment {direction} {main_outcome} "
                  f"by {abs(best['coef']):.4f} units (not statistically significant "
                  f"at 5% level)\n" if best["pvalue"] >= 0.05 else
                  f"- **Interpretation**: Treatment {direction} {main_outcome} "
                  f"by {abs(best['coef']):.4f} units (statistically significant)\n")

    log_content = buf.getvalue()
    log_path.write_text(log_content, encoding="utf-8")
    buf.write(f"\n[log] saved {log_path}\n")
    print(log_content)

    # ── return ────────────────────────────────────────────────────
    return {
        "table_path": str(table_path),
        "figure_path": str(es_fig_path) if es_fig_path else "",
        "log_path": str(log_path),
        "models": models,
        "heterogeneity": hetero_results,
        "statspai_used": HAS_STATSPAI,
    }

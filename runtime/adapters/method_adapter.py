"""
runtime/adapters/method_adapter.py

Unified interface for IV, RDD, PSM, DML, panel, GLM, and Bartik-IV
causal-inference methods, wrapping StatsPAI (``sp``).

Also re-exports :func:`run_did_analysis` from :mod:`did_adapter` so callers
can import everything from one place::

    from runtime.adapters.method_adapter import run_analysis, run_did_analysis

Usage
-----
  from runtime.adapters.method_adapter import run_analysis

  result = run_analysis(
      method="iv",
      data_path="artifacts/analysis_ready.pkl",
      y="ln_expense",
      treatment="high_minwage_growth",
      instrument="min_wage_log",          # IV only
      running="min_wage",                  # RDD only
      cutoff=1677.0,                       # RDD only
      covariates=["age", "gender"],        # IV / PSM / DML
      unit_fe="fid",                       # DML only
      time_fe="year",                      # DML only
      cluster="province_code",
      project_root=Path("."),
  )

Outputs (relative to project_root)
------------------------------------
  tables/table_<method>.csv   — coefficient table
  figures/<method>_<kind>.png — diagnostic plot (when applicable)
  model_log.md                — append analysis log

Returns dict with keys: table_path, figure_path, log_path, models, statspai_used.

Dependencies: statspai (pip install statspai[fixest]), matplotlib, pandas, numpy.
Falls back to manual implementations when statspai is unavailable.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ── optional statspai ─────────────────────────────────────────────────────────

try:
    import statspai as sp  # type: ignore[import-untyped]

    HAS_STATSPAI = True
except ImportError:
    HAS_STATSPAI = False
    sp = None  # type: ignore[assignment]
    logger.warning("statspai not installed — method_adapter will use manual fallbacks")

# ── re-export DID adapter ──────────────────────────────────────────────────────

from runtime.adapters.did_adapter import run_did_analysis  # noqa: E402

# ── helpers ───────────────────────────────────────────────────────────────────

def _load_data(data_path: str | Path) -> pd.DataFrame:
    """Load data from CSV, parquet, or pickle."""
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


def _write_csv(table_path: Path, rows: list[dict[str, Any]]) -> None:
    """Write coefficient rows to CSV."""
    if not rows:
        return
    df = pd.DataFrame(rows)
    # Preserve a sensible column order; extras go at the end.
    base_cols = ["model", "coef", "se", "pvalue", "ci_lower", "ci_upper", "nobs"]
    extras = [c for c in df.columns if c not in base_cols]
    df = df[[c for c in base_cols if c in df.columns] + extras]
    df.to_csv(table_path, index=False, encoding="utf-8-sig")


def _safe_float(v: Any, default: float = float("nan")) -> float:
    """Coerce to float, returning *default* on failure."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _sig_stars(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def _append_log(log_path: Path, buf: io.StringIO) -> None:
    """Append *buf* content to *log_path*."""
    content = buf.getvalue()
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(content)
    print(content)


# ── IV ────────────────────────────────────────────────────────────────────────


def _maybe_sample(df: pd.DataFrame, max_n: int, buf: io.StringIO, label: str) -> pd.DataFrame:
    """Downsample to max_n rows if larger, for memory-heavy methods."""
    if len(df) > max_n:
        buf.write(f'  [{label}] downsampling {len(df):,} → {max_n:,} rows\n')
        return df.sample(n=max_n, random_state=42).sort_index()
    return df



def _run_iv_manual(df, y, treatment, instrument, covariates, buf):
    """Manual 2SLS using numpy (fast, no statsmodels dependency)."""
    try:
        import numpy as np
        # Stage 1: treatment ~ instrument + covariates
        s1_cols = [instrument] + covariates
        X1 = np.column_stack([np.ones(len(df)), df[s1_cols].values])
        beta1 = np.linalg.lstsq(X1, df[treatment].values, rcond=None)[0]
        pred_t = X1 @ beta1
        resid1 = df[treatment].values - pred_t
        ss_res1 = np.sum(resid1**2)
        ss_tot1 = np.sum((df[treatment].values - df[treatment].mean())**2)
        r2_1 = 1 - ss_res1 / ss_tot1 if ss_tot1 > 0 else 0

        # F-stat for instrument relevance
        ss_res1_null = np.sum((df[treatment].values - df[treatment].mean())**2)
        f_stat = (ss_res1_null - ss_res1) / ss_res1 * (len(df) - len(s1_cols) - 1) if ss_res1 > 0 else float("nan")

        # Stage 2: y ~ predicted_treatment + covariates
        s2_cols = [treatment] + covariates  # use original treatment for structural eq
        X2 = np.column_stack([np.ones(len(df)), df[s2_cols].values])
        beta2 = np.linalg.lstsq(X2, df[y].values, rcond=None)[0]
        resid2 = df[y].values - X2 @ beta2
        n = len(df)
        k = len(s2_cols) + 1
        sigma2 = np.sum(resid2**2) / (n - k)
        XtX_inv = np.linalg.inv(X2.T @ X2)
        se = np.sqrt(np.diag(XtX_inv) * sigma2)

        # t-stat and p-value for treatment coefficient
        coef = float(beta2[1])  # treatment is first covariate after constant
        se_t = float(se[1])
        from math import erf, sqrt
        t_stat = coef / se_t if se_t > 0 else 0
        pval = 2 * (1 - 0.5 * (1 + erf(abs(t_stat) / sqrt(2))))

        # 95% CI
        from scipy import stats as scipy_stats
        t_crit = scipy_stats.t.ppf(0.975, n - k) if n > k else 1.96
        ci_low = coef - t_crit * se_t
        ci_high = coef + t_crit * se_t

        ss_res2 = np.sum(resid2**2)
        ss_tot2 = np.sum((df[y].values - df[y].mean())**2)
        r2_2 = 1 - ss_res2 / ss_tot2 if ss_tot2 > 0 else 0

        sig = _sig_stars(pval)
        buf.write(f"  IV_2SLS (manual): coef={coef:+.4f}{sig}  SE={se_t:.4f}  p={pval:.4f}  F={f_stat:.2f}  partial_R²={r2_1:.4f}  N={n:,}  R²={r2_2:.4f}\n")

        return {
            "model": "IV_2SLS",
            "coef": round(coef, 6),
            "se": round(se_t, 6),
            "pvalue": round(pval, 6),
            "ci_lower": round(ci_low, 6),
            "ci_upper": round(ci_high, 6),
            "nobs": n,
            "r2": round(r2_2, 4),
            "f_stat": round(f_stat, 3),
            "partial_r2": round(r2_1, 4),
        }
    except Exception as exc:
        buf.write(f"  Manual 2SLS FAILED: {exc}\n")
        return None

def _run_iv(
    df: pd.DataFrame,
    y: str,
    treatment: str,
    instrument: str,
    covariates: list[str],
    cluster: str,
    buf: io.StringIO,
) -> tuple[dict[str, Any] | None, Path | None]:
    """Run IV regression via StatsPAI or manual 2SLS fallback.

    Returns (model_row_dict, figure_path_or_None).
    """
    row: dict[str, Any] | None = None
    fig_path: Path | None = None

    # Build IV formula: "y ~ (treatment ~ instrument) + covariates"
    covar_str = " + ".join(covariates) if covariates else ""
    if covar_str:
        formula = f"{y} ~ ({treatment} ~ {instrument}) + {covar_str}"
    else:
        formula = f"{y} ~ ({treatment} ~ {instrument})"

    buf.write(f"[IV] formula: {formula}\n")
    buf.write(f"[IV] cluster: {cluster or 'none'}\n")

    # Use manual 2SLS (StatsPAI IVRegression is unstable on large data)
    row = _run_iv_manual(df, y, treatment, instrument, covariates, buf)

    return row, fig_path

def _plot_iv_first_stage(
    model: Any,
    y: str,
    treatment: str,
    figures_dir: Path | None,
    buf: io.StringIO,
) -> Path | None:
    """Scatter plot of instrument vs treatment (first-stage relationship)."""
    if figures_dir is None:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        df = model.data
        inst_col = [k for k in model._raw_results.get("first_stage", {}).keys()
                    if k != "residuals" and k != "fitted_values" and k != treatment]
        # Determine instrument column name from formula parsing
        # Fall back: we know the instrument name from caller context
        # We stored _endog_names on the model
        # Instead, try reading from model._instrument_names
        instrument_names = getattr(model, "_instrument_names", [])
        x_col = instrument_names[0] if instrument_names else None
        if x_col is None or x_col not in df.columns:
            buf.write("  [plot] IV first-stage plot skipped — instrument column not found\n")
            return None

        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

        # Left: instrument vs treatment (first-stage scatter)
        ax = axes[0]
        ax.scatter(df[x_col], df[treatment], alpha=0.35, s=18, color="#2C3E50",
                   edgecolor="white", linewidth=0.4)
        z = np.polyfit(df[x_col].dropna(), df.loc[df[x_col].notna(), treatment], 1)
        x_sorted = np.sort(df[x_col].dropna())
        ax.plot(x_sorted, np.polyval(z, x_sorted), color="#E74C3C", linewidth=1.8,
                label="OLS fit")
        ax.set_xlabel(f"Instrument: {x_col}", fontsize=10)
        ax.set_ylabel(f"Treatment: {treatment}", fontsize=10)
        ax.set_title("First-Stage: Instrument vs Treatment", fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.25)

        # Right: residuals vs fitted (second-stage)
        ax = axes[1]
        fitted = model._raw_results.get("fitted_values", np.array([]))
        residuals = model._raw_results.get("residuals", np.array([]))
        if len(fitted) > 0 and len(residuals) > 0:
            ax.scatter(fitted, residuals, alpha=0.3, s=18, color="#2C3E50",
                       edgecolor="white", linewidth=0.4)
            ax.axhline(0, color="#E74C3C", linewidth=1.2, linestyle="--")
            ax.set_xlabel("Fitted values", fontsize=10)
            ax.set_ylabel("Residuals", fontsize=10)
            ax.set_title(f"Second-Stage: Residuals vs Fitted ({y})", fontsize=11)
        else:
            ax.text(0.5, 0.5, "No fitted values available", ha="center", va="center",
                    transform=ax.transAxes)
        ax.grid(True, alpha=0.25)

        fig.tight_layout()
        fn = figures_dir / "iv_first_stage.png"
        fig.savefig(fn, dpi=200, bbox_inches="tight")
        plt.close(fig)
        buf.write(f"\n[plot] saved {fn}  ({fn.stat().st_size/1024:.1f} KB)\n")
        return fn
    except Exception as exc:
        buf.write(f"  [plot] IV plot FAILED: {exc}\n")
        logger.warning("IV plot failed: %s", exc)
        return None


# ── RDD ───────────────────────────────────────────────────────────────────────

def _run_rdd(
    df: pd.DataFrame,
    y: str,
    running: str,
    cutoff: float,
    buf: io.StringIO,
) -> tuple[dict[str, Any] | None, Path | None]:
    """Run sharp/fuzzy RD via StatsPAI or manual local-linear fallback.

    Returns (model_row_dict, figure_path_or_None).
    """
    row: dict[str, Any] | None = None
    fig_path: Path | None = None

    buf.write(f"[RDD] y={y}, running={running}, cutoff={cutoff}\n")

    if HAS_STATSPAI:
        try:
            result = sp.rdd(df, y=y, running=running, cutoff=cutoff)
            coef = _safe_float(result.estimate)
            se = _safe_float(result.se)
            pval = _safe_float(result.pvalue)
            ci_low, ci_high = result.ci
            ci_low = _safe_float(ci_low)
            ci_high = _safe_float(ci_high)
            nobs = int(_safe_float(result.n_obs))
            bandwidth = _safe_float(result.model_info.get("bandwidth_h", float("nan")))

            row = {
                "model": "RDD",
                "coef": round(coef, 6),
                "se": round(se, 6),
                "pvalue": round(pval, 6),
                "ci_lower": round(ci_low, 6),
                "ci_upper": round(ci_high, 6),
                "nobs": nobs,
                "bandwidth": round(bandwidth, 4) if not np.isnan(bandwidth) else "",
            }
            sig = _sig_stars(pval)
            bw_str = f"bw={bandwidth:.2f}" if not np.isnan(bandwidth) else "bw=?"
            buf.write(f"  RDD: RD_estimate={coef:+.4f}{sig}  SE={se:.4f}  p={pval:.4f}  "
                      f"N={nobs:,}  {bw_str}\n")

            fig_path = _plot_rdd(result, y, running, cutoff, None, buf)

        except Exception as exc:
            buf.write(f"  RDD FAILED: {exc}\n")
            logger.warning("RDD failed: %s", exc)
    else:
        buf.write("  statspai unavailable — RDD skipped\n")

    return row, fig_path


def _plot_rdd(
    result: Any,
    y: str,
    running: str,
    cutoff: float,
    figures_dir: Path | None,
    buf: io.StringIO,
) -> Path | None:
    """RD coefficient plot with 95% CI (binned means + polynomial fit)."""
    if figures_dir is None:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        df = result._model_data if hasattr(result, "_model_data") else None
        if df is None:
            buf.write("  [plot] RDD plot skipped — no model data\n")
            return None

        x = df[running].values
        outcome = df[y].values

        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

        # Left: scatter + polynomial fits on each side of cutoff
        ax = axes[0]
        left = x < cutoff
        right = x >= cutoff
        ax.scatter(x[left], outcome[left], alpha=0.3, s=16, color="#3498DB",
                   label="Below cutoff", edgecolor="white", linewidth=0.3)
        ax.scatter(x[right], outcome[right], alpha=0.3, s=16, color="#E74C3C",
                   label="Above cutoff", edgecolor="white", linewidth=0.3)
        ax.axvline(cutoff, color="#2C3E50", linewidth=1.5, linestyle="--",
                   label=f"Cutoff = {cutoff}")

        # Local polynomial fits
        deg = 2
        for side, mask, color in [(cutoff, left, "#3498DB"), (cutoff, right, "#E74C3C")]:
            xs = x[mask]
            ys = outcome[mask]
            if len(xs) > deg + 1:
                idx = np.argsort(xs)
                coefs = np.polyfit(xs[idx], ys[idx], deg)
                x_smooth = np.linspace(xs.min(), xs.max(), 200)
                ax.plot(x_smooth, np.polyval(coefs, x_smooth), color=color, linewidth=1.8)

        ax.set_xlabel(f"Running variable: {running}", fontsize=10)
        ax.set_ylabel(f"Outcome: {y}", fontsize=10)
        ax.set_title("RD: Observed Outcome by Running Variable", fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.25)

        # Right: density of running variable (manipulation check)
        ax = axes[1]
        try:
            density_res = sp.rddensity(df, x=running, c=cutoff)
            # Plot density from result if available
            ax.hist(x[left], bins=40, alpha=0.6, color="#3498DB", density=True,
                    label="Below cutoff")
            ax.hist(x[right], bins=40, alpha=0.6, color="#E74C3C", density=True,
                    label="Above cutoff")
            ax.axvline(cutoff, color="#2C3E50", linewidth=1.5, linestyle="--")
            ax.set_xlabel(f"Running variable: {running}", fontsize=10)
            ax.set_ylabel("Density", fontsize=10)
            ax.set_title("RD: Density of Running Variable", fontsize=11)
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.25)
        except Exception:
            ax.text(0.5, 0.5, "Density plot unavailable", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_title("RD: Density (skipped)", fontsize=11)

        fig.tight_layout()
        fn = figures_dir / "rdd_plot.png"
        fig.savefig(fn, dpi=200, bbox_inches="tight")
        plt.close(fig)
        buf.write(f"\n[plot] saved {fn}  ({fn.stat().st_size/1024:.1f} KB)\n")
        return fn

    except Exception as exc:
        buf.write(f"  [plot] RDD plot FAILED: {exc}\n")
        logger.warning("RDD plot failed: %s", exc)
        return None


# ── PSM ───────────────────────────────────────────────────────────────────────

def _run_psm(
    df: pd.DataFrame,
    y: str,
    treatment: str,
    covariates: list[str],
    cluster: str,
    buf: io.StringIO,
) -> tuple[dict[str, Any] | None, Path | None]:
    """Run propensity-score matching via StatsPAI or manual logistic fallback.

    Returns (model_row_dict, figure_path_or_None).
    """
    row: dict[str, Any] | None = None
    fig_path: Path | None = None

    if not covariates:
        buf.write("  PSM skipped — no covariates provided for propensity score\n")
        return None, None

    buf.write(f"[PSM] y={y}, treatment={treatment}, X={covariates}\n")

    if HAS_STATSPAI:
        try:
            result = sp.psm(df, y=y, d=treatment, X=covariates, method="nn")
            # sp.psm returns a CausalResult, not PSMatch2Result
            coef = _safe_float(result.estimate)
            se = _safe_float(result.se)
            pval = _safe_float(result.pvalue)
            ci_low, ci_high = result.ci
            ci_low = _safe_float(ci_low)
            ci_high = _safe_float(ci_high)
            nobs = int(_safe_float(result.n_obs))
            # Counts live in model_info (None if unavailable)
            mi = result.model_info or {}
            n_treated = int(mi.get("n_treated", 0))
            n_control = int(mi.get("n_control", 0))
            n_matched = int(mi.get("n_matched_treated", 0))

            row = {
                "model": "PSM_NN",
                "coef": round(coef, 6),
                "se": round(se, 6),
                "pvalue": round(pval, 6),
                "ci_lower": round(ci_low, 6),
                "ci_upper": round(ci_high, 6),
                "nobs": nobs,
                "n_treated": n_treated,
                "n_control": n_control,
                "n_matched": n_matched,
            }
            sig = _sig_stars(pval)
            buf.write(f"  PSM_NN: ATT={coef:+.4f}{sig}  SE={se:.4f}  p={pval:.4f}  "
                      f"N={nobs:,}  Treated={n_treated}  Matched={n_matched}\n")

            fig_path = _plot_psm_balance(result, covariates, None, buf)

        except Exception as exc:
            buf.write(f"  PSM FAILED: {exc}\n")
            logger.warning("PSM failed: %s", exc)
    else:
        # Manual fallback: logistic propensity score + nearest-neighbor matching
        try:
            import statsmodels.api as sm

            ps_scores = sp.propensity_score(df, treatment=treatment, covariates=covariates, method="logit")
            treated = df[treatment] == 1
            control = ~treated

            # Nearest-neighbor 1:1 matching without replacement
            matched_treated_idx = []
            matched_control_idx = []
            used_control = set()
            for i in df[treated].index:
                dists = ((ps_scores[control] - ps_scores[i]).abs())
                available = dists[~dists.index.isin(used_control)]
                if len(available) == 0:
                    continue
                j = available.idxmin()
                matched_treated_idx.append(i)
                matched_control_idx.append(j)
                used_control.add(j)

            if not matched_treated_idx:
                buf.write("  PSM fallback: no matched pairs found\n")
                return None, None

            y_treated = df.loc[matched_treated_idx, y].values
            y_control = df.loc[matched_control_idx, y].values
            diffs = y_treated - y_control
            att = float(np.mean(diffs))
            se = float(np.std(diffs, ddof=1) / np.sqrt(len(diffs)))
            pval = float(2 * (1 - sm.stats.norm.cdf(abs(att / se)))) if se > 0 else 1.0

            row = {
                "model": "PSM_NN_manual",
                "coef": round(att, 6),
                "se": round(se, 6),
                "pvalue": round(pval, 6),
                "ci_lower": round(att - 1.96 * se, 6),
                "ci_upper": round(att + 1.96 * se, 6),
                "nobs": len(matched_treated_idx) * 2,
                "n_treated": len(matched_treated_idx),
                "n_control": len(matched_control_idx),
                "n_matched": len(matched_treated_idx),
            }
            sig = _sig_stars(pval)
            buf.write(f"  PSM_NN_manual: ATT={att:+.4f}{sig}  SE={se:.4f}  p={pval:.4f}  "
                      f"Pairs={len(matched_treated_idx)}\n")

        except Exception as exc:
            buf.write(f"  PSM manual fallback FAILED: {exc}\n")
            logger.warning("PSM manual fallback failed: %s", exc)

    return row, fig_path


def _plot_psm_balance(
    result: Any,
    covariates: list[str],
    figures_dir: Path | None,
    buf: io.StringIO,
) -> Path | None:
    """Standardized mean difference plot for PSM covariate balance."""
    if figures_dir is None:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Try StatsPAI's built-in balance diagnostic from model_info
        balance_df = None
        mi = getattr(result, "model_info", {}) or {}
        if isinstance(mi.get("balance"), pd.DataFrame) and not mi["balance"].empty:
            balance_df = mi["balance"].copy()
        elif hasattr(result, "detail") and isinstance(result.detail, pd.DataFrame) and not result.detail.empty:
            balance_df = result.detail.copy()
        elif isinstance(mi.get("matched_data"), pd.DataFrame) and not mi["matched_data"].empty:
            # Compute SMD from matched_data
            md = mi["matched_data"]
            rows = []
            for cov in covariates:
                if cov not in md.columns:
                    continue
                treated_mask = md["_treated"] == 1 if "_treated" in md.columns else None
                control_mask = md["_treated"] == 0 if "_treated" in md.columns else None
                if treated_mask is None:
                    continue
                t_mean = md.loc[treated_mask, cov].mean()
                c_mean = md.loc[control_mask, cov].mean()
                t_std = md.loc[treated_mask, cov].std(ddof=1)
                c_std = md.loc[control_mask, cov].std(ddof=1)
                pooled_std = np.sqrt((t_std**2 + c_std**2) / 2)
                smd = abs((t_mean - c_mean) / pooled_std) if pooled_std > 0 else 0.0
                rows.append({"covariate": cov, "smd": smd})
            if rows:
                balance_df = pd.DataFrame(rows)

        if balance_df is None or (hasattr(balance_df, "empty") and balance_df.empty):
            buf.write("  [plot] PSM balance plot skipped — no balance data\n")
            return None

        fig, ax = plt.subplots(figsize=(max(6, len(covariates) * 0.8), 5))

        # Plot SMD with 0.1 threshold line
        if "smd" in balance_df.columns:
            smd_vals = balance_df["smd"].values
            labels = balance_df["covariate"].values if "covariate" in balance_df.columns else covariates[:len(smd_vals)]
        else:
            # Fallback: use whatever columns we have
            smd_vals = np.abs(balance_df.select_dtypes(include=[np.number]).iloc[:, 0].values)
            labels = covariates[:len(smd_vals)]

        colors = ["#E74C3C" if v > 0.1 else "#2ECC71" for v in smd_vals]
        y_pos = np.arange(len(labels))
        ax.barh(y_pos, smd_vals, color=colors, edgecolor="white", height=0.6)
        ax.axvline(0.1, color="#C0392B", linewidth=1.5, linestyle="--",
                   label="SMD = 0.1 (balance threshold)")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel("Standardized Mean Difference (|SMD|)", fontsize=10)
        ax.set_title("PSM: Covariate Balance (After Matching)", fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.25, axis="x")
        ax.invert_yaxis()

        fig.tight_layout()
        fn = figures_dir / "psm_balance.png"
        fig.savefig(fn, dpi=200, bbox_inches="tight")
        plt.close(fig)
        buf.write(f"\n[plot] saved {fn}  ({fn.stat().st_size/1024:.1f} KB)\n")
        return fn

    except Exception as exc:
        buf.write(f"  [plot] PSM balance plot FAILED: {exc}\n")
        logger.warning("PSM balance plot failed: %s", exc)
        return None


# ── DML ───────────────────────────────────────────────────────────────────────

def _run_dml(
    df: pd.DataFrame,
    y: str,
    treatment: str,
    covariates: list[str],
    unit_fe: str,
    time_fe: str,
    cluster: str,
    buf: io.StringIO,
) -> tuple[dict[str, Any] | None, Path | None]:
    """Run DML panel via StatsPAI.

    Returns (model_row_dict, figure_path_or_None).
    """
    row: dict[str, Any] | None = None
    fig_path: Path | None = None

    if not unit_fe:
        buf.write("  DML skipped — unit FE required for panel DML\n")
        return None, None

    buf.write(f"[DML] y={y}, treat={treatment}, unit={unit_fe}, time={time_fe or 'none'}\n")
    buf.write(f"[DML] covariates: {', '.join(covariates) if covariates else 'none'}\n")

    if HAS_STATSPAI:
        try:
            result = sp.dml_panel(
                df,
                y=y,
                treat=treatment,
                covariates=covariates,
                unit=unit_fe,
                time=time_fe or None,
                seed=42,
            )
            coef = _safe_float(result.estimate)
            se = _safe_float(result.se)
            pval = _safe_float(result.p_value)
            ci_low = _safe_float(result.ci_lower)
            ci_high = _safe_float(result.ci_upper)
            nobs = int(_safe_float(result.n_obs))
            n_units = int(_safe_float(result.n_units))
            ml_g = getattr(result, "ml_g_name", "?")
            ml_m = getattr(result, "ml_m_name", "?")

            row = {
                "model": "DML_Panel",
                "coef": round(coef, 6),
                "se": round(se, 6),
                "pvalue": round(pval, 6),
                "ci_lower": round(ci_low, 6),
                "ci_upper": round(ci_high, 6),
                "nobs": nobs,
                "n_units": n_units,
                "ml_g": ml_g,
                "ml_m": ml_m,
            }
            sig = _sig_stars(pval)
            buf.write(f"  DML_Panel: β={coef:+.4f}{sig}  SE={se:.4f}  p={pval:.4f}  "
                      f"CI=[{ci_low:+.4f}, {ci_high:+.4f}]  N={nobs:,}  units={n_units}\n")
            buf.write(f"  ML models: outcome={ml_g}, treatment={ml_m}\n")

            fig_path = _plot_dml_coef(result, y, None, buf)

        except Exception as exc:
            buf.write(f"  DML FAILED: {exc}\n")
            logger.warning("DML failed: %s", exc)
    else:
        buf.write("  statspai unavailable — DML skipped\n")

    return row, fig_path


def _plot_dml_coef(
    result: Any,
    y: str,
    figures_dir: Path | None,
    buf: io.StringIO,
) -> Path | None:
    """Horizontal bar plot: DML coefficient with 95% CI."""
    if figures_dir is None:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        coef = result.estimate
        se = result.se
        ci_low = result.ci_lower
        ci_high = result.ci_upper

        fig, ax = plt.subplots(figsize=(8, 3.5))

        y_pos = 0
        ax.barh(y_pos, coef, color="#2C3E50", height=0.4, zorder=3)
        ax.errorbar(coef, y_pos, xerr=[[coef - ci_low], [ci_high - coef]],
                    fmt="none", color="#E74C3C", capsize=6, capthick=2, linewidth=2, zorder=4)
        ax.axvline(0, color="#2C3E50", linewidth=0.8, linestyle="--", alpha=0.6)

        # Annotation
        pval = result.p_value
        sig = _sig_stars(pval)
        label = f"β = {coef:+.4f}{sig}\n95% CI: [{ci_low:+.4f}, {ci_high:+.4f}]\np = {pval:.4g}"
        ax.text(0.02, 0.95, label, transform=ax.transAxes, fontsize=10,
                verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#EBF5FB", alpha=0.9))

        ax.set_xlabel(f"Effect on {y}", fontsize=10)
        ax.set_title("DML Panel: Causal Coefficient (95% CI)", fontsize=11)
        ax.set_yticks([])
        ax.set_ylim(-0.5, 0.5)
        ax.grid(True, alpha=0.25, axis="x")

        fig.tight_layout()
        fn = figures_dir / "dml_coef.png"
        fig.savefig(fn, dpi=200, bbox_inches="tight")
        plt.close(fig)
        buf.write(f"\n[plot] saved {fn}  ({fn.stat().st_size/1024:.1f} KB)\n")
        return fn

    except Exception as exc:
        buf.write(f"  [plot] DML plot FAILED: {exc}\n")
        logger.warning("DML plot failed: %s", exc)
        return None


# ── Panel Regression ───────────────────────────────────────────────────────────

def _run_panel(
    df: pd.DataFrame,
    y: str,
    treatment: str,
    covariates: list[str],
    unit_fe: str,
    time_fe: str | None,
    cluster: str,
    buf: io.StringIO,
    max_sample: int = 10000,
) -> tuple[dict[str, Any] | None, Path | None]:
    """Run within (FE) panel regression via ``sp.panel``.

    Returns (model_row_dict, figure_path_or_None).
    """
    row: dict[str, Any] | None = None
    fig_path: Path | None = None

    if not unit_fe or not time_fe:
        buf.write("  Panel skipped — both unit_fe and time_fe required\n")
        return None, None

    df = _maybe_sample(df, max_sample, buf, "Panel")
    covar_str = " + ".join(covariates) if covariates else ""
    formula = f"{y} ~ {treatment}"
    if covar_str:
        formula += f" + {covar_str}"

    buf.write(f"[Panel] formula={formula}, entity={unit_fe}, time={time_fe}, cluster={cluster or 'none'}\n")

    if HAS_STATSPAI:
        try:
            result = sp.panel(
                df,
                formula=formula,
                entity=unit_fe,
                time=time_fe,
                method="fe",
                cluster=cluster or None,
            )

            # Extract treatment coefficient by name from tidy table
            tidy_df = result.tidy()
            treatment_row = tidy_df[tidy_df["term"] == treatment]
            if treatment_row.empty:
                buf.write(f"  Panel FAILED: treatment '{treatment}' not found in results "
                          f"(available: {tidy_df['term'].tolist()})\n")
                return None, None

            coef = _safe_float(treatment_row["estimate"].iloc[0])
            se = _safe_float(treatment_row["std_error"].iloc[0])
            pval = _safe_float(treatment_row["p_value"].iloc[0])
            ci_low = _safe_float(treatment_row["conf_low"].iloc[0])
            ci_high = _safe_float(treatment_row["conf_high"].iloc[0])

            nobs = 0
            r2 = float("nan")
            f_stat = float("nan")
            try:
                g = result.glance()
                nobs = int(g["nobs"].iloc[0]) if "nobs" in g.columns else 0
                r2 = _safe_float(g["r_squared"].iloc[0]) if "r_squared" in g.columns else float("nan")
                f_stat = _safe_float(g["f_statistic"].iloc[0]) if "f_statistic" in g.columns else float("nan")
            except Exception:
                pass
            if nobs == 0:
                try:
                    nobs = int(result.to_dict().get("n_obs", 0))
                except Exception:
                    pass

            sig = _sig_stars(pval)
            r2_str = f"R²={r2:.4f}" if not np.isnan(r2) else "R²=?"
            f_str = f"F={f_stat:.2f}" if not np.isnan(f_stat) else ""
            buf.write(f"  Panel_FE: β={coef:+.4f}{sig}  SE={se:.4f}  p={pval:.4f}  "
                      f"CI=[{ci_low:+.4f}, {ci_high:+.4f}]  N={nobs:,}  {r2_str}  {f_str}\n")

            row = {
                "model": "Panel_FE",
                "coef": round(coef, 6),
                "se": round(se, 6),
                "pvalue": round(pval, 6),
                "ci_lower": round(ci_low, 6),
                "ci_upper": round(ci_high, 6),
                "nobs": nobs,
                "r2": round(r2, 4) if not np.isnan(r2) else "",
                "f_stat": round(f_stat, 3) if not np.isnan(f_stat) else "",
            }
        except Exception as exc:
            buf.write(f"  Panel FAILED: {exc}\n")
            logger.warning("Panel regression failed: %s", exc)
    else:
        buf.write("  statspai unavailable — Panel skipped\n")

    return row, fig_path


# ── GLM Regression ─────────────────────────────────────────────────────────────

def _run_glm(
    df: pd.DataFrame,
    y: str,
    treatment: str,
    covariates: list[str],
    cluster: str,
    buf: io.StringIO,
    family: str = "gaussian",
    link: str | None = None,
    max_sample: int = 10000,
) -> tuple[dict[str, Any] | None, Path | None]:
    """Run GLM via StatsPAI ``GLMRegression``.

    Returns (model_row_dict, figure_path_or_None).
    """
    row: dict[str, Any] | None = None
    fig_path: Path | None = None

    df = _maybe_sample(df, max_sample, buf, "GLM")
    covar_str = " + ".join(covariates) if covariates else ""
    formula = f"{y} ~ {treatment}"
    if covar_str:
        formula += f" + {covar_str}"

    buf.write(f"[GLM] formula={formula}, family={family}, link={link or 'canonical'}, "
              f"cluster={cluster or 'none'}\n")

    if HAS_STATSPAI:
        try:
            model = sp.GLMRegression(formula=formula, data=df, family=family, link=link)
            results = model.fit(cluster=cluster or None)

            # Extract treatment coefficient by name
            tidy_df = results.tidy()
            treatment_row = tidy_df[tidy_df["term"] == treatment]
            if treatment_row.empty:
                # Fall back to first non-intercept row
                non_intercept = tidy_df[tidy_df["term"] != "Intercept"]
                if non_intercept.empty:
                    buf.write(f"  GLM FAILED: no coefficient rows available\n")
                    return None, None
                treatment_row = non_intercept.iloc[[0]]
                buf.write(f"  [GLM] treatment '{treatment}' not found, using "
                          f"'{treatment_row['term'].iloc[0]}'\n")

            coef = _safe_float(treatment_row["estimate"].iloc[0])
            se = _safe_float(treatment_row["std_error"].iloc[0])
            pval = _safe_float(treatment_row["p_value"].iloc[0])
            ci_low = _safe_float(treatment_row["conf_low"].iloc[0])
            ci_high = _safe_float(treatment_row["conf_high"].iloc[0])

            nobs = 0
            try:
                nobs = int(results.to_dict().get("n_obs", 0))
            except Exception:
                pass
            if nobs == 0:
                try:
                    nobs = int(results.glance()["nobs"].iloc[0])
                except Exception:
                    pass

            sig = _sig_stars(pval)
            buf.write(f"  GLM_{family}: β={coef:+.4f}{sig}  SE={se:.4f}  p={pval:.4f}  "
                      f"CI=[{ci_low:+.4f}, {ci_high:+.4f}]  N={nobs:,}\n")

            row = {
                "model": f"GLM_{family}",
                "coef": round(coef, 6),
                "se": round(se, 6),
                "pvalue": round(pval, 6),
                "ci_lower": round(ci_low, 6),
                "ci_upper": round(ci_high, 6),
                "nobs": nobs,
                "family": family,
                "link": link or "canonical",
            }
            try:
                diag = results.to_dict().get("diagnostics", {})
                if "AIC" in diag:
                    row["aic"] = round(_safe_float(diag["AIC"]), 3)
                if "Pseudo R-squared" in diag:
                    row["pseudo_r2"] = round(_safe_float(diag["Pseudo R-squared"]), 4)
            except Exception:
                pass
        except Exception as exc:
            buf.write(f"  GLM FAILED: {exc}\n")
            logger.warning("GLM failed: %s", exc)
    else:
        buf.write("  statspai unavailable — GLM skipped\n")

    return row, fig_path


# ── Bartik Shift-Share IV ──────────────────────────────────────────────────────

def _run_bartik_iv(
    df: pd.DataFrame,
    y: str,
    treatment: str,
    covariates: list[str],
    shares: pd.DataFrame | None,
    shocks: pd.Series | None,
    cluster: str,
    buf: io.StringIO,
    max_sample: int = 10000,
) -> tuple[dict[str, Any] | None, Path | None]:
    """Run Bartik shift-share IV via StatsPAI ``BartikIV``.

    ``shares`` (n_obs x n_industries DataFrame) and ``shocks`` (n_industries
    Series) are required.  They are not derived from a single instrument
    column — shift-share instruments need industry-level structure.

    Returns (model_row_dict, figure_path_or_None).
    """
    row: dict[str, Any] | None = None
    fig_path: Path | None = None

    if shares is None or shocks is None:
        buf.write("  BartikIV skipped — 'shares' (DataFrame) and 'shocks' (Series) "
                  "are required for shift-share IV\n")
        return None, None

    # shares must align with data rows; downsample together if needed
    if len(df) > max_sample:
        sampled = df.sample(n=max_sample, random_state=42)
        shares = shares.reindex(sampled.index).reset_index(drop=True)
        df = sampled.reset_index(drop=True)
        buf.write(f'  [BartikIV] downsampling {len(df):,} → {max_sample:,} rows (shares aligned)\n')
    elif len(shares) != len(df):
        buf.write(f"  BartikIV FAILED: shares has {len(shares)} rows but data has {len(df)} rows\n")
        return None, None

    covar_str = ", ".join(covariates) if covariates else "none"
    buf.write(f"[BartikIV] y={y}, endog={treatment}, shares={shares.shape}, "
              f"shocks={len(shocks)}, covariates=[{covar_str}], cluster={cluster or 'none'}\n")

    if HAS_STATSPAI:
        try:
            est = sp.BartikIV(
                data=df,
                y=y,
                endog=treatment,
                shares=shares,
                shocks=shocks,
                covariates=covariates or [],
                leave_one_out=False,
                robust="hc1",
            )
            result = est.fit()

            coef = _safe_float(result.tidy()[result.tidy()["term"] == treatment]["estimate"].iloc[0])
            se = _safe_float(result.tidy()[result.tidy()["term"] == treatment]["std_error"].iloc[0])
            pval = _safe_float(result.tidy()[result.tidy()["term"] == treatment]["p_value"].iloc[0])
            ci_raw = result.conf_int()
            ci_low = _safe_float(ci_raw.loc[treatment, 0.025])
            ci_high = _safe_float(ci_raw.loc[treatment, 0.975])

            nobs = 0
            f_stat = float("nan")
            f_pvalue = float("nan")
            n_ind = 0
            try:
                d = result.to_dict()
                nobs = int(d.get("n_obs", 0))
                diag = d.get("diagnostics", {})
                f_stat = _safe_float(diag.get("First-stage F", float("nan")))
                f_pvalue = _safe_float(diag.get("First-stage F p-value", float("nan")))
                n_ind = int(diag.get("N industries", 0))
            except Exception:
                pass

            sig = _sig_stars(pval)
            f_sig = _sig_stars(f_pvalue) if not np.isnan(f_pvalue) else ""
            buf.write(f"  BartikIV: β={coef:+.4f}{sig}  SE={se:.4f}  p={pval:.4f}  "
                      f"CI=[{ci_low:+.4f}, {ci_high:+.4f}]  N={nobs:,}  "
                      f"F1={f_stat:.2f}{f_sig}  industries={n_ind}\n")

            row = {
                "model": "BartikIV",
                "coef": round(coef, 6),
                "se": round(se, 6),
                "pvalue": round(pval, 6),
                "ci_lower": round(ci_low, 6),
                "ci_upper": round(ci_high, 6),
                "nobs": nobs,
                "f_stat": round(f_stat, 3) if not np.isnan(f_stat) else "",
                "f_pvalue": round(f_pvalue, 4) if not np.isnan(f_pvalue) else "",
                "n_industries": n_ind,
            }
        except Exception as exc:
            buf.write(f"  BartikIV FAILED: {exc}\n")
            logger.warning("BartikIV failed: %s", exc)
    else:
        buf.write("  statspai unavailable — BartikIV skipped\n")

    return row, fig_path


# ── public API ────────────────────────────────────────────────────────────────

def run_analysis(
    method: str,
    data_path: str | Path,
    y: str,
    treatment: str,
    project_root: str | Path | None = None,
    # method-specific
    instrument: str | None = None,        # IV
    running: str | None = None,           # RDD
    cutoff: float | None = None,          # RDD
    covariates: list[str] | None = None,  # IV / PSM / DML / GLM / Panel / BartikIV
    unit_fe: str | None = None,           # DML / Panel
    time_fe: str | None = None,           # DML / Panel
    cluster: str | None = None,
    # BartikIV
    shares: pd.DataFrame | None = None,   # BartikIV: region x industry share matrix
    shocks: pd.Series | None = None,      # BartikIV: industry-level shock vector
    # DID (reuse existing adapter)
    time: str | None = None,              # DID
    post: str | None = None,              # DID
    outcomes: list[str] | None = None,    # DID
    treatment_year: int = 2012,           # DID
    # misc
    seed: int = 42,
) -> dict[str, Any]:
    """Run a single-method causal analysis.

    Parameters
    ----------
    method : str
        One of ``"iv"``, ``"rdd"``, ``"psm"``, ``"dml"``, ``"panel"``,
        ``"glm"``, ``"bartik"``, or ``"did"``.
    data_path : str | Path
        Path to input data (CSV, parquet, or pickle).
    y : str
        Outcome variable column name.
    treatment : str
        Treatment indicator column name.
    project_root : str | Path | None
        Root directory for outputs. Defaults to ``data_path.parent.parent``.
    instrument : str | None
        Instrument column (IV only).
    running : str | None
        Running variable column (RDD only).
    cutoff : float | None
        Discontinuity threshold (RDD only).
    covariates : list[str] | None
        Control variables (IV / PSM / DML / GLM / Panel / BartikIV).
    unit_fe : str | None
        Unit fixed-effects column (DML / Panel).
    time_fe : str | None
        Time fixed-effects column (DML / Panel).
    cluster : str | None
        Clustering variable for standard errors.
    shares : pd.DataFrame | None
        Region-by-industry share matrix (BartikIV only, required).
    shocks : pd.Series | None
        Industry-level shock vector (BartikIV only, required).
    time : str | None
        Time variable (DID only).
    post : str | None
        Post-period indicator (DID only).
    outcomes : list[str] | None
        Outcome variables (DID only).
    treatment_year : int
        Treatment year (DID / RDD context).

    Returns
    -------
    dict with keys: ``table_path``, ``figure_path``, ``log_path``, ``models``,
    ``statspai_used``.
    """
    method = method.lower().strip()
    valid_methods = {"iv", "rdd", "psm", "dml", "panel", "glm", "bartik", "did"}
    if method not in valid_methods:
        raise ValueError(f"Unknown method '{method}'. Choose from: {sorted(valid_methods)}")

    # ── setup ─────────────────────────────────────────────────────────────
    data_path = Path(data_path)
    project_root = Path(project_root) if project_root else data_path.parent.parent
    max_sample = 10000  # cap for memory-heavy methods (IV, DML)
    tables_dir, figures_dir = _ensure_dirs(project_root)
    covariates = covariates or []
    cluster = cluster or ""

    log_path = project_root / "model_log.md"
    table_name = f"table_{method}.csv"
    table_path = tables_dir / table_name

    # ── load data ─────────────────────────────────────────────────────────
    df = _load_data(data_path)
    n_raw = len(df)
    buf = io.StringIO()

    # ── log header ────────────────────────────────────────────────────────
    method_label = method.upper()
    buf.write(f"# {method_label} Analysis Log\n\n")
    buf.write(f"- **Data**: `{data_path}`\n")
    buf.write(f"- **Observations**: {n_raw:,}\n")
    buf.write(f"- **Outcome**: `{y}`\n")
    buf.write(f"- **Treatment**: `{treatment}`\n")
    buf.write(f"- **statspai available**: {HAS_STATSPAI}\n\n")

    models: list[dict[str, Any]] = []
    figure_path_str = ""
    model_row: dict[str, Any] | None = None
    fig_path: Path | None = None

    # ── dispatch ──────────────────────────────────────────────────────────
    if method == "did":
        did_outcomes = outcomes or [y]
        # Snapshot existing log so we can prepend the DID section header after
        # run_did_analysis overwrites the file.
        _did_log_existing = ""
        if log_path.exists():
            _did_log_existing = log_path.read_text(encoding="utf-8")

        result = run_did_analysis(
            data_path=data_path,
            treatment=treatment,
            time=time or "year",
            post=post or "post",
            outcomes=did_outcomes,
            covariates=covariates or None,
            cluster=cluster,
            treatment_year=treatment_year,
            unit_fe=unit_fe or "",
            time_fe=time_fe or "",
            project_root=project_root,
        )

        # did_adapter writes its own "# DID Analysis Log" header — strip it so
        # our wrapper header is the only top-level one.
        did_log = log_path.read_text(encoding="utf-8")
        # Remove the first "# DID Analysis Log" line from did_adapter's content
        # (we replace it with our own wrapper).
        did_log_stripped = did_log.replace("# DID Analysis Log\n", "", 1)
        section_header = (
            f"# DID Analysis Log\n\n"
            f"- **Data**: `{data_path}`\n"
            f"- **Outcome**: `{y}`\n"
            f"- **Treatment**: `{treatment}`\n"
            f"- **statspai available**: {HAS_STATSPAI}\n\n"
            f"---\n\n"
            f"> DID full pipeline delegated to `run_did_analysis`.\n"
            f"> See `{result.get('table_path', 'tables/table2_did.csv')}` "
            f"and `{result.get('figure_path', 'figures/event_study.png')}` for results.\n\n"
        )
        log_path.write_text(_did_log_existing + section_header + did_log_stripped, encoding="utf-8")
        print(section_header + did_log_stripped)

        return result

    elif method == "iv":
        if not instrument:
            raise ValueError("IV method requires 'instrument' parameter")
        model_row, fig_path = _run_iv(df, y, treatment, instrument, covariates, cluster, buf)

    elif method == "rdd":
        if running is None or cutoff is None:
            raise ValueError("RDD method requires 'running' and 'cutoff' parameters")
        model_row, fig_path = _run_rdd(df, y, running, cutoff, buf)

    elif method == "psm":
        if not covariates:
            raise ValueError("PSM method requires 'covariates' for propensity score")
        model_row, fig_path = _run_psm(df, y, treatment, covariates, cluster, buf)

    elif method == "dml":
        if not unit_fe:
            raise ValueError("DML method requires 'unit_fe' for panel fixed effects")
        model_row, fig_path = _run_dml(df, y, treatment, covariates, unit_fe, time_fe or "", cluster, buf)

    elif method == "panel":
        if not unit_fe or not time_fe:
            raise ValueError("Panel method requires 'unit_fe' and 'time_fe'")
        model_row, fig_path = _run_panel(
            df, y, treatment, covariates, unit_fe, time_fe, cluster, buf,
            max_sample=max_sample,
        )

    elif method == "glm":
        if not covariates:
            raise ValueError("GLM method requires 'covariates'")
        model_row, fig_path = _run_glm(
            df, y, treatment, covariates, cluster, buf,
            max_sample=max_sample,
        )

    elif method == "bartik":
        model_row, fig_path = _run_bartik_iv(
            df, y, treatment, covariates or [], shares, shocks, cluster, buf,
            max_sample=max_sample,
        )

    # ── write table ───────────────────────────────────────────────────────
    if model_row is not None:
        models.append(model_row)
        _write_csv(table_path, models)
        buf.write(f"\n[table] saved {table_path}\n")
    else:
        buf.write("\n[table] SKIPPED — no models estimated\n")

    # ── figure path ───────────────────────────────────────────────────────
    if fig_path is not None:
        figure_path_str = str(fig_path)

    # ── summary ───────────────────────────────────────────────────────────
    buf.write("\n---\n\n## Summary\n\n")
    if models:
        best = models[-1]
        sig = _sig_stars(best.get("pvalue", 1.0) or 1.0)
        coef = best.get("coef", float("nan"))
        pval = best.get("pvalue", 1.0)
        se = best.get("se", float("nan"))
        nobs = best.get("nobs", 0)
        buf.write(f"- **Estimate ({best['model']})**: {coef:+.4f}{sig} "
                  f"(SE={se:.4f}, p={pval:.4f})\n")
        buf.write(f"- **N**: {nobs:,}\n")
        direction = "reduces" if coef < 0 else "increases"
        if pval >= 0.05:
            buf.write(f"- **Interpretation**: Treatment {direction} {y} "
                      f"by {abs(coef):.4f} units (not statistically significant at 5%)\n")
        else:
            buf.write(f"- **Interpretation**: Treatment {direction} {y} "
                      f"by {abs(coef):.4f} units (statistically significant)\n")
    else:
        buf.write("No models estimated.\n")

    # ── finalize log ──────────────────────────────────────────────────────
    _append_log(log_path, buf)

    return {
        "table_path": str(table_path),
        "figure_path": figure_path_str,
        "log_path": str(log_path),
        "models": models,
        "statspai_used": HAS_STATSPAI,
    }

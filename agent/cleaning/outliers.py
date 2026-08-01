"""Sub-step 4: outlier detection + winsorize.

Detects outliers via the IQR rule (for the report) and clips numeric columns
via percentile winsorization (StatsPAI ``winsor`` with a pandas fallback).
Before/after distribution stats are recorded per dataset in the step report.

The report carries ``stats_pai_used`` (bool) so callers can tell whether the
winsorization was delegated to StatsPAI or handled by the pandas fallback.
"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)

_DEFAULT_CUTS = (5, 95)


class OutliersStep:
    name = "outliers"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        workspace = config.get("workspace", "/tmp")
        order = config.get("order", 0)
        cuts = config.get("cuts", _DEFAULT_CUTS)

        before_list: list = []
        after_list: list = []
        iqr_outliers_list: list = []
        winsorized_list: list = []
        stats_pai_used = False

        sp_winsor = None
        try:
            from statspai import winsor as sp_winsor  # type: ignore
        except ImportError:
            sp_winsor = None

        for i, ds in enumerate(datasets):
            path = ds.get("path")
            if not path:
                before_list.append({})
                after_list.append({})
                iqr_outliers_list.append({})
                winsorized_list.append(False)
                continue

            df = pd.read_csv(path)
            numeric_cols = list(df.select_dtypes(include="number").columns)
            if not numeric_cols:
                before_list.append({})
                after_list.append({})
                iqr_outliers_list.append({})
                winsorized_list.append(False)
                continue

            before = _distribution(df, numeric_cols)
            iqr_outliers = _iqr_outlier_counts(df, numeric_cols)

            if sp_winsor is not None:
                try:
                    df = sp_winsor(df, vars=numeric_cols, cuts=cuts, replace=True)
                    stats_pai_used = True
                except Exception:
                    logger.warning(
                        "StatsPAI winsor() failed for dataset %d, falling back to pandas", i
                    )
                    df = _winsorize_pandas(df, numeric_cols, cuts)
            else:
                logger.warning(
                    "StatsPAI not available for winsorize (dataset %d), using pandas fallback", i
                )
                df = _winsorize_pandas(df, numeric_cols, cuts)

            after = _distribution(df, numeric_cols)

            if "original_path" not in ds:
                ds["original_path"] = path
            sidecar_path = f"{workspace}/{order:02d}_outliers_{i}.csv"
            df.to_csv(sidecar_path, index=False)
            ds["path"] = sidecar_path
            ds.setdefault("step_paths", []).append(sidecar_path)

            ds["outliers"] = {
                "before": before,
                "after": after,
                "iqr_outliers": iqr_outliers,
                "winsorized": True,
            }
            before_list.append(before)
            after_list.append(after)
            iqr_outliers_list.append(iqr_outliers)
            winsorized_list.append(True)

        return datasets, {
            "before": before_list,
            "after": after_list,
            "iqr_outliers": iqr_outliers_list,
            "winsorized": winsorized_list,
            "stats_pai_used": stats_pai_used,
        }


def _distribution(df: pd.DataFrame, cols: list) -> dict:
    out = {}
    for c in cols:
        s = df[c]
        if s.dropna().empty:
            out[c] = {"min": None, "max": None, "mean": None}
            continue
        out[c] = {
            "min": float(s.min()),
            "max": float(s.max()),
            "mean": float(s.mean()),
        }
    return out


def _iqr_outlier_counts(df: pd.DataFrame, cols: list) -> dict:
    out = {}
    for c in cols:
        s = df[c].dropna()
        if s.empty:
            out[c] = 0
            continue
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        out[c] = int(((s < lower) | (s > upper)).sum())
    return out


def _winsorize_pandas(df: pd.DataFrame, cols: list, cuts) -> pd.DataFrame:
    lo, hi = cuts[0] / 100.0, cuts[1] / 100.0
    for c in cols:
        s = df[c]
        non_nan = s.dropna()
        if non_nan.empty:
            continue
        lower = non_nan.quantile(lo)
        upper = non_nan.quantile(hi)
        df[c] = s.clip(lower=lower, upper=upper)
    return df

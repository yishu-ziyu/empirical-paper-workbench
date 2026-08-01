"""Sub-step 3: missing-value handling.

Three strategies, selected by the caller via ``config["strategy"]``:

- ``drop``   -- drop any row with a missing cell
- ``impute`` -- numeric cols filled with median, categorical with mode
- ``mice``   -- multiple imputation via StatsPAI (fallback sklearn IterativeImputer)

When ``strategy`` is ``None`` the step is *detect-only*: it records
``missing_count`` but does not modify the data, preserving the T-02 contract.

The report carries ``stats_pai_used`` (bool) — only relevant when
``strategy == "mice"``, indicating whether the imputation used StatsPAI
or fell back to sklearn / pandas.
"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class MissingStep:
    name = "missing"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        workspace = config.get("workspace", "/tmp")
        order = config.get("order", 0)
        strategy = config.get("strategy")

        missing_counts: list[int] = []
        rows_counts: list[int] = []
        stats_pai_used = False

        for i, ds in enumerate(datasets):
            path = ds.get("path")
            if not path:
                if "missing_count" not in ds:
                    ds["missing_count"] = 0
                missing_counts.append(int(ds.get("missing_count", 0)))
                rows_counts.append(int(ds.get("rows", 0)))
                continue

            df = pd.read_csv(path)

            if strategy == "drop":
                df = df.dropna().reset_index(drop=True)
            elif strategy == "impute":
                df = _impute_median_mode(df)
            elif strategy == "mice":
                df, pai = _mice_impute(df)
                if pai:
                    stats_pai_used = True

            ds["missing_count"] = int(df.isna().sum().sum())
            ds["rows"] = int(len(df))
            missing_counts.append(ds["missing_count"])
            rows_counts.append(ds["rows"])

            if strategy in ("drop", "impute", "mice"):
                if "original_path" not in ds:
                    ds["original_path"] = path
                sidecar_path = f"{workspace}/{order:02d}_missing_{i}.csv"
                df.to_csv(sidecar_path, index=False)
                ds["path"] = sidecar_path
                ds.setdefault("step_paths", []).append(sidecar_path)

        return datasets, {
            "strategy": strategy,
            "missing_count": missing_counts,
            "rows": rows_counts,
            "stats_pai_used": stats_pai_used,
        }


def _impute_median_mode(df: pd.DataFrame) -> pd.DataFrame:
    """Fill numeric columns with median, categorical with mode."""
    for col in df.columns:
        if not df[col].isna().any():
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            m = df[col].mode()
            df[col] = df[col].fillna(m[0] if not m.empty else "")
    return df


def _mice_impute(df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Multiple imputation via StatsPAI, falling back to sklearn then median/mode.

    Returns ``(DataFrame, stats_pai_used)``.
    """
    try:
        from statspai import mice as sp_mice

        result = sp_mice(df, m=1, max_iter=5, seed=42, print_progress=False)
        return result.complete(0), True
    except Exception:
        logger.warning("StatsPAI mice() failed, falling back to sklearn IterativeImputer")
    try:
        from sklearn.experimental import enable_iterative_imputer  # noqa: F401
        from sklearn.impute import IterativeImputer

        numeric = df.select_dtypes(include="number")
        if numeric.isna().any().any() and numeric.shape[1] >= 2:
            imp = IterativeImputer(random_state=42, max_iter=5)
            df[numeric.columns] = imp.fit_transform(numeric)
        return _impute_median_mode(df), False
    except Exception:
        logger.warning("sklearn IterativeImputer also failed, falling back to pandas median/mode")
        return _impute_median_mode(df), False

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

        # StatsPAI mice 只接受数值列，对含缺失的分类列会因 astype(float) 抛错。
        # 先把分类列编码为整数码喂给 mice，跑完再解码回原始标签，保证正常路径
        # 能用上 StatsPAI（stats_pai_used=True）。
        df_enc, encoders = _encode_categorical(df)
        result = sp_mice(df_enc, m=1, max_iter=5, seed=42, print_progress=False)
        completed = result.complete(0)
        return _decode_categorical(completed, encoders), True
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


def _encode_categorical(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """把非数值列编码为整数码，供 StatsPAI mice 使用。

    Returns ``(df_encoded, encoders)``，其中 ``encoders`` 为 ``列名 -> 标签列表``。
    缺失值先以占位串填充再编码，确保它能被 mice 当作可观测值处理。
    """
    encoders: dict[str, list] = {}
    df_enc = df.copy()
    for col in df_enc.columns:
        if pd.api.types.is_numeric_dtype(df_enc[col]):
            continue
        codes, uniques = pd.factorize(df_enc[col].fillna("__NA__"))
        encoders[col] = uniques.tolist()
        df_enc[col] = codes
    return df_enc, encoders


def _decode_categorical(df_enc: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    """把 mice 输出的整数码列映射回原始分类标签。"""
    df = df_enc.copy()
    for col, labels in encoders.items():

        def _to_label(v):
            i = int(v)
            if 0 <= i < len(labels):
                return labels[i]
            return labels[-1] if labels else None

        df[col] = df_enc[col].map(_to_label)
    return df

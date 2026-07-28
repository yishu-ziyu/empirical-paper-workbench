"""Sub-step 5: variable recoding & construction.

Applies, in order:
- categorical encode (one-hot / label)
- continuous binning (equal-frequency / equal-width)
- log transform (log1p on positive numeric columns)
- interaction terms (product of two columns)
- policy dummy (DiD treat x post)

New column names are recorded in ``ds["constructed_vars"]`` so downstream
nodes and the HITL UI can report what was constructed. Each dataset's
constructed frame is written to a sidecar ``<order>_transform_<i>.csv``
rather than overwriting the input path.
"""
import numpy as np
import pandas as pd


class TransformStep:
    name = "transform"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        workspace = config.get("workspace", "/tmp")
        order = config.get("order", 0)
        all_constructed: list[str] = []

        for i, ds in enumerate(datasets):
            path = ds.get("path")
            if not path:
                continue

            df = pd.read_csv(path)
            constructed: list[str] = []

            constructed += _apply_encodings(df, config.get("encodings", {}))
            constructed += _apply_bins(df, config.get("bins", {}))
            constructed += _apply_log_transform(df, config.get("log_transform", []))
            constructed += _apply_interactions(df, config.get("interactions", []))
            constructed += _apply_policy_dummies(df, config.get("policy_dummies", {}))

            if "original_path" not in ds:
                ds["original_path"] = path
            sidecar_path = f"{workspace}/{order:02d}_transform_{i}.csv"
            df.to_csv(sidecar_path, index=False)
            ds["path"] = sidecar_path
            ds.setdefault("step_paths", []).append(sidecar_path)

            existing = ds.get("constructed_vars", [])
            ds["constructed_vars"] = list(existing) + constructed
            all_constructed.extend(constructed)

        return datasets, {"constructed_vars": all_constructed}


def _apply_encodings(df: pd.DataFrame, encodings: dict) -> list[str]:
    created: list[str] = []
    for col, method in encodings.items():
        if col not in df.columns:
            continue
        if method == "onehot":
            dummies = pd.get_dummies(df[col], prefix=col).astype(int)
            df[dummies.columns] = dummies
            created.extend(dummies.columns)
        elif method == "label":
            codes = df[col].astype("category").cat.codes
            new_col = f"{col}_label"
            df[new_col] = codes.astype(int)
            created.append(new_col)
    return created


def _apply_bins(df: pd.DataFrame, bins: dict) -> list[str]:
    created: list[str] = []
    for col, spec in bins.items():
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue
        n = int(spec.get("n", 5))
        method = spec.get("method", "equal_width")
        new_col = f"{col}_bin"
        s = df[col].dropna()
        if s.empty:
            continue
        if method == "equal_freq":
            df[new_col] = pd.qcut(df[col], q=n, duplicates="drop").cat.codes
        else:
            df[new_col] = pd.cut(df[col], bins=n, include_lowest=True).cat.codes
        created.append(new_col)
    return created


def _apply_log_transform(df: pd.DataFrame, cols: list) -> list[str]:
    created: list[str] = []
    for col in cols:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue
        new_col = f"{col}_log"
        df[new_col] = np.log1p(df[col].clip(lower=0))
        created.append(new_col)
    return created


def _apply_interactions(df: pd.DataFrame, interactions: list) -> list[str]:
    created: list[str] = []
    for pair in interactions:
        if len(pair) != 2:
            continue
        c1, c2 = pair
        if c1 not in df.columns or c2 not in df.columns:
            continue
        new_col = f"{c1}_x_{c2}"
        df[new_col] = df[c1] * df[c2]
        created.append(new_col)
    return created


def _apply_policy_dummies(df: pd.DataFrame, policy_dummies: dict) -> list[str]:
    created: list[str] = []
    for name, spec in policy_dummies.items():
        treat_col = spec.get("treat")
        post_col = spec.get("post")
        if not treat_col or not post_col:
            continue
        if treat_col not in df.columns or post_col not in df.columns:
            continue
        df[name] = (df[treat_col] * df[post_col]).astype(int)
        created.append(name)
    return created

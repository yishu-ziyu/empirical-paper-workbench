"""Sub-step 1: data profiling.

Reads each dataset's CSV and reports per-variable type inference, missing rate,
unique-value count, and numeric flag. The profile reflects the data *as
uploaded* (before any cleaning sub-step modifies it).

T-11 extension: each profile is augmented with a ``dataset_type`` field
("CHARLS" / "generic") and, when CHARLS is detected, a ``charls_config``
field carrying the parsed ``charls.yaml`` mapping / waves / filter presets.
"""
import re

import pandas as pd


class ProfilingStep:
    name = "profiling"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        profiles = [_profile_one(ds) for ds in datasets]
        return datasets, {"profiles": profiles, "merged_profile": None}


def _profile_one(dataset_meta: dict) -> dict:
    path = dataset_meta.get("path")
    if not path:
        return {}

    df = pd.read_csv(path)
    variables = {}
    for col in df.columns:
        s = df[col]
        variables[col] = {
            "dtype": str(s.dtype),
            "missing_rate": float(s.isna().mean()),
            "n_unique": int(s.nunique()),
            "is_numeric": bool(pd.api.types.is_numeric_dtype(s)),
        }
    profile = {
        "n_rows": int(len(df)),
        "n_cols": int(len(df.columns)),
        "variables": variables,
    }

    dataset_type = _detect_dataset_type(df)
    profile["dataset_type"] = dataset_type
    if dataset_type == "CHARLS":
        profile["charls_config"] = _load_charls_config()
    return profile


def _detect_dataset_type(df: "pandas.DataFrame") -> str:
    cols = set(df.columns)

    if "community_id" in cols:
        qe_hi_count = sum(
            1 for c in cols if _is_qe_hi_column(c)
        )
        if qe_hi_count >= 5:
            return "CHARLS"
    return "generic"


def _is_qe_hi_column(col: str) -> bool:
    return bool(re.match(r"^qe\d+_hi$", col))


def _load_charls_config() -> dict:
    try:
        from dataset_profiles import load_profile  # noqa: PLC0415
    except ImportError:
        return {}
    cfg = load_profile("charls")
    return cfg if isinstance(cfg, dict) else {}

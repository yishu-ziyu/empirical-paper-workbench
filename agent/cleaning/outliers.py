"""Sub-step 4: outlier detection + winsorize.

Detects outliers via the IQR rule and clips only continuous columns that
actually contain IQR outliers. Research-design columns and binary indicators
are report-only. Before/after distribution stats are recorded per dataset.

Winsorization goes through ``clean_winsor`` (pywinsor2, explicit cuts=(1, 99),
replace=True). That is not Stata ``winsor2``'s default call. ``stats_pai_used``
is always False here: this step no longer delegates to StatsPAI.
"""
import pandas as pd

from .winsor import WINSOR_CUTS, clean_winsor, winsor_audit_row

_DEFAULT_CUTS = WINSOR_CUTS


class OutliersStep:
    name = "outliers"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        workspace = config.get("workspace", "/tmp")
        order = config.get("order", 0)
        cuts = config.get("cuts", _DEFAULT_CUTS)
        protected_columns = set(config.get("protected_columns") or [])

        before_list: list = []
        after_list: list = []
        iqr_outliers_list: list = []
        winsorized_list: list = []
        engine_list: list = []
        columns_list: list = []
        n_changed_list: list = []
        skipped_list: list = []

        for i, ds in enumerate(datasets):
            path = ds.get("path")
            if not path:
                before_list.append({})
                after_list.append({})
                iqr_outliers_list.append({})
                winsorized_list.append(False)
                engine_list.append(None)
                columns_list.append([])
                n_changed_list.append({})
                skipped_list.append({})
                continue

            df = pd.read_csv(path)
            numeric_cols = list(df.select_dtypes(include="number").columns)
            if not numeric_cols:
                before_list.append({})
                after_list.append({})
                iqr_outliers_list.append({})
                winsorized_list.append(False)
                engine_list.append(None)
                columns_list.append([])
                n_changed_list.append({})
                skipped_list.append({})
                continue

            before = _distribution(df, numeric_cols)
            iqr_outliers = _iqr_outlier_counts(df, numeric_cols)
            winsor_cols = [
                column
                for column in numeric_cols
                if column not in protected_columns
                and int(iqr_outliers.get(column, 0)) > 0
                and int(df[column].nunique(dropna=True)) > 2
            ]

            df, audit = clean_winsor(
                df,
                winsor_cols,
                cuts=cuts,
                protected_columns=protected_columns,
            )
            after = _distribution(df, numeric_cols)
            row = winsor_audit_row(
                audit, before=before, after=after, iqr_outliers=iqr_outliers
            )

            if "original_path" not in ds:
                ds["original_path"] = path
            sidecar_path = f"{workspace}/{order:02d}_outliers_{i}.csv"
            df.to_csv(sidecar_path, index=False)
            ds["path"] = sidecar_path
            ds.setdefault("step_paths", []).append(sidecar_path)
            ds["outliers"] = row

            before_list.append(before)
            after_list.append(after)
            iqr_outliers_list.append(iqr_outliers)
            winsorized_list.append(bool(row["columns"]))
            engine_list.append(row["engine"])
            columns_list.append(list(row["columns"]))
            n_changed_list.append(dict(row["n_changed"]))
            skipped_list.append(dict(row["skipped"]))

        return datasets, {
            "before": before_list,
            "after": after_list,
            "iqr_outliers": iqr_outliers_list,
            "winsorized": winsorized_list,
            "stats_pai_used": False,
            "engine": engine_list,
            "cuts": [int(cuts[0]), int(cuts[1])] if cuts is not None else list(WINSOR_CUTS),
            "columns": columns_list,
            "n_changed": n_changed_list,
            "skipped": skipped_list,
            "stata_default": False,
            "replace": True,
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

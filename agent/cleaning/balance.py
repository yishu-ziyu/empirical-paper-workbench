"""Sub-step 7: panel balance check.

Detects attrition and unbalanced panels. The step report carries:
- ``balanced``: entities present in ALL time periods
- ``n_periods``: number of distinct time periods observed
- ``attrition_rate``: fraction of entities present in the first period but
  absent from the last period
- ``stats_pai_used``: always ``false`` — this step computes metrics from scratch
  via pandas rather than delegating to StatsPAI (the previous attempt to call
  ``sp.balance_panel()`` was a no-op that discarded the result, so it was
  removed to avoid CPU waste and user confusion).
"""
import pandas as pd


class BalanceStep:
    name = "balance"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        panel_id = config.get("panel_id")
        time_col = config.get("time_col")

        path = _first_path(datasets)
        if not path or not panel_id or not time_col:
            return datasets, {"balanced": 0, "n_periods": 0, "attrition_rate": 0.0, "stats_pai_used": False}

        df = pd.read_csv(path)
        if panel_id not in df.columns or time_col not in df.columns:
            return datasets, {"balanced": 0, "n_periods": 0, "attrition_rate": 0.0, "stats_pai_used": False}

        base = _report_from_pandas(df, panel_id, time_col)
        n_periods = int(df[time_col].nunique())
        return datasets, {
            "balanced": base["balanced_n"],
            "n_periods": n_periods,
            "attrition_rate": base["attrition_rate"],
            "stats_pai_used": False,
        }


def _first_path(datasets: list) -> str | None:
    for ds in datasets:
        p = ds.get("path")
        if p:
            return p
    return None


def _report_from_pandas(
    df: pd.DataFrame, panel_id: str, time_col: str
) -> dict:
    periods = sorted(df[time_col].unique())
    n_periods = len(periods)
    if n_periods == 0:
        return {"balanced_n": 0, "unbalanced_n": 0, "attrition_rate": 0.0}

    counts = df.groupby(panel_id)[time_col].nunique()
    balanced_n = int((counts == n_periods).sum())
    unbalanced_n = int((counts < n_periods).sum())

    first_period_entities = set(
        df[df[time_col] == periods[0]][panel_id].unique()
    )
    last_period_entities = set(
        df[df[time_col] == periods[-1]][panel_id].unique()
    )
    dropped = first_period_entities - last_period_entities
    attrition_rate = (
        len(dropped) / len(first_period_entities)
        if first_period_entities
        else 0.0
    )

    return {
        "balanced_n": balanced_n,
        "unbalanced_n": unbalanced_n,
        "attrition_rate": float(attrition_rate),
    }

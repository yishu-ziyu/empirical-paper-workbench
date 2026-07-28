"""Sub-step 6: sample filtering.

Filters rows by a list of conditions (ANDed together) and records the
before/after sample counts on the dataset meta so the HITL UI can show
the impact of each filter.

Condition shape: ``{"col": str, "op": str, "val": Any}`` where op is one of
``>=``, ``<=``, ``>``, ``<``, ``==``, ``!=``. The filtered frame is written
to a sidecar ``<order>_filter_<i>.csv`` rather than overwriting the input.
"""
import operator

import pandas as pd

_OPS = {
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
    "==": operator.eq,
    "!=": operator.ne,
}


class FilterStep:
    name = "filter"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        workspace = config.get("workspace", "/tmp")
        order = config.get("order", 0)
        conditions = config.get("conditions", [])

        n_before_list: list[int] = []
        n_after_list: list[int] = []

        for i, ds in enumerate(datasets):
            path = ds.get("path")
            if not path:
                continue

            df = pd.read_csv(path)
            n_before = int(len(df))

            mask = pd.Series([True] * n_before, index=df.index)
            for cond in conditions:
                col = cond.get("col")
                op = cond.get("op")
                val = cond.get("val")
                if col not in df.columns or op not in _OPS:
                    continue
                mask = mask & _OPS[op](df[col], val)

            df = df[mask].reset_index(drop=True)
            n_after = int(len(df))

            if "original_path" not in ds:
                ds["original_path"] = path
            sidecar_path = f"{workspace}/{order:02d}_filter_{i}.csv"
            df.to_csv(sidecar_path, index=False)
            ds["path"] = sidecar_path
            ds.setdefault("step_paths", []).append(sidecar_path)

            ds["filter"] = {
                "n_before": n_before,
                "n_after": n_after,
                "conditions": list(conditions),
            }
            ds["rows"] = n_after
            n_before_list.append(n_before)
            n_after_list.append(n_after)

        return datasets, {
            "n_before": n_before_list,
            "n_after": n_after_list,
            "conditions": list(conditions),
        }

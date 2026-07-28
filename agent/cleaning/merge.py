"""Sub-step 2: multi-period / multi-source dataset merge.

Appends multiple same-schema CSVs (e.g. CHARLS waves) row-wise into a single
dataset. The merged frame is written to a sidecar ``<order>_merge_0.csv`` and
the returned list collapses to a single dataset meta.
"""
import pandas as pd


class MergeStep:
    name = "merge"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        workspace = config.get("workspace", "/tmp")
        order = config.get("order", 0)

        if len(datasets) <= 1:
            return datasets, {"merged_path": None, "n_before": 0, "n_after": 0}

        pathed = [ds for ds in datasets if ds.get("path")]
        if len(pathed) < 2:
            return datasets, {"merged_path": None, "n_before": 0, "n_after": 0}

        dfs = [pd.read_csv(ds["path"]) for ds in pathed]
        n_before = int(sum(len(df) for df in dfs))
        combined = pd.concat(dfs, ignore_index=True)
        n_after = int(len(combined))

        base = dict(datasets[0])
        if "original_path" not in base:
            base["original_path"] = base.get("path", "")
        sidecar_path = f"{workspace}/{order:02d}_merge_0.csv"
        combined.to_csv(sidecar_path, index=False)
        base["path"] = sidecar_path
        base["rows"] = n_after
        base["merged_from"] = len(pathed)
        base.setdefault("step_paths", []).append(sidecar_path)

        return [base], {
            "merged_path": sidecar_path,
            "n_before": n_before,
            "n_after": n_after,
        }

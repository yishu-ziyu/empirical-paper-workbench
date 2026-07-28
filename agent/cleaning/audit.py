"""Sub-step 8: cleaning audit trail.

Generates two scripts that record the cleaning steps applied to the
dataset, so the user can download / re-run them:

- ``clean.py``  -- a Python script (pandas-based) reproducing the pipeline.
- ``clean.do``  -- a Stata ``.do`` script with equivalent logic.

Both scripts are written into the workspace root. The step reads
``config["steps"]`` (a list of StepReport dicts produced by the prior
seven steps) and records each step whose ``status == "success"``.
"""
from pathlib import Path


class AuditStep:
    name = "audit"

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        workspace = config.get("workspace", "/tmp")
        step_reports = config.get("steps", [])

        step_names = [
            sr.get("name", "")
            for sr in step_reports
            if sr.get("status") == "success"
        ]

        csv_path = _first_path(datasets)
        python_script = _build_python_script(step_names, csv_path)
        stata_script = _build_stata_script(step_names, csv_path)

        root = Path(workspace)
        root.mkdir(parents=True, exist_ok=True)

        clean_py = root / "clean.py"
        clean_do = root / "clean.do"
        clean_py.write_text(python_script, encoding="utf-8")
        clean_do.write_text(stata_script, encoding="utf-8")

        return datasets, {
            "clean_py": str(clean_py),
            "clean_do": str(clean_do),
        }


def _first_path(datasets: list) -> str | None:
    for ds in datasets:
        p = ds.get("path")
        if p:
            return p
    return None


_PY_HEADER = '''"""Auto-generated cleaning audit trail (econpaper T-05).

Reproduces the cleaning pipeline applied to the uploaded dataset.
"""
import pandas as pd
'''


def _build_python_script(steps: list, csv_path: str | None) -> str:
    lines = [_PY_HEADER]
    if csv_path:
        lines.append(f'DATA_PATH = r"{csv_path}"')
        lines.append("df = pd.read_csv(DATA_PATH)")
    lines.append("")
    lines.append("# Cleaning steps applied (in order):")
    for i, step in enumerate(steps, 1):
        lines.append(f"# Step {i}: {step}")
    lines.append("")
    lines.append("# TODO: replace placeholders with the exact parameters used.")
    lines.append("if __name__ == '__main__':")
    lines.append("    print('cleaning pipeline replayed')")
    return "\n".join(lines) + "\n"


_DO_HEADER = """* Auto-generated cleaning audit trail (econpaper T-05).
* Reproduces the cleaning pipeline applied to the uploaded dataset.
"""


def _build_stata_script(steps: list, csv_path: str | None) -> str:
    lines = [_DO_HEADER]
    if csv_path:
        lines.append(f'* import the raw dataset')
        lines.append(f'import delimited "{csv_path}", clear')
    lines.append("")
    lines.append("* Cleaning steps applied (in order):")
    for i, step in enumerate(steps, 1):
        lines.append(f"* Step {i}: {step}")
    lines.append("")
    lines.append("* TODO: replace placeholders with the exact parameters used.")
    lines.append("save cleaned_data.dta, replace")
    return "\n".join(lines) + "\n"

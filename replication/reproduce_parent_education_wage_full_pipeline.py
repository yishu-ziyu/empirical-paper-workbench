#!/usr/bin/env python3
"""Reproduce main OLS for parent_education_wage full pipeline."""
from pathlib import Path
import json
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data/Interim/parent_education_wage_repaired.csv"
cols = ["ln_wage", "parent_education", "age", "female", "urban", "edu_last", "experience"]
d = pd.read_csv(DATA).dropna(subset=cols)
y = d["ln_wage"].astype(float)
X = sm.add_constant(d[["parent_education", "age", "female", "urban", "edu_last", "experience"]].astype(float))
m = sm.OLS(y, X).fit(cov_type="HC1")
out = {
  "nobs": int(m.nobs),
  "parent_education": float(m.params["parent_education"]),
  "parent_education_se": float(m.bse["parent_education"]),
}
print(json.dumps(out, ensure_ascii=False, indent=2))
expected = json.loads((ROOT / "Results/json/parent_education_wage_full_pipeline_main_results.json").read_text())
pe = next(c for c in expected["coefficients"] if c["term"] == "parent_education")
assert abs(out["parent_education"] - pe["coef"]) < 1e-6
assert out["nobs"] == expected["nobs"]
print("REPRO_OK")

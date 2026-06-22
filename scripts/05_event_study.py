#!/usr/bin/env python3
"""05_event_study.py — Event study + DID + heterogeneity via StatsEngine.

Calls runtime.stats_engine.StatsEngine for the full DID pipeline.
Outputs: tables/table2_did.csv, tables/table2_heterogeneity.csv,
         model_log.md, figures/event_study.png
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from runtime.stats_engine import StatsEngine

DATA_PATH = PROJECT_ROOT / "artifacts" / "analysis_ready.pkl"

engine = StatsEngine(project_root=PROJECT_ROOT)

# ── Main DID analysis ────────────────────────────────────────────────────────
result = engine.run_analysis(
    method="did",
    data_path=DATA_PATH,
    outcome="ln_expense",
    treatment="high_minwage_growth",
    time="year",
    post="post",
    outcomes=["ln_expense"],
    covariates=["age", "gender", "familysize", "ln_fincome1"],
    cluster="province_code",
    treatment_year=2012,
    unit_fe="fid",
    time_fe="year",
    heterogeneity_by="income",
    n_hetero_quantiles=4,
)

# ── Robustness checks ────────────────────────────────────────────────────────
rob = engine.robustness(
    data_path=DATA_PATH,
    outcome="ln_expense",
    treatment="high_minwage_growth",
    covariates=["age", "gender", "familysize", "ln_fincome1"],
    cluster="province_code",
    unit_fe="fid",
    time_fe="year",
)
print(f"\n  Robustness checks: {len(rob['checks'])} run")

# ── Generate paper draft ────────────────────────────────────────────────────
draft = engine.generate_draft()

print(f"\n✅ 05_event_study complete")
print(f"   Table:         {result['table_path']}")
print(f"   Heterogeneity: tables/table2_heterogeneity.csv")
print(f"   Figure:        {result['figure_path'] or '(skipped — no pre-period)'}")
print(f"   Log:           {result['log_path']}")
print(f"   Robustness:    {rob['log_path']}")
print(f"   Draft LaTeX:   {draft['tex']}")
print(f"   Draft Markdown: {draft['md']}")
if draft.get("docx"):
    print(f"   Draft DOCX:    {draft['docx']}")

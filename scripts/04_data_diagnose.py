#!/usr/bin/env python3
"""04_data_diagnose.py — Data diagnosis and method recommendation.

Calls engine.diagnose_and_recommend() on the analysis-ready data.
Outputs: artifacts/data_gate_report.md

用法:
    python3 scripts/04_data_diagnose.py
    python3 scripts/04_data_diagnose.py --outcome ln_expense --treatment high_minwage_growth
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from runtime.stats_engine import StatsEngine


def main() -> int:
    parser = argparse.ArgumentParser(description="数据诊断与方法推荐")
    parser.add_argument("--data", default=None, help="Path to data (default: artifacts/analysis_ready.pkl)")
    parser.add_argument("--outcome", default="ln_expense", help="Outcome variable")
    parser.add_argument("--treatment", default="high_minwage_growth", help="Treatment variable")
    parser.add_argument("--covariates", default="age,gender,familysize,ln_fincome1",
                        help="Comma-separated covariates")
    parser.add_argument("--cluster", default="province_code", help="Cluster variable")
    parser.add_argument("--unit-fe", default="fid", help="Unit fixed-effects column")
    parser.add_argument("--time-fe", default="year", help="Time fixed-effects column")
    args = parser.parse_args()

    covariates = [c.strip() for c in args.covariates.split(",") if c.strip()]

    engine = StatsEngine(project_root=PROJECT_ROOT)

    print(f"\n📊 Data Diagnosis")
    print(f"   Data:    {args.data or 'artifacts/analysis_ready.pkl'}")
    print(f"   Outcome: {args.outcome}")
    print(f"   Treatment: {args.treatment}")
    print(f"   Covariates: {', '.join(covariates)}")

    diag = engine.diagnose_and_recommend(
        data_path=args.data,
        outcome=args.outcome,
        treatment=args.treatment,
        covariates=covariates,
        cluster=args.cluster,
        unit_fe=args.unit_fe,
        time_fe=args.time_fe,
    )

    print(f"\n✅ Diagnosis complete")
    print(f"   Recommended method: {diag['recommended_method']}")
    print(f"   Report: {diag['report_path']}")
    print(f"   Warnings: {len(diag['warnings'])}")

    if diag["warnings"]:
        print("\n   ⚠️  Warnings:")
        for w in diag["warnings"]:
            print(f"      - {w}")

    print(f"\n   Variable roles:")
    for role, vlist in diag.get("variable_roles", {}).items():
        if vlist:
            print(f"      {role}: {', '.join(vlist)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

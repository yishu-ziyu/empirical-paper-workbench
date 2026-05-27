from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel

from Program.workbench.cgss_minimal_model import build_analysis_frame, load_cgss_2023_frame, safe_float


SCHEMA_VERSION = "p6.cgss_ordered_robustness.v1"
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_ordered_robustness.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_ordered_robustness.md")
MIN_NOBS = 30
MIN_OUTCOME_LEVELS = 3


def run_cgss_ordered_robustness(frame: pd.DataFrame, topic: str, dataset_path: str) -> dict[str, Any]:
    analysis = prepare_ordered_frame(frame)
    gate = evaluate_method_gate(analysis)
    base_report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "dataset": {
            "path": dataset_path,
            "year": "2023",
            "source": "CGSS2023.dta",
        },
        "method_gate": gate,
        "sample": {
            "nobs": int(len(analysis)),
            "outcome_levels": sorted([int(value) for value in analysis["happiness"].dropna().unique()]),
        },
        "models": {},
        "boundary_flags": {
            "modified_formal_package": False,
            "modified_formal_variable_roles": False,
            "promoted_to_canonical_claim": False,
        },
    }
    if gate["status"] == "blocked":
        base_report.update(
            {
                "status": "blocked_by_method_gate",
                "interpretation_seed": {
                    "writing_note": "有序模型没有通过方法门禁；先修数据口径或样本条件，再进入论文写作。",
                },
                "next_tasks": ["review_ordered_model_gate", "repair_cgss_variable_binding"],
            }
        )
        return base_report

    ordered_result = fit_ordered_logit(analysis)
    base_report.update(
        {
            "status": "completed_needs_human_review",
            "models": {
                "ordered_logit_index": summarize_ordered_model(
                    ordered_result,
                    predictors=[
                        "social_capital_index",
                        "female",
                        "age",
                        "education_level",
                        "log_income",
                        "health",
                        "urban_hukou",
                    ],
                )
            },
            "interpretation_seed": build_interpretation_seed(ordered_result),
            "next_tasks": [
                "review_cgss_ordered_robustness",
                "bind_cgss_variable_roles",
                "draft_cgss_paper_from_ordered_robustness",
            ],
        }
    )
    return base_report


def prepare_ordered_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = [
        "happiness",
        "social_capital_index",
        "female",
        "age",
        "education_level",
        "log_income",
        "health",
        "urban_hukou",
        "province",
    ]
    analysis = frame[required].copy()
    for column in required:
        if column != "province":
            analysis[column] = pd.to_numeric(analysis[column], errors="coerce")
    analysis["happiness"] = analysis["happiness"].round()
    analysis = analysis[analysis["happiness"].between(1, 5)]
    analysis = analysis.replace([np.inf, -np.inf], pd.NA).dropna(subset=required)
    analysis["happiness"] = analysis["happiness"].astype(int)
    analysis["province"] = analysis["province"].astype("string")
    return analysis


def evaluate_method_gate(analysis: pd.DataFrame) -> dict[str, Any]:
    blocking_reasons = []
    if len(analysis) < MIN_NOBS:
        blocking_reasons.append("sample_too_small_for_ordered_model")
    if analysis["happiness"].nunique(dropna=True) < MIN_OUTCOME_LEVELS:
        blocking_reasons.append("outcome_has_too_few_ordered_levels")
    if analysis["social_capital_index"].std(skipna=True) == 0:
        blocking_reasons.append("social_capital_index_has_no_variation")
    return {
        "method": "ordered_logit",
        "status": "blocked" if blocking_reasons else "passed",
        "blocking_reasons": blocking_reasons,
        "checks": {
            "minimum_nobs": MIN_NOBS,
            "minimum_outcome_levels": MIN_OUTCOME_LEVELS,
            "observed_nobs": int(len(analysis)),
            "observed_outcome_levels": int(analysis["happiness"].nunique(dropna=True)),
        },
    }


def fit_ordered_logit(analysis: pd.DataFrame) -> Any:
    y = analysis["happiness"]
    exog = analysis[
        ["social_capital_index", "female", "age", "education_level", "log_income", "health", "urban_hukou"]
    ].astype(float)
    province_dummies = pd.get_dummies(analysis["province"], prefix="province", drop_first=True, dtype=float)
    exog = pd.concat([exog, province_dummies], axis=1)
    model = OrderedModel(y, exog, distr="logit")
    return model.fit(method="bfgs", disp=False, maxiter=300)


def summarize_ordered_model(result: Any, predictors: list[str]) -> dict[str, Any]:
    coefficients = {}
    for name in predictors:
        if name not in result.params:
            continue
        coefficients[name] = {
            "coef": safe_float(result.params[name]),
            "std_error": safe_float(result.bse[name]),
            "p_value": safe_float(result.pvalues[name]),
        }
    return {
        "method": "ordered_logit",
        "nobs": int(result.nobs),
        "log_likelihood": safe_float(result.llf),
        "aic": safe_float(result.aic),
        "coefficients": coefficients,
        "thresholds": {
            str(name): {
                "coef": safe_float(value),
                "std_error": safe_float(result.bse[name]) if name in result.bse else None,
            }
            for name, value in result.params.items()
            if "/" in str(name)
        },
    }


def build_interpretation_seed(result: Any) -> dict[str, Any]:
    coef = result.params.get("social_capital_index")
    return {
        "social_capital_index_direction": direction_label(coef),
        "writing_note": "有序 Logit 把幸福感按等级结果处理，用来检验 OLS 方向是否稳健。",
    }


def direction_label(coef: Any) -> str:
    if coef is None or pd.isna(coef):
        return "not_estimated"
    if coef > 0:
        return "positive"
    if coef < 0:
        return "negative"
    return "zero"


def write_ordered_outputs(
    project_root: Path, report: dict[str, Any], result_path: Path, review_path: Path
) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# CGSS 社会资本与幸福感有序模型稳健性",
        "",
        f"- 题目：{report['topic']}",
        f"- 状态：{report['status']}",
        f"- 样本量：{report['sample']['nobs']}",
        f"- 幸福感等级：{', '.join(str(value) for value in report['sample']['outcome_levels'])}",
        f"- 方法门禁：{report['method_gate']['status']}",
        "- 正式层写回：否",
    ]
    if report["method_gate"]["blocking_reasons"]:
        lines.extend(["", "## 阻断原因"])
        for reason in report["method_gate"]["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines) + "\n"

    model = report["models"]["ordered_logit_index"]
    lines.extend(
        [
            "",
            "## Ordered Logit 结果",
            "",
            "| variable | coef | se | p-value |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for name, stats in model["coefficients"].items():
        lines.append(f"| `{name}` | {stats['coef']:.4f} | {stats['std_error']:.4f} | {stats['p_value']:.4f} |")
    lines.extend(
        [
            "",
            "## 下一步",
            "- 人工确认社会资本变量口径。",
            "- 将 OLS 与 Ordered Logit 结果合并进论文结果段落。",
            "- 补充社会资本与幸福感的文献综述和机制解释。",
        ]
    )
    return "\n".join(lines) + "\n"


__all__ = [
    "DEFAULT_RESULT_PATH",
    "DEFAULT_REVIEW_PATH",
    "build_analysis_frame",
    "load_cgss_2023_frame",
    "run_cgss_ordered_robustness",
    "write_ordered_outputs",
]

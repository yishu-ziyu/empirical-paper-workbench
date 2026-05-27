from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


SCHEMA_VERSION = "p6.cgss_minimal_model.v1"
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_minimal_model.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_minimal_model.md")
MODEL_COLUMNS = ["a36", "a33", "a31a", "a31b", "a311", "a2", "a3a", "a7a", "a8a", "a15", "a18", "s41"]


def load_cgss_2023_frame(dataset_path: Path) -> pd.DataFrame:
    import pyreadstat  # type: ignore

    raw, _ = pyreadstat.read_dta(str(dataset_path), usecols=MODEL_COLUMNS)
    return build_analysis_frame(raw)


def build_analysis_frame(raw: pd.DataFrame) -> pd.DataFrame:
    data = raw.copy()
    for column in MODEL_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    for column in ["a36", "a33", "a31a", "a31b", "a311", "a2", "a3a", "a7a", "a8a", "a15", "a18", "s41"]:
        data.loc[data[column] < 0, column] = pd.NA
    data.loc[data["a8a"] >= 9999997, "a8a"] = pd.NA

    frame = pd.DataFrame(
        {
            "happiness": data["a36"],
            "trust": data["a33"],
            "neighbor_social": reverse_frequency(data["a31a"]),
            "friend_social": reverse_frequency(data["a31b"]),
            "leisure_social": data["a311"],
            "female": (data["a2"] == 2).astype("float"),
            "age": 2023 - data["a3a"],
            "education_level": data["a7a"],
            "log_income": np.log1p(data["a8a"].astype("float")),
            "health": data["a15"],
            "urban_hukou": data["a18"].isin([2, 4]).astype("float"),
            "province": data["s41"].astype("Int64").astype("string"),
        }
    )
    for column in ["trust", "neighbor_social", "friend_social", "leisure_social"]:
        frame[f"z_{column}"] = zscore(frame[column])
    frame["social_capital_index"] = frame[
        ["z_trust", "z_neighbor_social", "z_friend_social", "z_leisure_social"]
    ].mean(axis=1, skipna=False)
    frame = frame.dropna(
        subset=[
            "happiness",
            "social_capital_index",
            "trust",
            "female",
            "age",
            "education_level",
            "log_income",
            "health",
            "urban_hukou",
            "province",
        ]
    )
    frame = frame[(frame["age"] >= 16) & (frame["age"] <= 100)]
    return frame


def reverse_frequency(series: pd.Series) -> pd.Series:
    cleaned = series.copy()
    cleaned = cleaned.where(cleaned.between(1, 7))
    return 8 - cleaned


def zscore(series: pd.Series) -> pd.Series:
    mean = series.mean(skipna=True)
    std = series.std(skipna=True)
    if not std or pd.isna(std):
        return series * 0
    return (series - mean) / std


def run_cgss_minimal_model(frame: pd.DataFrame, topic: str, dataset_path: str) -> dict[str, Any]:
    formulas = {
        "baseline_index": "happiness ~ social_capital_index + female + age + education_level + log_income + health + urban_hukou + C(province)",
        "trust_only": "happiness ~ trust + female + age + education_level + log_income + health + urban_hukou + C(province)",
        "social_dimensions": "happiness ~ trust + neighbor_social + friend_social + leisure_social + female + age + education_level + log_income + health + urban_hukou + C(province)",
    }
    models = {}
    for model_id, formula in formulas.items():
        result = smf.ols(formula, data=frame).fit(cov_type="HC1")
        models[model_id] = summarize_model(result, formula)

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "status": "completed_needs_human_review",
        "dataset": {
            "path": dataset_path,
            "year": "2023",
            "source": "CGSS2023.dta",
        },
        "sample": {
            "nobs": int(len(frame)),
            "mean_happiness": safe_float(frame["happiness"].mean()),
            "mean_social_capital_index": safe_float(frame["social_capital_index"].mean()),
        },
        "variables": {
            "outcome": "happiness <- a36",
            "social_capital_index": ["a33 trust", "a31a neighbor_social", "a31b friend_social", "a311 leisure_social"],
            "controls": ["female", "age", "education_level", "log_income", "health", "urban_hukou", "province fixed effects"],
        },
        "models": models,
        "interpretation_seed": build_interpretation_seed(models),
        "next_tasks": ["review_cgss_minimal_model", "run_ordered_logit_robustness", "draft_cgss_paper_from_results"],
        "boundary_flags": {
            "modified_formal_package": False,
            "modified_formal_variable_roles": False,
            "promoted_to_canonical_claim": False,
        },
    }
    return report


def summarize_model(result: Any, formula: str) -> dict[str, Any]:
    coefficients = {}
    for name, value in result.params.items():
        if name == "Intercept" or name.startswith("C(province)"):
            continue
        coefficients[name] = {
            "coef": safe_float(value),
            "std_error_hc1": safe_float(result.bse[name]),
            "p_value": safe_float(result.pvalues[name]),
        }
    return {
        "formula": formula,
        "nobs": int(result.nobs),
        "r_squared": safe_float(result.rsquared),
        "coefficients": coefficients,
    }


def build_interpretation_seed(models: dict[str, Any]) -> dict[str, Any]:
    baseline = models["baseline_index"]["coefficients"].get("social_capital_index", {})
    trust = models["trust_only"]["coefficients"].get("trust", {})
    return {
        "baseline_index_direction": direction_label(baseline.get("coef")),
        "trust_direction": direction_label(trust.get("coef")),
        "writing_note": "这只是第一版实证结果种子；正式写作还要补文献、变量口径审阅、稳健性和机制解释。",
    }


def direction_label(coef: Any) -> str:
    if coef is None:
        return "not_estimated"
    if coef > 0:
        return "positive"
    if coef < 0:
        return "negative"
    return "zero"


def safe_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def write_model_outputs(project_root: Path, report: dict[str, Any], result_path: Path, review_path: Path) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# CGSS 社会资本与幸福感最小模型",
        "",
        f"- 题目：{report['topic']}",
        f"- 状态：{report['status']}",
        f"- 样本量：{report['sample']['nobs']}",
        f"- 数据：{report['dataset']['path']}",
        "- 正式层写回：否",
        "",
        "## 主要结果",
    ]
    for model_id, model in report["models"].items():
        lines.extend(["", f"### {model_id}", "", "| variable | coef | robust se | p-value |", "| --- | ---: | ---: | ---: |"])
        for name, stats in model["coefficients"].items():
            lines.append(
                f"| `{name}` | {stats['coef']:.4f} | {stats['std_error_hc1']:.4f} | {stats['p_value']:.4f} |"
            )
    lines.extend(
        [
            "",
            "## 下一步",
            "- 增加有序 Logit 稳健性。",
            "- 把社会资本拆成信任、社交网络、互助参与三个小节解释。",
            "- 补 CNKI / Scholar 文献综述后再进入完整论文草稿。",
        ]
    )
    return "\n".join(lines) + "\n"

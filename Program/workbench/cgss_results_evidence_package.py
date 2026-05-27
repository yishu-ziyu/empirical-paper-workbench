from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_results_evidence_package.v1"
DEFAULT_MINIMAL_MODEL_PATH = Path("Results/json/cgss_social_capital_happiness_minimal_model.json")
DEFAULT_ORDERED_ROBUSTNESS_PATH = Path("Results/json/cgss_social_capital_happiness_ordered_robustness.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_results_evidence_package.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_results_evidence_package(
    minimal_model: dict[str, Any],
    ordered_robustness: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    boundary_flags = {
        "modified_formal_package": False,
        "modified_formal_variable_roles": False,
        "promoted_to_canonical_claim": False,
    }
    blocking_reasons = blocking_reasons_for(minimal_model, ordered_robustness)
    topic = minimal_model.get("topic") or ordered_robustness.get("topic") or ""
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "source_artifacts": {
            "minimal_model": {
                "path": source_paths.get("minimal_model", str(DEFAULT_MINIMAL_MODEL_PATH)),
                "schema_version": minimal_model.get("schema_version"),
                "status": minimal_model.get("status"),
            },
            "ordered_robustness": {
                "path": source_paths.get("ordered_robustness", str(DEFAULT_ORDERED_ROBUSTNESS_PATH)),
                "schema_version": ordered_robustness.get("schema_version"),
                "status": ordered_robustness.get("status"),
            },
        },
        "source_models": {
            "minimal_model_status": minimal_model.get("status"),
            "ordered_robustness_status": ordered_robustness.get("status"),
        },
        "boundary_flags": boundary_flags,
    }
    if blocking_reasons:
        base.update(
            {
                "status": "blocked_missing_model_evidence",
                "blocking_reasons": blocking_reasons,
                "primary_result": {},
                "evidence_consistency": {},
                "variables": {},
                "writing_inputs": {},
                "human_review_checklist": [],
            }
        )
        return base

    ols = minimal_model["models"]["baseline_index"]["coefficients"]["social_capital_index"]
    ordered = ordered_robustness["models"]["ordered_logit_index"]["coefficients"]["social_capital_index"]
    primary_result = {
        "ols": {
            "model": "baseline_index",
            "variable": "social_capital_index",
            "coef": ols["coef"],
            "std_error": ols.get("std_error_hc1"),
            "p_value": ols["p_value"],
            "nobs": minimal_model["sample"]["nobs"],
        },
        "ordered_logit": {
            "model": "ordered_logit_index",
            "variable": "social_capital_index",
            "coef": ordered["coef"],
            "std_error": ordered.get("std_error"),
            "p_value": ordered["p_value"],
            "nobs": ordered_robustness["sample"]["nobs"],
            "outcome_levels": ordered_robustness["sample"].get("outcome_levels", []),
        },
    }
    consistency = {
        "sample_nobs_match": minimal_model["sample"]["nobs"] == ordered_robustness["sample"]["nobs"],
        "ordered_method_gate": ordered_robustness.get("method_gate", {}).get("status"),
        "social_capital_direction": direction_consistency(ols["coef"], ordered["coef"]),
    }
    base.update(
        {
            "status": "ready_for_paper_draft_input",
            "blocking_reasons": [],
            "dataset": minimal_model.get("dataset", {}),
            "variables": {
                "outcome": minimal_model.get("variables", {}).get("outcome", "happiness <- a36"),
                "social_capital": {
                    "index": "social_capital_index",
                    "source_items": minimal_model.get("variables", {}).get("social_capital_index", []),
                },
                "controls": minimal_model.get("variables", {}).get("controls", []),
                "ordered_outcome_levels": ordered_robustness.get("sample", {}).get("outcome_levels", []),
            },
            "primary_result": primary_result,
            "evidence_consistency": consistency,
            "human_review_checklist": [
                "outcome_measurement",
                "social_capital_index_construction",
                "control_variable_set",
                "ordered_model_interpretation",
                "literature_support_for_mechanism",
            ],
            "writing_inputs": {
                "result_sentence_seed": result_sentence(primary_result, consistency),
                "table_title_seed": "社会资本与居民主观幸福感：OLS 与 Ordered Logit 结果",
                "paper_section_targets": ["数据与变量", "实证结果", "稳健性检验"],
            },
            "next_tasks": [
                "human_review_cgss_variable_roles",
                "build_cgss_literature_review_seed",
                "draft_cgss_social_capital_happiness_paper",
            ],
        }
    )
    return base


def blocking_reasons_for(minimal_model: dict[str, Any], ordered_robustness: dict[str, Any]) -> list[str]:
    reasons = []
    if not minimal_model:
        reasons.append("missing_minimal_model")
    elif "social_capital_index" not in minimal_model.get("models", {}).get("baseline_index", {}).get("coefficients", {}):
        reasons.append("missing_ols_social_capital_index")
    if not ordered_robustness:
        reasons.append("missing_ordered_robustness")
    elif ordered_robustness.get("method_gate", {}).get("status") != "passed":
        reasons.append("ordered_model_gate_not_passed")
    elif "social_capital_index" not in ordered_robustness.get("models", {}).get("ordered_logit_index", {}).get(
        "coefficients", {}
    ):
        reasons.append("missing_ordered_social_capital_index")
    return reasons


def direction_consistency(ols_coef: float, ordered_coef: float) -> str:
    if ols_coef > 0 and ordered_coef > 0:
        return "consistent_positive"
    if ols_coef < 0 and ordered_coef < 0:
        return "consistent_negative"
    return "mixed_direction"


def result_sentence(primary_result: dict[str, Any], consistency: dict[str, Any]) -> str:
    ols = primary_result["ols"]
    ordered = primary_result["ordered_logit"]
    if consistency["social_capital_direction"] == "consistent_positive":
        direction = "正向相关"
    elif consistency["social_capital_direction"] == "consistent_negative":
        direction = "负向相关"
    else:
        direction = "方向不完全一致"
    return (
        "在 CGSS2023 样本中，社会资本指数与居民主观幸福感呈"
        f"{direction}；OLS 系数约为 {ols['coef']:.4f}，Ordered Logit 系数约为 {ordered['coef']:.4f}。"
    )


def write_evidence_outputs(
    project_root: Path, package: dict[str, Any], result_path: Path, review_path: Path
) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(package), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(package: dict[str, Any]) -> str:
    lines = [
        "# CGSS 社会资本与幸福感结果证据包",
        "",
        f"- 题目：{package.get('topic', '')}",
        f"- 状态：{package['status']}",
        "- 正式层写回：否",
    ]
    if package["blocking_reasons"]:
        lines.extend(["", "## 阻断原因"])
        for reason in package["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines) + "\n"

    ols = package["primary_result"]["ols"]
    ordered = package["primary_result"]["ordered_logit"]
    lines.extend(
        [
            "",
            "## 来源",
            f"- OLS：`{package['source_artifacts']['minimal_model']['path']}`",
            f"- Ordered Logit：`{package['source_artifacts']['ordered_robustness']['path']}`",
            "",
            "## 变量口径",
            f"- 因变量：`{package['variables']['outcome']}`",
            f"- 社会资本：`{package['variables']['social_capital']['index']}`",
            f"- 控制变量：{', '.join(f'`{item}`' for item in package['variables']['controls'])}",
            "",
            "## 主结果",
            "",
            "| model | variable | coef | se | p-value | nobs |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
            f"| OLS | `{ols['variable']}` | {ols['coef']:.4f} | {ols['std_error']:.4f} | {ols['p_value']:.4f} | {ols['nobs']} |",
            f"| Ordered Logit | `{ordered['variable']}` | {ordered['coef']:.4f} | {ordered['std_error']:.4f} | {ordered['p_value']:.4f} | {ordered['nobs']} |",
            "",
            "## 写作种子",
            package["writing_inputs"]["result_sentence_seed"],
            "",
            "## 人工确认清单",
        ]
    )
    for item in package["human_review_checklist"]:
        lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"

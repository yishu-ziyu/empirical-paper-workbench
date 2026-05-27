from __future__ import annotations

import json
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_run_plan_seed.v1"
DEFAULT_DESIGN_DRAFT_PATH = Path("Results/json/cgss_social_capital_happiness_design_spec_draft.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_run_plan_seed.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_run_plan_seed.md")
OLS_RESULT_PATH = "Results/json/cgss_social_capital_happiness_minimal_model.json"
OLS_REVIEW_PATH = "Reviews/cgss_social_capital_happiness_minimal_model.md"
ORDERED_RESULT_PATH = "Results/json/cgss_social_capital_happiness_ordered_robustness.json"
ORDERED_REVIEW_PATH = "Reviews/cgss_social_capital_happiness_ordered_robustness.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_run_plan_seed(
    design_spec_draft: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    boundary_flags = {
        "modified_formal_run_plan": False,
        "modified_formal_design_spec": False,
        "modified_formal_variable_roles": False,
        "generated_formal_paper": False,
        "wrote_state_product": False,
        "ran_models": False,
    }
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": design_spec_draft.get("topic", ""),
        "source_artifacts": {
            "design_spec_draft": {
                "path": source_paths.get("design_spec_draft", str(DEFAULT_DESIGN_DRAFT_PATH)),
                "schema_version": design_spec_draft.get("schema_version", ""),
                "status": design_spec_draft.get("status", ""),
            }
        },
        "boundary_flags": boundary_flags,
    }
    blocking_reasons = blocking_reasons_for(design_spec_draft)
    if blocking_reasons:
        base.update(
            {
                "status": "blocked_missing_reviewable_design_spec_draft",
                "blocking_reasons": blocking_reasons,
                "run_plan_seed": {},
                "execution_preflight": {},
                "promotion": {"allowed": False, "required_decision": "repair_cgss_design_spec_draft"},
                "next_tasks": ["repair_cgss_design_spec_draft"],
            }
        )
        return base

    design = design_spec_draft["design_spec_draft"]
    preflight = build_execution_preflight(design)
    run_plan_seed = build_run_plan_seed(design_spec_draft.get("topic", ""), design, preflight)
    base.update(
        {
            "status": "needs_human_run_plan_seed_review",
            "blocking_reasons": [],
            "run_plan_seed": run_plan_seed,
            "execution_preflight": preflight,
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_cgss_run_plan_seed",
                "would_write_if_approved": "state/product/run_plan.json",
            },
            "next_tasks": [
                "human_review_cgss_run_plan_seed",
                "after_approval_execute_cgss_ols_and_ordered_logit",
                "combine_cgss_results_evidence_package",
            ],
        }
    )
    return base


def blocking_reasons_for(design_spec_draft: dict[str, Any]) -> list[str]:
    reasons = []
    if design_spec_draft.get("status") != "needs_human_design_spec_review":
        reasons.append("design_spec_draft_not_reviewable")
    design = design_spec_draft.get("design_spec_draft") or {}
    if not design:
        reasons.append("design_spec_draft_missing")
    if not design.get("dataset_path"):
        reasons.append("dataset_path_missing")
    if not design.get("model_candidates"):
        reasons.append("model_candidates_missing")
    return reasons


def build_execution_preflight(design: dict[str, Any]) -> dict[str, Any]:
    source_bindings = design.get("source_variable_bindings", {})
    outcome_source = first_item(source_bindings.get("outcome"))
    treatment_items = source_bindings.get("treatment_items", [])
    source_controls = source_bindings.get("control_items", [])
    required_source_columns = [
        outcome_source,
        *treatment_items,
        *[column for column in ["a2", "a3a", "a7a", "a8a", "a15", "a18", "s41"] if column in source_controls],
    ]
    required_source_columns = unique_nonempty(required_source_columns)
    return {
        "status": "ready_for_human_review",
        "dataset_path": design.get("dataset_path", ""),
        "required_source_columns": required_source_columns,
        "required_analysis_columns": [
            "happiness",
            "social_capital_index",
            "female",
            "age",
            "education_level",
            "log_income",
            "health",
            "urban_hukou",
            "province",
        ],
        "deferred_control_source_columns": [column for column in ["a7b", "a21", "a8b"] if column in source_controls],
        "feature_engineering": {
            "outcome": {"target": "happiness", "source": outcome_source, "rule": "numeric ordered 1-5 happiness scale"},
            "social_capital_index": {
                "target": "social_capital_index",
                "source_items": treatment_items,
                "rule": "z-score trust, reversed neighbor/friend frequency, leisure social participation, then average",
            },
            "controls": {
                "female": "a2 == 2",
                "age": "2023 - a3a",
                "education_level": "a7a",
                "log_income": "log1p(a8a)",
                "health": "a15",
                "urban_hukou": "a18 in [2, 4]",
                "province": "s41 fixed effects",
            },
            "missingness_policy": [
                "negative CGSS special codes are treated as missing",
                "a8a >= 9999997 is treated as missing",
                "drop rows missing outcome, treatment index, required controls, or province",
                "keep analysis ages from 16 to 100",
            ],
        },
        "failure_explanations": [
            "dataset_missing_or_unreadable",
            "required_source_columns_missing",
            "too_few_complete_rows_after_missingness_filter",
            "outcome_has_too_few_ordered_levels_for_ordered_logit",
            "social_capital_index_has_no_variation",
        ],
        "adapter_entrypoints": {
            "analysis_frame": "Program/workbench/cgss_minimal_model.py::build_analysis_frame",
            "ols": "Program/cgss_minimal_model.py",
            "ordered_logit": "Program/cgss_ordered_robustness.py",
        },
    }


def build_run_plan_seed(topic: str, design: dict[str, Any], preflight: dict[str, Any]) -> dict[str, Any]:
    dataset_path = design.get("dataset_path", "")
    formula = executable_formula()
    return {
        "id": "cgss_run_plan_seed",
        "version": 0,
        "status": "draft_needs_human_review",
        "evidence_level": "local_file",
        "design_spec_draft_id": design.get("id", "cgss_design_spec_draft"),
        "dataset_path": dataset_path,
        "tasks": [
            {
                "id": "cgss_data_preflight",
                "label": "CGSS 数据读取和字段预检",
                "method_id": "data_preflight",
                "status": "planned",
                "required_source_columns": preflight["required_source_columns"],
                "evidence_level": "local_file",
            },
            {
                "id": "build_cgss_analysis_frame",
                "label": "构造 CGSS 分析样本和社会资本指数",
                "method_id": "feature_engineering",
                "status": "planned",
                "adapter": "Program/workbench/cgss_minimal_model.py::build_analysis_frame",
                "required_analysis_columns": preflight["required_analysis_columns"],
                "evidence_level": "local_file",
            },
            {
                "id": "run_ols_baseline",
                "label": "OLS 基准模型",
                "method_id": "ols",
                "estimator": "ols",
                "status": "planned",
                "design_spec_id": design.get("id", "cgss_design_spec_draft"),
                "formula": formula,
                "cli": cli_command("Program/cgss_minimal_model.py", dataset_path, topic),
                "expected_outputs": [OLS_RESULT_PATH, OLS_REVIEW_PATH],
                "evidence_level": "local_file",
            },
            {
                "id": "run_ordered_logit_robustness",
                "label": "Ordered Logit 有序模型",
                "method_id": "ordered_logit",
                "estimator": "ordered_logit",
                "status": "planned",
                "design_spec_id": design.get("id", "cgss_design_spec_draft"),
                "formula": formula,
                "cli": cli_command("Program/cgss_ordered_robustness.py", dataset_path, topic),
                "expected_outputs": [ORDERED_RESULT_PATH, ORDERED_REVIEW_PATH],
                "evidence_level": "local_file",
            },
        ],
        "outputs": [
            OLS_RESULT_PATH,
            OLS_REVIEW_PATH,
            ORDERED_RESULT_PATH,
            ORDERED_REVIEW_PATH,
            "Results/json/cgss_social_capital_happiness_results_evidence_package.json",
        ],
        "decision_events": [],
    }


def executable_formula() -> str:
    return (
        "happiness ~ social_capital_index + female + age + education_level + "
        "log_income + health + urban_hukou + C(province)"
    )


def cli_command(script_path: str, dataset_path: str, topic: str) -> str:
    return f"python3 {script_path} --project-root . --dataset {shlex.quote(dataset_path)} --topic {shlex.quote(topic)}"


def write_cgss_run_plan_seed_outputs(
    project_root: Path,
    report: dict[str, Any],
    result_path: Path,
    review_path: Path,
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
        "# CGSS RunPlan seed",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- 状态：`{report['status']}`",
        "- 写入正式 RunPlan：不写正式 RunPlan",
        "- 执行模型：否，仅生成可审阅计划",
    ]
    if report["blocking_reasons"]:
        lines.extend(["", "## 当前阻断"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines) + "\n"

    preflight = report["execution_preflight"]
    lines.extend(
        [
            "",
            "## 执行前预检",
            f"- 数据：`{preflight['dataset_path']}`",
            f"- 必需原始字段：`{', '.join(preflight['required_source_columns'])}`",
            f"- 执行变量：`{', '.join(preflight['required_analysis_columns'])}`",
            f"- 暂缓控制字段：`{', '.join(preflight['deferred_control_source_columns']) or '无'}`",
            "",
            "## 任务",
        ]
    )
    for task in report["run_plan_seed"]["tasks"]:
        lines.append(f"- {task['label']}：`{task['id']}` / `{task['method_id']}`")
        if task.get("cli"):
            lines.append(f"  - 命令：`{task['cli']}`")
        if task.get("expected_outputs"):
            lines.append(f"  - 产物：`{', '.join(task['expected_outputs'])}`")
    lines.extend(["", "## 失败时先看"])
    for reason in preflight["failure_explanations"]:
        lines.append(f"- `{reason}`")
    lines.extend(["", "## 下一步"])
    for task in report["next_tasks"]:
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"


def first_item(value: Any) -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str):
        return value
    return ""


def unique_nonempty(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result

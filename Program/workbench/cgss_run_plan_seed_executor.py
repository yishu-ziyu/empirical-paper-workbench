from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from Program.workbench.cgss_minimal_model import (
    DEFAULT_RESULT_PATH as OLS_RESULT_PATH,
    DEFAULT_REVIEW_PATH as OLS_REVIEW_PATH,
    load_cgss_2023_frame,
    run_cgss_minimal_model,
    write_model_outputs,
)
from Program.workbench.cgss_ordered_robustness import (
    DEFAULT_RESULT_PATH as ORDERED_RESULT_PATH,
    DEFAULT_REVIEW_PATH as ORDERED_REVIEW_PATH,
    run_cgss_ordered_robustness,
    write_ordered_outputs,
)
from Program.workbench.cgss_results_evidence_package import (
    DEFAULT_RESULT_PATH as EVIDENCE_RESULT_PATH,
    DEFAULT_REVIEW_PATH as EVIDENCE_REVIEW_PATH,
    build_results_evidence_package,
    write_evidence_outputs,
)


SCHEMA_VERSION = "p6.cgss_run_plan_seed_execution.v1"
DEFAULT_APPROVED_SEED_PATH = Path("Results/json/cgss_social_capital_happiness_run_plan_seed_approved.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_run_plan_seed_execution.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_run_plan_seed_execution.md")
DEFAULT_TOPIC = "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析"
ModelRunner = Callable[[Path, dict[str, Any], str], tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_blocked_execution_report(approved_seed: dict[str, Any], topic: str, reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "status": "blocked_run_plan_seed_not_approved",
        "blocking_reasons": [reason],
        "approved_seed_status": approved_seed.get("status", ""),
        "ran_models": False,
        "formal_writeback_allowed": False,
        "draft_layer_only": True,
        "executed_tasks": [],
        "model_artifacts": {},
        "evidence_package": {},
        "next_tasks": ["approve_or_revise_cgss_run_plan_seed"],
    }


def execute_approved_cgss_run_plan_seed(
    project_root: Path,
    approved_seed: dict[str, Any],
    topic: str,
    model_runner: ModelRunner | None = None,
) -> dict[str, Any]:
    blocking_reason = approval_blocking_reason(approved_seed)
    if blocking_reason:
        return build_blocked_execution_report(approved_seed, topic, blocking_reason)

    model_runner = model_runner or run_model_tasks
    minimal_model, ordered_robustness, evidence_package = model_runner(project_root, approved_seed, topic)
    executed_tasks = planned_execution_task_ids(approved_seed)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "status": execution_status(evidence_package),
        "blocking_reasons": evidence_package.get("blocking_reasons", []),
        "approved_seed": {
            "id": approved_seed.get("id", ""),
            "status": approved_seed.get("status", ""),
            "approved_by": approved_seed.get("human_approval", {}).get("approved_by", ""),
        },
        "ran_models": True,
        "formal_writeback_allowed": False,
        "draft_layer_only": True,
        "executed_tasks": executed_tasks,
        "model_artifacts": {
            "minimal_model": {
                "path": str(OLS_RESULT_PATH),
                "schema_version": minimal_model.get("schema_version", ""),
                "status": minimal_model.get("status", ""),
            },
            "ordered_robustness": {
                "path": str(ORDERED_RESULT_PATH),
                "schema_version": ordered_robustness.get("schema_version", ""),
                "status": ordered_robustness.get("status", ""),
                "method_gate": ordered_robustness.get("method_gate", {}).get("status", ""),
            },
            "evidence_package": {
                "path": str(EVIDENCE_RESULT_PATH),
                "schema_version": evidence_package.get("schema_version", ""),
                "status": evidence_package.get("status", ""),
            },
        },
        "evidence_package": evidence_package,
        "next_tasks": [
            "human_review_cgss_results_evidence_package",
            "route_cgss_evidence_into_manuscript_draft",
        ],
    }


def approval_blocking_reason(approved_seed: dict[str, Any]) -> str:
    if not approved_seed:
        return "missing_approved_run_plan_seed"
    if approved_seed.get("status") != "approved_for_draft_execution":
        return "run_plan_seed_not_approved_for_draft_execution"
    if approved_seed.get("human_approval", {}).get("status") != "approved":
        return "missing_approved_human_decision"
    return ""


def planned_execution_task_ids(approved_seed: dict[str, Any]) -> list[str]:
    allowed_methods = {"ols", "ordered_logit"}
    return [
        task.get("id", "")
        for task in approved_seed.get("tasks", [])
        if task.get("method_id") in allowed_methods and task.get("id")
    ]


def execution_status(evidence_package: dict[str, Any]) -> str:
    if evidence_package.get("status") == "ready_for_paper_draft_input":
        return "completed_needs_human_result_review"
    return "completed_with_evidence_warnings"


def run_model_tasks(
    project_root: Path,
    approved_seed: dict[str, Any],
    topic: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    dataset_path = Path(approved_seed.get("dataset_path", ""))
    frame = load_cgss_2023_frame(dataset_path)

    minimal_model = run_cgss_minimal_model(frame, topic, str(dataset_path))
    write_model_outputs(project_root, minimal_model, OLS_RESULT_PATH, OLS_REVIEW_PATH)

    ordered_robustness = run_cgss_ordered_robustness(frame, topic, str(dataset_path))
    write_ordered_outputs(project_root, ordered_robustness, ORDERED_RESULT_PATH, ORDERED_REVIEW_PATH)

    evidence_package = build_results_evidence_package(
        minimal_model,
        ordered_robustness,
        {
            "minimal_model": str(OLS_RESULT_PATH),
            "ordered_robustness": str(ORDERED_RESULT_PATH),
        },
    )
    write_evidence_outputs(project_root, evidence_package, EVIDENCE_RESULT_PATH, EVIDENCE_REVIEW_PATH)
    return minimal_model, ordered_robustness, evidence_package


def write_cgss_run_plan_seed_execution_outputs(
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
        "# CGSS RunPlan seed 执行记录",
        "",
        f"- 题目：{report.get('topic', '')}",
        f"- schema：`{report['schema_version']}`",
        f"- 状态：`{report['status']}`",
        f"- 已执行模型：{'是' if report.get('ran_models') else '否'}",
        "- 草案层：是",
        "- 写入正式 RunPlan：否",
        "- 写入 state/product：否",
    ]
    if report.get("blocking_reasons"):
        lines.extend(["", "## 当前阻断"])
        for reason in report["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines) + "\n"

    lines.extend(["", "## 执行任务"])
    for task_id in report.get("executed_tasks", []):
        lines.append(f"- `{task_id}`")
    lines.extend(["", "## 产物"])
    for label, artifact in report.get("model_artifacts", {}).items():
        lines.append(f"- {label}：`{artifact.get('path', '')}`，状态 `{artifact.get('status', '')}`")
    evidence = report.get("evidence_package", {})
    if evidence.get("writing_inputs", {}).get("result_sentence_seed"):
        lines.extend(["", "## 写作种子", evidence["writing_inputs"]["result_sentence_seed"]])
    lines.extend(["", "## 下一步"])
    for task in report.get("next_tasks", []):
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"

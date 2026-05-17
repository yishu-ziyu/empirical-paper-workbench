from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id
from Product.backend.results_draft_service import get_project_results_draft, project_root_for


REVIEWER_SCORECARD_PATH = "state/product/reviewer_scorecard.json"


def reviewer_scorecard_state_path(project_root: Path) -> Path:
    return project_root / REVIEWER_SCORECARD_PATH


def get_project_reviewer_scorecard(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    results_draft = get_project_results_draft(product_root, repo_root, project_id)
    saved = load_saved_reviewer_scorecard(project_root)
    if saved:
        return {**saved, "_meta": local_file_meta()}
    return {
        "_meta": local_file_meta(),
        "project_id": project_id,
        "status": "not_generated",
        "evidence_level": "local_file",
        "reviewer_backend": "deterministic_baseline",
        "source_run_id": results_draft.get("latest_run_id"),
        "dimensions": [],
        "can_generate": True,
        "path": REVIEWER_SCORECARD_PATH,
        "empty_state": {
            "code": "reviewer_scorecard_not_generated",
            "title": "尚未生成审稿评分卡",
            "description": "生成后会显示五个审稿维度、证据绑定和后续任务建议。",
        },
    }


def generate_project_reviewer_scorecard(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    note: str = "",
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = project_root_for(project)
    results_draft = get_project_results_draft(product_root, repo_root, project_id)
    scorecard = build_scorecard(project_id, results_draft, note)
    path = reviewer_scorecard_state_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scorecard, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**scorecard, "_meta": local_file_meta()}


def load_saved_reviewer_scorecard(project_root: Path) -> dict[str, Any] | None:
    path = reviewer_scorecard_state_path(project_root)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_scorecard(project_id: str, results_draft: dict[str, Any], note: str = "") -> dict[str, Any]:
    finding = first_finding(results_draft)
    timestamp = utc_now()
    return {
        "id": "reviewer_scorecard",
        "project_id": project_id,
        "status": "needs_review",
        "evidence_level": "local_file",
        "reviewer_backend": "deterministic_baseline",
        "source_run_id": results_draft.get("latest_run_id"),
        "source_result_artifact": (results_draft.get("result_artifact") or {}).get("path"),
        "source_draft_artifact": (results_draft.get("draft_artifact") or {}).get("path"),
        "path": REVIEWER_SCORECARD_PATH,
        "generated_at": timestamp,
        "note": note,
        "dimensions": build_dimensions(results_draft, finding),
        "ui_contract": {
            "summary_first": True,
            "details_collapsed_by_default": True,
            "task_suggestions_require_human_acceptance": True,
        },
    }


def first_finding(results_draft: dict[str, Any]) -> dict[str, Any]:
    findings = results_draft.get("findings") or []
    if findings:
        return findings[0]
    return {}


def build_dimensions(results_draft: dict[str, Any], finding: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = base_evidence(results_draft, finding)
    return [
        {
            "id": "novelty",
            "label": "新颖性",
            "score": 6.0,
            "rationale": "当前论断已经绑定真实执行结果，但研究问题的新颖性还没有经过文献和相似选题检索。",
            "evidence": evidence,
            "suggested_tasks": [
                suggested_task(
                    "review_related_literature",
                    "检索相近研究并判断选题增量",
                    "Literature Agent",
                    ["research_question", "finding_card"],
                )
            ],
        },
        {
            "id": "identification_credibility",
            "label": "识别可信度",
            "score": 5.2,
            "rationale": "当前 FindingCard 来自 OLS 基准结果，尚未完成 DID/IV/RDD/PSM/DML 等更强识别或稳健性诊断。",
            "evidence": evidence + [{"path": "state/product/run_plan.json", "evidence_level": "local_file"}],
            "suggested_tasks": [
                suggested_task(
                    "add_method_diagnostics_or_robustness",
                    "补充方法诊断或稳健性检验",
                    "Design Agent",
                    ["method_workflows", "run_plan", "method_execution_result"],
                ),
                suggested_task(
                    "review_identification_assumptions",
                    "审阅识别假设和潜在内生性",
                    "Reviewer Agent",
                    ["design_spec", "finding_card"],
                ),
            ],
        },
        {
            "id": "data_quality",
            "label": "数据质量",
            "score": data_quality_score(finding),
            "rationale": "结果已绑定样本量和本地数据来源，但真实 CFPS 字段画像、缺失值和值标签审计仍需继续补齐。",
            "evidence": evidence + [{"path": "Data/Final/analysis_sample.csv", "evidence_level": "local_file"}],
            "suggested_tasks": [
                suggested_task(
                    "expand_data_quality_profile",
                    "补齐真实数据缺失值和值标签审计",
                    "Data Agent",
                    ["dataset_profile", "variable_roles"],
                )
            ],
        },
        {
            "id": "clarity",
            "label": "表达清晰度",
            "score": 6.5,
            "rationale": "草稿已有可追溯段落候选，但还没有完整 section editor、评论和版本历史。",
            "evidence": evidence + [{"path": "Manuscripts/generated/paper_draft.md", "evidence_level": "local_file"}],
            "suggested_tasks": [
                suggested_task(
                    "tighten_manuscript_claim_language",
                    "把可写入论断改成更清晰的结果段落",
                    "Manuscript Agent",
                    ["manuscript_candidate", "finding_review"],
                )
            ],
        },
        {
            "id": "policy_relevance",
            "label": "政策相关性",
            "score": 5.8,
            "rationale": "当前结果解释还没有明确连接政策场景、机制和外部有效性边界。",
            "evidence": evidence,
            "suggested_tasks": [
                suggested_task(
                    "add_policy_relevance_review",
                    "补充政策含义和外部有效性边界",
                    "Reviewer Agent",
                    ["finding_card", "draft_section"],
                )
            ],
        },
    ]


def base_evidence(results_draft: dict[str, Any], finding: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "path": (results_draft.get("result_artifact") or {}).get("path") or "Results/json/analysis_result.json",
            "evidence_level": "local_execution",
        },
        {
            "path": finding.get("artifact_path") or "Results/json/analysis_result.json",
            "evidence_level": finding.get("evidence_level") or "local_execution",
            "run_id": finding.get("run_id") or results_draft.get("latest_run_id"),
        },
    ]


def data_quality_score(finding: dict[str, Any]) -> float:
    sample_size = finding.get("sample_size") or 0
    if sample_size >= 100:
        return 7.5
    if sample_size >= 10:
        return 7.0
    return 5.5


def suggested_task(task_id: str, label: str, target_agent: str, evidence_requirements: list[str]) -> dict[str, Any]:
    return {
        "id": task_id,
        "label": label,
        "target_agent": target_agent,
        "requires_human_acceptance": True,
        "evidence_requirements": evidence_requirements,
        "status": "suggested",
    }


def local_file_meta() -> dict[str, str]:
    return {
        "evidence_level": "local_file",
        "service": "reviewer_score_service",
        "generated_at": utc_now(),
    }

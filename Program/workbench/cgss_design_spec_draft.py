from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_design_spec_draft.v1"
DEFAULT_ROLE_DRAFT_PATH = Path("Results/json/cgss_social_capital_happiness_dataset_bound_variable_role_draft.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_design_spec_draft.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_design_spec_draft.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_design_spec_draft(
    dataset_bound_role_draft: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    boundary_flags = {
        "modified_formal_design_spec": False,
        "modified_formal_variable_roles": False,
        "modified_run_plan": False,
        "generated_formal_paper": False,
        "wrote_state_product": False,
    }
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": dataset_bound_role_draft.get("topic", ""),
        "source_artifacts": {
            "dataset_bound_variable_role_draft": {
                "path": source_paths.get("dataset_bound_variable_role_draft", str(DEFAULT_ROLE_DRAFT_PATH)),
                "schema_version": dataset_bound_role_draft.get("schema_version", ""),
                "status": dataset_bound_role_draft.get("status", ""),
            }
        },
        "boundary_flags": boundary_flags,
    }
    blocking_reasons = blocking_reasons_for(dataset_bound_role_draft)
    if blocking_reasons:
        base.update(
            {
                "status": "blocked_missing_dataset_bound_variable_roles",
                "blocking_reasons": blocking_reasons,
                "design_spec_draft": {},
                "method_family_gate": {"blocked_method_families": []},
                "review_gates": [],
                "promotion": {"allowed": False, "required_decision": "repair_dataset_bound_variable_roles"},
                "next_tasks": ["repair_dataset_bound_variable_role_draft"],
            }
        )
        return base

    roles = dataset_bound_role_draft["proposed_roles"]
    dataset = dataset_bound_role_draft["dataset_binding"]
    design_spec = build_design_spec(dataset_bound_role_draft.get("topic", ""), dataset, roles)
    base.update(
        {
            "status": "needs_human_design_spec_review",
            "blocking_reasons": [],
            "design_spec_draft": design_spec,
            "method_family_gate": build_method_family_gate(),
            "review_gates": [
                "outcome_order_and_coding_review",
                "social_capital_index_construction_review",
                "control_set_and_missingness_review",
                "cross_section_identification_boundary_review",
                "literature_support_required",
            ],
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_cgss_design_spec_draft",
                "would_write_if_approved": "state/product/design_spec.json",
            },
            "next_tasks": [
                "human_review_cgss_design_spec_draft",
                "after_approval_build_RunPlan_draft",
                "prepare_cgss_minimal_model_execution",
            ],
        }
    )
    return base


def blocking_reasons_for(role_draft: dict[str, Any]) -> list[str]:
    reasons = []
    if role_draft.get("status") != "needs_human_dataset_bound_role_review":
        reasons.append("dataset_bound_variable_roles_not_reviewable")
    if not role_draft.get("dataset_binding"):
        reasons.append("dataset_binding_missing")
    proposed_roles = role_draft.get("proposed_roles") or {}
    if not proposed_roles.get("outcome"):
        reasons.append("outcome_role_missing")
    if not proposed_roles.get("treatment"):
        reasons.append("treatment_role_missing")
    if not proposed_roles.get("controls"):
        reasons.append("control_roles_missing")
    return reasons


def build_design_spec(topic: str, dataset: dict[str, Any], roles: dict[str, Any]) -> dict[str, Any]:
    outcome = roles["outcome"]
    treatment = roles["treatment"]
    controls = roles["controls"]
    outcome_name = outcome["canonical_name"]
    treatment_name = treatment["canonical_name"]
    control_items = controls.get("source_items", [])
    formula = build_formula(outcome_name, treatment_name, control_items)
    return {
        "id": "cgss_design_spec_draft",
        "status": "draft_needs_human_review",
        "research_question": topic,
        "dataset_year": dataset.get("year"),
        "dataset_path": dataset.get("path"),
        "dataset_evidence_level": dataset.get("evidence_level", "local_file"),
        "variables": {
            "outcome": [outcome_name],
            "treatment": [treatment_name],
            "controls": control_items,
            "fixed_effects": ["s41"] if "s41" in control_items else [],
            "cluster_by": [],
        },
        "source_variable_bindings": {
            "outcome": [outcome.get("source_variable", "")],
            "treatment_items": treatment.get("source_items", []),
            "control_items": control_items,
            "role_mapping": controls.get("role_mapping", {}),
        },
        "identification_strategy": {
            "name": "cross_section_conditional_association",
            "summary": "当前 CGSS2023 是横截面数据，本阶段先估计社会资本与主观幸福感之间的条件相关关系。",
            "assumptions": [
                "控制人口学、教育、健康、收入、户籍和地区差异后，剩余相关关系可作为探索性证据。",
                "社会资本指数构造方向、幸福感编码方向和缺失值处理需要人工确认。",
            ],
            "threats": [
                "遗漏变量偏误",
                "反向因果",
                "共同方法偏差",
                "社会资本指数构造偏差",
                "横截面数据无法识别动态因果路径",
            ],
        },
        "feature_engineering": {
            "social_capital_index": {
                "target_name": treatment_name,
                "source_items": treatment.get("source_items", []),
                "construction_plan": "先按信任、邻里交往、朋友交往和休闲社交四个维度做标准化方向核对；人工确认后再决定均值指数或分维度模型。",
                "requires_human_review": True,
            },
            "happiness_scale": {
                "source_item": outcome.get("source_variable", ""),
                "construction_plan": "核对 a36 的编码方向、拒答/不知道缺失码和 1-5 有序等级含义。",
                "requires_human_review": True,
            },
        },
        "model_candidates": [
            {
                "id": "ols_baseline",
                "estimator": "ols",
                "formula": formula,
                "purpose": "给出最直观的基准相关关系，便于解释方向、数量级和控制变量变化。",
                "readiness": "ready_after_variable_construction_review",
            },
            {
                "id": "ordered_logit",
                "estimator": "ordered_logit",
                "formula": formula,
                "purpose": "把幸福感作为有序结果处理，用于检验 OLS 方向是否稳定。",
                "readiness": "ready_after_outcome_scale_review",
            },
        ],
        "claim_boundary": {
            "level": "conditional_association_not_strong_causality",
            "plain_language": "可以写社会资本与幸福感存在正向或负向条件相关；暂不写社会资本严格导致幸福感变化。",
        },
    }


def build_formula(outcome: str, treatment: str, controls: list[str]) -> str:
    rhs = [treatment, *[item for item in controls if item != ""]]
    return f"{outcome} ~ {' + '.join(rhs)}"


def build_method_family_gate() -> dict[str, Any]:
    return {
        "recommended_now": ["OLS baseline", "Ordered Logit robustness"],
        "blocked_method_families": [
            {"method": "DID", "reason": "当前题目没有明确政策冲击、处理组/对照组、处理时间和处理前趋势。"},
            {"method": "IV", "reason": "当前没有经过文献和数据共同支持的工具变量，也没有排除性约束说明。"},
            {"method": "RDD", "reason": "当前没有断点、运行变量、阈值规则和带宽诊断条件。"},
            {"method": "PSM", "reason": "当前社会资本是连续/多维构造草案，还没有二元处理定义和平衡性诊断。"},
            {"method": "DML", "reason": "当前目标是建立可解释基准模型，还没有因果处理设定、交叉拟合方案和 nuisance 模型诊断。"},
        ],
    }


def write_cgss_design_spec_draft_outputs(
    project_root: Path,
    draft: dict[str, Any],
    result_path: Path,
    review_path: Path,
) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(draft), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(draft: dict[str, Any]) -> str:
    lines = [
        "# CGSS 研究设计草案",
        "",
        f"- 题目：{draft.get('topic', '')}",
        f"- 状态：`{draft['status']}`",
        "- 写入正式 DesignSpec：不写正式 DesignSpec",
        "- 写入 RunPlan：否",
    ]
    if draft["blocking_reasons"]:
        lines.extend(["", "## 当前阻断"])
        for reason in draft["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines) + "\n"

    design = draft["design_spec_draft"]
    lines.extend(
        [
            "",
            "## 数据与变量",
            f"- 数据：CGSS{design['dataset_year']} `{design['dataset_path']}`",
            f"- 因变量：`{design['variables']['outcome'][0]}` <- `{design['source_variable_bindings']['outcome'][0]}`",
            f"- 核心解释变量：`{design['variables']['treatment'][0]}` <- `{', '.join(design['source_variable_bindings']['treatment_items'])}`",
            f"- 控制变量：`{', '.join(design['variables']['controls'])}`",
            "",
            "## 识别边界",
            f"- {design['identification_strategy']['summary']}",
            f"- 结论边界：{design['claim_boundary']['plain_language']}",
            "",
            "## 模型候选",
        ]
    )
    for model in design["model_candidates"]:
        model_label = readable_model_label(model["id"])
        lines.append(f"- {model_label}（{model['estimator']}）：`{model['formula']}`；{model['purpose']}")
    lines.extend(["", "## 暂不进入的计量方法"])
    for item in draft["method_family_gate"]["blocked_method_families"]:
        lines.append(f"- {item['method']}：{item['reason']}")
    lines.extend(["", "## 审阅门禁"])
    for gate in draft["review_gates"]:
        lines.append(f"- `{gate}`")
    lines.extend(["", "## 下一步"])
    for task in draft["next_tasks"]:
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"


def readable_model_label(model_id: str) -> str:
    labels = {
        "ols_baseline": "OLS 基准模型",
        "ordered_logit": "Ordered Logit 有序模型",
    }
    return labels.get(model_id, model_id)

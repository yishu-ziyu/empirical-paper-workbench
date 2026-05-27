from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_variable_role_review_draft.v1"
DEFAULT_EVIDENCE_PACKAGE_PATH = Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json")
DEFAULT_VARIABLE_CANDIDATES_PATH = Path("Results/json/cgss_social_capital_happiness_variable_candidates.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_variable_role_review_draft.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_variable_role_review_draft.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_variable_role_review_draft(
    evidence_package: dict[str, Any],
    variable_candidates: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    boundary_flags = {
        "modified_formal_package": False,
        "modified_formal_variable_roles": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "wrote_state_product": False,
    }
    source_artifacts = {
        "evidence_package": {
            "path": source_paths.get("evidence_package", str(DEFAULT_EVIDENCE_PACKAGE_PATH)),
            "schema_version": evidence_package.get("schema_version", ""),
            "status": evidence_package.get("status", ""),
        },
        "variable_candidates": {
            "path": source_paths.get("variable_candidates", str(DEFAULT_VARIABLE_CANDIDATES_PATH)),
            "schema_version": variable_candidates.get("schema_version", ""),
            "status": variable_candidates.get("status", ""),
        },
    }
    source_artifacts.update(evidence_package.get("source_artifacts", {}))
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": evidence_package.get("topic") or variable_candidates.get("topic") or "",
        "source_artifacts": source_artifacts,
        "boundary_flags": boundary_flags,
    }
    blocking_reasons = blocking_reasons_for(evidence_package, variable_candidates)
    if blocking_reasons:
        base.update(
            {
                "status": "blocked_missing_evidence_package",
                "blocking_reasons": blocking_reasons,
                "proposed_roles": {},
                "review_gates": [],
                "promotion": {"allowed": False, "required_decision": "repair_inputs"},
            }
        )
        return base

    variables = evidence_package["variables"]
    candidate_roles = variable_candidates.get("role_candidates", {})
    proposed_roles = {
        "outcome": {
            "canonical_name": "happiness",
            "source_variable": parse_source_variable(variables["outcome"]),
            "source_label": label_for(candidate_roles.get("outcome", []), parse_source_variable(variables["outcome"])),
            "ordered_levels": variables.get("ordered_outcome_levels", []),
            "measurement_level": "ordered_1_to_5",
            "rationale": "题项直接询问总体生活幸福感，和题目中的居民主观幸福感概念一致；有序模型已经验证 1-5 等级口径可用。",
        },
        "treatment": {
            "canonical_name": variables["social_capital"]["index"],
            "source_items": source_item_names(variables["social_capital"].get("source_items", [])),
            "source_labels": source_labels_for(
                candidate_roles.get("social_capital", []),
                source_item_names(variables["social_capital"].get("source_items", [])),
            ),
            "construction": "standardized_mean_index",
            "rationale": "社会资本先按信任、邻里交往、朋友交往和休闲社交构成综合指数，适合先形成可检验的主结果；后续仍要人工确认是否拆成多维度报告。",
        },
        "controls": variables.get("controls", []),
        "control_rationale": {
            "female": "控制性别差异。",
            "age": "控制生命周期差异。",
            "education_level": "控制人力资本和社会经济地位差异。",
            "log_income": "控制收入水平差异。",
            "health": "控制健康对幸福感的直接影响。",
            "urban_hukou": "控制城乡户籍差异。",
            "province fixed effects": "控制省份层面的地区差异。",
        },
        "control_source_candidates": control_source_candidates(candidate_roles.get("controls", [])),
    }
    base.update(
        {
            "status": "needs_human_role_review",
            "blocking_reasons": [],
            "dataset": evidence_package.get("dataset", {}),
            "proposed_roles": proposed_roles,
            "result_evidence": {
                "primary_result": evidence_package.get("primary_result", {}),
                "evidence_consistency": evidence_package.get("evidence_consistency", {}),
                "writing_inputs": evidence_package.get("writing_inputs", {}),
            },
            "review_gates": [
                "outcome_measurement",
                "social_capital_index_construction",
                "control_variable_set",
                "ordered_model_interpretation",
                "literature_support_for_mechanism",
            ],
            "review_decisions": {
                "outcome": empty_review_decision(),
                "treatment": empty_review_decision(),
                "controls": empty_review_decision(),
                "model_evidence": empty_review_decision(),
            },
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_variable_roles",
                "would_write_if_approved": "state/product/variable_roles.json",
            },
            "next_tasks": [
                "human_review_cgss_variable_role_draft",
                "promote_cgss_variable_roles_after_approval",
                "build_cgss_literature_review_seed",
            ],
        }
    )
    return base


def blocking_reasons_for(evidence_package: dict[str, Any], variable_candidates: dict[str, Any]) -> list[str]:
    reasons = []
    if evidence_package.get("status") != "ready_for_paper_draft_input":
        reasons.append("evidence_package_not_ready")
    if "variables" not in evidence_package:
        reasons.append("missing_evidence_variables")
    if variable_candidates.get("status") != "needs_human_review":
        reasons.append("variable_candidates_not_reviewable")
    if "role_candidates" not in variable_candidates:
        reasons.append("missing_role_candidates")
    return reasons


def parse_source_variable(value: str) -> str:
    if "<-" in value:
        return value.split("<-", 1)[1].strip()
    return value.strip()


def source_item_names(source_items: list[str]) -> list[str]:
    return [item.split(" ", 1)[0].strip() for item in source_items]


def label_for(candidates: list[dict[str, Any]], name: str) -> str:
    for candidate in candidates:
        if candidate.get("name") == name:
            return candidate.get("label", "")
    return ""


def source_labels_for(candidates: list[dict[str, Any]], names: list[str]) -> dict[str, str]:
    return {name: label_for(candidates, name) for name in names}


def control_source_candidates(candidates: list[dict[str, Any]]) -> dict[str, list[str]]:
    mapping = {
        "female": ["a2"],
        "age": ["a3a", "birth"],
        "education_level": ["a7a", "a7b"],
        "log_income": ["a62", "income"],
        "health": ["a15"],
        "urban_hukou": ["a18", "a21"],
        "province fixed effects": ["province", "s41"],
    }
    available = {candidate.get("name") for candidate in candidates}
    return {role: [name for name in names if name in available] for role, names in mapping.items()}


def empty_review_decision() -> dict[str, Any]:
    return {
        "decision": "pending",
        "allowed_values": ["approve", "revise", "reject"],
        "reviewer_notes": "",
        "open_questions": [],
    }


def write_review_draft_outputs(
    project_root: Path, draft: dict[str, Any], result_path: Path, review_path: Path
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
        "# CGSS 变量角色审阅草案",
        "",
        f"- 题目：{draft.get('topic', '')}",
        f"- 状态：{draft['status']}",
        "- 正式变量角色写回：否",
    ]
    if draft["blocking_reasons"]:
        lines.extend(["", "## 阻断原因"])
        for reason in draft["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines) + "\n"

    outcome = draft["proposed_roles"]["outcome"]
    treatment = draft["proposed_roles"]["treatment"]
    lines.extend(
        [
            "",
            "## 因变量",
            f"- `{outcome['canonical_name']}` <- `{outcome['source_variable']}`",
            f"- 题项：{outcome['source_label']}",
            f"- 有序等级：{', '.join(str(level) for level in outcome.get('ordered_levels', []))}",
            f"- 理由：{outcome['rationale']}",
            "",
            "## 核心解释变量",
            f"- `{treatment['canonical_name']}`",
            f"- 来源题项：{', '.join(f'`{item}`' for item in treatment['source_items'])}",
            f"- 构造：`{treatment['construction']}`",
            f"- 理由：{treatment['rationale']}",
            "",
            "## 控制变量",
        ]
    )
    for control in draft["proposed_roles"]["controls"]:
        rationale = draft["proposed_roles"]["control_rationale"].get(control, "待人工确认。")
        sources = draft["proposed_roles"].get("control_source_candidates", {}).get(control, [])
        suffix = f" 原始候选：{', '.join(f'`{source}`' for source in sources)}。" if sources else ""
        lines.append(f"- `{control}`：{rationale}{suffix}")
    lines.extend(["", "## 模型证据"])
    primary_result = draft.get("result_evidence", {}).get("primary_result", {})
    for model_name in ["ols", "ordered_logit"]:
        result = primary_result.get(model_name, {})
        if result:
            lines.append(
                f"- `{model_name}`：`{result.get('variable', '')}` 系数 {result.get('coef', ''):.4f}，"
                f"标准误 {result.get('std_error', ''):.4f}，p 值 {result.get('p_value', ''):.3g}，"
                f"样本量 {result.get('nobs', '')}。"
            )
    consistency = draft.get("result_evidence", {}).get("evidence_consistency", {})
    if consistency:
        lines.append(
            "- 一致性检查："
            f"样本量一致={consistency.get('sample_nobs_match')}；"
            f"有序模型门禁={consistency.get('ordered_method_gate')}；"
            f"方向={consistency.get('social_capital_direction')}。"
        )
    lines.extend(["", "## 审阅门禁"])
    for gate in draft["review_gates"]:
        lines.append(f"- `{gate}`")
    lines.extend(
        [
            "",
            "## 人工审阅决定",
            "- 因变量：pending",
            "- 核心解释变量：pending",
            "- 控制变量：pending",
            "- 模型证据：pending",
        ]
    )
    return "\n".join(lines) + "\n"

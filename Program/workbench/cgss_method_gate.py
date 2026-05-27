from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_method_gate.v1"
DEFAULT_EVIDENCE_PACKAGE_PATH = Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json")
DEFAULT_LITERATURE_PACKET_PATH = Path("Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json")
DEFAULT_PAPER_ASSEMBLY_PATH = Path("Results/json/cgss_social_capital_happiness_paper_assembly.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_method_gate.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_method_gate.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_method_gate(
    evidence_package: dict[str, Any],
    literature_packet: dict[str, Any],
    paper_assembly: dict[str, Any],
    *,
    profile: str = "working_paper",
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": evidence_package.get("topic") or paper_assembly.get("topic", ""),
        "profile": profile,
        "method_family": "cross_section_ols_ordered_logit",
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_artifacts": {
            "results_evidence_package": {
                "path": source_paths.get("evidence_package", str(DEFAULT_EVIDENCE_PACKAGE_PATH)),
                "schema_version": evidence_package.get("schema_version", ""),
                "status": evidence_package.get("status", ""),
            },
            "literature_review_draft_packet": {
                "path": source_paths.get("literature_packet", str(DEFAULT_LITERATURE_PACKET_PATH)),
                "schema_version": literature_packet.get("schema_version", ""),
                "status": literature_packet.get("status", ""),
            },
            "paper_assembly": {
                "path": source_paths.get("paper_assembly", str(DEFAULT_PAPER_ASSEMBLY_PATH)),
                "schema_version": paper_assembly.get("schema_version", ""),
                "status": paper_assembly.get("status", ""),
            },
        },
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_verified_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
        },
    }
    blocking_reasons = input_blocking_reasons(evidence_package, literature_packet, paper_assembly)
    if blocking_reasons:
        return {
            **base,
            "status": "blocked_missing_method_gate_inputs",
            "blocking_reasons": blocking_reasons,
            "gate_status": "blocked",
            "gate_enforcement": {
                "required": False,
                "mode": "blocked",
                "profile": profile,
                "recommended_profiles": ["aer_like"],
            },
            "checks": [],
            "required_evidence": [],
            "risk_register": [],
            "result_number_bindings": {},
            "evidence_rules": ["do_not_invent_numbers", "draft_layer_only"],
            "next_tasks": ["repair_method_gate_inputs"],
        }

    checks = build_checks(evidence_package, literature_packet, paper_assembly)
    gate_required = profile == "aer_like"
    return {
        **base,
        "status": "needs_human_method_gate_review" if gate_required else "method_gate_suggested_needs_human_review",
        "blocking_reasons": [],
        "gate_status": "yellow",
        "gate_enforcement": {
            "required": gate_required,
            "mode": "required" if gate_required else "suggested",
            "profile": profile,
            "recommended_profiles": ["aer_like"],
            "requires_user_choice_for_enforcement": not gate_required,
        },
        "checks": checks,
        "required_evidence": required_evidence(),
        "risk_register": ["reverse_causality", "omitted_variables"],
        "result_number_bindings": result_number_bindings(evidence_package),
        "evidence_rules": [
            "do_not_invent_numbers",
            "all_result_numbers_must_bind_to_results_evidence_package",
            "candidate_citations_require_human_verification",
            "draft_layer_only",
        ],
        "promotion": {
            "allowed": False,
            "required_decision": "human_approve_cgss_method_gate",
            "would_write_if_approved": [
                "Manuscripts/sections/empirical-strategy.md",
                "Manuscripts/sections/robustness-mechanisms-heterogeneity.md",
            ],
        },
        "agent_team_schedule": {
            "call_when": "after_exploratory_paper_and_pdf_preflight",
            "called_agents": ["MethodAgent", "ReviewerAgent", "VerifierAgent"],
            "recall_when": "after_method_gate_json_and_review_are_written",
            "next_call_when": "before_reviewer_report_and_revision_queue",
            "boundary": "方法门只产出审阅层缺口和风险，不提升正式论文层。",
        },
        "next_tasks": [
            "human_review_cgss_method_gate",
            "add_variable_definition_detail",
            "plan_robustness_heterogeneity_mechanism_tests",
            "address_endogeneity_risk_in_reviewer_loop",
        ],
    }


def input_blocking_reasons(
    evidence_package: dict[str, Any],
    literature_packet: dict[str, Any],
    paper_assembly: dict[str, Any],
) -> list[str]:
    reasons = []
    if evidence_package.get("status") != "ready_for_paper_draft_input":
        reasons.append("results_evidence_package_not_ready")
    if literature_packet.get("status") != "needs_human_literature_review_draft_approval":
        reasons.append("literature_review_packet_not_reviewable")
    if paper_assembly.get("status") != "needs_human_exploratory_paper_review":
        reasons.append("exploratory_paper_not_review_ready")
    return reasons


def build_checks(
    evidence_package: dict[str, Any],
    literature_packet: dict[str, Any],
    paper_assembly: dict[str, Any],
) -> list[dict[str, Any]]:
    variables = evidence_package.get("variables", {})
    controls = variables.get("controls", [])
    section_ids = {section.get("section_id") for section in paper_assembly.get("assembled_sections", [])}
    return [
        {
            "id": "variable_definitions",
            "label": "变量定义是否充分",
            "status": "passed" if variables.get("outcome") and variables.get("social_capital") else "needs_followup",
            "evidence": [
                variables.get("outcome", ""),
                f"social_capital_items={variables.get('social_capital', {}).get('source_items', [])}",
            ],
            "review_note": "正式稿仍需把题项方向、量表含义和缺失处理写入变量表。",
        },
        {
            "id": "ordered_outcome_model_fit",
            "label": "主观幸福感因变量是否适合 OLS + Ordered Logit",
            "status": "passed" if evidence_package.get("evidence_consistency", {}).get("ordered_method_gate") == "passed" else "needs_followup",
            "evidence": ["OLS baseline", "Ordered Logit ordered outcome robustness"],
            "review_note": "OLS 可作可解释基准，Ordered Logit 用于有序因变量稳健性。",
        },
        {
            "id": "social_capital_theory_literature",
            "label": "社会资本核心解释变量是否有理论和文献依据",
            "status": "needs_human_verification",
            "evidence": extract_literature_evidence(literature_packet),
            "review_note": "候选引用存在，但正式 bibliography 和中文文献仍需人工核验。",
        },
        {
            "id": "baseline_controls",
            "label": "控制变量是否覆盖基本人口学和经济变量",
            "status": "passed" if has_baseline_controls(controls) else "needs_followup",
            "evidence": controls,
            "review_note": "已覆盖性别、年龄、教育、收入、健康和户籍；可继续补地区与家庭结构。",
        },
        {
            "id": "robustness_heterogeneity_mechanism_plan",
            "label": "是否需要进一步稳健性、异质性、机制检验",
            "status": "needs_followup",
            "evidence": sorted(section_ids),
            "review_note": "当前完整稿已有计划段落，但尚未真实执行分项指数、异质性和机制检验。",
        },
        {
            "id": "reverse_causality_and_omitted_variable_risk",
            "label": "是否存在反向因果和遗漏变量风险",
            "status": "risk_flagged",
            "evidence": ["cross_section_data", "conditional_association_claim_boundary"],
            "review_note": "横截面结果只能支持条件相关；幸福感也可能影响社会参与，遗漏人格、社区质量等变量。",
        },
    ]


def has_baseline_controls(controls: list[str]) -> bool:
    control_text = " ".join(controls)
    required_groups = [
        ["female", "gender", "sex"],
        ["age"],
        ["education", "edu"],
        ["income"],
        ["health"],
        ["hukou", "urban"],
    ]
    return all(any(token in control_text for token in group) for group in required_groups)


def extract_literature_evidence(literature_packet: dict[str, Any]) -> list[str]:
    keys = []
    for block in literature_packet.get("paragraph_blocks", []):
        keys.extend(block.get("citation_keys", []))
    if not keys:
        keys.extend(literature_packet.get("candidate_citations", []))
    if literature_packet.get("open_dependencies"):
        keys.append("manual_source_verification_required")
    return sorted(set(keys))


def required_evidence() -> list[dict[str, Any]]:
    return [
        {"id": "variable_codebook", "status": "required_for_formal_promotion"},
        {"id": "ols_ordered_logit_model_outputs", "status": "present_in_results_evidence_package"},
        {"id": "candidate_citation_verification", "status": "required_for_formal_promotion"},
        {"id": "robustness_plan_or_results", "status": "required_for_next_revision"},
        {"id": "endogeneity_risk_statement", "status": "required_for_next_revision"},
    ]


def result_number_bindings(evidence_package: dict[str, Any]) -> dict[str, Any]:
    primary = evidence_package.get("primary_result", {})
    ols = primary.get("ols", {})
    ordered = primary.get("ordered_logit", {})
    return {
        "source": "cgss_results_evidence_package",
        "ols": {
            "coef": round(float(ols.get("coef", 0)), 4),
            "std_error": round(float(ols.get("std_error", 0)), 4),
            "p_value": float(ols.get("p_value", 0)),
            "nobs": int(ols.get("nobs", 0)),
        },
        "ordered_logit": {
            "coef": round(float(ordered.get("coef", 0)), 4),
            "std_error": round(float(ordered.get("std_error", 0)), 4),
            "p_value": float(ordered.get("p_value", 0)),
            "nobs": int(ordered.get("nobs", 0)),
        },
    }


def write_cgss_method_gate_outputs(
    project_root: Path,
    gate: dict[str, Any],
    result_path: Path = DEFAULT_RESULT_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(gate, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(gate), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(gate: dict[str, Any]) -> str:
    lines = [
        "# CGSS AER-like 方法规范门",
        "",
        f"- 题目：{gate.get('topic', '')}",
        f"- 状态：`{gate.get('status')}`",
        f"- profile：`{gate.get('profile')}`",
        f"- gate_status：`{gate.get('gate_status')}`",
        f"- 强制启用：`{str(gate.get('gate_enforcement', {}).get('required', False)).lower()}`",
        f"- 正式层写回：`{str(gate.get('formal_writeback_allowed', False)).lower()}`",
    ]
    if gate.get("blocking_reasons"):
        lines.extend(["", "## 阻断原因"])
        for reason in gate["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(["", "## 方法检查"])
    for check in gate.get("checks", []):
        lines.append(f"- `{check['id']}`：{check['label']} -> `{check['status']}`")
        lines.append(f"  - 审阅说明：{check['review_note']}")

    lines.extend(["", "## 结果数字绑定"])
    numbers = gate.get("result_number_bindings", {})
    lines.append(f"- 来源：`{numbers.get('source')}`")
    lines.append(f"- OLS：coef={numbers.get('ols', {}).get('coef')}，n={numbers.get('ols', {}).get('nobs')}")
    lines.append(
        f"- Ordered Logit：coef={numbers.get('ordered_logit', {}).get('coef')}，n={numbers.get('ordered_logit', {}).get('nobs')}"
    )

    lines.extend(["", "## 风险登记"])
    risk_labels = {
        "reverse_causality": "反向因果",
        "omitted_variables": "遗漏变量",
    }
    for risk in gate.get("risk_register", []):
        lines.append(f"- `{risk}`：{risk_labels.get(risk, risk)}")

    lines.extend(["", "## 下一步"])
    for task in gate.get("next_tasks", []):
        lines.append(f"- `{task}`")
    return "\n".join(lines).rstrip() + "\n"

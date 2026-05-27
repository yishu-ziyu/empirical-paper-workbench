from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.paper_quality import REQUIRED_SECTIONS, SECTION_LENGTH_STANDARDS


SCHEMA_VERSION = "p6.cgss_method_structure_gate_packet.v1"
DEFAULT_EVIDENCE_PACKAGE_PATH = Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json")
DEFAULT_LITERATURE_PACKET_PATH = Path("Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_method_structure_gate_packet.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_method_structure_gate_packet.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_method_structure_gate_packet(
    evidence_package: dict[str, Any],
    literature_packet: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": evidence_package.get("topic", ""),
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
        },
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "wrote_state_product": False,
        },
    }
    blocking_reasons = input_blocking_reasons(evidence_package, literature_packet)
    if blocking_reasons:
        base.update(
            {
                "status": "blocked_missing_method_or_literature_inputs",
                "blocking_reasons": blocking_reasons,
                "paper_length_standard": {},
                "section_standards": {},
                "method_claim_gates": {},
                "promotion": {"allowed": False, "required_decision": "repair_method_or_literature_inputs"},
                "next_tasks": ["repair_results_evidence_or_literature_packet"],
            }
        )
        return base

    main_result = extract_main_result(evidence_package)
    base.update(
        {
            "status": "needs_human_method_structure_approval",
            "blocking_reasons": ["method_structure_gate_needs_human_approval"],
            "paper_length_standard": build_paper_length_standard(),
            "section_standards": build_section_standards(),
            "method_claim_gates": build_method_claim_gates(main_result),
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_method_structure_gate",
                "would_write_if_approved": [
                    "Results/json/cgss_social_capital_happiness_design_spec_review.json",
                    "Manuscripts/sections/empirical-strategy.md",
                    "Manuscripts/sections/main-results.md",
                ],
            },
            "next_tasks": [
                "human_review_method_structure_gate",
                "decide_primary_model_ols_or_ordered_logit",
                "draft_empirical_strategy_after_approval",
                "draft_main_results_after_approval",
            ],
        }
    )
    return base


def input_blocking_reasons(evidence_package: dict[str, Any], literature_packet: dict[str, Any]) -> list[str]:
    reasons = []
    if evidence_package.get("status") != "ready_for_paper_draft_input":
        reasons.append("results_evidence_package_not_ready")
    if literature_packet.get("status") != "needs_human_literature_review_draft_approval":
        reasons.append("literature_review_draft_packet_not_ready")
    if not literature_packet.get("paragraph_blocks"):
        reasons.append("literature_review_paragraph_blocks_missing")
    return reasons


def extract_main_result(evidence_package: dict[str, Any]) -> dict[str, Any]:
    primary = evidence_package.get("primary_result") or {}
    if primary:
        ols = primary["ols"]
        ordered = primary["ordered_logit"]
        return {
            "nobs": int(ols["nobs"]),
            "ols_coef": round(float(ols["coef"]), 4),
            "ols_se": round(float(ols["std_error"]), 4),
            "ols_p_value": float(ols["p_value"]),
            "ordered_logit_coef": round(float(ordered["coef"]), 4),
            "ordered_logit_se": round(float(ordered["std_error"]), 4),
            "ordered_logit_p_value": float(ordered["p_value"]),
            "outcome_levels": ordered.get("outcome_levels", []),
            "claim_boundary": "positive_conditional_association",
        }
    by_model = {item["model"]: item for item in evidence_package.get("main_results", [])}
    ols = by_model["OLS"]
    ordered = by_model["Ordered Logit"]
    return {
        "nobs": int(ols["nobs"]),
        "ols_coef": round(float(ols["coef"]), 4),
        "ols_se": round(float(ols["se"]), 4),
        "ols_p_value": float(ols["p_value"]),
        "ordered_logit_coef": round(float(ordered["coef"]), 4),
        "ordered_logit_se": round(float(ordered["se"]), 4),
        "ordered_logit_p_value": float(ordered["p_value"]),
        "outcome_levels": [1, 2, 3, 4, 5],
        "claim_boundary": "positive_conditional_association",
    }


def build_paper_length_standard() -> dict[str, Any]:
    return {
        "profile": "chinese_empirical_paper_package",
        "total_target_chinese_chars": 22000,
        "total_minimum_chinese_chars": 16000,
        "total_maximum_chinese_chars": 32000,
        "required_sections": REQUIRED_SECTIONS,
        "writing_rule": "先按 section 写足证据、变量、方法和结果，再由审稿式修订循环压缩重复内容。",
    }


def build_section_standards() -> dict[str, dict[str, Any]]:
    standards = {}
    for section in REQUIRED_SECTIONS:
        length = SECTION_LENGTH_STANDARDS.get(section, {})
        standards[section] = {
            "min_chinese_chars": length.get("min_chinese_chars"),
            "max_chinese_chars": length.get("max_chinese_chars"),
            "required_evidence": section_required_evidence(section),
        }
    return standards


def section_required_evidence(section: str) -> list[str]:
    mapping = {
        "Literature and Contribution": ["verified_bibliography_candidates", "citation_bindings", "contribution_position"],
        "Data and Measurement": ["CGSS2023_path", "variable_role_review_draft", "sample_construction"],
        "Empirical Strategy": ["model_formula", "claim_boundary", "method_gate"],
        "Main Results": ["OLS_result", "Ordered_Logit_result", "main_table"],
        "Robustness / Mechanisms / Heterogeneity": ["ordered_outcome_robustness", "future_robustness_matrix"],
        "References": ["human_approved_verified_bibliography"],
    }
    return mapping.get(section, ["section_specific_evidence"])


def build_method_claim_gates(main_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "main_result_gate": main_result,
        "supported_claims": [
            {
                "claim_type": "conditional_association",
                "allowed_wording": "社会资本指数与居民主观幸福感呈正向相关。",
                "evidence": ["OLS", "controls", "province_fixed_effects"],
            },
            {
                "claim_type": "ordered_outcome_robustness",
                "allowed_wording": "在有序响应模型下，正向关系保持稳定。",
                "evidence": ["Ordered Logit", "five_ordered_happiness_levels"],
            },
        ],
        "blocked_method_families": [
            {"method": "DID", "reason": "当前没有政策冲击、处理组、对照组和处理时间。"},
            {"method": "IV", "reason": "当前没有通过相关性与排除性讨论的工具变量。"},
            {"method": "RDD", "reason": "当前没有明确断点、运行变量和带宽诊断。"},
            {"method": "PSM", "reason": "当前没有已定义处理状态和匹配前平衡诊断。"},
            {"method": "DML", "reason": "当前没有因果处理设定、交叉拟合计划和 nuisance 模型诊断。"},
        ],
        "human_decisions": [
            "OLS 作为主模型还是 Ordered Logit 作为主模型",
            "是否把社会资本指数拆成信任、交往、参与三个分维度",
            "是否补充跨年份 CGSS 或其他稳健性数据",
        ],
    }


def write_method_structure_gate_packet_outputs(
    project_root: Path,
    packet: dict[str, Any],
    result_path: Path,
    review_path: Path,
) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(packet), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(packet: dict[str, Any]) -> str:
    lines = [
        "# CGSS 方法规范与论文结构门禁",
        "",
        f"- 题目：{packet.get('topic', '')}",
        f"- 状态：`{packet['status']}`",
        "- 写入正式论文：否",
        "- 写入 DesignSpec / RunPlan：否",
    ]
    if packet["blocking_reasons"]:
        lines.extend(["", "## 当前需要处理"])
        for reason in packet["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if packet["status"].startswith("blocked"):
        return "\n".join(lines) + "\n"

    length = packet["paper_length_standard"]
    lines.extend(
        [
            "",
            "## 论文长度标准",
            f"- 目标总长度：{length['total_target_chinese_chars']} 中文字符左右",
            f"- 最低总长度：{length['total_minimum_chinese_chars']} 中文字符",
            f"- 建议上限：{length['total_maximum_chinese_chars']} 中文字符",
            f"- 写作规则：{length['writing_rule']}",
            "",
            "## 方法门禁",
        ]
    )
    main = packet["method_claim_gates"]["main_result_gate"]
    lines.extend(
        [
            f"- 样本量：{main['nobs']}",
            f"- OLS：系数 {main['ols_coef']}，稳健标准误 {main['ols_se']}",
            f"- Ordered Logit：系数 {main['ordered_logit_coef']}，标准误 {main['ordered_logit_se']}",
            f"- 当前主结论边界：`{main['claim_boundary']}`",
            "",
            "### 当前可以写的说法",
        ]
    )
    for item in packet["method_claim_gates"]["supported_claims"]:
        lines.append(f"- `{item['claim_type']}`：{item['allowed_wording']}")
    lines.extend(["", "### 当前暂不进入的计量方法"])
    for item in packet["method_claim_gates"]["blocked_method_families"]:
        lines.append(f"- {item['method']}：{item['reason']}")
    lines.extend(["", "## 章节长度和证据要求"])
    for section, standard in packet["section_standards"].items():
        min_chars = standard.get("min_chinese_chars")
        max_chars = standard.get("max_chinese_chars")
        length_text = f"{min_chars}-{max_chars} 中文字符" if min_chars and max_chars else "按内容需要"
        lines.append(f"- {section}：{length_text}；证据：{', '.join(standard['required_evidence'])}")
    lines.extend(["", "## 人工批准后才会写入"])
    for path in packet["promotion"]["would_write_if_approved"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## 下一步"])
    for task in packet["next_tasks"]:
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"

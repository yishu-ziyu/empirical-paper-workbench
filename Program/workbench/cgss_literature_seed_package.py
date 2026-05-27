from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_literature_seed_package.v1"
DEFAULT_ROLE_REVIEW_DRAFT_PATH = Path("Results/json/cgss_social_capital_happiness_variable_role_review_draft.json")
DEFAULT_EVIDENCE_PACKAGE_PATH = Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_literature_seed_package.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_literature_seed_package.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_literature_seed_package(
    role_review_draft: dict[str, Any],
    evidence_package: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    topic = role_review_draft.get("topic") or evidence_package.get("topic") or ""
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "source_artifacts": {
            "variable_role_review_draft": {
                "path": source_paths.get("variable_role_review_draft", str(DEFAULT_ROLE_REVIEW_DRAFT_PATH)),
                "schema_version": role_review_draft.get("schema_version", ""),
                "status": role_review_draft.get("status", ""),
            },
            "results_evidence_package": {
                "path": source_paths.get("evidence_package", str(DEFAULT_EVIDENCE_PACKAGE_PATH)),
                "schema_version": evidence_package.get("schema_version", ""),
                "status": evidence_package.get("status", ""),
            },
        },
        "boundary_flags": {
            "modified_formal_bibliography": False,
            "modified_formal_manuscript": False,
            "modified_formal_variable_roles": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "wrote_state_product": False,
        },
    }
    blocking_reasons = blocking_reasons_for(role_review_draft, evidence_package)
    if blocking_reasons:
        base.update(
            {
                "status": "blocked_missing_variable_role_review",
                "blocking_reasons": blocking_reasons,
                "coverage": [],
                "seed_sources": [],
                "variable_support": {},
                "mechanism_map": {},
                "method_support": {},
                "cnki_manual_queue": [],
                "promotion": {"allowed": False, "required_decision": "repair_literature_seed_inputs"},
            }
        )
        return base

    proposed_roles = role_review_draft["proposed_roles"]
    base.update(
        {
            "status": "needs_human_literature_review",
            "blocking_reasons": [],
            "coverage": [
                "social_capital_theory",
                "subjective_wellbeing_measurement",
                "cgss_empirical_context",
                "ordinal_outcome_method",
                "chinese_literature_queue",
            ],
            "seed_sources": seed_sources(),
            "variable_support": variable_support(proposed_roles),
            "mechanism_map": mechanism_map(proposed_roles),
            "method_support": method_support(evidence_package),
            "cnki_manual_queue": cnki_manual_queue(),
            "zotero_scholar_queue": zotero_scholar_queue(),
            "review_questions": [
                "CGSS2023 是否作为主样本，还是需要追加 CGSS2018/2021 做稳健性？",
                "社会资本指数是否保留综合指数，还是拆成社会信任、社会交往、参与网络三个分维度？",
                "中文文献是否足以支撑 CGSS 场景，哪些条目需要 CNKI 原文核验？",
                "Ordered Logit 是否作为主模型，OLS 是否只作为可读性稳健性？",
            ],
            "promotion": {
                "allowed": False,
                "required_decision": "human_review_literature_seed_package",
                "would_write_if_approved": [
                    "Data/literature/processed/candidate_literature.csv",
                    "Data/literature/processed/verified_bibliography.csv",
                    "Data/literature/processed/contribution_matrix.md",
                ],
            },
            "next_tasks": [
                "run_cnki_manual_search",
                "verify_scholar_zotero_sources",
                "bind_literature_to_variable_roles",
                "draft_literature_review_section",
            ],
        }
    )
    return base


def blocking_reasons_for(role_review_draft: dict[str, Any], evidence_package: dict[str, Any]) -> list[str]:
    reasons = []
    if role_review_draft.get("status") != "needs_human_role_review":
        reasons.append("variable_role_review_not_ready")
    if "proposed_roles" not in role_review_draft:
        reasons.append("missing_proposed_roles")
    if evidence_package.get("status") != "ready_for_paper_draft_input":
        reasons.append("evidence_package_not_ready")
    return reasons


def seed_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "S01",
            "source_type": "official_data",
            "title": "CGSS 项目概况",
            "authors": ["中国人民大学中国调查与数据中心"],
            "year": "",
            "url": "https://cgss.ruc.edu.cn/xmjs/xmgk.htm",
            "evidence_role": ["cgss_empirical_context", "data_source_description"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "说明 CGSS 的项目来源、全国综合社会调查定位和数据使用边界。",
            "do_not_claim": "不能仅凭数据来源说明把本文结果写成严格因果效应。",
        },
        {
            "id": "S02",
            "source_type": "classic_theory",
            "title": "Social Capital in the Creation of Human Capital",
            "authors": ["James S. Coleman"],
            "year": "1988",
            "url": "https://www.journals.uchicago.edu/doi/10.1086/228943",
            "evidence_role": ["social_capital_theory", "mechanism"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "支撑社会资本通过义务、期望、信息渠道和社会规范影响个体福利的理论机制。",
            "do_not_claim": "不能直接证明 CGSS 中某个题项就是完整社会资本。",
        },
        {
            "id": "S03",
            "source_type": "classic_theory",
            "title": "Bowling Alone: The Collapse and Revival of American Community",
            "authors": ["Robert D. Putnam"],
            "year": "2000",
            "url": "https://www.simonandschuster.com/books/Bowling-Alone-Revised-and-Updated/Robert-D-Putnam/9781982130848",
            "evidence_role": ["social_capital_theory", "trust_norms_networks"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "用于组织信任、规范和网络三类社会资本维度。",
            "do_not_claim": "不能把美国社区衰退叙事直接套用到中国居民幸福感。",
        },
        {
            "id": "S04",
            "source_type": "classic_theory",
            "title": "The Forms of Capital",
            "authors": ["Pierre Bourdieu"],
            "year": "1986",
            "url": "https://web.stanford.edu/~eckert/PDF/Bourdieu1986.pdf",
            "evidence_role": ["social_capital_theory", "resource_network"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "补充社会资本作为可动员关系资源的解释。",
            "do_not_claim": "不能把阶层再生产理论直接写成本文实证结论。",
        },
        {
            "id": "S05",
            "source_type": "measurement_standard",
            "title": "Subjective Well-Being",
            "authors": ["Ed Diener"],
            "year": "1984",
            "url": "https://doi.org/10.1037/0033-2909.95.3.542",
            "evidence_role": ["subjective_wellbeing_measurement"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "界定主观幸福感和生活评价的概念边界。",
            "do_not_claim": "CGSS 单题幸福感只是代理变量，不能覆盖多维 SWB。",
        },
        {
            "id": "S06",
            "source_type": "measurement_standard",
            "title": "OECD Guidelines on Measuring Subjective Well-being",
            "authors": ["OECD"],
            "year": "2025",
            "url": "https://www.oecd.org/en/publications/oecd-guidelines-on-measuring-subjective-well-being-2025-update_9203632a-en/full-report/measuring-subjective-well-being_b4b53f27.html",
            "evidence_role": ["subjective_wellbeing_measurement", "measurement_limits"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "说明主观幸福感测量应区分生活评价、情感体验和其他福利指标。",
            "do_not_claim": "不能把幸福感自评当作客观福利水平。",
        },
        {
            "id": "S07",
            "source_type": "measurement_standard",
            "title": "Measuring Social Capital: An Integrated Questionnaire",
            "authors": ["World Bank"],
            "year": "2004",
            "url": "https://openknowledge.worldbank.org/entities/publication/634c867c-cbc8-536a-8446-a2703177bc7c",
            "evidence_role": ["social_capital_measurement", "variable_operationalization"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "为信任、网络、集体行动、信息沟通等社会资本维度提供测量参照。",
            "do_not_claim": "CGSS 不是完整 SC-IQ，不能声称完全复刻该量表。",
        },
        {
            "id": "S08",
            "source_type": "cgss_empirical_study",
            "title": "Social trust, social capital, and subjective well-being of rural residents",
            "authors": ["Xu", "Zhang", "Huang"],
            "year": "2023",
            "url": "https://www.nature.com/articles/s41599-023-01532-1",
            "evidence_role": ["cgss_empirical_context", "mechanism", "variable_operationalization"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "提供 CGSS 语境下社会信任、社会资本与主观幸福感的实证参照。",
            "do_not_claim": "该文样本和波次不同，不能直接外推到本文 CGSS2023 全样本。",
        },
        {
            "id": "S09",
            "source_type": "chinese_literature_seed",
            "title": "机会不均等、社会资本与农民主观幸福感",
            "authors": ["张彤进", "万广华"],
            "year": "2020",
            "url": "https://qks.shufe.edu.cn/J/ArticleQuery/f824063e-2826-4256-90f5-e5ff8aa79e7a/CN",
            "evidence_role": ["cnki_manual_queue", "chinese_empirical_context"],
            "review_status": "cnki_or_journal_page_needs_manual_verification",
            "use_in_paper": "作为中文 CGSS 幸福感研究和社会资本机制的候选中文文献。",
            "do_not_claim": "其农民样本和机会不均等框架不能直接替代本文居民样本框架。",
        },
        {
            "id": "S10",
            "source_type": "method_reference",
            "title": "How Important is Methodology for the estimates of the determinants of Happiness?",
            "authors": ["Ferrer-i-Carbonell", "Frijters"],
            "year": "2004",
            "url": "https://doi.org/10.1111/j.1468-0297.2004.00235.x",
            "evidence_role": ["ordinal_outcome_method", "subjective_wellbeing_method"],
            "review_status": "seed_needs_human_verification",
            "use_in_paper": "支撑幸福感有序变量建模和 OLS/有序模型稳健性讨论。",
            "do_not_claim": "方法选择仍需结合 CGSS 量表和本文诊断结果说明。",
        },
    ]


def variable_support(proposed_roles: dict[str, Any]) -> dict[str, Any]:
    outcome = proposed_roles["outcome"]
    treatment = proposed_roles["treatment"]
    return {
        "outcome": {
            "canonical_name": outcome.get("canonical_name"),
            "source_variables": [outcome.get("source_variable")],
            "concept": "subjective_wellbeing",
            "literature_needs": ["Diener 1984", "OECD SWB Guidelines", "CGSS questionnaire/codebook verification"],
            "measurement_warning": "CGSS a36 是单题总体幸福感代理变量。",
        },
        "treatment": {
            "canonical_name": treatment.get("canonical_name"),
            "source_items": treatment.get("source_items", []),
            "concept": "social_capital",
            "literature_needs": ["Coleman 1988", "Putnam 2000", "Bourdieu 1986", "World Bank SC-IQ"],
            "measurement_warning": "综合指数需要人工确认维度权重和缺失值处理。",
        },
        "controls": {
            "items": proposed_roles.get("controls", []),
            "literature_needs": ["收入、健康、教育、年龄、性别、城乡户籍作为幸福感常见混杂因素的文献支持。"],
        },
    }


def mechanism_map(proposed_roles: dict[str, Any]) -> dict[str, Any]:
    treatment_items = proposed_roles.get("treatment", {}).get("source_items", [])
    return {
        "social_trust_mechanism": {
            "variables": [item for item in treatment_items if item == "a33"],
            "claim_seed": "社会信任降低互动不确定性，增强安全感和社会支持预期。",
            "required_sources": ["Coleman 1988", "Putnam 2000", "Xu et al. 2023"],
            "review_status": "needs_human_literature_review",
        },
        "social_participation_mechanism": {
            "variables": [item for item in treatment_items if item in {"a31a", "a31b", "a311"}],
            "claim_seed": "社会交往和参与网络可能通过情感支持、信息交换和资源获得影响幸福感。",
            "required_sources": ["Putnam 2000", "World Bank SC-IQ", "Chinese CGSS literature"],
            "review_status": "needs_human_literature_review",
        },
        "health_income_confounding": {
            "variables": ["health", "log_income", "education_level"],
            "claim_seed": "健康、收入和教育同时影响社会资本积累和幸福感评价，需要作为控制变量处理。",
            "required_sources": ["subjective well-being empirical literature"],
            "review_status": "needs_human_literature_review",
        },
    }


def method_support(evidence_package: dict[str, Any]) -> dict[str, Any]:
    primary_result = evidence_package.get("primary_result", {})
    return {
        "ordered_logit": {
            "why_needed": "CGSS a36 是 1-5 有序幸福感量表，Ordered Logit 应进入主模型或核心稳健性。",
            "current_evidence": primary_result.get("ordered_logit", {}),
            "required_literature": ["Ferrer-i-Carbonell and Frijters 2004", "ordinal outcome model reference"],
            "open_checks": ["报告边际效应", "检查比例优势假设或说明局限"],
        },
        "ols_baseline": {
            "why_needed": "OLS 便于解释系数方向和大小，可作为可读性基准。",
            "current_evidence": primary_result.get("ols", {}),
            "required_literature": ["subjective well-being methodology discussion"],
            "open_checks": ["说明有序变量被连续化处理的限制"],
        },
    }


def cnki_manual_queue() -> list[dict[str, str]]:
    return [
        {
            "query": "社会资本 主观幸福感 CGSS",
            "purpose": "确认中文核心文献中社会资本与幸福感的变量定义和常用控制变量。",
            "status": "manual_search_required",
        },
        {
            "query": "社会信任 居民幸福感 CGSS 有序Logit",
            "purpose": "核验 CGSS 幸福感题项、社会信任题项和有序 Logit 写法。",
            "status": "manual_search_required",
        },
        {
            "query": "社会参与 社会网络 主观幸福感 中国综合社会调查",
            "purpose": "补充分维度社会资本机制，避免只使用社会信任解释所有结果。",
            "status": "manual_search_required",
        },
    ]


def zotero_scholar_queue() -> list[dict[str, str]]:
    return [
        {"query": "Diener 1984 Subjective Well-Being", "target": "zotero_or_scholar", "status": "needs_lookup"},
        {"query": "Coleman 1988 Social Capital in the Creation of Human Capital", "target": "zotero_or_scholar", "status": "needs_lookup"},
        {"query": "Ferrer-i-Carbonell Frijters 2004 determinants of happiness methodology", "target": "zotero_or_scholar", "status": "needs_lookup"},
    ]


def write_literature_seed_outputs(
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
        "# CGSS 文献综述种子包",
        "",
        f"- 题目：{package.get('topic', '')}",
        f"- 状态：{package['status']}",
        "- 正式参考文献写回：否",
        "- 正式论文写回：否",
    ]
    if package["blocking_reasons"]:
        lines.extend(["", "## 阻断原因"])
        for reason in package["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines) + "\n"

    lines.extend(["", "## 覆盖范围"])
    for item in package["coverage"]:
        lines.append(f"- `{item}`")

    lines.extend(["", "## 种子文献"])
    for source in package["seed_sources"]:
        roles = ", ".join(f"`{role}`" for role in source["evidence_role"])
        lines.extend(
            [
                f"### {source['id']} {source['title']}",
                f"- 类型：`{source['source_type']}`",
                f"- 作者/机构：{', '.join(source['authors'])}",
                f"- 年份：{source['year']}",
                f"- 链接：{source['url']}",
                f"- 证据角色：{roles}",
                f"- 可用于：{source['use_in_paper']}",
                f"- 不应直接写成：{source['do_not_claim']}",
                "",
            ]
        )

    lines.extend(["## 变量支持"])
    outcome = package["variable_support"]["outcome"]
    treatment = package["variable_support"]["treatment"]
    controls = package["variable_support"]["controls"]
    lines.extend(
        [
            f"- 因变量 `{outcome['canonical_name']}`：{', '.join(f'`{item}`' for item in outcome['source_variables'])}；{outcome['measurement_warning']}",
            f"- 核心解释变量 `{treatment['canonical_name']}`：{', '.join(f'`{item}`' for item in treatment['source_items'])}；{treatment['measurement_warning']}",
            f"- 控制变量：{', '.join(f'`{item}`' for item in controls['items'])}",
            "",
            "## 机制地图",
        ]
    )
    for key, mechanism in package["mechanism_map"].items():
        lines.append(f"- `{key}`：{mechanism['claim_seed']} 需要来源：{', '.join(mechanism['required_sources'])}。")

    lines.extend(["", "## 方法支持"])
    for method_name, method in package["method_support"].items():
        lines.append(f"- `{method_name}`：{method['why_needed']} 待检查：{', '.join(method['open_checks'])}。")

    lines.extend(["", "## CNKI 人工检索队列"])
    for item in package["cnki_manual_queue"]:
        lines.append(f"- `{item['query']}`：{item['purpose']} 状态：`{item['status']}`。")

    lines.extend(["", "## 下一步"])
    for task in package["next_tasks"]:
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"

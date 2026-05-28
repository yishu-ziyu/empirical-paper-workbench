from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = "p7.method_knowledge_base.v1"
DEFAULT_REPORT_PATH = Path("Results/json/method_knowledge_base.json")
DEFAULT_REVIEW_PATH = Path("Reviews/method_knowledge_base.md")
METHODOLOGY_ROOT = Path("Program/methodology")
PROTECTED_PATHS = [
    "Manuscripts/sections/empirical-strategy.md",
    "Manuscripts/sections/robustness-mechanisms-heterogeneity.md",
    "Data/literature/processed/verified_bibliography.csv",
    "Data/literature/processed/contribution_matrix.md",
    "state/product/design_spec.json",
    "state/product/run_plan.json",
    "state/product/method_knowledge_base.json",
    "Program/methodology/canonical/",
]


def build_method_knowledge_base(
    project_root: Path,
    *,
    query: str = "",
    profile: str = "working_paper",
) -> dict[str, Any]:
    project_root = Path(project_root)
    methodology_root = project_root / METHODOLOGY_ROOT
    readme_path = methodology_root / "README.md"
    proposal_paths = sorted((methodology_root / "proposals").glob("**/proposal.yml"))
    canonical_paths = sorted((methodology_root / "canonical").glob("**/*.yml"))
    missing_inputs = missing_methodology_inputs(readme_path, proposal_paths, canonical_paths)

    if missing_inputs:
        return base_report(project_root, query=query, profile=profile) | {
            "status": "blocked_missing_methodology_sources",
            "missing_inputs": missing_inputs,
            "source_summary": {
                "methodology_readme_present": readme_path.exists(),
                "proposal_source_count": 0,
                "canonical_rule_count": 0,
                "reviewed_canonical_blocking_rule_count": 0,
            },
            "proposal_sources": [],
            "canonical_rules": [],
            "method_families": [],
            "recommended_checks": [],
            "profile_policy": build_profile_policy(profile, has_proposal_sources=False),
            "formal_export_policy": build_formal_export_policy([]),
        }

    proposal_sources = [build_proposal_source(project_root, path) for path in proposal_paths]
    canonical_rules = collect_canonical_rules(project_root, canonical_paths)
    method_families = infer_method_families(query, canonical_rules)
    recommended_checks = build_recommended_checks(query, method_families)
    blocking_canonical_rules = [rule for rule in canonical_rules if rule["can_block_formal_export"]]

    return base_report(project_root, query=query, profile=profile) | {
        "status": "needs_human_method_kb_review",
        "missing_inputs": [],
        "source_summary": {
            "methodology_readme_present": readme_path.exists(),
            "proposal_source_count": len(proposal_sources),
            "canonical_rule_count": len(canonical_rules),
            "reviewed_canonical_blocking_rule_count": len(blocking_canonical_rules),
        },
        "source_artifacts": {
            "methodology_readme": str(readme_path.relative_to(project_root)),
            "proposal_paths": [source["path"] for source in proposal_sources],
            "canonical_paths": sorted({rule["path"] for rule in canonical_rules}),
        },
        "proposal_sources": proposal_sources,
        "canonical_rules": canonical_rules,
        "method_families": method_families,
        "recommended_checks": recommended_checks,
        "profile_policy": build_profile_policy(profile, has_proposal_sources=bool(proposal_sources)),
        "formal_export_policy": build_formal_export_policy(canonical_rules),
    }


def base_report(project_root: Path, *, query: str, profile: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "query": query,
        "profile": profile,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "modified_canonical_rules": False,
        },
        "write_policy": {
            "mode": "method_kb_report_only",
            "does_not_modify": PROTECTED_PATHS,
            "requires_human_review_before_formal_state_writeback": True,
            "requires_human_review_before_canonical_rule_promotion": True,
        },
    }


def missing_methodology_inputs(readme_path: Path, proposal_paths: list[Path], canonical_paths: list[Path]) -> list[str]:
    missing = []
    if not readme_path.exists():
        missing.append("Program/methodology/README.md")
    if not proposal_paths and not canonical_paths:
        missing.append("Program/methodology/proposals")
    return missing


def build_proposal_source(project_root: Path, path: Path) -> dict[str, Any]:
    payload = load_yaml(path)
    status = str(payload.get("status") or "")
    review_status = "proposal_only" if status == "proposal_only" else str(payload.get("review_status") or "needs_human_review")
    return {
        "id": payload.get("id") or path.parent.name,
        "path": str(path.relative_to(project_root)),
        "status": status or "proposal_only",
        "review_status": review_status,
        "purpose": payload.get("purpose") or "",
        "initial_scope": normalize_string_list(payload.get("initial_scope")),
        "external_sources": normalize_external_sources(payload.get("external_sources")),
        "proposal_cannot": normalize_string_list((payload.get("rules_boundary") or {}).get("proposal_cannot")),
        "can_block_formal_export": False,
        "trust_layer": "proposal_unreviewed",
    }


def collect_canonical_rules(project_root: Path, canonical_paths: list[Path]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    for path in canonical_paths:
        payload = load_yaml(path)
        for rule in iter_rule_payloads(payload):
            review_status = str(rule.get("review_status") or "")
            blocks_formal_export = bool(rule.get("blocks_formal_export"))
            can_block = review_status in {"reviewed", "approved", "canonical_reviewed"} and blocks_formal_export
            rules.append(
                {
                    "id": rule.get("id") or path.stem,
                    "path": str(path.relative_to(project_root)),
                    "standard": rule.get("standard") or "",
                    "method_family": rule.get("method_family") or "",
                    "review_status": review_status or "unknown",
                    "severity": rule.get("severity") or "warning",
                    "blocks_formal_export": blocks_formal_export,
                    "can_block_formal_export": can_block,
                    "required_evidence": normalize_string_list(rule.get("required_evidence")),
                    "trust_layer": "canonical_reviewed" if can_block else "canonical_needs_review",
                }
            )
    return rules


def iter_rule_payloads(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        rules = payload.get("rules")
        if isinstance(rules, list):
            return [item for item in rules if isinstance(item, dict)]
        if "id" in payload:
            return [payload]
    return []


def infer_method_families(query: str, canonical_rules: list[dict[str, Any]]) -> list[str]:
    text = query.lower()
    families: list[str] = []
    if any(token in text for token in ["ordered logit", "ordered_logit", "主观幸福", "幸福感", "有序"]) or (
        "ols" in text and "cgss" in text
    ):
        families.append("cross_section_ols_ordered_logit")
    if any(token in text for token in ["bartik", "shift-share", "shift share"]):
        families.append("bartik_shift_share_iv")
    if any(token in text for token in ["iv", "2sls", "weak instrument", "工具变量", "弱工具"]):
        families.append("iv")
    for method in ["did", "rdd", "psm", "dml"]:
        if method in text:
            families.append(method)
    if not families:
        families.extend(rule["method_family"] for rule in canonical_rules if rule.get("method_family"))
    if not families and query.strip():
        families.append("general_empirical_design")
    return unique_preserve_order(families)


def build_recommended_checks(query: str, method_families: list[str]) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    checks: list[dict[str, Any]] = []
    if "cross_section_ols_ordered_logit" in method_families:
        checks.extend(cgss_ols_ordered_logit_checks())
    if "iv" in method_families or "bartik_shift_share_iv" in method_families:
        checks.extend(iv_checks())
    if not checks:
        checks.extend(general_empirical_checks())
    return dedupe_checks(checks)


def cgss_ols_ordered_logit_checks() -> list[dict[str, Any]]:
    return [
        method_check(
            "ordered_outcome_model_fit",
            "主观幸福感等有序因变量需要 Ordered Logit/Ordered Probit 稳健性或解释边界。",
            ["ordered_logit_output", "ordered_outcome_interpretation"],
            ["Program/workbench/cgss_method_gate.py", "tests/test_cgss_method_gate.py"],
        ),
        method_check(
            "ols_association_boundary",
            "横截面 OLS 只能支持条件相关，不能自动升级为强因果。",
            ["claim_boundary_statement", "identification_limit"],
            ["Program/workbench/cgss_method_gate.py"],
        ),
        method_check(
            "endogeneity_risk_statement",
            "需要说明反向因果、遗漏变量和样本选择风险。",
            ["reverse_causality_note", "omitted_variable_risk_note"],
            ["Program/workbench/cgss_method_gate.py"],
        ),
        method_check(
            "baseline_controls",
            "控制变量应覆盖基本人口学、经济条件、健康、户籍或地区差异。",
            ["control_variable_table", "codebook_binding"],
            ["Program/workbench/cgss_method_gate.py"],
        ),
        method_check(
            "robustness_heterogeneity_mechanism_plan",
            "需要进入下一轮稳健性、异质性和机制检验计划或真实结果。",
            ["robustness_plan_or_results", "heterogeneity_plan_or_results", "mechanism_plan_or_results"],
            ["Program/workbench/cgss_method_gate.py"],
        ),
        method_check(
            "candidate_citation_verification",
            "候选引用不能支撑正式方法或理论主张，必须进入人工核验。",
            ["verified_bibliography", "candidate_reference_markers"],
            ["Program/workbench/level3_manuscript_quality_gate.py"],
        ),
    ]


def iv_checks() -> list[dict[str, Any]]:
    return [
        method_check(
            "weak_iv_robust_inference",
            "IV/Bartik 设计不能只报告常规 first stage，需要弱工具稳健推断。",
            ["robust_first_stage_f_or_kp", "ar_or_clr_interval"],
            ["Program/workbench/method_gate.py", "docs/architecture-v2/journal-skill-registry-design-2026-05-26.md"],
        ),
        method_check(
            "exclusion_restriction_review",
            "工具变量排除限制和 share/shock 外生性需要人工审阅。",
            ["exclusion_restriction_argument", "shock_exogeneity_argument"],
            ["Program/workbench/method_gate.py"],
        ),
    ]


def general_empirical_checks() -> list[dict[str, Any]]:
    return [
        method_check(
            "method_claim_boundary",
            "方法设计必须把可支持的经验主张和不可支持的强因果主张分开。",
            ["claim_boundary_statement"],
            ["Program/methodology/README.md"],
        )
    ]


def method_check(
    check_id: str,
    rule: str,
    required_evidence: list[str],
    source_refs: list[str],
) -> dict[str, Any]:
    return {
        "id": check_id,
        "status": "recommended",
        "rule": rule,
        "required_evidence": required_evidence,
        "source_refs": source_refs,
        "blocks_formal_export": False,
        "requires_human_review": True,
    }


def build_profile_policy(profile: str, *, has_proposal_sources: bool) -> dict[str, Any]:
    recommended = ["AER-like 顶刊标准"] if profile in {"aer_like", "top_journal"} else []
    return {
        "requested_profile": profile,
        "recommended_standards": recommended,
        "has_proposal_sources": has_proposal_sources,
        "proposal_enforcement_mode": "recommendation_only_until_canonical_review",
        "canonical_enforcement_mode": "reviewed_rules_may_block_formal_export",
    }


def build_formal_export_policy(canonical_rules: list[dict[str, Any]]) -> dict[str, Any]:
    blocking_count = sum(1 for rule in canonical_rules if rule["can_block_formal_export"])
    return {
        "proposal_rules_can_block": False,
        "reviewed_canonical_blocking_rule_count": blocking_count,
        "canonical_rules_can_block_after_human_review": blocking_count > 0,
        "can_export_based_on_method_kb_alone": False,
        "requires_export_gate_integration": True,
    }


def write_outputs(
    project_root: Path,
    kb: dict[str, Any],
    report_path: Path,
    review_path: Path,
) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(kb), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(kb: dict[str, Any]) -> str:
    summary = kb.get("source_summary", {})
    lines = [
        "# Method Knowledge Base",
        "",
        f"- 状态：{kb['status']}",
        f"- profile：{kb['profile']}",
        f"- query：{kb.get('query', '') or '(none)'}",
        f"- proposal 来源数：{summary.get('proposal_source_count', 0)}",
        f"- canonical 规则数：{summary.get('canonical_rule_count', 0)}",
        f"- reviewed canonical blocking 规则数：{summary.get('reviewed_canonical_blocking_rule_count', 0)}",
        "- proposal 规则阻断正式导出：否",
        "- 正式论文写回：否",
        "- 正式 bibliography 写回：否",
        "- DesignSpec/RunPlan 写回：否",
        "- product state 写回：否",
        "- canonical 规则写回：否",
        "",
        "## 推荐方法检查",
    ]
    checks = kb.get("recommended_checks", [])
    if checks:
        for check in checks:
            lines.append(f"- `{check['id']}`：{check['rule']}")
    else:
        lines.append("- 无推荐检查；可能是未提供 query，或方法库来源缺失。")
    if kb.get("missing_inputs"):
        lines.extend(["", "## 缺失输入"])
        lines.extend(f"- {item}" for item in kb["missing_inputs"])
    lines.extend(
        [
            "",
            "## 人工审阅",
            "- 核对 proposal 来源是否可以进入 canonical review。",
            "- 核对 recommended checks 是否适用于当前研究设计。",
            "- 只有人工 review 后的 canonical blocking 规则才能接入正式导出门禁。",
        ]
    )
    return "\n".join(lines) + "\n"


def load_yaml(path: Path) -> Any:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload


def normalize_external_sources(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def dedupe_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped = []
    for check in checks:
        if check["id"] in seen:
            continue
        seen.add(check["id"])
        deduped.append(check)
    return deduped

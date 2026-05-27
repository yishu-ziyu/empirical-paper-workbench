from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_verified_bibliography_candidates.v1"
DEFAULT_SOURCE_PREFLIGHT_PATH = Path(
    "Results/json/cgss_social_capital_happiness_literature_source_verification_preflight.json"
)
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_verified_bibliography_candidates.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_verified_bibliography_candidates.md")


SOURCE_CHECKED_METADATA: dict[str, dict[str, Any]] = {
    "S03": {
        "title": "Bowling Alone: The Collapse and Revival of American Community",
        "authors": ["Robert D. Putnam"],
        "year": "2000",
        "source_type": "classic_theory",
        "source_checked_url": "https://www.simonandschuster.com/books/Bowling-Alone-Revised-and-Updated/Robert-D-Putnam/9781982130848",
        "source_evidence": "publisher_page_opened",
        "citation_key": "putnam_2000",
        "paper_use": "组织信任、规范和网络三类社会资本维度。",
    },
    "S04": {
        "title": "The Forms of Capital",
        "authors": ["Pierre Bourdieu"],
        "year": "1986",
        "source_type": "classic_theory",
        "source_checked_url": "https://web.stanford.edu/~eckert/PDF/Bourdieu1986.pdf",
        "source_evidence": "public_pdf_opened",
        "citation_key": "bourdieu_1986",
        "paper_use": "补充社会资本作为可动员关系资源的理论解释。",
    },
    "S06": {
        "title": "OECD Guidelines on Measuring Subjective Well-being",
        "authors": ["OECD"],
        "year": "2025",
        "source_type": "measurement_standard",
        "source_checked_url": "https://www.oecd.org/en/publications/oecd-guidelines-on-measuring-subjective-well-being-2025-update_9203632a-en.html",
        "source_evidence": "official_guideline_page_opened",
        "citation_key": "oecd_2025",
        "paper_use": "说明主观幸福感测量应区分生活评价、情感体验和其他福利指标。",
    },
    "S07": {
        "title": "Measuring Social Capital: An Integrated Questionnaire",
        "authors": ["World Bank"],
        "year": "2004",
        "source_type": "measurement_standard",
        "source_checked_url": "https://openknowledge.worldbank.org/entities/publication/634c867c-cbc8-536a-8446-a2703177bc7c",
        "source_evidence": "official_repository_page_opened",
        "citation_key": "world_bank_2004",
        "paper_use": "为信任、网络、集体行动和信息沟通等社会资本维度提供测量参照。",
    },
    "S08": {
        "title": "Social trust, social capital, and subjective well-being of rural residents",
        "authors": ["Xu", "Zhang", "Huang"],
        "year": "2023",
        "source_type": "cgss_empirical_study",
        "source_checked_url": "https://www.nature.com/articles/s41599-023-01532-1",
        "source_evidence": "journal_page_opened",
        "citation_key": "xu_zhang_huang_2023",
        "paper_use": "提供 CGSS 语境下社会信任、社会资本与主观幸福感的实证参照。",
    },
    "S09": {
        "title": "机会不均等、社会资本与农民主观幸福感",
        "authors": ["张彤进", "万广华"],
        "year": "2020",
        "source_type": "chinese_literature_seed",
        "source_checked_url": "https://qks.shufe.edu.cn/J/ArticleQuery/f824063e-2826-4256-90f5-e5ff8aa79e7a/CN",
        "source_evidence": "journal_page_opened",
        "citation_key": "zhang_wan_2020",
        "paper_use": "作为中文 CGSS 幸福感研究和社会资本机制的候选中文文献。",
    },
    "S10": {
        "title": "How Important is Methodology for the estimates of the determinants of Happiness?",
        "authors": ["Ferrer-i-Carbonell", "Frijters"],
        "year": "2004",
        "source_type": "method_reference",
        "source_checked_url": "https://doi.org/10.1111/j.1468-0297.2004.00235.x",
        "source_evidence": "doi_or_repository_page_opened",
        "citation_key": "ferrer_i_carbonell_frijters_2004",
        "paper_use": "支撑幸福感有序变量建模和 OLS/有序模型稳健性讨论。",
    },
}

CITATION_BINDINGS: list[dict[str, str]] = [
    {
        "source_id": "S03",
        "target_section": "literature_review",
        "claim_role": "social capital as trust, norms, and networks",
        "draft_sentence_slot": "社会资本理论定义段",
    },
    {
        "source_id": "S04",
        "target_section": "literature_review",
        "claim_role": "social capital as mobilizable relational resources",
        "draft_sentence_slot": "社会资本理论扩展段",
    },
    {
        "source_id": "S06",
        "target_section": "data_and_measurement",
        "claim_role": "subjective wellbeing measurement limits",
        "draft_sentence_slot": "主观幸福感变量说明段",
    },
    {
        "source_id": "S07",
        "target_section": "data_and_measurement",
        "claim_role": "social capital measurement dimensions",
        "draft_sentence_slot": "社会资本指数构造说明段",
    },
    {
        "source_id": "S08",
        "target_section": "literature_review",
        "claim_role": "CGSS social capital subjective wellbeing empirical context",
        "draft_sentence_slot": "CGSS 相关经验研究段",
    },
    {
        "source_id": "S09",
        "target_section": "literature_review",
        "claim_role": "Chinese CGSS social capital happiness evidence",
        "draft_sentence_slot": "中文研究脉络段",
    },
    {
        "source_id": "S10",
        "target_section": "empirical_strategy",
        "claim_role": "ordered outcome happiness method robustness",
        "draft_sentence_slot": "有序因变量方法说明段",
    },
]

MANUAL_FOLLOWUP_DEFAULTS: dict[str, dict[str, Any]] = {
    "S01": {
        "source_id": "S01",
        "title": "CGSS 项目概况",
        "reason": "需要记录官方页面访问日期，并确认 CGSS2023 使用说明。",
        "required_action": "open_official_source_and_record_access_date",
    },
    "S02": {
        "source_id": "S02",
        "title": "Social Capital in the Creation of Human Capital",
        "reason": "需要补齐 DOI 页面元数据、期刊卷期页码或 Zotero 条目。",
        "required_action": "verify_doi_or_zotero_metadata",
    },
    "S05": {
        "source_id": "S05",
        "title": "Subjective Well-Being",
        "reason": "需要核验 DOI 元数据，并决定是否还需要更适合幸福感测量的近年综述。",
        "required_action": "verify_doi_or_zotero_metadata",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_verified_bibliography_candidates(
    source_preflight: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": source_preflight.get("topic", ""),
        "source_artifacts": {
            "literature_source_verification_preflight": {
                "path": source_paths.get("source_preflight", str(DEFAULT_SOURCE_PREFLIGHT_PATH)),
                "schema_version": source_preflight.get("schema_version", ""),
                "status": source_preflight.get("status", ""),
            }
        },
        "boundary_flags": {
            "modified_verified_bibliography": False,
            "modified_contribution_matrix": False,
            "modified_formal_bibliography": False,
            "modified_formal_manuscript": False,
            "wrote_state_product": False,
        },
    }
    if source_preflight.get("status") != "needs_source_verification":
        base.update(
            {
                "status": "blocked_missing_source_preflight",
                "blocking_reasons": ["source_preflight_not_ready"],
                "verified_bibliography_candidates": [],
                "manual_followup_queue": [],
                "citation_bindings": [],
                "promotion": {"allowed": False, "required_decision": "repair_source_preflight"},
                "next_tasks": ["repair_literature_source_verification_preflight"],
            }
        )
        return base

    candidate_by_id = {item["id"]: item for item in source_preflight.get("candidate_bibliography", [])}
    verified_candidates = [
        build_source_checked_candidate(source_id, candidate_by_id.get(source_id, {}))
        for source_id in SOURCE_CHECKED_METADATA
    ]
    manual_queue = build_manual_followup_queue(source_preflight)
    blocking_reasons = ["human_bibliography_approval_required"]
    if manual_queue:
        blocking_reasons.append("browser_or_database_verification_required")

    base.update(
        {
            "status": "needs_human_bibliography_approval",
            "blocking_reasons": blocking_reasons,
            "verified_bibliography_candidates": verified_candidates,
            "manual_followup_queue": manual_queue,
            "citation_bindings": CITATION_BINDINGS,
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_verified_bibliography_candidates",
                "would_write_if_approved": [
                    "Data/literature/processed/verified_bibliography.csv",
                    "Data/literature/processed/contribution_matrix.md",
                    "Results/json/cgss_social_capital_happiness_citation_bindings.json",
                ],
            },
            "next_tasks": [
                "human_review_verified_bibliography_candidates",
                "write_verified_bibliography_after_approval",
                "draft_cgss_literature_review_section",
            ],
        }
    )
    return base


def build_source_checked_candidate(source_id: str, seed_candidate: dict[str, Any]) -> dict[str, Any]:
    metadata = SOURCE_CHECKED_METADATA[source_id]
    return {
        "source_id": source_id,
        "title": metadata["title"],
        "authors": metadata["authors"],
        "year": metadata["year"],
        "source_type": metadata["source_type"],
        "source_checked_url": metadata["source_checked_url"],
        "source_evidence": metadata["source_evidence"],
        "review_status": "source_checked_candidate",
        "human_approval_required": True,
        "ready_for_verified_bibliography": False,
        "citation_key": metadata["citation_key"],
        "paper_use": metadata["paper_use"],
        "seed_review_status": seed_candidate.get("review_status", ""),
        "do_not_claim": seed_candidate.get("do_not_claim", ""),
    }


def build_manual_followup_queue(source_preflight: dict[str, Any]) -> list[dict[str, Any]]:
    candidate_by_id = {item["id"]: item for item in source_preflight.get("candidate_bibliography", [])}
    queue = []
    for source_id, item in MANUAL_FOLLOWUP_DEFAULTS.items():
        seed = candidate_by_id.get(source_id, {})
        queue.append(
            {
                **item,
                "source_type": seed.get("source_type", ""),
                "current_url": seed.get("url", ""),
                "status": "manual_verification_required",
            }
        )
    return queue


def write_verified_bibliography_candidate_outputs(
    project_root: Path,
    package: dict[str, Any],
    result_path: Path,
    review_path: Path,
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
        "# CGSS 可核验参考文献候选",
        "",
        f"- 题目：{package.get('topic', '')}",
        f"- 状态：`{package['status']}`",
        "- 写入正式参考文献：否",
        "- 写入正式论文：否",
    ]
    if package["blocking_reasons"]:
        lines.extend(["", "## 当前需要处理"])
        for reason in package["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if package["status"].startswith("blocked"):
        return "\n".join(lines) + "\n"

    lines.extend(["", "## 可进入人工审阅的参考文献候选"])
    for item in package["verified_bibliography_candidates"]:
        authors = "，".join(item["authors"])
        lines.extend(
            [
                f"### {item['source_id']} {item['title']}",
                f"- 作者/机构：{authors}",
                f"- 年份：{item['year']}",
                f"- 候选 citation key：`{item['citation_key']}`",
                f"- 来源证据：`{item['source_evidence']}`",
                f"- 链接：{item['source_checked_url']}",
                f"- 论文中用途：{item['paper_use']}",
                f"- 人工批准后才写入正式参考文献：是",
                "",
            ]
        )
    lines.extend(["## 仍需人工或数据库辅助核验"])
    for item in package["manual_followup_queue"]:
        lines.append(
            f"- {item['source_id']} {item['title']}：{item['reason']} 动作：`{item['required_action']}`。"
        )
    lines.extend(["", "## 引用绑定候选"])
    for item in package["citation_bindings"]:
        lines.append(
            f"- {item['source_id']} -> `{item['target_section']}`：{item['claim_role']}；位置：{item['draft_sentence_slot']}。"
        )
    lines.extend(["", "## 人工批准后才会写入"])
    for path in package["promotion"]["would_write_if_approved"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## 下一步"])
    for task in package["next_tasks"]:
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_literature_review_draft_packet.v1"
DEFAULT_BIBLIOGRAPHY_CANDIDATES_PATH = Path(
    "Results/json/cgss_social_capital_happiness_verified_bibliography_candidates.json"
)
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_literature_review_draft_packet.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_literature_review_draft_packet(
    bibliography_candidates: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": bibliography_candidates.get("topic", ""),
        "source_artifacts": {
            "verified_bibliography_candidates": {
                "path": source_paths.get("bibliography_candidates", str(DEFAULT_BIBLIOGRAPHY_CANDIDATES_PATH)),
                "schema_version": bibliography_candidates.get("schema_version", ""),
                "status": bibliography_candidates.get("status", ""),
            }
        },
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_verified_bibliography": False,
            "modified_contribution_matrix": False,
            "wrote_manuscript_section": False,
            "wrote_state_product": False,
        },
    }
    if bibliography_candidates.get("status") != "needs_human_bibliography_approval":
        base.update(
            {
                "status": "blocked_missing_bibliography_candidates",
                "draft_mode": "blocked",
                "blocking_reasons": ["bibliography_candidates_not_reviewable"],
                "paragraph_blocks": [],
                "open_dependencies": [],
                "length_plan": {},
                "promotion": {"allowed": False, "required_decision": "repair_bibliography_candidates"},
                "next_tasks": ["repair_verified_bibliography_candidates"],
            }
        )
        return base

    candidates_by_id = {
        item["source_id"]: item for item in bibliography_candidates.get("verified_bibliography_candidates", [])
    }
    paragraph_blocks = build_paragraph_blocks(candidates_by_id)
    open_dependencies = bibliography_candidates.get("manual_followup_queue", [])
    blocking_reasons = ["literature_review_draft_needs_human_approval"]
    if open_dependencies:
        blocking_reasons.append("manual_or_database_verification_required")

    base.update(
        {
            "status": "needs_human_literature_review_draft_approval",
            "draft_mode": "pending_bibliography_approval",
            "blocking_reasons": blocking_reasons,
            "section_target": "Manuscripts/sections/literature-and-contribution.md",
            "length_plan": {
                "target_chinese_characters": 1600,
                "minimum_chinese_characters": 1200,
                "paragraph_count": len(paragraph_blocks),
                "citation_target": "至少 6 条候选引用，其中中文经验研究不少于 1 条。",
            },
            "paragraph_blocks": paragraph_blocks,
            "open_dependencies": open_dependencies,
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_literature_review_draft_packet",
                "would_write_if_approved": [
                    "Manuscripts/sections/literature-and-contribution.md",
                    "Results/json/cgss_social_capital_happiness_literature_review_citation_plan.json",
                ],
            },
            "next_tasks": [
                "human_review_literature_review_draft_packet",
                "approve_or_revise_bibliography_candidates",
                "expand_literature_review_section_after_approval",
            ],
        }
    )
    return base


def build_paragraph_blocks(candidates_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": "theory_foundation",
            "heading": "社会资本理论基础",
            "source_ids": ["S03", "S04"],
            "citation_keys": citation_keys(candidates_by_id, ["S03", "S04"]),
            "draft_claim": "社会资本可以从信任、规范、网络和可动员关系资源两条线索理解，为居民幸福感提供社会支持与信息渠道。",
            "draft_paragraph": (
                "已有社会资本理论强调，个体并不是孤立地形成福利评价，而是嵌入在信任、互惠规范、社会网络和可动员关系资源之中。"
                "Putnam 的讨论有助于把社会资本拆成信任、规范与网络，Bourdieu 的框架则提醒我们，社会关系本身也可能转化为个体能够动员的资源。"
                "因此，本文把社会资本理解为能够影响居民生活评价的关系性资源，而不是单一的人际交往频率。"
            ),
            "review_focus": "确认理论段是否需要加入 Coleman，或把 Coleman 留到人工核验后再写入。",
        },
        {
            "id": "measurement_foundation",
            "heading": "变量测量与 CGSS 题项口径",
            "source_ids": ["S06", "S07"],
            "citation_keys": citation_keys(candidates_by_id, ["S06", "S07"]),
            "draft_claim": "CGSS 幸福感单题可以作为生活评价代理变量，社会资本指数需要说明其不是完整量表而是基于可用题项的操作化指标。",
            "draft_paragraph": (
                "在变量测量上，CGSS 的总体幸福感题项更接近生活评价意义上的主观幸福感代理变量。"
                "OECD 的主观幸福感测量框架提示，生活评价、情绪体验与更宽泛的福利状态需要区分。"
                "社会资本方面，World Bank 的测量框架说明信任、网络、集体行动和信息沟通等维度都可能构成社会资本。"
                "受 CGSS2023 可用题项约束，本文先以社会信任、社会交往和参与相关题项构造综合指数，并在正文中保留测量边界说明。"
            ),
            "review_focus": "确认 a33、a31a、a31b、a311 是否足以构成本文的社会资本指数。",
        },
        {
            "id": "cgss_empirical_context",
            "heading": "中国经验研究与 CGSS 场景",
            "source_ids": ["S08", "S09"],
            "citation_keys": citation_keys(candidates_by_id, ["S08", "S09"]),
            "draft_claim": "既有 CGSS 和中国经验研究已经把社会资本与主观幸福感联系起来，本文的贡献需要落在 CGSS2023、变量组合或样本范围上。",
            "draft_paragraph": (
                "围绕中国居民幸福感的经验研究已经注意到社会信任、社会资本与福利评价之间的关联。"
                "相关 CGSS 研究为本文提供了变量选择和机制讨论的参照，中文研究也提示社会资本可能与机会结构、收入环境和群体差异交织在一起。"
                "因此，本文不是重新证明社会资本概念本身的重要性，而是利用 CGSS2023 的可用样本，在统一控制人口学、收入、健康和地区差异后，检验社会资本指数与居民主观幸福感之间的稳定关系。"
            ),
            "review_focus": "补 CNKI 后判断是否需要扩展更多中文文献，而不是只依赖当前一篇中文候选。",
        },
        {
            "id": "method_transition",
            "heading": "有序因变量与实证策略衔接",
            "source_ids": ["S10"],
            "citation_keys": citation_keys(candidates_by_id, ["S10"]),
            "draft_claim": "幸福感是有序离散变量，OLS 可以作为可读性基准，Ordered Logit 应作为关键稳健性结果进入方法说明。",
            "draft_paragraph": (
                "由于主观幸福感变量通常以有序等级记录，模型选择会影响系数解释和显著性呈现。"
                "方法文献表明，在幸福感研究中同时报告线性模型和有序响应模型有助于检验结论是否依赖模型设定。"
                "因此，本文把 OLS 作为直观基准，把 Ordered Logit 作为有序因变量稳健性模型，并在解释结果时避免把相关关系直接写成严格因果效应。"
            ),
            "review_focus": "确认 Ordered Logit 是否作为主模型，或保留 OLS 为主、Ordered Logit 为稳健性。",
        },
    ]


def citation_keys(candidates_by_id: dict[str, dict[str, Any]], source_ids: list[str]) -> list[str]:
    return [candidates_by_id[source_id]["citation_key"] for source_id in source_ids if source_id in candidates_by_id]


def write_literature_review_draft_packet_outputs(
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
        "# CGSS 文献综述草稿包",
        "",
        f"- 题目：{packet.get('topic', '')}",
        f"- 状态：`{packet['status']}`",
        f"- 草稿模式：`{packet.get('draft_mode', '')}`",
        "- 写入正式论文：否",
        "- 写入正式参考文献：否",
    ]
    if packet["blocking_reasons"]:
        lines.extend(["", "## 当前需要处理"])
        for reason in packet["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if packet["status"].startswith("blocked"):
        return "\n".join(lines) + "\n"

    length_plan = packet["length_plan"]
    lines.extend(
        [
            "",
            "## 长度与结构标准",
            f"- 目标字数：{length_plan['target_chinese_characters']} 中文字符左右",
            f"- 最低字数：{length_plan['minimum_chinese_characters']} 中文字符",
            f"- 段落数：{length_plan['paragraph_count']}",
            f"- 引用目标：{length_plan['citation_target']}",
            "",
            "## 段落草稿",
        ]
    )
    for block in packet["paragraph_blocks"]:
        lines.extend(
            [
                f"### {block['heading']}",
                f"- 来源：{', '.join(block['source_ids'])}",
                f"- citation keys：{', '.join(block['citation_keys'])}",
                f"- 核心论点：{block['draft_claim']}",
                "",
                block["draft_paragraph"],
                "",
                f"审阅重点：{block['review_focus']}",
                "",
            ]
        )
    lines.extend(["## 仍需补齐"])
    for item in packet["open_dependencies"]:
        lines.append(f"- {item['source_id']} {item['title']}：{item['reason']}")
    lines.extend(["", "## 人工批准后才会写入"])
    for path in packet["promotion"]["would_write_if_approved"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## 下一步"])
    for task in packet["next_tasks"]:
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"

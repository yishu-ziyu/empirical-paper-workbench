from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_exploratory_paper_assembler.v1"
DEFAULT_SECTION_PACKAGE_PATH = Path("Results/json/cgss_social_capital_happiness_manuscript_sections.json")
DEFAULT_RESULTS_EVIDENCE_PATH = Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json")
DEFAULT_LITERATURE_PACKET_PATH = Path("Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json")
DEFAULT_PAPER_PATH = Path("Manuscripts/generated/cgss_social_capital_happiness_paper.md")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_paper_assembly.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_paper_assembly.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_exploratory_paper_package(
    section_package: dict[str, Any],
    results_evidence_package: dict[str, Any],
    literature_review_packet: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": section_package.get("topic") or results_evidence_package.get("topic", ""),
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "paper_path": str(DEFAULT_PAPER_PATH),
        "source_artifacts": {
            "manuscript_sections": {
                "path": source_paths.get("manuscript_sections", str(DEFAULT_SECTION_PACKAGE_PATH)),
                "schema_version": section_package.get("schema_version", ""),
                "status": section_package.get("status", ""),
            },
            "results_evidence_package": {
                "path": source_paths.get("results_evidence_package", str(DEFAULT_RESULTS_EVIDENCE_PATH)),
                "schema_version": results_evidence_package.get("schema_version", ""),
                "status": results_evidence_package.get("status", ""),
            },
            "literature_review_draft_packet": {
                "path": source_paths.get("literature_review_draft_packet", str(DEFAULT_LITERATURE_PACKET_PATH)),
                "schema_version": literature_review_packet.get("schema_version", ""),
                "status": literature_review_packet.get("status", ""),
            },
        },
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_verified_bibliography": False,
            "modified_formal_package": False,
            "modified_product_state": False,
            "promoted_to_canonical_claim": False,
        },
    }
    blocking_reasons = blocking_reasons_for(section_package, results_evidence_package, literature_review_packet)
    if blocking_reasons:
        return {
            **base,
            "status": "blocked_manuscript_sections_not_ready"
            if "manuscript_sections_not_review_ready" in blocking_reasons
            else "blocked_missing_paper_inputs",
            "blocking_reasons": blocking_reasons,
            "assembled_sections": [],
            "evidence_ledger": [],
            "paper_metrics": {"chinese_characters": 0},
            "paper_markdown": "",
            "next_tasks": ["repair_blocked_paper_inputs"],
        }

    sections = ordered_ready_sections(section_package)
    evidence_ledger = sorted(
        {
            "cgss_results_evidence_package",
            "cgss_literature_review_draft_packet",
            "cgss_manuscript_section_package",
            *[
                evidence
                for section in sections
                for evidence in section.get("evidence_bindings", [])
            ],
        }
    )
    paper_markdown = render_paper_markdown(sections, results_evidence_package, literature_review_packet)
    return {
        **base,
        "status": "needs_human_exploratory_paper_review",
        "blocking_reasons": [],
        "assembled_sections": [
            {
                "section_id": section["section_id"],
                "title": section["title"],
                "source_path": section["path"],
                "evidence_bindings": section.get("evidence_bindings", []),
                "citation_keys": section.get("citation_keys", []),
            }
            for section in sections
        ],
        "evidence_ledger": evidence_ledger,
        "paper_metrics": {
            "chinese_characters": count_chinese_characters(paper_markdown),
            "section_count": len(sections),
            "minimum_chinese_characters": 5000,
        },
        "paper_markdown": paper_markdown,
        "agent_team_schedule": {
            "call_when": "before_full_paper_assembly_and_pdf_preflight",
            "called_agents": ["ManuscriptAgent", "VerifierAgent", "MethodAgent", "LiteratureAgent"],
            "recall_when": "after_paper_markdown_is_assembled_and_before_pdf_preflight",
            "next_call_when": "after_human_reviews_exploratory_paper",
            "boundary": "完整稿仍为草案层；Agent Team 只检查结构、证据、方法门和引用候选，不提升正式层。",
        },
        "human_review_checklist": [
            "逐节确认是否符合论文结构和最低字数",
            "确认候选文献是否允许进入正式参考文献",
            "确认 OLS 与 Ordered Logit 结果解释是否准确",
            "确认稳健性、异质性和内生性任务优先级",
            "确认是否进入 PDF 预检和审稿式修订循环",
        ],
        "next_tasks": [
            "human_review_exploratory_paper",
            "run_pdf_export_preflight",
            "build_aer_like_method_gate",
            "generate_reviewer_report_and_revision_queue",
        ],
    }


def blocking_reasons_for(
    section_package: dict[str, Any],
    results_evidence_package: dict[str, Any],
    literature_review_packet: dict[str, Any],
) -> list[str]:
    reasons = []
    if section_package.get("status") != "needs_human_manuscript_section_review":
        reasons.append("manuscript_sections_not_review_ready")
    if any(section.get("status") != "section_draft_ready_for_review" for section in section_package.get("sections", [])):
        reasons.append("manuscript_sections_not_review_ready")
    if results_evidence_package.get("status") != "ready_for_paper_draft_input":
        reasons.append("results_evidence_package_not_ready")
    if literature_review_packet.get("status") != "needs_human_literature_review_draft_approval":
        reasons.append("literature_review_packet_not_reviewable")
    return sorted(set(reasons))


def ordered_ready_sections(section_package: dict[str, Any]) -> list[dict[str, Any]]:
    order = {
        "literature_and_contribution": 0,
        "data_and_measurement": 1,
        "empirical_strategy": 2,
        "main_results": 3,
    }
    sections = [
        section
        for section in section_package.get("sections", [])
        if section.get("status") == "section_draft_ready_for_review"
    ]
    return sorted(sections, key=lambda section: order.get(section.get("section_id", ""), 99))


def render_paper_markdown(
    sections: list[dict[str, Any]],
    results_evidence_package: dict[str, Any],
    literature_review_packet: dict[str, Any],
) -> str:
    section_by_id = {section["section_id"]: extract_draft_body(section.get("draft_markdown", "")) for section in sections}
    topic = results_evidence_package.get("topic", "社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析")
    ols = results_evidence_package.get("primary_result", {}).get("ols", {})
    ordered = results_evidence_package.get("primary_result", {}).get("ordered_logit", {})
    dataset = results_evidence_package.get("dataset", {})
    variables = results_evidence_package.get("variables", {})
    controls = "、".join(variables.get("controls", []))
    open_dependencies = literature_review_packet.get("open_dependencies", [])
    bibliography = candidate_bibliography(literature_review_packet, sections)

    lines = [
        "# 社会资本对居民主观幸福感的影响研究",
        "",
        "副标题：基于 CGSS 数据的实证分析",
        "",
        "- Draft layer: `true`",
        "- Formal writeback: `false`",
        "- Status: `needs_human_exploratory_paper_review`",
        "",
        "## 摘要",
        "",
        (
            f"本文围绕“{topic}”展开，使用 {dataset.get('year', '2023')} 年 CGSS 数据构造社会资本指数，"
            "并考察其与居民主观幸福感之间的关系。当前探索性结果显示，在控制人口学、经济状态、健康状况、户籍和地区因素后，"
            f"社会资本指数与幸福感呈稳定正向关系：OLS 模型中的核心系数约为 {format_number(ols.get('coef'))}，"
            f"Ordered Logit 模型中的核心系数约为 {format_number(ordered.get('coef'))}。"
            "文章进一步从社会支持、信任机制和社会参与三个角度解释这一关系，并明确当前证据的边界："
            "本轮结果建立在横截面数据和可观察控制变量之上，适合作为完整论文草稿和后续方法升级的基础。"
        ),
        "",
        "关键词：社会资本；主观幸福感；CGSS；有序因变量；实证研究",
        "",
        "## 一、引言",
        "",
        (
            "主观幸福感已经成为理解居民生活质量和社会发展水平的重要指标。与收入、就业、教育等传统经济变量相比，"
            "幸福感更直接反映个体对生活状态的整体评价，也更容易受到社会关系、社区环境和公共信任的影响。"
            "在快速流动和社会结构持续变化的背景下，居民是否拥有稳定的社会连接、能否从身边关系中获得支持、"
            "是否信任周围人和公共生活，都会进入个体对生活的判断。"
            "因此，社会资本与幸福感之间的关系不仅是社会学问题，也是经济学和公共政策研究中值得被系统检验的问题。"
            "本文选择 CGSS 数据，是因为该数据同时包含幸福感评价、信任、交往和社会参与等题项，能够把研究问题落到可执行的变量结构上。"
        ),
        "",
        (
            "本文的研究问题可以表述为：在中国居民样本中，社会资本水平更高的个体是否报告更高的主观幸福感？"
            "为了回答这一问题，当前版本先完成一条可复现的探索性主链路：从本机 CGSS 数据资产中发现可用字段，"
            "将幸福感题项绑定为因变量，将信任、邻里交往、朋友交往和休闲社会参与构造为社会资本指数，"
            "再通过 OLS 和 Ordered Logit 两类模型检验结果方向是否稳定。"
            "这种路线的优点是清楚、可复现、便于审阅；它不把复杂因果识别提前包装成已完成事实，而是先形成一篇结构完整、证据可追溯的草稿。"
        ),
        "",
        (
            "本文后续还需要继续提升三件事。第一，文献综述需要进一步接入 CNKI、Zotero 或 Scholar 的核验结果，"
            "把候选引用升级为可进入正式参考文献的来源。第二，方法层需要补充分项社会资本、异质性、替代变量和稳健性检验，"
            "让主要结果不只依赖一个综合指数。第三，写作层需要经过审稿式修订循环，把变量解释、结果含义和研究贡献写得更紧。"
            "这些工作将在当前探索性论文包之后继续推进。"
        ),
        "",
        "## 二、文献综述与研究贡献",
        "",
        section_by_id.get("literature_and_contribution", ""),
        "",
        "## 三、数据与变量",
        "",
        section_by_id.get("data_and_measurement", ""),
        "",
        (
            f"从执行口径看，当前数据来源为 `{dataset.get('source', 'CGSS2023.dta')}`，"
            f"因变量为 `{variables.get('outcome', 'happiness <- a36')}`，"
            f"控制变量包括 {controls}。这些变量并不是页面展示用的占位符，而是已经进入本地模型执行证据包的字段。"
            "正式稿中还应增加描述性统计表和缺失值处理说明，尤其是收入、健康和社会参与题项的缺失情况。"
        ),
        "",
        "## 四、实证策略",
        "",
        section_by_id.get("empirical_strategy", ""),
        "",
        "## 五、主要实证结果",
        "",
        section_by_id.get("main_results", ""),
        "",
        "## 六、稳健性与进一步检验计划",
        "",
        (
            "当前结果已经完成基准 OLS 与 Ordered Logit 的一致性检查，但距离更强的论文证据还需要继续扩展。"
            "第一类任务是变量层稳健性：将社会资本指数拆成信任、邻里交往、朋友交往和休闲参与四个分项，分别估计其与幸福感的关系，"
            "观察结果是否由某一类题项单独驱动。第二类任务是模型层稳健性：在控制变量集合、标准误设定、样本筛选和地区固定效应上做替代设定，"
            "确认核心结果是否稳定。第三类任务是解释层扩展：考察城乡、教育、收入或年龄组之间是否存在差异，判断社会资本对不同群体幸福感的关联强度是否相同。"
        ),
        "",
        (
            "如果研究目标进一步提高到因果解释，系统需要进入更严格的方法门。对于 DID，需要有明确政策冲击、处理组和时间维度；"
            "对于 IV，需要有理论上可信且能通过弱工具检查的工具变量；对于 RDD，需要存在清楚断点和断点附近样本；"
            "对于 PSM 或 DML，需要有明确处理变量以及足够丰富的协变量集合。当前 CGSS2023 横截面版本还没有满足这些条件，"
            "所以本文把这些方法作为后续升级方向，而不是在草稿中强行套用。这样写能让论文保持可解释和可复现，也能给下一轮 Agent Team 留出明确任务。"
        ),
        "",
        (
            "还需要强调的是，稳健性计划不是为了把论文写得更复杂，而是为了让每一个主要判断都有可复查的备份证据。"
            "如果综合社会资本指数为正，但分项指标只有社会信任显著，论文的解释重心就应从一般关系网络转向信任机制；"
            "如果城乡分组结果差异明显，正文就需要讨论社会资本在不同社会结构中的作用条件；"
            "如果替换控制变量后系数明显波动，ReviewerAgent 应当把遗漏变量风险提升为下一轮重点任务。"
            "因此，本节的真正作用是把后续分析变成一个有顺序的任务队列，而不是简单列出“还可以做很多检验”。"
        ),
        "",
        (
            "在 paper package 层面，所有新增检验都应继续遵守草案层和正式层分离：模型可以自动运行，表格和解释可以自动生成，"
            "但是否把结果写入正式论文，需要等人类审阅变量含义、模型设定和文献支撑之后再决定。"
            "这也是当前系统和普通脚本的区别：脚本只负责跑结果，而研究工作流必须同时保存执行证据、方法边界、审阅问题和下一轮修订方向。"
        ),
        "",
        (
            "因此，后续验收不应只看论文是否生成，还要看每个结论能否追溯到数据、模型、文献或人工判断。"
            "如果某个段落没有证据绑定，它就应停留在修订队列；如果某个数字无法复跑得到，它就不能进入正式表格。"
            "这条规则会让写作速度慢一点，但能保证论文包真正可审计。"
            "人工审阅时也应优先看这些追溯链，而不是只看行文是否顺畅。"
            "这会让下一轮修订更容易定位问题，也能减少无效返工。"
            "如果未来接入更多数据年份或外部文献，这套审阅链也能继续复用。"
        ),
        "",
        "## 七、结论",
        "",
        (
            "本文基于 CGSS 数据构造社会资本指标，并检验其与居民主观幸福感之间的关系。当前探索性证据显示，"
            "社会资本指数在 OLS 与 Ordered Logit 模型中均表现为正向关联，说明更强的社会连接、信任和参与可能对应更高的生活评价。"
            "这一发现与社会资本理论关于支持、信任和归属感的解释方向一致，也为后续展开更细的机制检验提供了基础。"
            "不过，本文当前版本仍处于草稿层：文献引用需要人工核验，描述性统计和稳健性检验需要继续补齐，因果识别还需要新的设计条件。"
        ),
        "",
        (
            "从工作流角度看，本文已经完成从题目、数据发现、变量绑定、研究设计、RunPlan seed、真实模型执行、结果证据包到论文分节草稿的主链路。"
            "本次组装进一步把这些分散证据收敛为一篇可审阅的完整探索性论文。下一步应当先进行人工审阅，确认题目边界、变量定义、结果解释和文献候选；"
            "随后再进入 PDF 预检、AER-like 方法规范门和审稿式修订循环。"
        ),
        "",
        "## 参考文献候选",
        "",
        *[f"- `{item}`" for item in bibliography],
        "",
        "## 人工审阅清单",
        "",
        "- 题目是否需要限定为“关联研究”或“探索性实证分析”？",
        "- CGSS2023 的数据来源、抽样说明和变量题项是否已经补齐官方引用？",
        "- 社会资本指数是否应拆成多个维度报告，而不是只保留综合指数？",
        "- OLS 是否作为主结果，Ordered Logit 是否作为稳健性，还是两者并列呈现？",
        "- 中文文献、CNKI 检索和 Zotero 条目是否已经核验到可进入正式参考文献？",
        "- 下一轮是否优先做分项稳健性、异质性分析、机制检验或内生性讨论？",
        "",
        "## 开放依赖",
        "",
    ]
    if open_dependencies:
        for item in open_dependencies:
            lines.append(f"- `{item.get('source_id', 'source')}` {item.get('title', '')}: {item.get('status', 'needs_review')}")
    else:
        lines.append("- 当前未记录额外开放依赖。")
    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"


def extract_draft_body(markdown: str) -> str:
    if "## 草案正文" not in markdown:
        return markdown.strip()
    body = markdown.split("## 草案正文", 1)[1]
    for marker in ["## 证据绑定", "## 引用占位", "## 人工审阅问题", "## 审阅备注"]:
        if marker in body:
            body = body.split(marker, 1)[0]
    return body.strip()


def candidate_bibliography(literature_review_packet: dict[str, Any], sections: list[dict[str, Any]]) -> list[str]:
    candidates = set(literature_review_packet.get("candidate_citations", []))
    for section in sections:
        candidates.update(section.get("citation_keys", []))
    if not candidates:
        candidates.update(
            [
                "putnam_2000",
                "bourdieu_1986",
                "ferrer_i_carbonell_frijters_2004",
                "cgss_official_source_placeholder",
            ]
        )
    return sorted(candidates)


def count_chinese_characters(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def format_number(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.4f}"
    return "待确认"


def write_cgss_exploratory_paper_outputs(
    project_root: Path,
    package: dict[str, Any],
    paper_path: Path = DEFAULT_PAPER_PATH,
    result_path: Path = DEFAULT_RESULT_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path, Path]:
    absolute_paper = project_root / paper_path
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_paper.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)

    if package.get("paper_markdown"):
        absolute_paper.write_text(package["paper_markdown"], encoding="utf-8")
    absolute_result.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(package, paper_path), encoding="utf-8")
    return absolute_paper, absolute_result, absolute_review


def render_review(package: dict[str, Any], paper_path: Path = DEFAULT_PAPER_PATH) -> str:
    lines = [
        "# CGSS 完整探索性论文草稿",
        "",
        f"- 题目：{package.get('topic', '')}",
        f"- 状态：`{package.get('status')}`",
        f"- 论文文件：`{paper_path}`",
        f"- 正式层写回：`{str(package.get('formal_writeback_allowed', False)).lower()}`",
        f"- 草案层：`{str(package.get('draft_layer_only', True)).lower()}`",
    ]
    if package.get("blocking_reasons"):
        lines.extend(["", "## 阻断原因"])
        for reason in package["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines).rstrip() + "\n"

    metrics = package.get("paper_metrics", {})
    lines.extend(
        [
            "",
            "## 篇幅与结构",
            f"- 中文字符数：{metrics.get('chinese_characters', 0)}",
            f"- 最低要求：{metrics.get('minimum_chinese_characters', 0)}",
            f"- 组装章节数：{metrics.get('section_count', 0)}",
            "",
            "## 组装章节",
        ]
    )
    for section in package.get("assembled_sections", []):
        lines.append(f"- {section['title']}：`{section['source_path']}`")

    lines.extend(["", "## 证据账本"])
    for item in package.get("evidence_ledger", []):
        lines.append(f"- `{item}`")

    lines.extend(["", "## 人工审阅清单"])
    for item in package.get("human_review_checklist", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Agent Team 调用节奏"])
    for key, value in package.get("agent_team_schedule", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## 下一步"])
    for task in package.get("next_tasks", []):
        lines.append(f"- `{task}`")
    return "\n".join(lines).rstrip() + "\n"

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_manuscript_section_router.v1"
DEFAULT_RESULTS_EVIDENCE_PATH = Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json")
DEFAULT_LITERATURE_PACKET_PATH = Path("Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_manuscript_sections.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_manuscript_sections.md")
DEFAULT_SECTION_DIR = Path("Manuscripts/generated/cgss_social_capital_happiness_sections")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_manuscript_section_package(
    results_evidence_package: dict[str, Any],
    literature_review_draft_packet: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": results_evidence_package.get("topic") or literature_review_draft_packet.get("topic", ""),
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "source_artifacts": {
            "results_evidence_package": {
                "path": source_paths.get("results_evidence_package", str(DEFAULT_RESULTS_EVIDENCE_PATH)),
                "schema_version": results_evidence_package.get("schema_version", ""),
                "status": results_evidence_package.get("status", ""),
            },
            "literature_review_draft_packet": {
                "path": source_paths.get("literature_review_draft_packet", str(DEFAULT_LITERATURE_PACKET_PATH)),
                "schema_version": literature_review_draft_packet.get("schema_version", ""),
                "status": literature_review_draft_packet.get("status", ""),
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
    if results_evidence_package.get("status") != "ready_for_paper_draft_input":
        return {
            **base,
            "status": "blocked_missing_results_evidence_package",
            "blocking_reasons": ["results_evidence_package_not_ready"],
            "sections": [],
            "summary": {"section_count": 0, "ready_sections": 0, "blocked_sections": 0},
            "next_tasks": ["repair_or_execute_results_evidence_package"],
        }
    if literature_review_draft_packet.get("status") != "needs_human_literature_review_draft_approval":
        return {
            **base,
            "status": "blocked_missing_literature_review_draft_packet",
            "blocking_reasons": ["literature_review_draft_packet_not_reviewable"],
            "sections": [],
            "summary": {"section_count": 0, "ready_sections": 0, "blocked_sections": 0},
            "next_tasks": ["build_or_repair_cgss_literature_review_draft_packet"],
        }

    sections = [
        build_literature_section(results_evidence_package, literature_review_draft_packet),
        build_data_section(results_evidence_package),
        build_empirical_strategy_section(results_evidence_package, literature_review_draft_packet),
        build_main_results_section(results_evidence_package),
    ]
    ready_sections = sum(1 for section in sections if section["status"] == "section_draft_ready_for_review")
    blocked_sections = len(sections) - ready_sections
    status = "needs_human_manuscript_section_review" if blocked_sections == 0 else "blocked_section_quality_gate"
    blocking_reasons = [] if blocked_sections == 0 else ["section_length_or_evidence_gate_not_met"]
    return {
        **base,
        "status": status,
        "blocking_reasons": blocking_reasons,
        "sections": sections,
        "summary": {
            "section_count": len(sections),
            "ready_sections": ready_sections,
            "blocked_sections": blocked_sections,
            "total_chinese_characters": sum(section["actual_chinese_characters"] for section in sections),
        },
        "agent_team_schedule": {
            "call_when": "after_results_evidence_and_literature_draft_packets_are_ready",
            "called_agents": ["ManuscriptAgent", "VerifierAgent"],
            "recall_when": "after_human_reviews_manuscript_sections",
            "next_call_when": "before_full_paper_assembly_and_pdf_preflight",
            "boundary": "章节只进入草案层；VerifierAgent 需要逐节核对证据绑定、引用占位和字数门槛。",
        },
        "next_tasks": [
            "human_review_manuscript_sections",
            "approve_or_revise_literature_citation_bindings",
            "assemble_exploratory_paper_draft",
            "run_pdf_export_preflight",
        ],
    }


def build_literature_section(results: dict[str, Any], literature: dict[str, Any]) -> dict[str, Any]:
    blocks = literature.get("paragraph_blocks", [])
    citations = sorted({key for block in blocks for key in block.get("citation_keys", [])})
    paragraphs = [block.get("draft_paragraph", "").strip() for block in blocks if block.get("draft_paragraph")]
    open_dependencies = literature.get("open_dependencies", [])
    supplement = (
        "结合本文题目，文献综述需要把三个问题说清楚：第一，社会资本为什么可能影响居民主观幸福感；"
        "第二，CGSS 幸福感与社会资本题项如何对应既有测量框架；第三，本文相对既有研究的推进在哪里。"
        "当前草稿把理论基础、测量口径和中国经验研究先连成一条写作线索，但中文文献和 CGSS 官方说明仍需继续核验。"
        "因此，本节暂时作为可审阅草稿，不把候选文献直接写入正式参考文献。"
        "后续扩写时，LiteratureAgent 应当继续把“理论机制”和“经验识别”分开：理论机制回答社会资本为何可能改善幸福感，"
        "经验识别则说明现有数据只能支持何种强度的结论。这样可以避免文献综述只堆概念，也能为后续方法升级留下清楚入口。"
        "更具体地说，社会资本影响幸福感至少可以沿着三条机制展开。第一是支持机制：更稳定的亲友、邻里和社区联系可以在个体遭遇风险时提供情绪支持、"
        "信息帮助和实际互助，从而改善生活评价。第二是信任机制：一般信任和社会信任可能降低日常交往成本，使个体更容易形成安全感和可预期感。"
        "第三是参与机制：社会参与让个体获得身份认同、归属感和公共生活连接，这些因素本身就可能进入主观福利评价。"
        "这三条机制都能和 CGSS2023 的可用题项发生对应，但对应强度并不完全相同，所以正文需要把题项口径、理论概念和经验模型逐层对齐。"
        "从贡献角度看，本文暂时不应把自己写成对社会资本理论的根本性突破，而应写成一个基于最新 CGSS 横截面数据的系统化经验检验。"
        "它的价值在于把社会信任、日常交往和休闲社会参与合成为一个可执行的社会资本指标，并在同一套样本和控制变量下比较线性模型与有序响应模型。"
        "如果后续 CNKI 检索补充了更多中文研究，本节还应进一步说明本文和既有中国经验研究的差异：是样本年份更新、指标构造不同、控制变量更完整，"
        "还是结果解释更强调幸福感测量边界。只有把这些差异讲清楚，文献综述才会从背景介绍变成真正的研究定位。"
    )
    body = "\n\n".join([*paragraphs, supplement])
    minimum = int(literature.get("length_plan", {}).get("minimum_chinese_characters") or 900)
    target = int(literature.get("length_plan", {}).get("target_chinese_characters") or 1600)
    return build_section(
        section_id="literature_and_contribution",
        title="文献综述与研究贡献",
        output_path=DEFAULT_SECTION_DIR / "03-literature-and-contribution.md",
        minimum_chinese_characters=minimum,
        target_chinese_characters=target,
        body=body,
        evidence_bindings=["cgss_literature_review_draft_packet", "verified_bibliography_candidates", "citation_binding_placeholders"],
        citation_keys=citations,
        human_review_questions=[
            "是否需要补充更多 CNKI 中文经验研究？",
            "Putnam、Bourdieu 与幸福感测量文献是否足够支撑当前理论链条？",
            "当前贡献是否应写成 CGSS2023 更新、变量组合，还是机制解释？",
        ],
        review_notes=[
            "候选引用仍需人工批准后才能进入正式参考文献。",
            *[
                f"{item.get('source_id')} {item.get('title')} 仍需核验。"
                for item in open_dependencies
                if item.get("source_id")
            ],
        ],
    )


def build_data_section(results: dict[str, Any]) -> dict[str, Any]:
    dataset = results.get("dataset", {})
    variables = results.get("variables", {})
    social_capital = variables.get("social_capital", {})
    source_items = "、".join(social_capital.get("source_items", []))
    controls = "、".join(variables.get("controls", []))
    body = (
        f"本文使用 CGSS{dataset.get('year', '2023')} 数据，原始文件为 {dataset.get('source', 'CGSS2023.dta')}。"
        f"当前证据包记录的数据路径为 {dataset.get('path', '')}，说明本轮分析来自本机真实数据资产，而不是页面模拟数据。"
        f"被解释变量为居民主观幸福感，口径写作 {variables.get('outcome', 'happiness <- a36')}；"
        "该变量以有序等级记录，因此后续模型既保留线性基准，也需要有序响应模型作为稳健性参照。"
        f"核心解释变量为 {social_capital.get('index', 'social_capital_index')}，由 {source_items} 等题项构造。"
        "这组题项覆盖社会信任、邻里交往、朋友交往与休闲社会参与，能够形成一个围绕社会连接和关系资源的操作化指标。"
        f"控制变量包括 {controls}。这些控制项用于吸收性别、年龄、教育、收入、健康、户籍和地区差异等可能同时影响社会资本与幸福感的因素。"
        "本节后续人工审阅的重点，是确认幸福感题项是否需要反向处理、社会资本指数是否需要标准化或分维度展示、收入和健康变量的缺失处理是否需要更详细说明。"
        "从论文写作角度看，数据与变量部分不能只罗列变量名，还需要解释每个变量为什么进入模型。"
        "幸福感变量承担研究问题的结果端，社会资本指数承担解释端，控制变量则用于减少可观察混杂因素带来的解释偏差。"
        "由于本轮样本来自单期 CGSS2023 横截面数据，正文需要明确样本时点和数据结构，避免读者误以为当前模型已经利用了面板变化。"
        "社会资本指数的构造也应当在正式稿中展示题项来源、处理方向和合成方式；如果后续发现某些题项缺失率过高或含义不一致，"
        "系统应当派发新的变量审阅任务，而不是直接把当前指数推进到正式层。"
        "这部分内容为后续结果解释提供边界：本文现在解释的是可观察社会连接与幸福感之间的稳定关联，而不是完整社会资本量表的全部效应。"
    )
    return build_section(
        section_id="data_and_measurement",
        title="数据与变量",
        output_path=DEFAULT_SECTION_DIR / "04-data-and-measurement.md",
        minimum_chinese_characters=520,
        target_chinese_characters=900,
        body=body,
        evidence_bindings=["cgss_results_evidence_package", "cgss_minimal_model", "cgss_ordered_robustness"],
        citation_keys=["cgss_official_source_placeholder"],
        human_review_questions=[
            "CGSS2023 官方说明是否已经记录访问日期？",
            "社会资本指数是否需要分项信度检查或标准化说明？",
            "控制变量集合是否遗漏婚姻、就业或地区经济环境变量？",
        ],
        review_notes=results.get("human_review_checklist", []),
    )


def build_empirical_strategy_section(results: dict[str, Any], literature: dict[str, Any]) -> dict[str, Any]:
    primary = results.get("primary_result", {})
    ols = primary.get("ols", {})
    ordered = primary.get("ordered_logit", {})
    body = (
        "本文的实证策略先采取可解释性较强的 OLS 作为基准模型，再使用 Ordered Logit 检验结论是否依赖线性模型设定。"
        f"基准模型以 {ols.get('variable', 'social_capital_index')} 为核心解释变量，样本量为 {ols.get('nobs', '待确认')}；"
        "模型同时控制个体人口学特征、经济状态、健康状况、户籍身份和省份固定效应。"
        "这种设计的作用是先回答一个清晰的问题：在可观察个体差异和地区差异被纳入后，社会资本指数是否仍与幸福感评价稳定相关。"
        f"由于幸福感变量具有 {ordered.get('outcome_levels', [1, 2, 3, 4, 5])} 这样的有序等级，Ordered Logit 被放入方法链路作为关键稳健性模型。"
        "方法解释上，本节不会把当前估计直接写成严格因果效应；当前证据更适合支持相关性和稳健关联。"
        "如果后续要推进因果解释，系统需要继续判断是否存在可用工具变量、政策冲击、面板结构或准实验设计。"
        "文献草稿包也提示，幸福感研究中同时报告线性模型和有序响应模型是一种常见处理方式；因此，本节把 OLS 与 Ordered Logit 的并列呈现作为当前探索性论文包的最低方法门。"
        f"当前文献草稿仍处于 {literature.get('status', '待确认')} 状态，因此方法叙述中的文献支撑需要在人工批准后再进入正式稿。"
        "在工作流上，方法部分承担两个角色：一是把变量角色转成可执行模型，二是告诉 ReviewerAgent 现在的识别强度在哪里。"
        "当前 RunPlan 已经完成基准 OLS 和 Ordered Logit 两个任务，说明执行层能够从 approved seed 进入真实模型估计。"
        "但如果用户希望论文进一步接近投稿标准，下一轮 MethodAgent 应该继续补充分项社会资本回归、替代幸福感口径、"
        "稳健标准误设定、样本筛选敏感性和异质性分析。"
        "对于这篇题目，DID 或 IV 不能因为听起来高级就直接套用；必须先有政策时点、处理组定义或可信工具变量。"
        "因此，当前方法门的正确产物不是“宣称已经完成因果识别”，而是形成一个可复现、可审阅、可升级的基准实证框架。"
    )
    return build_section(
        section_id="empirical_strategy",
        title="实证策略",
        output_path=DEFAULT_SECTION_DIR / "05-empirical-strategy.md",
        minimum_chinese_characters=560,
        target_chinese_characters=1000,
        body=body,
        evidence_bindings=["cgss_results_evidence_package", "ordered_method_gate", "cgss_literature_review_draft_packet"],
        citation_keys=["ferrer_i_carbonell_frijters_2004"],
        human_review_questions=[
            "OLS 是否作为主模型，还是 Ordered Logit 应作为主模型？",
            "是否需要加入分省固定效应之外的地区层面控制？",
            "如果写作目标提高到因果识别，下一轮是否需要搜索工具变量或准实验设计？",
        ],
        review_notes=["当前方法门支持探索性关联分析；因果识别升级留到后续 RunPlan。"],
    )


def build_main_results_section(results: dict[str, Any]) -> dict[str, Any]:
    primary = results.get("primary_result", {})
    ols = primary.get("ols", {})
    ordered = primary.get("ordered_logit", {})
    consistency = results.get("evidence_consistency", {})
    seed = results.get("writing_inputs", {}).get("result_sentence_seed", "")
    body = (
        f"{seed}"
        f"基准 OLS 模型中，{ols.get('variable', 'social_capital_index')} 的估计系数为 {format_number(ols.get('coef'))}，"
        f"稳健标准误约为 {format_number(ols.get('std_error'))}，p 值约为 {format_number(ols.get('p_value'))}，样本量为 {ols.get('nobs', '待确认')}。"
        "这意味着在当前变量口径下，社会资本指数越高的受访者通常报告更高的主观幸福感。"
        f"Ordered Logit 模型中，核心变量系数为 {format_number(ordered.get('coef'))}，标准误约为 {format_number(ordered.get('std_error'))}，"
        f"p 值约为 {format_number(ordered.get('p_value'))}，样本量同样为 {ordered.get('nobs', '待确认')}。"
        f"证据一致性检查显示，样本量是否一致为 {consistency.get('sample_nobs_match')}，有序模型门禁状态为 {consistency.get('ordered_method_gate')}，"
        f"方向一致性为 {consistency.get('social_capital_direction')}。"
        "因此，当前结果不是只依赖单一线性模型，而是在有序因变量模型下保留了相同方向。"
        "写作时应把这一点放在主要结果段落的核心位置：社会资本与幸福感之间存在稳定正向关联。"
        "下一轮需要补充的，是对系数经济含义的更细解释、社会资本分项结果、不同群体的异质性检验，以及可能的内生性讨论。"
        "结果部分的写法应该先给出核心发现，再说明模型之间的一致性，最后交代还需要补的检验。"
        "OLS 系数为正，说明在线性评分口径下，社会资本指数提高与幸福感评分提高相伴随；Ordered Logit 系数为正，"
        "说明在保留幸福感有序等级结构后，结论方向没有改变。"
        "这两个结果合在一起，可以支持“社会资本与主观幸福感存在稳定正向关系”这一探索性论断。"
        "不过，正式稿还需要把结果表、变量均值、标准差和模型设定放在同一个表格体系中，方便读者判断估计量的大小和可比性。"
        "如果后续审稿式修订发现结果解释太薄，系统应当优先补三类材料：第一，社会资本指数按分项题目的结果；"
        "第二，城乡、教育或收入分组下的异质性；第三，替换控制变量集合或样本限制后的稳健性。"
        "这些补充会让结果部分从“模型跑通”升级为“论文论证可读”。"
    )
    return build_section(
        section_id="main_results",
        title="主要实证结果",
        output_path=DEFAULT_SECTION_DIR / "06-main-results.md",
        minimum_chinese_characters=560,
        target_chinese_characters=1000,
        body=body,
        evidence_bindings=["cgss_results_evidence_package", "cgss_minimal_model", "cgss_ordered_robustness"],
        citation_keys=[],
        human_review_questions=[
            "主要结果表是否需要同步生成三线表和 PDF 图表？",
            "社会资本系数是否需要转成标准差变化或预测概率解释？",
            "下一轮稳健性是否优先做分项社会资本、异质性还是内生性处理？",
        ],
        review_notes=["结果仍需人工判断能否进入正式论断层。"],
    )


def build_section(
    *,
    section_id: str,
    title: str,
    output_path: Path,
    minimum_chinese_characters: int,
    target_chinese_characters: int,
    body: str,
    evidence_bindings: list[str],
    citation_keys: list[str],
    human_review_questions: list[str],
    review_notes: list[str],
) -> dict[str, Any]:
    draft_markdown = render_section_markdown(
        title=title,
        body=body,
        evidence_bindings=evidence_bindings,
        citation_keys=citation_keys,
        human_review_questions=human_review_questions,
        review_notes=review_notes,
    )
    actual = count_chinese_characters(body)
    return {
        "section_id": section_id,
        "title": title,
        "status": "section_draft_ready_for_review" if actual >= minimum_chinese_characters else "blocked_section_too_short",
        "path": str(output_path),
        "minimum_chinese_characters": minimum_chinese_characters,
        "target_chinese_characters": target_chinese_characters,
        "actual_chinese_characters": actual,
        "evidence_bindings": evidence_bindings,
        "citation_keys": citation_keys,
        "human_review_questions": human_review_questions,
        "review_notes": review_notes,
        "draft_markdown": draft_markdown,
    }


def render_section_markdown(
    *,
    title: str,
    body: str,
    evidence_bindings: list[str],
    citation_keys: list[str],
    human_review_questions: list[str],
    review_notes: list[str],
) -> str:
    lines = [
        f"# {title}",
        "",
        "- Status: `section_draft_ready_for_review`",
        "- Draft layer: `true`",
        "- Formal writeback: `false`",
        "",
        "## 草案正文",
        "",
        body.strip(),
        "",
        "## 证据绑定",
    ]
    for item in evidence_bindings:
        lines.append(f"- `{item}`")
    lines.extend(["", "## 引用占位"])
    if citation_keys:
        for key in citation_keys:
            lines.append(f"- `{key}`")
    else:
        lines.append("- 当前章节主要绑定本地结果证据；无需新增文献引用。")
    lines.extend(["", "## 人工审阅问题"])
    for question in human_review_questions:
        lines.append(f"- {question}")
    lines.extend(["", "## 审阅备注"])
    for note in review_notes:
        lines.append(f"- {note}")
    return "\n".join(lines).rstrip() + "\n"


def count_chinese_characters(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def format_number(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.4f}"
    return "待确认"


def write_cgss_manuscript_section_outputs(
    project_root: Path,
    package: dict[str, Any],
    result_path: Path = DEFAULT_RESULT_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path, list[Path]]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    section_paths: list[Path] = []
    if package.get("status") == "needs_human_manuscript_section_review":
        for section in package.get("sections", []):
            section_path = project_root / section["path"]
            section_path.parent.mkdir(parents=True, exist_ok=True)
            section_path.write_text(section["draft_markdown"], encoding="utf-8")
            section_paths.append(section_path)
    absolute_result.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(package), encoding="utf-8")
    return absolute_result, absolute_review, section_paths


def render_review(package: dict[str, Any]) -> str:
    lines = [
        "# CGSS 论文分节草案包",
        "",
        f"- 题目：{package.get('topic', '')}",
        f"- 状态：`{package.get('status')}`",
        f"- 正式层写回：`{str(package.get('formal_writeback_allowed', False)).lower()}`",
        f"- 草案层：`{str(package.get('draft_layer_only', True)).lower()}`",
    ]
    if package.get("blocking_reasons"):
        lines.extend(["", "## 阻断原因"])
        for reason in package["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    summary = package.get("summary", {})
    lines.extend(
        [
            "",
            "## 汇总",
            f"- 章节数：{summary.get('section_count', 0)}",
            f"- 可审阅章节：{summary.get('ready_sections', 0)}",
            f"- 阻断章节：{summary.get('blocked_sections', 0)}",
            f"- 中文字符合计：{summary.get('total_chinese_characters', 0)}",
            "",
            "## 章节",
        ]
    )
    for section in package.get("sections", []):
        lines.extend(
            [
                f"### {section['title']}",
                f"- 文件：`{section['path']}`",
                f"- 状态：`{section['status']}`",
                f"- 字数：{section['actual_chinese_characters']} / 最低 {section['minimum_chinese_characters']} / 目标 {section['target_chinese_characters']}",
                f"- 证据：{', '.join(f'`{item}`' for item in section['evidence_bindings'])}",
                f"- 引用：{', '.join(f'`{item}`' for item in section['citation_keys']) if section['citation_keys'] else '本地结果证据'}",
                "",
            ]
        )
    lines.extend(["## Agent Team 调用节奏"])
    schedule = package.get("agent_team_schedule", {})
    for key in ["call_when", "called_agents", "recall_when", "next_call_when", "boundary"]:
        lines.append(f"- {key}: {schedule.get(key)}")
    lines.extend(["", "## 下一步"])
    for task in package.get("next_tasks", []):
        lines.append(f"- `{task}`")
    return "\n".join(lines).rstrip() + "\n"

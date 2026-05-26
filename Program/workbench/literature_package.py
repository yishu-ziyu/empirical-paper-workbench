from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p4.literature_package.v1"
PROTECTED_FORMAL_PATHS = [
    "state/product/research_question.json",
    "state/product/variable_roles.json",
    "state/product/design_spec.json",
    "state/product/run_plan.json",
]

CSV_FIELDS = [
    "source_id",
    "citation_key",
    "title",
    "authors",
    "year",
    "venue",
    "volume_issue_pages",
    "doi",
    "publisher_url",
    "working_paper_url",
    "cnki_url",
    "google_scholar_url",
    "openalex_id",
    "semantic_scholar_id",
    "zotero_key",
    "pdf_hash",
    "acquisition_source",
    "verification_status",
    "verification_notes",
    "topic_relevance",
    "method_relevance",
    "data_relevance",
    "contribution_role",
    "used_in_section",
]


def build_literature_package(project_root: Path) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, str]], str]:
    research_question = read_json(project_root / "state" / "product" / "research_question.json")
    design_spec = read_json(project_root / "state" / "product" / "design_spec.json")
    run_plan = read_json(project_root / "state" / "product" / "run_plan.json")
    reconciliation = read_json(project_root / "state" / "proposals" / "variable_role_reconciliation.json")

    seed_rows = seed_robot_labor_literature()
    candidate_rows = enrich_rows(seed_rows)
    verified_rows = [
        row for row in candidate_rows if row["verification_status"] != "needs_manual_review"
    ]
    matrix_md = build_contribution_matrix(candidate_rows)

    report = {
        "schema_version": SCHEMA_VERSION,
        "package_id": f"p4c_literature_package_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "needs_human_review",
        "evidence_level": "official_source_seed_plus_manual_cnki_queue",
        "write_policy": {
            "mode": "processed_evidence_only",
            "does_not_modify": PROTECTED_FORMAL_PATHS,
            "requires_human_review_before_manuscript_citation_writeback": True,
        },
        "formal_state_inputs": {
            "research_question": summarize_state_input(
                research_question,
                "state/product/research_question.json",
                ["version", "status", "question", "evidence_level"],
            ),
            "design_spec": summarize_state_input(
                design_spec,
                "state/product/design_spec.json",
                ["version", "status", "dataset_path", "variables", "identification_strategy"],
            ),
            "run_plan": summarize_state_input(
                run_plan,
                "state/product/run_plan.json",
                ["version", "status", "dataset_path", "tasks"],
            ),
            "variable_role_reconciliation": summarize_state_input(
                reconciliation,
                "state/proposals/variable_role_reconciliation.json",
                ["status", "recommended_variable_roles", "detected_conflicts"],
            ),
        },
        "outputs": {
            "candidate_literature": "Data/literature/processed/candidate_literature.csv",
            "verified_bibliography": "Data/literature/processed/verified_bibliography.csv",
            "contribution_matrix": "Data/literature/processed/contribution_matrix.md",
        },
        "counts": {
            "candidate_count": len(candidate_rows),
            "verified_count": len(verified_rows),
            "closest_or_method_count": len(
                [
                    row
                    for row in verified_rows
                    if row["contribution_role"] in {"closest_paper", "method_reference"}
                ]
            ),
        },
        "verification_channels": [
            "publisher_url",
            "doi",
            "working_paper_url",
            "cnki_manual_queue",
            "zotero_manual_import",
        ],
        "cnki_manual_queue": build_cnki_manual_queue(research_question, design_spec),
        "missing_evidence": build_missing_evidence(),
        "agent_team_schedule": {
            "call_when": "after_candidate_literature_written",
            "recall_when": "before_manuscript_citation_writeback",
            "integration_owner": "main_codex_thread",
            "parallel_lanes": [
                {
                    "agent": "LiteratureAgent",
                    "task": "核验 DOI、期刊页、Zotero key、中文核心文献和引用格式。",
                    "output": "verified_bibliography_patch",
                },
                {
                    "agent": "MethodAgent",
                    "task": "核验文献是否覆盖 shift-share/Bartik、任务模型、IV 风险和本研究识别门。",
                    "output": "method_literature_gap_patch",
                },
                {
                    "agent": "DataAgent",
                    "task": "核验文献中的机器人变量、样本、时间跨度和本项目 CFPS/机器人数据字段是否可映射。",
                    "output": "data_literature_mapping_patch",
                },
            ],
            "next_call_after_integration": "after_cnki_and_zotero_manual_review",
            "boundary": "Agent Team 只补证据包和 processed 文献文件，不直接写正式论文层或 state/product。",
        },
        "recommended_next_tasks": [
            "run_cnki_manual_search",
            "import_verified_sources_to_zotero",
            "review_contribution_matrix",
            "bind_literature_package_to_manuscript_sections",
        ],
    }
    return report, candidate_rows, verified_rows, matrix_md


def seed_robot_labor_literature() -> list[dict[str, str]]:
    return [
        {
            "source_id": "robot_wage_closest_us",
            "citation_key": "acemoglu_restrepo_robots_jobs_2020",
            "title": "Robots and Jobs: Evidence from US Labor Markets",
            "authors": "Acemoglu, Daron; Restrepo, Pascual",
            "year": "2020",
            "venue": "Journal of Political Economy",
            "volume_issue_pages": "128(6):2188-2244",
            "doi": "10.1086/705716",
            "publisher_url": "https://www.journals.uchicago.edu/doi/10.1086/705716",
            "working_paper_url": "https://www.nber.org/papers/w23285",
            "verification_status": "doi_verified",
            "verification_notes": "Official DOI and NBER working paper page identify JPE publication.",
            "topic_relevance": "industrial robot exposure and local labor market wages/employment",
            "method_relevance": "local labor market shift-share robot exposure",
            "data_relevance": "IFR robot data linked to local labor markets",
            "contribution_role": "closest_paper",
            "used_in_section": "Literature and Contribution; Empirical Strategy",
        },
        {
            "source_id": "robot_data_restat_anchor",
            "citation_key": "graetz_michaels_robots_work_2018",
            "title": "Robots at Work",
            "authors": "Graetz, Georg; Michaels, Guy",
            "year": "2018",
            "venue": "Review of Economics and Statistics",
            "volume_issue_pages": "100(5):753-768",
            "doi": "10.1162/rest_a_00754",
            "publisher_url": "https://direct.mit.edu/rest/article/100/5/753/58489/Robots-at-Work",
            "working_paper_url": "",
            "verification_status": "doi_verified",
            "verification_notes": "MIT Press journal page confirms DOI, title and page range.",
            "topic_relevance": "industrial robot adoption and productivity/labor outcomes",
            "method_relevance": "country-industry panel robot use",
            "data_relevance": "IFR country-industry robot use",
            "contribution_role": "data_reference",
            "used_in_section": "Data and Measurement; Literature and Contribution",
        },
        {
            "source_id": "robot_adjustment_germany",
            "citation_key": "dauth_findeisen_suedekum_woessner_2021",
            "title": "The Adjustment of Labor Markets to Robots",
            "authors": "Dauth, Wolfgang; Findeisen, Sebastian; Suedekum, Jens; Woessner, Nicole",
            "year": "2021",
            "venue": "Journal of the European Economic Association",
            "volume_issue_pages": "19(6):3104-3153",
            "doi": "10.1093/jeea/jvab012",
            "publisher_url": "https://academic.oup.com/jeea/article/19/6/3104/6179884",
            "working_paper_url": "",
            "verification_status": "doi_verified",
            "verification_notes": "Oxford Academic page confirms DOI, venue and robot labor market adjustment design.",
            "topic_relevance": "robot exposure and labor market adjustment",
            "method_relevance": "predicted shift-share robot exposure",
            "data_relevance": "German administrative local labor market data",
            "contribution_role": "closest_paper",
            "used_in_section": "Literature and Contribution; Robustness / Mechanisms / Heterogeneity",
        },
        {
            "source_id": "polarization_aer_anchor",
            "citation_key": "autor_dorn_service_jobs_2013",
            "title": "The Growth of Low-Skill Service Jobs and the Polarization of the US Labor Market",
            "authors": "Autor, David H.; Dorn, David",
            "year": "2013",
            "venue": "American Economic Review",
            "volume_issue_pages": "103(5):1553-1597",
            "doi": "10.1257/aer.103.5.1553",
            "publisher_url": "https://www.aeaweb.org/articles?id=10.1257/aer.103.5.1553",
            "working_paper_url": "",
            "verification_status": "doi_verified",
            "verification_notes": "AEA article page confirms DOI and AER publication.",
            "topic_relevance": "employment and wage polarization",
            "method_relevance": "local labor markets and routine-task specialization",
            "data_relevance": "US commuting zones and occupational task content",
            "contribution_role": "method_reference",
            "used_in_section": "Literature and Contribution; Institutional Background / Theory / Context",
        },
        {
            "source_id": "task_theory_handbook",
            "citation_key": "acemoglu_autor_tasks_2011",
            "title": "Skills, Tasks and Technologies: Implications for Employment and Earnings",
            "authors": "Acemoglu, Daron; Autor, David",
            "year": "2011",
            "venue": "Handbook of Labor Economics",
            "volume_issue_pages": "4B:1043-1171",
            "doi": "10.1016/S0169-7218(11)02410-5",
            "publisher_url": "https://www.sciencedirect.com/science/article/pii/S0169721811024105",
            "working_paper_url": "",
            "verification_status": "doi_verified",
            "verification_notes": "ScienceDirect page confirms Handbook chapter and DOI.",
            "topic_relevance": "task-based labor market framework",
            "method_relevance": "theoretical framework for skills/tasks/technology",
            "data_relevance": "guides variable grouping by tasks and skills",
            "contribution_role": "method_reference",
            "used_in_section": "Institutional Background / Theory / Context; Empirical Strategy",
        },
        {
            "source_id": "automation_task_aer_model",
            "citation_key": "acemoglu_restrepo_race_2018",
            "title": "The Race between Man and Machine: Implications of Technology for Growth, Factor Shares, and Employment",
            "authors": "Acemoglu, Daron; Restrepo, Pascual",
            "year": "2018",
            "venue": "American Economic Review",
            "volume_issue_pages": "108(6):1488-1542",
            "doi": "10.1257/aer.20160696",
            "publisher_url": "https://www.aeaweb.org/articles?id=10.1257/aer.20160696",
            "working_paper_url": "",
            "verification_status": "doi_verified",
            "verification_notes": "AEA article page confirms DOI and automation/new task framework.",
            "topic_relevance": "automation, new tasks, employment and labor share",
            "method_relevance": "displacement and reinstatement task model",
            "data_relevance": "conceptual mapping for treatment mechanism",
            "contribution_role": "method_reference",
            "used_in_section": "Institutional Background / Theory / Context; Empirical Strategy",
        },
        {
            "source_id": "wage_inequality_task_displacement",
            "citation_key": "acemoglu_restrepo_tasks_wage_inequality_2022",
            "title": "Tasks, Automation, and the Rise in U.S. Wage Inequality",
            "authors": "Acemoglu, Daron; Restrepo, Pascual",
            "year": "2022",
            "venue": "Econometrica",
            "volume_issue_pages": "90(5)",
            "doi": "10.3982/ECTA19815",
            "publisher_url": "https://www.econometricsociety.org/publications/econometrica/2022/09/01/Tasks-Automation-and-the-Rise-in-US-Wage-Inequality",
            "working_paper_url": "",
            "verification_status": "doi_verified",
            "verification_notes": "Econometric Society publication page confirms DOI and task displacement focus.",
            "topic_relevance": "automation and wage inequality",
            "method_relevance": "task displacement accounting",
            "data_relevance": "wage structure and education wage differential framework",
            "contribution_role": "review_source",
            "used_in_section": "Literature and Contribution; Main Results",
        },
        {
            "source_id": "firm_robot_adoption_spillover",
            "citation_key": "acemoglu_lelarge_restrepo_competing_2020",
            "title": "Competing with Robots: Firm-Level Evidence from France",
            "authors": "Acemoglu, Daron; Lelarge, Claire; Restrepo, Pascual",
            "year": "2020",
            "venue": "AEA Papers and Proceedings",
            "volume_issue_pages": "110:383-388",
            "doi": "10.1257/pandp.20201003",
            "publisher_url": "https://www.aeaweb.org/articles?id=10.1257/pandp.20201003",
            "working_paper_url": "https://www.nber.org/papers/w26738",
            "verification_status": "doi_verified",
            "verification_notes": "AEA and NBER pages identify firm-level robot adoption evidence.",
            "topic_relevance": "firm robot adoption, employment and labor share",
            "method_relevance": "firm-level adoption and industry spillover comparison",
            "data_relevance": "firm-level robot adoption measures",
            "contribution_role": "contrasting_result",
            "used_in_section": "Literature and Contribution; Robustness / Mechanisms / Heterogeneity",
        },
        {
            "source_id": "shift_share_method_core",
            "citation_key": "goldsmith_pinkham_sorkin_swift_bartik_2020",
            "title": "Bartik Instruments: What, When, Why, and How",
            "authors": "Goldsmith-Pinkham, Paul; Sorkin, Isaac; Swift, Henry",
            "year": "2020",
            "venue": "American Economic Review",
            "volume_issue_pages": "110(8):2586-2624",
            "doi": "10.1257/aer.20181047",
            "publisher_url": "https://www.aeaweb.org/articles?id=10.1257/aer.20181047",
            "working_paper_url": "",
            "verification_status": "doi_verified",
            "verification_notes": "AEA article page is the method anchor for Bartik/shift-share instrument diagnostics.",
            "topic_relevance": "Bartik and shift-share identification for local exposure designs",
            "method_relevance": "instrument relevance, identifying variation and exogeneity diagnostics",
            "data_relevance": "share construction and shock-share decomposition",
            "contribution_role": "method_reference",
            "used_in_section": "Empirical Strategy; Robustness / Mechanisms / Heterogeneity",
        },
    ]


def enrich_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    for row in rows:
        full = {field: "" for field in CSV_FIELDS}
        full.update(row)
        full["acquisition_source"] = "official_source_seed"
        full["google_scholar_url"] = build_google_scholar_url(row["title"])
        full["cnki_url"] = ""
        full["openalex_id"] = ""
        full["semantic_scholar_id"] = ""
        full["zotero_key"] = ""
        full["pdf_hash"] = ""
        enriched.append(full)
    return enriched


def build_google_scholar_url(title: str) -> str:
    return "https://scholar.google.com/scholar?q=" + "+".join(title.split())


def build_contribution_matrix(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Contribution Matrix",
        "",
        "| source_id | citation_key | contribution_role | used_in_section | variables_or_method_evidence | difference_from_this_paper | verification_status |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        difference = contribution_difference(row["source_id"])
        evidence = "; ".join(
            item
            for item in [row["topic_relevance"], row["method_relevance"], row["data_relevance"]]
            if item
        )
        lines.append(
            "| {source_id} | {citation_key} | {contribution_role} | {used_in_section} | {evidence} | {difference} | {verification_status} |".format(
                source_id=row["source_id"],
                citation_key=row["citation_key"],
                contribution_role=row["contribution_role"],
                used_in_section=row["used_in_section"],
                evidence=evidence.replace("|", "/"),
                difference=difference.replace("|", "/"),
                verification_status=row["verification_status"],
            )
        )
    lines.append("")
    lines.append("## 使用边界")
    lines.append("")
    lines.append("- 这些文献进入的是 processed evidence 层，正式正文引用前需要人工确认 Zotero key、CNKI 中文补证和引用格式。")
    lines.append("- “机器人采用”和“机器人暴露”不能混用；企业采用、行业机器人密度和地区暴露必须在正文里分开定义。")
    return "\n".join(lines)


def contribution_difference(source_id: str) -> str:
    differences = {
        "robot_wage_closest_us": "美国 commuting-zone 机器人暴露；本研究用 CFPS 个体数据和中国语境重新映射工资结果。",
        "robot_data_restat_anchor": "国家-行业面板生产率/就业；本研究需要说明机器人变量与个体工资之间的连接。",
        "robot_adjustment_germany": "德国行政数据和本地劳动市场调整；本研究用于对照中国劳动力市场机制。",
        "polarization_aer_anchor": "自动化任务极化框架；本研究只在机制/异质性中借鉴，不直接复制设定。",
        "task_theory_handbook": "理论框架，不是实证识别模板；用于定义技能、任务和技术冲击。",
        "automation_task_aer_model": "宏观任务模型；用于解释位移效应和新任务效应。",
        "wage_inequality_task_displacement": "美国工资不平等解释；本研究聚焦中国个体工资和机器人暴露。",
        "firm_robot_adoption_spillover": "企业采用和竞争外溢；本研究当前主链路是地区/个体暴露，不直接等同企业采用。",
    }
    return differences.get(source_id, "待人工补充与本研究的具体差异。")


def build_cnki_manual_queue(research_question: dict[str, Any], design_spec: dict[str, Any]) -> list[dict[str, Any]]:
    question = research_question.get("question") or "工业机器人应用对劳动力市场匹配效率的影响"
    strategy = ((design_spec.get("identification_strategy") or {}).get("name") or "bartik_iv_2sls")
    return [
        {
            "query": "工业机器人 AND 就业",
            "purpose": "寻找中国语境下工业机器人影响就业结构的核心中文文献。",
            "record_fields": ["题名", "作者", "期刊", "年份", "数据来源", "核心解释变量", "被解释变量", "方法"],
        },
        {
            "query": "工业机器人 AND 工资",
            "purpose": "寻找与 ln_wage / 工资回报相关的中文证据。",
            "record_fields": ["题名", "作者", "期刊", "年份", "工资指标", "控制变量", "机制解释"],
        },
        {
            "query": "工业机器人 AND 劳动力市场匹配",
            "purpose": f"核验研究问题“{question}”是否已有本土文献直接讨论。",
            "record_fields": ["题名", "作者", "期刊", "年份", "匹配效率指标", "样本", "识别策略"],
        },
        {
            "query": "机器人渗透度 AND 劳动力市场",
            "purpose": "核验机器人密度/渗透度变量在中文文献中的构造方式。",
            "record_fields": ["题名", "作者", "期刊", "年份", "机器人变量", "数据来源", "IFR 是否使用"],
        },
        {
            "query": f"机器人 AND {strategy}",
            "purpose": "寻找中文文献中与当前识别策略相近的经验做法。",
            "record_fields": ["题名", "作者", "期刊", "年份", "工具变量", "Bartik 或 shift-share 设定", "稳健性"],
        },
    ]


def build_missing_evidence() -> list[dict[str, str]]:
    return [
        {
            "id": "cnki_china_context_not_verified",
            "severity": "medium",
            "next_step": "用 CNKI 人工辅助检索补齐中国本土核心文献和中文引用格式。",
        },
        {
            "id": "zotero_keys_missing",
            "severity": "medium",
            "next_step": "将英文核心文献导入 Zotero，并把 zotero_key 写回 verified_bibliography.csv。",
        },
        {
            "id": "full_text_pdf_hash_missing",
            "severity": "low",
            "next_step": "对本地 PDF 做 hash，形成可复查的 PDF 证据链。",
        },
    ]


def write_literature_package(
    project_root: Path,
    report: dict[str, Any],
    candidate_rows: list[dict[str, str]],
    verified_rows: list[dict[str, str]],
    matrix_md: str,
    output_dir: Path | None = None,
    report_path: Path | None = None,
) -> dict[str, Path]:
    processed = output_dir or (project_root / "Data" / "literature" / "processed")
    processed.mkdir(parents=True, exist_ok=True)
    paths = {
        "candidate_literature": processed / "candidate_literature.csv",
        "verified_bibliography": processed / "verified_bibliography.csv",
        "contribution_matrix": processed / "contribution_matrix.md",
        "literature_package_report": report_path or (project_root / "Results" / "json" / "literature_package_report.json"),
    }
    write_csv(paths["candidate_literature"], candidate_rows)
    write_csv(paths["verified_bibliography"], verified_rows)
    paths["contribution_matrix"].write_text(matrix_md, encoding="utf-8")
    paths["literature_package_report"].parent.mkdir(parents=True, exist_ok=True)
    paths["literature_package_report"].write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return paths


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_state_input(payload: dict[str, Any], path: str, keys: list[str]) -> dict[str, Any]:
    return {
        "path": path,
        "exists": bool(payload),
        "summary": {key: payload.get(key) for key in keys if key in payload},
    }

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.literature_discovery_seed.v1"
DEFAULT_DATASET_INDEX_PATH = Path("Results/json/dataset_motherlode_index.json")
DEFAULT_REPORT_PATH = Path("Results/json/literature_discovery_seed.json")
DEFAULT_REVIEW_PATH = Path("Reviews/literature_discovery_seed.md")

BIBLIOGRAPHY_STATES = [
    "candidate",
    "metadata_verified",
    "fulltext_located",
    "source_span_extracted",
    "citation_use_proposed",
    "needs_human_review",
    "approved_for_project_bibliography",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_literature_discovery_seed(
    topic: str,
    dataset_index: dict[str, Any] | None = None,
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    dataset_context_terms = derive_dataset_context_terms(dataset_index or {})
    query_plan = build_query_plan(topic, dataset_context_terms)
    source_registry = build_source_registry()
    candidate_records = build_candidate_search_records(query_plan["search_queries"])
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "status": "needs_human_literature_discovery_review",
        "source_artifacts": {
            "dataset_motherlode_index": {
                "path": source_paths.get("dataset_index", str(DEFAULT_DATASET_INDEX_PATH)),
                "schema_version": (dataset_index or {}).get("schema_version", ""),
                "status": (dataset_index or {}).get("status", "not_provided"),
            }
        },
        "query_plan": query_plan,
        "source_registry": source_registry,
        "candidate_search_records": candidate_records,
        "bibliography_state_model": {
            "states": BIBLIOGRAPHY_STATES,
            "claim_use_rule": "candidate records cannot support substantive paper claims until source spans are extracted and human review approves project bibliography use.",
            "promotion_required_state": "approved_for_project_bibliography",
        },
        "promotion": {
            "allowed": False,
            "required_decision": "human_approve_literature_discovery_seed",
            "would_write_if_approved": [
                "Results/json/literature_metadata_search_results.json",
                "Results/json/project_bibliography_candidates.json",
                "Reviews/literature_discovery_execution_queue.md",
            ],
        },
        "boundary_flags": {
            "modified_formal_bibliography": False,
            "modified_formal_manuscript": False,
            "modified_project_bibliography": False,
            "downloaded_fulltext": False,
            "wrote_state_product": False,
        },
        "next_tasks": [
            "run_literature_metadata_search",
            "dedupe_literature_candidates",
            "locate_available_fulltext",
            "extract_source_spans_for_used_claims",
            "human_review_project_bibliography_candidates",
        ],
    }


def build_query_plan(topic: str, dataset_context_terms: list[str]) -> dict[str, Any]:
    concepts = detect_topic_concepts(topic)
    queries = build_search_queries(topic, dataset_context_terms)
    return {
        "topic": topic,
        "concepts": concepts,
        "dataset_context_terms": dataset_context_terms,
        "search_queries": queries,
        "query_policy": {
            "goal": "maximize_literature_discovery_and_available_fulltext",
            "metadata_first": True,
            "used_claims_require_source_spans": True,
        },
    }


def detect_topic_concepts(topic: str) -> dict[str, list[str]]:
    topic_lower = topic.lower()
    exposure_terms = ["核心解释变量"]
    outcome_terms = ["被解释变量"]
    method_context = ["empirical economics", "labor economics"]
    if "机器人" in topic or "robot" in topic_lower:
        exposure_terms = ["工业机器人", "机器人", "industrial robots", "robot adoption", "automation", "IFR"]
    if any(term in topic for term in ["劳动力", "劳动", "就业", "匹配"]):
        outcome_terms = ["劳动力市场匹配效率", "就业匹配", "劳动力配置效率", "labor market matching", "matching efficiency"]
        method_context.extend(["matching function", "employment", "wages", "microdata"])
    return {
        "exposure_terms": exposure_terms,
        "outcome_terms": outcome_terms,
        "method_context": sorted(set(method_context)),
    }


def derive_dataset_context_terms(dataset_index: dict[str, Any]) -> list[str]:
    terms: set[str] = set()
    for item in dataset_index.get("candidate_data_bindings", []):
        text = " ".join(
            [
                str(item.get("family_name", "")),
                " ".join(str(reason) for reason in item.get("match_reasons", [])),
            ]
        ).lower()
        if "ifr" in text:
            terms.add("IFR")
        if "robot" in text or "机器人" in text:
            terms.add("robot")
        if "clds" in text or "劳动力" in text:
            terms.add("CLDS")
        if "cfps" in text:
            terms.add("CFPS")
        if "cgss" in text:
            terms.add("CGSS")
        if "cmds" in text or "流动人口" in text:
            terms.add("CMDS")
        if "charls" in text:
            terms.add("CHARLS")
    return sorted(terms)


def build_search_queries(topic: str, dataset_context_terms: list[str]) -> list[dict[str, Any]]:
    query_texts: list[tuple[str, str, str]] = [
        ("zh", "core_topic", "工业机器人 劳动力市场 匹配效率"),
        ("zh", "core_topic", "工业机器人 就业匹配 劳动力配置效率"),
        ("zh", "core_topic", "机器人采用 就业 工资 中国"),
        ("zh", "core_topic", "工业机器人 劳动力市场 中国 微观数据"),
        ("en", "core_topic", "industrial robots labor market matching efficiency"),
        ("en", "core_topic", "automation labor market matching China"),
        ("en", "core_topic", "robot adoption worker firm matching labor market"),
        ("en", "core_topic", "industrial robots employment wages China"),
    ]
    if "IFR" in dataset_context_terms or "robot" in dataset_context_terms:
        query_texts.append(("en", "dataset_index", "IFR industrial robots labor allocation China"))
    if "CLDS" in dataset_context_terms:
        query_texts.append(("en", "dataset_index", "CLDS industrial robots employment China"))
    if "CFPS" in dataset_context_terms:
        query_texts.append(("en", "dataset_index", "CFPS automation employment China"))
    if "CMDS" in dataset_context_terms:
        query_texts.append(("en", "dataset_index", "CMDS labor mobility automation China"))
    if "CGSS" in dataset_context_terms:
        query_texts.append(("en", "dataset_index", "CGSS automation labor market attitudes China"))

    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for language, source_context, query in query_texts:
        if query in seen:
            continue
        seen.add(query)
        records.append(
            {
                "query_id": f"Q{len(records) + 1:02d}",
                "language": language,
                "source_context": source_context,
                "query": query,
                "target_sources": target_sources_for_query(language),
                "intended_use": "discover_candidate_literature",
            }
        )
    return records


def target_sources_for_query(language: str) -> list[str]:
    if language == "zh":
        return ["cnki_manual_review_queue", "google_scholar_manual_queue", "local_pdf_or_zotero_import"]
    return ["openalex_metadata", "crossref_metadata", "semantic_scholar_metadata", "open_fulltext_discovery", "google_scholar_manual_queue"]


def build_source_registry() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "local_pdf_or_zotero_import",
            "source_type": "local_user_library",
            "capability": "import_user_local_pdf_or_zotero_metadata_and_fulltext",
            "output_state": "candidate",
        },
        {
            "source_id": "openalex_metadata",
            "source_type": "academic_metadata",
            "capability": "discover_cross_discipline_metadata_and_citation_links",
            "output_state": "candidate",
        },
        {
            "source_id": "crossref_metadata",
            "source_type": "academic_metadata",
            "capability": "verify_doi_publisher_metadata",
            "output_state": "metadata_verified",
        },
        {
            "source_id": "semantic_scholar_metadata",
            "source_type": "academic_metadata",
            "capability": "discover_related_papers_abstracts_and_citation_graph",
            "output_state": "candidate",
        },
        {
            "source_id": "open_fulltext_discovery",
            "source_type": "available_fulltext_discovery",
            "capability": "locate_available_fulltext_from_open_repository_author_page_or_user_import",
            "output_state": "fulltext_located",
        },
        {
            "source_id": "cnki_manual_review_queue",
            "source_type": "chinese_literature_review_queue",
            "capability": "queue_chinese_database_search_terms_for_human_or_browser_review",
            "output_state": "candidate",
        },
        {
            "source_id": "google_scholar_manual_queue",
            "source_type": "broad_literature_review_queue",
            "capability": "queue_broad_scholar_search_terms_for_browser_or_human_review",
            "output_state": "candidate",
        },
        {
            "source_id": "user_uploaded_fulltext",
            "source_type": "user_provided_fulltext",
            "capability": "promote_user_uploaded_fulltext_to_source_span_extraction",
            "output_state": "fulltext_located",
        },
    ]


def build_candidate_search_records(search_queries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for query in search_queries:
        records.append(
            {
                "record_id": f"LQ{len(records) + 1:03d}",
                "query_id": query["query_id"],
                "query": query["query"],
                "target_sources": query["target_sources"],
                "review_state": "candidate",
                "required_next_state": "metadata_verified",
                "can_support_strong_claims": False,
                "citation_use_policy": "candidate_reference_only_until_metadata_fulltext_source_span_and_human_review",
            }
        )
    return records


def write_report(project_root: Path, report: dict[str, Any], report_path: Path, review_path: Path) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Literature Discovery Seed Review",
        "",
        f"- 题目：{report['topic']}",
        f"- 状态：{report['status']}",
        "- 正式 bibliography 写回：否",
        "- 正式论文写回：否",
        "",
        "## 查询计划",
    ]
    for query in report["query_plan"]["search_queries"]:
        lines.append(f"- `{query['query_id']}` [{query['language']}/{query['source_context']}]: {query['query']}")

    lines.extend(["", "## 来源注册表"])
    for source in report["source_registry"]:
        lines.append(f"- `{source['source_id']}`: {source['capability']} -> `{source['output_state']}`")

    lines.extend(["", "## Bibliography 状态链"])
    lines.append(" -> ".join(report["bibliography_state_model"]["states"]))
    lines.extend(["", "## 候选检索记录"])
    for record in report["candidate_search_records"][:20]:
        lines.append(
            f"- `{record['record_id']}` {record['query']} | state={record['review_state']} | "
            f"strong_claims={record['can_support_strong_claims']}"
        )

    lines.extend(["", "## 下一步"])
    for task in report["next_tasks"]:
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"

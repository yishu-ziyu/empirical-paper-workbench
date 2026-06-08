from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def write_reference_chain_seed_package(
    task: dict[str, Any],
    project_root: Path,
    run_id: str,
    created_at: str,
) -> dict[str, Any]:
    """Write a candidate-only literature source seed package for review."""
    policy = task.get("reference_chain_policy") if isinstance(task.get("reference_chain_policy"), dict) else {}
    package = build_reference_chain_seed_package(task, policy, run_id, created_at)
    artifact_path = Path("workspace") / "runs" / run_id / "reference_chain_seed_package.json"
    absolute_path = project_root / artifact_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "artifact_path": artifact_path.as_posix(),
        "package": package,
    }


def build_reference_chain_seed_package(
    task: dict[str, Any],
    policy: dict[str, Any],
    run_id: str,
    created_at: str,
) -> dict[str, Any]:
    question = extract_research_question(task)
    ordered_sources = order_sources_by_priority(
        normalize_sources(policy.get("sources")),
        normalize_str_list(policy.get("source_priority")),
    )
    source_priority = normalize_str_list(policy.get("source_priority")) or [source["id"] for source in ordered_sources]
    candidate_queries = [
        build_candidate_query(index, source, question)
        for index, source in enumerate(ordered_sources, start=1)
    ]
    return {
        "schema_version": "p1.reference_chain_seed_package.v1",
        "status": "candidate_reference_seed_package_ready",
        "run_id": run_id,
        "task_id": str(task.get("id") or ""),
        "owner_agent": str(task.get("owner_agent") or ""),
        "task_title": str(task.get("title") or ""),
        "created_at": created_at,
        "research_question": question,
        "source_priority": source_priority,
        "sources": ordered_sources,
        "max_depth": normalize_positive_int(policy.get("max_depth"), 2),
        "max_iterations": normalize_positive_int(policy.get("max_iterations"), 5),
        "required_artifacts": normalize_str_list(policy.get("required_artifacts"))
        or [
            "LiteratureSeedPackage",
            "search_query_graph",
            "citation_verification_queue",
            "source_relevance_review",
        ],
        "candidate_queries": candidate_queries,
        "citation_verification_queue": [
            {
                "query_id": query["id"],
                "source_id": query["source_id"],
                "review_state": "candidate",
                "required_before": "verified_citation_or_formal_writeback",
            }
            for query in candidate_queries
        ],
        "citation_verification_policy": {
            "default_state": "candidate",
            "allowed_states": normalize_str_list(policy.get("candidate_reference_states"))
            or ["candidate", "verified", "rejected"],
            "verified_requires": [
                "source_specific_connector_check",
                "bibliographic_metadata_match",
                "human_literature_review",
            ],
        },
        "formal_writeback_gate": str(policy.get("formal_writeback_gate") or "review_literature_seed_package"),
        "writes_formal_layer": False,
        "claims_verified_citations": False,
        "output_boundary": "candidate_sources_only",
        "next_action": "review_literature_seed_package",
    }


def extract_research_question(task: dict[str, Any]) -> str:
    input_evidence = task.get("input_evidence") if isinstance(task.get("input_evidence"), dict) else {}
    question = input_evidence.get("research_question") if isinstance(input_evidence.get("research_question"), dict) else {}
    return str(question.get("question") or task.get("summary") or task.get("title") or "").strip()


def normalize_sources(value: Any) -> list[dict[str, str]]:
    raw_sources = value if isinstance(value, list) else []
    sources: list[dict[str, str]] = []
    for item in raw_sources:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        sources.append(
            {
                "id": str(item.get("id")),
                "label": str(item.get("label") or item.get("id")),
                "trigger": str(item.get("trigger") or ""),
                "mode": str(item.get("mode") or "manual_assisted_search"),
                "review_state": str(item.get("review_state") or "candidate"),
            }
        )
    return sources or default_sources()


def default_sources() -> list[dict[str, str]]:
    return [
        {"id": "arxiv", "label": "arXiv", "trigger": "英文工作论文和方法线索。", "mode": "automated_search", "review_state": "candidate"},
        {"id": "scholar", "label": "Google Scholar", "trigger": "引用网络和英文核心文献。", "mode": "browser_or_manual_assisted_search", "review_state": "candidate"},
        {"id": "cnki", "label": "CNKI", "trigger": "中文制度背景和本土文献。", "mode": "manual_assisted_or_browser_assisted_search", "review_state": "candidate"},
        {"id": "zotero", "label": "Zotero", "trigger": "用户已有文献库。", "mode": "local_connector_or_export_import", "review_state": "candidate"},
        {"id": "local_notes", "label": "Local notes", "trigger": "本地笔记和历史研究材料。", "mode": "local_file_search", "review_state": "candidate"},
    ]


def order_sources_by_priority(
    sources: list[dict[str, str]],
    priority: list[str],
) -> list[dict[str, str]]:
    by_id = {source["id"]: source for source in sources}
    ordered: list[dict[str, str]] = []
    for source_id in priority:
        if source_id in by_id:
            ordered.append(by_id[source_id])
    for source in sources:
        if source["id"] not in {item["id"] for item in ordered}:
            ordered.append(source)
    return ordered


def build_candidate_query(index: int, source: dict[str, str], question: str) -> dict[str, Any]:
    source_id = source["id"]
    query_terms = build_query_terms(question)
    query = " ".join(query_terms)
    if source_id == "cnki":
        query = f"{query} 实证研究 影响机制"
    elif source_id == "scholar":
        query = f"{query} empirical study causal evidence"
    elif source_id == "arxiv":
        query = f"{query} working paper empirical"
    elif source_id == "zotero":
        query = f"{query} saved library review"
    else:
        query = f"{query} local notes evidence"
    mode = source.get("mode", "")
    return {
        "id": f"candidate_query_{index:02d}_{source_id}",
        "source_id": source_id,
        "source_label": source.get("label", source_id),
        "query": query.strip(),
        "mode": mode,
        "trigger": source.get("trigger", ""),
        "review_state": "candidate",
        "manual_required": "manual" in mode or source_id in {"cnki", "scholar"},
        "can_enter_formal_layer": False,
        "required_before_formal_layer": "source_relevance_review_and_citation_verification",
    }


def build_query_terms(question: str) -> list[str]:
    normalized = re.sub(r"[，。！？；：、,.!?;:()\[\]{}\"'“”‘’]", " ", question)
    tokens = [token.strip() for token in normalized.split() if token.strip()]
    if not tokens and question:
        tokens = [question]
    return tokens[:12] or ["empirical", "research"]


def normalize_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def normalize_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default

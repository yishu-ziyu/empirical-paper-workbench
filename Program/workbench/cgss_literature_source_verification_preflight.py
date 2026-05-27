from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_literature_source_verification_preflight.v1"
DEFAULT_SEED_PACKAGE_PATH = Path("Results/json/cgss_social_capital_happiness_literature_seed_package.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_literature_source_verification_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_literature_source_verification_preflight.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_literature_source_verification_preflight(
    seed_package: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": seed_package.get("topic", ""),
        "source_artifacts": {
            "literature_seed_package": {
                "path": source_paths.get("literature_seed_package", str(DEFAULT_SEED_PACKAGE_PATH)),
                "schema_version": seed_package.get("schema_version", ""),
                "status": seed_package.get("status", ""),
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
    if seed_package.get("status") != "needs_human_literature_review":
        base.update(
            {
                "status": "blocked_missing_literature_seed",
                "blocking_reasons": ["literature_seed_not_reviewable"],
                "candidate_bibliography": [],
                "manual_review_queue": [],
                "cnki_queue": [],
                "zotero_scholar_queue": [],
                "promotion": {"allowed": False, "required_decision": "repair_literature_seed_package"},
            }
        )
        return base

    candidate_bibliography = [candidate_from_seed(source) for source in seed_package.get("seed_sources", [])]
    manual_review_queue = [item for item in candidate_bibliography if item["requires_manual_review"]]
    cnki_queue = build_cnki_queue(seed_package, candidate_bibliography)
    zotero_scholar_queue = build_zotero_scholar_queue(seed_package, candidate_bibliography)
    blocking_reasons = blocking_reasons_for(manual_review_queue, cnki_queue, zotero_scholar_queue)
    base.update(
        {
            "status": "needs_source_verification",
            "blocking_reasons": blocking_reasons,
            "candidate_bibliography": candidate_bibliography,
            "manual_review_queue": manual_review_queue,
            "cnki_queue": cnki_queue,
            "zotero_scholar_queue": zotero_scholar_queue,
            "citation_binding_targets": {
                "literature_review": "Manuscripts/sections/literature-and-contribution.md",
                "data_and_measurement": "Manuscripts/sections/data-and-measurement.md",
                "empirical_strategy": "Manuscripts/sections/empirical-strategy.md",
                "references": "Manuscripts/sections/references.md",
            },
            "promotion": {
                "allowed": False,
                "required_decision": "human_verify_sources_and_approve_bibliography_candidates",
                "would_write_if_approved": [
                    "Data/literature/processed/verified_bibliography.csv",
                    "Data/literature/processed/contribution_matrix.md",
                    "Results/json/cgss_social_capital_happiness_citation_bindings.json",
                ],
            },
            "next_tasks": [
                "open_official_sources_and_record_access_dates",
                "run_cnki_manual_verification",
                "lookup_zotero_or_scholar_metadata",
                "build_verified_bibliography_candidates",
                "bind_sources_to_literature_review_claims",
            ],
        }
    )
    return base


def candidate_from_seed(source: dict[str, Any]) -> dict[str, Any]:
    source_type = source.get("source_type", "")
    actions = verification_actions(source)
    return {
        "id": source.get("id", ""),
        "title": source.get("title", ""),
        "authors": source.get("authors", []),
        "year": source.get("year", ""),
        "url": source.get("url", ""),
        "source_type": source_type,
        "evidence_role": source.get("evidence_role", []),
        "review_status": "candidate_needs_source_check",
        "verification_actions": actions,
        "requires_manual_review": True,
        "ready_for_verified_bibliography": False,
        "citation_key_seed": citation_key_seed(source),
        "use_in_paper": source.get("use_in_paper", ""),
        "do_not_claim": source.get("do_not_claim", ""),
    }


def verification_actions(source: dict[str, Any]) -> list[str]:
    source_type = source.get("source_type", "")
    title = source.get("title", "")
    if source_type == "official_data":
        return ["open_official_source", "record_access_date"]
    if source_type == "chinese_literature_seed" or any("cnki" in role for role in source.get("evidence_role", [])):
        return ["cnki_or_journal_page_check", "record_chinese_metadata", "confirm_cssci_or_journal_level_if_needed"]
    if "doi.org" in source.get("url", "") or source_type in {"classic_theory", "method_reference", "measurement_standard"}:
        return ["verify_doi_or_publisher_page", "lookup_zotero_or_scholar_metadata", "record_access_date"]
    if "CGSS" in title or source_type == "cgss_empirical_study":
        return ["open_journal_page", "lookup_zotero_or_scholar_metadata", "confirm_wave_and_sample"]
    return ["manual_source_check"]


def citation_key_seed(source: dict[str, Any]) -> str:
    authors = source.get("authors", [])
    first_author = authors[0] if authors else "source"
    surname = first_author.split()[-1].lower().replace(".", "").replace(",", "")
    year = source.get("year") or "nd"
    return f"{surname}_{year}"


def build_cnki_queue(seed_package: dict[str, Any], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queue = []
    for item in seed_package.get("cnki_manual_queue", []):
        queue.append(
            {
                "query": item.get("query", ""),
                "purpose": item.get("purpose", ""),
                "status": "manual_search_required",
                "expected_output": "candidate_cnki_record_with_title_authors_year_journal_url_or_note",
            }
        )
    for candidate in candidates:
        if "cnki_or_journal_page_check" in candidate["verification_actions"]:
            queue.append(
                {
                    "query": f"{candidate['title']} {candidate['authors'][0] if candidate['authors'] else ''}",
                    "purpose": "核验中文文献元数据、期刊来源和可引用页面。",
                    "status": "manual_search_required",
                    "expected_output": "verified_chinese_bibliography_candidate_or_reject_reason",
                }
            )
    return queue


def build_zotero_scholar_queue(seed_package: dict[str, Any], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queue = []
    for item in seed_package.get("zotero_scholar_queue", []):
        queue.append(
            {
                "query": item.get("query", ""),
                "target": item.get("target", "zotero_or_scholar"),
                "status": "needs_lookup",
                "expected_output": "doi_or_stable_url_and_bibtex_candidate",
            }
        )
    for candidate in candidates:
        if "lookup_zotero_or_scholar_metadata" in candidate["verification_actions"]:
            queue.append(
                {
                    "query": f"{candidate['title']} {candidate['year']}",
                    "target": "zotero_or_scholar",
                    "status": "needs_lookup",
                    "expected_output": "metadata_match_or_reject_reason",
                }
            )
    return queue


def blocking_reasons_for(
    manual_review_queue: list[dict[str, Any]],
    cnki_queue: list[dict[str, Any]],
    zotero_scholar_queue: list[dict[str, Any]],
) -> list[str]:
    reasons = []
    if manual_review_queue:
        reasons.append("manual_source_review_required")
    if cnki_queue:
        reasons.append("manual_cnki_verification_required")
    if zotero_scholar_queue:
        reasons.append("zotero_or_scholar_metadata_required")
    return reasons


def write_literature_source_preflight_outputs(
    project_root: Path, preflight: dict[str, Any], result_path: Path, review_path: Path
) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(preflight), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(preflight: dict[str, Any]) -> str:
    lines = [
        "# CGSS 文献来源校验预检",
        "",
        f"- 题目：{preflight.get('topic', '')}",
        f"- 状态：{preflight['status']}",
        "- 写入正式参考文献：否",
        "- 写入正式论文：否",
    ]
    if preflight["blocking_reasons"]:
        lines.extend(["", "## 当前阻断"])
        for reason in preflight["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if preflight["status"].startswith("blocked"):
        return "\n".join(lines) + "\n"

    lines.extend(["", "## 候选参考文献"])
    for item in preflight["candidate_bibliography"]:
        actions = ", ".join(f"`{action}`" for action in item["verification_actions"])
        lines.extend(
            [
                f"### {item['id']} {item['title']}",
                f"- citation key seed：`{item['citation_key_seed']}`",
                f"- 来源类型：`{item['source_type']}`",
                f"- 校验动作：{actions}",
                f"- 可引用状态：`{item['review_status']}`",
                f"- 链接：{item['url']}",
                "",
            ]
        )
    lines.extend(["## CNKI / 中文文献人工队列"])
    for item in preflight["cnki_queue"]:
        lines.append(f"- `{item['query']}`：{item['purpose']} 输出：`{item['expected_output']}`。")
    lines.extend(["", "## Zotero / Scholar 元数据队列"])
    for item in preflight["zotero_scholar_queue"]:
        lines.append(f"- `{item['query']}` -> `{item['target']}`：{item['expected_output']}。")
    lines.extend(["", "## 下一步"])
    for task in preflight["next_tasks"]:
        lines.append(f"- `{task}`")
    return "\n".join(lines) + "\n"

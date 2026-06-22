from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p1a.parent_education_wage_literature_evidence_ledger.v1"
TOPIC = "父母受教育水平对子女工资收入的影响"
TOPIC_SLUG = "parent-education-wage"
DEFAULT_LITERATURE_PATH = Path("Tasks/parent-education-wage/literature.md")
DEFAULT_LEDGER_PATH = Path("Results/json/parent_education_wage_literature_evidence_ledger.json")
DEFAULT_REVIEW_PATH = Path("Reviews/parent_education_wage_literature_evidence_ledger.md")
PROTECTED_FORMAL_PATHS = [
    "Manuscripts/references.bib",
    "Manuscripts/paper.md",
    "Manuscripts/generated/paper_draft.md",
    "Data/literature/processed/verified_bibliography.csv",
    "Data/literature/processed/contribution_matrix.md",
]


def build_parent_education_wage_literature_evidence_ledger(
    project_root: Path,
    literature_path: Path = DEFAULT_LITERATURE_PATH,
) -> dict[str, Any]:
    absolute_literature_path = project_root / literature_path
    literature_text = absolute_literature_path.read_text(encoding="utf-8") if absolute_literature_path.exists() else ""
    directions = extract_search_directions(literature_text)
    citation_records = build_seed_citation_records(directions)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "status": "needs_external_literature_verification",
        "source_artifacts": {
            "topic_literature": {
                "path": literature_path.as_posix(),
                "exists": absolute_literature_path.exists(),
                "evidence_status": extract_frontmatter_value(literature_text, "evidence_status"),
            }
        },
        "candidate_topics": directions,
        "citation_state_model": {
            "states": ["seed", "candidate", "metadata_verified", "source_checked_candidate", "verified", "rejected"],
            "verified_state": "verified",
            "claim_use_rule": "Only verified records with source metadata and human approval can support formal manuscript claims.",
        },
        "citation_records": citation_records,
        "verified_count": len([record for record in citation_records if record["citation_status"] == "verified"]),
        "blocking_reasons": [
            "external_or_manual_literature_search_required",
            "human_bibliography_approval_required",
        ],
        "promotion": {
            "allowed": False,
            "required_decision": "human_approve_verified_literature_sources",
            "would_write_if_approved": [
                "Data/literature/processed/verified_bibliography.csv",
                "Data/literature/processed/contribution_matrix.md",
                "Results/json/parent_education_wage_citation_bindings.json",
            ],
        },
        "boundary_flags": {
            "modified_formal_bibliography": False,
            "modified_formal_manuscript": False,
            "modified_verified_bibliography": False,
            "wrote_state_product": False,
            "downloaded_fulltext": False,
        },
        "protected_formal_paths": PROTECTED_FORMAL_PATHS,
        "product_control_signal": {
            "phase": "P1-A",
            "label": "真实文献候选与引用核验",
            "status": "needs_external_literature_verification",
            "next_action": "run_external_or_manual_literature_search_then_review_sources",
        },
        "outputs": {
            "json": DEFAULT_LEDGER_PATH.as_posix(),
            "review": DEFAULT_REVIEW_PATH.as_posix(),
        },
    }


def extract_search_directions(literature_text: str) -> list[dict[str, str]]:
    directions: list[dict[str, str]] = []
    in_search_section = False
    for line in literature_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_search_section = "待检索方向" in stripped
            continue
        if not in_search_section:
            continue
        match = re.match(r"^\s*\d+[\.\、]\s*(.+?)\s*$", line)
        if not match:
            continue
        text = match.group(1).strip()
        if not text or "不得" in text:
            continue
        directions.append(
            {
                "id": f"PEW-Q{len(directions) + 1:02d}",
                "query_seed": text.rstrip("。"),
                "review_status": "seed",
                "intended_use": "discover_candidate_literature",
            }
        )
    if directions:
        return directions
    return [
        {
            "id": "PEW-Q01",
            "query_seed": "父母教育、家庭背景与子女工资收入",
            "review_status": "seed",
            "intended_use": "discover_candidate_literature",
        },
        {
            "id": "PEW-Q02",
            "query_seed": "代际人力资本传递与教育回报",
            "review_status": "seed",
            "intended_use": "discover_candidate_literature",
        },
        {
            "id": "PEW-Q03",
            "query_seed": "中国微观调查中的工资与父母教育测量",
            "review_status": "seed",
            "intended_use": "discover_candidate_literature",
        },
        {
            "id": "PEW-Q04",
            "query_seed": "义务教育、教育扩张或家庭教育背景的识别策略",
            "review_status": "seed",
            "intended_use": "discover_candidate_literature",
        },
    ]


def build_seed_citation_records(candidate_topics: list[dict[str, str]]) -> list[dict[str, Any]]:
    records = []
    for topic in candidate_topics:
        records.append(
            {
                "source_id": topic["id"].replace("Q", "S"),
                "query_id": topic["id"],
                "title": "",
                "authors": [],
                "year": "",
                "source_or_url": "",
                "local_source": DEFAULT_LITERATURE_PATH.as_posix(),
                "fit_reason": topic["query_seed"],
                "citation_status": "seed",
                "can_support_claims": False,
                "required_next_state": "candidate",
                "review_note": "This is a local search direction, not a verified literature source.",
            }
        )
    return records


def extract_frontmatter_value(text: str, key: str) -> str:
    for line in text.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


def write_parent_education_wage_literature_evidence_ledger(
    project_root: Path,
    ledger: dict[str, Any],
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_ledger_path = project_root / ledger_path
    absolute_review_path = project_root / review_path
    absolute_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review_path.write_text(render_review(ledger), encoding="utf-8")
    return absolute_ledger_path, absolute_review_path


def render_review(ledger: dict[str, Any]) -> str:
    lines = [
        "# P1-A 文献证据账本",
        "",
        f"- 题目：{ledger['topic']}",
        f"- 状态：`{ledger['status']}`",
        f"- verified_count：{ledger['verified_count']}",
        "- 写入正式 bibliography：否",
        "- 写入正式论文：否",
        "",
        "## 当前阻塞",
    ]
    for reason in ledger["blocking_reasons"]:
        lines.append(f"- `{reason}`")
    lines.extend(["", "## 检索 seed"])
    for topic in ledger["candidate_topics"]:
        lines.append(f"- `{topic['id']}` {topic['query_seed']} | status={topic['review_status']}")
    lines.extend(["", "## Citation Records"])
    for record in ledger["citation_records"]:
        lines.append(
            f"- `{record['source_id']}` query={record['query_id']} | status={record['citation_status']} | "
            f"claims={str(record['can_support_claims']).lower()}"
        )
    lines.extend(["", "## 正式层边界"])
    for path in ledger["protected_formal_paths"]:
        lines.append(f"- `{path}`")
    lines.append("")
    return "\n".join(lines)

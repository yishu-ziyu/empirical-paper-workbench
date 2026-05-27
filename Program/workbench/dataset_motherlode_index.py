from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p7.dataset_motherlode_index.v1"
DEFAULT_DATA_ROOT = Path("/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库")
DEFAULT_REPORT_PATH = Path("Results/json/dataset_motherlode_index.json")
DEFAULT_REVIEW_PATH = Path("Reviews/dataset_motherlode_index.md")
SUPPORTED_SUFFIXES = {
    ".7z",
    ".csv",
    ".do",
    ".dta",
    ".doc",
    ".docx",
    ".feather",
    ".md",
    ".parquet",
    ".pdf",
    ".py",
    ".rar",
    ".sav",
    ".txt",
    ".xls",
    ".xlsx",
    ".zip",
}

TOPIC_EXPANSIONS = {
    "robot": {
        "triggers": ["机器人", "工业机器人", "robot", "robots"],
        "terms": ["机器人", "工业机器人", "robot", "robots", "ifr", "penetration", "density", "installation"],
    },
    "labor": {
        "triggers": ["劳动力", "劳动", "就业", "工资", "匹配", "labor", "labour", "employment", "wage"],
        "terms": [
            "劳动力",
            "劳动",
            "就业",
            "工资",
            "匹配",
            "labor",
            "labour",
            "employment",
            "wage",
            "market",
            "segmentation",
            "clds",
            "cfps",
            "cmds",
        ],
    },
    "happiness": {
        "triggers": ["幸福", "满意", "happiness", "wellbeing", "well-being"],
        "terms": ["幸福", "满意", "happiness", "wellbeing", "well-being", "cgss", "cfps"],
    },
}


def build_dataset_motherlode_index(data_root: Path, topic: str | None = None) -> dict[str, Any]:
    dataset_families = scan_dataset_families(data_root)
    candidate_bindings = match_topic_to_families(topic or "", dataset_families)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic or "",
        "status": "needs_human_dataset_index_review" if data_root.exists() else "blocked_dataset_motherlode_missing",
        "data_source": {
            "id": "primary_local_dataset_motherlode",
            "path": str(data_root),
            "status": "read_only",
            "scope": "local_only",
            "source_type": "user_provided_public_dataset_pool",
        },
        "dataset_families": dataset_families,
        "candidate_data_bindings": candidate_bindings,
        "match_policy": {
            "mode": "metadata_only_family_name_and_path_match",
            "profiled_fields": False,
            "raw_data_read": False,
        },
        "boundary_flags": {
            "modified_raw_dataset": False,
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_run_plan": False,
            "generated_formal_paper": False,
        },
    }


def scan_dataset_families(data_root: Path) -> list[dict[str, Any]]:
    if not data_root.exists():
        return []

    grouped: dict[str, list[Path]] = {}
    for path in data_root.rglob("*"):
        if not is_supported_index_file(data_root, path):
            continue
        family_name = family_name_for_path(data_root, path)
        grouped.setdefault(family_name, []).append(path)

    families: list[dict[str, Any]] = []
    for family_name in sorted(grouped):
        files = sorted(grouped[family_name], key=lambda item: str(item.relative_to(data_root)))
        path_text = " ".join(str(path.relative_to(data_root)) for path in files)
        extensions = sorted({path.suffix.lower() for path in files if path.suffix})
        year_hints = infer_year_hints(path_text)
        families.append(
            {
                "family_name": family_name,
                "family_root": str((data_root / family_name).resolve()) if family_name != "root_files" else str(data_root.resolve()),
                "file_count": len(files),
                "total_bytes": sum(path.stat().st_size for path in files),
                "extensions": extensions,
                "year_hints": year_hints,
                "path_keyword_hints": extract_path_keyword_hints(path_text),
                "sample_paths": [str(path.relative_to(data_root)) for path in files[:8]],
                "field_profile_status": "not_profiled_metadata_index_only",
            }
        )
    return families


def family_name_for_path(data_root: Path, path: Path) -> str:
    relative = path.relative_to(data_root)
    return relative.parts[0] if len(relative.parts) > 1 else "root_files"


def is_supported_index_file(data_root: Path, path: Path) -> bool:
    if not path.is_file():
        return False
    relative = path.relative_to(data_root)
    if any(part.startswith(".") for part in relative.parts):
        return False
    suffix = path.suffix.lower()
    return bool(suffix and suffix in SUPPORTED_SUFFIXES)


def infer_year_hints(text: str) -> list[str]:
    return sorted(set(re.findall(r"(?:19|20)\d{2}", text)))


def extract_path_keyword_hints(text: str) -> list[str]:
    lowered = text.lower()
    terms = {term.lower() for expansion in TOPIC_EXPANSIONS.values() for term in expansion["terms"]}
    return sorted(term for term in terms if term in lowered)


def match_topic_to_families(topic: str, dataset_families: list[dict[str, Any]]) -> list[dict[str, Any]]:
    query_terms = build_query_terms(topic)
    candidates: list[dict[str, Any]] = []
    for family in dataset_families:
        searchable = " ".join(
            [
                str(family.get("family_name", "")),
                " ".join(str(path) for path in family.get("sample_paths", [])),
                " ".join(str(term) for term in family.get("path_keyword_hints", [])),
            ]
        ).lower()
        matched_terms: list[str] = []
        score = 0
        for term in query_terms:
            lowered = term.lower()
            if lowered not in searchable:
                continue
            matched_terms.append(term)
            score += term_score(term)
        if score <= 0:
            continue
        candidates.append(
            {
                "family_name": family["family_name"],
                "score": score,
                "match_reasons": sorted(set(matched_terms), key=lambda item: (-term_score(item), item)),
                "family_root": family["family_root"],
                "year_hints": family["year_hints"],
                "extensions": family["extensions"],
                "field_profile_status": family["field_profile_status"],
                "recommended_next_action": "profile_fields_before_dataset_binding",
            }
        )
    return sorted(candidates, key=lambda item: (-item["score"], item["family_name"]))[:20]


def build_query_terms(topic: str) -> list[str]:
    topic_lower = topic.lower()
    terms: list[str] = []
    for expansion in TOPIC_EXPANSIONS.values():
        if any(trigger.lower() in topic_lower for trigger in expansion["triggers"]):
            terms.extend(expansion["terms"])
    if not terms:
        terms.extend(token for token in re.split(r"[\s,，:：;；\-]+", topic) if token)
    return sorted(set(terms), key=lambda item: (-term_score(item), item))


def term_score(term: str) -> int:
    lowered = term.lower()
    if lowered in {"工业机器人", "机器人", "robot", "robots", "ifr"}:
        return 6
    if lowered in {"劳动力", "劳动", "labor", "labour", "clds", "cfps", "cmds", "segmentation"}:
        return 4
    if lowered in {"cgss", "happiness", "wellbeing", "well-being", "幸福", "满意"}:
        return 3
    return 2


def write_report(project_root: Path, report: dict[str, Any], report_path: Path, review_path: Path) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(report: dict[str, Any]) -> str:
    source = report["data_source"]
    lines = [
        "# Dataset Motherlode Index Review",
        "",
        f"- 题目：{report.get('topic') or '未指定'}",
        f"- 状态：{report['status']}",
        f"- 数据源：{source['id']}",
        f"- 路径：{source['path']}",
        f"- 边界：{source['status']} / {source['scope']} / {source['source_type']}",
        "- 正式层写回：否",
        "",
        "## 候选数据绑定",
    ]
    candidates = report.get("candidate_data_bindings", [])
    if not candidates:
        lines.append("- 暂无候选绑定；需要人工补充题目关键词或数据源。")
    for item in candidates[:15]:
        reasons = ", ".join(item.get("match_reasons", [])) or "metadata match"
        years = ", ".join(item.get("year_hints", [])) or "unknown year"
        lines.append(f"- {item['family_name']} | score={item['score']} | years={years} | reasons={reasons}")

    lines.extend(["", "## 数据族概览"])
    for family in report.get("dataset_families", [])[:30]:
        extensions = ", ".join(family.get("extensions", [])) or "unknown extension"
        years = ", ".join(family.get("year_hints", [])) or "unknown year"
        lines.append(f"- {family['family_name']}: {family['file_count']} files, {family['total_bytes']} bytes, {extensions}, years={years}")

    lines.extend(
        [
            "",
            "## 边界确认",
            f"- 修改原始数据：{report['boundary_flags']['modified_raw_dataset']}",
            f"- 修改正式论文：{report['boundary_flags']['modified_formal_manuscript']}",
            f"- 修改正式 bibliography：{report['boundary_flags']['modified_formal_bibliography']}",
            f"- 修改 run plan：{report['boundary_flags']['modified_run_plan']}",
            "",
            "## 下一步",
            "- 人工审阅候选数据绑定。",
            "- 对入选数据族运行字段级 profiling。",
            "- 生成项目级 DatasetBinding proposal，仍不写正式层。",
        ]
    )
    return "\n".join(lines) + "\n"

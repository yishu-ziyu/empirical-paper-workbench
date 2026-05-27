from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.cgss_topic_variable_discovery import (
    DEFAULT_DATA_ROOT,
    YEAR_PRIORITY,
    build_candidate_report,
    classify_variable,
    infer_year,
    read_dta_metadata,
    select_cgss_dta_files,
)


SCHEMA_VERSION = "p6.cgss_data_discovery.v1"
DEFAULT_REPORT_PATH = Path("Results/json/cgss_social_capital_happiness_data_discovery.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_data_discovery.md")
SUPPORTING_DOCUMENT_SUFFIXES = {".xlsx", ".xls", ".pdf", ".doc", ".docx", ".txt", ".md"}
SUPPORTING_DOCUMENT_TOKENS = ["编码", "代码", "变量", "问卷", "说明", "codebook", "questionnaire"]


def discover_cgss_data_assets(data_root: Path, topic: str) -> dict[str, Any]:
    datasets = load_cgss_dataset_profiles(data_root)
    return build_cgss_data_discovery_report(topic=topic, data_root=data_root, datasets=datasets)


def load_cgss_dataset_profiles(data_root: Path) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for path in select_cgss_dta_files(data_root):
        profiles.append(profile_cgss_dataset(path, data_root))
    return sorted(profiles, key=dataset_sort_key)


def profile_cgss_dataset(path: Path, data_root: Path | None = None) -> dict[str, Any]:
    variables: list[dict[str, str]] = []
    row_count: int | None = None
    readability_status = "readable"
    read_error: str | None = None
    try:
        variables = read_dta_metadata(path)
        row_count = read_dta_row_count(path)
    except Exception as exc:  # pragma: no cover - exercised by corrupted local files only
        readability_status = "metadata_read_failed"
        read_error = str(exc)

    return {
        "year": infer_year(path),
        "path": str(path),
        "file_type": path.suffix.lstrip(".").lower() or "unknown",
        "size_bytes": path.stat().st_size if path.exists() else None,
        "row_count": row_count,
        "variable_count": len(variables),
        "readability_status": readability_status,
        "read_error": read_error,
        "evidence_level": "local_file",
        "supporting_documents": discover_supporting_documents(path, data_root),
        "variables": variables,
    }


def read_dta_row_count(path: Path) -> int | None:
    try:
        import pyreadstat  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("pyreadstat is required to read CGSS .dta metadata") from exc

    _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
    value = getattr(meta, "number_rows", None)
    return int(value) if value is not None else None


def discover_supporting_documents(dataset_path: Path, data_root: Path | None = None) -> list[str]:
    roots = [dataset_path.parent]
    if data_root is not None and data_root.exists():
        roots.append(data_root)

    dataset_year = infer_year(dataset_path)
    seen: set[Path] = set()
    matches: list[Path] = []
    for root in roots:
        if root in seen:
            continue
        seen.add(root)
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in SUPPORTING_DOCUMENT_SUFFIXES:
                continue
            text = path.name.lower()
            if "cfps" in text:
                continue
            if any(token.lower() in text for token in SUPPORTING_DOCUMENT_TOKENS):
                matches.append(path)
    unique_matches = sorted(set(matches), key=lambda item: support_document_rank(item, dataset_path, dataset_year))
    same_year_matches = [path for path in unique_matches if dataset_year != "unknown" and dataset_year in str(path)]
    selected = same_year_matches if same_year_matches else unique_matches
    return [str(path) for path in selected[:12]]


def support_document_rank(path: Path, dataset_path: Path, dataset_year: str) -> tuple[int, int, str]:
    text = str(path).lower()
    same_year = 0 if dataset_year != "unknown" and dataset_year in text else 1
    same_parent = 0 if path.parent == dataset_path.parent else 1
    cgss_named = 0 if "cgss" in text else 1
    return (same_year, same_parent, cgss_named, len(str(path)), str(path))


def build_cgss_data_discovery_report(topic: str, data_root: Path, datasets: list[dict[str, Any]]) -> dict[str, Any]:
    readable = [dataset for dataset in datasets if dataset.get("readability_status") == "readable"]
    recommended = readable[0] if readable else None
    role_support = build_candidate_report(topic=topic, datasets=readable) if readable else None

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "data_root": str(data_root),
        "status": "needs_human_dataset_binding_review" if recommended else "blocked_no_cgss_dataset",
        "dataset_binding_draft": {
            "status": "needs_human_dataset_binding_review" if recommended else "blocked_no_cgss_dataset",
            "candidate_count": len(datasets),
            "recommended_dataset": summarize_dataset(recommended) if recommended else None,
            "binding_rule": "先确认 CGSS 年份、数据文件、编码表和问卷，再进入变量角色草案。",
        },
        "dataset_candidates": [summarize_dataset(dataset) for dataset in datasets],
        "field_profile": build_field_profile(readable),
        "role_candidate_preview": summarize_role_support(role_support),
        "next_tasks": next_tasks(bool(recommended)),
        "boundary_flags": {
            "modified_formal_research_question": False,
            "modified_formal_variable_roles": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "generated_formal_paper": False,
        },
        "agent_team_routing": {
            "first_agent_to_call": "DataAgent" if recommended else "Supervisor",
            "handoff_after_this_node": "VariableRoleAgent" if recommended else "HumanDataLocator",
            "recall_condition": "人工确认 DatasetBinding 后，再让 VariableRoleAgent 读取字段画像。",
        },
    }


def summarize_dataset(dataset: dict[str, Any] | None) -> dict[str, Any] | None:
    if dataset is None:
        return None
    return {
        "year": dataset.get("year"),
        "path": dataset.get("path"),
        "file_type": dataset.get("file_type"),
        "size_bytes": dataset.get("size_bytes"),
        "row_count": dataset.get("row_count"),
        "variable_count": dataset.get("variable_count"),
        "readability_status": dataset.get("readability_status"),
        "read_error": dataset.get("read_error"),
        "evidence_level": dataset.get("evidence_level", "local_file"),
        "supporting_documents": dataset.get("supporting_documents", []),
    }


def build_field_profile(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"outcome": 0, "social_capital": 0, "control": 0}
    examples: dict[str, list[dict[str, Any]]] = {"outcome": [], "social_capital": [], "control": []}
    for dataset in datasets:
        for variable in dataset.get("variables", []):
            classified = classify_variable(variable)
            role = classified.get("primary_role")
            if role not in counts:
                continue
            counts[role] += 1
            if len(examples[role]) < 8:
                examples[role].append(
                    {
                        "name": variable.get("name", ""),
                        "label": variable.get("label", ""),
                        "year": dataset.get("year"),
                        "dataset_path": dataset.get("path"),
                        "matched_terms": classified.get("matched_terms", []),
                    }
                )
    return {
        "outcome_candidates": counts["outcome"],
        "social_capital_candidates": counts["social_capital"],
        "control_candidates": counts["control"],
        "examples": examples,
    }


def summarize_role_support(role_support: dict[str, Any] | None) -> dict[str, Any]:
    if not role_support:
        return {"status": "not_available"}
    return {
        "status": role_support.get("status"),
        "recommended_dataset_order": role_support.get("recommended_dataset_order", []),
        "top_outcome": role_support.get("role_candidates", {}).get("outcome", [])[:5],
        "top_social_capital": role_support.get("role_candidates", {}).get("social_capital", [])[:8],
        "top_controls": role_support.get("role_candidates", {}).get("controls", [])[:8],
    }


def next_tasks(has_recommended_dataset: bool) -> list[str]:
    if not has_recommended_dataset:
        return ["locate_cgss_dataset", "rerun_cgss_data_discovery"]
    return [
        "review_cgss_dataset_binding",
        "draft_cgss_variable_roles",
        "build_cgss_literature_seed_package",
        "run_cgss_method_gate",
    ]


def dataset_sort_key(dataset: dict[str, Any]) -> tuple[int, int, str]:
    readability_rank = 0 if dataset.get("readability_status") == "readable" else 1
    year_rank = YEAR_PRIORITY.get(str(dataset.get("year")), 99)
    return (readability_rank, year_rank, str(dataset.get("path", "")))


def write_report(project_root: Path, report: dict[str, Any], report_path: Path, review_path: Path) -> tuple[Path, Path]:
    absolute_report = project_root / report_path
    absolute_review = project_root / review_path
    absolute_report.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(report), encoding="utf-8")
    return absolute_report, absolute_review


def render_review(report: dict[str, Any]) -> str:
    binding = report["dataset_binding_draft"]
    recommended = binding.get("recommended_dataset")
    lines = [
        "# CGSS DatasetBinding 草案",
        "",
        f"- 题目：{report['topic']}",
        f"- 数据根目录：{report['data_root']}",
        f"- 状态：{report['status']}",
        "- 正式层写回：否；本节点只确认数据资产，不自动改变量角色、方法设计或论文正文。",
        "",
        "## 人工要确认什么",
        "",
        "- 确认是否使用推荐 CGSS 数据。",
        "- 确认编码表、问卷或变量说明是否足够支撑下一步变量角色判断。",
        "- 确认后再进入幸福感、社会资本和控制变量候选审阅。",
        "",
        "## 推荐数据",
    ]
    if recommended:
        lines.extend(format_dataset(recommended))
    else:
        lines.append("- 暂未找到可读 CGSS 数据，请先绑定本地数据目录。")

    lines.extend(["", "## 候选数据文件"])
    for dataset in report["dataset_candidates"]:
        lines.extend(format_dataset(dataset))

    profile = report["field_profile"]
    lines.extend(
        [
            "",
            "## 字段画像预览",
            f"- 幸福感候选：{profile['outcome_candidates']}",
            f"- 社会资本候选：{profile['social_capital_candidates']}",
            f"- 控制变量候选：{profile['control_candidates']}",
            "",
            "## 下一步",
        ]
    )
    for task in report["next_tasks"]:
        lines.append(f"- {task}")
    return "\n".join(lines) + "\n"


def format_dataset(dataset: dict[str, Any]) -> list[str]:
    lines = [
        f"- {Path(str(dataset.get('path'))).name}",
        f"  - 年份：{dataset.get('year')}",
        f"  - 路径：{dataset.get('path')}",
        f"  - 样本量：{dataset.get('row_count')}",
        f"  - 字段数：{dataset.get('variable_count')}",
        f"  - 可读性：{dataset.get('readability_status')}",
        f"  - 证据等级：{dataset.get('evidence_level')}",
    ]
    documents = dataset.get("supporting_documents") or []
    if documents:
        lines.append("  - 配套材料：")
        for path in documents[:5]:
            lines.append(f"    - {path}")
    return lines


__all__ = [
    "DEFAULT_DATA_ROOT",
    "DEFAULT_REPORT_PATH",
    "DEFAULT_REVIEW_PATH",
    "build_cgss_data_discovery_report",
    "discover_cgss_data_assets",
    "load_cgss_dataset_profiles",
    "profile_cgss_dataset",
    "render_review",
    "write_report",
]

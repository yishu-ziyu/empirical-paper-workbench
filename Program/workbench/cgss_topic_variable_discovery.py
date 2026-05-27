from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_topic_variable_discovery.v1"
DEFAULT_DATA_ROOT = Path("/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A004CGSS中国综合社会调查")
DEFAULT_REPORT_PATH = Path("Results/json/cgss_social_capital_happiness_variable_candidates.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_variable_candidates.md")

YEAR_PRIORITY = {"2023": 0, "2021": 1, "2018": 2}

ROLE_TOKENS = {
    "outcome": ["幸福", "生活满意", "满意度", "快乐"],
    "social_capital": [
        "信任",
        "可信",
        "朋友",
        "邻居",
        "聚会",
        "社交",
        "联系",
        "帮助",
        "求助",
        "公益",
        "志愿",
        "社区",
        "捐赠",
        "工会",
        "组织",
    ],
    "control": [
        "性别",
        "年龄",
        "出生",
        "教育",
        "收入",
        "健康",
        "婚姻",
        "户口",
        "就业",
        "工作",
        "省",
        "市",
        "地区",
        "城乡",
        "民族",
    ],
}

NAME_HINTS = {
    "outcome": {"a36", "A36", "D36", "D1"},
    "social_capital": {
        "a33",
        "A33",
        "v505",
        "a31a",
        "a31b",
        "a311",
        "A31_1",
        "A31a",
        "A31b",
        "A30_6",
        "A30_7",
        "c17a",
        "c17b",
        "c17c",
        "c17d",
        "c17e",
        "c17f",
        "c17g",
        "c17h",
        "c17i",
        "c17j",
        "c17k",
        "c17l",
        "c17m",
        "c17n",
        "c17o",
        "c17p",
        "c17q",
        "c11a",
        "c11b",
        "c11c",
        "c11d",
        "c11e",
        "c11f",
        "c12a",
        "c12b",
        "c12c",
        "c1b",
        "c1c",
        "c1e",
        "c1h",
    },
    "control": {
        "a2",
        "A2",
        "a7a",
        "a7b",
        "a7c",
        "A7a",
        "A7b",
        "A7c",
        "a8a",
        "a8b",
        "A8a",
        "A8b",
        "a15",
        "a16",
        "A15",
        "A16",
        "a18",
        "a21",
        "A18",
        "A21",
        "s41",
        "s42",
    },
}


def discover_cgss_variable_candidates(data_root: Path, topic: str) -> dict[str, Any]:
    datasets = load_cgss_datasets(data_root)
    return build_candidate_report(topic=topic, datasets=datasets)


def load_cgss_datasets(data_root: Path) -> list[dict[str, Any]]:
    files = select_cgss_dta_files(data_root)
    datasets: list[dict[str, Any]] = []
    for path in files:
        metadata = read_dta_metadata(path)
        datasets.append(
            {
                "year": infer_year(path),
                "path": str(path),
                "variable_count": len(metadata),
                "variables": metadata,
            }
        )
    return datasets


def select_cgss_dta_files(data_root: Path) -> list[Path]:
    if not data_root.exists():
        return []
    candidates = [path for path in data_root.rglob("*.dta") if "cgss" in path.name.lower()]
    selected_by_year: dict[str, Path] = {}
    for path in candidates:
        year = infer_year(path)
        if year not in YEAR_PRIORITY:
            continue
        current = selected_by_year.get(year)
        if current is None or rank_path(path) < rank_path(current):
            selected_by_year[year] = path
    return [selected_by_year[year] for year in sorted(selected_by_year, key=lambda item: YEAR_PRIORITY[item])]


def rank_path(path: Path) -> tuple[int, int, str]:
    text = str(path)
    duplicate_penalty = 10 if "外部" in text or "副本" in text else 0
    stata_penalty = 0 if "stata" in text.lower() else 1
    return (duplicate_penalty + stata_penalty, len(text), text)


def read_dta_metadata(path: Path) -> list[dict[str, str]]:
    try:
        import pyreadstat  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("pyreadstat is required to read CGSS .dta metadata") from exc

    _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
    labels = getattr(meta, "column_labels", None) or []
    variables: list[dict[str, str]] = []
    for index, name in enumerate(meta.column_names):
        label = labels[index] if index < len(labels) and labels[index] else ""
        variables.append({"name": str(name), "label": str(label)})
    return variables


def build_candidate_report(topic: str, datasets: list[dict[str, Any]]) -> dict[str, Any]:
    role_candidates = {"outcome": [], "social_capital": [], "controls": []}
    dataset_summaries: list[dict[str, Any]] = []
    for dataset in datasets:
        dataset_summaries.append(
            {
                "year": dataset.get("year"),
                "path": dataset.get("path"),
                "variable_count": dataset.get("variable_count", 0),
            }
        )
        for variable in dataset.get("variables", []):
            classified = classify_variable(variable)
            role = classified["primary_role"]
            if role == "control":
                role_key = "controls"
            elif role:
                role_key = role
            else:
                continue
            role_candidates[role_key].append(
                {
                    "name": variable.get("name", ""),
                    "label": variable.get("label", ""),
                    "year": dataset.get("year"),
                    "dataset_path": dataset.get("path"),
                    "matched_terms": classified["matched_terms"],
                    "priority": candidate_priority(dataset.get("year"), classified),
                }
            )

    for key, values in role_candidates.items():
        deduped = dedupe_candidates(values)
        role_candidates[key] = sorted(deduped, key=lambda item: item["priority"])[:30 if key == "social_capital" else 20]

    status = "needs_human_review" if datasets else "blocked_no_cgss_dataset"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "status": status,
        "recommended_dataset_order": sorted(dataset_summaries, key=lambda item: YEAR_PRIORITY.get(str(item.get("year")), 99)),
        "role_candidates": role_candidates,
        "recommended_minimal_plan": {
            "dataset": "先用 CGSS2023 单年横截面；如果变量质量不足，再切到 2021 或做 2021/2023 口径对齐。",
            "outcome": "主结果变量用 a36/A36 幸福感题项；2021 可用 D36 做评分口径稳健性。",
            "treatment": "社会资本先拆成信任、社交网络、互助参与三个维度，不急着合成一个黑箱指数。",
            "models": ["OLS baseline", "ordered logit robustness", "dimension-by-dimension robustness"],
        },
        "next_tasks": ["review_cgss_variable_candidates", "run_cgss_minimal_model", "draft_cgss_paper_package"],
        "boundary_flags": {
            "modified_formal_variable_roles": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "generated_formal_paper": False,
        },
    }


def classify_variable(variable: dict[str, Any]) -> dict[str, Any]:
    name = str(variable.get("name") or "")
    label = str(variable.get("label") or "")
    matched: dict[str, list[str]] = {}
    for role, names in NAME_HINTS.items():
        if name in names:
            matched.setdefault(role, []).append(name)
    searchable = f"{name} {label}".lower()
    for role, tokens in ROLE_TOKENS.items():
        for token in tokens:
            if token.lower() in searchable:
                matched.setdefault(role, []).append(token)

    role_order = ["outcome", "social_capital", "control"]
    primary_role = next((role for role in role_order if matched.get(role)), None)
    return {
        "primary_role": primary_role,
        "matched_terms": matched.get(primary_role, []) if primary_role else [],
        "all_matches": matched,
    }


def candidate_priority(year: Any, classified: dict[str, Any]) -> tuple[int, int, str]:
    year_rank = YEAR_PRIORITY.get(str(year), 99)
    hint_rank = 0 if any(term for term in classified.get("matched_terms", []) if re.fullmatch(r"[A-Za-z0-9_]+", str(term))) else 1
    return (year_rank, hint_rank, ",".join(str(term) for term in classified.get("matched_terms", [])))


def dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for item in sorted(candidates, key=lambda candidate: candidate["priority"]):
        key = (str(item.get("year")), str(item.get("name")).lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def infer_year(path: Path) -> str:
    match = re.search(r"20\d{2}", str(path))
    return match.group(0) if match else "unknown"


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
        "# CGSS 社会资本与幸福感变量候选",
        "",
        f"- 题目：{report['topic']}",
        f"- 状态：{report['status']}",
        "- 正式层写回：否",
        "",
        "## 推荐数据",
    ]
    for item in report["recommended_dataset_order"]:
        lines.append(f"- {item.get('year')}: {item.get('path')} ({item.get('variable_count')} variables)")
    lines.extend(["", "## 候选变量"])
    for role_key, title in [("outcome", "因变量：主观幸福感"), ("social_capital", "核心解释变量：社会资本"), ("controls", "控制变量")]:
        lines.extend(["", f"### {title}"])
        for item in report["role_candidates"][role_key][:15]:
            label = item.get("label") or "无标签"
            lines.append(f"- `{item.get('name')}` ({item.get('year')}): {label}")
    lines.extend(
        [
            "",
            "## 下一步",
            "- 人工审阅变量候选，确认第一版口径。",
            "- 跑最小模型：幸福感 = 社会资本维度 + 个体控制 + 地区控制。",
            "- 结果只进入 CGSS 新题目的草案层，不覆盖当前正式包。",
        ]
    )
    return "\n".join(lines) + "\n"

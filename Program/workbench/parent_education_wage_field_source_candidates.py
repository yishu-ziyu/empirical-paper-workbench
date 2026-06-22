from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


SCHEMA_VERSION = "p4.parent_education_wage_field_source_candidates.v1"
TOPIC = "父母受教育水平对子女工资收入的影响"
TOPIC_SLUG = "parent-education-wage"

DEFAULT_LEDGER_PATH = Path("Results/json/parent_education_wage_p4_field_source_candidates.json")
DEFAULT_REVIEW_PATH = Path("Reviews/parent_education_wage_p4_field_source_candidates.md")
FORMAL_VARIABLE_ROLES_PATH = Path("state/product/variable_roles.json")
FORMAL_DESIGN_SPEC_PATH = Path("state/product/design_spec.json")
FORMAL_RUN_PLAN_PATH = Path("state/product/run_plan.json")

KNOWN_CFPS_ROOTS = (
    Path("/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库/A001CFPS中国家庭追踪调查"),
    Path("/Users/mahaoxuan/Desktop/实证数据库/A001CFPS中国家庭追踪调查"),
)

TARGET_FIELDS = ("father_education", "mother_education", "parent_education", "hukou")


def run_parent_education_wage_field_source_candidates(
    project_root: Path,
    data_root: Path | str | None = None,
) -> tuple[dict[str, Any], Path, Path]:
    ledger = build_parent_education_wage_field_source_candidates(project_root, data_root=data_root)
    json_path, review_path = write_parent_education_wage_field_source_candidates(project_root, ledger)
    return ledger, json_path, review_path


def build_parent_education_wage_field_source_candidates(
    project_root: Path,
    data_root: Path | str | None = None,
) -> dict[str, Any]:
    root_resolution = resolve_cfps_root(project_root, data_root=data_root)
    selected_root = Path(root_resolution["selected_root"]) if root_resolution.get("selected_root") else None
    source_fields = scan_stata_variable_labels(selected_root) if selected_root else []
    field_source_candidates = build_field_source_candidates(source_fields)
    by_field = {item["dataset_column"]: item for item in field_source_candidates}
    parent_fields_ready = all(
        by_field.get(field, {}).get("candidate_status") == "candidate_found"
        for field in ("father_education", "mother_education")
    )
    status = "field_source_candidates_ready_for_review" if parent_fields_ready else "field_source_candidates_incomplete"
    candidate_count = sum(len(item["candidates"]) for item in field_source_candidates)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "status": status,
        "run_id": None,
        "source_roots": {
            **root_resolution,
            "scanned_file_count": len({item["source_path"] for item in source_fields}),
            "source_field_count": len(source_fields),
        },
        "candidate_count": candidate_count,
        "field_source_candidates": field_source_candidates,
        "human_review_required": [
            "confirm_parent_education_construction",
            "confirm_preferred_cfps_wave",
            "confirm_hukou_role",
            "approve_before_formal_variable_roles_write",
        ],
        "boundary_flags": {
            "modified_formal_variable_roles": False,
            "modified_formal_design_spec": False,
            "modified_formal_run_plan": False,
            "executed_regression": False,
            "created_run_id": False,
            "loaded_full_data": False,
        },
        "formal_state": {
            "variable_roles": {"path": FORMAL_VARIABLE_ROLES_PATH.as_posix(), "modified": False},
            "design_spec": {"path": FORMAL_DESIGN_SPEC_PATH.as_posix(), "modified": False},
            "run_plan": {"path": FORMAL_RUN_PLAN_PATH.as_posix(), "modified": False},
        },
        "product_control_signal": {
            "phase": "P4",
            "label": "字段来源",
            "status": status,
            "next_action": "human_review_parent_education_field_candidates"
            if parent_fields_ready
            else "locate_parent_education_source_fields",
        },
        "outputs": {
            "json": DEFAULT_LEDGER_PATH.as_posix(),
            "review": DEFAULT_REVIEW_PATH.as_posix(),
        },
    }


def resolve_cfps_root(project_root: Path, data_root: Path | str | None = None) -> dict[str, Any]:
    candidate_roots: list[Path] = []
    if data_root:
        candidate_roots.append(Path(data_root).expanduser())
    env_root = os.environ.get("CFPS_DATA_ROOT")
    if env_root:
        candidate_roots.append(Path(env_root).expanduser())
    candidate_roots.extend(KNOWN_CFPS_ROOTS)

    seen: set[str] = set()
    unique_roots = []
    for root in candidate_roots:
        resolved = str(root)
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_roots.append(root)

    existing_roots = [root.resolve() for root in unique_roots if root.exists() and root.is_dir()]
    stale_paths = collect_stale_source_paths(project_root)
    return {
        "selected_root": str(existing_roots[0]) if existing_roots else None,
        "candidate_roots": [str(root) for root in unique_roots],
        "existing_roots": [str(root) for root in existing_roots],
        "stale_source_paths": stale_paths,
        "resolution_note": "selected_existing_root_metadata_only" if existing_roots else "no_existing_cfps_root_found",
    }


def collect_stale_source_paths(project_root: Path) -> list[str]:
    paths: set[str] = set()
    for relative_path in (
        Path("state/product/variable_role_candidates.json"),
        Path("Results/json/parent_education_wage_p2_execution_readiness.json"),
    ):
        state = load_json(project_root / relative_path)
        collect_paths_from_json(state, paths)
    return sorted(path for path in paths if path and not Path(path).expanduser().exists())


def collect_paths_from_json(value: Any, paths: set[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"path", "source_path"} and isinstance(item, str) and (item.startswith("/") or item.startswith("~")):
                paths.add(item)
            else:
                collect_paths_from_json(item, paths)
    elif isinstance(value, list):
        for item in value:
            collect_paths_from_json(item, paths)


def scan_stata_variable_labels(root: Path | None) -> list[dict[str, Any]]:
    if root is None:
        return []
    fields: list[dict[str, Any]] = []
    for dta_path in sorted(root.glob("**/*.dta")):
        try:
            reader = pd.io.stata.StataReader(str(dta_path))
            labels = reader.variable_labels()
            row_count = getattr(reader, "nobs", None)
        except Exception:
            continue
        relative_path = dta_path.relative_to(root).as_posix()
        for name, label in labels.items():
            label_text = str(label or "")
            fields.append(
                {
                    "name": str(name),
                    "label": label_text,
                    "source_path": relative_path,
                    "source_type": "stata_variable_label",
                    "source_root": str(root),
                    "file_name": dta_path.name,
                    "row_count": row_count,
                    "evidence_level": "local_stata_metadata",
                }
            )
    return fields


def build_field_source_candidates(source_fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    father_candidates = rank_candidates([field for field in source_fields if is_father_education(field)])
    mother_candidates = rank_candidates([field for field in source_fields if is_mother_education(field)])
    hukou_candidates = rank_candidates([field for field in source_fields if is_hukou(field)])
    parent_constructable = bool(father_candidates and mother_candidates)
    return [
        field_candidate_item("father_education", "父亲受教育水平", father_candidates),
        field_candidate_item("mother_education", "母亲受教育水平", mother_candidates),
        {
            "dataset_column": "parent_education",
            "semantic_label": "父母受教育水平",
            "candidate_status": "constructable_needs_review" if parent_constructable else "missing_source_fields",
            "candidates": [],
            "construction_draft": {
                "source_fields": ["father_education", "mother_education"],
                "options": [
                    "max(father_education, mother_education)",
                    "mean(father_education, mother_education)",
                    "separate father/mother coefficients",
                ],
                "decision_status": "requires_human_confirmation",
            },
            "required_next_state": "confirm_parent_education_construction"
            if parent_constructable
            else "locate_father_and_mother_education_fields",
            "can_write_formal_variable_roles": False,
        },
        field_candidate_item("hukou", "户口状态", hukou_candidates),
    ]


def field_candidate_item(dataset_column: str, semantic_label: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "dataset_column": dataset_column,
        "semantic_label": semantic_label,
        "candidate_status": "candidate_found" if candidates else "missing",
        "candidates": candidates[:20],
        "required_next_state": "human_bind_candidate_field" if candidates else "locate_source_field_or_adjust_scope",
        "can_write_formal_variable_roles": False,
    }


def is_father_education(field: dict[str, Any]) -> bool:
    name = str(field.get("name", "")).lower()
    text = f"{name} {field.get('label', '')}"
    return (
        name in {"feduc", "tb4_a_f", "qv102"}
        or ("父亲" in text and contains_education_term(text))
    )


def is_mother_education(field: dict[str, Any]) -> bool:
    name = str(field.get("name", "")).lower()
    text = f"{name} {field.get('label', '')}"
    return (
        name in {"meduc", "tb4_a_m", "qv202"}
        or ("母亲" in text and contains_education_term(text))
    )


def is_hukou(field: dict[str, Any]) -> bool:
    name = str(field.get("name", "")).lower()
    text = f"{name} {field.get('label', '')}"
    return name in {"hukou", "qa2", "urban_hukou"} or "户口" in text or "户籍" in text


def contains_education_term(text: str) -> bool:
    return any(term in text for term in ("最高学历", "教育程度", "受教育", "学历", "教育年限", "文化程度"))


def rank_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def score(field: dict[str, Any]) -> tuple[int, str, str]:
        name = str(field.get("name", "")).lower()
        label = str(field.get("label", ""))
        points = 0
        if "最高学历" in label:
            points += 40
        if name in {"feduc", "meduc", "tb4_a_f", "tb4_a_m"}:
            points += 30
        if "14岁时" in label:
            points += 15
        if "户口" in label:
            points += 20
        return (-points, str(field.get("source_path", "")), name)

    ranked = sorted(candidates, key=score)
    return [format_candidate(field) for field in ranked]


def format_candidate(field: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": field["name"],
        "label": field.get("label", ""),
        "source_path": field.get("source_path", ""),
        "source_type": field.get("source_type", ""),
        "source_root": field.get("source_root", ""),
        "file_name": field.get("file_name", ""),
        "row_count": field.get("row_count"),
        "evidence_level": field.get("evidence_level", "local_stata_metadata"),
        "match_reason": "matched_stata_variable_label",
    }


def write_parent_education_wage_field_source_candidates(
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
        "# P4 字段来源候选审计",
        "",
        f"- 题目：{ledger['topic']}",
        f"- 状态：`{ledger['status']}`",
        f"- 选中数据根目录：`{ledger['source_roots']['selected_root']}`",
        f"- 扫描 .dta 文件数：{ledger['source_roots']['scanned_file_count']}",
        f"- 候选字段数：{ledger['candidate_count']}",
        "- 只读元数据扫描：是",
        "- 正式 VariableRoleSet 写回：否",
        "- 正式 DesignSpec 写回：否",
        "- 正式 RunPlan 写回：否",
        "- 执行回归：否",
        "",
        "## 字段候选",
    ]
    for item in ledger["field_source_candidates"]:
        lines.append(f"- `{item['dataset_column']}` | {item['candidate_status']} | {item['semantic_label']}")
        for candidate in item.get("candidates", [])[:5]:
            lines.append(f"  - `{candidate['name']}` | {candidate['label']} | `{candidate['source_path']}`")
    lines.extend(["", "## 过期路径"])
    stale_paths = ledger["source_roots"].get("stale_source_paths") or []
    if stale_paths:
        lines.extend(f"- `{path}`" for path in stale_paths)
    else:
        lines.append("- none")
    lines.extend(["", "## 人工确认"])
    lines.extend(f"- `{item}`" for item in ledger["human_review_required"])
    lines.append("")
    return "\n".join(lines)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

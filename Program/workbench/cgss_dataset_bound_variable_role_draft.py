from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_dataset_bound_variable_role_draft.v1"
DEFAULT_DATA_DISCOVERY_PATH = Path("Results/json/cgss_social_capital_happiness_data_discovery.json")
DEFAULT_VARIABLE_CANDIDATES_PATH = Path("Results/json/cgss_social_capital_happiness_variable_candidates.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_dataset_bound_variable_role_draft.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_dataset_bound_variable_role_draft.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_dataset_bound_variable_role_draft(
    data_discovery: dict[str, Any],
    variable_candidates: dict[str, Any],
    source_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    source_paths = source_paths or {}
    boundary_flags = {
        "modified_formal_variable_roles": False,
        "modified_design_spec": False,
        "modified_run_plan": False,
        "generated_formal_paper": False,
        "wrote_state_product": False,
    }
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": data_discovery.get("topic") or variable_candidates.get("topic") or "",
        "source_artifacts": {
            "data_discovery": {
                "path": source_paths.get("data_discovery", str(DEFAULT_DATA_DISCOVERY_PATH)),
                "schema_version": data_discovery.get("schema_version", ""),
                "status": data_discovery.get("status", ""),
            },
            "variable_candidates": {
                "path": source_paths.get("variable_candidates", str(DEFAULT_VARIABLE_CANDIDATES_PATH)),
                "schema_version": variable_candidates.get("schema_version", ""),
                "status": variable_candidates.get("status", ""),
            },
        },
        "boundary_flags": boundary_flags,
    }
    blocking_reasons = blocking_reasons_for(data_discovery, variable_candidates)
    if blocking_reasons:
        base.update(
            {
                "status": "blocked_missing_dataset_binding",
                "blocking_reasons": blocking_reasons,
                "dataset_binding": {},
                "proposed_roles": {},
                "selected_source_variables": [],
                "review_gates": [],
                "promotion": {"allowed": False, "required_decision": "repair_dataset_binding_inputs"},
            }
        )
        return base

    recommended = data_discovery["dataset_binding_draft"]["recommended_dataset"]
    dataset_binding = {
        "year": str(recommended.get("year", "")),
        "path": recommended.get("path", ""),
        "row_count": recommended.get("row_count"),
        "variable_count": recommended.get("variable_count"),
        "evidence_level": recommended.get("evidence_level", "local_file"),
    }
    role_candidates = variable_candidates.get("role_candidates", {})
    bound_candidates = {
        role: filter_to_dataset(items, dataset_binding) for role, items in role_candidates.items()
    }
    outcome = first_by_name(bound_candidates.get("outcome", []), ["a36"])
    social_items = first_items_by_name(
        bound_candidates.get("social_capital", []),
        ["a33", "a31a", "a31b", "a311"],
    )
    controls = first_items_by_name(
        bound_candidates.get("controls", []),
        ["a2", "a3a", "a7a", "a7b", "a15", "a18", "a21", "a8a", "a8b", "s41"],
    )
    if not outcome or len(social_items) < 2:
        base.update(
            {
                "status": "blocked_missing_dataset_bound_candidates",
                "blocking_reasons": ["missing_dataset_bound_outcome_or_social_capital"],
                "dataset_binding": dataset_binding,
                "proposed_roles": {},
                "selected_source_variables": [],
                "review_gates": ["review_dataset_bound_candidate_extraction"],
                "promotion": {"allowed": False, "required_decision": "repair_variable_candidate_inputs"},
            }
        )
        return base

    selected_names = unique_names([outcome, *social_items, *controls])
    proposed_roles = {
        "outcome": {
            "canonical_name": "happiness",
            "source_variable": outcome["name"],
            "source_label": outcome.get("label", ""),
            "measurement_level": "ordered_happiness_scale_needs_codebook_review",
            "why_selected": "这个题项直接测量居民对自身生活是否幸福的判断，和题目里的主观幸福感概念最贴近；进入正式模型前还要核对编码方向、缺失值和有序等级。",
            "why_not_final": "这是草案层变量选择，尚未经过人工确认、编码表复核和文献口径核验。",
        },
        "treatment": {
            "canonical_name": "social_capital_index_draft",
            "source_items": [item["name"] for item in social_items],
            "source_labels": {item["name"]: item.get("label", "") for item in social_items},
            "dimensions": {
                "general_trust": item_name_if_present(social_items, "a33"),
                "neighborhood_ties": item_name_if_present(social_items, "a31a"),
                "friend_ties": item_name_if_present(social_items, "a31b"),
                "leisure_social_participation": item_name_if_present(social_items, "a311"),
            },
            "construction": "先保留多维题项，人工确认后再决定是否合成指数或分维度回归。",
            "why_selected": "社会资本不是单一题项：信任、邻里社交、朋友社交和休闲社交分别覆盖信任与网络互动两个核心维度。先按多维结构进入草案，比直接合成黑箱指数更稳。",
            "why_not_final": "指数构造、标准化方向、反向题处理和维度权重需要文献支持与人工确认。",
        },
        "controls": {
            "source_items": [item["name"] for item in controls],
            "source_labels": {item["name"]: item.get("label", "") for item in controls},
            "role_mapping": {
                "gender": sources_present(controls, ["a2"]),
                "age": sources_present(controls, ["a3a"]),
                "education": sources_present(controls, ["a7a", "a7b"]),
                "health": sources_present(controls, ["a15"]),
                "hukou": sources_present(controls, ["a18", "a21"]),
                "income": sources_present(controls, ["a8a", "a8b"]),
                "province_fixed_effect": sources_present(controls, ["s41"]),
            },
            "why_selected": "这些变量覆盖人口学、教育、人力资本、收入、健康、户籍和地区差异，是社会资本与幸福感关系中最容易造成混杂因素的一组基础控制。",
            "why_not_final": "控制变量集合仍需结合文献、缺失率、变量编码和样本量损耗做人工确认。",
        },
    }
    base.update(
        {
            "status": "needs_human_dataset_bound_role_review",
            "blocking_reasons": [],
            "dataset_binding": dataset_binding,
            "proposed_roles": proposed_roles,
            "selected_source_variables": selected_names,
            "excluded_candidate_counts_by_year": excluded_counts_by_year(role_candidates, dataset_binding),
            "review_gates": [
                "outcome_coding_and_scale_review",
                "social_capital_index_construction",
                "control_set_completeness",
                "missingness_and_sample_loss_review",
                "literature_support_required",
            ],
            "promotion": {
                "allowed": False,
                "required_decision": "human_approve_dataset_bound_variable_roles",
                "would_write_if_approved": "state/product/variable_roles.json",
            },
            "next_tasks": [
                "human_review_dataset_bound_variable_roles",
                "promote_variable_roles_after_approval",
                "build_cgss_design_spec_draft",
            ],
        }
    )
    return base


def blocking_reasons_for(data_discovery: dict[str, Any], variable_candidates: dict[str, Any]) -> list[str]:
    reasons = []
    if data_discovery.get("status") != "needs_human_dataset_binding_review":
        reasons.append("dataset_binding_not_reviewable")
    recommended = data_discovery.get("dataset_binding_draft", {}).get("recommended_dataset")
    if not recommended:
        reasons.append("missing_recommended_dataset")
    if variable_candidates.get("status") != "needs_human_review":
        reasons.append("variable_candidates_not_reviewable")
    if "role_candidates" not in variable_candidates:
        reasons.append("missing_role_candidates")
    return reasons


def filter_to_dataset(items: list[dict[str, Any]], dataset_binding: dict[str, Any]) -> list[dict[str, Any]]:
    path = dataset_binding.get("path")
    year = str(dataset_binding.get("year", ""))
    exact = [item for item in items if item.get("dataset_path") == path]
    if exact:
        return exact
    return [item for item in items if str(item.get("year", "")) == year]


def first_by_name(items: list[dict[str, Any]], names: list[str]) -> dict[str, Any] | None:
    for name in names:
        for item in items:
            if item.get("name") == name:
                return item
    return items[0] if items else None


def first_items_by_name(items: list[dict[str, Any]], names: list[str]) -> list[dict[str, Any]]:
    selected = []
    for name in names:
        for item in items:
            if item.get("name") == name and item not in selected:
                selected.append(item)
                break
    return selected


def item_name_if_present(items: list[dict[str, Any]], name: str) -> str | None:
    return name if any(item.get("name") == name for item in items) else None


def sources_present(items: list[dict[str, Any]], names: list[str]) -> list[str]:
    available = {item.get("name") for item in items}
    return [name for name in names if name in available]


def unique_names(items: list[dict[str, Any]]) -> list[str]:
    names = []
    for item in items:
        name = item.get("name")
        if name and name not in names:
            names.append(name)
    return names


def excluded_counts_by_year(
    role_candidates: dict[str, list[dict[str, Any]]],
    dataset_binding: dict[str, Any],
) -> dict[str, int]:
    selected_year = str(dataset_binding.get("year", ""))
    counts: dict[str, int] = {}
    for items in role_candidates.values():
        for item in items:
            year = str(item.get("year", ""))
            if year and year != selected_year:
                counts[year] = counts.get(year, 0) + 1
    return counts


def write_dataset_bound_role_draft_outputs(
    project_root: Path, draft: dict[str, Any], result_path: Path, review_path: Path
) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(draft), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(draft: dict[str, Any]) -> str:
    lines = [
        "# CGSS DatasetBinding 后变量角色草案",
        "",
        f"- 题目：{draft.get('topic', '')}",
        f"- 状态：{draft['status']}",
        "- 正式变量角色写回：不写正式变量角色",
    ]
    if draft["blocking_reasons"]:
        lines.extend(["", "## 阻断原因"])
        for reason in draft["blocking_reasons"]:
            lines.append(f"- `{reason}`")
        return "\n".join(lines) + "\n"

    dataset = draft["dataset_binding"]
    outcome = draft["proposed_roles"]["outcome"]
    treatment = draft["proposed_roles"]["treatment"]
    controls = draft["proposed_roles"]["controls"]
    lines.extend(
        [
            "",
            "## 数据绑定",
            f"- 推荐数据：CGSS{dataset['year']} `{dataset['path']}`",
            f"- 样本量：{dataset.get('row_count')}；字段数：{dataset.get('variable_count')}",
            "- 规则：本草案只读取推荐数据集对应年份的字段画像，其他年份只作为后续稳健性或口径对齐候选。",
            "",
            "## 因变量",
            f"- `{outcome['canonical_name']}` <- `{outcome['source_variable']}`",
            f"- 题项：{outcome['source_label']}",
            f"- 理由：{outcome['why_selected']}",
            "",
            "## 核心解释变量",
            f"- `{treatment['canonical_name']}`",
            f"- 来源题项：{', '.join(f'`{item}`' for item in treatment['source_items'])}",
            f"- 理由：{treatment['why_selected']}",
            "",
            "## 控制变量",
            f"- 来源题项：{', '.join(f'`{item}`' for item in controls['source_items'])}",
            f"- 理由：{controls['why_selected']}",
            "",
            "## 审阅门禁",
        ]
    )
    for gate in draft["review_gates"]:
        lines.append(f"- `{gate}`")
    lines.extend(
        [
            "",
            "## 下一步",
            "- 人工确认变量角色后，才允许进入 DesignSpec 草案。",
            "- 未确认前，不写 `state/product/variable_roles.json`。",
        ]
    )
    return "\n".join(lines) + "\n"

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml

from Product.backend.design_spec_service import has_approved_design_spec, has_approved_run_plan
from Product.backend.variable_role_service import has_approved_variable_role_set
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


STATUS_VALUES = {"completed", "in_progress", "blocked", "not_started"}
DATASET_SUFFIXES = {".csv", ".dta", ".xlsx", ".xls", ".sav", ".parquet", ".feather"}


def mock_meta(service: str) -> dict[str, str]:
    return {
        "evidence_level": "mock",
        "service": service,
        "generated_at": utc_now(),
        "note": "Phase A skeleton response; not a verified research fact.",
    }


def local_file_meta(service: str) -> dict[str, str]:
    return {
        "evidence_level": "local_file",
        "service": service,
        "generated_at": utc_now(),
    }


def project_identity(project: dict[str, Any]) -> dict[str, str]:
    return {
        "id": project["id"],
        "slug": project["slug"],
        "title": project["title"],
        "question": project.get("question", ""),
    }


def get_project_overview(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    root = Path(project.get("project_root") or project["root"]).resolve()
    dataset_count = count_local_datasets(root)
    variable_roles_confirmed = has_approved_variable_role_set(root)
    design_spec_confirmed = has_approved_design_spec(root)
    run_plan_confirmed = has_approved_run_plan(root)
    return {
        "_meta": mock_meta("overview_service"),
        "project": project_identity(project),
        "research_question": project.get("question", ""),
        "current_stage": "overview",
        "overall_progress": 0.1,
        "workflow_contract": build_workflow_contract(
            dataset_count,
            variable_roles_confirmed,
            design_spec_confirmed,
            run_plan_confirmed,
        ),
        "next_action": {
            "label": "补充数据与变量信息",
            "href": "#view-data-variables",
        },
        "stage_summaries": [
            {
                "stage_id": "data",
                "title": "数据与变量",
                "status": "in_progress",
                "progress": 0.1,
                "summary": "等待登记数据源、样本口径和核心变量。",
            },
            {
                "stage_id": "design",
                "title": "研究设计",
                "status": "not_started",
                "progress": 0.0,
                "summary": "等待确认变量角色、识别策略和基准模型。",
            },
            {
                "stage_id": "execution",
                "title": "实证执行",
                "status": "not_started",
                "progress": 0.0,
                "summary": "Phase A 尚未接入真实执行器。",
            },
            {
                "stage_id": "draft",
                "title": "论文草稿",
                "status": "not_started",
                "progress": 0.0,
                "summary": "草稿页将读取 Manuscripts/generated/ 的本地文件。",
            },
            {
                "stage_id": "artifacts",
                "title": "产物与复现",
                "status": "not_started",
                "progress": 0.0,
                "summary": "等待后续登记结果、表格、图形和复现链路。",
            },
            {
                "stage_id": "agents",
                "title": "Agent 控制台",
                "status": "in_progress",
                "progress": 0.2,
                "summary": "已定义流水线角色和研究维度角色的分离骨架。",
            },
        ],
    }


def count_local_datasets(root: Path) -> int:
    data_root = root / "Data"
    if not data_root.exists():
        return 0
    return sum(
        1
        for path in data_root.rglob("*")
        if path.is_file() and path.suffix.lower() in DATASET_SUFFIXES
    )


def build_workflow_contract(
    dataset_count: int,
    variable_roles_confirmed: bool = False,
    design_spec_confirmed: bool = False,
    run_plan_confirmed: bool = False,
) -> dict[str, Any]:
    has_dataset = dataset_count > 0
    blockers = []
    if not variable_roles_confirmed:
        blockers.append("variable_roles_unconfirmed")
    if not design_spec_confirmed:
        blockers.append("design_unconfirmed")
    if not run_plan_confirmed:
        blockers.append("run_plan_missing")
    next_action = next_workflow_action(has_dataset, variable_roles_confirmed, design_spec_confirmed, run_plan_confirmed)
    return {
        "primary_workspace": "data-design",
        "canonical_stages": [
            {
                "id": "dataset",
                "name": "Dataset",
                "workspace": "data-design",
                "status": "completed" if has_dataset else "blocked",
            },
            {
                "id": "variable_roles",
                "name": "VariableRoleSet",
                "workspace": "data-design",
                "status": "completed"
                if variable_roles_confirmed
                else ("requires_confirmation" if has_dataset else "blocked"),
            },
            {
                "id": "research_question",
                "name": "ResearchQuestion",
                "workspace": "data-design",
                "status": "in_progress",
            },
            {
                "id": "design_spec",
                "name": "DesignSpec",
                "workspace": "data-design",
                "status": "completed"
                if design_spec_confirmed
                else ("requires_confirmation" if variable_roles_confirmed else "blocked"),
            },
            {
                "id": "run_plan",
                "name": "RunPlan",
                "workspace": "execution",
                "status": "completed"
                if run_plan_confirmed
                else ("requires_confirmation" if design_spec_confirmed else "blocked"),
            },
            {
                "id": "run",
                "name": "Run",
                "workspace": "execution",
                "status": "not_started" if run_plan_confirmed else "blocked",
            },
            {
                "id": "results",
                "name": "Results",
                "workspace": "results-draft",
                "status": "not_started",
            },
            {
                "id": "draft",
                "name": "Draft",
                "workspace": "results-draft",
                "status": "not_started",
            },
            {
                "id": "review_export",
                "name": "Review and Export",
                "workspace": "review-export",
                "status": "not_started",
            },
        ],
        "next_action": next_action,
        "run_readiness": {
            "can_start_full_run": variable_roles_confirmed and design_spec_confirmed and run_plan_confirmed,
            "blockers": blockers,
            "development_shortcut_allowed": True,
        },
    }


def next_workflow_action(
    has_dataset: bool,
    variable_roles_confirmed: bool,
    design_spec_confirmed: bool,
    run_plan_confirmed: bool,
) -> dict[str, str]:
    if not variable_roles_confirmed:
        return {
            "id": "confirm_variable_roles",
            "label": "检查并确认变量角色",
            "workspace": "data-design",
            "view": "data-variables",
            "reason": "已发现本地数据，但尚未形成可审计 VariableRoleSet。"
            if has_dataset
            else "尚未发现可用数据集，需要先放入或选择本地数据文件。",
        }
    if not design_spec_confirmed:
        return {
            "id": "confirm_design_spec",
            "label": "确认研究设计",
            "workspace": "data-design",
            "view": "research-design",
            "reason": "变量角色已确认，下一步需要形成可审计 DesignSpec。",
        }
    if not run_plan_confirmed:
        return {
            "id": "confirm_run_plan",
            "label": "确认 Run Plan",
            "workspace": "execution",
            "view": "empirical-execution",
            "reason": "研究设计已确认，下一步需要形成可执行、可审计的 RunPlan。",
        }
    return {
        "id": "start_full_run",
        "label": "启动完整实证执行",
        "workspace": "execution",
        "view": "empirical-execution",
        "reason": "变量角色、研究设计和 RunPlan 均已确认，可以进入完整执行。",
    }


def get_project_journey(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    stages = [
        ("question", "研究问题", "completed", 1.0, "#view-overview"),
        ("data", "数据准备", "in_progress", 0.1, "#view-data-variables"),
        ("variables", "变量定义", "not_started", 0.0, "#view-data-variables"),
        ("design", "研究设计", "not_started", 0.0, "#view-data-variables"),
        ("execution", "实证执行", "not_started", 0.0, "#view-empirical-execution"),
        ("robustness", "稳健性", "not_started", 0.0, "#view-empirical-execution"),
        ("manuscript", "论文草稿", "not_started", 0.0, "#view-paper-draft"),
        ("review", "审查确认", "not_started", 0.0, "#view-artifacts-replication"),
        ("export", "产物复现", "not_started", 0.0, "#view-artifacts-replication"),
    ]
    return {
        "_meta": mock_meta("journey_service"),
        "project": project_identity(project),
        "stages": [
            {"id": stage_id, "name": name, "status": status, "progress": progress, "href": href}
            for stage_id, name, status, progress, href in stages
        ],
    }


def list_project_datasets(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    root = Path(project.get("project_root") or project["root"]).resolve()
    configured_final_dataset = configured_dataset_path(root)
    items: list[dict[str, Any]] = []
    data_root = root / "Data"
    if data_root.exists():
        for path in sorted(data_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in DATASET_SUFFIXES:
                continue
            relative_path = path.resolve().relative_to(root).as_posix()
            stat = path.stat()
            shape = inspect_dataset_shape(path)
            quality_profile = build_dataset_quality_profile(path, shape)
            items.append(
                {
                    "name": path.name,
                    "path": relative_path,
                    "file_type": path.suffix.lower().lstrip("."),
                    "size": stat.st_size,
                    "row_count": shape["row_count"],
                    "column_count": shape["column_count"],
                    "evidence_level": "local_file",
                    "role": "configured_final_dataset"
                    if configured_final_dataset == relative_path
                    else "candidate_dataset",
                    "quality_profile": quality_profile,
                    "updated_at": utc_now(),
                }
            )

    return {
        "_meta": local_file_meta("dataset_service"),
        "project": project_identity(project),
        "items": items,
        "empty_state": {
            "title": "尚未登记数据集",
            "description": "已检查项目 Data 目录，当前没有发现 csv/dta/xlsx/parquet 等可识别数据文件。",
            "next_action": "将数据文件放入 Data/Raw、Data/Interim 或 Data/Final 后刷新。",
        }
        if not items
        else None,
    }


def configured_dataset_path(root: Path) -> str | None:
    paper_path = root / "paper.yaml"
    if not paper_path.exists():
        return None
    payload = yaml.safe_load(paper_path.read_text(encoding="utf-8")) or {}
    configured = payload.get("data", {}).get("final_dataset")
    return str(configured).replace("\\", "/") if configured else None


def inspect_dataset_shape(path: Path) -> dict[str, int | None]:
    if path.suffix.lower() != ".csv":
        return {"row_count": None, "column_count": None}
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return {"row_count": 0, "column_count": 0}
    return {
        "row_count": max(len(rows) - 1, 0),
        "column_count": len(rows[0]),
    }


def build_dataset_quality_profile(path: Path, shape: dict[str, int | None]) -> dict[str, Any]:
    if path.suffix.lower() != ".csv":
        return {
            "evidence_level": "local_file",
            "supported": False,
            "readiness_status": "not_profiled",
            "row_count": shape["row_count"],
            "column_count": shape["column_count"],
            "missing_cells": None,
            "missing_rate": None,
            "numeric_column_count": None,
            "text_column_count": None,
            "columns": [],
            "checks": [
                {
                    "id": "profile_supported",
                    "label": "数据画像支持",
                    "status": "warning",
                    "detail": f"{path.suffix.lower().lstrip('.') or 'unknown'} 暂未接入内容解析。",
                }
            ],
        }

    rows = read_csv_rows(path)
    if not rows:
        return empty_csv_quality_profile()

    headers = rows[0]
    data_rows = rows[1:]
    column_count = len(headers)
    row_count = len(data_rows)
    columns = build_column_profiles(headers, data_rows)
    missing_cells = sum(column["missing_count"] for column in columns)
    total_cells = row_count * column_count
    missing_rate = round(missing_cells / total_cells, 4) if total_cells else 0
    numeric_column_count = sum(1 for column in columns if column["inferred_type"] == "numeric")
    text_column_count = sum(1 for column in columns if column["inferred_type"] == "text")

    if row_count == 0 or column_count == 0:
        readiness_status = "blocked"
    elif missing_cells > 0:
        readiness_status = "needs_review"
    else:
        readiness_status = "ready"

    return {
        "evidence_level": "local_file",
        "supported": True,
        "readiness_status": readiness_status,
        "row_count": row_count,
        "column_count": column_count,
        "missing_cells": missing_cells,
        "missing_rate": missing_rate,
        "numeric_column_count": numeric_column_count,
        "text_column_count": text_column_count,
        "columns": columns,
        "checks": [
            {
                "id": "schema_detected",
                "label": "字段结构",
                "status": "passed" if column_count > 0 else "failed",
                "detail": f"识别到 {column_count} 个字段。",
            },
            {
                "id": "sample_size_checked",
                "label": "样本数量",
                "status": "passed" if row_count > 0 else "failed",
                "detail": f"识别到 {row_count} 行样本。",
            },
            {
                "id": "missing_values_checked",
                "label": "缺失值",
                "status": "warning" if missing_cells > 0 else "passed",
                "detail": f"发现 {missing_cells} 个空单元格。",
            },
        ],
    }


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        return list(csv.reader(handle))


def empty_csv_quality_profile() -> dict[str, Any]:
    return {
        "evidence_level": "local_file",
        "supported": True,
        "readiness_status": "blocked",
        "row_count": 0,
        "column_count": 0,
        "missing_cells": 0,
        "missing_rate": 0,
        "numeric_column_count": 0,
        "text_column_count": 0,
        "columns": [],
        "checks": [
            {
                "id": "schema_detected",
                "label": "字段结构",
                "status": "failed",
                "detail": "CSV 文件为空。",
            }
        ],
    }


def build_column_profiles(headers: list[str], data_rows: list[list[str]]) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    row_count = len(data_rows)
    for index, header in enumerate(headers):
        values = [row[index] if index < len(row) else "" for row in data_rows]
        non_missing = [value.strip() for value in values if value.strip()]
        missing_count = row_count - len(non_missing)
        inferred_type = infer_column_type(non_missing)
        profiles.append(
            {
                "name": header or f"column_{index + 1}",
                "index": index,
                "inferred_type": inferred_type,
                "missing_count": missing_count,
                "missing_rate": round(missing_count / row_count, 4) if row_count else 0,
                "sample_values": non_missing[:3],
            }
        )
    return profiles


def infer_column_type(values: list[str]) -> str:
    if not values:
        return "empty"
    for value in values:
        try:
            float(value)
        except ValueError:
            return "text"
    return "numeric"


def get_project_design(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    return {
        "_meta": mock_meta("design_service"),
        "project": project_identity(project),
        "research_question": project.get("question", ""),
        "variables": {
            "outcome": [],
            "treatment": [],
            "controls": [],
            "fixed_effects": [],
            "notes": "Phase A 不推断真实变量，仅提供可渲染骨架。",
        },
        "strategies": [
            {
                "id": "baseline_panel",
                "name": "双向固定效应基准模型",
                "status": "candidate",
                "evidence_level": "mock",
            },
            {
                "id": "iv_or_policy_shift",
                "name": "工具变量或政策冲击识别",
                "status": "candidate",
                "evidence_level": "mock",
            },
        ],
        "model_spec": {
            "status": "pending_confirmation",
            "formula": "",
            "estimator": "",
        },
        "pending_confirmations": [
            "确认被解释变量的测度口径。",
            "确认工业机器人暴露度的构造方式。",
            "确认固定效应、聚类标准误和样本范围。",
        ],
    }

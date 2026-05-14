from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

import yaml

from Product.backend.design_spec_service import has_approved_design_spec, has_approved_run_plan
from Product.backend.variable_role_service import has_approved_variable_role_set
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


STATUS_VALUES = {"completed", "in_progress", "blocked", "not_started"}
DATASET_SUFFIXES = {".csv", ".dta", ".xlsx", ".xls", ".sav", ".parquet", ".feather"}
EXTERNAL_CATALOG_LIMIT = 40
EXTERNAL_CSV_PREVIEW_ROWS = 200
DATASET_IMPORT_PREFLIGHT_PATH = Path("state/product/dataset_import_preflights.json")


class CloudUploadRequiredError(RuntimeError):
    pass


class DatasetPreflightStateError(RuntimeError):
    pass


class DatasetImportProfileStateError(RuntimeError):
    pass


class DatasetImportSourceChangedError(RuntimeError):
    pass


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
        "external_catalog": build_external_data_catalog(),
        "external_import_preflight": latest_external_import_preflight(root),
        "external_import_profile": latest_external_import_profile(root),
        "empty_state": {
            "title": "尚未登记数据集",
            "description": "已检查项目 Data 目录，当前没有发现 csv/dta/xlsx/parquet 等可识别数据文件。",
            "next_action": "将数据文件放入 Data/Raw、Data/Interim 或 Data/Final 后刷新。",
        }
        if not items
        else None,
    }


def save_external_dataset_bind_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    source_path: str,
    strategy: str = "copy_to_project_raw",
    note: str = "",
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    source, catalog_root = validate_external_source_path(Path(source_path))
    if strategy != "copy_to_project_raw":
        raise ValueError(f"Unsupported external dataset bind strategy: {strategy}")

    preflight = build_external_dataset_bind_preflight(project_root, source, catalog_root, strategy, note)
    manifest = load_dataset_import_preflight_manifest(project_root)
    manifest.setdefault("preflights", {})[preflight["id"]] = preflight
    manifest["latest_preflight_id"] = preflight["id"]
    manifest["updated_at"] = utc_now()
    write_dataset_import_preflight_manifest(project_root, manifest)
    return {
        "_meta": local_file_meta("dataset_import_preflight_service"),
        "project": project_identity(project),
        "preflight": preflight,
    }


def apply_external_dataset_bind_preflight(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    preflight_id: str,
    action: str,
    runtime_mode: str = "local",
    note: str = "",
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    manifest = load_dataset_import_preflight_manifest(project_root)
    preflight = manifest.get("preflights", {}).get(preflight_id)
    if not isinstance(preflight, dict):
        raise KeyError(preflight_id)
    if preflight.get("status") != "ready_for_review":
        raise DatasetPreflightStateError(f"Preflight {preflight_id} is {preflight.get('status')}")
    if runtime_mode == "cloud":
        raise CloudUploadRequiredError("Cloud runtime cannot read local filesystem paths; upload data first.")
    if runtime_mode != "local":
        raise ValueError(f"Unsupported runtime_mode: {runtime_mode}")
    if action not in {"copy_to_project_raw", "bind_external_reference", "cancel"}:
        raise ValueError(f"Unsupported dataset import action: {action}")

    source, _catalog_root = validate_external_source_path(Path(preflight["source"]["path"]))
    source_hash = file_sha256(source)
    timestamp = utc_now()
    dataset_import = {
        "id": f"dataset_import_{preflight_id.removeprefix('dataset_bind_preflight_')}",
        "preflight_id": preflight_id,
        "status": "cancelled" if action == "cancel" else "applied",
        "action": action,
        "runtime_mode": runtime_mode,
        "evidence_level": "local_file",
        "note": note,
        "source": {
            **preflight["source"],
            "sha256": source_hash,
        },
        "target": preflight["target"],
        "created_project_file": False,
        "will_mutate_source": False,
        "created_at": timestamp,
        "updated_at": timestamp,
        "checks": [],
    }

    if action == "copy_to_project_raw":
        target = (project_root / preflight["target"]["path"]).resolve()
        try:
            target.relative_to(project_root)
        except ValueError as exc:
            raise PermissionError(target) from exc
        if target.exists():
            raise FileExistsError(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        dataset_import["target"] = {
            **preflight["target"],
            "exists": True,
            "size": target.stat().st_size,
            "sha256": file_sha256(target),
            "evidence_level": "local_file",
        }
        dataset_import["created_project_file"] = True
        dataset_import["checks"] = [
            {
                "id": "project_file_created",
                "label": "项目内文件已创建",
                "status": "passed",
                "detail": preflight["target"]["path"],
            },
            {
                "id": "source_hash_preserved",
                "label": "源文件哈希已记录",
                "status": "passed",
                "detail": source_hash,
            },
        ]
    elif action == "bind_external_reference":
        dataset_import["binding"] = {
            "mode": "external_reference",
            "path": preflight["source"]["path"],
            "read_only": True,
            "warning": "本项目依赖本机外部路径；线上版本必须改用上传或云对象存储。",
        }
        dataset_import["checks"] = [
            {
                "id": "external_reference_recorded",
                "label": "外部引用已登记",
                "status": "passed",
                "detail": preflight["source"]["path"],
            }
        ]
    else:
        dataset_import["checks"] = [
            {
                "id": "preflight_cancelled",
                "label": "预检已取消",
                "status": "passed",
                "detail": "未创建项目文件，未绑定外部引用。",
            }
        ]

    preflight["status"] = dataset_import["status"]
    preflight["dataset_import"] = dataset_import
    preflight["updated_at"] = timestamp
    manifest.setdefault("dataset_imports", {})[dataset_import["id"]] = dataset_import
    manifest["latest_import_id"] = dataset_import["id"]
    manifest["latest_preflight_id"] = preflight_id
    manifest["updated_at"] = timestamp
    write_dataset_import_preflight_manifest(project_root, manifest)
    return {
        "_meta": local_file_meta("dataset_import_apply_service"),
        "project": project_identity(project),
        "preflight": preflight,
        "dataset_import": dataset_import,
    }


def profile_external_dataset_import(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    dataset_import_id: str,
    row_limit: int = EXTERNAL_CSV_PREVIEW_ROWS,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    manifest = load_dataset_import_preflight_manifest(project_root)
    dataset_import = manifest.get("dataset_imports", {}).get(dataset_import_id)
    if not isinstance(dataset_import, dict):
        raise KeyError(dataset_import_id)
    if dataset_import.get("status") != "applied":
        raise DatasetImportProfileStateError(f"Dataset import {dataset_import_id} is {dataset_import.get('status')}")

    dataset_path = resolve_dataset_import_profile_path(project_root, dataset_import)
    expected_hash = expected_dataset_import_hash(dataset_import)
    actual_hash = file_sha256(dataset_path)
    if expected_hash and actual_hash != expected_hash:
        raise DatasetImportSourceChangedError(
            f"Dataset import {dataset_import_id} source hash changed from {expected_hash} to {actual_hash}."
        )

    profile = build_dataset_import_profile(project_root, dataset_import, dataset_path, actual_hash, row_limit)
    manifest.setdefault("dataset_import_profiles", {})[profile["id"]] = profile
    manifest["latest_import_profile_id"] = profile["id"]
    manifest["latest_import_id"] = dataset_import_id
    manifest["updated_at"] = utc_now()
    dataset_import["field_profile"] = {
        "id": profile["id"],
        "status": profile["status"],
        "readiness_status": profile["readiness_status"],
        "evidence_level": "local_file",
        "can_feed_variable_roles": False,
    }
    dataset_import["updated_at"] = profile["updated_at"]
    write_dataset_import_preflight_manifest(project_root, manifest)
    return {
        "_meta": local_file_meta("dataset_import_profile_service"),
        "project": project_identity(project),
        "dataset_import": dataset_import,
        "dataset_import_profile": profile,
    }


def resolve_dataset_import_profile_path(project_root: Path, dataset_import: dict[str, Any]) -> Path:
    action = dataset_import.get("action")
    if action == "copy_to_project_raw":
        target_path = dataset_import.get("target", {}).get("path")
        if not target_path:
            raise FileNotFoundError("Missing copied dataset target path.")
        dataset_path = (project_root / target_path).resolve()
        try:
            dataset_path.relative_to(project_root)
        except ValueError as exc:
            raise PermissionError(dataset_path) from exc
        if not dataset_path.exists() or not dataset_path.is_file():
            raise FileNotFoundError(dataset_path)
        return dataset_path
    if action == "bind_external_reference":
        source_path = dataset_import.get("binding", {}).get("path") or dataset_import.get("source", {}).get("path")
        if not source_path:
            raise FileNotFoundError("Missing external dataset source path.")
        source, _catalog_root = validate_external_source_path(Path(source_path))
        return source
    raise DatasetImportProfileStateError(f"Dataset import action {action} cannot be profiled.")


def expected_dataset_import_hash(dataset_import: dict[str, Any]) -> str | None:
    if dataset_import.get("action") == "copy_to_project_raw":
        return dataset_import.get("target", {}).get("sha256") or dataset_import.get("source", {}).get("sha256")
    return dataset_import.get("source", {}).get("sha256")


def build_dataset_import_profile(
    project_root: Path,
    dataset_import: dict[str, Any],
    dataset_path: Path,
    actual_hash: str,
    row_limit: int,
) -> dict[str, Any]:
    timestamp = utc_now()
    profile_id = f"dataset_import_profile_{dataset_import['id'].removeprefix('dataset_import_')}"
    source = {
        "name": dataset_import.get("source", {}).get("name") or dataset_path.name,
        "path": str(dataset_path),
        "file_type": dataset_path.suffix.lower().lstrip("."),
        "size": dataset_path.stat().st_size,
        "sha256": actual_hash,
        "evidence_level": "local_file",
    }
    binding = dataset_import.get("binding")

    if dataset_path.suffix.lower() == ".csv":
        rows, sampled = read_csv_preview_rows(dataset_path, row_limit)
        if rows:
            headers = rows[0]
            data_rows = rows[1:]
            quality_profile = build_dataset_quality_profile_from_rows(headers, data_rows)
            quality_profile["profile_scope"] = "dataset_import_profile"
            quality_profile["row_count_source"] = "sampled_preview" if sampled else "complete_preview"
            if sampled:
                quality_profile["checks"].append(
                    {
                        "id": "preview_limited",
                        "label": "画像范围",
                        "status": "warning",
                        "detail": f"仅读取前 {row_limit} 行用于字段画像。",
                    }
                )
        else:
            quality_profile = empty_csv_quality_profile()
            quality_profile["profile_scope"] = "dataset_import_profile"
            quality_profile["row_count_source"] = "empty"

        fields = quality_profile.get("columns", [])
        status = "profiled" if quality_profile.get("supported") and fields else "blocked"
        readiness_status = quality_profile.get("readiness_status", "blocked")
        checks = [
            {
                "id": "source_hash_verified",
                "label": "来源哈希一致",
                "status": "passed",
                "detail": actual_hash,
            },
            {
                "id": "profile_supported",
                "label": "字段画像解析器",
                "status": "passed",
                "detail": "CSV 字段结构已读取。",
            },
            {
                "id": "no_research_state_write",
                "label": "研究状态未改写",
                "status": "passed",
                "detail": "未改写 VariableRoleSet、DesignSpec 或 RunPlan。",
            },
        ]
        blocking_reason = None if status == "profiled" else "CSV 文件为空或缺少字段。"
    else:
        file_type = dataset_path.suffix.lower().lstrip(".") or "unknown"
        quality_profile = build_dataset_quality_profile(
            dataset_path,
            {"row_count": None, "column_count": None},
        )
        quality_profile["profile_scope"] = "dataset_import_profile"
        fields = []
        status = "blocked"
        readiness_status = "not_profiled"
        blocking_reason = f"{file_type} 暂未接入安全字段读取器。"
        checks = [
            {
                "id": "source_hash_verified",
                "label": "来源哈希一致",
                "status": "passed",
                "detail": actual_hash,
            },
            {
                "id": "profile_supported",
                "label": "字段画像解析器",
                "status": "warning",
                "detail": blocking_reason,
            },
            {
                "id": "no_fake_fields",
                "label": "未伪造字段",
                "status": "passed",
                "detail": "解析器未接入前字段列表保持为空。",
            },
        ]

    return {
        "id": profile_id,
        "dataset_import_id": dataset_import["id"],
        "status": status,
        "readiness_status": readiness_status,
        "evidence_level": "local_file",
        "profile_scope": "dataset_import_profile",
        "row_limit": row_limit,
        "source": source,
        "target": dataset_import.get("target", {}),
        "binding": binding
        or {
            "mode": "project_file",
            "path": dataset_import.get("target", {}).get("path"),
            "read_only": False,
        },
        "quality_profile": quality_profile,
        "fields": fields,
        "checks": checks,
        "blocking_reason": blocking_reason,
        "can_feed_variable_roles": False,
        "next_action": "先人工审阅字段画像，再手动确认 VariableRoleSet。",
        "manifest_path": DATASET_IMPORT_PREFLIGHT_PATH.as_posix(),
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def build_external_dataset_bind_preflight(
    project_root: Path,
    source: Path,
    catalog_root: Path,
    strategy: str,
    note: str,
) -> dict[str, Any]:
    relative_source = source.relative_to(catalog_root)
    target_relative_path = Path("Data/Raw") / source.name
    target_absolute_path = (project_root / target_relative_path).resolve()
    try:
        target_absolute_path.relative_to(project_root)
    except ValueError as exc:
        raise PermissionError(target_absolute_path) from exc

    timestamp = utc_now()
    stat = source.stat()
    preflight_id = build_dataset_preflight_id(source, strategy)
    checks = [
        {
            "id": "source_exists",
            "label": "源文件存在",
            "status": "passed",
            "detail": "已确认真实数据文件位于候选池内。",
        },
        {
            "id": "source_in_external_catalog",
            "label": "候选池边界",
            "status": "passed",
            "detail": f"相对路径：{relative_source.as_posix()}",
        },
        {
            "id": "target_inside_project",
            "label": "目标路径边界",
            "status": "passed",
            "detail": f"预检目标：{target_relative_path.as_posix()}",
        },
        {
            "id": "preflight_only",
            "label": "仅生成预检",
            "status": "passed",
            "detail": "本步骤不会复制、移动、链接或修改真实数据文件。",
        },
    ]
    return {
        "id": preflight_id,
        "status": "ready_for_review",
        "evidence_level": "local_file",
        "strategy": strategy,
        "note": note,
        "source": {
            "name": source.name,
            "path": str(source),
            "relative_path": relative_source.as_posix(),
            "collection": external_collection_label(relative_source),
            "file_type": source.suffix.lower().lstrip("."),
            "size": stat.st_size,
            "evidence_level": "local_file",
            "read_only": True,
        },
        "target": {
            "path": target_relative_path.as_posix(),
            "absolute_path": str(target_absolute_path),
            "exists": target_absolute_path.exists(),
            "evidence_level": "local_file",
        },
        "checks": checks,
        "will_mutate_source": False,
        "will_create_project_file": False,
        "can_apply": False,
        "manifest_path": DATASET_IMPORT_PREFLIGHT_PATH.as_posix(),
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def validate_external_source_path(source_path: Path) -> tuple[Path, Path]:
    source = source_path.expanduser().absolute()
    source_resolved = source.resolve()
    if source.suffix.lower() not in DATASET_SUFFIXES:
        raise ValueError(source)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)

    for root in external_data_library_roots():
        catalog_root = root.expanduser().absolute()
        catalog_root_resolved = catalog_root.resolve()
        if not catalog_root.exists() or not catalog_root.is_dir():
            continue
        try:
            source_resolved.relative_to(catalog_root_resolved)
        except ValueError:
            continue
        return source, catalog_root
    raise PermissionError(source)


def build_dataset_preflight_id(source: Path, strategy: str) -> str:
    digest = hashlib.sha1(f"{source}|{strategy}".encode("utf-8")).hexdigest()[:12]
    return f"dataset_bind_preflight_{digest}"


def latest_external_import_preflight(project_root: Path) -> dict[str, Any] | None:
    manifest = load_dataset_import_preflight_manifest(project_root)
    latest_id = manifest.get("latest_preflight_id")
    if not latest_id:
        return None
    preflight = manifest.get("preflights", {}).get(latest_id)
    return preflight if isinstance(preflight, dict) else None


def latest_external_import_profile(project_root: Path) -> dict[str, Any] | None:
    manifest = load_dataset_import_preflight_manifest(project_root)
    latest_id = manifest.get("latest_import_profile_id")
    if not latest_id:
        return None
    profile = manifest.get("dataset_import_profiles", {}).get(latest_id)
    return profile if isinstance(profile, dict) else None


def load_dataset_import_preflight_manifest(project_root: Path) -> dict[str, Any]:
    path = project_root / DATASET_IMPORT_PREFLIGHT_PATH
    if not path.exists():
        return {
            "preflights": {},
            "dataset_imports": {},
            "dataset_import_profiles": {},
            "latest_preflight_id": None,
            "latest_import_id": None,
            "latest_import_profile_id": None,
            "updated_at": None,
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "preflights": {},
            "dataset_imports": {},
            "dataset_import_profiles": {},
            "latest_preflight_id": None,
            "latest_import_id": None,
            "latest_import_profile_id": None,
            "updated_at": None,
        }
    if not isinstance(payload, dict):
        return {
            "preflights": {},
            "dataset_imports": {},
            "dataset_import_profiles": {},
            "latest_preflight_id": None,
            "latest_import_id": None,
            "latest_import_profile_id": None,
            "updated_at": None,
        }
    payload.setdefault("preflights", {})
    payload.setdefault("dataset_imports", {})
    payload.setdefault("dataset_import_profiles", {})
    payload.setdefault("latest_preflight_id", None)
    payload.setdefault("latest_import_id", None)
    payload.setdefault("latest_import_profile_id", None)
    payload.setdefault("updated_at", None)
    return payload


def write_dataset_import_preflight_manifest(project_root: Path, manifest: dict[str, Any]) -> None:
    path = project_root / DATASET_IMPORT_PREFLIGHT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_external_data_catalog() -> dict[str, Any]:
    roots = external_data_library_roots()
    root = next((candidate for candidate in roots if candidate.exists() and candidate.is_dir()), None)
    if root is None:
        configured_root = roots[0] if roots else None
        return {
            "evidence_level": "local_file",
            "exists": False,
            "read_only": True,
            "root": str(configured_root) if configured_root else None,
            "items": [],
            "total_count": 0,
            "empty_state": {
                "title": "尚未找到真实数据仓库",
                "description": "可通过 EMPIRICAL_DATA_LIBRARY_ROOT 指向本机实证数据库目录。",
            },
        }

    items: list[dict[str, Any]] = []
    total_count = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in DATASET_SUFFIXES:
            continue
        total_count += 1
        if len(items) >= EXTERNAL_CATALOG_LIMIT:
            continue
        relative_path = path.relative_to(root).as_posix()
        stat = path.stat()
        shape, quality_profile = build_external_dataset_preview(path)
        items.append(
            {
                "name": path.name,
                "path": str(path),
                "relative_path": relative_path,
                "collection": external_collection_label(path.relative_to(root)),
                "file_type": path.suffix.lower().lstrip("."),
                "size": stat.st_size,
                "row_count": shape["row_count"],
                "column_count": shape["column_count"],
                "evidence_level": "local_file",
                "role": "external_candidate_dataset",
                "scope": "external_data_library",
                "read_only": True,
                "quality_profile": quality_profile,
                "updated_at": utc_now(),
            }
        )

    return {
        "evidence_level": "local_file",
        "exists": True,
        "read_only": True,
        "root": str(root),
        "items": items,
        "total_count": total_count,
        "limit": EXTERNAL_CATALOG_LIMIT,
        "empty_state": None
        if items
        else {
            "title": "真实数据仓库为空",
            "description": "已找到目录，但没有发现 csv/dta/xlsx/parquet 等可识别数据文件。",
        },
    }


def external_data_library_roots() -> list[Path]:
    configured = os.environ.get("EMPIRICAL_DATA_LIBRARY_ROOT")
    if configured:
        return [Path(item).expanduser() for item in configured.split(os.pathsep) if item.strip()]
    return [Path.home() / "Desktop" / "实证数据库"]


def external_collection_label(relative_path: Path) -> str:
    parts = relative_path.parts
    if len(parts) >= 2:
        return " / ".join(parts[:2])
    return parts[0] if parts else "未分组"


def build_external_dataset_preview(path: Path) -> tuple[dict[str, int | None], dict[str, Any]]:
    if path.suffix.lower() != ".csv":
        shape = {"row_count": None, "column_count": None}
        return shape, {
            "evidence_level": "local_file",
            "supported": False,
            "profile_scope": "catalog_preview",
            "readiness_status": "not_profiled",
            "row_count": None,
            "column_count": None,
            "missing_cells": None,
            "missing_rate": None,
            "numeric_column_count": None,
            "text_column_count": None,
            "columns": [],
            "checks": [
                {
                    "id": "profile_supported",
                    "label": "候选池画像支持",
                    "status": "warning",
                    "detail": f"{path.suffix.lower().lstrip('.') or 'unknown'} 暂未接入预览解析。",
                }
            ],
        }

    rows, sampled = read_csv_preview_rows(path, EXTERNAL_CSV_PREVIEW_ROWS)
    if not rows:
        profile = empty_csv_quality_profile()
        profile["profile_scope"] = "catalog_preview"
        profile["row_count_source"] = "empty"
        return {"row_count": 0, "column_count": 0}, profile

    headers = rows[0]
    data_rows = rows[1:]
    shape = {
        "row_count": len(data_rows),
        "column_count": len(headers),
    }
    profile = build_dataset_quality_profile_from_rows(headers, data_rows)
    profile["profile_scope"] = "catalog_preview"
    profile["row_count_source"] = "sampled_preview" if sampled else "complete_preview"
    if sampled:
        profile["checks"].append(
            {
                "id": "preview_limited",
                "label": "预览范围",
                "status": "warning",
                "detail": f"仅读取前 {EXTERNAL_CSV_PREVIEW_ROWS} 行用于候选池画像。",
            }
        )
    return shape, profile


def read_csv_preview_rows(path: Path, row_limit: int) -> tuple[list[list[str]], bool]:
    rows: list[list[str]] = []
    sampled = False
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        reader = csv.reader(handle)
        for index, row in enumerate(reader):
            if index > row_limit:
                sampled = True
                break
            rows.append(row)
    return rows, sampled


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
    return build_dataset_quality_profile_from_rows(headers, data_rows)


def build_dataset_quality_profile_from_rows(headers: list[str], data_rows: list[list[str]]) -> dict[str, Any]:
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

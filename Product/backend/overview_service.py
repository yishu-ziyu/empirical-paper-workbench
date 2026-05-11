from __future__ import annotations

from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


STATUS_VALUES = {"completed", "in_progress", "blocked", "not_started"}


def mock_meta(service: str) -> dict[str, str]:
    return {
        "evidence_level": "mock",
        "service": service,
        "generated_at": utc_now(),
        "note": "Phase A skeleton response; not a verified research fact.",
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
    return {
        "_meta": mock_meta("overview_service"),
        "project": project_identity(project),
        "research_question": project.get("question", ""),
        "current_stage": "overview",
        "overall_progress": 0.1,
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


def get_project_journey(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    stages = [
        ("question", "研究问题", "completed", 1.0, "#view-overview"),
        ("data", "数据准备", "in_progress", 0.1, "#view-data-variables"),
        ("variables", "变量定义", "not_started", 0.0, "#view-data-variables"),
        ("design", "研究设计", "not_started", 0.0, "#view-design"),
        ("execution", "实证执行", "not_started", 0.0, "#view-execution"),
        ("robustness", "稳健性", "not_started", 0.0, "#view-execution"),
        ("manuscript", "论文草稿", "not_started", 0.0, "#view-drafts"),
        ("review", "审查确认", "not_started", 0.0, "#view-agents"),
        ("export", "产物复现", "not_started", 0.0, "#view-artifacts"),
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
    return {
        "_meta": mock_meta("dataset_service"),
        "project": project_identity(project),
        "items": [],
        "empty_state": {
            "title": "尚未登记数据集",
            "description": "Phase A 只返回可解释空状态；真实上传和 schema 解析留到后续阶段。",
            "next_action": "在数据与变量页登记数据来源、样本口径和变量字典。",
        },
    }


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

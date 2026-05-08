from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Product.backend.codex_provider import local_codex_status
from Product.backend.registry import get_project_by_id, list_projects
from Product.backend.workflow_schema import Workflow, WorkflowArtifact, WorkflowTask


RESEARCH_DIMENSIONS = [
    {
        "agent_name": "墨白",
        "role": "政策语境研究员",
        "dimension": "研究背景与政策语境",
        "scope": ["政策背景", "制度变化", "研究问题边界"],
    },
    {
        "agent_name": "知远",
        "role": "文献综述研究员",
        "dimension": "文献综述与研究缺口",
        "scope": ["核心文献", "识别争议", "边际贡献"],
    },
    {
        "agent_name": "数澜",
        "role": "数据架构研究员",
        "dimension": "数据源与变量可得性",
        "scope": ["数据来源", "样本口径", "变量可得性"],
    },
    {
        "agent_name": "量衡",
        "role": "测度设计研究员",
        "dimension": "核心变量定义与测度",
        "scope": ["被解释变量", "核心解释变量", "控制变量"],
    },
    {
        "agent_name": "维农",
        "role": "识别策略研究员",
        "dimension": "识别策略与内生性处理",
        "scope": ["识别假设", "内生性来源", "工具变量或准实验"],
    },
    {
        "agent_name": "建模",
        "role": "计量建模研究员",
        "dimension": "基准模型与估计方案",
        "scope": ["基准回归", "固定效应", "标准误处理"],
    },
    {
        "agent_name": "固盾",
        "role": "稳健性研究员",
        "dimension": "稳健性检验设计",
        "scope": ["替代变量", "样本调整", "安慰剂检验"],
    },
    {
        "agent_name": "析微",
        "role": "机制异质性研究员",
        "dimension": "异质性与机制分析",
        "scope": ["分组异质性", "作用机制", "边界条件"],
    },
    {
        "agent_name": "图灵",
        "role": "结果呈现研究员",
        "dimension": "表格图形与结果呈现",
        "scope": ["主表结构", "机制表", "可视化呈现"],
    },
    {
        "agent_name": "文心",
        "role": "论文写作研究员",
        "dimension": "论文结构与写作路径",
        "scope": ["章节结构", "写作顺序", "投稿材料"],
    },
]

TASK_STATUS_BY_PROGRESS = [
    (0.2, "planning"),
    (0.45, "researching"),
    (0.7, "synthesizing"),
    (0.95, "reviewing"),
    (1.0, "completed"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def workflow_state_root(product_root: Path) -> Path:
    return product_root / "state" / "workflows"


def workflow_root(product_root: Path, workflow_id: str) -> Path:
    return workflow_state_root(product_root) / workflow_id


def workflow_path(product_root: Path, workflow_id: str) -> Path:
    return workflow_root(product_root, workflow_id) / "workflow.json"


def tasks_path(product_root: Path, workflow_id: str) -> Path:
    return workflow_root(product_root, workflow_id) / "tasks.json"


def artifacts_path(product_root: Path, workflow_id: str) -> Path:
    return workflow_root(product_root, workflow_id) / "artifacts.json"


def report_state_path(product_root: Path, workflow_id: str) -> Path:
    return workflow_root(product_root, workflow_id) / "report.json"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:36] or "workflow"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def resolve_project(product_root: Path, repo_root: Path, project_id: str | None) -> dict[str, Any]:
    if project_id:
        return get_project_by_id(product_root, repo_root, project_id)
    projects = list_projects(product_root, repo_root)
    if not projects:
        raise KeyError("no_projects")
    return projects[0]


def project_root_for(project: dict[str, Any]) -> Path:
    return Path(project.get("project_root") or project["root"]).resolve()


def create_workflow(product_root: Path, repo_root: Path, title: str, project_id: str | None = None) -> dict[str, Any]:
    project = resolve_project(product_root, repo_root, project_id)
    now = utc_now()
    workflow_id = f"wf_{slugify(title)}_{uuid.uuid4().hex[:10]}"
    workflow = Workflow(
        id=workflow_id,
        project_id=project["id"],
        title=title,
        agent_count=len(RESEARCH_DIMENSIONS),
        provider_status=local_codex_status(),
        created_at=now,
        updated_at=now,
    )
    tasks = [
        WorkflowTask(
            id=f"{workflow_id}_task_{index:02d}",
            workflow_id=workflow_id,
            agent_name=dimension["agent_name"],
            role=dimension["role"],
            dimension=dimension["dimension"],
            dimension_number=index,
            research_scope=dimension["scope"],
            evidence_gaps=["当前已选择 local_codex 作为第一执行 provider，但真实 Codex 子任务执行尚未默认开启。"],
        ).to_dict()
        for index, dimension in enumerate(RESEARCH_DIMENSIONS, start=1)
    ]
    write_json(workflow_path(product_root, workflow_id), workflow.to_dict())
    write_json(tasks_path(product_root, workflow_id), tasks)
    write_json(artifacts_path(product_root, workflow_id), [])
    write_json(report_state_path(product_root, workflow_id), {})
    return {"workflow": workflow.to_dict(), "tasks": tasks, "artifacts": []}


def list_workflows(product_root: Path) -> list[dict[str, Any]]:
    root = workflow_state_root(product_root)
    if not root.exists():
        return []
    items = []
    for path in root.glob("*/workflow.json"):
        try:
            items.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return sorted(items, key=lambda item: item.get("updated_at", ""), reverse=True)


def load_workflow(product_root: Path, workflow_id: str) -> dict[str, Any]:
    path = workflow_path(product_root, workflow_id)
    if not path.exists():
        raise KeyError(workflow_id)
    return json.loads(path.read_text(encoding="utf-8"))


def load_tasks(product_root: Path, workflow_id: str) -> list[dict[str, Any]]:
    if not workflow_path(product_root, workflow_id).exists():
        raise KeyError(workflow_id)
    return read_json(tasks_path(product_root, workflow_id), [])


def load_artifacts(product_root: Path, workflow_id: str) -> list[dict[str, Any]]:
    if not workflow_path(product_root, workflow_id).exists():
        raise KeyError(workflow_id)
    return read_json(artifacts_path(product_root, workflow_id), [])


def get_workflow_bundle(product_root: Path, repo_root: Path, workflow_id: str) -> dict[str, Any]:
    advance_workflow(product_root, repo_root, workflow_id)
    return {
        "workflow": load_workflow(product_root, workflow_id),
        "tasks": load_tasks(product_root, workflow_id),
        "artifacts": load_artifacts(product_root, workflow_id),
    }


def start_workflow(product_root: Path, repo_root: Path, workflow_id: str) -> dict[str, Any]:
    workflow = load_workflow(product_root, workflow_id)
    if workflow["status"] in {"completed", "cancelled", "failed"}:
        return {"workflow": workflow}
    now = utc_now()
    workflow.update(
        {
            "status": "running",
            "phase": "parallel_research",
            "progress": 0.05,
            "provider_status": local_codex_status(),
            "updated_at": now,
        }
    )
    tasks = load_tasks(product_root, workflow_id)
    for task in tasks:
        if task["status"] == "queued":
            task.update({"status": "planning", "progress": 0.2, "started_at": now})
    write_json(workflow_path(product_root, workflow_id), workflow)
    write_json(tasks_path(product_root, workflow_id), tasks)
    return {"workflow": workflow}


def cancel_workflow(product_root: Path, workflow_id: str) -> dict[str, Any]:
    workflow = load_workflow(product_root, workflow_id)
    if workflow["status"] == "completed":
        return {"workflow": workflow}
    now = utc_now()
    workflow.update({"status": "cancelled", "phase": "cancelled", "updated_at": now})
    tasks = load_tasks(product_root, workflow_id)
    for task in tasks:
        if task["status"] not in {"completed", "failed"}:
            task["status"] = "cancelled"
    write_json(workflow_path(product_root, workflow_id), workflow)
    write_json(tasks_path(product_root, workflow_id), tasks)
    return {"workflow": workflow}


def get_task(product_root: Path, workflow_id: str, task_id: str) -> dict[str, Any]:
    for task in load_tasks(product_root, workflow_id):
        if task["id"] == task_id:
            return task
    raise KeyError(task_id)


def advance_workflow(product_root: Path, repo_root: Path, workflow_id: str) -> None:
    workflow = load_workflow(product_root, workflow_id)
    if workflow["status"] != "running":
        return
    project = get_project_by_id(product_root, repo_root, workflow["project_id"])
    project_root = project_root_for(project)
    now = utc_now()
    tasks = load_tasks(product_root, workflow_id)
    artifacts = load_artifacts(product_root, workflow_id)
    artifact_ids = {artifact["id"] for artifact in artifacts}

    for task in tasks:
        if task["status"] in {"completed", "failed", "cancelled"}:
            continue
        task["progress"] = min(1.0, round(float(task.get("progress", 0.0)) + 0.28, 2))
        task["status"] = status_for_progress(task["progress"])
        task["summary"] = summarize_task(task)
        if task["status"] == "completed":
            task["completed_at"] = task.get("completed_at") or now
            artifact = build_task_artifact(project_root, workflow, task, now)
            if artifact["id"] not in artifact_ids:
                artifacts.append(artifact)
                artifact_ids.add(artifact["id"])
            if artifact["path"] not in task["outputs"]:
                task["outputs"].append(artifact["path"])

    completed = [task for task in tasks if task["status"] == "completed"]
    workflow["progress"] = round(len(completed) / max(len(tasks), 1), 2)
    workflow["updated_at"] = now
    if len(completed) == len(tasks):
        workflow.update({"status": "completed", "phase": "completed", "progress": 1.0})
        ensure_final_report(product_root, project_root, workflow, tasks, artifacts)
    else:
        workflow["phase"] = current_phase(tasks)

    write_json(tasks_path(product_root, workflow_id), tasks)
    write_json(artifacts_path(product_root, workflow_id), artifacts)
    write_json(workflow_path(product_root, workflow_id), workflow)


def status_for_progress(progress: float) -> str:
    for threshold, status in TASK_STATUS_BY_PROGRESS:
        if progress < threshold:
            return status
    return "completed"


def current_phase(tasks: list[dict[str, Any]]) -> str:
    statuses = {task["status"] for task in tasks}
    if "researching" in statuses:
        return "researching"
    if "synthesizing" in statuses:
        return "synthesizing"
    if "reviewing" in statuses:
        return "reviewing"
    return "parallel_research"


def summarize_task(task: dict[str, Any]) -> str:
    if task["status"] == "completed":
        return f"{task['agent_name']}已完成「{task['dimension']}」的占位研究产物。"
    return f"{task['agent_name']}正在推进「{task['dimension']}」，当前阶段：{task['status']}。"


def build_task_artifact(project_root: Path, workflow: dict[str, Any], task: dict[str, Any], created_at: str) -> dict[str, Any]:
    filename = f"{task['dimension_number']:02d}_{task['dimension']}.md"
    relative_path = f"docs/workflows/{workflow['id']}/{filename}"
    artifact = WorkflowArtifact(
        id=f"art_{task['id']}",
        workflow_id=workflow["id"],
        task_id=task["id"],
        kind="research_note",
        path=relative_path,
        title=f"{task['dimension']}研究笔记",
        created_by=task["agent_name"],
        created_at=created_at,
    ).to_dict()
    content = render_task_artifact(workflow, task)
    target = project_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return artifact


def render_task_artifact(workflow: dict[str, Any], task: dict[str, Any]) -> str:
    scope = "\n".join(f"- {item}" for item in task["research_scope"])
    gaps = "\n".join(f"- {item}" for item in task["evidence_gaps"])
    return (
        f"# {task['dimension']}研究笔记\n\n"
        f"- Workflow: {workflow['id']}\n"
        f"- Agent: {task['agent_name']}（{task['role']}）\n"
        f"- Execution provider: {workflow.get('execution_provider', 'local_codex')}\n"
        f"- Evidence level: mock\n\n"
        "## 研究范围\n"
        f"{scope}\n\n"
        "## 当前结论\n"
        f"{task['summary']}\n\n"
        "## 证据缺口\n"
        f"{gaps}\n"
    )


def ensure_final_report(
    product_root: Path,
    project_root: Path,
    workflow: dict[str, Any],
    tasks: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    relative_path = f"docs/workflows/{workflow['id']}/final_research_report.md"
    content = render_final_report(workflow, tasks, artifacts)
    target = project_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    report = {"path": relative_path, "content": content, "updated_at": utc_now()}
    write_json(report_state_path(product_root, workflow["id"]), report)
    return report


def render_final_report(workflow: dict[str, Any], tasks: list[dict[str, Any]], artifacts: list[dict[str, Any]]) -> str:
    task_lines = "\n".join(
        f"- {task['dimension_number']:02d}. {task['agent_name']}：{task['dimension']} - {task['status']}"
        for task in tasks
    )
    artifact_lines = "\n".join(f"- {artifact['title']}: `{artifact['path']}`" for artifact in artifacts)
    return (
        f"# {workflow['title']} - Agent Cluster 研究报告\n\n"
        "本报告由当前后端 API 框架生成，用于验证工作流、任务、产物和报告链路。"
        "内容仍为 mock evidence，不应作为论文事实依据。\n\n"
        "## 任务矩阵\n"
        f"{task_lines}\n\n"
        "## 产物清单\n"
        f"{artifact_lines}\n"
    )


def get_report(product_root: Path, repo_root: Path, workflow_id: str) -> dict[str, Any]:
    workflow = load_workflow(product_root, workflow_id)
    project = get_project_by_id(product_root, repo_root, workflow["project_id"])
    project_root = project_root_for(project)
    report = read_json(report_state_path(product_root, workflow_id), {})
    if report:
        return {"content": report["content"], "path": report["path"]}
    tasks = load_tasks(product_root, workflow_id)
    artifacts = load_artifacts(product_root, workflow_id)
    report = ensure_final_report(product_root, project_root, workflow, tasks, artifacts)
    return {"content": report["content"], "path": report["path"]}

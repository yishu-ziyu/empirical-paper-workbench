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


PAPER_PIPELINE_NODES = [
    {
        "agent_name": "ResearchIntentAgent",
        "role": "研究意图与验收标准",
        "dimension": "Research Intent",
        "scope": ["研究问题", "数据边界", "交付标准"],
    },
    {
        "agent_name": "LiteratureAgent",
        "role": "文献与贡献矩阵",
        "dimension": "Literature",
        "scope": ["检索计划", "候选文献", "贡献矩阵"],
    },
    {
        "agent_name": "DataAgent",
        "role": "数据契约与样本构造",
        "dimension": "Data Contract",
        "scope": ["数据入口", "样本构造", "变量字典"],
    },
    {
        "agent_name": "MethodAgent",
        "role": "方法门与识别设计",
        "dimension": "Method Gate",
        "scope": ["识别策略", "方法准入", "诊断要求"],
    },
    {
        "agent_name": "ExecutionAgent",
        "role": "统计执行与结果表",
        "dimension": "Execution",
        "scope": ["RunPlan", "模型执行", "表格和日志"],
    },
    {
        "agent_name": "RobustnessAgent",
        "role": "稳健性和异质性",
        "dimension": "Robustness",
        "scope": ["稳健性", "异质性", "机制或替代规格"],
    },
    {
        "agent_name": "ManuscriptAgent",
        "role": "论文草稿生成",
        "dimension": "Manuscript",
        "scope": ["章节结构", "证据绑定", "完整草稿"],
    },
    {
        "agent_name": "ReviewerAgent",
        "role": "论文审阅和 claim audit",
        "dimension": "Review Gates",
        "scope": ["审阅检查", "claim audit", "修订队列"],
    },
    {
        "agent_name": "ReplicationAgent",
        "role": "复现清单和哈希门",
        "dimension": "Replication",
        "scope": ["manifest", "hash baseline", "repro report"],
    },
    {
        "agent_name": "ExportAgent",
        "role": "交付包和 PDF 导出",
        "dimension": "Export",
        "scope": ["delivery package", "PDF", "人工验收"],
    },
]

RESEARCH_DIMENSIONS = PAPER_PIPELINE_NODES

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
        agent_count=len(PAPER_PIPELINE_NODES),
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
            evidence_gaps=["当前节点是 pipeline contract；只有接入 CLI 执行产物后才能升级为 local_execution。"],
        ).to_dict()
        for index, dimension in enumerate(PAPER_PIPELINE_NODES, start=1)
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
        return f"{task['agent_name']}已完成「{task['dimension']}」节点契约。"
    return f"{task['agent_name']}正在推进「{task['dimension']}」节点，当前阶段：{task['status']}。"


def build_task_artifact(project_root: Path, workflow: dict[str, Any], task: dict[str, Any], created_at: str) -> dict[str, Any]:
    filename = f"{task['dimension_number']:02d}_{task['dimension']}.md"
    relative_path = f"docs/workflows/{workflow['id']}/{filename}"
    artifact = WorkflowArtifact(
        id=f"art_{task['id']}",
        workflow_id=workflow["id"],
        task_id=task["id"],
        kind="pipeline_node_contract",
        path=relative_path,
        title=f"{task['dimension']} pipeline contract",
        created_by=task["agent_name"],
        status="contract_ready",
        created_at=created_at,
        evidence_level="pipeline_contract",
        promotion_status="not_promotable",
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
        f"# {task['dimension']} Pipeline Contract\n\n"
        f"- Workflow: {workflow['id']}\n"
        f"- Agent: {task['agent_name']} ({task['role']})\n"
        f"- Execution provider: {workflow.get('execution_provider', 'local_codex')}\n"
        "- Evidence level: pipeline_contract\n"
        "- Promotion: not_promotable_without_cli_outputs\n\n"
        "## 研究范围\n"
        f"{scope}\n\n"
        "## 当前节点契约\n"
        f"{task['summary']}\n\n"
        "## 升级为真实执行证据的条件\n"
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
        f"# {workflow['title']} - Paper Pipeline Contract\n\n"
        "本报告只记录第二层 Agent 的论文生产节点契约。"
        "它不是论文事实依据；只有 CLI 执行产物、论文审阅、claim audit 和复现检查完成后，才能进入交付。\n\n"
        "## Pipeline 节点\n"
        f"{task_lines}\n\n"
        "## 契约产物清单\n"
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

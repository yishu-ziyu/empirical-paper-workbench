from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.agent_task_queue_service import build_agent_task_queue
from Product.backend.product_control_demo_audit_service import (
    load_topic_binding,
    run_product_control_demo_topic_binding_audit,
)
from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


SUPERVISOR_PLAN_PATH = Path("state/product/supervisor_plan.json")
AGENT_TASK_QUEUE_PATH = Path("state/product/agent_task_queue.json")
P0_PHASE_JSON_PATH = Path("Results/json/product_control_p0_phase.json")
EVIDENCE_AUDIT_JSON_PATH = Path("Results/json/product_control_demo_evidence_audit.json")
EVIDENCE_AUDIT_REVIEW_PATH = Path("Reviews/product_control_demo_evidence_audit.md")
PORTFOLIO_PACKAGE_JSON_PATH = Path("Results/json/product_control_demo_portfolio_package.json")
PORTFOLIO_PACKAGE_REVIEW_PATH = Path("Reviews/product_control_demo_portfolio_package.md")
PORTFOLIO_SCRIPT_PATH = Path("docs/product-control/07_作品集Demo脚本.md")


def run_project_product_control_p0_phase(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    report = run_product_control_p0_phase(project_root)
    report["project"] = project_summary(project, project_root)
    write_json(project_root / P0_PHASE_JSON_PATH, report)
    return report


def get_project_product_control_p0_phase(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = project_root / P0_PHASE_JSON_PATH
    if not path.exists():
        return {
            "status": "p0_phase_report_missing",
            "project": project_summary(project, project_root),
            "can_refresh": True,
            "refresh_endpoint": f"/api/v1/projects/{project_id}/product-control/p0-phase",
            "p0_phase_report_path": P0_PHASE_JSON_PATH.as_posix(),
            "next_action": "点击刷新 P0 阶段包；读取操作不会自动改写阶段产物。",
        }
    report = json.loads(path.read_text(encoding="utf-8"))
    report["project"] = project_summary(project, project_root)
    report["can_refresh"] = True
    report["refresh_endpoint"] = f"/api/v1/projects/{project_id}/product-control/p0-phase"
    return report


def project_summary(project: dict[str, Any], project_root: Path) -> dict[str, str]:
    return {
        "id": str(project["id"]),
        "slug": str(project["slug"]),
        "title": str(project["title"]),
        "project_root": str(project_root),
    }


def run_product_control_p0_phase(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    topic_audit = run_product_control_demo_topic_binding_audit(project_root, persist=True)
    if topic_audit["status"] != "ready_for_p0b":
        return build_blocked_p0_report(project_root, topic_audit)
    supervisor_plan = write_product_control_supervisor_plan(project_root)
    agent_task_queue = write_product_control_agent_task_queue(project_root, supervisor_plan)
    evidence_audit = write_product_control_evidence_audit(project_root, topic_audit, agent_task_queue)
    portfolio_package = write_product_control_portfolio_package(
        project_root,
        topic_audit,
        agent_task_queue,
        evidence_audit,
    )
    report = {
        "status": "p0_phase_ready_for_review",
        "topic_binding": topic_audit["topic_binding"],
        "p0_phase_report_path": P0_PHASE_JSON_PATH.as_posix(),
        "supervisor_plan_path": SUPERVISOR_PLAN_PATH.as_posix(),
        "agent_task_queue_path": AGENT_TASK_QUEUE_PATH.as_posix(),
        "evidence_audit_path": EVIDENCE_AUDIT_JSON_PATH.as_posix(),
        "portfolio_package_path": PORTFOLIO_PACKAGE_JSON_PATH.as_posix(),
        "portfolio_script_path": PORTFOLIO_SCRIPT_PATH.as_posix(),
        "summary": {
            "task_count": agent_task_queue["summary"]["total_tasks"],
            "evidence_audit_status": evidence_audit["status"],
            "portfolio_status": portfolio_package["status"],
        },
        "agent_tasks": p0_agent_task_summaries(agent_task_queue),
        "evidence_checks": evidence_audit["checks"],
        "formal_boundary": "不能进入正式论文；P0 只生成审阅层产物，真实文献、数据与变量、方法执行证据仍需补齐。",
    }
    write_json(project_root / P0_PHASE_JSON_PATH, report)
    return report


def build_blocked_p0_report(project_root: Path, topic_audit: dict[str, Any]) -> dict[str, Any]:
    report = {
        "status": "blocked_by_topic_binding_audit",
        "topic_binding": topic_audit.get("topic_binding", {}),
        "blocking_audit_path": "Results/json/product_control_demo_topic_binding_audit.json",
        "critical_issues": topic_audit.get("critical_issues", []),
    }
    write_json(project_root / P0_PHASE_JSON_PATH, report)
    return report


def p0_agent_task_summaries(agent_task_queue: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = []
    for task in agent_task_queue.get("tasks", []):
        if not isinstance(task, dict):
            continue
        summaries.append(
            {
                "id": task.get("id") or task.get("agent_id") or "",
                "role": task.get("role") or "",
                "task": task.get("task") or task.get("title") or "",
                "status": task.get("status") or "",
                "can_execute": bool(task.get("can_execute", False)),
                "next_action": task.get("next_action") or "",
            }
        )
    return summaries


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_product_control_supervisor_plan(project_root: Path) -> dict[str, Any]:
    topic_binding = load_topic_binding(project_root)
    timestamp = utc_now()
    plan = {
        "id": "supervisor_plan",
        "version": 1,
        "status": "approved",
        "can_dispatch": True,
        "evidence_level": "local_file",
        "objective": "把当前项目 topic 拆成可审阅的 P0 Agent Task Queue",
        "path": SUPERVISOR_PLAN_PATH.as_posix(),
        "input_research_question": {
            "question": topic_binding["expected_topic"],
            "topic_slug": topic_binding["expected_slug"],
            "source": topic_binding["source"],
        },
        "input_evidence": {
            "topic_binding_path": "state/product/topic_binding.json",
            "research_question_path": "state/product/research_question.json",
            "task_brief_path": f"Tasks/{topic_binding['expected_slug']}/brief.md",
            "topic_literature_path": f"Tasks/{topic_binding['expected_slug']}/literature.md",
            "topic_variables_path": f"Tasks/{topic_binding['expected_slug']}/variables.yaml",
            "topic_design_path": f"Tasks/{topic_binding['expected_slug']}/design.json",
        },
        "stage_plan": p0_stage_plan(),
        "subagent_dispatch": p0_subagent_dispatch(topic_binding),
        "evidence_requirements": p0_evidence_requirements(topic_binding),
        "risks": [
            {
                "id": "demo_not_product_hardcode",
                "level": "medium",
                "description": "当前题目是项目 topic binding，不得写死为产品全局逻辑。",
            },
            {
                "id": "draft_not_formal_output",
                "level": "high",
                "description": "P0 只生成审阅层产物，不写正式论文结论。",
            },
        ],
        "human_gates": [
            {
                "id": "dispatch_review",
                "label": "人工派工审阅",
                "required": True,
            },
            {
                "id": "evidence_audit_review",
                "label": "证据审计审阅",
                "required": True,
            },
        ],
        "decision_events": [
            {
                "actor": "product_control_phase_service",
                "action": "seed_p0_supervisor_plan",
                "timestamp": timestamp,
                "note": "P0-B deterministic plan from project topic binding.",
            }
        ],
        "write_boundary": "P0 SupervisorPlan 只组织审阅层任务；不会写正式 VariableRoleSet、DesignSpec、RunPlan 或论文正文。",
        "updated_at": timestamp,
    }
    path = project_root / SUPERVISOR_PLAN_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan


def write_product_control_agent_task_queue(project_root: Path, supervisor_plan: dict[str, Any]) -> dict[str, Any]:
    timestamp = utc_now()
    queue = build_agent_task_queue(supervisor_plan, supervisor_plan["subagent_dispatch"], timestamp)
    path = project_root / AGENT_TASK_QUEUE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    return queue


def p0_stage_plan() -> list[dict[str, str]]:
    return [
        {"stage": "任务书", "goal": "确认当前研究题目、边界和成功标准", "status": "planned"},
        {"stage": "数据与变量", "goal": "发现数据候选和变量角色候选", "status": "planned"},
        {"stage": "方法设计", "goal": "列出可行识别策略、前置条件和阻断原因", "status": "planned"},
        {"stage": "执行预检", "goal": "确认是否存在真实数据、脚本、run id 和结果产物", "status": "planned"},
        {"stage": "证据审计", "goal": "区分真实证据、候选证据、占位材料和正式层边界", "status": "planned"},
        {"stage": "作品集交付", "goal": "生成可讲述的 P0 demo package", "status": "planned"},
    ]


def p0_subagent_dispatch(topic_binding: dict[str, Any]) -> list[dict[str, Any]]:
    topic = topic_binding["expected_topic"]
    slug = topic_binding["expected_slug"]
    return [
        dispatch_item("research_brief", "ResearchBriefAgent", "确认研究任务书", topic, slug, "Tasks/{slug}/brief.md"),
        dispatch_item("data_discovery", "DataAgent", "发现数据源和字段画像", topic, slug, "Data/ 或外部数据索引"),
        dispatch_item("variable_roles", "VariableAgent", "生成变量角色候选", topic, slug, "Tasks/{slug}/variables.yaml"),
        dispatch_item("method_design", "MethodAgent", "生成方法设计和前置条件", topic, slug, "Tasks/{slug}/design.json"),
        dispatch_item("execution_preflight", "ExecutionAgent", "检查执行预检和结果证据", topic, slug, "Results/json/"),
        dispatch_item("evidence_audit", "EvidenceAuditAgent", "审计证据链和草稿边界", topic, slug, "Reviews/product_control_demo_evidence_audit.md"),
    ]


def dispatch_item(
    agent_id: str,
    role: str,
    task: str,
    topic: str,
    slug: str,
    artifact_template: str,
) -> dict[str, Any]:
    artifact = artifact_template.format(slug=slug)
    return {
        "agent_id": agent_id,
        "role": role,
        "task": task,
        "summary": f"围绕《{topic}》{task}。",
        "output_requirements": [
            {
                "id": f"{agent_id}_reviewable_output",
                "requirement": f"输出可审阅产物：{artifact}",
                "artifact_path": artifact,
                "evidence_level": "local_file",
            }
        ],
    }


def p0_evidence_requirements(topic_binding: dict[str, Any]) -> list[dict[str, Any]]:
    slug = topic_binding["expected_slug"]
    return [
        {
            "id": "topic_binding_consistency",
            "requirement": "所有 current product surfaces 必须匹配项目 topic binding。",
            "artifact_path": "Results/json/product_control_demo_topic_binding_audit.json",
            "evidence_level": "local_file",
        },
        {
            "id": "agent_queue_traceability",
            "requirement": "Agent Queue 必须从当前 SupervisorPlan 生成，并保留输入路径。",
            "artifact_path": "state/product/agent_task_queue.json",
            "evidence_level": "local_file",
        },
        {
            "id": "topic_materials",
            "requirement": "任务书、变量、设计材料必须在当前 topic 目录下。",
            "artifact_path": f"Tasks/{slug}/",
            "evidence_level": "local_file",
        },
    ]


def write_product_control_evidence_audit(
    project_root: Path,
    topic_audit: dict[str, Any],
    agent_task_queue: dict[str, Any],
) -> dict[str, Any]:
    topic_binding = topic_audit["topic_binding"]
    checks = build_evidence_checks(project_root, topic_audit, agent_task_queue)
    report = {
        "_meta": {
            "evidence_level": "local_file",
            "service": "product_control_phase_service",
            "generated_at": utc_now(),
        },
        "schema_version": "p0c.product_control_demo_evidence_audit.v1",
        "status": "p0_evidence_audit_ready",
        "topic_binding": topic_binding,
        "checks": checks,
        "evidence_items": build_evidence_items(checks),
        "can_export_formal_paper": False,
        "can_enter_p0d": all(check["status"] in {"passed", "needs_evidence"} for check in checks),
        "artifact_paths": {
            "json": EVIDENCE_AUDIT_JSON_PATH.as_posix(),
            "review": EVIDENCE_AUDIT_REVIEW_PATH.as_posix(),
        },
        "next_action": "进入 P0-D 作品集验收包；真实研究执行仍需后续数据、文献和方法证据补齐。",
    }
    json_path = project_root / EVIDENCE_AUDIT_JSON_PATH
    review_path = project_root / EVIDENCE_AUDIT_REVIEW_PATH
    json_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_evidence_audit_review(report), encoding="utf-8")
    return report


def build_evidence_checks(
    project_root: Path,
    topic_audit: dict[str, Any],
    agent_task_queue: dict[str, Any],
) -> list[dict[str, Any]]:
    slug = topic_audit["topic_binding"]["expected_slug"]
    expected_roles = {
        "ResearchBriefAgent",
        "DataAgent",
        "VariableAgent",
        "MethodAgent",
        "ExecutionAgent",
        "EvidenceAuditAgent",
    }
    actual_roles = {task.get("role") for task in agent_task_queue.get("tasks", [])}
    return [
        check(
            "topic_binding_audit",
            "passed" if topic_audit.get("status") == "ready_for_p0b" else "failed",
            "Topic binding audit",
            "Results/json/product_control_demo_topic_binding_audit.json",
            "当前 topic surface 已通过一致性审计。",
        ),
        check(
            "agent_task_queue",
            "passed" if expected_roles.issubset(actual_roles) else "failed",
            "Agent Task Queue",
            "state/product/agent_task_queue.json",
            "已生成 6 个 P0 Agent 任务。" if expected_roles.issubset(actual_roles) else "P0 Agent 任务不完整。",
        ),
        check(
            "real_literature_candidates",
            "needs_evidence",
            "真实文献候选",
            f"Tasks/{slug}/literature.md",
            "当前文献工作面干净，但仍需真实检索和引用核验。",
        ),
        check(
            "dataset_variable_binding",
            "needs_evidence",
            "数据与变量绑定",
            f"Tasks/{slug}/variables.yaml",
            "变量仍是候选层，需要绑定真实数据字典和字段画像。",
        ),
        check(
            "method_execution_evidence",
            "needs_evidence",
            "方法执行证据",
            "Results/json/method_execution_result.json",
            "P0 不要求真实回归结果；后续执行阶段必须补 run id 和结果产物。",
        ),
        check(
            "formal_boundary",
            "passed",
            "正式层边界",
            "Reviews/product_control_demo_evidence_audit.md",
            "当前仅生成审阅层产物，不授权正式论文写回。",
        ),
    ]


def check(check_id: str, status: str, label: str, artifact_path: str, detail: str) -> dict[str, str]:
    return {
        "id": check_id,
        "status": status,
        "label": label,
        "artifact_path": artifact_path,
        "evidence_level": "local_file",
        "detail": detail,
    }


def build_evidence_items(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "claim": check["label"],
            "status": check["status"],
            "evidence_path": check["artifact_path"],
            "detail": check["detail"],
        }
        for check in checks
    ]


def render_evidence_audit_review(report: dict[str, Any]) -> str:
    lines = [
        "# Product Control Demo Evidence Audit",
        "",
        f"- status: {report['status']}",
        f"- topic: {report['topic_binding']['expected_topic']}",
        f"- can_export_formal_paper: {str(report['can_export_formal_paper']).lower()}",
        f"- can_enter_p0d: {str(report['can_enter_p0d']).lower()}",
        "",
        "## Checks",
        "",
    ]
    for check_item in report["checks"]:
        lines.append(f"- {check_item['id']} | {check_item['status']} | {check_item['detail']} | {check_item['artifact_path']}")
    lines.extend(["", f"Next action: {report['next_action']}", ""])
    return "\n".join(lines)


def write_product_control_portfolio_package(
    project_root: Path,
    topic_audit: dict[str, Any],
    agent_task_queue: dict[str, Any],
    evidence_audit: dict[str, Any],
) -> dict[str, Any]:
    topic_binding = topic_audit["topic_binding"]
    script = render_portfolio_script(topic_binding, agent_task_queue, evidence_audit)
    script_path = project_root / PORTFOLIO_SCRIPT_PATH
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
    package = {
        "_meta": {
            "evidence_level": "local_file",
            "service": "product_control_phase_service",
            "generated_at": utc_now(),
        },
        "schema_version": "p0d.product_control_demo_portfolio_package.v1",
        "status": "portfolio_demo_package_ready",
        "topic_binding": topic_binding,
        "artifacts": {
            "script": PORTFOLIO_SCRIPT_PATH.as_posix(),
            "topic_binding_audit": "Results/json/product_control_demo_topic_binding_audit.json",
            "agent_task_queue": AGENT_TASK_QUEUE_PATH.as_posix(),
            "evidence_audit": EVIDENCE_AUDIT_JSON_PATH.as_posix(),
            "review": PORTFOLIO_PACKAGE_REVIEW_PATH.as_posix(),
        },
        "demo_assets": [
            "3_minute_script",
            "product_flow_mermaid",
            "agent_split_mermaid",
            "evidence_status_table",
            "next_roadmap",
        ],
        "formal_boundary": "Portfolio package is a product demonstration artifact; it does not write a formal paper.",
    }
    json_path = project_root / PORTFOLIO_PACKAGE_JSON_PATH
    review_path = project_root / PORTFOLIO_PACKAGE_REVIEW_PATH
    json_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_portfolio_review(package), encoding="utf-8")
    return package


def render_portfolio_script(
    topic_binding: dict[str, Any],
    agent_task_queue: dict[str, Any],
    evidence_audit: dict[str, Any],
) -> str:
    topic = topic_binding["expected_topic"]
    tasks = agent_task_queue.get("tasks", [])
    evidence_rows = "\n".join(
        f"| {item['claim']} | {item['status']} | `{item['evidence_path']}` |"
        for item in evidence_audit["evidence_items"]
    )
    agent_edges = "\n".join(
        f"    Topic --> {task['role']}[{task['role']}]" for task in tasks if isinstance(task, dict)
    )
    return f"""# 07 作品集 Demo 脚本

## Demo 题目

{topic}

## 3 分钟讲述

第一分钟：我做的不是论文生成器，而是一个本地 AI 实证研究 OS。用户输入题目后，系统先确认当前项目 topic，避免旧项目、旧运行态和旧材料串题。

第二分钟：系统把研究推进拆成 Agent Task Queue。每个 Agent 都有输入、输出、状态和人工审阅点。当前 P0 阶段生成 6 个任务，但它们默认不能直接执行，必须先经过派工审阅。

第三分钟：Evidence Audit 告诉用户哪些东西已有本地证据，哪些还只是候选，哪些不能进入正式论文。作品集展示的重点是可审计流程，而不是一键生成结论。

## 产品流程图

```mermaid
flowchart LR
    A[Topic Binding] --> B[Research Brief]
    B --> C[Agent Task Queue]
    C --> D[Evidence Audit]
    D --> E[Portfolio Demo Package]
    D --> F[Next Research Execution]
```

## Agent 分工图

```mermaid
flowchart TD
    Topic[{topic}]
{agent_edges}
```

## 证据链状态

| Claim | Status | Evidence |
| --- | --- | --- |
{evidence_rows}

## 当前做到哪里

- P0-A：topic binding audit 已通过。
- P0-B：Agent Task Queue 已生成，等待人工派工审阅。
- P0-C：Evidence Audit 已列出证据状态。
- P0-D：作品集脚本和 package 已生成。

## 还差哪里

- 真实文献候选和引用核验。
- 真实数据字段绑定和变量角色确认。
- 方法执行结果、run id、表格和 evidence_id。
- 前端/CLI 对 P0 产物的统一展示。
"""


def render_portfolio_review(package: dict[str, Any]) -> str:
    lines = [
        "# Product Control Demo Portfolio Package",
        "",
        f"- status: {package['status']}",
        f"- topic: {package['topic_binding']['expected_topic']}",
        "",
        "## Artifacts",
        "",
    ]
    for name, path in package["artifacts"].items():
        lines.append(f"- {name}: `{path}`")
    lines.extend(["", f"Formal boundary: {package['formal_boundary']}", ""])
    return "\n".join(lines)

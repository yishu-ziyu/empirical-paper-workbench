from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p4.paper_supervisor_run.v1"


def load_supervisor_context(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Supervisor context not found: {path}")
    context = json.loads(path.read_text(encoding="utf-8"))
    if context.get("schema_version") != "p4.paper_supervisor_context.v1":
        raise ValueError("Expected p4.paper_supervisor_context.v1 supervisor context.")
    return context


def build_supervisor_execution_prompt(context: dict[str, Any]) -> str:
    sources = "\n".join(f"- {source}" for source in context.get("context_sources", []))
    tasks = "\n".join(
        f"- {task.get('id')}: {task.get('agent')} -> {task.get('reason')}"
        for task in context.get("agent_task_queue", [])
    )
    gates = "\n".join(f"- {gate}" for gate in context.get("release_gate", {}).get("required_before_review", []))
    return (
        f"{context.get('task_prompt', '').strip()}\n\n"
        "你现在运行在本地实证论文工作台中。请作为 LLM Supervisor 输出一份可审阅的下一轮研究执行计划。\n\n"
        "上下文来源：\n"
        f"{sources}\n\n"
        "当前 Agent Task Queue：\n"
        f"{tasks}\n\n"
        "进入审阅前必须满足的 gate：\n"
        f"{gates}\n\n"
        "输出要求：\n"
        "1. 用 Markdown 写出下一轮路线、依赖顺序和每个 Agent 的任务边界。\n"
        "2. 明确哪些任务调用 StatsPAI、Python、StataMCP 或本地文献/数据源。\n"
        "3. 明确每个任务的输入证据、输出文件、验收条件和人工确认点。\n"
        "4. 只写草案层和 proposal 层，不改写正式变量、设计、运行计划或正式论文。\n"
    )


def build_supervisor_run(
    *,
    project_root: Path,
    context_path: Path,
    raw_output_path: Path,
    context: dict[str, Any],
    provider_result: dict[str, Any],
    provider_status: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "needs_human_review",
        "evidence_level": "local_execution",
        "provider": {
            "provider": provider_status.get("provider", "local_codex"),
            "path": provider_status.get("path"),
            "version": provider_status.get("version"),
            "execution_enabled": provider_status.get("execution_enabled"),
            "returncode": provider_result.get("returncode"),
        },
        "input_context_path": relative_or_absolute(context_path, project_root),
        "raw_output_path": relative_or_absolute(raw_output_path, project_root),
        "profile": context.get("profile"),
        "current_verdict": context.get("current_verdict", []),
        "agent_task_queue": context.get("agent_task_queue", []),
        "release_gate": context.get("release_gate", {}),
        "write_boundary": context.get("write_boundary"),
        "formal_state_write": {
            "can_promote": False,
            "requires_human_review": True,
            "protected_paths": [
                "state/product/research_question.json",
                "state/product/variable_roles.json",
                "state/product/design_spec.json",
                "state/product/run_plan.json",
            ],
        },
        "next_action": {
            "id": "review_supervisor_run",
            "label": "审阅本地 Codex Supervisor 输出",
        },
    }


def write_supervisor_run(path: Path, run: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)

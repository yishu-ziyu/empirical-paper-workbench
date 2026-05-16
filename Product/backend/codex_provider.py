from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


CODEX_EXEC_ENV = "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC"


def local_codex_status() -> dict[str, Any]:
    path = shutil.which("codex")
    status: dict[str, Any] = {
        "provider": "local_codex",
        "available": bool(path),
        "path": path,
        "version": None,
        "execution_enabled": os.environ.get(CODEX_EXEC_ENV) == "1",
        "execution_env": CODEX_EXEC_ENV,
    }
    if not path:
        return status

    try:
        result = subprocess.run(
            [path, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return status

    output = (result.stdout or result.stderr).strip()
    status["version"] = output.splitlines()[-1] if output else None
    return status


def build_codex_task_prompt(workflow: dict[str, Any], task: dict[str, Any]) -> str:
    scope = "\n".join(f"- {item}" for item in task.get("research_scope", []))
    return (
        "你是本地 Codex 驱动的实证研究子 Agent。请只基于本地可见项目文件和明确证据输出，"
        "不要编造文献、数据或结论。\n\n"
        f"Workflow: {workflow['id']}\n"
        f"研究问题: {workflow['title']}\n"
        f"Agent: {task['agent_name']} ({task['role']})\n"
        f"研究维度: {task['dimension']}\n\n"
        "研究范围:\n"
        f"{scope}\n\n"
        "输出要求:\n"
        "- 用 Markdown 写一份可审查研究笔记。\n"
        "- 明确列出已检查的本地路径。\n"
        "- 明确列出证据缺口。\n"
        "- 如果证据不足，直接说明不足，不要替论文补结论。\n"
    )


def run_local_codex_task(
    project_root: Path,
    workflow: dict[str, Any],
    task: dict[str, Any],
    output_path: Path,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    return run_local_codex_prompt(
        project_root,
        build_codex_task_prompt(workflow, task),
        output_path,
        timeout_seconds,
    )


def run_local_codex_prompt(
    project_root: Path,
    prompt: str,
    output_path: Path,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    status = local_codex_status()
    if not status["available"]:
        raise FileNotFoundError("codex")
    if not status["execution_enabled"]:
        raise RuntimeError(f"Set {CODEX_EXEC_ENV}=1 to allow local Codex task execution.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        status["path"],
        "exec",
        "--cd",
        str(project_root),
        "--sandbox",
        "read-only",
        "--output-last-message",
        str(output_path),
        prompt,
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return {
        "provider": "local_codex",
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_path": str(output_path),
    }

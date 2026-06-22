#!/usr/bin/env python3
"""Run deterministic preflight checks for the agent workflow layer."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "artifacts" / "agent_runtime_preflight_report.md"

COMMANDS = [
    ["python3", "scripts/20_validate_workflow_contracts.py"],
    ["python3", "scripts/21_route_next_workflow.py"],
    ["python3", "scripts/22_validate_agent_specs.py"],
    ["python3", "scripts/23_workflow_runbook.py"],
    ["python3", "scripts/24_validate_runbook_api.py"],
    ["python3", "scripts/26_validate_context_strategy.py"],
    ["python3", "scripts/27_validate_tool_adapters.py"],
    ["python3", "scripts/28_agent_orchestrator.py", "--mode", "dry-run", "--no-trace"],
    ["python3", "scripts/28_agent_orchestrator.py", "--mode", "execute", "--adapter", "reproduction_verify", "--no-trace"],
    ["python3", "scripts/29_validate_orchestrator.py"],
    ["python3", "scripts/30_test_orchestrator_negative.py"],
    ["python3", "scripts/31_validate_skill_subagent_registry.py"],
    ["python3", "scripts/32_test_skill_subagent_negative.py"],
    ["python3", "scripts/33_validate_plugin_package.py"],
    ["python3", "-m", "json.tool", "artifacts/workflow_runbook_state.json"],
    ["python3", "-m", "json.tool", "workflows/schemas/runbook_state.schema.json"],
    ["python3", "-m", "json.tool", "workflows/memory_index.json"],
    ["python3", "-m", "json.tool", "workflows/schemas/memory_index.schema.json"],
    ["python3", "-m", "json.tool", "workflows/tool_adapters.json"],
    ["python3", "-m", "json.tool", "workflows/schemas/tool_adapters.schema.json"],
    ["python3", "-m", "json.tool", "workflows/schemas/agent_trace.schema.json"],
    ["python3", "-m", "json.tool", "workflows/orchestrator_policy.json"],
    ["python3", "-m", "json.tool", "workflows/schemas/orchestrator_policy.schema.json"],
    ["python3", "-m", "json.tool", "workflows/schemas/orchestrator_run_state.schema.json"],
    ["python3", "-m", "json.tool", "artifacts/orchestrator_run_state.json"],
    ["python3", "-m", "json.tool", "workflows/skill_subagent_registry.json"],
    ["python3", "-m", "json.tool", "workflows/schemas/skill_subagent_registry.schema.json"],
    ["python3", "-m", "json.tool", "plugins/statspai-empirical-workflow-runtime/.codex-plugin/plugin.json"],
    ["python3", "-m", "json.tool", "plugins/statspai-empirical-workflow-runtime/package_manifest.json"],
    ["git", "diff", "--check"],
]


def run_command(command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": " ".join(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main() -> None:
    results = [run_command(command) for command in COMMANDS]
    status = "PASS" if all(result["returncode"] == 0 for result in results) else "FAIL"

    lines = [
        "# Agent Runtime Preflight",
        "",
        f"Status: {status}",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Commands",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"### `{result['command']}`",
                "",
                f"- exit: {result['returncode']}",
                "",
            ]
        )
        if result["stdout"]:
            lines.extend(["stdout:", "", "```text", result["stdout"], "```", ""])
        if result["stderr"]:
            lines.extend(["stderr:", "", "```text", result["stderr"], "```", ""])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"{status} report={REPORT_PATH.relative_to(ROOT)}")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

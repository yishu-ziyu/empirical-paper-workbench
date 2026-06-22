from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "workflows/registry.json",
    "workflows/tool_adapters.json",
    "workflows/orchestrator_policy.json",
    "workflows/schemas/workflow_io.schema.json",
    "workflows/schemas/runbook_state.schema.json",
    "workflows/schemas/orchestrator_policy.schema.json",
    "workflows/schemas/orchestrator_run_state.schema.json",
    "workflows/schemas/agent_trace.schema.json",
    "scripts/20_validate_workflow_contracts.py",
    "scripts/21_route_next_workflow.py",
    "scripts/22_validate_agent_specs.py",
    "scripts/23_workflow_runbook.py",
    "scripts/24_validate_runbook_api.py",
    "scripts/25_agent_runtime_preflight.py",
    "scripts/26_validate_context_strategy.py",
    "scripts/27_validate_tool_adapters.py",
    "scripts/28_agent_orchestrator.py",
    "scripts/29_validate_orchestrator.py",
    "scripts/30_test_orchestrator_negative.py",
    ".codex/skills/statspai-empirical-workflow/SKILL.md",
    ".codex/agents/statspai-router.toml",
    "workflows/skill_subagent_registry.json",
    "workflows/schemas/skill_subagent_registry.schema.json",
    "scripts/31_validate_skill_subagent_registry.py",
    "scripts/32_test_skill_subagent_negative.py",
    "plugins/statspai-empirical-workflow-runtime/.codex-plugin/plugin.json",
    "scripts/33_validate_plugin_package.py",
]


FORBIDDEN_CHARLS_PATHS = [
    "verify_repro.py",
    "baseline_hashes.txt",
    "paper.pdf",
    "paper.tex",
    "artifacts/did_sample.pkl",
]


def test_runtime_bootstrap_files_are_installed() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    assert missing == []


def test_charls_paper_outputs_are_not_copied() -> None:
    copied = [path for path in FORBIDDEN_CHARLS_PATHS if (ROOT / path).exists()]
    assert copied == []


def test_runtime_preflight_passes_after_bootstrap() -> None:
    completed = subprocess.run(
        ["python3", "scripts/25_agent_runtime_preflight.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = ROOT / "artifacts" / "agent_runtime_preflight_report.md"
    assert report.exists()
    assert "Status: PASS" in report.read_text(encoding="utf-8")

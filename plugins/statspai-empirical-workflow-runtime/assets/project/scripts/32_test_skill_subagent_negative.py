#!/usr/bin/env python3
"""Negative tests for Runtime Gap P4 skill/subagent registry behavior."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def copy_repo_subset(tmpdir: Path) -> Path:
    dst = tmpdir / "repo"
    dst.mkdir()
    for path in [
        ".codex/agents",
        ".codex/skills/statspai-empirical-workflow",
        "scripts/31_validate_skill_subagent_registry.py",
        "workflows/registry.json",
        "workflows/tool_adapters.json",
        "workflows/orchestrator_policy.json",
        "workflows/skill_subagent_registry.json",
        "workflows/schemas/skill_subagent_registry.schema.json",
    ]:
        source = ROOT / path
        target = dst / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)
    return dst


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="statspai_p4_negative_") as tmp:
        repo = copy_repo_subset(Path(tmp))

        baseline = run(["python3", "scripts/31_validate_skill_subagent_registry.py"], repo)
        if baseline.returncode != 0:
            print(baseline.stdout)
            print(baseline.stderr)
            raise SystemExit("baseline registry validator should pass before mutation")

        registry_path = repo / "workflows" / "skill_subagent_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["workflow_bindings"] = [
            binding for binding in registry["workflow_bindings"] if binding["workflow_id"] != "10_defense"
        ]
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        mutated = run(["python3", "scripts/31_validate_skill_subagent_registry.py"], repo)
        if mutated.returncode == 0:
            print(mutated.stdout)
            raise SystemExit("validator failed to reject missing 10_defense binding")
        if "10_defense" not in (mutated.stdout + mutated.stderr):
            print(mutated.stdout)
            print(mutated.stderr)
            raise SystemExit("validator failed without naming missing 10_defense binding")

    print("PASS missing 10_defense binding rejected")


if __name__ == "__main__":
    main()

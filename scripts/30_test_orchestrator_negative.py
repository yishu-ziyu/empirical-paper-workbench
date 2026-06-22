#!/usr/bin/env python3
"""Negative tests for Runtime Gap P3 validator behavior."""

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
        "scripts/28_agent_orchestrator.py",
        "scripts/29_validate_orchestrator.py",
        "workflows/orchestrator_policy.json",
        "workflows/schemas/orchestrator_policy.schema.json",
        "workflows/schemas/orchestrator_run_state.schema.json",
        "workflows/tool_adapters.json",
        "artifacts/orchestrator_run_state.json",
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
    with tempfile.TemporaryDirectory(prefix="statspai_p3_negative_") as tmp:
        repo = copy_repo_subset(Path(tmp))

        baseline = run(["python3", "scripts/29_validate_orchestrator.py"], repo)
        if baseline.returncode != 0:
            print(baseline.stdout)
            print(baseline.stderr)
            raise SystemExit("baseline validator should pass before mutation")

        state_path = repo / "artifacts" / "orchestrator_run_state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state.pop("trace_path", None)
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        mutated = run(["python3", "scripts/29_validate_orchestrator.py"], repo)
        if mutated.returncode == 0:
            print(mutated.stdout)
            raise SystemExit("validator failed to reject missing top-level trace_path")
        if "trace_path" not in (mutated.stdout + mutated.stderr):
            print(mutated.stdout)
            print(mutated.stderr)
            raise SystemExit("validator failed without naming trace_path")

    print("PASS missing trace_path rejected")


if __name__ == "__main__":
    main()

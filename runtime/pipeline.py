#!/usr/bin/env python3
"""Core pipeline engine: reads registry, executes steps, handles checkpoints."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.checkpoints import checkpoint, report_progress
from runtime.state import PipelineState, ROOT

REGISTRY_PATH = ROOT / "workflows" / "registry.json"
POLICY_PATH = ROOT / "workflows" / "orchestrator_policy.json"
REPORT_PATH = ROOT / "artifacts" / "pipeline_report.md"


# ── low-level helpers ───────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _run(cmd: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run a shell command, return the CompletedProcess."""
    return subprocess.run(
        cmd,
        shell=True,
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
    )


# ── step execution ──────────────────────────────────────────────

class StepResult:
    def __init__(self, step_id: str, passed: bool, output: str, error: str = "") -> None:
        self.step_id = step_id
        self.passed = passed
        self.output = output
        self.error = error

    @property
    def status(self) -> str:
        return "pass" if self.passed else "fail"


def _run_automated_gates(step: dict) -> StepResult:
    """Run all automated gates for a step. Stops at first failure."""
    for gate in step.get("gates", []):
        if gate.get("type") != "automated":
            continue
        cmd = gate.get("command", "")
        if not cmd:
            continue
        print(f"  [gate] {gate['name']}: {cmd}")
        result = _run(cmd)
        # LaTeX compilers return non-zero in nonstopmode even on success;
        # treat as pass if a PDF was produced.
        is_latex = any(k in cmd.lower() for k in ("xelatex", "pdflatex", "lualatex"))
        pdf_ok = (ROOT / "paper.pdf").exists() and (ROOT / "paper.pdf").stat().st_size > 1000
        if result.returncode != 0 and not (is_latex and pdf_ok):
            return StepResult(
                step_id=step["id"],
                passed=False,
                output=result.stdout,
                error=result.stderr or f"gate '{gate['name']}' failed (exit {result.returncode})",
            )
    return StepResult(step_id=step["id"], passed=True, output="")


def _run_step_commands(step: dict) -> StepResult:
    """Run the step's primary commands (from registry gates or adapters)."""
    commands: list[str] = []
    for gate in step.get("gates", []):
        if gate.get("type") == "automated":
            cmd = gate.get("command", "")
            if cmd:
                commands.append(cmd)

    if not commands:
        return StepResult(step_id=step["id"], passed=True, output="(no commands — human-only step)")

    outputs: list[str] = []
    errors: list[str] = []
    for cmd in commands:
        print(f"  $ {cmd}")
        r = _run(cmd)
        outputs.append(r.stdout.strip())
        is_latex = any(k in cmd.lower() for k in ("xelatex", "pdflatex", "lualatex"))
        pdf_ok = (ROOT / "paper.pdf").exists() and (ROOT / "paper.pdf").stat().st_size > 1000
        if r.returncode != 0 and not (is_latex and pdf_ok):
            errors.append(f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    if errors:
        return StepResult(step_id=step["id"], passed=False, output="\n".join(outputs), error="; ".join(errors))
    return StepResult(step_id=step["id"], passed=True, output="\n".join(outputs))


# ── pipeline ────────────────────────────────────────────────────

class Pipeline:
    """Read registry → execute steps → handle checkpoints → persist state."""

    def __init__(self, mode: str = "execute", auto: bool = False, start_step: str | None = None) -> None:
        self.registry = _load_json(REGISTRY_PATH)
        self.policy = _load_json(POLICY_PATH) if POLICY_PATH.exists() else {}
        self.state = PipelineState()
        self.mode = mode
        self.auto = auto
        self.start_step = start_step
        self.steps: list[dict] = self.registry["workflows"]
        self.report_lines: list[str] = []

    # ── public API ───────────────────────────────────────────────

    def run(self) -> bool:
        """Execute the pipeline. Returns True if all steps pass."""
        self._banner()
        total = len(self.steps)

        start_idx = self._resolve_start_index()
        if start_idx is None:
            print("  ✅ 所有步骤已完成。")
            return True

        for idx in range(start_idx, total):
            step = self.steps[idx]
            step_id = step["id"]
            step_name = step["name"]

            # --- skip if artifacts already present (resume safety) ---
            if self.mode == "execute" and self._all_artifacts_present(step):
                print(f"  ⏭  {step_name} — 产物已存在，跳过")
                self.state.set_done(step_id)
                self._append_report_step(step, StepResult(step_id, True, "(skipped — artifacts exist)"))
                continue

            report_progress(step_name, idx + 1, total, "running")
            self.state.set_running(step_id, idx)

            # --- dry-run: just show what would happen ---
            if self.mode == "dry-run":
                self._print_dry_step(step)
                self.state.set_done(step_id)
                continue

            # --- automated gates ---
            gate_result = _run_automated_gates(step)
            if not gate_result.passed:
                print(f"  ❌ Gate failed: {gate_result.error}")
                self.state.set_blocked(step_id, gate_result.error)
                self.state.increment_failures()
                self._write_report()
                return False

            # --- human checkpoint ---
            if step.get("human_checkpoints") and not self.auto:
                try:
                    checkpoint(step_name, step["human_checkpoints"])
                except SystemExit:
                    self.state.set_stopped("human stopped")
                    self._write_report()
                    raise
            elif step.get("human_checkpoints") and self.auto:
                print(f"  [auto] Skipping human checkpoint: {step_name}")

            # --- execute step commands ---
            exec_result = _run_step_commands(step)
            if not exec_result.passed:
                print(f"  ❌ Step failed: {exec_result.error}")
                self.state.set_blocked(step_id, exec_result.error)
                self.state.increment_failures()
                self._write_report()
                return False

            print(f"  ✅ {step_name} 完成")
            self.state.set_done(step_id)
            self._write_report()
            self._append_report_step(step, exec_result)

        self.state._state["status"] = "done"
        self.state._state["current_step"] = None
        self.state._state["updated_at"] = _now()
        self._write_report()
        print("\n🎉 全流程完成!")
        return True

    # ── internals ────────────────────────────────────────────────

    def _all_artifacts_present(self, step: dict) -> bool:
        """Check if all required_outputs for a step exist on disk."""
        for item in step.get("required_outputs", []):
            hint = item.get("path_hint", item.get("artifact", ""))
            if not hint:
                continue
            p = ROOT / hint
            if "*" in hint:
                if not list(p.parent.glob(p.name)):
                    return False
            elif not p.exists():
                return False
        return True

    def _resolve_start_index(self) -> int | None:
        """Decide where to start based on mode and state."""
        if self.start_step:
            for i, s in enumerate(self.steps):
                if s["id"] == self.start_step:
                    return i
            print(f"  未知步骤: {self.start_step}")
            sys.exit(1)

        if self.mode == "resume":
            cur = self.state.current_step
            if cur:
                for i, s in enumerate(self.steps):
                    if s["id"] == cur:
                        return i
            # state exists but nothing pending → done
            return None

        if self.state.status in ("done",):
            return None

        # default: start from beginning
        return 0

    def _banner(self) -> None:
        label = "execute"
        if self.mode == "dry-run":
            label = "dry-run"
        elif self.mode == "resume":
            label = "resume"
        if self.auto:
            label += "/auto"
        total = len(self.steps)
        done = sum(1 for h in self.state.history if h["result"] == "done")
        print(f"\n{'=' * 50}")
        print(f"  📊 论文流水线  [{label}]")
        print(f"  总步骤: {total}  |  已完成: {done}  |  模式: {self.mode}")
        print(f"{'=' * 50}\n")

    def _print_dry_step(self, step: dict) -> None:
        print(f"  → {step['id']} {step['name']}")
        if step.get("human_checkpoints"):
            for cp in step["human_checkpoints"]:
                print(f"    🔔 {cp}")
        for gate in step.get("gates", []):
            if gate.get("type") == "automated" and gate.get("command"):
                print(f"    $ {gate['command']}")

    def _append_report_step(self, step: dict, result: StepResult) -> None:
        self.report_lines.append(f"## {step['id']} {step['name']}\n")
        self.report_lines.append(f"- 状态: {result.status}")
        if result.output:
            self.report_lines.append(f"- 输出: {result.output[:200]}")
        self.report_lines.append("")

    def _write_report(self) -> None:
        lines = [
            f"# Pipeline Report",
            f"",
            f"生成时间: {_now()}",
            f"模式: {self.mode}",
            f"状态: {self.state.status}",
            f"",
            "## 步骤历史",
            "",
        ]
        for h in self.state.history:
            lines.append(f"- **{h['step_id']}**: {h['result']}  ({h.get('note', '')})")
        if self.report_lines:
            lines.append("")
            lines.extend(self.report_lines)

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        self.state.save()

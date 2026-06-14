"""Gray-box subcommand: run-agent with approve/edit/view/reject/skip prompt."""
from __future__ import annotations

import argparse
import os
import subprocess
import time
from pathlib import Path

from Product.cli._common import (
    AGENT_ROLES,
    default_output_files_for_agent,
    print_manifest,
    save_checkpoint_from_input,
)
from Product.backend.orchestrator import _run_stage  # internal but stable


def prompt_graybox(stage: str, agent_role: str, output_files: list[Path] | None = None) -> str:
    """5-option gray-box: a/e/v/r/s. edit opens $EDITOR, view cats first 50 lines."""
    print(f"\n[graybox] Stage '{stage}' (agent: {agent_role}) finished.")
    if output_files:
        rel = [str(f.relative_to(Path(__file__).resolve().parents[2])) for f in output_files if f.exists()]
        print(f"  artifacts: {', '.join(rel)}")
    print("  [a]pprove  /  [e]dit ($EDITOR)  /  [v]iew (cat first file)  /  [r]eject  /  [s]kip")
    while True:
        choice = input("  > ").strip().lower()
        if choice in ("a", "approve"):
            return "approved"
        if choice in ("e", "edit"):
            if not output_files:
                print("  no output files to edit")
                continue
            target = output_files[0]
            if not target.exists():
                print(f"  file missing: {target}")
                continue
            editor = os.environ.get("EDITOR", "vim")
            print(f"  opening {target.name} in $EDITOR ({editor})...")
            try:
                subprocess.run([editor, str(target)], check=False)
            except FileNotFoundError:
                print(f"  $EDITOR={editor} not found, falling back to cat")
                subprocess.run(["cat", str(target)])
            return "modified"
        if choice in ("v", "view"):
            if not output_files or not output_files[0].exists():
                print("  no file to view")
                continue
            text = output_files[0].read_text(encoding="utf-8", errors="replace")
            head = "\n".join(text.splitlines()[:50])
            print(f"---- {output_files[0].name} (first 50 lines) ----")
            print(head)
            print("---- end ----")
            continue
        if choice in ("r", "reject"):
            return "rejected"
        if choice in ("s", "skip"):
            return "modified"
        print("  please type a / e / v / r / s")


def cmd_run_agent(args: argparse.Namespace) -> int:
    """单跑某 agent. 接 graybox (a/e/v/r/s) + 写 checkpoint + progress timing."""
    project_root = Path(args.project_root).resolve()
    agent_role = args.agent
    if agent_role not in AGENT_ROLES:
        print(f"[error] unknown agent: {agent_role}. valid: {AGENT_ROLES}")
        return 2

    repo_root = Path(__file__).resolve().parents[2]
    rel = project_root.relative_to(repo_root) if str(project_root).startswith(str(repo_root)) else project_root
    print(f"[run-agent] project={rel} agent={agent_role}")

    # P2: progress timing — print heartbeat every 5s while _run_stage runs (sync)
    print(f"[run-agent] invoking orchestrator._run_stage() at {time.strftime('%H:%M:%S')}...")
    t0 = time.time()
    try:
        result = _run_stage(
            project_root=project_root,
            stage=agent_role,
            run_id=args.run_id or "cli_run_agent",
            agent_display_name=agent_role.capitalize() + "Agent",
        )
    except Exception as exc:
        print(f"[run-agent] error during _run_stage: {exc}")
        return 1
    duration = time.time() - t0
    print(f"[run-agent] _run_stage() finished in {duration:.1f}s")

    # graybox prompt
    output_files = default_output_files_for_agent(project_root, agent_role)
    decision = prompt_graybox(stage=agent_role, agent_role=agent_role, output_files=output_files)

    # checkpoint
    save_checkpoint_from_input(project_root, agent_role, decision, note=f"cli run-agent {agent_role}")

    print_manifest({
        "stage": agent_role,
        "decision": decision,
        "duration_s": round(duration, 1),
        "result_preview": str(result)[:500],
    })
    return 0

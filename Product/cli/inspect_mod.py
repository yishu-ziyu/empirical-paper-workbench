"""Inspect subcommand: list runs / agents / checkpoints / paper."""
from __future__ import annotations

import argparse
from pathlib import Path

from Product.cli._common import (
    REPO_ROOT,
    list_agents_in_run,
    list_runs,
    load_checkpoints,
)
from Product.backend.workbench_paths import runs_base, stage_dir


def cmd_inspect(args: argparse.Namespace) -> int:
    workspace_root = Path(args.workspace_root or REPO_ROOT).resolve()

    if args.target == "runs":
        runs = list_runs(workspace_root)
        if not runs:
            print(f"[inspect] no runs found at {runs_base(workspace_root)}")
            return 0
        print(f"[inspect] {len(runs)} run(s):")
        for r in runs:
            print(f"  - {r.name}")
        return 0

    if args.target == "agents":
        if not args.run:
            print("[inspect] --run <run_id> required for `inspect agents`")
            return 2
        run_dir = runs_base(workspace_root) / args.run
        if not run_dir.exists():
            print(f"[inspect] run not found: {run_dir}")
            return 1
        agents = list_agents_in_run(run_dir)
        print(f"[inspect] run={args.run} has {len(agents)} agent segment(s):")
        for name, sub in agents:
            files = sorted([f.name for f in sub.iterdir() if f.is_file()])
            preview = ', '.join(files[:4]) + ('...' if len(files) > 4 else '')
            print(f"  - {name} ({sub.name}/): {len(files)} file(s) [{preview}]")
        return 0

    if args.target == "checkpoints":
        if not args.run:
            print("[inspect] --run <run_id> required for `inspect checkpoints`")
            return 2
        run_dir = runs_base(workspace_root) / args.run
        if not run_dir.exists():
            print(f"[inspect] run not found: {run_dir}")
            return 1
        cps = load_checkpoints(run_dir)
        if not cps:
            print(f"[inspect] no checkpoints recorded for {args.run}")
            return 0
        print(f"[inspect] {len(cps)} checkpoint(s) for {args.run}:")
        for cp in cps:
            stage = cp.get("stage", "?")
            status = cp.get("status", "?")
            note = cp.get("user_feedback", "")
            # P1 fix: orchestrator writes created_at + resolved_at, not updated_at
            ts = cp.get("resolved_at") or cp.get("created_at") or ""
            print(f"  - {stage:<14} status={status:<10}  ts={ts}  note={note[:60]}")
        return 0

    if args.target == "paper":
        if not args.run:
            print("[inspect] --run <run_id> required for `inspect paper`")
            return 2
        run_dir = runs_base(workspace_root) / args.run
        for candidate in (
            run_dir / stage_dir("06_writing") / "paper_draft.md",
            run_dir / "06_writing" / "paper_draft.md",
        ):
            if candidate.exists():
                text = candidate.read_text(encoding="utf-8")
                lines = text.splitlines()
                print(f"[inspect] paper_draft.md: {len(text)} chars, {len(lines)} lines")
                print("---- first 30 lines ----")
                for ln in lines[:30]:
                    print(ln)
                print("---- last 10 lines ----")
                for ln in lines[-10:]:
                    print(ln)
                return 0
        print(f"[inspect] no paper_draft.md in {run_dir}/{stage_dir('06_writing')}/ or {run_dir}/06_writing/")
        return 1

    print(f"[inspect] unknown --target {args.target}")
    return 2

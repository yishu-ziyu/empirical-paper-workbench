"""Demo subcommand: 一键 tour 某个 run (runs / agents / paper head 30 lines)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from Product.cli._common import REPO_ROOT, list_runs
from Product.backend.workbench_paths import runs_base, stage_dir


def cmd_demo(args: argparse.Namespace) -> int:
    """P3: 一键 tour. 不需要 --run, 自动选最近一个; 也可以显式传 --run."""
    workspace_root = Path(args.workspace_root or REPO_ROOT).resolve()
    runs = list_runs(workspace_root)
    if not runs:
        print(f"[demo] no runs found at {runs_base(workspace_root)}")
        return 0

    run_id = args.run
    if not run_id:
        # 默认用最近一个
        run_id = runs[-1].name
        print(f"[demo] no --run given, using latest: {run_id}")

    run_dir = runs_base(workspace_root) / run_id
    if not run_dir.exists():
        print(f"[demo] run not found: {run_dir}")
        return 1

    print(f"\n========== Codex CoPaper CLI demo (run={run_id}) ==========\n")

    # 1) inspect runs (1-line)
    print(f"--- 1) {len(runs)} run(s) in workspace ---")
    for r in runs[-3:]:
        print(f"  - {r.name}")
    if len(runs) > 3:
        print(f"  ... +{len(runs) - 3} earlier")
    print()

    # 2) inspect agents
    print(f"--- 2) agents in {run_id} ---")
    from Product.cli._common import list_agents_in_run
    agents = list_agents_in_run(run_dir)
    for name, sub in agents:
        n_files = sum(1 for f in sub.iterdir() if f.is_file())
        print(f"  {sub.name}  {name:<20}  {n_files} file(s)")
    print()

    # 3) inspect paper head
    paper = run_dir / stage_dir("06_writing") / "paper_draft.md"
    if not paper.exists():
        paper = run_dir / "06_writing" / "paper_draft.md"
    if paper.exists():
        text = paper.read_text(encoding="utf-8")
        lines = text.splitlines()
        print(f"--- 3) paper_draft.md ({len(text)} chars, {len(lines)} lines) ---")
        print("---- first 25 lines ----")
        for ln in lines[:25]:
            print(ln)
        print("...")
        print()
    else:
        print(f"--- 3) no paper_draft.md at {paper} ---\n")

    # 4) 收尾 + 引导
    print("--- 4) next steps (PM-friendly) ---")
    print(f"  - 看所有产物:    python3 Product/cli.py inspect --target agents --run {run_id}")
    print(f"  - 续跑 / 编辑:  python3 Product/cli.py run-agent --project-root {run_dir} --agent execution")
    print(f"  - 看 checkpoints: python3 Product/cli.py inspect --target checkpoints --run {run_id}")
    print(f"  - 重看 paper:   python3 Product/cli.py inspect --target paper --run {run_id}")
    print()
    return 0

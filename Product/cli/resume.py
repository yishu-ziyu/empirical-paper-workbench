"""Resume subcommand: 从 last checkpoint 续跑 run_workbench."""
from __future__ import annotations

import argparse
from pathlib import Path

from Product.backend.orchestrator import load_checkpoints, run_workbench
from Product.cli._common import print_manifest


def cmd_resume(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    checkpoints = load_checkpoints(project_root)
    if not checkpoints:
        print(f"[resume] no checkpoints found at {project_root}/.checkpoints/state.json — running from scratch")
    else:
        last = checkpoints[-1]
        print(f"[resume] last checkpoint: stage={last.get('stage')} status={last.get('status')}")
        print(f"[resume] {len(checkpoints)} checkpoint(s) on record; will skip already-approved stages")

    manifest = run_workbench(
        project_root,
        mode=args.mode,
        user_goal=args.user_goal or "",
    )
    print_manifest({"resumed_from_checkpoints": len(checkpoints), "manifest_keys": list(manifest.keys())})
    return 0

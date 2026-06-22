#!/usr/bin/env python3
"""CLI entry point for the empirical paper workflow runtime."""

from __future__ import annotations

import argparse
import sys

from runtime.pipeline import Pipeline
from runtime.state import PipelineState


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI: 论文流水线 orchestrator",
    )
    parser.add_argument(
        "--mode",
        choices=["execute", "dry-run", "resume"],
        default="execute",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Skip human checkpoints (CI/automation mode)",
    )
    parser.add_argument(
        "--start-step",
        default=None,
        help="Start from a specific step ID",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show pipeline state",
    )
    args = parser.parse_args()

    if args.status:
        state = PipelineState()
        s = state.to_dict()
        print(f"status: {s['status']}")
        print(f"current_step: {s.get('current_step')}")
        print(f"done: {len(s.get('history', []))} steps")
        print(f"failures: {s.get('failed_count', 0)}")
        if s.get("history"):
            for h in s["history"]:
                print(f"  {h['step_id']}: {h['result']}")
        sys.exit(0)

    pipeline = Pipeline(mode=args.mode, auto=args.auto, start_step=args.start_step)
    ok = pipeline.run()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

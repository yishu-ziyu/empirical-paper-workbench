#!/usr/bin/env python3
"""CLI entry point for the empirical paper workflow runtime."""

from __future__ import annotations

import argparse
import sys

from runtime.pipeline import Pipeline
from runtime.state import PipelineState


def main() -> None:
    parser = argparse.ArgumentParser(
        description="论文流水线 Orchestrator — 读 registry → 执行 10 步 → human checkpoint 管理",
    )
    parser.add_argument(
        "--mode",
        choices=["execute", "dry-run", "resume"],
        default="execute",
        help="execute=真实跑, dry-run=预演不写文件, resume=从上次停止处继续",
    )
    parser.add_argument(
        "--step",
        default=None,
        help="从指定步骤开始 (如 05_causal_analysis)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="显示当前 pipeline 状态",
    )
    args = parser.parse_args()

    if args.status:
        state = PipelineState()
        s = state.to_dict()
        print(f"状态: {s['status']}")
        print(f"当前步骤: {s.get('current_step')}")
        print(f"已完成: {len(s.get('history', []))} 步")
        print(f"失败次数: {s.get('failed_count', 0)}")
        if s.get("history"):
            print("\n历史:")
            for h in s["history"]:
                print(f"  {h['step_id']}: {h['result']}")
        sys.exit(0)

    pipeline = Pipeline(mode=args.mode, start_step=args.step)
    ok = pipeline.run()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

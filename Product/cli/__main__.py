"""argparse + main() for cli/ package."""
from __future__ import annotations

import argparse
from pathlib import Path

from Product.backend.orchestrator import run_workbench
from Product.backend.auto_research_service import run_auto_research
from Product.cli._common import AGENT_ROLES, print_manifest
from Product.cli.demo import cmd_demo
from Product.cli.graybox import cmd_run_agent
from Product.cli.inspect_mod import cmd_inspect
from Product.cli.resume import cmd_resume


def cmd_run_workbench(args: argparse.Namespace) -> int:
    manifest = run_workbench(
        Path(args.project_root).resolve(),
        mode=args.mode,
        user_goal=args.user_goal,
    )
    print_manifest(manifest)
    return 0


def cmd_auto_research(args: argparse.Namespace) -> int:
    manifest = run_auto_research(
        Path(args.project_root).resolve(),
        topic=args.topic,
        mode=args.mode,
        max_depth=args.max_depth,
        max_iterations=args.max_iterations,
    )
    print_manifest(manifest)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex CoPaper CLI v0.3 (gray-box, modular)")
    subs = parser.add_subparsers(dest="command", required=True)

    # v0.1 (preserved)
    run = subs.add_parser("run-workbench", help="[v0.1] 整链路跑 workbench")
    run.add_argument("--project-root", required=True)
    run.add_argument("--mode", default="dry-run", choices=["dry-run", "live"])
    run.add_argument("--user-goal", default="")
    run.set_defaults(func=cmd_run_workbench)

    auto = subs.add_parser("auto-research", help="[v0.1] 自动研究入口")
    auto.add_argument("--project-root", default=".")
    auto.add_argument("--topic", required=True)
    auto.add_argument("--mode", default="auto", choices=["auto", "dry-run"])
    auto.add_argument("--max-depth", type=int, default=2)
    auto.add_argument("--max-iterations", type=int, default=5)
    auto.set_defaults(func=cmd_auto_research)

    # v0.2 NEW
    ra = subs.add_parser("run-agent", help="[v0.2] 单跑某 agent (gray-box)")
    ra.add_argument("--project-root", required=True, help="run workspace 路径 (含 _shared/ 和 00_intake/ 等)")
    ra.add_argument("--agent", required=True, choices=AGENT_ROLES, help="agent role 名")
    ra.add_argument("--run-id", default="", help="可选, 自定义 run_id")
    ra.set_defaults(func=cmd_run_agent)

    rs = subs.add_parser("resume", help="[v0.2] 从 last checkpoint 续跑")
    rs.add_argument("--project-root", required=True)
    rs.add_argument("--mode", default="live", choices=["dry-run", "live"])
    rs.add_argument("--user-goal", default="")
    rs.set_defaults(func=cmd_resume)

    ins = subs.add_parser("inspect", help="[v0.2] 列 run / agent / checkpoint / paper")
    ins.add_argument("--target", required=True, choices=["runs", "agents", "checkpoints", "paper"])
    ins.add_argument("--workspace-root", default="", help="workbench 根 (默认 repo root)")
    ins.add_argument("--run", default="", help="run_id (e.g. run_charls_did_20260614_001)")
    ins.set_defaults(func=cmd_inspect)

    # v0.3 NEW
    demo = subs.add_parser("demo", help="[v0.3] 一键 tour 最新 run (runs + agents + paper head)")
    demo.add_argument("--run", default="", help="run_id (默认用最新一个)")
    demo.add_argument("--workspace-root", default="")
    demo.set_defaults(func=cmd_demo)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Product.backend.orchestrator import run_workbench


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex CoPaper internal workbench")
    subcommands = parser.add_subparsers(dest="command", required=True)

    run = subcommands.add_parser("run-workbench")
    run.add_argument("--project-root", required=True)
    run.add_argument("--mode", default="dry-run", choices=["dry-run", "live"])
    run.add_argument("--user-goal", default="")

    args = parser.parse_args()
    if args.command == "run-workbench":
        manifest = run_workbench(Path(args.project_root).resolve(), mode=args.mode, user_goal=args.user_goal)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

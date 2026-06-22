#!/usr/bin/env python3
"""Human checkpoint prompts for the empirical paper runtime."""

from __future__ import annotations

import sys
from typing import Sequence

_ASK = "[pipeline] 请确认:"


def ask(question: str, options: Sequence[str] | None = None) -> str:
    """Block and ask the user a question. Returns the answer string."""
    prompt = question
    if options:
        opts = "/".join(options)
        prompt = f"{question} [{opts}]"
    while True:
        try:
            answer = input(f"\n{_ASK} {prompt} ").strip()
        except EOFError:
            sys.exit(1)
        if not answer:
            continue
        if options and answer not in options:
            print(f"  请选择: {', '.join(options)}")
            continue
        return answer


def confirm(question: str, default: bool = False) -> bool:
    """Ask a yes/no question. Returns True for yes."""
    yes = "Y/n" if default else "y/N"
    raw = ask(f"{question} ({yes})", options=("y", "n", ""))
    if raw == "":
        return default
    return raw.lower() == "y"


def checkpoint(step_name: str, checkpoints: list[str]) -> None:
    """Display the human checkpoints for a step and wait for acknowledgement."""
    print(f"\n{'=' * 60}")
    print(f"  🔔  Human Checkpoint: {step_name}")
    print(f"{'=' * 60}")
    for i, cp in enumerate(checkpoints, 1):
        print(f"  {i}. {cp}")
    print()
    while True:
        try:
            raw = input("  确认以上判断? (yes / stop) ").strip().lower()
        except EOFError:
            sys.exit(1)
        if raw in ("yes", "y"):
            return
        if raw in ("stop", "s", "no", "n"):
            print("  流程已暂停。修复后重新运行即可恢复。")
            sys.exit(0)
        print("  请输入 yes 或 stop")


def report_progress(current: str, index: int, total: int, status: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  Step {index}/{total}: {current}  [{status}]")
    print(f"{'─' * 50}")

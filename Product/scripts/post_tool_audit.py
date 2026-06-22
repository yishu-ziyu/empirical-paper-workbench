#!/usr/bin/env python3
"""PostToolUse hook: 每次 Edit/Write 完成后,自动跑 integrity_audit。

从 stdin 读 Claude Code 传入的 JSON tool call 记录,
提取 file_path;如果文件在 Manuscripts/sections/ 下,跑 audit。

退出码语义(传递给 Claude Code):
  0 = audit 通过(继续)
  2 = audit 失败 / section 不在登记(阻断,LLM 收到 error)
  1 = 工具错误(audit 脚本本身炸了,不阻断)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECTION_DIR = PROJECT_ROOT / "Manuscripts" / "sections"
AUDIT_SCRIPT = PROJECT_ROOT / "evidence" / "integrity_audit.py"


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 1  # 工具错误

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    path = Path(file_path).resolve()
    try:
        path.relative_to(SECTION_DIR)
    except ValueError:
        return 0  # 不在 sections 目录,放过

    if path.suffix != ".md":
        return 0

    section = path.stem
    if not AUDIT_SCRIPT.exists():
        print(f"[post_tool_audit] audit script missing: {AUDIT_SCRIPT}", file=sys.stderr)
        return 1

    proc = subprocess.run(
        ["python3", str(AUDIT_SCRIPT), "--section", section],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    # 把 audit 的 stdout/stderr 透传,让 LLM 在被 block 时看到原因
    if proc.stdout:
        sys.stderr.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)

    if proc.returncode == 0:
        return 0
    if proc.returncode == 1:
        return 2  # audit 找到 BLOCKER,阻断 LLM
    return 1  # 工具错误,不阻断


if __name__ == "__main__":
    sys.exit(main())

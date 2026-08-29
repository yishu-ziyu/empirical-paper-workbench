#!/usr/bin/env python3
"""仓库根目录入口：派出三位审稿代理跑对照。

依赖 agent 已作为可编辑包安装（`pip install -e ./agent`），故 `from agent.eval...`
与 `from agent.nodes...` 无需任何进程级 sys.path 拼接即可唯一解析。
"""
from __future__ import annotations

from agent.eval.ab_review import main

if __name__ == "__main__":
    raise SystemExit(main())
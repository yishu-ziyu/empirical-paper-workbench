#!/usr/bin/env python3
"""仓库根目录入口：派出三位审稿代理跑对照。"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_AGENT = _ROOT / "agent"
if str(_AGENT) not in sys.path:
    sys.path.insert(0, str(_AGENT))

from eval.ab_review import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())

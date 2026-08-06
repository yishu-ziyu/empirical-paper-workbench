#!/usr/bin/env python3
"""Compatibility wrapper → scripts/serve_dashboard.py (default port 8765)."""
from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).with_name("serve_dashboard.py")
    raise SystemExit(runpy.run_path(str(target), run_name="__main__") or 0)

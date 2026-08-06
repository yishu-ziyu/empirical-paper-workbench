#!/usr/bin/env python3
"""CLI entry for full paper pipeline E2E.

Usage:
  PYTHONPATH=. python3 scripts/40_full_paper_pipeline_e2e.py
  PYTHONPATH=. python3 scripts/40_full_paper_pipeline_e2e.py --no-llm
  PYTHONPATH=. python3 scripts/40_full_paper_pipeline_e2e.py --model MiniMax-M3
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.full_pipeline import main

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Runtime runner — unified entry point for the empirical paper workflow.

Usage:
    python3 scripts/runtime_runner.py --mode dry-run
    python3 scripts/runtime_runner.py --mode execute
    python3 scripts/runtime_runner.py --mode execute --step 05_causal_analysis
    python3 scripts/runtime_runner.py --status
    python3 scripts/runtime_runner.py --resume
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.cli import main as runtime_main


if __name__ == "__main__":
    runtime_main()

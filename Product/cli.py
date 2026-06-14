"""Codex CoPaper CLI v0.3 — thin shell, see Product/cli/ for actual code.

Usage:
    python3 Product/cli.py <subcommand> [args]
    # or equivalently
    python3 -m Product.cli <subcommand> [args]
"""
import sys
from pathlib import Path

# Make 'Product' importable when invoked as a script (`python3 Product/cli.py ...`)
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from cli.__main__ import main  # noqa: E402  (cli is a sub-package of Product/)

if __name__ == "__main__":
    raise SystemExit(main())

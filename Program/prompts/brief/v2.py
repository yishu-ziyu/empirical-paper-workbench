"""brief prompt v2 loader — 紧凑 4 段（加速 + 节 token）。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v2.md"


def load_prompt_v2() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

"""brief prompt v3 loader — 4 段含 4 要素结构 + 可量化成功标准。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v3.md"


def load_prompt_v3() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

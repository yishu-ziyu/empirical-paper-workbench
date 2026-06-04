"""execution/section_results prompt v2 loader — 4 段结构（系数/经济/异质/对比）。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v2.md"


def load_prompt_v2() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

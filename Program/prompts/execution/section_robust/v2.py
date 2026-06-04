"""execution/section_robust prompt v2 loader — 4 段结构。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v2.md"


def load_prompt_v2() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

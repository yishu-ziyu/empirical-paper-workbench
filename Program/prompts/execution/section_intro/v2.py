"""execution/section_intro prompt v2 loader — 4 段 IMRaD 显式分段。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v2.md"


def load_prompt_v2() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

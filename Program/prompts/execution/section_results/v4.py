"""execution/section_results prompt v4 loader — evidence binding + 第 5 段 identification 联动。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v4.md"


def load_prompt_v4() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

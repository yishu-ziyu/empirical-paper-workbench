"""execution/section_intro prompt v3 loader — evidence binding 硬约束。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v3.md"


def load_prompt_v3() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

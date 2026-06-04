"""execution/section_robust prompt v4 loader — evidence binding + identification falsification。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v4.md"


def load_prompt_v4() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

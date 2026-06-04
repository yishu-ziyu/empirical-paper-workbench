"""execution/section_strategy prompt v4 loader — evidence binding + refutability 子段。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v4.md"


def load_prompt_v4() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

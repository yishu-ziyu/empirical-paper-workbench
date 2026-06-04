"""variables prompt v2 loader — 强化列名→研究变量映射的清晰度。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v2.md"


def load_prompt_v2() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

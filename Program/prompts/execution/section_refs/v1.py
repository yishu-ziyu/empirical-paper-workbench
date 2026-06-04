"""execution.section_refs prompt v1 loader。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v1.md"


def load_prompt_v1() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

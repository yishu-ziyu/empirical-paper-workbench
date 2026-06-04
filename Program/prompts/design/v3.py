"""design prompt v3 loader — 严格 JSON schema + 3 候选硬约束。"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v3.md"


def load_prompt_v3() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

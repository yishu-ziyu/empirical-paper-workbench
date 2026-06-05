"""brief prompt v4 loader — 4-step thinking with explicit STEP_N_DONE markers.

Used by Product.backend.wrapper.brief_stream_service to drive SSE step cards.
"""
from pathlib import Path

_PROMPT_PATH = Path(__file__).parent / "v4.md"


def load_prompt_v4() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")

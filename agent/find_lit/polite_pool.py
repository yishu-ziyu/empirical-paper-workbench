"""Re-export the FL polite-pool hook (shared with OpenAlex / Crossref / S2)."""
from ..nodes.literature_sources.polite_pool import (
    DEFAULT_MAILTO,
    ENV_MAILTO,
    mailto,
    polite_pool_note,
    user_agent,
)

__all__ = [
    "DEFAULT_MAILTO",
    "ENV_MAILTO",
    "mailto",
    "polite_pool_note",
    "user_agent",
]

"""FIND-LIT V1: OpenAlex + Crossref + S2, DOI dedupe, cards, bib export."""

from .cards import MIN_CARDS, has_min_cards, hits_to_cards, is_verifiable
from .chapter_gate import literature_write_allowed, literature_write_blockers
from .dedupe import dedupe_hits, normalize_doi
from .export import export_checked
from .polite_pool import mailto, polite_pool_note, user_agent
from .query import build_query, design_is_confirmed, session_design
from .search import check_cards, search_find_lit

__all__ = [
    "MIN_CARDS",
    "build_query",
    "check_cards",
    "dedupe_hits",
    "design_is_confirmed",
    "export_checked",
    "has_min_cards",
    "hits_to_cards",
    "is_verifiable",
    "literature_write_allowed",
    "literature_write_blockers",
    "mailto",
    "normalize_doi",
    "polite_pool_note",
    "search_find_lit",
    "session_design",
    "user_agent",
]

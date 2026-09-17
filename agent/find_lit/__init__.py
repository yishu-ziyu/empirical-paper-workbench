"""FIND-LIT V1: OpenAlex + Crossref + S2, DOI dedupe, cards, bib export.

Two uses of the same three sources: `topic_positioning` (search_find_lit,
confirmed design required) and `method_check` (check_method_literature, works on
a tentative design and records reading level + source status per evidence)."""

from .cards import MIN_CARDS, has_min_cards, hits_to_cards, is_verifiable
from .chapter_gate import literature_write_allowed, literature_write_blockers
from .dedupe import dedupe_hits, normalize_doi
from .export import export_checked
from .fetch_papers import (
    DEFAULT_PURPOSE,
    PURPOSE_METHOD_CHECK,
    PURPOSE_TOPIC_POSITIONING,
    VALID_PURPOSES,
    V1_SOURCES,
    default_searchers,
    fetch_papers,
)
from .method_check import (
    READING_LEVELS,
    annotate_evidence,
    check_method_literature,
    reading_level_of,
    source_status_for,
)
from .polite_pool import mailto, polite_pool_note, user_agent
from .query import (
    build_method_check_query,
    build_query,
    build_risk_queries,
    classify_method,
    design_is_confirmed,
    session_design,
)
from .search import check_cards, search_find_lit

__all__ = [
    "DEFAULT_PURPOSE",
    "MIN_CARDS",
    "PURPOSE_METHOD_CHECK",
    "PURPOSE_TOPIC_POSITIONING",
    "READING_LEVELS",
    "VALID_PURPOSES",
    "V1_SOURCES",
    "annotate_evidence",
    "build_method_check_query",
    "build_query",
    "build_risk_queries",
    "check_cards",
    "check_method_literature",
    "classify_method",
    "dedupe_hits",
    "default_searchers",
    "design_is_confirmed",
    "export_checked",
    "fetch_papers",
    "has_min_cards",
    "hits_to_cards",
    "is_verifiable",
    "literature_write_allowed",
    "literature_write_blockers",
    "mailto",
    "normalize_doi",
    "polite_pool_note",
    "reading_level_of",
    "search_find_lit",
    "session_design",
    "source_status_for",
    "user_agent",
]

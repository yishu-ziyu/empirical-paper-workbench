"""R-lit-bar mailto polite pool (V1 stub).

OpenAlex / Crossref / S2 User-Agent must include mailto. G0 did not pick a
production address; `mailto:dev@local` is the V1 stub, replaceable via
ECONPAPER_POLITE_MAILTO without committing credentials.
"""
from __future__ import annotations

import os

DEFAULT_MAILTO = "dev@local"
ENV_MAILTO = "ECONPAPER_POLITE_MAILTO"
PRODUCT = "econpaper"


def mailto() -> str:
    raw = (os.environ.get(ENV_MAILTO) or "").strip()
    return raw or DEFAULT_MAILTO


def user_agent() -> str:
    return f"{PRODUCT}/1.0 (find-lit; mailto:{mailto()})"


def polite_pool_note() -> dict[str, str]:
    return {
        "mailto": mailto(),
        "user_agent": user_agent(),
        "hook": ENV_MAILTO,
    }

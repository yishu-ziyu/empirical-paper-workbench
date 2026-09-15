"""FD-BE-fetch-wdi: confirmed growth design → WDI download or honest link.

Tries the public World Bank Indicators API and writes a CSV into the
session workspace when that API returns observations. Otherwise returns
the WDI landing URL with ``source_kind=external_link`` and an honest
upload note.

Never treats ``barro1991_growth`` (or any classic-5 fixture) as the WDI
fetch. Does not set ``dataAttached``. Unconfirmed design is refused.
"""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Callable, Mapping

from agent.find_data.plan import (
    DesignUnconfirmed,
    classify_route_family,
    is_confirmed_design,
)

HttpGet = Callable[[str], bytes]

DEFAULT_INDICATOR = "NY.GDP.PCAP.KD.ZG"
WDI_PAGE = "https://data.worldbank.org/indicator/{indicator}"
WDI_API = "https://api.worldbank.org/v2/country/all/indicator/{indicator}"
UA = "econpaper/1.0 (find-data; mailto:dev@local)"
HTTP_TIMEOUT_SECONDS = 10
MAX_PAGES = 4
PER_PAGE = 20000
_INDICATOR_RE = re.compile(r"^[A-Z]{2}\.[A-Z0-9.]+$")
_HTML_PREFIXES = (b"<!doctype html", b"<html", b"<head", b"<body")
_BARRO_MARKERS = (
    "barro1991_growth",
    "classic-5:barro",
    "fixtures/classic-5",
)

STAGING_DIR = "fetch"
_FORBIDDEN_COPY = (
    "WDI fetch must not copy a Barro / classic-5 fixture as the download"
)


class WdiFetchNotApplicable(ValueError):
    """WDI session fetch is the growth venue only."""

    def __init__(self, reason: str = "wdi_fetch_requires_growth_design") -> None:
        super().__init__(reason)
        self.reason = reason


def wdi_page_url(indicator: str = DEFAULT_INDICATOR) -> str:
    return WDI_PAGE.format(indicator=_safe_indicator(indicator))


def fetch_wdi(
    design: Mapping[str, Any] | None,
    *,
    workspace: Path | str,
    http_get: HttpGet | None = None,
    indicator: str | None = None,
) -> dict[str, Any]:
    """Download WDI into *workspace* or return an honest link+upload row.

    Raises ``DesignUnconfirmed`` when design is missing/draft.
    Raises ``WdiFetchNotApplicable`` when the confirmed design is not growth.
    """
    if not is_confirmed_design(design):
        raise DesignUnconfirmed("design_unconfirmed")
    assert design is not None
    family = classify_route_family(design)
    if family != "growth":
        raise WdiFetchNotApplicable("wdi_fetch_requires_growth_design")

    code = _safe_indicator(indicator or DEFAULT_INDICATOR)
    getter = http_get if http_get is not None else _default_http_get
    observations, fail_reason = _pull_observations(getter, code)
    if observations:
        candidate = _write_session_csv(design, workspace, code, observations)
        if candidate is not None:
            return candidate
        fail_reason = fail_reason or "empty_or_unparseable"
    return _link_only(design, code, fail_reason or "empty_or_unparseable")


def _safe_indicator(raw: str) -> str:
    text = str(raw or "").strip().upper()
    if _INDICATOR_RE.fullmatch(text):
        return text
    return DEFAULT_INDICATOR


def _default_http_get(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
        return resp.read()


def _pull_observations(
    http_get: HttpGet,
    indicator: str,
) -> tuple[list[Mapping[str, Any]], str]:
    rows: list[Mapping[str, Any]] = []
    page = 1
    pages = 1
    last_reason = "http_error"
    while page <= pages and page <= MAX_PAGES:
        url = (
            f"{WDI_API.format(indicator=indicator)}"
            f"?format=json&per_page={PER_PAGE}&page={page}"
        )
        try:
            raw = http_get(url)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            return rows, last_reason if rows else "http_error"
        parsed, reason, meta_pages = _parse_worldbank_payload(raw)
        if not parsed and not rows:
            return [], reason
        rows.extend(parsed)
        pages = meta_pages or 1
        last_reason = reason
        page += 1
    if not rows:
        return [], last_reason
    return rows, ""


def _parse_worldbank_payload(
    raw: bytes,
) -> tuple[list[Mapping[str, Any]], str, int]:
    blob = raw.lstrip()
    if not blob:
        return [], "empty_or_unparseable", 1
    lower = blob[:64].lower()
    if any(lower.startswith(prefix) for prefix in _HTML_PREFIXES):
        return [], "html_landing", 1
    try:
        payload = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return [], "empty_or_unparseable", 1
    if isinstance(payload, Mapping) and payload.get("message"):
        return [], "empty_or_unparseable", 1
    if not isinstance(payload, list) or not payload:
        return [], "empty_or_unparseable", 1
    meta = payload[0] if isinstance(payload[0], Mapping) else {}
    if meta.get("message"):
        return [], "empty_or_unparseable", 1
    try:
        pages = int(meta.get("pages") or 1)
    except (TypeError, ValueError):
        pages = 1
    items = payload[1] if len(payload) > 1 else []
    if not isinstance(items, list):
        return [], "empty_or_unparseable", 1
    observations = [item for item in items if isinstance(item, Mapping)]
    if not observations:
        return [], "empty_or_unparseable", pages
    return observations, "", pages


def _write_session_csv(
    design: Mapping[str, Any],
    workspace: Path | str,
    indicator: str,
    observations: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    csv_text = _observations_to_csv(indicator, observations)
    if not csv_text:
        return None
    root = Path(workspace)
    dest_dir = root / STAGING_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"wdi_{indicator}.csv"
    if _looks_like_barro(dest):
        raise RuntimeError(_FORBIDDEN_COPY)
    dest.write_text(csv_text, encoding="utf-8")
    session_path = f"{root.name}/{STAGING_DIR}/{dest.name}"
    if _looks_like_barro(session_path):
        dest.unlink(missing_ok=True)
        raise RuntimeError(_FORBIDDEN_COPY)
    return _candidate(
        design,
        indicator=indicator,
        source_kind="fetched",
        fetch_status="into_session",
        session_path=session_path,
        reason="world bank indicators api",
        notes=(
            "WDI public download into session; not attached; "
            "not a Barro fixture"
        ),
    )


def _observations_to_csv(
    indicator: str,
    observations: Sequence[Mapping[str, Any]],
) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["country", "countryiso3code", "year", indicator])
    n = 0
    for obs in observations:
        if not isinstance(obs, Mapping):
            continue
        year = str(obs.get("date") or "").strip()
        value = obs.get("value")
        if not year or value is None:
            continue
        country = obs.get("country")
        name = ""
        if isinstance(country, Mapping):
            name = str(country.get("value") or "").strip()
        iso = str(obs.get("countryiso3code") or "").strip()
        writer.writerow([name, iso, year, value])
        n += 1
    if n == 0:
        return ""
    return buf.getvalue()


def _link_only(
    design: Mapping[str, Any],
    indicator: str,
    reason: str,
) -> dict[str, Any]:
    return _candidate(
        design,
        indicator=indicator,
        source_kind="external_link",
        fetch_status="link_only",
        session_path=None,
        reason=reason,
        notes=(
            "WDI public API did not land bytes; followable link plus "
            "honest upload; not a Barro fixture"
        ),
    )


def _candidate(
    design: Mapping[str, Any],
    *,
    indicator: str,
    source_kind: str,
    fetch_status: str,
    session_path: str | None,
    reason: str,
    notes: str,
) -> dict[str, Any]:
    outcome = str(design.get("outcome") or "").strip()
    treatment = str(design.get("treatment") or "").strip()
    method = str(design.get("method") or "").strip().lower()
    url = wdi_page_url(indicator)
    return {
        "source_id": f"wdi:{indicator}",
        "source_kind": source_kind,
        "title": (
            "World Bank World Development Indicators "
            f"({indicator})"
        ),
        "url_or_fixture": url,
        "license": "cc-by-4.0",
        "suggested_cols": [c for c in (outcome, treatment, indicator) if c],
        "design_fit": {
            "method": method,
            "outcome": outcome,
            "treatment": treatment,
            "notes": notes,
        },
        "fetch": {
            "status": fetch_status,
            "session_path": session_path,
            "reason": reason,
        },
    }


def _looks_like_barro(path: Path | str) -> bool:
    text = str(path).replace("\\", "/").lower()
    return any(marker in text for marker in _BARRO_MARKERS)


__all__ = [
    "DEFAULT_INDICATOR",
    "DesignUnconfirmed",
    "WdiFetchNotApplicable",
    "fetch_wdi",
    "wdi_page_url",
]

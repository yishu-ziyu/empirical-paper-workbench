"""Data candidates after confirmed ``session.design`` (FD-BE-suggest).

Reads a confirmed design's facets, searches Dataverse, and may list a
matching classic-5 / teaching fixture. Fixtures are candidates only —
never an answer key, never an attach. Without a fixture id the R-sources
external path (Card zip, IPUMS, WDI, FRED, Dataverse) still appears.

Does not propose or confirm a design, does not attach, does not set
``dataAttached`` / ``allow_did``, and does not emit a find-data plan.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from agent.data_honesty import (
    count_csv_data_rows,
    honesty_for_n,
    is_found_scale,
    is_toy_filename,
)
from agent.design.spec import norm_method
from agent.find_data.plan import is_confirmed_design

REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CLASSIC5 = REPO_ROOT / "fixtures" / "classic-5"
CATALOG_ENV_FILE = "ECONPAPER_CLASSIC5_CATALOG"
CATALOG_ENV_DIR = "ECONPAPER_CLASSIC5_DIR"

DATAVERSE_SEARCH = "https://dataverse.harvard.edu/api/search"
DATAVERSE_HOME = "https://dataverse.harvard.edu/"
UA = "econpaper/1.0 (find-data; mailto:dev@local)"
HTTP_TIMEOUT_SECONDS = 10
MAX_DATAVERSE_HITS = 8
_FIXTURE_EXTS = (".csv", ".dta", ".xlsx", ".xls")

CANDIDATE_FIELDS = (
    "source_id",
    "title",
    "url_or_fixture",
    "license",
    "suggested_cols",
    "design_fit",
)

_MINWAGE = re.compile(
    r"最低工资|minimum[\s\-]?wages?|min[\s_]?wage|"
    r"card[\s&\-]+krueger|card[\s]+and[\s]+krueger|"
    r"nj[\s\-]?pa|新泽西",
    re.I,
)
_SCHOOLING = re.compile(
    r"受教育|教育年限|schooling|\beducation\b|教育|mincer|wage1",
    re.I,
)
_WAGES = re.compile(r"(?<!最低)工资|\bwages?\b|收入|earnings", re.I)
_GROWTH = re.compile(
    r"\bbarro\b|经济增长|economic\s+growth|determinants of growth|"
    r"跨国增长|增长回归|cross[\s\-]?country\s+growth",
    re.I,
)
_MACRO = re.compile(
    r"\bfred\b|interest\s+rate|unemployment\s+rate|inflation|"
    r"federal\s+funds|macro\b|联邦基金|宏观",
    re.I,
)

_FIXTURE_IDS = {
    "educ_wage": ("schooling-wages", "wage1"),
    "minwage": ("ck1994_long", "ck1994", "minimum-wage-employment"),
    "growth": ("barro1991_growth",),
    "macro": (),
    "else": (),
}

_FIXTURE_META = {
    "ck1994_long": ("Card and Krueger minimum wage", "public-reproduction"),
    "ck1994": ("Card and Krueger minimum wage", "public-reproduction"),
    "minimum-wage-employment": ("Minimum wage and employment", "public-reproduction"),
    "barro1991_growth": ("Barro cross-country growth", "public-reproduction"),
    "schooling-wages": ("Education and wages", "public-reproduction"),
    "wage1": ("Wooldridge wage1 teaching extract", "public-reproduction"),
}

_SOURCE_ID = {
    "wage1": "wage1",
}

CARD_ZIP_URL = "https://davidcard.berkeley.edu/data_sets.html"
IPUMS_URL = "https://cps.ipums.org/cps/"
WDI_URL = "https://data.worldbank.org/indicator/NY.GDP.PCAP.KD.ZG"
FRED_URL = "https://fred.stlouisfed.org/series/UNRATE"


def is_real_candidate(obj: Any) -> bool:
    """True iff *obj* is a §5 real candidate (not a classic-5 id string)."""
    if not isinstance(obj, Mapping):
        return False
    for key in CANDIDATE_FIELDS:
        if key not in obj:
            return False
    source_id = str(obj.get("source_id") or "").strip()
    title = str(obj.get("title") or "").strip()
    url = str(obj.get("url_or_fixture") or "").strip()
    license_text = str(obj.get("license") or "").strip()
    if not source_id or not title or not url or not license_text:
        return False
    if url == source_id or url in {
        "ck1994",
        "ck1994_long",
        "minimum-wage-employment",
        "barro1991_growth",
        "schooling-wages",
    }:
        return False
    cols = obj.get("suggested_cols")
    fit = obj.get("design_fit")
    if not isinstance(cols, list) or not isinstance(fit, Mapping):
        return False
    return True


def suggest_data_candidates(
    design: Mapping[str, Any] | None,
    *,
    dataverse_search: Callable[[str], Sequence[Mapping[str, Any]]] | None = None,
    catalog_dir: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Return §5 candidates for a confirmed design. Unconfirmed → []."""
    if not is_confirmed_design(design):
        return []
    assert design is not None
    family = _route_family(design)
    search = (
        dataverse_search
        if dataverse_search is not None
        else search_dataverse
    )
    query = _search_query(design)

    found: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add(item: Mapping[str, Any] | None) -> None:
        if item is None or not is_real_candidate(item):
            return
        sid = str(item["source_id"])
        if sid in seen:
            return
        seen.add(sid)
        found.append(dict(item))

    for fixture in _fixture_candidates(design, family, catalog_dir):
        _add(fixture)
    for external in _route_externals(design, family):
        _add(external)
    for hit in _dataverse_candidates(design, query, search):
        _add(hit)
    if not any(str(c["source_id"]).startswith("dataverse:") for c in found):
        _add(_dataverse_landing(design, query))

    return found


def search_dataverse(
    query: str,
    *,
    max_results: int = MAX_DATAVERSE_HITS,
) -> list[dict[str, Any]]:
    """Harvard Dataverse catalog search. Network / parse errors → []."""
    if not query or not str(query).strip():
        return []
    params = urllib.parse.urlencode(
        {
            "q": query.strip(),
            "type": "dataset",
            "per_page": str(min(max_results, MAX_DATAVERSE_HITS)),
        }
    )
    url = f"{DATAVERSE_SEARCH}?{params}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError):
        return []
    if not isinstance(payload, Mapping) or payload.get("status") != "OK":
        return []
    items = ((payload.get("data") or {}) if isinstance(payload.get("data"), Mapping) else {}).get(
        "items"
    ) or []
    hits: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        if str(item.get("type") or "dataset").lower() not in {"", "dataset"}:
            continue
        mapped = _map_dataverse_item(item)
        if mapped is not None:
            hits.append(mapped)
        if len(hits) >= max_results:
            break
    return hits


def _facet_blob(design: Mapping[str, Any]) -> str:
    source = design.get("source") if isinstance(design.get("source"), Mapping) else {}
    parts = [
        design.get("outcome"),
        design.get("treatment"),
        source.get("title") if isinstance(source, Mapping) else "",
        source.get("question") if isinstance(source, Mapping) else "",
    ]
    return " ".join(str(p).strip() for p in parts if str(p or "").strip())


def _route_family(design: Mapping[str, Any]) -> str:
    """R-sources family. Specific families before ``else``; wage≠minwage."""
    text = _facet_blob(design)
    if _MINWAGE.search(text):
        return "minwage"
    if _SCHOOLING.search(text) and _WAGES.search(text):
        return "educ_wage"
    if _GROWTH.search(text):
        return "growth"
    if _MACRO.search(text):
        return "macro"
    return "else"


def _search_query(design: Mapping[str, Any]) -> str:
    source = design.get("source") if isinstance(design.get("source"), Mapping) else {}
    parts = [
        design.get("outcome"),
        design.get("treatment"),
        source.get("title") if isinstance(source, Mapping) else "",
        source.get("question") if isinstance(source, Mapping) else "",
    ]
    return " ".join(str(p).strip() for p in parts if str(p or "").strip())


def _method(design: Mapping[str, Any]) -> str:
    return norm_method(design.get("method")) or str(design.get("method") or "").strip().lower()


def _design_fit(design: Mapping[str, Any], *, notes: str) -> dict[str, str]:
    return {
        "method": _method(design),
        "outcome": str(design.get("outcome") or "").strip(),
        "treatment": str(design.get("treatment") or "").strip(),
        "notes": notes,
    }


def _suggested_from_design(design: Mapping[str, Any], extras: Iterable[str] = ()) -> list[str]:
    cols: list[str] = []
    for key in ("outcome", "treatment", "treated", "period"):
        val = str(design.get(key) or "").strip()
        if val and val not in cols:
            cols.append(val)
    for extra in extras:
        val = str(extra).strip()
        if val and val not in cols:
            cols.append(val)
    return cols


def _candidate(
    *,
    source_id: str,
    title: str,
    url_or_fixture: str,
    license: str,
    suggested_cols: Sequence[str],
    design: Mapping[str, Any],
    notes: str,
    found: bool = True,
    teaching_fixture: bool = False,
    n_rows: int | None = None,
    honesty_warning: str | None = None,
) -> dict[str, Any]:
    item = {
        "source_id": source_id,
        "title": title,
        "url_or_fixture": url_or_fixture,
        "license": license,
        "suggested_cols": list(suggested_cols),
        "design_fit": _design_fit(design, notes=notes),
        "found": found,
        "teaching_fixture": teaching_fixture,
        "n_rows": n_rows,
    }
    if honesty_warning:
        item["honesty_warning"] = honesty_warning
    return item


def _route_externals(
    design: Mapping[str, Any],
    family: str,
) -> list[dict[str, Any]]:
    if family == "minwage":
        return [
            _candidate(
                source_id="card-zip:njmin",
                title="Card–Krueger NJ–PA fast-food data (author zip)",
                url_or_fixture=CARD_ZIP_URL,
                license="author-posted",
                suggested_cols=[],
                design=design,
                notes="external path; Card zip; candidate only",
            )
        ]
    if family == "educ_wage":
        return [
            _candidate(
                source_id="ipums:cps",
                title="IPUMS CPS / USA extracts",
                url_or_fixture=IPUMS_URL,
                license="registration-required",
                suggested_cols=[],
                design=design,
                notes="external path; IPUMS; candidate only",
            )
        ]
    if family == "growth":
        return [
            _candidate(
                source_id="wdi:NY.GDP.PCAP.KD.ZG",
                title="World Bank World Development Indicators (GDP growth)",
                url_or_fixture=WDI_URL,
                license="cc-by-4.0",
                suggested_cols=[],
                design=design,
                notes="external path; WDI; candidate only",
            )
        ]
    if family == "macro":
        return [
            _candidate(
                source_id="fred:UNRATE",
                title="FRED unemployment rate (UNRATE)",
                url_or_fixture=FRED_URL,
                license="public",
                suggested_cols=[],
                design=design,
                notes="external path; FRED; candidate only",
            )
        ]
    return []


def _dataverse_landing(
    design: Mapping[str, Any],
    query: str,
) -> dict[str, Any]:
    if query:
        url = (
            "https://dataverse.harvard.edu/dataverse/harvard?"
            + urllib.parse.urlencode({"q": query})
        )
    else:
        url = DATAVERSE_HOME
    return _candidate(
        source_id="dataverse:search",
        title="Harvard Dataverse catalog search",
        url_or_fixture=url,
        license="unknown",
        suggested_cols=[],
        design=design,
        notes="Dataverse backup; candidate only",
    )


def _map_dataverse_item(item: Mapping[str, Any]) -> dict[str, Any] | None:
    name = str(item.get("name") or item.get("title") or "").strip()
    global_id = str(item.get("global_id") or item.get("globalId") or "").strip()
    raw_url = str(item.get("url") or "").strip()
    if global_id.lower().startswith("doi:"):
        doi = global_id.split(":", 1)[1]
        doi_url = f"https://doi.org/{doi}"
    elif global_id.lower().startswith("https://doi.org/"):
        doi_url = global_id
    else:
        doi_url = ""
    url = raw_url or doi_url
    if not name or not url:
        return None
    source_id = f"dataverse:{global_id}" if global_id else f"dataverse:{url}"
    license_text = _license_from_item(item)
    return {
        "source_id": source_id,
        "title": name,
        "url_or_fixture": url,
        "license": license_text,
        "suggested_cols": [],
    }


def _license_from_item(item: Mapping[str, Any]) -> str:
    raw = item.get("license")
    if isinstance(raw, Mapping):
        text = str(raw.get("name") or raw.get("uri") or "").strip()
    else:
        text = str(raw or "").strip()
    return text or "unknown"


def _dataverse_candidates(
    design: Mapping[str, Any],
    query: str,
    search: Callable[[str], Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    try:
        hits = list(search(query) if query else [])
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for hit in hits:
        if not isinstance(hit, Mapping):
            continue
        if "source_id" in hit and "url_or_fixture" in hit:
            mapped = dict(hit)
        else:
            mapped = _map_dataverse_item(hit) or {}
        if not mapped:
            continue
        out.append(
            _candidate(
                source_id=str(mapped["source_id"]),
                title=str(mapped["title"]),
                url_or_fixture=str(mapped["url_or_fixture"]),
                license=str(mapped.get("license") or "unknown"),
                suggested_cols=list(mapped.get("suggested_cols") or []),
                design=design,
                notes="Dataverse search hit; candidate only",
            )
        )
    return out


def _classic5_dir(catalog_dir: Path | str | None) -> Path:
    if catalog_dir is not None:
        return Path(catalog_dir)
    env_file = (os.getenv(CATALOG_ENV_FILE) or "").strip()
    if env_file:
        return Path(env_file).expanduser().parent
    env_dir = (os.getenv(CATALOG_ENV_DIR) or "").strip()
    if env_dir:
        return Path(env_dir).expanduser()
    return _DEFAULT_CLASSIC5


def _read_catalog_titles(catalog_dir: Path) -> dict[str, str]:
    catalog = catalog_dir / "catalog.json"
    try:
        raw = json.loads(catalog.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return {}
    if not isinstance(raw, Mapping) or raw.get("catalog_id") != "classic-5":
        return {}
    titles: dict[str, str] = {}
    for item in raw.get("entries") or []:
        if not isinstance(item, Mapping):
            continue
        entry_id = str(item.get("id") or "").strip()
        title = str(item.get("title") or "").strip()
        if entry_id and title:
            titles[entry_id] = title
    return titles


def _find_fixture_file(catalog_dir: Path, entry_id: str) -> Path | None:
    for ext in _FIXTURE_EXTS:
        path = catalog_dir / f"{entry_id}{ext}"
        if path.is_file():
            return path
    return None


def _fixture_url(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _fixture_candidates(
    design: Mapping[str, Any],
    family: str,
    catalog_dir: Path | str | None,
) -> list[dict[str, Any]]:
    root = _classic5_dir(catalog_dir)
    titles = _read_catalog_titles(root)
    wanted = list(_FIXTURE_IDS.get(family, ()))
    if family == "else":
        blob = _facet_blob(design).lower()
        wanted = [
            entry_id
            for entry_id, title in titles.items()
            if entry_id.lower() in blob or any(
                token and token in blob
                for token in title.lower().split()
                if len(token) >= 4
            )
        ]
    found: list[dict[str, Any]] = []
    for entry_id in wanted:
        path = _find_fixture_file(root, entry_id)
        if path is None:
            continue
        if is_toy_filename(path):
            continue
        n_rows = count_csv_data_rows(path)
        honesty = honesty_for_n(n_rows, name=path.name)
        if not honesty["found"] or not is_found_scale(n_rows):
            continue
        meta_title, license_text = _FIXTURE_META.get(
            entry_id, (entry_id, "unknown")
        )
        title = titles.get(entry_id) or meta_title
        source_id = _SOURCE_ID.get(entry_id, f"classic-5:{entry_id}")
        extras: tuple[str, ...] = ()
        if family == "minwage":
            extras = ("employment", "treated", "period")
        found.append(
            _candidate(
                source_id=source_id,
                title=title,
                url_or_fixture=_fixture_url(path),
                license=license_text,
                suggested_cols=_suggested_from_design(design, extras),
                design=design,
                notes=f"matches confirmed {family}; candidate only",
                found=True,
                teaching_fixture=False,
                n_rows=n_rows,
            )
        )
    return found

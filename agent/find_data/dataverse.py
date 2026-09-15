"""FD-BE-fetch-dataverse: live Dataverse search + session download.

After confirmed ``session.design``, search Harvard Dataverse from design
facets and write a public file into the session workspace when the Native
API allows. Otherwise keep a followable dataset / search URL (honest
link + upload). Never copies a fixture into the session, never labels a
fixture as discovered / fetched, and never sets ``dataAttached``.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from agent.find_data.candidates import is_real_candidate, search_dataverse
from agent.find_data.plan import (
    DesignUnconfirmed,
    build_find_data_plan,
    is_confirmed_design,
    search_facets,
)
from agent.nodes.literature_sources.polite_pool import mailto

DATAVERSE_API = "https://dataverse.harvard.edu/api"
DATAVERSE_HOME = "https://dataverse.harvard.edu/"
DATAVERSE_SEARCH_PAGE = "https://dataverse.harvard.edu/dataverse/harvard"
SESSION_FETCH_DIR = "fetch/dataverse"
HTTP_TIMEOUT_SECONDS = 15
DOWNLOAD_TIMEOUT_SECONDS = 60
MAX_SEARCH_HITS = 8

_TABULAR_EXT = {
    ".csv",
    ".tsv",
    ".tab",
    ".dta",
    ".sav",
    ".xlsx",
    ".xls",
    ".rds",
    ".parquet",
}
_HTML_MARKERS = (b"<!doctype html", b"<html")
_FIXTURE_PREFIXES = ("classic-5:", "fixtures/")

SearchFn = Callable[[str], Sequence[Mapping[str, Any]]]
ListFilesFn = Callable[[str], Sequence[Mapping[str, Any]]]
DownloadFn = Callable[[str], tuple[bytes, str, str]]


def dataverse_user_agent() -> str:
    """Same mailto polite pool as FL; product token is find-data."""
    return f"econpaper/1.0 (find-data; mailto:{mailto()})"


def persistent_id_from_source_id(source_id: str | None) -> str | None:
    """``dataverse:doi:10.7910/DVN/…`` → ``doi:10.7910/DVN/…``. Else None."""
    raw = str(source_id or "").strip()
    if raw.startswith("dataverse:"):
        raw = raw[len("dataverse:") :].strip()
    if not raw or raw == "search":
        return None
    if raw.lower().startswith("https://doi.org/"):
        return "doi:" + raw.split("https://doi.org/", 1)[1].strip()
    if raw.lower().startswith("doi:") or raw.lower().startswith("hdl:"):
        return raw
    return None


def apply_dataverse_fetch(
    state: Mapping[str, Any] | None,
    *,
    workspace: Path | str,
    source_id: str | None = None,
    file_id: str | None = None,
    search: SearchFn | None = None,
    list_files: ListFilesFn | None = None,
    download_file: DownloadFn | None = None,
) -> dict[str, Any]:
    """Search/fetch Dataverse into ``session.find_data``. Unconfirmed → raise."""
    state = state or {}
    design = state.get("design")
    if not is_confirmed_design(design):
        raise DesignUnconfirmed("design_unconfirmed")
    assert isinstance(design, Mapping)
    dataverse_rows = search_and_fetch_dataverse(
        design,
        workspace=workspace,
        source_id=source_id,
        file_id=file_id,
        search=search,
        list_files=list_files,
        download_file=download_file,
    )
    stored = state.get("find_data")
    if isinstance(stored, dict) and stored.get("status") == "planned":
        record = dict(stored)
        record["candidates"] = _merge_dataverse_candidates(
            stored.get("candidates") or [],
            dataverse_rows,
        )
        return record
    record = build_find_data_plan(design)
    record["candidates"] = dataverse_rows
    return record


def search_and_fetch_dataverse(
    design: Mapping[str, Any],
    *,
    workspace: Path | str,
    source_id: str | None = None,
    file_id: str | None = None,
    search: SearchFn | None = None,
    list_files: ListFilesFn | None = None,
    download_file: DownloadFn | None = None,
) -> list[dict[str, Any]]:
    """Return Dataverse-only real candidates. Empty search still shows the path."""
    if not is_confirmed_design(design):
        return []
    search_fn = search if search is not None else search_dataverse
    list_fn = list_files if list_files is not None else list_dataset_files
    download_fn = download_file if download_file is not None else download_datafile
    dest_root = Path(workspace)

    query = _query_from_design(design)
    hits = _search_hits(design, query, search_fn)
    chosen = str(source_id or "").strip() or None
    if chosen and persistent_id_from_source_id(chosen) is None:
        chosen = None
    hits = _ensure_chosen_hit(design, hits, chosen)

    if not hits:
        landing = _search_landing(design, query)
        return [landing] if is_real_candidate(landing) else []

    if chosen:
        target = next((h for h in hits if h["source_id"] == chosen), hits[0])
        _try_fetch_one(
            target,
            dest_root,
            list_fn,
            download_fn,
            preferred_file_id=str(file_id).strip() if file_id else None,
        )
    else:
        _try_fetch_one(
            hits[0],
            dest_root,
            list_fn,
            download_fn,
            preferred_file_id=str(file_id).strip() if file_id else None,
        )

    out: list[dict[str, Any]] = []
    for hit in hits:
        row = dict(hit)
        if row.get("source_kind") != "fetched":
            fetch = row.get("fetch") if isinstance(row.get("fetch"), Mapping) else {}
            row["source_kind"] = "discovered"
            row["fetch"] = {
                "status": "link_only",
                "session_path": None,
                "reason": str(fetch.get("reason") or "download not yet attempted"),
            }
        out.append(row)
    return [c for c in out if _is_honest_dataverse_candidate(c)]


def list_dataset_files(persistent_id: str) -> list[dict[str, Any]]:
    """Native API file list. Network / parse errors → []."""
    pid = str(persistent_id or "").strip()
    if not pid:
        return []
    params = urllib.parse.urlencode({"persistentId": pid})
    url = (
        f"{DATAVERSE_API}/datasets/:persistentId/versions/"
        f":latest-published/files?{params}"
    )
    payload = _get_json(url)
    if not isinstance(payload, Mapping) or payload.get("status") != "OK":
        return []
    raw = payload.get("data")
    if isinstance(raw, Mapping):
        raw = raw.get("files") or []
    if not isinstance(raw, list):
        return []
    files: list[dict[str, Any]] = []
    for item in raw:
        mapped = _map_file_item(item)
        if mapped is not None:
            files.append(mapped)
    return files


def download_datafile(file_id: str) -> tuple[bytes, str, str]:
    """Return ``(body, content_type, filename)``. HTTP errors → empty body."""
    fid = str(file_id or "").strip()
    if not fid:
        return b"", "", ""
    url = f"{DATAVERSE_API}/access/datafile/{urllib.parse.quote(fid)}"
    status, body, content_type, filename = _get_bytes(url, timeout=DOWNLOAD_TIMEOUT_SECONDS)
    if status != 200 or not body:
        return b"", content_type, filename
    return body, content_type, filename


def _query_from_design(design: Mapping[str, Any]) -> str:
    facets = search_facets(dict(design))
    terms = [str(t).strip() for t in facets.get("query_terms") or [] if str(t).strip()]
    if terms:
        return " ".join(terms)
    return " ".join(
        p
        for p in (
            str(facets.get("outcome") or "").strip(),
            str(facets.get("treatment") or "").strip(),
            str(facets.get("title") or "").strip(),
            str(facets.get("question") or "").strip(),
        )
        if p
    )


def _search_hits(
    design: Mapping[str, Any],
    query: str,
    search_fn: SearchFn,
) -> list[dict[str, Any]]:
    try:
        raw = list(search_fn(query) if query else [])
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        mapped = _as_discovered(design, item)
        if mapped is not None and _is_honest_dataverse_candidate(mapped):
            out.append(mapped)
        if len(out) >= MAX_SEARCH_HITS:
            break
    return out


def _as_discovered(
    design: Mapping[str, Any],
    item: Mapping[str, Any],
) -> dict[str, Any] | None:
    if "source_id" in item and "url_or_fixture" in item:
        source_id = str(item.get("source_id") or "").strip()
        title = str(item.get("title") or "").strip()
        url = str(item.get("url_or_fixture") or "").strip()
        license_text = str(item.get("license") or "").strip() or "unknown"
        cols = list(item.get("suggested_cols") or [])
    else:
        return None
    if not source_id.startswith("dataverse:") or not title or not url:
        return None
    if _looks_like_fixture(source_id, url):
        return None
    return _candidate(
        design,
        source_id=source_id,
        title=title,
        url_or_fixture=url,
        license=license_text,
        suggested_cols=cols,
        source_kind="discovered",
        notes="Dataverse search hit; not a fixture",
        fetch={
            "status": "link_only",
            "session_path": None,
            "reason": "download not yet attempted",
        },
    )


def _ensure_chosen_hit(
    design: Mapping[str, Any],
    hits: list[dict[str, Any]],
    source_id: str | None,
) -> list[dict[str, Any]]:
    if not source_id:
        return hits
    if any(h["source_id"] == source_id for h in hits):
        return hits
    pid = persistent_id_from_source_id(source_id)
    if pid is None:
        return hits
    extra = _candidate(
        design,
        source_id=f"dataverse:{pid}",
        title=f"Dataverse dataset {pid}",
        url_or_fixture=_url_for_persistent_id(pid),
        license="unknown",
        suggested_cols=[],
        source_kind="discovered",
        notes="Dataverse dataset; not a fixture",
        fetch={
            "status": "link_only",
            "session_path": None,
            "reason": "download not yet attempted",
        },
    )
    return [extra, *hits]


def _try_fetch_one(
    hit: dict[str, Any],
    workspace: Path,
    list_fn: ListFilesFn,
    download_fn: DownloadFn,
    *,
    preferred_file_id: str | None,
) -> str | None:
    pid = persistent_id_from_source_id(str(hit.get("source_id") or ""))
    if pid is None:
        hit["fetch"] = {
            "status": "link_only",
            "session_path": None,
            "reason": "no public file API; download then upload",
        }
        return None
    try:
        files = list(list_fn(pid) or [])
    except Exception:
        hit["fetch"] = {
            "status": "link_only",
            "session_path": None,
            "reason": "file list failed; download then upload",
        }
        return None
    chosen = _choose_public_file(files, preferred_file_id)
    if chosen is None:
        hit["fetch"] = {
            "status": "link_only",
            "session_path": None,
            "reason": _no_file_reason(files),
        }
        return None
    file_id = str(chosen.get("id") or "").strip()
    filename = _safe_filename(str(chosen.get("filename") or file_id or "dataverse-file"))
    try:
        body, content_type, header_name = download_fn(file_id)
    except Exception:
        hit["fetch"] = {
            "status": "link_only",
            "session_path": None,
            "reason": "download failed; download then upload",
        }
        return None
    if header_name:
        filename = _safe_filename(header_name) or filename
    if not body:
        hit["fetch"] = {
            "status": "link_only",
            "session_path": None,
            "reason": "download failed; download then upload",
        }
        return None
    if _looks_like_html(body, content_type):
        hit["fetch"] = {
            "status": "link_only",
            "session_path": None,
            "reason": "landing HTML is not a table; download then upload",
        }
        return None
    rel = f"{SESSION_FETCH_DIR}/{filename}"
    dest = workspace / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    hit["source_kind"] = "fetched"
    hit["fetch"] = {
        "status": "into_session",
        "session_path": rel,
        "reason": "dataverse public file",
    }
    notes = dict(hit.get("design_fit") or {})
    notes["notes"] = "Dataverse public file written to this session; not attached"
    hit["design_fit"] = notes


def _choose_public_file(
    files: Sequence[Mapping[str, Any]],
    preferred_file_id: str | None,
) -> dict[str, Any] | None:
    public = [dict(f) for f in files if isinstance(f, Mapping) and not f.get("restricted")]
    if preferred_file_id:
        for item in public:
            if str(item.get("id") or "") == preferred_file_id:
                return item
    tabular = [f for f in public if _is_tabular(f)]
    if tabular:
        return tabular[0]
    return public[0] if public else None


def _no_file_reason(files: Sequence[Mapping[str, Any]]) -> str:
    if not files:
        return "no public file API; download then upload"
    if all(isinstance(f, Mapping) and f.get("restricted") for f in files):
        return "restricted; no anonymous file API"
    return "no public file API; download then upload"


def _is_tabular(item: Mapping[str, Any]) -> bool:
    name = str(item.get("filename") or "").lower()
    ext = Path(name).suffix
    if ext in _TABULAR_EXT:
        return True
    ctype = str(item.get("contentType") or "").lower()
    return any(token in ctype for token in ("csv", "tab-separated", "stata", "excel", "x-rlang"))


def _looks_like_html(body: bytes, content_type: str) -> bool:
    ctype = (content_type or "").lower()
    if "text/html" in ctype or "application/xhtml" in ctype:
        return True
    head = body[:256].lstrip().lower()
    return any(head.startswith(marker) for marker in _HTML_MARKERS)


def _looks_like_fixture(source_id: str, url: str) -> bool:
    blob = f"{source_id} {url}".replace("\\", "/")
    if "fixtures/classic-5" in blob or "fixtures/cfps_association" in blob:
        return True
    return source_id.startswith(_FIXTURE_PREFIXES) or url.startswith("fixtures/")


def _is_honest_dataverse_candidate(item: Mapping[str, Any]) -> bool:
    if not is_real_candidate(item):
        return False
    source_id = str(item.get("source_id") or "")
    url = str(item.get("url_or_fixture") or "")
    kind = str(item.get("source_kind") or "")
    if _looks_like_fixture(source_id, url):
        return False
    if not source_id.startswith("dataverse:"):
        return False
    return kind in {"discovered", "fetched", "external_link"}


def _merge_dataverse_candidates(
    existing: Sequence[Any],
    dataverse_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for item in existing:
        if not isinstance(item, Mapping):
            continue
        sid = str(item.get("source_id") or "")
        if sid.startswith("dataverse:"):
            continue
        kept.append(dict(item))
    return [dict(row) for row in dataverse_rows] + kept


def _search_landing(design: Mapping[str, Any], query: str) -> dict[str, Any]:
    if query:
        url = DATAVERSE_SEARCH_PAGE + "?" + urllib.parse.urlencode({"q": query})
    else:
        url = DATAVERSE_HOME
    return _candidate(
        design,
        source_id="dataverse:search",
        title="Harvard Dataverse catalog search",
        url_or_fixture=url,
        license="unknown",
        suggested_cols=[],
        source_kind="external_link",
        notes="search miss; Dataverse path still shown; not a fixture find",
        fetch={
            "status": "link_only",
            "session_path": None,
            "reason": "search miss; followable Dataverse URL; upload your file",
        },
    )


def _candidate(
    design: Mapping[str, Any],
    *,
    source_id: str,
    title: str,
    url_or_fixture: str,
    license: str,
    suggested_cols: Sequence[str],
    source_kind: str,
    notes: str,
    fetch: Mapping[str, Any],
) -> dict[str, Any]:
    method = str(design.get("method") or "").strip().lower()
    return {
        "source_id": source_id,
        "title": title,
        "url_or_fixture": url_or_fixture,
        "license": license,
        "suggested_cols": list(suggested_cols),
        "design_fit": {
            "method": method,
            "outcome": str(design.get("outcome") or "").strip(),
            "treatment": str(design.get("treatment") or "").strip(),
            "notes": notes,
        },
        "source_kind": source_kind,
        "fetch": dict(fetch),
    }


def _url_for_persistent_id(pid: str) -> str:
    if pid.lower().startswith("doi:"):
        return "https://doi.org/" + pid.split(":", 1)[1]
    return (
        "https://dataverse.harvard.edu/dataset.xhtml?"
        + urllib.parse.urlencode({"persistentId": pid})
    )


def _safe_filename(name: str) -> str:
    base = Path(str(name or "")).name.strip()
    if not base or base in {".", ".."}:
        return "dataverse-file"
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", base)
    return cleaned or "dataverse-file"


def _map_file_item(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, Mapping):
        return None
    data_file = item.get("dataFile") if isinstance(item.get("dataFile"), Mapping) else item
    if not isinstance(data_file, Mapping):
        return None
    file_id = data_file.get("id")
    if file_id is None:
        file_id = data_file.get("dataFileId")
    filename = str(
        data_file.get("filename") or item.get("label") or data_file.get("label") or ""
    ).strip()
    if file_id is None or not filename:
        return None
    restricted = bool(item.get("restricted") or data_file.get("restricted"))
    return {
        "id": str(file_id),
        "filename": filename,
        "contentType": str(data_file.get("contentType") or item.get("contentType") or ""),
        "restricted": restricted,
    }


def _get_json(url: str) -> dict[str, Any] | None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": dataverse_user_agent(), "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
        ValueError,
        UnicodeError,
    ):
        return None
    return payload if isinstance(payload, dict) else None


def _get_bytes(
    url: str,
    *,
    timeout: float,
) -> tuple[int, bytes, str, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": dataverse_user_agent(), "Accept": "*/*"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = str(resp.headers.get("Content-Type") or "")
            filename = _filename_from_disposition(str(resp.headers.get("Content-Disposition") or ""))
            return int(getattr(resp, "status", 200) or 200), resp.read(), content_type, filename
    except urllib.error.HTTPError as exc:
        body = b""
        try:
            body = exc.read()
        except Exception:
            body = b""
        headers = exc.headers or {}
        return (
            int(exc.code or 0),
            body,
            str(headers.get("Content-Type") or ""),
            _filename_from_disposition(str(headers.get("Content-Disposition") or "")),
        )
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, b"", "", ""


def _filename_from_disposition(header: str) -> str:
    if not header:
        return ""
    match = re.search(r"filename\*?=(?:UTF-8''|\")?([^\";]+)", header, re.I)
    if not match:
        return ""
    return urllib.parse.unquote(match.group(1).strip().strip('"'))


__all__ = [
    "DesignUnconfirmed",
    "SESSION_FETCH_DIR",
    "apply_dataverse_fetch",
    "dataverse_user_agent",
    "download_datafile",
    "list_dataset_files",
    "persistent_id_from_source_id",
    "search_and_fetch_dataverse",
]

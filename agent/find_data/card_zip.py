"""FD-BE-fetch-card: resolve author-posted Card–Krueger zip into the session.

After a confirmed R-sources ``minwage`` design, try to download the posted
NJ–PA archive into session workspace staging. If the file is not
retrievable, keep the landing URL and an honest-upload reason.

Does not attach, does not set ``dataAttached`` / ``allow_did``, does not
use ``/demos/card``, and does not copy classic-5 / toy CSV bytes as the zip.
"""

from __future__ import annotations

import io
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Callable, Mapping

from agent.find_data.plan import (
    DesignUnconfirmed,
    classify_route_family,
    is_confirmed_design,
)

CARD_ZIP_SOURCE_ID = "card-zip:njmin"
CARD_ZIP_LANDING_URL = "https://davidcard.berkeley.edu/data_sets.html"
CARD_ZIP_POSTED_URL = "https://davidcard.berkeley.edu/data_sets/njmin.zip"
CARD_ZIP_TITLE = "Card–Krueger NJ–PA fast-food data (author zip)"
SESSION_RELATIVE_PATH = "fetch/card-zip/njmin.zip"

UA = "econpaper/1.0 (find-data; mailto:dev@local)"
HTTP_TIMEOUT_SECONDS = 15
MAX_ZIP_BYTES = 20 * 1024 * 1024

_HREF = re.compile(r"""href\s*=\s*["']\s*([^"'#]+)\s*["']""", re.I)
_NJMIN = re.compile(r"njmin", re.I)

HONEST_UPLOAD_REASON = (
    "posted archive not retrievable; Card zip link + honest upload "
    "(follow the author page, then upload). Product did not ingest a live "
    "file. Fixture is not the fetch."
)

ReadUrl = Callable[[str], bytes]


class CardZipNotApplicable(ValueError):
    """Card zip fetch only runs on confirmed R-sources minwage designs."""

    def __init__(self, reason: str = "not_minwage") -> None:
        super().__init__(reason)
        self.reason = reason


def read_url_bytes(url: str) -> bytes:
    """GET *url*. Network / HTTP errors propagate to the caller."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "*/*"},
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
        payload = resp.read(MAX_ZIP_BYTES + 1)
    if len(payload) > MAX_ZIP_BYTES:
        raise OSError("card zip exceeds size limit")
    return payload


def is_posted_zip(payload: bytes) -> bool:
    """True iff *payload* is a zip archive, not HTML/CSV/fixture text."""
    if not payload or payload.lstrip()[:1] in {b"<", b"{"}:
        return False
    head = payload.lstrip().split(b"\n", 1)[0]
    if b"," in head and not payload.startswith(b"PK"):
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            if archive.testzip() is not None:
                return False
            return True
    except (zipfile.BadZipFile, OSError, ValueError):
        return False


def zip_urls_from_html(html: str, base_url: str) -> list[str]:
    """NJ–PA zip hrefs only. Card 1995 proximity.zip is not the Card zip."""
    ordered: list[str] = []
    for match in _HREF.finditer(html or ""):
        href = _abs_url(base_url, match.group(1))
        if not href.lower().endswith(".zip"):
            continue
        if not _NJMIN.search(href):
            continue
        if href not in ordered:
            ordered.append(href)
    return ordered


def fetch_card_zip(
    design: Mapping[str, Any] | None,
    workspace: Path | str,
    *,
    read_url: ReadUrl | None = None,
) -> dict[str, Any]:
    """Download the author zip into *workspace* or return link + honest upload.

    Raises ``DesignUnconfirmed`` when design is missing/draft.
    Raises ``CardZipNotApplicable`` when the confirmed design is not minwage.
    """
    if not is_confirmed_design(design):
        raise DesignUnconfirmed("design_unconfirmed")
    assert design is not None
    if classify_route_family(design) != "minwage":
        raise CardZipNotApplicable("not_minwage")

    reader = read_url if read_url is not None else read_url_bytes
    payload, resolved, reason = _retrieve_zip(reader)
    if payload is None:
        return _candidate(
            design,
            source_kind="external_link",
            fetch_status="link_only",
            session_path=None,
            reason=reason or HONEST_UPLOAD_REASON,
        )

    try:
        session_path = _write_session_zip(Path(workspace), payload)
    except OSError as exc:
        return _candidate(
            design,
            source_kind="external_link",
            fetch_status="link_only",
            session_path=None,
            reason=f"session write failed: {exc}; {HONEST_UPLOAD_REASON}",
        )

    return _candidate(
        design,
        source_kind="fetched",
        fetch_status="into_session",
        session_path=session_path,
        reason=f"downloaded {resolved}",
    )


def merge_card_zip_candidate(
    record: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    """Put the Card zip row first. Do not invent fixture candidates."""
    merged = dict(record)
    others = [
        item
        for item in (merged.get("candidates") or [])
        if isinstance(item, Mapping) and item.get("source_id") != CARD_ZIP_SOURCE_ID
    ]
    merged["candidates"] = [dict(candidate), *others]
    return merged


def _retrieve_zip(reader: ReadUrl) -> tuple[bytes | None, str, str]:
    reasons: list[str] = []
    urls: list[str] = []

    html_bytes, _, landing_err = _try_url(
        reader, CARD_ZIP_LANDING_URL, require_zip=False
    )
    if html_bytes is not None:
        html = html_bytes.decode("utf-8", errors="replace")
        urls.extend(zip_urls_from_html(html, CARD_ZIP_LANDING_URL))
    elif landing_err:
        reasons.append(landing_err)

    if CARD_ZIP_POSTED_URL not in urls:
        urls.append(CARD_ZIP_POSTED_URL)

    for href in urls:
        payload, resolved, err = _try_url(reader, href)
        if payload is not None:
            return payload, resolved, ""
        if err:
            reasons.append(err)

    return None, CARD_ZIP_LANDING_URL, _join_reasons(reasons)


def _try_url(
    reader: ReadUrl,
    url: str,
    *,
    require_zip: bool = True,
) -> tuple[bytes | None, str, str]:
    try:
        payload = reader(url)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return None, url, f"{url}: {exc}"
    if payload is None:
        return None, url, f"{url}: empty"
    if require_zip and not is_posted_zip(payload):
        return None, url, f"{url}: not a zip archive"
    return payload, url, ""


def _write_session_zip(workspace: Path, payload: bytes) -> str:
    root = workspace.resolve()
    dest = (root / SESSION_RELATIVE_PATH).resolve()
    if not _is_relative_to(dest, root):
        raise OSError("session path escapes workspace")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(payload)
    return SESSION_RELATIVE_PATH


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _abs_url(base: str, href: str) -> str:
    return urllib.parse.urljoin(base, href.strip())


def _join_reasons(reasons: list[str]) -> str:
    detail = "; ".join(reasons) if reasons else "no posted zip"
    return f"{detail}; {HONEST_UPLOAD_REASON}"


def _method(design: Mapping[str, Any]) -> str:
    return str(design.get("method") or "").strip().lower()


def _candidate(
    design: Mapping[str, Any],
    *,
    source_kind: str,
    fetch_status: str,
    session_path: str | None,
    reason: str,
) -> dict[str, Any]:
    return {
        "source_id": CARD_ZIP_SOURCE_ID,
        "title": CARD_ZIP_TITLE,
        "url_or_fixture": CARD_ZIP_LANDING_URL,
        "license": "author-posted",
        "suggested_cols": [],
        "design_fit": {
            "method": _method(design),
            "outcome": str(design.get("outcome") or "").strip(),
            "treatment": str(design.get("treatment") or "").strip(),
            "notes": reason,
        },
        "source_kind": source_kind,
        "fetch": {
            "status": fetch_status,
            "session_path": session_path,
            "reason": reason,
        },
    }


__all__ = [
    "CARD_ZIP_LANDING_URL",
    "CARD_ZIP_POSTED_URL",
    "CARD_ZIP_SOURCE_ID",
    "HONEST_UPLOAD_REASON",
    "SESSION_RELATIVE_PATH",
    "CardZipNotApplicable",
    "fetch_card_zip",
    "is_posted_zip",
    "merge_card_zip_candidate",
    "read_url_bytes",
    "zip_urls_from_html",
]

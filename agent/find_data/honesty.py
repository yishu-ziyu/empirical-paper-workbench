"""FD-BE-honesty: source_kind, teaching shelf, toy ban, fail-closed copy.

Fixtures and teaching toys are never discovered/found data. DATA-RIGOR
may also quarantine the same toys; this module treats that flag as skip.
Does not download files, attach, or set dataAttached / allow_did.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, MutableMapping

SOURCE_KINDS = (
    "discovered",
    "teaching_fixture",
    "external_link",
    "fetched",
    "captain_local_real",
    "user_upload",
)
FIND_SUCCESS_KINDS = frozenset({"discovered", "fetched", "external_link"})
CAPTAIN_LOCAL_REAL_SOURCE = "captain-local-real"
N_DEMO_CLAIM_MIN = 200
TEACHING_SHELF_LABEL = (
    "教学已知样本 / teaching-known extract — not a find result"
)
HONESTY_LABELS = {
    "discovered": "检索到 / Dataverse 命中",
    "fetched": "已下载到本会话",
    "teaching_fixture": TEACHING_SHELF_LABEL,
    "external_link": "公开链接；请下载后上传",
    "user_upload": "上传你自己的文件",
    "captain_local_real": (
        "船长本地真实面板 / captain-local-real — not a find result"
    ),
}
FETCH_STATUS = {
    "discovered": "link_only",
    "fetched": "into_session",
    "teaching_fixture": "not_applicable",
    "external_link": "link_only",
    "user_upload": "into_session",
    "captain_local_real": "into_session",
}
FETCH_REASON = {
    "discovered": "download not yet attempted",
    "fetched": "bytes written into session",
    "teaching_fixture": "in-repo teaching extract",
    "external_link": "link + honest upload; not ingested",
    "user_upload": "user upload",
    "captain_local_real": "captain-local-real upload",
}

DECIDE7_FIELDS = (
    "source_id",
    "title",
    "url_or_fixture",
    "license",
    "suggested_cols",
    "design_fit",
)

BANNED_TOY_NAMES = frozenset(
    {
        "minimum_wage.csv",
        "course-panel.csv",
        "sanitized_sample.csv",
    }
)
BANNED_TOY_PATH_MARKERS = (
    "agent/spike/fixtures",
    "frontend/public/samples",
    "fixtures/cfps_association",
)
CLASSIC5_ID_TOKENS = frozenset(
    {
        "ck1994",
        "ck1994_long",
        "minimum-wage-employment",
        "barro1991_growth",
        "schooling-wages",
        "wage1",
    }
)

_FOUND_COPY = re.compile(
    r"找到了|为你找到|检索结果|"
    r"\bwe found\b|\bfound data\b|\bdiscovered dataset\b|"
    r"\bmatched your\b|\brecommended data\b|\bclassic_found\b",
    re.I,
)
_TEACHING_AS_PRIMARY = re.compile(
    r"教学样本|teaching sample",
    re.I,
)


def honesty_label(source_kind: str) -> str:
    return HONESTY_LABELS.get(str(source_kind or "").strip(), "")


def default_fetch(source_kind: str, *, session_path: str | None = None) -> dict[str, Any]:
    kind = str(source_kind or "").strip()
    status = FETCH_STATUS.get(kind)
    if not status:
        return {
            "status": "not_applicable",
            "session_path": None,
            "reason": "unknown source_kind",
        }
    path = session_path if status == "into_session" else None
    return {
        "status": status,
        "session_path": path,
        "reason": FETCH_REASON.get(kind, ""),
    }


def demo_claim_allowed(n: int | None) -> bool:
    """Attach/estimate demo claims fail closed when n is missing or n < 200."""
    if n is None:
        return False
    try:
        count = int(n)
    except (TypeError, ValueError):
        return False
    return count >= N_DEMO_CLAIM_MIN


def demo_claim_warning(n: int | None) -> str:
    if demo_claim_allowed(n):
        return ""
    return (
        "this file is too small to stand in for a real panel; "
        "it is not a demo success"
    )


def _norm_path(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/")
    return text


def _basename(value: Any) -> str:
    text = _norm_path(value)
    if not text:
        return ""
    return PurePosixPath(text.rstrip("/")).name.lower()


def is_quarantined(obj: Any) -> bool:
    """DATA-RIGOR may stamp quarantine; missing stamp still checks toy paths."""
    if isinstance(obj, Mapping):
        if obj.get("quarantined") is True:
            return True
        rigor = obj.get("data_rigor")
        if isinstance(rigor, Mapping) and rigor.get("quarantined") is True:
            return True
        if str(obj.get("data_rigor") or "").strip().lower() == "quarantined":
            return True
        path = obj.get("url_or_fixture") or obj.get("path") or obj.get("source_id")
        return is_banned_toy(path)
    return is_banned_toy(obj)


def is_banned_toy(value: Any) -> bool:
    """Teaching toys never found / shelf / captain-local-real."""
    text = _norm_path(value).lower()
    if not text:
        return False
    name = _basename(text)
    if name in BANNED_TOY_NAMES:
        return True
    return any(marker in text for marker in BANNED_TOY_PATH_MARKERS)


def is_fixture_ref(obj: Mapping[str, Any] | None) -> bool:
    if not isinstance(obj, Mapping):
        return False
    source_id = str(obj.get("source_id") or "").strip()
    url = _norm_path(obj.get("url_or_fixture"))
    sid_l = source_id.lower()
    if sid_l.startswith("classic-5:") or sid_l in CLASSIC5_ID_TOKENS:
        return True
    if url.startswith("fixtures/") or "/fixtures/" in url:
        return True
    if _basename(url) in {f"{token}.csv" for token in CLASSIC5_ID_TOKENS}:
        return True
    if url in CLASSIC5_ID_TOKENS or source_id in CLASSIC5_ID_TOKENS:
        return True
    return False


def copy_is_forbidden(source_kind: str, text: Any) -> bool:
    blob = str(text or "")
    kind = str(source_kind or "").strip()
    if kind in {"teaching_fixture", "captain_local_real", "user_upload"}:
        return bool(_FOUND_COPY.search(blob))
    if kind in FIND_SUCCESS_KINDS:
        return bool(_TEACHING_AS_PRIMARY.search(blob))
    return False


def is_real_candidate(obj: Any) -> bool:
    """DECIDE-7 shape plus required source_kind. Missing kind fails closed."""
    if not isinstance(obj, Mapping):
        return False
    for key in DECIDE7_FIELDS:
        if key not in obj:
            return False
    source_kind = str(obj.get("source_kind") or "").strip()
    if source_kind not in SOURCE_KINDS:
        return False
    source_id = str(obj.get("source_id") or "").strip()
    title = str(obj.get("title") or "").strip()
    url = str(obj.get("url_or_fixture") or "").strip()
    license_text = str(obj.get("license") or "").strip()
    if not source_id or not title or not url or not license_text:
        return False
    if url == source_id or url in CLASSIC5_ID_TOKENS:
        return False
    cols = obj.get("suggested_cols")
    fit = obj.get("design_fit")
    if not isinstance(cols, list) or not isinstance(fit, Mapping):
        return False
    return True


def is_find_success_candidate(obj: Any) -> bool:
    if not is_real_candidate(obj):
        return False
    kind = str(obj.get("source_kind") or "").strip()
    if kind not in FIND_SUCCESS_KINDS:
        return False
    if is_quarantined(obj) or is_fixture_ref(obj) or is_banned_toy(obj.get("url_or_fixture")):
        return False
    return True


def honest_candidate(obj: Any) -> dict[str, Any] | None:
    """Return a labeled candidate or None (fail closed)."""
    if not isinstance(obj, Mapping):
        return None
    if is_quarantined(obj):
        return None
    kind = str(obj.get("source_kind") or "").strip()
    if kind not in SOURCE_KINDS:
        return None
    item = dict(obj)
    url = item.get("url_or_fixture")
    if is_banned_toy(url) or is_banned_toy(item.get("source_id")):
        return None
    if kind in FIND_SUCCESS_KINDS and is_fixture_ref(item):
        return None
    if kind == "teaching_fixture" and is_banned_toy(url):
        return None
    if kind == "captain_local_real":
        if is_banned_toy(url) or is_fixture_ref(item):
            return None
        item["source"] = CAPTAIN_LOCAL_REAL_SOURCE
    if kind == "teaching_fixture":
        item["fetch"] = default_fetch("teaching_fixture")
    elif not isinstance(item.get("fetch"), Mapping):
        item["fetch"] = default_fetch(kind)
    notes = ""
    fit = item.get("design_fit")
    if isinstance(fit, MutableMapping):
        notes = str(fit.get("notes") or "")
        if copy_is_forbidden(kind, notes):
            fit = dict(fit)
            fit["notes"] = honesty_label(kind)
            item["design_fit"] = fit
            notes = fit["notes"]
    label = str(item.get("honesty_label") or "").strip() or honesty_label(kind)
    if copy_is_forbidden(kind, label):
        label = honesty_label(kind)
    item["honesty_label"] = label
    if copy_is_forbidden(kind, notes):
        return None
    if not is_real_candidate(item):
        return None
    return item


def teaching_shelf_payload(candidates: Iterable[Mapping[str, Any]]) -> dict[str, Any] | None:
    labeled: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in candidates:
        item = dict(raw)
        item["source_kind"] = "teaching_fixture"
        honest = honest_candidate(item)
        if honest is None:
            continue
        sid = str(honest["source_id"])
        if sid in seen:
            continue
        seen.add(sid)
        labeled.append(honest)
    if not labeled:
        return None
    return {"label": TEACHING_SHELF_LABEL, "candidates": labeled}


def project_honest_find_data(record: Mapping[str, Any] | None) -> dict[str, Any]:
    """Split shelf vs find list. Drop unlabeled / toy / fixture-as-found rows."""
    if not isinstance(record, Mapping):
        return {
            "status": "missing",
            "planned_at": None,
            "route_family": None,
            "primary_venue": None,
            "plan": None,
            "candidates": [],
            "teaching_shelf": None,
        }
    out = dict(record)
    find_rows: list[dict[str, Any]] = []
    shelf_rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _take(raw: Any, *, force_kind: str | None = None) -> None:
        if not isinstance(raw, Mapping):
            return
        item = dict(raw)
        if force_kind:
            item["source_kind"] = force_kind
        if is_banned_toy(item.get("url_or_fixture")) or is_quarantined(item):
            return
        if is_fixture_ref(item):
            item["source_kind"] = "teaching_fixture"
        honest = honest_candidate(item)
        if honest is None:
            return
        sid = str(honest["source_id"])
        if sid in seen:
            return
        seen.add(sid)
        kind = str(honest["source_kind"])
        if kind == "teaching_fixture":
            shelf_rows.append(honest)
        else:
            find_rows.append(honest)

    for raw in record.get("candidates") or []:
        _take(raw)
    stored_shelf = record.get("teaching_shelf")
    shelf_items: Iterable[Any] = ()
    if isinstance(stored_shelf, Mapping):
        shelf_items = stored_shelf.get("candidates") or []
    elif isinstance(stored_shelf, list):
        shelf_items = stored_shelf
    for raw in shelf_items:
        _take(raw, force_kind="teaching_fixture")

    out["candidates"] = find_rows
    out["teaching_shelf"] = teaching_shelf_payload(shelf_rows)
    return out


def captain_local_real_candidate(
    *,
    path: str,
    design: Mapping[str, Any],
    title: str = "Captain-local real panel",
    license: str = "user-provided",
    suggested_cols: Iterable[str] = (),
    session_path: str | None = None,
    row_count: int | None = None,
) -> dict[str, Any] | None:
    """Label a captain-local-real acquire. Toys / fixtures → None."""
    if is_banned_toy(path) or is_banned_toy(title):
        return None
    warning = demo_claim_warning(row_count)
    notes = "captain-local-real acquire; not a find result; not a toy"
    if warning:
        notes = f"{notes}; {warning}"
    item = {
        "source_id": "captain-local-real:upload",
        "source_kind": "captain_local_real",
        "source": CAPTAIN_LOCAL_REAL_SOURCE,
        "title": title,
        "url_or_fixture": path,
        "license": license,
        "suggested_cols": [str(c).strip() for c in suggested_cols if str(c).strip()],
        "design_fit": {
            "method": str(design.get("method") or "").strip(),
            "outcome": str(design.get("outcome") or "").strip(),
            "treatment": str(design.get("treatment") or "").strip(),
            "notes": notes,
        },
        "honesty_label": honesty_label("captain_local_real"),
        "fetch": default_fetch("captain_local_real", session_path=session_path),
    }
    return honest_candidate(item)


__all__ = [
    "CAPTAIN_LOCAL_REAL_SOURCE",
    "FIND_SUCCESS_KINDS",
    "HONESTY_LABELS",
    "N_DEMO_CLAIM_MIN",
    "SOURCE_KINDS",
    "TEACHING_SHELF_LABEL",
    "captain_local_real_candidate",
    "copy_is_forbidden",
    "default_fetch",
    "demo_claim_allowed",
    "demo_claim_warning",
    "honest_candidate",
    "honesty_label",
    "is_banned_toy",
    "is_find_success_candidate",
    "is_fixture_ref",
    "is_quarantined",
    "is_real_candidate",
    "project_honest_find_data",
    "teaching_shelf_payload",
]

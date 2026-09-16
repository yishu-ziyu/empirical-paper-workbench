"""Honesty gates for found-data vs teaching toys (FM-E-DATA-RIGOR-1).

Product suggest/find paths must not present teaching toys as found data.
Captain-local real panel upload is first-class acquire (`source=captain-local-real`).
Attach/estimate may still run on a small real upload, but n < 200 cannot
be claimed as a demo or found-data success.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

DEMO_MIN_ROWS = 200
CAPTAIN_LOCAL_REAL = "captain-local-real"

TOY_FILENAMES = frozenset(
    {
        "course-panel.csv",
        "minimum_wage.csv",
        "sanitized_sample.csv",
        "sample_wage.csv",
        "sample_panel_mini.csv",
        "wage_panel.csv",
        "wage1.csv",
        "wage1.dta",
    }
)

HONESTY_TOO_SMALL = (
    "n={n} is below {min_rows}; too small to claim demo or found-data success"
)
HONESTY_TEACHING = "teaching fixture cannot be claimed as found data"


def filename_of(name: str | Path | None) -> str:
    if name is None:
        return ""
    return Path(str(name)).name.strip().lower()


def is_toy_filename(name: str | Path | None) -> bool:
    return filename_of(name) in TOY_FILENAMES


def acquire_source_for_upload(name: str | Path | None) -> str | None:
    """POST /upload of a non-toy file is first-class captain-local-real acquire.

    Interim OK for real Desktop/经济学论文 CSV / Stata .dta. Teaching toys
    never receive this source. n<200 still cannot claim demo/found success.
    """
    if not filename_of(name) or is_toy_filename(name):
        return None
    return CAPTAIN_LOCAL_REAL


def count_csv_data_rows(path: Path | str) -> int | None:
    """Count data rows in a CSV (header excluded). Missing/unreadable → None."""
    file = Path(path)
    if not file.is_file():
        return None
    try:
        text = file.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return 0
    return max(0, len(lines) - 1)


def is_found_scale(n: int | None) -> bool:
    return isinstance(n, int) and n >= DEMO_MIN_ROWS


def honesty_for_n(
    n: int | None,
    *,
    name: str | Path | None = None,
) -> dict[str, Any]:
    """Return demo_success / honesty_warning for attach-estimate claims."""
    toy = is_toy_filename(name)
    too_small = not is_found_scale(n)
    if toy:
        warning = HONESTY_TEACHING
        if too_small and isinstance(n, int):
            warning = HONESTY_TOO_SMALL.format(n=n, min_rows=DEMO_MIN_ROWS)
        return {
            "demo_success": False,
            "honesty_warning": warning,
            "found": False,
            "teaching_fixture": True,
        }
    if too_small:
        shown = 0 if n is None else n
        return {
            "demo_success": False,
            "honesty_warning": HONESTY_TOO_SMALL.format(
                n=shown, min_rows=DEMO_MIN_ROWS
            ),
            "found": False,
            "teaching_fixture": False,
        }
    return {
        "demo_success": True,
        "honesty_warning": None,
        "found": True,
        "teaching_fixture": False,
    }


def stamp_mapping(payload: Mapping[str, Any], honesty: Mapping[str, Any]) -> dict[str, Any]:
    """Copy honesty fields onto a dict payload."""
    out = dict(payload)
    out["demo_success"] = bool(honesty.get("demo_success"))
    warning = honesty.get("honesty_warning")
    if warning:
        out["honesty_warning"] = warning
    else:
        out.pop("honesty_warning", None)
    return out


__all__ = [
    "CAPTAIN_LOCAL_REAL",
    "DEMO_MIN_ROWS",
    "HONESTY_TEACHING",
    "HONESTY_TOO_SMALL",
    "TOY_FILENAMES",
    "acquire_source_for_upload",
    "count_csv_data_rows",
    "filename_of",
    "honesty_for_n",
    "is_found_scale",
    "is_toy_filename",
    "stamp_mapping",
]

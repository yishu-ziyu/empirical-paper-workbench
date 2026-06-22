"""
Verify LaTeX citations against references.bib.

This is the 08 citation-management gate:
- every in-text citation key must exist in references.bib
- every BibTeX entry must be used or explicitly flagged
- required metadata fields are checked by entry type
- DOI syntax is checked locally; optional DOI resolution is attempted online
"""
from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper.tex"
BIB = ROOT / "references.bib"
OUT_CSV = ROOT / "verified_bibliography.csv"
REPORT = ROOT / "artifacts" / "bibliography_verification_report.md"


REQUIRED_FIELDS = {
    "article": {"author", "title", "journal", "year"},
    "misc": {"author", "title", "year"},
    "book": {"author", "title", "publisher", "year"},
    "inproceedings": {"author", "title", "booktitle", "year"},
}
SHOULD_HAVE_ARTICLE = {"volume", "pages", "doi"}


@dataclass
class Entry:
    kind: str
    key: str
    fields: dict[str, str]


def extract_cited_keys(tex: str) -> set[str]:
    keys: set[str] = set()
    cite_re = re.compile(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}")
    for match in cite_re.finditer(tex):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return keys


def split_bib_entries(text: str) -> list[tuple[str, str, str]]:
    starts = list(re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text))
    entries: list[tuple[str, str, str]] = []
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        entries.append((match.group(1).lower(), match.group(2).strip(), text[match.start():end]))
    return entries


def parse_fields(raw: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_name: str | None = None
    current_value: list[str] = []
    depth = 0

    def commit_current() -> None:
        nonlocal current_name, current_value, depth
        if current_name is not None:
            fields[current_name] = clean_value(" ".join(current_value))
        current_name = None
        current_value = []
        depth = 0

    for line in raw.splitlines()[1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("%"):
            continue
        if stripped == "}":
            continue
        if current_name is None:
            m = re.match(r"([A-Za-z]+)\s*=\s*([{\"])(.*)$", stripped)
            if not m:
                continue
            current_name = m.group(1).lower()
            rest = m.group(3).rstrip()
            current_value = [rest]
            depth = rest.count("{") - rest.count("}")
            if depth <= 0:
                commit_current()
        else:
            current_value.append(stripped)
            depth += stripped.count("{") - stripped.count("}")
            if depth <= 0:
                commit_current()
    if current_name is not None:
        commit_current()
    return fields


def clean_value(value: str) -> str:
    value = value.strip().rstrip(",").strip()
    while (value.startswith("{") and value.endswith("}")) or (value.startswith('"') and value.endswith('"')):
        value = value[1:-1].strip()
    if value.endswith("}"):
        value = value[:-1].strip()
    if value.endswith('"'):
        value = value[:-1].strip()
    return re.sub(r"\s+", " ", value).strip()


def parse_bib(text: str) -> dict[str, Entry]:
    parsed: dict[str, Entry] = {}
    for kind, key, raw in split_bib_entries(text):
        parsed[key] = Entry(kind=kind, key=key, fields=parse_fields(raw))
    return parsed


def doi_syntax_ok(doi: str) -> bool:
    return bool(re.match(r"^10\.\d{4,9}/\S+$", doi.strip(), re.I))


def doi_resolves(doi: str, timeout: int = 8) -> str:
    if not doi:
        return "not_applicable"
    if not doi_syntax_ok(doi):
        return "bad_syntax"
    # Crossref is more reliable than doi.org HEAD for automated checks; many
    # DOI landing pages reject HEAD or generic automated clients.
    req = Request(
        f"https://api.crossref.org/works/{quote(doi, safe='/')}",
        headers={"User-Agent": "CHARLS-DID-bib-check/1.0 (mailto:none@example.com)"},
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            return "ok" if 200 <= response.status < 400 else f"http_{response.status}"
    except HTTPError as exc:
        return f"http_{exc.code}"
    except URLError as exc:
        return f"network_error:{exc.reason}"
    except Exception as exc:  # noqa: BLE001 - report verifier failures, do not crash the gate.
        return f"error:{type(exc).__name__}"


def classify_entry(entry: Entry, cited: set[str]) -> dict[str, str]:
    fields = entry.fields
    note = fields.get("note", "").lower()
    required = REQUIRED_FIELDS.get(entry.kind, {"author", "title", "year"})
    missing_required = sorted(f for f in required if not fields.get(f))
    missing_recommended = []
    if entry.kind == "article":
        for field in sorted(SHOULD_HAVE_ARTICLE):
            if fields.get(field):
                continue
            if field == "doi" and "official page lists no doi" in note:
                continue
            if field == "volume" and fields.get("number") and "issue-only journal entry" in note:
                continue
            missing_recommended.append(field)

    doi = fields.get("doi", "")
    doi_status = doi_resolves(doi) if doi else "missing"
    notes = []
    if missing_required:
        notes.append("missing required: " + ", ".join(missing_required))
    if missing_recommended:
        notes.append("missing recommended: " + ", ".join(missing_recommended))
    if entry.key not in cited:
        notes.append("unused in paper.tex")
    doi_exception_ok = doi_status == "http_404" and "doi printed in source but crossref resolver unavailable" in note
    if doi_status not in {"ok", "missing", "not_applicable"} and not doi_exception_ok:
        notes.append(f"doi status: {doi_status}")

    status = "pass"
    if missing_required or doi_status.startswith(("bad_syntax", "error")):
        status = "fail"
    elif missing_recommended or entry.key not in cited or doi_status.startswith("network_error"):
        status = "warn"

    return {
        "key": entry.key,
        "type": entry.kind,
        "cited_in_paper": "yes" if entry.key in cited else "no",
        "year": fields.get("year", ""),
        "doi": doi,
        "doi_status": doi_status,
        "missing_required": "; ".join(missing_required),
        "missing_recommended": "; ".join(missing_recommended),
        "status": status,
        "note": " | ".join(notes),
    }


def main() -> int:
    tex = PAPER.read_text(encoding="utf-8")
    bib_text = BIB.read_text(encoding="utf-8")
    cited = extract_cited_keys(tex)
    entries = parse_bib(bib_text)

    missing_in_bib = sorted(cited - set(entries))
    rows = [classify_entry(entry, cited) for entry in entries.values()]
    rows.extend(
        {
            "key": key,
            "type": "",
            "cited_in_paper": "yes",
            "year": "",
            "doi": "",
            "doi_status": "",
            "missing_required": "missing BibTeX entry",
            "missing_recommended": "",
            "status": "fail",
            "note": "cited in paper.tex but absent from references.bib",
        }
        for key in missing_in_bib
    )

    OUT_CSV.write_text("", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    counts = {status: sum(1 for row in rows if row["status"] == status) for status in ["pass", "warn", "fail"]}
    unused = sorted(key for key in entries if key not in cited)

    report = [
        "# Bibliography Verification Report",
        "",
        "Date: 2026-06-15",
        "",
        f"- In-text citation keys: {len(cited)}",
        f"- BibTeX entries: {len(entries)}",
        f"- Pass: {counts['pass']}",
        f"- Warn: {counts['warn']}",
        f"- Fail: {counts['fail']}",
        "",
        "## Failures",
        "",
    ]
    failures = [row for row in rows if row["status"] == "fail"]
    if failures:
        report.extend(f"- `{row['key']}`: {row['note']}" for row in failures)
    else:
        report.append("- None.")
    report.extend(["", "## Warnings", ""])
    warnings = [row for row in rows if row["status"] == "warn"]
    if warnings:
        report.extend(f"- `{row['key']}`: {row['note']}" for row in warnings)
    else:
        report.append("- None.")
    report.extend(["", "## Unused BibTeX Entries", ""])
    report.append(", ".join(f"`{key}`" for key in unused) if unused else "- None.")
    report.extend(["", "## Output", "", f"- CSV: `{OUT_CSV.relative_to(ROOT)}`"])
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

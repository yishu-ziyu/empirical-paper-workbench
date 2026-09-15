# classic-5 catalog

Named built-in catalog for formal TITLE/TOPIC find/select
(`docs/data-completion-contract.md` §3).

## Ranking metadata (DC-BE-suggest)

DC-BE-suggest reads `catalog.json` and ranks entries from TITLE/TOPIC.
Suggest is read-only: it never attaches or sets `dataAttached`.

Override the catalog file with `ECONPAPER_CLASSIC5_CATALOG` or the
directory with `ECONPAPER_CLASSIC5_DIR`.

## Byte load / confirm-attach (DC-BE-attach)

Formal TITLE/TOPIC attach loads catalog bytes from this tree, or from
`ECONPAPER_CLASSIC5_ROOT` / `ECONPAPER_CLASSIC5_DIR` / `ECONPAPER_CLASSIC5_<ENTRY_ID>`.

Layout: `{entry_id}.csv` (also `.dta` / `.xlsx`). Entry ids are `[A-Za-z0-9._-]`.

Selecting or attaching a candidate leaves `dataAttached` false. Only
confirm-attach sets the snapshot gate, and only when ingest is READY
with a dataset.

Not Card (`POST /demos/card`), not CHARLS/CFPS, not course-panel, not
sketch sample names. Entries are catalog data, not the user's study.

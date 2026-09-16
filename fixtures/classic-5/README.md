# classic-5 catalog

Named built-in catalog for formal TITLE/TOPIC find/select.

**Found vs teaching:** product suggest/find only treats a fixture as
found data when the file exists and has n ≥ 200. Metadata-only stubs
and small extracts (including Barro 110-country) are `teaching_fixture`
and must not be presented as found.

## Ranking metadata (DC-BE-suggest)

DC-BE-suggest reads `catalog.json` and ranks entries from a confirmed
design. Suggest is read-only: it never attaches or sets `dataAttached`.
`candidates` are found-scale only. Matching stubs go on `teaching`.

Override the catalog file with `ECONPAPER_CLASSIC5_CATALOG` or the
directory with `ECONPAPER_CLASSIC5_DIR`.

## Vendored files (see `SOURCE.txt`)

- `ck1994_long.csv` — Card and Krueger (1994) NJ–PA min-wage panel (768 rows, found)
- `barro1991_growth.csv` — Barro (1991) / Barro–Lee 1960–85 growth cross-section (110 rows, teaching_fixture; honesty fail-closed for demo claims)

Not Card (`POST /demos/card`), not CHARLS/CFPS, not course-panel, not
sketch sample names. Entries are catalog data, not the user's study.
No private CGSS extracts.

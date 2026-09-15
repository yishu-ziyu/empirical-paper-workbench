# classic-5 catalog (reserved)

Formal TITLE/TOPIC attach loads catalog bytes from this tree, or from
`ECONPAPER_CLASSIC5_ROOT` / `ECONPAPER_CLASSIC5_DIR` / `ECONPAPER_CLASSIC5_<ENTRY_ID>`.

Layout: `{entry_id}.csv` (also `.dta` / `.xlsx`). Entry ids are `[A-Za-z0-9._-]`.

This is not Card (`POST /demos/card`). DC-BE-attach binds an entry; it does
not rank the catalog. Suggest ranking belongs to DC-BE-suggest.

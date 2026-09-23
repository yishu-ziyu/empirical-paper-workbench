# 6. Venue notes (later fetch slices)

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


Exact URLs and API query strings are **implementation** (later slices). G0 freezes **roles**.

| Slice / route | Must | Must not |
|---|---|---|
| **FD-BE-fetch-card** | After confirmed minwage (or equivalent R-sources `minwage`) design, resolve the author-posted Card–Krueger zip and **download into session** when the posted file is retrievable; else link + honest upload | Use `/demos/card`; copy classic-5 CSV as the zip; set `dataAttached`; call it a find of `ck1994` |
| **FD-BE-fetch-dataverse** | Search Dataverse from confirmed facets; **download** a chosen public file into session when the Dataverse API allows; else dataset URL + upload | Treat Dataverse landing HTML as a fetched table; substitute classic-5 on search miss |
| **FD-BE-fetch-wdi** | For `growth`, pull WDI (World Bank indicators API or equivalent public download) into session when allowed; else WDI page + upload | Treat `barro1991_growth` as the WDI fetch |
| **FRED / IPUMS** | Same prefer-download-else-link rule on existing R-sources families (`macro` / `educ_wage`) | Commit IPUMS extracts to git; scrape FRED behind a key if the product has no configured public path — then link + upload |

Dataverse remains the **always-on backup** when a named venue cannot fetch.

---

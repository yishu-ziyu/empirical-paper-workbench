# 1. Purpose and non-goals

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


## 1.1 Purpose (frozen)

Given a formal-path session whose **`session.design.status === "confirmed"`**, this flow only:

1. **Real fetch first** — Searches / fetches **external** sources for the confirmed design (FD + R-sources venues). Hits that come from a live catalog or public download are `source_kind = discovered` (or `external_link` when only a URL can be shown).
2. **Never fixture-as-found** — In-repo classic-5 / teaching extracts must **not** be labeled, ordered, or copied as discovered / found / matched-your-study data.
3. **Teaching-known only** — Those extracts may appear **only** as `source_kind = teaching_fixture`, on an **optional teaching shelf** with an **explicit** label. Their presence is **not** find success.
4. **Download into session when the API allows** — For Dataverse, Card zip, WDI, and FRED/IPUMS per existing R-sources routes: if a public API or posted file can be retrieved, write bytes into the **session workspace** (staging). That is **fetch**, not attach.
5. **Else honest path** — If download is not allowed, fails, or needs login / registration, show a followable **link** plus an **honest upload**. Do not pad with a fixture or a toy CSV.
6. **Captain-local-real (first-class acquire)** — Captain may upload **real** `.dta`/CSV panels from Desktop/经济学论文, labeled `source_kind=captain_local_real` / `source=captain-local-real`, while Research still scouts find→acquire→organize→clean. This is **not** discovered/found data and **not** a toy.
7. **DATA-RIGOR** — Keep synthetic / invented / toy samples off the product path (§3.4–§3.7). Tiny fixtures live only under `tests/`, labeled synthetic.

FIND-DATA still lists candidates; it never auto-selects, never confirm-attaches, never writes gold chapter bodies. Fetch-into-session does **not** set `dataAttached`.

## 1.2 Non-goals (frozen)

This contract does **not**:

- Propose or confirm `session.design` (INF-BE-propose / INF-BE-confirm)
- Own the FIND-DATA **where/how plan** (FD-BE-plan) or FIND-LIT / R-lit-bar
- Treat catalog → locked spec, catalog → `allow_did`, catalog → found dataset, or catalog → gold biblio as a win path
- Auto-succeed, auto-select, or prefill a fixture as the user’s study
- Attach a dataset or set `dataAttached` (download-into-session ≠ confirm-attach)
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, `generate_title` / `state.title_chapter`, or export docx
- Vendor restricted microdata (IPUMS extracts, CHARLS, …) into the git repo
- Scrape behind login, store user credentials, or treat a teaching shelf as a find
- Present teaching **toys** (`minimum_wage.csv`, `course-panel.csv`, CFPS `sanitized_sample.csv`, or other n≈4–24 invented CSVs) as found data, suggest hits, `captain_local_real`, or product demos
- Vendor Captain Desktop/经济学论文 files into git
- Ship Design FIND-1 / `econpaper-ui-temp/flow-sketch` as product chrome
- Merge DATA-COMPLETE / DID / INF / FIND-LIT / FIND-DATA implementation branches
- Implement application code, API routes, OpenAPI shapes, or frontend chrome (G0 is markdown only)

`TITLE/TOPIC` is already consumed by infer-design. Real-fetch reads the **confirmed** `session.design`, not the title as a substitute for confirm.

---

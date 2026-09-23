# 4. Fetch policy — download vs link + upload

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


## 4.0 Prefer-or (frozen)

Acquire on the product path **prefers**, as an **OR** (any one is enough; not a ranked fail-over that pads with toys):

1. **Live public fetch** — Dataverse, Card zip, WDI, FRED/IPUMS per existing routes (§4.1)
2. **Captain-local-real upload** — first-class acquire (§4.4)
3. **Honest link + upload** — followable URL plus generic upload when fetch cannot land bytes (§4.2)

Do not invent a fixture find or a toy when one of these three is available. Research scouting (find→acquire→organize→clean) continues in parallel; captain-local-real does **not** wait for scouts to finish.

## 4.1 Prefer session download (frozen)

When a **public** API or posted file allows anonymous retrieval, later fetch slices **must** try to write bytes into the **session workspace** (staging under the session run dir). Preferred venues:

| Venue | R-sources family (DECIDE-7 §4) | G0 named slice |
|---|---|---|
| **Dataverse** | `else` primary; **always-on backup** for every family | **FD-BE-fetch-dataverse** |
| **Card zip** | `minwage` (author-posted NJ–PA archive) | **FD-BE-fetch-card** |
| **WDI** | `growth` (World Bank World Development Indicators) | **FD-BE-fetch-wdi** |
| **FRED** | `macro` (existing route) | no extra G0 slice; same prefer-download rule |
| **IPUMS** | `educ_wage` (existing route) | no extra G0 slice; same prefer-download rule |

**Card zip** is the Card–Krueger author-posted reproduction archive. It is **not** `/demos/card` and **not** `allow_did`.

Success: candidate may move to `source_kind=fetched` with `fetch.status=into_session` and a session path. The user still **confirm-attaches** (DATA-COMPLETE) before `dataAttached`.

## 4.2 Else: link + honest upload (frozen)

If any of the following hold, **do not** invent a fixture find:

- No public file API
- Registration / login / ToS wall (typical for IPUMS extracts)
- HTTP / parse / license refusal
- Ambiguous HTML landing page with no resolvable file

Then: `source_kind=external_link` (or keep `discovered` with `fetch.status=link_only` when the row is a live catalog hit), show the **URL**, and offer **honest upload** (generic `user_upload` **or** captain-local-real when the file is a real panel from Desktop/经济学论文). Copy must say the product did **not** ingest a live catalog file. Upload of `course-panel.csv` / `minimum_wage.csv` / CFPS `sanitized_sample.csv` (or copies) is **not** a FIND win, **not** captain-local-real, and **not** a demo claim (§3.4–§3.7).

## 4.3 Fetch must not (frozen)

| Refusal | Frozen |
|---|---|
| Set `dataAttached` | Fetch is pre-attach staging. |
| Confirm-attach | User still confirms. |
| Treat fixture bytes as a fetch | Copying `fixtures/classic-5/*.csv` into the session is **not** real fetch and **not** `source_kind=fetched`. |
| Treat toy bytes as a fetch | Copying `minimum_wage.csv` / `course-panel.csv` / CFPS `sanitized_sample.csv` (or other n≈4–24 synthetics) into the session is **not** real fetch, **not** found data, and **not** a demo claim. |
| Vendor restricted files into git | IPUMS / CHARLS / licensed microdata stay out of the repo. Session staging is per-session, not a catalog commit. |
| Scrape behind login | No password, cookie, or token harvest. |
| Skip confirm-design | No authoritative fetch against missing / draft design. |
| Unlock DiD | Catalog / Card zip / Dataverse fetch does not set `allow_did`. |
| Label a toy as captain-local-real | Banned files and n≈4–24 synthetics never get `source_kind=captain_local_real`. |
| Vendor Desktop panels into git | Captain-local files stay session-local. G0 cites the **folder class**, not file bytes. |

## 4.4 Captain-local-real upload — first-class acquire (frozen)

Captain-authorized **interim** while Research scouts find→acquire→organize→clean.

| Rule | Frozen |
|---|---|
| Path name | **captain-local-real upload** |
| Label | `source_kind=captain_local_real` and/or `source=captain-local-real` (same meaning) |
| Bytes | **Real** `.dta` or CSV **panels** from Captain Desktop **经济学论文** (folder class). Not toys. Not synthetic. |
| Role | First-class **acquire**. Session may ingest these bytes for later confirm-attach. |
| Not FIND | Must **not** be copied as discovered / found / Dataverse / “we found your data”. |
| Not toys | DATA-RIGOR §3.4–§3.7 still holds. Banned CSVs cannot be relabeled captain-local-real. |
| n<200 | Honesty warning; demo claims fail closed (§3.6). A real panel that happens to be small is still not a demo win. |
| Git | Do **not** commit those Desktop files. Session staging only. |
| Scouts | Does not replace or skip Research find→acquire→organize→clean. Parallel interim. |
| Attach | Upload ≠ `dataAttached`. Confirm-attach still required. |

G0 does not freeze individual filenames from that Desktop folder (privacy / no user data in the contract). Later slices bind whatever **real** `.dta`/CSV the Captain uploads.

---

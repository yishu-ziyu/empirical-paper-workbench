# 8. Acceptance criteria (DECIDE-10; later slices)

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


G0 does not add tests. Later slices **must** implement and show these acceptance criteria. Do **not** evaluate by reading gold chapter bodies. Do **not** treat a fixture as found data.

**Locks (must remain true on every named slice):** real fetch first; fixtures = teaching-known only, never find success; optional teaching shelf with explicit label (**not** toys); prefer live public fetch **OR** captain-local-real upload **OR** honest link+upload; fixtures ≠ answer key; **no synthetic / toy data on the product path**; captain-local-real is acquire, not found data; CK title→propose DiD deferred to infer-design.

## 8.1 Named slice accept bullets

| Slice | Accept (gate reading) | Fail (unacceptable substitute) |
|---|---|---|
| **FD-BE-honesty** | Every FIND-DATA candidate has `source_kind`. Copy and list membership never present a fixture as discovered / found. Teaching extracts only as `teaching_fixture` (optional labeled shelf). Empty real fetch must not be padded with classic-5. | Fixture with `source_kind=discovered` / `fetched`; “找到了 ck1994”; id-only chip as the find; gold-body read; auto-attach. |
| **FD-BE-fetch-card** | Confirmed minwage design: attempt Card zip **download into session** when the posted archive is retrievable; else Card zip **link + honest upload**. Fixture is not the fetch. | `/demos/card`; copy `ck1994_long.csv` into session and call it the zip; skip confirm-design; set `dataAttached`; unlock DiD. |
| **FD-BE-fetch-dataverse** | Confirmed design: Dataverse search from facets; download a public file into session when the API allows; else dataset / search URL + honest upload. Search miss → Dataverse path still shown, **not** a fixture find. | Fixture as the Dataverse hit; hide Dataverse because a catalog id existed; attach without confirm. |
| **FD-BE-fetch-wdi** | Confirmed growth design: WDI download into session when the public API allows; else WDI link + honest upload. `barro1991_growth` stays teaching-known if shown. | Barro fixture as the WDI fetch; skip confirm; set `dataAttached`. |
| **FD-FE-honesty** | UI labels separate discovered / fetched / external_link / **captain-local-real** / teaching shelf / upload. Teaching shelf and captain-local-real explicitly **not** a find result. May use Design FIND-1 (`econpaper-ui-temp/flow-sketch`) as **draft sketch only**. | Sketch shipped as the formal UI; fixture cards with “found” copy; mixing unlabeled fixtures into the discovered list; toy sample as found; captain-local-real copied as discovered. |

## 8.2 DATA-RIGOR accept bullets (Captain; later slices)

| # | Accept (gate reading) | Fail (unacceptable substitute) |
|---|---|---|
| 1 | Teaching toys never presented as found data (copy, `source_kind`, suggest, FIND UI). | `course-panel.csv` / `minimum_wage.csv` / CFPS `sanitized_sample.csv` as discovered / fetched / “找到了数据”. |
| 2 | After confirm: live public fetch **OR** captain-local-real upload **OR** honest link+upload. | Guide-sample / spike / CFPS synthetic as the preferred path; pad miss with a toy; unlabeled generic upload standing in for captain-local-real. |
| 3 | Tiny fixtures only under `tests/`, labeled synthetic. Never in suggest / find-data UI. | New toy CSV in `frontend/public/` or `fixtures/` used as product data; test double shown as a find. |
| 4 | Smoke / rehearsal / classic write-loops use real Card 1995 extract or real panels. | 4–24-row toys as the proving write-loop; `course-panel.csv` golden-path as product rigor. |
| 5 | Attach or estimate with `n < 200`: honesty warning; **demo claims fail closed**. | Silent success; “demo passed” on 24 rows; missing n treated as large enough. |

## 8.3 Captain-local-real accept bullets (Captain interim; later slices)

| # | Accept (gate reading) | Fail (unacceptable substitute) |
|---|---|---|
| 1 | First-class acquire path exists: captain-local-real upload of **real** `.dta`/CSV panels. | Path missing; only guide-sample / toy CSV; wait for scouts before any acquire. |
| 2 | Rows labeled `source_kind=captain_local_real` and/or `source=captain-local-real`. | Unlabeled; copied as `discovered` / `fetched` / found data. |
| 3 | Still **not** toys; still **not** synthetic as found data. Banned CSVs cannot wear this label. | `course-panel.csv` / `minimum_wage.csv` / CFPS `sanitized_sample.csv` as captain-local-real. |
| 4 | Prefer live public fetch **OR** captain-local-real **OR** honest link+upload. | Fetch-only with no acquire; toy padding; captain-local-real waives FIND plan. |

OLS remains the default when DiD is not allowed (**infer-design**). Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block. FIND-LIT / R-lit-bar stay as DECIDE-7. This file does not change those rules.

DECIDE-7 extras still owed by FIND-DATA (not substitutes for the table above): where/how plan; ≥1 **non-fixture** real candidate after confirm (discovered / fetched / external_link); fixture **may** appear only as teaching-known; without that id still show the external path.

---

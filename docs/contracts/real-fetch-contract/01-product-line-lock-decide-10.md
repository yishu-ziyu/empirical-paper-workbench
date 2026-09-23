# 0. Product-line lock — DECIDE-10

> 上级：[Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)](../real-fetch-contract.md)


**DECIDE-10 (frozen; Decide via Firstmate / Captain).** Encode the following **verbatim**:

**Real fetch first.** find-data must not present fixtures as discovered/found data.

**Locks:**

- Fixtures = **teaching-known only**, never find success. Optional teaching shelf with explicit label.
- Prefer actual download into session when API allows: Dataverse, Card zip, WDI (and FRED/IPUMS per existing routes).
- Else: show link + honest upload path.
- Align with infer-design + find-data-lit contracts; fixtures ≠ answer key.

**FM-E-DATA-RIGOR-1 (frozen; Captain hard lock).** Encode the following **verbatim**:

**NO synthetic / invented / toy sample data on the product path.** Fake small CSVs that pass demos then die on real panels are forbidden.

**BANNED as product "found data":** `minimum_wage.csv` (4 rows), `course-panel.csv` (24), CFPS `sanitized_sample.csv` (24, synthetic).

**MUST:**

1. Never present teaching toys as found data.
2. Prefer live public fetch OR captain-local real files via upload.
3. Tiny fixtures ONLY under `tests/`, labeled synthetic — never in suggest/find-data UI.
4. Smoke/rehearsal/classic write-loops ≥ real Card1995 or real panels — not 4–24 row toys.
5. On attach/estimate, rows < 200 → fail-closed for demo claims (honesty warning).

**Captain-authorized interim (frozen).** Encode the following **verbatim**:

**First-class acquire path: captain-local-real upload.** Desktop/经济学论文 **real** `.dta`/CSV panels (not toys) while Research scouts find→acquire→organize→clean.

**Label:** `source=captain-local-real` (or `source_kind=captain_local_real`).

**Still NOT toys; still NOT synthetic as found data.**

**Prefer** live public fetch **OR** captain-local-real upload **OR** honest link+upload.

**Order after design confirm:** confirmed `session.design` → **real fetch / discovered candidates first** **or** **captain-local-real acquire** → optional teaching shelf (`teaching_fixture`, labeled; **not** toys) → attach → prewrite.

Product-object names in this file: `session.find_data.candidates[]` with required **`source_kind`**, optional **`source=captain-local-real`**, plus optional **`session.find_data.teaching_shelf`**. They are **not** `session.design`, **not** `dataAttached`, and **not** chapter bodies. Later slices must not evaluate by reading gold chapter bodies or treating a classic-5 id as a find.

In scope: the formal econpaper paper path **after** infer-design confirm — the same product line as `docs/contracts/find-data-lit-contract.md` and `docs/contracts/infer-design-contract.md`. This contract **recuts FIND-DATA honesty and fetch**. It does **not** reopen FIND-LIT / R-lit-bar.

Out of product line for this contract (do not extend, re-label, or treat as FIND / fetch success):

- Card teaching case **chrome** (`POST /demos/card`, `research.teaching_case=card_1995`, ADR-0015) as FIND success (real Card 1995 extract may still back **smoke / rehearsal** write-loops — §3.7)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`, 24 rows) — **DATA-RIGOR banned found-data**
- Spike toy (`agent/spike/fixtures/minimum_wage.csv`, 4 rows) — **DATA-RIGOR banned found-data**
- CFPS synthetic (`fixtures/cfps_association/sanitized_sample.csv`, 24 rows) — **DATA-RIGOR banned found-data**
- CHARLS wizard, other spike CSVs, eval datasets (including `agent/eval/tasks/undergrad_did_01`) presented as found data
- Agent spike (`/spike`), first-value marketing review, **flow-sketch / draft-product chrome as shipped UI**
- Sketch-only sample names (`sample_wage.csv`, `sample_panel_mini.csv`, `wage_panel.csv`)
- Catalog identity alone (`ck1994`, `ck1994_long`, `minimum-wage-employment`, `barro1991_growth`, `schooling-wages`, …) presented as **discovered / found**
- Unconfirmed `session.design` (`missing` / `draft`)
- Gold-body reads, six-chapter fill from catalog, generate-as-lit

`session.design` (infer-design), `session.find_data` plan (FIND-DATA / DECIDE-7), `dataAttached` (data-completion), and `table1Confirmed` / `specConfirmed` (PREWRITE-PAUSE) are **different** gates. This contract does not propose or confirm a design, does not replace the where/how plan, does not skip confirm-attach, and does not replace those flags. It **does** freeze that fixtures and teaching toys are never “found data”, that acquire prefers live public fetch **OR** captain-local-real upload **OR** honest link+upload, and that n<200 cannot carry a product demo claim.

DiD permission stays in `docs/contracts/infer-design-contract.md` §7. FIND-LIT / R-lit-bar stay in `docs/contracts/find-data-lit-contract.md` §7–§8. This file must not reopen catalog-token `allow_did`, must not propose DiD from a fixture id, and must not contradict title-first CK propose.

---

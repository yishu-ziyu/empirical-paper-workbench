# Real-fetch contract (after design confirm; DECIDE-10 + DATA-RIGOR)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-REAL-FETCH-1` · slice **G0** (DECIDE-10) · recut **`FM-E-DATA-RIGOR-1`** (Captain hard lock) · interim **captain-local-real** (Captain authorized)  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `feat/fm-e-build-did-spec-recut-1` @ `bf6957150713d9d8ff3ae72379d4233e5bd9b253`  
Design input: **DECIDE-10** (Decide via Firstmate / Captain) plus **FM-E-DATA-RIGOR-1** Captain hard lock plus Captain-authorized **interim acquire**: Desktop/经济学论文 **real** `.dta`/CSV panels (not toys) while Research scouts find→acquire→organize→clean  
Sister contracts (cited, not merged): `docs/contracts/find-data-lit-contract.md` (`FM-E-BUILD-FIND-DATA-LIT` FD-G0 / DECIDE-7), `docs/contracts/infer-design-contract.md` (`FM-E-BUILD-INFER-DESIGN-1` INF-G0 / DECIDE-6), `docs/contracts/data-completion-contract.md` (`FM-E-BUILD-DATA-COMPLETE-1` G0), `docs/contracts/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Authority: this file freezes the DECIDE-10 **order**, **locks**, **`source_kind`** (including **`captain_local_real`**), the **DATA-RIGOR** toy ban / n<200 honesty gate, and **slice accept bullets** below. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so FD-BE-honesty / FD-BE-fetch-\* / FD-FE-honesty can run without colliding with infer-design confirm, FIND-DATA plan authorship, FIND-LIT / R-lit-bar, DATA-COMPLETE attach, PREWRITE-PAUSE flags, classic-5 CSV authorship, or gold chapter bodies. Acceptance is the DECIDE-10 bullets in §8 plus DATA-RIGOR in §8.2 plus captain-local-real in §8.3 — **not** gold-body reads, **not** fixture-as-found, and **not** 4–24-row toys as product demos.

---

## 目录

1. [0. Product-line lock — DECIDE-10](real-fetch-contract/01-product-line-lock-decide-10.md)
2. [1. Purpose and non-goals](real-fetch-contract/02-purpose-and-non-goals.md)
3. [2. Named object — `source_kind`](real-fetch-contract/03-named-object-source-kind.md)
4. [3. Honesty — fixtures are teaching-known only](real-fetch-contract/04-honesty-fixtures-are-teaching-known-only.md)
5. [4. Fetch policy — download vs link + upload](real-fetch-contract/05-fetch-policy-download-vs-link-upload.md)
6. [5. Order vs infer-design, FIND-DATA, DATA-COMPLETE](real-fetch-contract/06-order-vs-infer-design-find-data.md)
7. [6. Venue notes (later fetch slices)](real-fetch-contract/07-venue-notes-later-fetch-slices.md)
8. [7. FD-FE-honesty — labels (draft sketch only)](real-fetch-contract/08-fd-fe-honesty-labels-draft-sketch.md)
9. [8. Acceptance criteria (DECIDE-10; later slices)](real-fetch-contract/09-acceptance-criteria-decide-10-later-slices.md)
10. [9. Later parallel slices (do not implement in G0)](real-fetch-contract/10-later-parallel-slices-do-not-implement.md)
11. [10. Concurrent write-sets (stay out)](real-fetch-contract/11-concurrent-write-sets-stay-out.md)
12. [11. G0 done rule](real-fetch-contract/12-g0-done-rule.md)

# Infer-design contract (title-first; DECIDE-6)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-INFER-DESIGN-1` · slice **INF-G0**  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `main` @ `79c9c91508f9f1479dc5cd8c6d85b3342f7c913d`  
Design input: **DECIDE-6** acceptance from Decide (via Firstmate) — title-first research-design inference; catalog is candidates only; **no gold body reads**  
Sister contracts (cited, not merged): `docs/contracts/data-completion-contract.md` (`FM-E-BUILD-DATA-COMPLETE-1` G0), `docs/contracts/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Authority: this file freezes the DECIDE-6 **order**, **locks**, and **accept bullets** below, plus **`session.design` draft vs confirmed** and the DiD rewrite that **deprecates catalog-token `allow_did`**. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so INF-BE-\* / DID-BE-\* / DC-BE-suggest can run without colliding with DATA-COMPLETE attach, PREWRITE-PAUSE flags, or classic-5 CSV authorship. Acceptance is the DECIDE-6 bullets in §8 — **not** gold-body reads.

---

## 目录

1. [0. Product-line lock — DECIDE-6](infer-design-contract/01-product-line-lock-decide-6.md)
2. [1. Purpose and non-goals](infer-design-contract/02-purpose-and-non-goals.md)
3. [2. Named object — `session.design`](infer-design-contract/03-named-object-session-design.md)
4. [3. Propose flow](infer-design-contract/04-propose-flow.md)
5. [4. Confirm flow](infer-design-contract/05-confirm-flow.md)
6. [5. Order vs DATA-COMPLETE and PREWRITE-PAUSE](infer-design-contract/06-order-vs-data-complete-and-prewrite.md)
7. [6. Fixtures / classic-5 — candidates only](infer-design-contract/07-fixtures-classic-5-candidates-only.md)
8. [7. DiD narrow-exception rewrite — deprecate catalog-token `allow_did`](infer-design-contract/08-did-narrow-exception-rewrite-deprecate-catalog.md)
9. [8. Acceptance criteria (DECIDE-6; verbatim)](infer-design-contract/09-acceptance-criteria-decide-6-verbatim.md)
10. [9. Later parallel slices (do not implement in G0)](infer-design-contract/10-later-parallel-slices-do-not-implement.md)
11. [10. Concurrent write-sets (stay out)](infer-design-contract/11-concurrent-write-sets-stay-out.md)
12. [11. G0 done rule](infer-design-contract/12-g0-done-rule.md)

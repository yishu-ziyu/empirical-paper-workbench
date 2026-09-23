# Find-data + find-literature contract (after design confirm; DECIDE-7)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-FIND-DATA-LIT` · slice **FD-G0**  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `feat/fm-e-build-infer-design-1` @ `2a663915cb590a8d6026021e1f9604dc2978ddb6`  
Design input: **DECIDE-7** acceptance from Decide (via Firstmate) — FIND data sources + FIND literature **after** design confirm; catalog/fixtures are candidates only; **no catalog answer keys**; **no gold biblio paste**  
Sister contracts (cited, not merged): `docs/contracts/infer-design-contract.md` (`FM-E-BUILD-INFER-DESIGN-1` INF-G0), `docs/contracts/data-completion-contract.md` (`FM-E-BUILD-DATA-COMPLETE-1` G0), `docs/contracts/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Research V1 tokens (must appear; frozen below): **FD**, **R-sources**, **R-lit-bar**, **FL**  
Authority: this file freezes the DECIDE-7 **order**, **locks**, and **accept bullets** below, plus **FD** (design facets → Dataverse + fixture candidates), the **R-sources** data route table, the **candidate shape**, **FL** (OpenAlex + Crossref + S2, DOI dedupe), and the **R-lit-bar** that **replaces generate-as-lit**. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so FD-BE-\* / FL-BE-\* / FD-FE-\* / FL-FE-\* can run without colliding with infer-design confirm, DATA-COMPLETE attach, PREWRITE-PAUSE flags, classic-5 CSV authorship, or gold chapter bodies. Acceptance is the DECIDE-7 bullets in §9 — **not** gold-body reads and **not** gold bibliography pastes.

---

## 目录

1. [0. Product-line lock — DECIDE-7](find-data-lit-contract/01-product-line-lock-decide-7.md)
2. [1. Purpose and non-goals](find-data-lit-contract/02-purpose-and-non-goals.md)
3. [2. Named objects](find-data-lit-contract/03-named-objects.md)
4. [3. FD — design facets → Dataverse + fixture candidates](find-data-lit-contract/04-fd-design-facets-dataverse-fixture-candidates.md)
5. [4. R-sources — data route table (frozen)](find-data-lit-contract/05-r-sources-data-route-table-frozen.md)
6. [5. Candidate shape (frozen)](find-data-lit-contract/06-candidate-shape-frozen.md)
7. [6. Order vs infer-design, DATA-COMPLETE, PREWRITE-PAUSE](find-data-lit-contract/07-order-vs-infer-design-data-complete.md)
8. [7. FL — OpenAlex + Crossref + S2, DOI dedupe](find-data-lit-contract/08-fl-openalex-crossref-s2-doi-dedupe.md)
9. [8. R-lit-bar — replace generate-as-lit (frozen)](find-data-lit-contract/09-r-lit-bar-replace-generate-as.md)
10. [9. Acceptance criteria (DECIDE-7; verbatim)](find-data-lit-contract/10-acceptance-criteria-decide-7-verbatim.md)
11. [10. Later parallel slices (do not implement in G0)](find-data-lit-contract/11-later-parallel-slices-do-not-implement.md)
12. [11. Concurrent write-sets (stay out)](find-data-lit-contract/12-concurrent-write-sets-stay-out.md)
13. [12. G0 done rule](find-data-lit-contract/13-g0-done-rule.md)

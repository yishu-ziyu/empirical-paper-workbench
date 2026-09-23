# Bryce tools contract (four IN; DECIDE-8)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-BRYCE-G0` · slice **BRYCE-G0** (pointers folded for later `FM-E-BUILD-BRYCE-1`)  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `feat/fm-e-build-did-spec-recut-1` @ `bf6957150713d9d8ff3ae72379d4233e5bd9b253`  
Design input: **DECIDE-8** acceptance from Decide (via Firstmate) — four Bryce-adjacent tools **IN** as thin mappings onto existing formal surfaces; four named dumps **OUT**. Research **INTEGRATE** + `FM-E-BUILD-BRYCE-1` supply the **pointer names** in §0.1.  
Sister contracts (cited, not merged): `docs/contracts/infer-design-contract.md` (`FM-E-BUILD-INFER-DESIGN-1` INF-G0 / DECIDE-6), `docs/contracts/find-data-lit-contract.md` (`FM-E-BUILD-FIND-DATA-LIT` FD-G0), `docs/contracts/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Authority: this file freezes the DECIDE-8 **IN set**, **OUT set**, **order relative to DECIDE-6/7**, the **INTEGRATE pointers**, and **accept bullets** below. Later BE slices (`FM-E-BUILD-BRYCE-1`) implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so later **FL-BE-reuse** / **CL-BE-winsor** / **NORMS-BE** / **EVAL-top5** can run without standing up a parallel Bryce product, a second literature pipeline, a Stata-default cleaner, a p-hack helper, a Claude skill runner, or a sprawling eval farm. Acceptance is the DECIDE-8 bullets in §7 — **not** gold-body reads, **not** a Paper-WorkFlow dump, and **not** a full AER-Skills dump.

**G0 still does not implement BE.** INTEGRATE pointer names have landed (§0.1). Do not start those slices in this write-set. G0 aliases (`BRYCE-BE-lit-thin`, `BRYCE-BE-winsor`, `BRYCE-BE-aer-gates`, `BRYCE-BE-top5-eval`) are **retired as slice ids**; they map 1:1 onto the INTEGRATE tokens. Later work cites the INTEGRATE names.

---

## 目录

1. [0. Product-line lock — DECIDE-8](bryce-tools-contract/01-product-line-lock-decide-8.md)
2. [1. Purpose and non-goals](bryce-tools-contract/02-purpose-and-non-goals.md)
3. [2. How the four picks map onto existing surfaces](bryce-tools-contract/03-how-the-four-picks-map-onto.md)
4. [3. Order vs DECIDE-6 / DECIDE-7](bryce-tools-contract/04-order-vs-decide-6-decide-7.md)
5. [4. Four picks IN (detail)](bryce-tools-contract/05-four-picks-in-detail.md)
6. [5. Explicitly OUT (frozen)](bryce-tools-contract/06-explicitly-out-frozen.md)
7. [6. Named objects (reuse, do not fork)](bryce-tools-contract/07-named-objects-reuse-do-not-fork.md)
8. [7. Acceptance criteria (DECIDE-8 + INTEGRATE pointers)](bryce-tools-contract/08-acceptance-criteria-decide-8-integrate-pointers.md)
9. [8. Later parallel slices (`FM-E-BUILD-BRYCE-1`; do not implement in G0)](bryce-tools-contract/09-later-parallel-slices-fm-e-build.md)
10. [9. Concurrent write-sets (stay out)](bryce-tools-contract/10-concurrent-write-sets-stay-out.md)
11. [10. G0 done rule](bryce-tools-contract/11-g0-done-rule.md)

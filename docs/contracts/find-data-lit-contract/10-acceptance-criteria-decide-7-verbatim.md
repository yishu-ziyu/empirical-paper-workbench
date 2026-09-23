# 9. Acceptance criteria (DECIDE-7; verbatim)

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


G0 does not add tests. Later FD / FL slices **must** implement and show these acceptance criteria. Text below is **verbatim** from Decide (via Firstmate). Do **not** evaluate by reading gold chapter bodies or gold bibliographies.

1. After design confirm: where/how find-data plan + ≥1 real candidate (not only classic-5 id)
2. Fixture may appear as candidate; without that id still show external path (Dataverse etc.)
3. Lit: verifiable title/author/year/DOI or link; no gold biblio paste
4. CK still title→propose DiD first (defer to infer-design; do not contradict)

## 9.1 How later slices bind those bullets (not substitutes)

| # | Gate reading | Fail (unacceptable substitute) |
|---|---|---|
| 1 | After `session.design` confirm: emit a **where/how** plan (FD + R-sources) **and** ≥1 **real** candidate in the §5 shape. A classic-5 id without `url_or_fixture` does not count. | Plan without confirm; id-only chip as the only hit; auto-attach; gold-body read. |
| 2 | Fixture **may** be listed (`ck1994_long`, wage1, `barro1991_growth`, …). If that id is renamed/removed/absent, still show the **external** path (Dataverse, Card zip, IPUMS, WDI, FRED per R-sources). | Fail closed when fixture missing; treat fixture as answer key; hide Dataverse because a catalog id existed. |
| 3 | Each literature card has verifiable **title / author / year / DOI or link** from FL search. No gold biblio paste into chapters or `literature_entries`. | generate-as-lit; mock/gold biblio as success; cards with title only and no DOI/link. |
| 4 | Card–Krueger class **title** still goes **title → propose DiD** (treated×period) **before** ck attach, per `docs/contracts/infer-design-contract.md` §8 bullet 1. This contract lists ck fixture + Card zip **after** confirm, as candidates. | Propose DiD from catalog id; skip infer-design; FIND-DATA sets `allow_did`; contradict DECIDE-6. |

OLS remains the default when DiD is not allowed (**infer-design**). Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block. This file does not change those rules.

**Research V1 extras later slices also owe** (not substitutes for the four bullets): FD Dataverse + fixtures; R-sources table; candidate shape; FL three-source search + DOI dedupe; R-lit-bar five steps; no Elicit / 知网爬 / Consensus-as-chapter.

---

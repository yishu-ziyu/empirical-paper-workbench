# 0. Product-line lock — DECIDE-7

> 上级：[Find-data + find-literature contract (after design confirm; DECIDE-7)](../find-data-lit-contract.md)


**DECIDE-7 (frozen; Decide via Firstmate).** Encode the following **verbatim**:

**Order relative to infer-design:** title → propose → confirm → **find-data plan + candidates** → attach → prewrite.

**Locks:**

- Fixtures never answer key.
- No catalog answer keys.
- CK still title → propose DiD first (defer to infer-design; do not contradict).

**Accept bullets (verbatim; bound in §9):**

1. After design confirm: where/how find-data plan + ≥1 real candidate (not only classic-5 id)
2. Fixture may appear as candidate; without that id still show external path (Dataverse etc.)
3. Lit: verifiable title/author/year/DOI or link; no gold biblio paste
4. CK still title→propose DiD first (defer to infer-design; do not contradict)

Product-object names in this file: `session.find_data` (plan + candidates) and `session.find_lit` (search hits + checkbox cards + export). They are **not** `session.design`, **not** `dataAttached`, and **not** chapter bodies. Later slices must not evaluate by reading gold chapter bodies or a gold bibliography.

**Research V1 (frozen; must appear).** Formal-path FIND after confirmed `session.design`:

| Token | Frozen meaning |
|---|---|
| **FD** | Design facets → Dataverse search + fixture candidates. |
| **R-sources** | Data route table: educ/wage → IPUMS/wage1; minwage → ck fixture + Card zip; growth → WDI/barro; macro → FRED; else Dataverse. |
| **Candidate shape** | `source_id`, `title`, `url_or_fixture`, `license`, `suggested_cols`, `design_fit`. |
| **FL** | OpenAlex + Crossref + S2, DOI dedupe. |
| **R-lit-bar** | Replaces generate-as-lit. See §8. |

**R-lit-bar (frozen; replace generate-as-lit):**

1. OpenAlex + Crossref + S2 search
2. DOI dedupe
3. ≥5 checkbox cards before write into chapters
4. checked → `refs.bib` or CSL-JSON
5. mailto polite pool

No Elicit / 知网爬 / Consensus-as-chapter in V1.

In scope: the formal econpaper paper path **after** infer-design confirm — the same product line as `docs/contracts/infer-design-contract.md` and `docs/contracts/data-completion-contract.md`.

Out of product line for this contract (do not extend, re-label, or treat as FIND success):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`, ADR-0015)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets (including `agent/eval/tasks/undergrad_did_01`)
- Agent spike (`/spike`), first-value marketing review, flow-sketch / draft-product chrome
- Sketch-only sample names (`sample_wage.csv`, `sample_panel_mini.csv`, `wage_panel.csv`)
- Catalog identity alone (`ck1994`, `ck1994_long`, `minimum-wage-employment`, `barro1991_growth`, `schooling-wages`, …) as the **only** candidate
- Unconfirmed `session.design` (`missing` / `draft`)
- Elicit, 知网爬取, Consensus-as-chapter, Apodex-as-V1-source (ADR-0011 remains an expired optional bypass, not FL)
- LLM generate-as-lit (invented title/author/year written into `lit_review` / References)
- Gold bibliography paste, gold-body reads, six-chapter fill from catalog

`session.design` (infer-design) and `dataAttached` (data-completion) and `table1Confirmed` / `specConfirmed` (PREWRITE-PAUSE) are **different** gates. This contract does not propose or confirm a design, does not attach a dataset, does not skip confirm-attach, and does not replace those flags. It **does** freeze what “data candidates” means after confirm, and it **does** replace generate-as-lit with **R-lit-bar**.

DiD permission stays in `docs/contracts/infer-design-contract.md` §7. This file must not reopen catalog-token `allow_did`, must not propose DiD from a fixture id, and must not contradict title-first CK propose.

---

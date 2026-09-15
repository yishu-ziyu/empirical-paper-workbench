# Find-data + find-literature contract (after design confirm; DECIDE-7)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-FIND-DATA-LIT` · slice **FD-G0**  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `feat/fm-e-build-infer-design-1` @ `2a663915cb590a8d6026021e1f9604dc2978ddb6`  
Design input: **DECIDE-7** acceptance from Decide (via Firstmate) — FIND data sources + FIND literature **after** design confirm; catalog/fixtures are candidates only; **no catalog answer keys**; **no gold biblio paste**  
Sister contracts (cited, not merged): `docs/infer-design-contract.md` (`FM-E-BUILD-INFER-DESIGN-1` INF-G0), `docs/data-completion-contract.md` (`FM-E-BUILD-DATA-COMPLETE-1` G0), `docs/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Research V1 tokens (must appear; frozen below): **FD**, **R-sources**, **R-lit-bar**, **FL**  
Authority: this file freezes the DECIDE-7 **order**, **locks**, and **accept bullets** below, plus **FD** (design facets → Dataverse + fixture candidates), the **R-sources** data route table, the **candidate shape**, **FL** (OpenAlex + Crossref + S2, DOI dedupe), and the **R-lit-bar** that **replaces generate-as-lit**. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so FD-BE-\* / FL-BE-\* / FD-FE-\* / FL-FE-\* can run without colliding with infer-design confirm, DATA-COMPLETE attach, PREWRITE-PAUSE flags, classic-5 CSV authorship, or gold chapter bodies. Acceptance is the DECIDE-7 bullets in §9 — **not** gold-body reads and **not** gold bibliography pastes.

---

## 0. Product-line lock — DECIDE-7

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

In scope: the formal econpaper paper path **after** infer-design confirm — the same product line as `docs/infer-design-contract.md` and `docs/data-completion-contract.md`.

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

DiD permission stays in `docs/infer-design-contract.md` §7. This file must not reopen catalog-token `allow_did`, must not propose DiD from a fixture id, and must not contradict title-first CK propose.

---

## 1. Purpose and non-goals

### 1.1 Purpose (frozen)

Given a formal-path session whose **`session.design.status === "confirmed"`**, this flow only:

1. **FD** — Builds a **find-data plan** (where / how) from **design facets**, then lists **candidates**: Dataverse search hits **plus** matching fixture candidates (R-sources may add a named external path).
2. Requires **≥1 real candidate**. A classic-5 **id string alone is not** a real candidate (§5).
3. Lets DATA-COMPLETE **attach** a chosen candidate later. FIND-DATA still lists candidates; it never auto-selects, never confirm-attaches, never writes gold chapter bodies.
4. **FL** — Searches **OpenAlex + Crossref + S2**, **DOI-dedupes**, and shows **≥5 checkbox cards** with verifiable title / author / year / DOI or link.
5. Exports **checked** cards to `refs.bib` **or** CSL-JSON. Only checked entries may be written into chapters (**R-lit-bar**).

### 1.2 Non-goals (frozen)

This contract does **not**:

- Propose or confirm `session.design` (INF-BE-propose / INF-BE-confirm)
- Treat catalog → locked spec, catalog → `allow_did`, or catalog → gold biblio as a win path
- Auto-succeed, auto-select, or prefill a fixture as the user’s study
- Attach a dataset or set `dataAttached`
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, `generate_title` / `state.title_chapter`, or export docx
- Write `lit_review` / References from an LLM memory dump (**generate-as-lit**)
- Paste a gold bibliography, gold chapter body, or classic-5 answer key
- Crawl 知网, call Elicit, or treat Consensus output as a chapter
- Merge `feat/fm-e-build-data-complete-1`, `feat/fm-e-build-infer-design-1` implementation slices, `feat/fm-e-build-did-narrow-1`, or other DC / DID / INF code branches
- Implement application code, API routes, OpenAPI shapes, or frontend chrome (FD-G0 is markdown only)

`TITLE/TOPIC` here is the session-start title / topic string already consumed by infer-design. FIND-DATA / FIND-LIT read the **confirmed** `session.design`, not the title as a substitute for confirm.

---

## 2. Named objects

### 2.1 `session.find_data` (frozen)

Product object name: **`session.find_data`**.

This is the formal-path FIND-DATA record emitted **after** design confirm. It is **not** a catalog entry, **not** `dataAttached`, and **not** `session.design`.

G0 does not add the object to snapshot, OpenAPI, or session state. Later slices may project it. Missing / null / absent **is** “no FIND-DATA yet.” Fail closed: do not treat a classic-5 id highlight as a plan.

### 2.2 Plan vs candidates (frozen)

| Field | Meaning | Downstream may treat as attached? |
|---|---|---|
| `plan` | Where / how to look, derived from confirmed design facets + **R-sources** | No |
| `candidates[]` | Real candidate objects (§5). Fixtures may appear. | No — still candidates |
| `status` | `missing` / `planned` | No |

| Flag | Meaning |
|---|---|
| `planned_at` | When the current plan + candidate list was written |
| `route_family` | R-sources family: `educ_wage` / `minwage` / `growth` / `macro` / `else` |
| `primary_venue` | Where the plan sends the user first (Dataverse, IPUMS, FRED, WDI, fixture+Card zip, …) |

Selecting a candidate still requires DATA-COMPLETE confirm-attach. FIND-DATA never sets `dataAttached`.

### 2.3 `session.find_lit` (frozen)

Product object name: **`session.find_lit`**.

This is the formal-path FIND-LIT record. It is **not** `literature_entries` filled by generate-as-lit, **not** a gold biblio, and **not** a chapter body.

| Field | Meaning |
|---|---|
| `hits[]` | Deduped FL hits (OpenAlex + Crossref + S2) |
| `cards[]` | Checkbox cards shown to the user. V1 requires **≥5** before any chapter write |
| `checked_ids[]` | Cards the user checked |
| `export` | `refs.bib` and/or CSL-JSON built **only** from checked cards |
| `polite_pool` | mailto identity used in User-Agent (§8.5) |

G0 does not add the object. Missing / null / absent **is** “no FIND-LIT yet.” Chapter write of literature **fails closed**.

### 2.4 Must not live on these objects as a win path

Catalog id alone, `allow_did`, `dataAttached`, chapter bodies, gold-body hashes, gold biblio blobs, Elicit/知网/Consensus payloads, unconfirmed `session.design`.

---

## 3. FD — design facets → Dataverse + fixture candidates

### 3.1 Design facets (frozen)

**FD** reads **only** a confirmed `session.design` (plus the title/RQ already stored on `session.design.source`). Facets used to search:

| Facet | From | Used for |
|---|---|---|
| `method` | confirmed `session.design.method` | Route + `design_fit` |
| `outcome` / `treatment` | confirmed Y / X slots | Query terms + `suggested_cols` |
| `controls` / DiD slots | confirmed controls, `treated`, `period`, interactions | Column suggestions |
| `qType` | confirmed | Do not weaken HET hard-block |
| `source.title` / `source.question` | infer-design source | Query text; **not** a confirm substitute |

Unconfirmed or missing design: FD **must not** rank as an authoritative match. Fail closed or stay silent. Infer-design §5.3 still holds: before confirm, the attach panel may open in **candidates-only** mode with **no** ranked-as-authoritative FIND-DATA plan.

### 3.2 What FD must do

After confirm:

1. Classify **R-sources** `route_family` from the confirmed facets (§4).
2. Emit a **find-data plan**: **where** (venue) and **how** (query / landing path).
3. Search **Dataverse** with those facets (Harvard Dataverse catalog search or equivalent public Dataverse API). Hits become candidates with URLs.
4. List matching **fixture** candidates from `classic-5` / named teaching extracts (**candidates only**, never answer key).
5. Return **≥1 real candidate** in the §5 shape. Not only a classic-5 id.

Dataverse is the **default external catalog** for `else` and the **always-on backup** when a named fixture id is missing.

### 3.3 What FD must not do

| Refusal | Frozen |
|---|---|
| Run before confirm-design | No authoritative plan; no “matched ck1994” as success. |
| Attach / ingest | Must not call upload, classic-5 attach, or stamp snapshot `dataset`. |
| `dataAttached` | Must not set true. FIND-DATA is pre-attach. |
| Catalog as answer key | Must not auto-select `ck1994` / `ck1994_long` / `barro1991_growth` / `schooling-wages` / any `classic-5` entry. |
| Classic-5 id as the only candidate | A candidate must have `url_or_fixture` (and the rest of §5). An id token is not enough. |
| DiD from catalog | Must not set `allow_did` or propose `method=did`. Defer to infer-design. |
| Gold / chapter bodies | Must not write chapter text, gold-body fixtures, or six-chapter fill. |
| Restricted microdata commit | Must not vendor IPUMS extracts, CHARLS, or other restricted files into the repo. External path only. |

---

## 4. R-sources — data route table (frozen)

**R-sources** is the named V1 route table. Classify from confirmed design facets (outcome / treatment / title-RQ topic). First matching row wins. Ambiguous → `else` (Dataverse).

| Family | When (illustrative facets) | Where / how (plan) | Fixture may appear | External path if fixture id absent |
|---|---|---|---|---|
| `educ_wage` | schooling / educ / wage / earnings / Mincer | **IPUMS** extract landing + **wage1** (Wooldridge wage1 teaching extract) | `schooling-wages` / wage1 if present in classic-5 / fixtures | IPUMS (CPS/USA or equivalent) + Dataverse backup |
| `minwage` | minimum wage / Card–Krueger / NJ–PA employment | **ck fixture** + **Card zip** (author-published NJ–PA zip) | `ck1994_long` / `ck1994` / `minimum-wage-employment` | Card zip URL + Dataverse |
| `growth` | cross-country growth / Barro / enrollment / investment | **WDI** (World Bank World Development Indicators) + **barro** | `barro1991_growth` | WDI + Dataverse |
| `macro` | FRED-style macro series / rates / aggregates without a growth-Barro object | **FRED** | none required | FRED + Dataverse backup |
| `else` | no row above | **Dataverse** search from facets | any classic-5 hit that `design_fit`s | Dataverse (required) |

Plan text must name **where** and **how** (e.g. “search Dataverse for confirmed outcome+treatment; also list ck fixture; Card zip at the author page”). A family label without a venue is not a plan.

**Card zip** is an external reproduction path for the Card–Krueger study data. It is **not** `/demos/card` (Card 1995 teaching case) and **not** `allow_did`.

**IPUMS** and **WDI** and **FRED** are external venues. FIND-DATA lists them as `url_or_fixture` candidates. It does not scrape behind login, does not store restricted extracts, and does not skip the user’s own confirm-attach.

---

## 5. Candidate shape (frozen)

A **real candidate** is an object with **all** of:

| Field | Type | Meaning |
|---|---|---|
| `source_id` | string | Stable id. Examples: `classic-5:ck1994_long`, `dataverse:doi:10.7910/DVN/…`, `fred:UNRATE`, `wdi:NY.GDP.PCAP.KD.ZG`, `ipums:cps`, `card-zip:njmin`, `wage1`. |
| `title` | string | Human title of the dataset / extract. |
| `url_or_fixture` | string | Followable URL **or** in-repo fixture path. Empty / id-only **fails** the real-candidate test. |
| `license` | string | Declared license or access class (`CC0`, `public`, `registration-required`, …). Unknown → say `unknown`; do not invent CC0. |
| `suggested_cols` | string[] | Columns that bind to confirmed Y / X / DiD slots when known; empty allowed. |
| `design_fit` | object | Why this candidate matches the **confirmed** design (`method`, outcome, treatment, short note). |

```json
{
  "source_id": "classic-5:ck1994_long",
  "title": "Card and Krueger minimum wage",
  "url_or_fixture": "fixtures/classic-5/ck1994_long.csv",
  "license": "public-reproduction",
  "suggested_cols": ["employment", "treated", "period"],
  "design_fit": {
    "method": "did",
    "outcome": "employment",
    "treatment": "min_wage",
    "notes": "matches confirmed minwage DiD; candidate only"
  }
}
```

A second minwage candidate **without** that fixture id still required when the id is missing:

```json
{
  "source_id": "card-zip:njmin",
  "title": "Card–Krueger NJ–PA fast-food data (author zip)",
  "url_or_fixture": "https://davidcard.berkeley.edu/data_sets.html",
  "license": "author-posted",
  "suggested_cols": [],
  "design_fit": {
    "method": "did",
    "outcome": "employment",
    "treatment": "min_wage",
    "notes": "external path; fixture id absent"
  }
}
```

(Exact author URL may resolve to the current Card data-sets page. G0 freezes the **role**, not a byte hash.)

### 5.1 Real vs not real

| Object | Real candidate? |
|---|---|
| Full §5 object with URL or fixture path | Yes |
| classic-5 id string (`ck1994_long`) with no `url_or_fixture` | **No** |
| Catalog highlight / chip with only `entry_id` | **No** |
| Dataverse hit with dataset URL | Yes |
| IPUMS / FRED / WDI / Card zip landing URL | Yes |
| “use your own file” action | Allowed extra action; does not replace the ≥1 real candidate |

Fixture **may** appear as a candidate. Absence of that fixture id **must not** empty the list: show the R-sources external path (Dataverse etc.).

---

## 6. Order vs infer-design, DATA-COMPLETE, PREWRITE-PAUSE

### 6.1 Intended sequence (frozen)

DECIDE-7 order (verbatim relative to infer-design):

```
title → propose → confirm → find-data plan + candidates → attach → prewrite
```

Mapped onto named gates already in this product line:

```
title/question
    → design propose                         ⇒  session.design status=draft     (infer-design)
    → human confirm                          ⇒  session.design status=confirmed
    → find-data plan + candidates            ⇒  session.find_data (FD + R-sources)
    → attach                                 ⇒  dataAttached                    (data-completion)
    → prewrite pauses                        table1Confirmed then specConfirmed
```

FIND-LIT (**FL** + **R-lit-bar**) is **after design confirm** and **before any literature chapter write**. It does **not** skip attach, PREWRITE-PAUSE, or estimate. It does **not** sit in the attach slot.

```
confirm-design
    → FL search (OpenAlex + Crossref + S2) + DOI dedupe
    → ≥5 checkbox cards
    → user checks → refs.bib or CSL-JSON
    → (only then) write checked entries into chapters
```

Estimate / robustness may still run before chapter write (existing paper-engine order). R-lit-bar forbids writing literature chapters from generate-as-lit even if estimate already ran.

### 6.2 Rules

1. **Confirm-design first.** FD must not emit an authoritative plan against missing or draft `session.design`.
2. **FIND-DATA does not attach.** `dataAttached` still first for data (`docs/data-completion-contract.md`).
3. **PREWRITE-PAUSE still owns** `table1Confirmed` and `specConfirmed`. FIND-DATA / FIND-LIT do not set them.
4. **CK DiD propose stays on infer-design.** Title/question only → propose DiD + treated×period **before** any ck attach (infer-design §8 bullet 1). This file lists ck / Card zip **after** that confirm, as candidates.
5. **Fixtures never answer key.** Suggest / FIND list is not success, not gold, not auto-attach.
6. **Independence.** `dataAttached` does not complete FIND-LIT. Checking lit cards does not set `dataAttached`. A catalog highlight does not do either.

### 6.3 What may happen before confirm-design

- Infer-design draft propose / edit
- Opening an attach panel in **candidates-only** mode (no FD plan as authoritative match)

What must not happen before confirm-design:

- FD plan that claims a confirmed-design match
- Catalog → `allow_did` or catalog → locked spec
- R-lit-bar chapter write
- `table1Confirmed` / `specConfirmed` / estimate / gold biblio paste

---

## 7. FL — OpenAlex + Crossref + S2, DOI dedupe

### 7.1 Sources (frozen)

**FL** V1 search set is exactly:

| Source | Role |
|---|---|
| **OpenAlex** | Works search from confirmed design facets + title/RQ |
| **Crossref** | Works search (existing `literature_sources/crossref.py` is a later-slice implementation target, not a G0 edit) |
| **S2** | Semantic Scholar works search |

All three are searched in V1. Missing key / network failure on one source **does not** license generate-as-lit. Remaining sources still feed the card list. If the merged, deduped list cannot fill **≥5** verifiable cards, **do not write** literature into chapters. Fail closed.

**Not V1 sources:** Elicit, 知网爬, Consensus, Google Scholar scrape, Apodex, mock corpus as a success path, gold biblio fixtures.

ADR-0004 mock and ADR-0011 Apodex stay out of the V1 win path. pytest may still mock HTTP; that is a test double, not generate-as-lit and not a gold biblio.

### 7.2 Query (frozen)

Build the query from **confirmed** `session.design` facets (method, outcome, treatment, title/RQ). Do not require `dataAttached`. Do not let the model free-write the only query without those facets.

### 7.3 DOI dedupe (frozen)

Merge hits across OpenAlex, Crossref, and S2.

1. Normalize DOI (lowercase, strip `https://doi.org/` prefix).
2. Same DOI → one card. Prefer the record that has the fullest title/author/year.
3. No DOI → fallback key `normalized(title) + year + first author`. Do not drop a verifiable link-only hit solely for missing DOI.
4. One checkbox card per surviving work.

### 7.4 Verifiable card fields (frozen)

Each card **must** expose:

| Field | Rule |
|---|---|
| `title` | From a search hit, not LLM memory |
| `authors` | From a search hit |
| `year` | From a search hit |
| `doi` **or** `url` | At least one followable identifier. DOI preferred. |

Missing all of DOI and URL → **not** a V1 card. Do not fill gaps from gold biblio or generate-as-lit.

---

## 8. R-lit-bar — replace generate-as-lit (frozen)

**R-lit-bar** is the named V1 literature bar. It **replaces generate-as-lit**.

**generate-as-lit** (forbidden win path) = writing `lit_review`, References, `literature_entries`, or citation indices from an LLM’s remembered papers, a gold bibliography paste, or a mock corpus presented as the user’s search.

### 8.1 Five steps (verbatim order)

1. **OpenAlex + Crossref + S2 search** (§7.1)
2. **DOI dedupe** (§7.3)
3. **≥5 checkbox cards** before write into chapters
4. **checked → `refs.bib` or CSL-JSON**
5. **mailto polite pool**

### 8.2 Checkbox cards (frozen)

- Show **at least five** cards that pass §7.4 **before** any literature chapter write.
- Each card has a checkbox. Unchecked cards must not enter `refs.bib`, CSL-JSON, or chapter citations.
- Fewer than five verifiable cards: **block** literature chapter write. Do not pad with generate-as-lit or gold paste.
- Checking is a human action. Auto-check-all is not V1 success.

### 8.3 Export (frozen)

Checked cards export to **either or both**:

- `refs.bib` (BibTeX)
- CSL-JSON

Export contains **only** checked cards. Empty `checked_ids` → empty export; chapter write still blocked.

Later export/docx may render References from this export. It must not invent extra works.

### 8.4 Chapter write gate (frozen)

Literature into chapters is allowed iff **all** of:

1. `session.design.status === "confirmed"`
2. ≥5 checkbox cards were shown
3. The citations being written are in `checked_ids` / the export
4. Each cited work still has verifiable title / author / year / DOI or link

Otherwise do not write `lit_review` / References as if a bibliography existed.

This gate does **not** skip `dataAttached` or PREWRITE-PAUSE for estimate. It is additional for literature text.

### 8.5 mailto polite pool (frozen)

V1 HTTP User-Agent for OpenAlex, Crossref, and S2 **must** include a `mailto:` of a project contact (Crossref / OpenAlex polite-pool rule). Requests share one **polite pool**: identify the product, do not hammer, reuse the same mailto across FD Dataverse and FL searches.

G0 does not pick the address and does not commit secrets. `mailto:dev@local` is **not** the production pool; later slices replace it with a real project contact without putting credentials in git.

### 8.6 V1 refusals (frozen)

| Refusal | Frozen |
|---|---|
| Elicit | Not a V1 source. |
| 知网爬 | Not a V1 source. No crawl. |
| Consensus-as-chapter | Consensus output must not be pasted as a chapter. |
| generate-as-lit | Forbidden. |
| Gold biblio paste | Forbidden as acceptance. |
| Mock corpus as user bibliography | Forbidden as V1 success. |

---

## 9. Acceptance criteria (DECIDE-7; verbatim)

G0 does not add tests. Later FD / FL slices **must** implement and show these acceptance criteria. Text below is **verbatim** from Decide (via Firstmate). Do **not** evaluate by reading gold chapter bodies or gold bibliographies.

1. After design confirm: where/how find-data plan + ≥1 real candidate (not only classic-5 id)
2. Fixture may appear as candidate; without that id still show external path (Dataverse etc.)
3. Lit: verifiable title/author/year/DOI or link; no gold biblio paste
4. CK still title→propose DiD first (defer to infer-design; do not contradict)

### 9.1 How later slices bind those bullets (not substitutes)

| # | Gate reading | Fail (unacceptable substitute) |
|---|---|---|
| 1 | After `session.design` confirm: emit a **where/how** plan (FD + R-sources) **and** ≥1 **real** candidate in the §5 shape. A classic-5 id without `url_or_fixture` does not count. | Plan without confirm; id-only chip as the only hit; auto-attach; gold-body read. |
| 2 | Fixture **may** be listed (`ck1994_long`, wage1, `barro1991_growth`, …). If that id is renamed/removed/absent, still show the **external** path (Dataverse, Card zip, IPUMS, WDI, FRED per R-sources). | Fail closed when fixture missing; treat fixture as answer key; hide Dataverse because a catalog id existed. |
| 3 | Each literature card has verifiable **title / author / year / DOI or link** from FL search. No gold biblio paste into chapters or `literature_entries`. | generate-as-lit; mock/gold biblio as success; cards with title only and no DOI/link. |
| 4 | Card–Krueger class **title** still goes **title → propose DiD** (treated×period) **before** ck attach, per `docs/infer-design-contract.md` §8 bullet 1. This contract lists ck fixture + Card zip **after** confirm, as candidates. | Propose DiD from catalog id; skip infer-design; FIND-DATA sets `allow_did`; contradict DECIDE-6. |

OLS remains the default when DiD is not allowed (**infer-design**). Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block. This file does not change those rules.

**Research V1 extras later slices also owe** (not substitutes for the four bullets): FD Dataverse + fixtures; R-sources table; candidate shape; FL three-source search + DOI dedupe; R-lit-bar five steps; no Elicit / 知网爬 / Consensus-as-chapter.

---

## 10. Later parallel slices (do not implement in G0)

G0 owns **only** `docs/find-data-lit-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **FD-BE-plan** | Confirmed design facets → find-data **plan** (where/how) + R-sources `route_family` | Attach / `dataAttached`, catalog auto-select, `allow_did`, chapter bodies, FL ownership |
| **FD-BE-candidates** | Dataverse search + fixture candidates + R-sources external paths; emit §5 objects; ≥1 real candidate | Confirm-attach, classic-5 CSV bytes, infer-design propose/confirm, gold bodies |
| **FD-FE-cards** (optional) | Show plan + candidate cards (not as the user’s study) | Backend routes, Table1 / equation pause UI, auto-check attach |
| **FL-BE-search** | OpenAlex + Crossref + S2 query from confirmed design; mailto polite pool | generate-as-lit, Elicit/知网/Consensus, mock-as-success, chapter write |
| **FL-BE-dedupe** | DOI dedupe across the three sources | Ranking ownership of FD, attach, gold biblio |
| **FL-FE-cards** | ≥5 checkbox cards before write; checked set | Backend search ownership, PREWRITE-PAUSE flags, estimate |
| **FL-BE-export** | checked → `refs.bib` or CSL-JSON; chapter write may consume **only** this export | Inventing extra works; docx math (WORD-FIX); six-chapter fill from unchecked hits |

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

**FD-FE-cards / FL-FE-cards alignment (frozen):** optional chrome. Absence of the cards UI does not waive backend gates (plan + real candidates; ≥5 verifiable hits + checked export before literature write).

DC-BE-suggest (data-completion) may still rank classic-5 against the confirmed design. FIND-DATA **extends** that list with Dataverse + R-sources external paths. Suggest alignment is named only. **Do not merge** those branches in G0. Classic-5 ranking remains **candidates**, never answer key.

---

## 11. Concurrent write-sets (stay out)

| External slice | Lives at | This contract must not touch |
|---|---|---|
| **INFER-DESIGN** | `docs/infer-design-contract.md`; `session.design`; INF-BE-propose / INF-BE-confirm | Propose/confirm ownership, DiD permission rewrite, catalog-token `allow_did` revival. **Cite and defer** on CK title→propose DiD. |
| **DATA-COMPLETE** | `docs/data-completion-contract.md`; `dataAttached`; DC-BE-attach / DC-FE-\* | Confirm-attach, upload readiness, attach-panel chrome. Suggest **alignment** is named only (§10). **Do not merge** those branches in G0. |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision`; `docs/api/prewrite-confirm.md` | Implementing those flags, freeze/reveal, estimate-prep UI |
| **DID-NARROW / DID-BE-\*** | `docs/did-narrow-exception-contract.md`; infer-design §7 | Merging those branches; setting DiD from a FIND candidate |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking ids are cited only. |
| **OLS lock** | `agent/engine/ols_lock.py`; generate-chapter / estimate / prompts; issue #24 | Rewriting the lock into general TWFE; sanitizer / prompt-lock edits |
| **HET-CODE-EXPORT** | Heterogeneity × interaction hard-block | `educ×region` policy ownership, results-chapter lock |
| **WORD-FIX** | docx math export samples | Export nodes, math samples, chapter body fill |
| **Card canonical** | `/demos/card`, ADR-0015 | Teaching seed, Evidence Lab |
| **ADR-0004 / 0009 / 0011 literature nodes** | `search_literature`, citation graph, Apodex bypass | Replacing those modules in G0; treating mock/Apodex as R-lit-bar success |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `session.design`, `dataAttached`, snapshot `dataset`, PREWRITE-PAUSE flag names, existing Crossref/S2 adapters as **implementation targets**. Add `session.find_data` and `session.find_lit` — do not replace `session.design` or `dataAttached`, and do not treat catalog id as a real candidate.

---

## 12. G0 done rule

- File present: `docs/find-data-lit-contract.md`
- Folded: DECIDE-7 order / locks / four accept bullets (verbatim, §0 + §9); title → propose → confirm → **find-data plan + candidates** → attach → prewrite; **FD** design facets → Dataverse + fixture candidates; **R-sources** route table (educ/wage → IPUMS/wage1; minwage → ck fixture + Card zip; growth → WDI/barro; macro → FRED; else Dataverse); **candidate shape** (`source_id`, `title`, `url_or_fixture`, `license`, `suggested_cols`, `design_fit`); **FL** OpenAlex + Crossref + S2 + DOI dedupe; **R-lit-bar** replaces generate-as-lit (five steps; ≥5 checkbox cards; checked → `refs.bib` or CSL-JSON; mailto polite pool); no Elicit / 知网爬 / Consensus-as-chapter in V1; fixtures/catalog = candidates only, never answer key; CK title→propose DiD deferred to infer-design; **no gold biblio paste**; **no gold body reads**
- No application code, API routes, frontend, fixtures, OpenAPI, or OLS-lock change in G0
- No merge of DATA-COMPLETE / DID-NARROW / INF implementation branches
- No pull request from this slice
- Later slices cite this file; they do not rewrite §2–§8 without a new serial contract

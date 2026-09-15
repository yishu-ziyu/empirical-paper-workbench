# Bryce tools contract (four IN; DECIDE-8)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-BRYCE-G0` · slice **BRYCE-G0**  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `feat/fm-e-build-did-spec-recut-1` @ `bf6957150713d9d8ff3ae72379d4233e5bd9b253`  
Design input: **DECIDE-8** acceptance from Decide (via Firstmate) — four Bryce-adjacent tools **IN** as thin mappings onto existing formal surfaces; four named dumps **OUT**  
Sister contracts (cited, not merged): `docs/infer-design-contract.md` (`FM-E-BUILD-INFER-DESIGN-1` INF-G0 / DECIDE-6), `docs/find-data-lit-contract.md` (`FM-E-BUILD-FIND-DATA-LIT` FD-G0), `docs/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Authority: this file freezes the DECIDE-8 **IN set**, **OUT set**, **order relative to DECIDE-6/7**, and **accept bullets** below. Later BE slices implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so later BRYCE-BE-\* slices can run without standing up a parallel Bryce product, a second literature pipeline, a Stata-default cleaner, a p-hack helper, or a sprawling eval farm. Acceptance is the DECIDE-8 bullets in §7 — **not** gold-body reads, **not** a Paper-WorkFlow dump, and **not** a full AER-Skills dump.

**BE slices are held.** Do not start BRYCE-BE-\* until the Research **INTEGRATE** brief lands with pointer names. Placeholder ids below (`BRYCE-BE-lit-thin`, `BRYCE-BE-winsor`, `BRYCE-BE-aer-gates`, `BRYCE-BE-top5-eval`) are **names only**. G0 does not schedule, implement, or merge them.

---

## 0. Product-line lock — DECIDE-8

**DECIDE-8 (frozen; Decide via Firstmate).** Encode the following **IN / OUT**:

**Four picks IN:**

1. **lit-review thin into `find_lit`** — do not stand up a parallel lit pipeline; thin/reuse the existing `find_lit` (OpenAlex+Crossref+S2 cards, checkbox, bib) path.
2. **pywinsor2 cleaning** — winsorize/clean step as a named cleaning tool (Python `pywinsor2`), not a Stata-only default.
3. **AER-Skills distilled gates** — distill AER-Skills into product gates/checks (acceptance-style), not a full skill dump.
4. **top5 eval only** — evaluation/benchmark scope limited to a top-5 set; no sprawling eval farm in V1.

**Explicitly OUT:**

- Paper-WorkFlow dump (do not import wholesale workflow dump)
- p-hack feature (no p-hacking helper)
- stata-code default (Stata is export option, not the default cleaning/codegen path for this slice)
- ppt / 小红书 (xhs) outputs

**Order relative to DECIDE-6 / DECIDE-7 (do not reorder):**

```
title → design → confirm → find data/lit → attach → prewrite
```

Bryce tools **do not** insert a new station before confirm-design. They **do not** skip attach. They **do not** replace PREWRITE-PAUSE. Cleaning sits on the existing post-attach clean path. Distilled AER gates fire on confirm / prewrite / identification / robustness / literature-write / export — they are checks, not a second workflow.

In scope: the formal econpaper paper path — the same product line as `docs/infer-design-contract.md` and `docs/find-data-lit-contract.md`.

Out of product line for this contract (do not extend, re-label, or treat as Bryce V1 success):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`, ADR-0015)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets **outside** the named top-5 set (including `agent/eval/tasks/undergrad_did_01` as a farm seed)
- Agent spike (`/spike`), first-value marketing review, flow-sketch / draft-product chrome
- Sketch-only sample names (`sample_wage.csv`, `sample_panel_mini.csv`, `wage_panel.csv`)
- Catalog identity alone (`ck1994`, `ck1994_long`, `minimum-wage-employment`, `barro1991_growth`, …) as an answer key **or** as the eval set
- Unconfirmed `session.design` (`missing` / `draft`)
- A second literature agent beside `session.find_lit` / **FL** / **R-lit-bar**
- AERS / AER-Skills file dump into `.agents/skills/`
- Paper-WorkFlow / stata-code / p-hack / ppt / xhs as V1 surfaces

`session.design` (infer-design), `session.find_data` / `session.find_lit` (FIND), `dataAttached` (data-completion), and `table1Confirmed` / `specConfirmed` (PREWRITE-PAUSE) stay **different** gates. This contract does not propose or confirm a design, does not attach a dataset, does not skip confirm-attach, and does not replace those flags. It **does** freeze how the four IN picks sit on those surfaces.

DiD permission stays in `docs/infer-design-contract.md` §7. R-lit-bar stays in `docs/find-data-lit-contract.md` §7–§8. This file must not reopen catalog-token `allow_did`, must not contradict title-first CK propose, and must not replace generate-as-lit with a second lit dump.

---

## 1. Purpose and non-goals

### 1.1 Purpose (frozen)

On the formal path, DECIDE-8 only:

1. **Thins** any Bryce “lit-review” capability into existing **`session.find_lit`** (**FL** + **R-lit-bar**). Same OpenAlex + Crossref + S2 search, DOI dedupe, ≥5 checkbox cards, checked → `refs.bib` or CSL-JSON.
2. **Names** winsorize/clean as a **Python `pywinsor2` cleaning tool** on the existing `CleaningStep` path (ADR-0002 outliers / winsor step). Stata `winsor2` / `stata-code` is not the default.
3. **Distills** AER-Skills into a **small set of product gates** (acceptance-style checks on design confirm, cleaning provenance, PREWRITE-PAUSE, identification/robustness, literature write, export). Not a skill dump.
4. **Limits** V1 evaluation/benchmark to a **named top-5 set**. No eval farm. Pointer names wait for the Research INTEGRATE brief.

### 1.2 Non-goals (frozen)

This contract does **not**:

- Propose or confirm `session.design` (INF-BE-propose / INF-BE-confirm)
- Replace **FD** / **R-sources** / candidate shape / **FL** / **R-lit-bar**
- Attach a dataset or set `dataAttached`
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, `generate_title` / `state.title_chapter`, or export as G0 work
- Import Paper-WorkFlow wholesale (prompts, graphs, agents, PPT/xhs emitters, p-hack helpers)
- Dump AER-Skills / AERS into `.agents/skills/` or a parallel review agent
- Make Stata the default cleaning or codegen path
- Add ppt / pptx / 小红书 (xhs) export
- Add a p-hacking / specification-search / star-hunting helper
- Grow `agent/eval/tasks/` into a farm; treat `undergrad_did_01` or Card 1995 as the V1 Bryce eval set
- Treat `classic-5` catalog ids as the top-5 eval set or as gold bodies
- Merge DATA-COMPLETE / DID / INF / FD / FL implementation branches
- Implement application code, API routes, OpenAPI shapes, fixtures, or frontend chrome (BRYCE-G0 is markdown only)
- Start BRYCE-BE-\* before the Research INTEGRATE brief

`TITLE/TOPIC` here is the session-start title already consumed by infer-design. Bryce tools read **confirmed** `session.design` and the FIND / clean / prewrite / export surfaces that already exist. They do not invent a Bryce station that jumps the DECIDE-6/7 order.

---

## 2. How the four picks map onto existing surfaces

Product surfaces named in DECIDE-6/7 and this file:

| Surface | Contract / object | Bryce pick that may touch it later |
|---|---|---|
| **infer-design** | `docs/infer-design-contract.md`; `session.design` | AER distilled gates (design confirmed; method + interactions stated). Not a new design engine. |
| **find-data-lit** | `docs/find-data-lit-contract.md`; `session.find_data`; **`session.find_lit`** | **lit-review thin** (must reuse `find_lit`). AER distilled gate on literature write (R-lit-bar). |
| **prewrite** | PREWRITE-PAUSE `table1Confirmed` then `specConfirmed`; `run_prewrite`; `identification_verify`; `robustness_check` | AER distilled gates (Table 1, spec, identification, robustness). Cleaning named tool runs **before** prewrite, after attach. |
| **export** | `GET /code-export` (`py` / `do` / `R` / `m`); `GET /doc-export` (`tex` / `pdf` / `docx`); FL bib export | Code default stays Python; Stata is an **option** (`format=do`). Doc export stays tex/pdf/docx. **No** ppt / xhs. |

### 2.1 lit-review thin → `find_lit` (frozen)

| Must reuse | Must not create |
|---|---|
| `session.find_lit` (`hits[]`, `cards[]`, `checked_ids[]`, `export`) | `session.bryce_lit`, a second search agent, Paper-WorkFlow lit node, generate-as-lit |
| **FL**: OpenAlex + Crossref + S2, DOI dedupe | Elicit / 知网爬 / Consensus-as-chapter / Apodex-as-V1 |
| **R-lit-bar**: ≥5 checkbox cards; checked → `refs.bib` or CSL-JSON; mailto polite pool | Auto-check-all; gold biblio paste; mock corpus as user bibliography |
| Query from **confirmed** `session.design` facets | Title-only search that skips confirm-design |

A “lit-review” Bryce tool in V1 **is** FL + R-lit-bar, possibly with a thinner prompt/UI label. It is not a parallel pipeline.

### 2.2 pywinsor2 cleaning → existing clean path (frozen)

| Must reuse | Must not create |
|---|---|
| ADR-0002 `CleaningStep` protocol; `clean_data` orchestrator; `cleaning_report.steps` | A Stata-only cleaner as the default |
| Named outliers / winsor step (today: `OutliersStep`, StatsPAI `winsor` or pandas fallback) | Silent rewrite of design columns; undocumented cuts |
| Python **`pywinsor2`** as the named V1 winsor tool | `stata-code` / `winsor2` as the required runtime |
| Sidecar + before/after stats already required by the outliers step | A second cleaning graph imported from Paper-WorkFlow |

Attach (`dataAttached`) still happens **before** this tool runs on the session dataset. Confirm-design does not clean. FIND-DATA does not clean.

### 2.3 AER-Skills distilled gates → checks, not a dump (frozen)

Distill, do not dump. V1 gates are **acceptance checks** on objects this product already has. They are **not** a copy of AERS skill files, AERS Stage 04 prose, or an AER handbook pasted into the repo.

| Gate (distilled) | Existing surface | Fail closed if |
|---|---|---|
| Design stated and **confirmed** | infer-design `session.design.status === "confirmed"` | Draft / missing design treated as locked spec |
| Method + required interactions | infer-design §2.4; DID-BE-spec; HET hard-block | Confirmed `method=did` without treated×period; `qType=heterogeneity` without interaction |
| Data attached with auditable clean | `dataAttached` + `cleaning_report.steps` including the named pywinsor2 step | Clean skipped; Stata-only default presented as the only path |
| Table 1 then spec confirm | PREWRITE-PAUSE | Estimate / chapter write without `table1Confirmed` / `specConfirmed` |
| Identification / robustness recorded | `identification_verify`, `robustness_check` | Invented diagnostics; p-hack helper as a substitute |
| Literature from checked FL cards | R-lit-bar | generate-as-lit; gold biblio; unchecked cards in chapters |
| Export from the session | code-export + doc-export | ppt / xhs; Stata as the only codegen; export of a spec that never confirmed |

Later BRYCE-BE-aer-gates may name error codes. G0 does not add them. Absence of a dedicated “AER panel” UI does not waive the checks.

### 2.4 top-5 eval only → eval harness, not catalog (frozen)

| Is | Is not |
|---|---|
| A **named top-5 evaluation/benchmark set** for V1 | `classic-5` catalog used as an answer key |
| Scope cap: **only** that set in V1 | An eval farm under `agent/eval/tasks/` |
| Pointer names from Research INTEGRATE brief | Invented paper titles in this G0 file |
| Out of line: Card 1995 teaching case; `undergrad_did_01` as farm seed | Gold-body reads as the eval metric |

`classic-5` remains FIND/DATA-COMPLETE **candidates** (DECIDE-6/7). The top-5 **eval** set is a different object. Do not conflate them.

---

## 3. Order vs DECIDE-6 / DECIDE-7

### 3.1 Intended sequence (frozen)

DECIDE-6 (verbatim): `title/question → design propose (Y/X/interactions/method) → human confirm → data candidates → attach → prewrite pauses`

DECIDE-7 (verbatim relative to infer-design): `title → propose → confirm → find-data plan + candidates → attach → prewrite`

DECIDE-8 **does not change that order**. Mapped:

```
title/question
    → design propose                         ⇒  session.design status=draft          (infer-design)
    → human confirm                           ⇒  session.design status=confirmed
    → find-data plan + candidates            ⇒  session.find_data (FD + R-sources)
    → find-lit (FL + R-lit-bar)            ⇒  session.find_lit   (Bryce lit-review THINS HERE)
    → attach                                 ⇒  dataAttached
    → named pywinsor2 clean                 ⇒  cleaning_report.steps (after attach)
    → prewrite pauses                        table1Confirmed then specConfirmed
                                                + distilled AER gates on those flags
                                                + identification / robustness
    → chapter write / export                 doc: tex/pdf/docx; code: py default, Stata option
```

FIND-LIT remains **after design confirm** and **before any literature chapter write**, as in find-data-lit §6. It does not sit in the attach slot. Cleaning does not sit before confirm-design.

### 3.2 Rules

1. **Confirm-design first.** Bryce tools must not treat missing or draft `session.design` as locked.
2. **FIND-DATA still does not attach.** `dataAttached` still first for data.
3. **pywinsor2 runs after attach**, on the session dataset, as a named `CleaningStep`. It does not attach, does not confirm design, and does not set PREWRITE-PAUSE flags.
4. **PREWRITE-PAUSE still owns** `table1Confirmed` and `specConfirmed`. Distilled AER gates **read** those flags; they do not replace them.
5. **CK DiD propose stays on infer-design.** Title/question only → propose DiD + treated×period **before** ck attach.
6. **Fixtures never answer key.** classic-5 is not the top-5 eval set and not gold.
7. **Independence.** Checking lit cards does not set `dataAttached`. Cleaning does not confirm spec. Export does not skip pauses.

### 3.3 What may happen before confirm-design

- Infer-design draft propose / edit
- Opening an attach panel in **candidates-only** mode (no FD plan as authoritative match)

What must not happen before confirm-design:

- Authoritative FIND-DATA / FIND-LIT / Bryce lit-review as a confirmed-design match
- pywinsor2 presented as having cleaned “the study dataset” when nothing is attached
- AER gates treated as passed
- Catalog → `allow_did` or catalog → locked spec
- `table1Confirmed` / `specConfirmed` / estimate / gold biblio paste / eval-farm gold bodies

---

## 4. Four picks IN (detail)

### 4.1 lit-review thin into `find_lit`

**IN.** Thin/reuse. Implementation target for later `BRYCE-BE-lit-thin` is `agent/find_lit/` + R-lit-bar chapter gate — not a new package.

Must:

- Search OpenAlex + Crossref + S2 from confirmed design facets
- DOI-dedupe; ≥5 verifiable checkbox cards before literature chapter write
- Export **checked** cards only to `refs.bib` or CSL-JSON
- Fail closed if fewer than five verifiable cards (do not pad with generate-as-lit)

Must not:

- Stand up a parallel lit pipeline, Paper-WorkFlow lit dump, or second `literature_entries` writer
- Skip confirm-design
- Write chapters from unchecked cards
- Call Elicit / 知网 / Consensus as V1 success

### 4.2 pywinsor2 cleaning

**IN.** Named Python cleaning tool.

Must:

- Expose winsorize/clean as a **named** step on the ADR-0002 pipeline (outliers / winsor family)
- Use **Python `pywinsor2`** as the V1 tool identity (not “run Stata winsor2”)
- Keep before/after stats and sidecar auditability
- Protect research-design columns (do not winsorize treated/period/id/time as a silent default)

Must not:

- Require `stata-code` or a `.do` winsor2 as the default cleaner
- Replace the whole 8-step pipeline with a Paper-WorkFlow clean dump
- Run before `dataAttached`
- Present Card teaching extract vs winsor sidecar confusion as a win (ADR-0015 extract path stays teaching-only)

G0 does not pick cuts, API field names, or a PyPI pin. Later `BRYCE-BE-winsor` does, after INTEGRATE pointer names.

### 4.3 AER-Skills distilled gates

**IN.** Distill into product checks.

Must (V1 distilled set — this is the dump ceiling, not a floor to expand):

1. Confirmed `session.design` before estimate / spec lock
2. Required interactions present (DiD treated×period; HET interaction) or **hard block**
3. `dataAttached` + named cleaning step recorded before Table 1 / spec confirm
4. `table1Confirmed` then `specConfirmed` before estimate admission
5. Identification / robustness results recorded when those nodes run; do not invent
6. Literature chapter write only through R-lit-bar
7. Export only tex/pdf/docx + code-export languages already in product; no ppt/xhs

Must not:

- Copy AER-Skills / AERS / Paper-WorkFlow into `.agents/skills/` as V1
- Add a parallel “AER reviewer” that bypasses PREWRITE-PAUSE
- Treat a skill-file presence test as acceptance
- Add p-hack / spec-search as an “AER robustness” feature (that pick is **OUT**)

### 4.4 top-5 eval only

**IN.** Scope cap.

Must:

- Keep V1 Bryce evaluation/benchmark to **one named top-5 set**
- Wait for Research INTEGRATE brief for the five pointer names
- Evaluate later BE slices by the §7 bullets, **not** by gold-body reads

Must not:

- Add a sprawling eval farm (`agent/eval/tasks/*` growth, extra personas, extra gold packets)
- Use Card 1995 or `undergrad_did_01` as a substitute for the named set
- Use classic-5 catalog identity as the eval answer key
- Treat “more tasks” as a quality improvement in V1

---

## 5. Explicitly OUT (frozen)

| OUT | Frozen refusal |
|---|---|
| **Paper-WorkFlow dump** | Do not import wholesale workflow dump (agents, graphs, prompts, emitters). Cite nothing from that dump as a V1 win path. |
| **p-hack feature** | No specification-search helper, no star-hunting, no “try controls until significant.” Robustness stays the existing named suite, not a search. |
| **stata-code default** | Stata is an **export option** (`code-export?format=do`). Default cleaning/codegen for this slice is **Python** (`pywinsor2` + `format=py`). `docs/dependencies.md` already rejects `stata-code` as a retained runtime. |
| **ppt / 小红书 (xhs)** | No pptx, no xhs/social copy as product outputs. Doc export remains `tex` / `pdf` / `docx`. |

OUT items must not re-enter as “optional chrome” in V1. A later contract would be required.

---

## 6. Named objects (reuse, do not fork)

G0 adds **no** new snapshot / OpenAPI objects.

| Object | Owner | Bryce G0 |
|---|---|---|
| `session.design` | infer-design | Read after confirm. Do not write. |
| `session.find_data` | find-data-lit | Untouched (not a Bryce pick). |
| `session.find_lit` | find-data-lit | **Reuse** for lit-review thin. |
| `dataAttached` / snapshot `dataset` | data-completion | Read after attach for cleaning. Do not set. |
| `cleaning_report.steps` | ADR-0002 | Later winsor slice names `pywinsor2` here. |
| `table1Confirmed` / `specConfirmed` | PREWRITE-PAUSE | Distilled AER gates read; do not own. |
| `find_lit.export` | FL-BE-export | Bib/CSL only from checked cards. |
| code-export / doc-export | existing routers | Python default; Stata option; no ppt/xhs. |

Must not live on a Bryce object as a win path: catalog id, `allow_did`, gold-body hashes, gold biblio, Paper-WorkFlow dump, p-hack payloads, ppt/xhs blobs, unconfirmed `session.design`.

---

## 7. Acceptance criteria (DECIDE-8)

G0 does not add tests. Later BRYCE-BE-\* slices **must** implement and show these acceptance criteria. Do **not** evaluate by reading gold chapter bodies or gold bibliographies. Placeholder ids are frozen for later BE; **held** until Research INTEGRATE brief.

### 7.1 BRYCE-BE-lit-thin

- Lit-review is the existing `find_lit` path: OpenAlex + Crossref + S2, DOI dedupe, checkbox cards, bib/CSL from **checked** cards.
- No second literature pipeline. No generate-as-lit. No gold biblio paste.
- Unconfirmed design cannot rank as an authoritative lit-review success.

**Fail (unacceptable substitute):** Paper-WorkFlow lit dump; Elicit/知网/Consensus; a new `session.bryce_lit` that writes chapters; skip R-lit-bar.

### 7.2 BRYCE-BE-winsor

- Winsorize/clean is a **named** Python `pywinsor2` tool on the cleaning pipeline after attach.
- Stata `winsor2` / `stata-code` is not the default.
- Design columns are not silently winsorized. Before/after stats remain.

**Fail (unacceptable substitute):** Stata-only default cleaner; undocumented pandas one-off presented as the named tool; clean-before-attach; Paper-WorkFlow clean dump.

### 7.3 BRYCE-BE-aer-gates

- AER-Skills appear only as **distilled gates** on infer-design / find-lit / prewrite / identification / robustness / export (§2.3 / §4.3).
- No full skill dump. No p-hack feature dressed as robustness.

**Fail (unacceptable substitute):** `.agents/skills/` dump; bypass of `table1Confirmed` / `specConfirmed`; catalog → locked spec; p-hack helper.

### 7.4 BRYCE-BE-top5-eval

- V1 eval/benchmark is **only** the named top-5 set (pointer names from INTEGRATE brief).
- No sprawling eval farm. classic-5 catalog ≠ eval set. Card / `undergrad_did_01` are not the V1 set.

**Fail (unacceptable substitute):** adding many `agent/eval/tasks/*`; gold-body rubric as the only metric; catalog id as answer key.

OLS remains the default when DiD is not allowed (**infer-design**). Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block. This file does not change those rules.

---

## 8. Later parallel slices (held; do not implement in G0)

G0 owns **only** `docs/bryce-tools-contract.md`.

**Held until Research INTEGRATE brief lands with pointer names.** Do not start, merge, or partially land these slices in G0.

| Slice (placeholder id) | Owns (when unblocked) | Must not write |
|---|---|---|
| **BRYCE-BE-lit-thin** | Thin lit-review into `session.find_lit` / `agent/find_lit` | Parallel lit pipeline, generate-as-lit, FD ownership, attach, PREWRITE-PAUSE flags |
| **BRYCE-BE-winsor** | Named `pywinsor2` cleaning step + report | Stata-default cleaner, classic-5 CSV bytes, infer-design, ppt/xhs |
| **BRYCE-BE-aer-gates** | Distilled gates/checks on existing flags and nodes | AER-Skills dump, p-hack feature, DID unlock rewrite, gold bodies |
| **BRYCE-BE-top5-eval** | Bind V1 eval to the named top-5 set | Eval farm; treating catalog or Card as the set |

Slices stay **write-set-disjoint** when they eventually run. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

Optional FE chrome (labels on FIND-LIT cards, a named clean step in the clean wizard, a gate checklist) does not waive backend gates. Absence of that chrome does not change the IN/OUT set.

---

## 9. Concurrent write-sets (stay out)

| External slice | Lives at | This contract must not touch |
|---|---|---|
| **INFER-DESIGN** | `docs/infer-design-contract.md`; `session.design`; INF-BE-propose / INF-BE-confirm | Propose/confirm ownership, DiD permission rewrite, catalog-token `allow_did` revival |
| **FIND-DATA-LIT** | `docs/find-data-lit-contract.md`; FD / FL / R-lit-bar | Replacing FL sources; generate-as-lit revival. **Cite and reuse** `find_lit`. |
| **DATA-COMPLETE** | `docs/data-completion-contract.md`; `dataAttached`; DC-BE-attach / DC-FE-\* | Confirm-attach, upload readiness, attach-panel chrome. **Do not merge** those branches in G0. |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision`; `docs/api/prewrite-confirm.md` | Implementing those flags, freeze/reveal, estimate-prep UI |
| **DID-NARROW / DID-BE-\*** | `docs/did-narrow-exception-contract.md`; infer-design §7 | Merging those branches; setting DiD from a Bryce tool |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking ids are cited only. |
| **OLS lock** | `agent/engine/ols_lock.py`; generate-chapter / estimate / prompts; issue #24 | Rewriting the lock into general TWFE |
| **HET-CODE-EXPORT** | Heterogeneity × interaction hard-block | `educ×region` policy ownership |
| **WORD-FIX** | docx math export samples | Export nodes, math samples, chapter body fill |
| **Card canonical** | `/demos/card`, ADR-0015 | Teaching seed, Evidence Lab |
| **ADR-0002 cleaning** | `docs/adr/0002-cleaning-pipeline-step-protocol.md` | Rewriting the protocol in G0; Stata-default swap |
| **AERS / stata-code (rejected deps)** | `docs/dependencies.md` | Re-retaining them as runtime; skill dump |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `session.design`, `session.find_lit`, `dataAttached`, `cleaning_report`, PREWRITE-PAUSE flag names, `code-export` / `doc-export`. Do not replace those objects with a Bryce-named duplicate.

---

## 10. G0 done rule

- File present: `docs/bryce-tools-contract.md`
- Folded: DECIDE-8 four IN (lit-review thin into `find_lit`; pywinsor2 cleaning; AER-Skills distilled gates; top-5 eval only); four OUT (Paper-WorkFlow dump; p-hack; stata-code default; ppt / xhs); order **title → design → confirm → find data/lit → attach → prewrite** vs DECIDE-6/7; mapping onto infer-design / find-data-lit / prewrite / export; accept bullets with placeholder ids `BRYCE-BE-lit-thin`, `BRYCE-BE-winsor`, `BRYCE-BE-aer-gates`, `BRYCE-BE-top5-eval`; **BE slices held** until Research INTEGRATE brief with pointer names; **no gold body reads**
- No application code, API routes, frontend, fixtures, OpenAPI, skills dump, or eval-farm change in G0
- No merge of DATA-COMPLETE / DID / INF / FD / FL implementation branches
- No pull request from this slice
- Later slices cite this file; they do not rewrite §2–§5 without a new serial contract

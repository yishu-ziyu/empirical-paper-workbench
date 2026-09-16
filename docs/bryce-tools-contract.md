# Bryce tools contract (four IN; DECIDE-8)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-BRYCE-G0` · slice **BRYCE-G0** (pointers folded for later `FM-E-BUILD-BRYCE-1`)  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `feat/fm-e-build-did-spec-recut-1` @ `bf6957150713d9d8ff3ae72379d4233e5bd9b253`  
Design input: **DECIDE-8** acceptance from Decide (via Firstmate) — four Bryce-adjacent tools **IN** as thin mappings onto existing formal surfaces; four named dumps **OUT**. Research **INTEGRATE** + `FM-E-BUILD-BRYCE-1` supply the **pointer names** in §0.1.  
Sister contracts (cited, not merged): `docs/infer-design-contract.md` (`FM-E-BUILD-INFER-DESIGN-1` INF-G0 / DECIDE-6), `docs/find-data-lit-contract.md` (`FM-E-BUILD-FIND-DATA-LIT` FD-G0), `docs/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Authority: this file freezes the DECIDE-8 **IN set**, **OUT set**, **order relative to DECIDE-6/7**, the **INTEGRATE pointers**, and **accept bullets** below. Later BE slices (`FM-E-BUILD-BRYCE-1`) implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so later **FL-BE-reuse** / **CL-BE-winsor** / **NORMS-BE** / **EVAL-top5** can run without standing up a parallel Bryce product, a second literature pipeline, a Stata-default cleaner, a p-hack helper, a Claude skill runner, or a sprawling eval farm. Acceptance is the DECIDE-8 bullets in §7 — **not** gold-body reads, **not** a Paper-WorkFlow dump, and **not** a full AER-Skills dump.

**G0 still does not implement BE.** INTEGRATE pointer names have landed (§0.1). Do not start those slices in this write-set. G0 aliases (`BRYCE-BE-lit-thin`, `BRYCE-BE-winsor`, `BRYCE-BE-aer-gates`, `BRYCE-BE-top5-eval`) are **retired as slice ids**; they map 1:1 onto the INTEGRATE tokens. Later work cites the INTEGRATE names.

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

### 0.1 Research INTEGRATE pointers (frozen; `FM-E-BUILD-BRYCE-1`)

Research INTEGRATE + `FM-E-BUILD-BRYCE-1` freeze these **pointer names**. They must appear. They do **not** change DECIDE-8 IN/OUT. G0 does not add the files or code they name.

| Token | Frozen meaning | DECIDE-8 pick | Retired G0 alias |
|---|---|---|---|
| **FL-BE-reuse** | Thin wrap `fetch_papers.py` (OpenAlex + Crossref + S2, DOI dedupe) into existing `find_lit`. Checkbox before write. | lit-review thin into `find_lit` | `BRYCE-BE-lit-thin` |
| **CL-BE-winsor** | pip `pywinsor2`; named `clean_winsor`; `cuts=(1,99)`; **continuous only**; auditable. | pywinsor2 cleaning | `BRYCE-BE-winsor` |
| **NORMS-BE** | Distill AER rules into `design_gates.yaml` + `chapter_gates.yaml`; hook **propose** and **write**. **No** Claude skill runner. | AER-Skills distilled gates | `BRYCE-BE-aer-gates` |
| **EVAL-top5** | Optional **submodule** eval only. Never a product catalog answer key. | top5 eval only | `BRYCE-BE-top5-eval` |

`fetch_papers.py`, `clean_winsor`, `design_gates.yaml`, and `chapter_gates.yaml` are **later-slice implementation targets**. Their absence from this G0 tree is not a defect. Claude skill runner / `.agents/skills/` dump remains **OUT**.

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
- AERS / AER-Skills file dump into `.agents/skills/` or a Claude skill runner
- Paper-WorkFlow / stata-code / p-hack / ppt / xhs as V1 surfaces

`session.design` (infer-design), `session.find_data` / `session.find_lit` (FIND), `dataAttached` (data-completion), and `table1Confirmed` / `specConfirmed` (PREWRITE-PAUSE) stay **different** gates. This contract does not propose or confirm a design, does not attach a dataset, does not skip confirm-attach, and does not replace those flags. It **does** freeze how the four IN picks sit on those surfaces.

DiD permission stays in `docs/infer-design-contract.md` §7. R-lit-bar stays in `docs/find-data-lit-contract.md` §7–§8. This file must not reopen catalog-token `allow_did`, must not contradict title-first CK propose, and must not replace generate-as-lit with a second lit dump.

---

## 1. Purpose and non-goals

### 1.1 Purpose (frozen)

On the formal path, DECIDE-8 only:

1. **Thins** any Bryce “lit-review” capability into existing **`session.find_lit`** (**FL-BE-reuse**: thin wrap `fetch_papers.py` into **FL** + **R-lit-bar**). OpenAlex + Crossref + S2, DOI dedupe, checkbox **before write**, checked → `refs.bib` or CSL-JSON.
2. **Names** winsorize/clean as **`clean_winsor`** (**CL-BE-winsor**: pip `pywinsor2`, `cuts=(1,99)`, continuous only, auditable) on the existing `CleaningStep` path. Stata `winsor2` / `stata-code` is not the default.
3. **Distills** AER-Skills into **`design_gates.yaml` + `chapter_gates.yaml`** (**NORMS-BE**), hooked on **propose** and **write**. Not a skill dump. **No** Claude skill runner.
4. **Limits** V1 evaluation/benchmark to **EVAL-top5**: optional submodule eval only. Never a product catalog answer key. No eval farm.

### 1.2 Non-goals (frozen)

This contract does **not**:

- Propose or confirm `session.design` (INF-BE-propose / INF-BE-confirm)
- Replace **FD** / **R-sources** / candidate shape / **FL** / **R-lit-bar**
- Attach a dataset or set `dataAttached`
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, `generate_title` / `state.title_chapter`, or export as G0 work
- Import Paper-WorkFlow wholesale (prompts, graphs, agents, PPT/xhs emitters, p-hack helpers)
- Dump AER-Skills / AERS into `.agents/skills/` or run a **Claude skill runner**
- Make Stata the default cleaning or codegen path
- Add ppt / pptx / 小红书 (xhs) export
- Add a p-hacking / specification-search / star-hunting helper
- Grow `agent/eval/tasks/` into a farm; treat `undergrad_did_01` or Card 1995 as the V1 Bryce eval set
- Treat `classic-5` catalog ids as **EVAL-top5** or as gold bodies; vendor the eval set into the product catalog
- Merge DATA-COMPLETE / DID / INF / FD / FL implementation branches
- Implement application code, API routes, OpenAPI shapes, fixtures, yaml gates, `fetch_papers.py`, or frontend chrome (BRYCE-G0 is markdown only)
- Land **FL-BE-reuse** / **CL-BE-winsor** / **NORMS-BE** / **EVAL-top5** in this G0 write-set

`TITLE/TOPIC` here is the session-start title already consumed by infer-design. Bryce tools read **confirmed** `session.design` and the FIND / clean / prewrite / export surfaces that already exist. They do not invent a Bryce station that jumps the DECIDE-6/7 order.

---

## 2. How the four picks map onto existing surfaces

Product surfaces named in DECIDE-6/7 and this file:

| Surface | Contract / object | INTEGRATE slice | Bryce pick |
|---|---|---|---|
| **infer-design** | `docs/infer-design-contract.md`; `session.design` | **NORMS-BE** `design_gates.yaml` hooked on **propose** | AER distilled gates. Not a new design engine. |
| **find-data-lit** | `docs/find-data-lit-contract.md`; `session.find_data`; **`session.find_lit`** | **FL-BE-reuse** thin wrap `fetch_papers.py` into `find_lit`; checkbox before write. **NORMS-BE** literature write via R-lit-bar | lit-review thin. No parallel pipeline. |
| **prewrite** | PREWRITE-PAUSE `table1Confirmed` then `specConfirmed`; `run_prewrite`; `identification_verify`; `robustness_check` | **NORMS-BE** `chapter_gates.yaml` hooked on **write**; **CL-BE-winsor** `clean_winsor` **before** prewrite, after attach | AER distilled gates + named Python clean. |
| **export** | `GET /code-export` (`py` / `do` / `R` / `m`); `GET /doc-export` (`tex` / `pdf` / `docx`); FL bib export | (no new Bryce export slice) | Python default; Stata **option**. **No** ppt / xhs. |
| **eval** | not the product catalog | **EVAL-top5** optional submodule | top5 eval only; never catalog answer key. |

### 2.1 lit-review thin → `find_lit` — **FL-BE-reuse** (frozen)

| Must reuse | Must not create |
|---|---|
| `session.find_lit` (`hits[]`, `cards[]`, `checked_ids[]`, `export`) | `session.bryce_lit`, a second search agent, Paper-WorkFlow lit node, generate-as-lit |
| **FL**: OpenAlex + Crossref + S2, DOI dedupe | Elicit / 知网爬 / Consensus-as-chapter / Apodex-as-V1 |
| Thin wrap **`fetch_papers.py`** (same three sources + DOI dedupe) **into** existing `find_lit` | A standalone fetch-papers product path beside `agent/find_lit/` |
| **R-lit-bar**: checkbox cards **before write**; checked → `refs.bib` or CSL-JSON; mailto polite pool | Auto-check-all; gold biblio paste; mock corpus as user bibliography; write without checkbox |
| Query from **confirmed** `session.design` facets | Title-only search that skips confirm-design |

A “lit-review” Bryce tool in V1 **is** FL + R-lit-bar, with `fetch_papers.py` as a **thin wrap** inside `find_lit`. It is not a parallel pipeline.

### 2.2 pywinsor2 cleaning → `clean_winsor` — **CL-BE-winsor** (frozen)

| Must reuse | Must not create |
|---|---|
| ADR-0002 `CleaningStep` protocol; `clean_data` orchestrator; `cleaning_report.steps` | A Stata-only cleaner as the default |
| Named step **`clean_winsor`** (outliers / winsor family) | Silent rewrite of design / binary columns; undocumented cuts |
| pip **`pywinsor2`** as the named V1 runtime | `stata-code` / Stata `winsor2` as the required runtime |
| **`cuts=(1,99)`**; **continuous only** | Winsorizing treated/period/id/time or 0/1 indicators as a silent default |
| Sidecar + before/after stats (auditable) | A second cleaning graph imported from Paper-WorkFlow |

Attach (`dataAttached`) still happens **before** this tool runs on the session dataset. Confirm-design does not clean. FIND-DATA does not clean.

### 2.3 AER-Skills distilled gates → yaml + hooks — **NORMS-BE** (frozen)

Distill, do not dump. V1 gates are **YAML check lists** plus **hooks**, not a copy of AERS skill files, AERS Stage 04 prose, an AER handbook, or a **Claude skill runner**.

| Artifact | Hook | Existing surface | Fail closed if |
|---|---|---|---|
| `design_gates.yaml` | **propose** (infer-design propose → draft; confirm still required to lock) | `session.design` | Draft / missing design treated as locked spec; propose skips yaml |
| `design_gates.yaml` | confirmed method + required interactions | infer-design §2.4; DID-BE-spec; HET hard-block | Confirmed `method=did` without treated×period; `qType=heterogeneity` without interaction |
| `chapter_gates.yaml` | **write** (chapter generate / literature write) | PREWRITE-PAUSE; R-lit-bar; generate-chapter | Estimate / chapter write without `table1Confirmed` / `specConfirmed`; generate-as-lit |
| Distilled checks (same ceiling as before) | prewrite / identification / robustness / export | `dataAttached` + `clean_winsor` audit; `identification_verify`; `robustness_check`; code/doc export | Invented diagnostics; p-hack helper; ppt/xhs; Stata as the only codegen |

G0 does not add the yaml files. Later **NORMS-BE** owns them. Absence of a dedicated “AER panel” UI or a Claude skill does not waive the checks. A skill-runner presence test is **not** acceptance.

### 2.4 top-5 eval only → optional submodule — **EVAL-top5** (frozen)

| Is | Is not |
|---|---|
| An **optional submodule** eval/benchmark for V1 | Product catalog (`classic-5`) used as an **answer key** |
| Scope cap: **only** that top-5 set in V1 | An eval farm under `agent/eval/tasks/` |
| Optional: product runs without the submodule | Vendoring the eval set into `fixtures/classic-5/` |
| Out of line: Card 1995 teaching case; `undergrad_did_01` as farm seed | Gold-body reads as the eval metric |

`classic-5` remains FIND/DATA-COMPLETE **candidates** (DECIDE-6/7). **EVAL-top5** is a different object. Do not conflate them. Never treat catalog identity as the eval answer key.

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
    → find-lit (FL + R-lit-bar)            ⇒  session.find_lit   (FL-BE-reuse: fetch_papers.py THINS HERE)
    → attach                                 ⇒  dataAttached
    → clean_winsor (pywinsor2, 1/99, cont.) ⇒  cleaning_report.steps (CL-BE-winsor; after attach)
    → prewrite pauses                        table1Confirmed then specConfirmed
                                                + NORMS-BE design_gates / chapter_gates
                                                + identification / robustness
    → chapter write / export                 chapter_gates.yaml on write; doc: tex/pdf/docx; code: py default, Stata option
```

FIND-LIT remains **after design confirm** and **before any literature chapter write**, as in find-data-lit §6. It does not sit in the attach slot. Cleaning does not sit before confirm-design.

### 3.2 Rules

1. **Confirm-design first.** Bryce tools must not treat missing or draft `session.design` as locked.
2. **FIND-DATA still does not attach.** `dataAttached` still first for data.
3. **`clean_winsor` runs after attach**, on the session dataset, as a named `CleaningStep` (`cuts=(1,99)`, continuous only, pip `pywinsor2`). It does not attach, does not confirm design, and does not set PREWRITE-PAUSE flags.
4. **PREWRITE-PAUSE still owns** `table1Confirmed` and `specConfirmed`. **NORMS-BE** yaml **reads** those flags and hooks propose/write; it does not replace them and does not run a Claude skill runner.
5. **CK DiD propose stays on infer-design.** Title/question only → propose DiD + treated×period **before** ck attach. `design_gates.yaml` hooks propose; it does not unlock DiD from catalog.
6. **Fixtures never answer key.** classic-5 is not **EVAL-top5** and not gold. EVAL-top5 is an optional submodule only.
7. **Independence.** Checking lit cards does not set `dataAttached`. Cleaning does not confirm spec. Export does not skip pauses. Missing eval submodule is not a product failure.

### 3.3 What may happen before confirm-design

- Infer-design draft propose / edit
- Opening an attach panel in **candidates-only** mode (no FD plan as authoritative match)

What must not happen before confirm-design:

- Authoritative FIND-DATA / FIND-LIT / Bryce lit-review as a confirmed-design match
- pywinsor2 presented as having cleaned “the study dataset” when nothing is attached
- AER gates treated as passed (yaml missing or skipped is fail-closed, not a Claude-skill pass)
- Catalog → `allow_did` or catalog → locked spec
- `table1Confirmed` / `specConfirmed` / estimate / gold biblio paste / eval-farm gold bodies
- Catalog identity treated as **EVAL-top5** answer key

---

## 4. Four picks IN (detail)

### 4.1 lit-review thin into `find_lit` — **FL-BE-reuse**

**IN.** Thin/reuse. Implementation target is a **thin wrap** of `fetch_papers.py` (OpenAlex + Crossref + S2, DOI dedupe) into `agent/find_lit/` + R-lit-bar chapter gate — not a new package.

Must:

- Thin wrap `fetch_papers.py` into existing `find_lit` (same three sources + DOI dedupe)
- Checkbox **before write**; ≥5 verifiable cards before literature chapter write
- Export **checked** cards only to `refs.bib` or CSL-JSON
- Fail closed if fewer than five verifiable cards (do not pad with generate-as-lit)

Must not:

- Stand up a parallel lit pipeline, Paper-WorkFlow lit dump, or second `literature_entries` writer
- Skip confirm-design
- Write chapters from unchecked cards
- Call Elicit / 知网 / Consensus as V1 success

### 4.2 pywinsor2 cleaning — **CL-BE-winsor**

**IN.** Named Python cleaning tool.

Must:

- pip-install **`pywinsor2`** (Python; not Stata `winsor2` as runtime)
- Named step **`clean_winsor`** on the ADR-0002 pipeline
- **`cuts=(1,99)`**; **continuous columns only**
- Keep before/after stats and sidecar **audit** (`cleaning_report.steps`)
- Protect research-design columns and binaries (do not winsorize treated/period/id/time as a silent default)

Must not:

- Require `stata-code` or a `.do` winsor2 as the default cleaner
- Replace the whole 8-step pipeline with a Paper-WorkFlow clean dump
- Run before `dataAttached`
- Present Card teaching extract vs winsor sidecar confusion as a win (ADR-0015 extract path stays teaching-only)

G0 does not add the pip pin or the step module. Later **CL-BE-winsor** does.

### 4.3 AER-Skills distilled gates — **NORMS-BE**

**IN.** Distill into product yaml + hooks. **No Claude skill runner.**

Must (V1 distilled set — this is the dump ceiling, not a floor to expand):

1. Encode distilled AER rules in **`design_gates.yaml`** and **`chapter_gates.yaml`** (files owned by **NORMS-BE**, not G0)
2. Hook **`design_gates.yaml`** on infer-design **propose** (draft still unconfirmed until human confirm)
3. Hook **`chapter_gates.yaml`** on chapter **write**
4. Confirmed `session.design` before estimate / spec lock
5. Required interactions present (DiD treated×period; HET interaction) or **hard block**
6. `dataAttached` + auditable `clean_winsor` recorded before Table 1 / spec confirm
7. `table1Confirmed` then `specConfirmed` before estimate admission
8. Identification / robustness results recorded when those nodes run; do not invent
9. Literature chapter write only through R-lit-bar (checkbox before write)
10. Export only tex/pdf/docx + code-export languages already in product; no ppt/xhs

Must not:

- Copy AER-Skills / AERS / Paper-WorkFlow into `.agents/skills/` as V1
- Run a **Claude skill runner** as the gate engine
- Add a parallel “AER reviewer” that bypasses PREWRITE-PAUSE
- Treat a skill-file presence test as acceptance
- Add p-hack / spec-search as an “AER robustness” feature (that pick is **OUT**)

### 4.4 top-5 eval only — **EVAL-top5**

**IN.** Scope cap.

Must:

- Keep V1 Bryce evaluation/benchmark to **EVAL-top5**
- Ship it as an **optional submodule** only
- Never use it as a product catalog **answer key**
- Evaluate later BE slices by the §7 bullets, **not** by gold-body reads
- Allow the product to run when the submodule is absent

Must not:

- Add a sprawling eval farm (`agent/eval/tasks/*` growth, extra personas, extra gold packets)
- Use Card 1995 or `undergrad_did_01` as a substitute for the named set
- Use classic-5 catalog identity as the eval answer key
- Vendor EVAL-top5 into `fixtures/classic-5/`
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

**NORMS-BE extra refusal (not a fifth DECIDE-8 OUT):** no Claude skill runner. Distilled yaml + propose/write hooks only.

---

## 6. Named objects (reuse, do not fork)

G0 adds **no** new snapshot / OpenAPI objects and **no** yaml / `fetch_papers.py` files.

| Object | Owner | Bryce G0 |
|---|---|---|
| `session.design` | infer-design | Read after confirm. Do not write. **NORMS-BE** later hooks propose via `design_gates.yaml`. |
| `session.find_data` | find-data-lit | Untouched (not a Bryce pick). |
| `session.find_lit` | find-data-lit | **Reuse.** **FL-BE-reuse** thin-wraps `fetch_papers.py` here. |
| `fetch_papers.py` | later **FL-BE-reuse** | Pointer only. Not added in G0. |
| `dataAttached` / snapshot `dataset` | data-completion | Read after attach for cleaning. Do not set. |
| `clean_winsor` / `cleaning_report.steps` | ADR-0002; later **CL-BE-winsor** | pip `pywinsor2`; `cuts=(1,99)`; continuous only; auditable. |
| `table1Confirmed` / `specConfirmed` | PREWRITE-PAUSE | **NORMS-BE** reads; does not own. |
| `design_gates.yaml` / `chapter_gates.yaml` | later **NORMS-BE** | Pointer only. Hook propose / write. No Claude skill runner. |
| `find_lit.export` | FL-BE-export | Bib/CSL only from checked cards. |
| **EVAL-top5** submodule | later **EVAL-top5** | Optional. Never catalog answer key. |
| code-export / doc-export | existing routers | Python default; Stata option; no ppt/xhs. |

Must not live on a Bryce object as a win path: catalog id, `allow_did`, gold-body hashes, gold biblio, Paper-WorkFlow dump, p-hack payloads, ppt/xhs blobs, Claude skill-runner output, unconfirmed `session.design`.

---

## 7. Acceptance criteria (DECIDE-8 + INTEGRATE pointers)

G0 does not add tests. Later `FM-E-BUILD-BRYCE-1` slices **must** implement and show these acceptance criteria. Do **not** evaluate by reading gold chapter bodies or gold bibliographies. Slice ids are the INTEGRATE tokens in §0.1.

### 7.1 FL-BE-reuse (alias: BRYCE-BE-lit-thin)

- Thin wrap `fetch_papers.py` (OpenAlex + Crossref + S2, DOI dedupe) into existing `find_lit`.
- Checkbox before write. Bib/CSL from **checked** cards only.
- No second literature pipeline. No generate-as-lit. No gold biblio paste.
- Unconfirmed design cannot rank as an authoritative lit-review success.

**Fail (unacceptable substitute):** Paper-WorkFlow lit dump; Elicit/知网/Consensus; a new `session.bryce_lit` that writes chapters; skip R-lit-bar; fetch-papers as a parallel product path.

### 7.2 CL-BE-winsor (alias: BRYCE-BE-winsor)

- pip `pywinsor2`. Named `clean_winsor`. `cuts=(1,99)`. Continuous only. Auditable (`cleaning_report.steps`).
- Stata `winsor2` / `stata-code` is not the default.
- Design / binary columns are not silently winsorized.

**Fail (unacceptable substitute):** Stata-only default cleaner; undocumented pandas one-off presented as the named tool; clean-before-attach; Paper-WorkFlow clean dump; winsorizing binaries.

### 7.3 NORMS-BE (alias: BRYCE-BE-aer-gates)

- Distill AER rules into `design_gates.yaml` + `chapter_gates.yaml`.
- Hook **propose** (design) and **write** (chapters). No Claude skill runner.
- No full skill dump. No p-hack feature dressed as robustness.

**Fail (unacceptable substitute):** `.agents/skills/` dump; Claude skill runner as the gate engine; bypass of `table1Confirmed` / `specConfirmed`; catalog → locked spec; p-hack helper.

### 7.4 EVAL-top5 (alias: BRYCE-BE-top5-eval)

- V1 eval/benchmark is **EVAL-top5** as an **optional submodule** only.
- Never a product catalog answer key. No sprawling eval farm. Card / `undergrad_did_01` are not the V1 set.
- Product still runs if the submodule is absent.

**Fail (unacceptable substitute):** adding many `agent/eval/tasks/*`; gold-body rubric as the only metric; catalog id as answer key; vendoring the submodule into classic-5.

OLS remains the default when DiD is not allowed (**infer-design**). Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block. This file does not change those rules.

---

## 8. Later parallel slices (`FM-E-BUILD-BRYCE-1`; do not implement in G0)

G0 owns **only** `docs/bryce-tools-contract.md`.

INTEGRATE pointer names have landed. **Do not start, merge, or partially land these slices in G0.** Implementation is `FM-E-BUILD-BRYCE-1`, write-set-disjoint, after this contract.

| Slice (INTEGRATE id) | Owns (when started) | Must not write |
|---|---|---|
| **FL-BE-reuse** | Thin wrap `fetch_papers.py` into `session.find_lit` / `agent/find_lit`; checkbox before write | Parallel lit pipeline, generate-as-lit, FD ownership, attach, PREWRITE-PAUSE flags |
| **CL-BE-winsor** | pip `pywinsor2`; `clean_winsor` `cuts=(1,99)` continuous only; auditable report | Stata-default cleaner, classic-5 CSV bytes, infer-design, ppt/xhs |
| **NORMS-BE** | `design_gates.yaml` + `chapter_gates.yaml`; hook propose + write | Claude skill runner, AER-Skills dump, p-hack feature, DID unlock rewrite, gold bodies |
| **EVAL-top5** | Optional submodule eval only | Eval farm; catalog or Card as answer key; required submodule for product boot |

Slices stay **write-set-disjoint** when they eventually run. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

Optional FE chrome (labels on FIND-LIT cards, a named `clean_winsor` step in the clean wizard, a gate checklist) does not waive backend gates. Absence of that chrome does not change the IN/OUT set.

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
| **Claude skill runner** | `.agents/skills/` | **NORMS-BE** must not use it as the gate engine |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `session.design`, `session.find_lit`, `dataAttached`, `cleaning_report`, PREWRITE-PAUSE flag names, `code-export` / `doc-export`. Do not replace those objects with a Bryce-named duplicate.

---

## 10. G0 done rule

- File present: `docs/bryce-tools-contract.md`
- Folded: DECIDE-8 four IN (lit-review thin into `find_lit`; pywinsor2 cleaning; AER-Skills distilled gates; top-5 eval only); four OUT (Paper-WorkFlow dump; p-hack; stata-code default; ppt / xhs); order **title → design → confirm → find data/lit → attach → prewrite** vs DECIDE-6/7; mapping onto infer-design / find-data-lit / prewrite / export
- Folded Research INTEGRATE + `FM-E-BUILD-BRYCE-1` pointers: **FL-BE-reuse** (`fetch_papers.py` thin wrap into `find_lit`; checkbox before write); **CL-BE-winsor** (pip `pywinsor2`; `clean_winsor` `cuts=(1,99)` continuous only; auditable); **NORMS-BE** (`design_gates.yaml` + `chapter_gates.yaml`; hook propose/write; **no** Claude skill runner); **EVAL-top5** (optional submodule eval only; never product catalog answer key)
- Retired G0 aliases remain mapped, not used as later-slice ids
- **no gold body reads**
- No application code, API routes, frontend, fixtures, OpenAPI, yaml files, skills dump, submodule, or eval-farm change in G0
- No merge of DATA-COMPLETE / DID / INF / FD / FL implementation branches
- No pull request from this slice
- Later slices cite this file; they do not rewrite §2–§5 without a new serial contract

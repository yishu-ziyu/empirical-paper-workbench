# Data-completion contract (TITLE/TOPIC only)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-DATA-COMPLETE-1` · slice **G0**  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `fix/fm-e-build-math-1-docx-typesetting` @ `af9056b4`  
Design input: `FM-E-DESIGN-DATA-COMPLETE-1` D-data SPEC + 9-screen sketch — **draft sketch only**, not a product freeze, not an expert path.  
Authority: this file freezes TITLE/TOPIC coverage, the **`dataAttached` confirm-attach gate**, classic-5 usage, and **order vs PREWRITE-PAUSE**. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR and not an acceptance checklist. It is the serial write-set freeze so DC-BE-\* / DC-FE-\* can run in parallel without colliding with PREWRITE-PAUSE or WORD-FIX.

---

## 0. Product-line lock

In scope: the formal econpaper paper path — user states a **title/topic**, then must **confirm-attach** data (`dataAttached`) before Table 1, before spec confirm, and before estimate.

Out of product line for this contract (do not extend, re-label, or reuse as classic-5):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets
- Agent spike (`/spike`), first-value marketing review, Copaper historical specs except as cited facts
- Sketch-only sample names (`sample_wage.csv`, `sample_panel_mini.csv`, `wage_panel.csv`) — draft pixels, not catalog inventory

Card remains a teaching / reproduction case (ADR-0015). This flow must not disguise classic-5 as the user’s own research, and must not route formal TITLE/TOPIC attach through `/demos/card`.

The D-data sketch is **draft HITL**. Do not treat its copy, chips, or 9-screen chrome as locked UI. Fold **gate + order** only.

---

## 1. TITLE/TOPIC only — what this flow covers

### 1.1 Named stage (frozen)

**TITLE/TOPIC** is the formal-path session-start stage where the user has a research title or topic and has not yet **confirm-attached** data.

Repo + D-data anchors (do not invent a new engine node):

| Layer | Anchor | Role in this flow |
|---|---|---|
| Empty desk | `DeskPage` `onConfirm(title)` → `setShapedQuestion`; sketch s0/s1 开场 / 先聊钉问题 | Pre-session title/topic text. Chat-first pins a question **without** a data table. |
| Journey | `_JOURNEY_STAGES[0]` **选题**; upload-only stays at stage 0 (`test_journey_upload_only_stays_at_topic`) | Engine-stage name for “topic chosen, not yet past data” |
| Workbench | `question` tab before confirm-attach | Post-session TITLE/TOPIC surface |
| Snapshot | `has_dataset`, `upload_readiness`, `dataset` on `GET /sessions/{id}` (ADR-0013) | Pipeline / ingest truth |
| Product gate | **`dataAttached`** | Confirm-attach succeeded. Distinct from “file picked” and from PREWRITE-PAUSE flags. |

**TITLE/TOPIC is not** `generate_title` / `state.title_chapter`. That node writes the paper `\title{...}` **after** estimate / literature / robustness (`PRWRITE_SEQUENCE`). Data-completion must not move, rename, or gate that node.

### 1.2 Covers (data-completion at TITLE/TOPIC)

Given a formal-path title/topic, this flow only:

1. Lets the user **find / select / upload** a candidate (classic-5 or own file) on an **attach panel**.
2. Requires **确认挂接 (confirm-attach)** to set **`dataAttached`**. Pick or upload alone does not.
3. May **suggest** a classic-5 catalog entry from the title/topic text (DC-BE-suggest; not in G0).
4. May **attach** the chosen source (DC-BE-attach; not in G0).
5. **Blocks Table 1, spec confirm, and estimate** until `dataAttached` (DC-FE-gate; not in G0).
6. After `dataAttached`, may show a data preview (table + N). Preview is ingest, not Table 1 confirm.

“Complete data” means **bind and confirm-attach** an analysis dataset. It does not mean finishing the eight cleaning sub-steps as a user-facing wizard. Cleaning stays on the existing `upload_pipeline` / `clean_data` path.

Open-fork “有数据 / 用样例” may **prefill** the attach panel. Prefill is still a candidate. Confirm-attach is still required before preview / Table 1 / estimate.

### 1.3 Does not cover

- Direction form field semantics (dv / iv / controls / method / template) beyond “proceed requires `dataAttached`”
- **Implementing** PREWRITE-PAUSE: `table1Confirmed`, `specConfirmed`, `blockingDecision` Table1/equation CTAs, `frozen_at` — this contract only freezes that they come **after** `dataAttached`
- Heterogeneity × no-interaction hard-block (`qType === heterogeneity` ∩ no `educ×region`) — estimate-prep / PREWRITE-PAUSE, not G0
- Identification `hitl_pause`, outline chapter-pause, claim ledger, prepare-paper
- Estimate execution, robustness, literature, six-chapter write, code export
- Docx / math typesetting and export samples — **WORD-FIX**
- Card Evidence Lab, Surprise, Next-best Challenge, teaching seed
- New sessionStorage mirrors for dataset columns/name (ADR-0013 forbids them)
- A second upload lifecycle or a second snapshot truth model
- Sketch HTML, slogans, or 9-screen chrome in the product tree
- Implementation of DC-BE-suggest, DC-BE-attach, DC-FE-step, or DC-FE-gate

Desk / chat shaping may pin a title **without** data. That conversation is allowed. No data table, Table 1, or estimate until confirm-attach.

---

## 2. Attach gate — `dataAttached` (confirm-attach)

### 2.1 Named gate (frozen)

Product gate name: **`dataAttached`**.

`dataAttached === true` iff **confirm-attach succeeded** for the current candidate on the formal path.

| State | Meaning | `dataAttached` |
|---|---|---|
| No candidate | Nothing picked or uploaded | `false` |
| Candidate only (找 / 选 / 传) | File or classic-5 entry chosen, not confirmed | `false` |
| Pipeline in flight | `upload_readiness ∈ {PROCESSING, FAILED, CANCELLED}` | `false` |
| Confirm-attach succeeded | User confirmed hang; ingest ready | `true` |

`hasData` / snapshot `has_dataset` / `dataset` may describe bytes on disk. They are **not** the product gate. A prefilled upload or sample is not `dataAttached` until confirm-attach.

Pipeline readiness still applies (do not fork a second queue):

| Session class | Ingest-ready iff |
|---|---|
| Upload-era / classic-5-era (this flow) | `upload_readiness === "READY"` **and** snapshot `has_dataset` / `dataset` present |
| Legacy (no `upload_readiness` field) | Keep upload-recovery **KTD7**. Do not use legacy-missing as the **new** formal TITLE/TOPIC path. |

**`dataAttached` requires ingest-ready + confirm-attach.** New formal TITLE/TOPIC sessions must be upload-era or classic-5-era with an explicit `upload_readiness`. Confirm-attach must not succeed while ingest is `PROCESSING` / `FAILED` / `CANCELLED`.

User-owned files still enter through `POST /upload` → `upload_pipeline` (202, idempotency, KTD1–KTD8). classic-5 attach (DC-BE-attach) must **terminate on the same readiness contract**. Do not invent a parallel run kind for “picked but unconfirmed.”

### 2.2 Required before Table 1 / before estimate

On the formal econpaper path, **confirm-attach must succeed before Table 1 and before estimate.**

Blocked until `dataAttached === true`:

- Data preview that presents the analysis table / N as hung data (sketch s3)
- Table 1 confirm (PREWRITE-PAUSE `table1Confirmed`)
- Equation / 题型→设定 confirm (PREWRITE-PAUSE `specConfirmed`)
- `POST /sessions/{id}/direction` prewrite admission that would run estimate
- Running estimate / filling `mainResults`

DC-FE-step and DC-FE-gate **must** place confirm-attach **before** those PREWRITE-PAUSE surfaces. They must not jump from TITLE/TOPIC or a prefilled candidate to Table 1 or estimate.

### 2.3 Blocked

| Condition | Frozen refusal |
|---|---|
| No candidate | Confirm-attach CTA disabled. |
| Candidate only, not confirmed | `dataAttached` stays false. No preview-as-hung, no Table 1, no estimate. |
| `upload_readiness ∈ {PROCESSING, FAILED, CANCELLED}` | Backend `409` `upload_not_ready` (keep code). Confirm-attach cannot succeed. |
| Session already has an active durable run | Existing `409` `session_busy` + `run_id`. |
| Attach in flight | Do not admit a second upload or classic-5 attach until the active run is terminal. |
| classic-5 path used as a silent Card boot | Block. Card stays `/demos/card`. |
| Table 1 / spec / estimate requested without `dataAttached` | Return to attach-confirm. Do not set PREWRITE-PAUSE flags. |

`FAILED` / `CANCELLED` keep the session visible and require a **new** attach intent (new idempotency key). They do not count as `dataAttached`.

### 2.4 Not blocked (explicit)

- Shaping or pinning the title/topic before attach
- Opening the attach panel; finding / selecting / uploading a **candidate**
- Prefilling the attach panel from “有数据” or “用样例”
- Opening Guide, switching UI language, login/register
- Refresh / snapshot restore of a session that already has `dataAttached`
- Reattach to an in-flight `upload_pipeline` (or future classic-5 attach run) via `active_run` / SSE
- Card teaching boot (other product path)
- **After** `dataAttached`: PREWRITE-PAUSE may run `table1Confirmed` then `specConfirmed` (those slices own the flags)
- WORD-FIX surfaces

### 2.5 How attach is performed (contract, not G0 code)

Legal sources, one confirm, one readiness:

1. **User file** — `POST /upload` (existing). Idempotency-Key, `POST /upload/resolve`, no path leakage (R8).
2. **classic-5 catalog entry** — DC-BE-suggest ranks; DC-BE-attach binds. Same readiness + snapshot projection.
3. **Confirm-attach** — user CTA. This is the only transition that sets `dataAttached`.

Suggest **must not** attach. Attach **must not** invent ranking. Selecting a candidate **must not** set `dataAttached`. Frontend step UI (DC-FE-step) is the 找/选/传/确认挂接 chrome. Frontend gate (DC-FE-gate) consumes `dataAttached` plus snapshot / 409 codes and blocks Table 1 / estimate.

Truth owner remains Project Snapshot (ADR-0013). No new `econpaper_csv_meta` / column mirrors. `dataAttached` is a product flag later slices may project on the snapshot; G0 does not add the field.

---

## 2a. Order vs PREWRITE-PAUSE (frozen; flags not owned here)

Serial order on the formal path:

```
TITLE/TOPIC (pin question; no table)
    → attach panel (找 / 选 / 传)
    → confirm-attach  ⇒  dataAttached
    → data preview (optional ingest view)
    → PREWRITE-PAUSE table1Confirmed     (Table 1 / 样本组成)
    → PREWRITE-PAUSE specConfirmed       (方程 / 题型→设定)
    → estimate
```

Rules:

1. **`dataAttached` first.** Table 1 and spec pauses must not open, and must not become true, unless `dataAttached`.
2. This slice **does not implement** `table1Confirmed` or `specConfirmed`. PREWRITE-PAUSE owns those flags, `blockingDecision` copy, and estimate-prep CTAs.
3. DC-FE-step / DC-FE-gate align with **confirm-attach before Table1 / estimate pauses**. They do not own the pause screens.
4. Estimate must not run if `dataAttached` is false, even if PREWRITE-PAUSE flags were somehow set (fail closed: treat as unattached; return to confirm-attach).
5. Heterogeneity hard-block and results-chapter lock (no main table) stay with estimate-prep / write — not G0.

---

## 3. classic-5 usage

### 3.1 What classic-5 is

`classic-5` is the **named built-in catalog** for formal TITLE/TOPIC find/select on the attach panel.

Frozen identifiers (G0 does not create files or loaders):

| Token | Meaning |
|---|---|
| Catalog id | `classic-5` |
| Reserved tree | `fixtures/classic-5/` |
| Attach source stamp | `source: "classic-5"` plus a stable entry id |
| Suggest scope | Rank **only** classic-5 entries against TITLE/TOPIC text (plus a non-catalog “use your own file” action) |

There is **no** classic-5 inventory in this repository today. G0 does **not** name five papers, vendor CSVs, or add fixtures. Sketch filenames are not catalog entries. Entry list, hashes, and loaders belong to later slices (DC-BE-suggest / DC-BE-attach), still under this path and id.

### 3.2 How it is used in this flow

1. User is on TITLE/TOPIC with a title/topic string (chat-first or open fork).
2. Attach panel: suggest (later) may show classic-5 **candidates** labeled as built-in catalog data, not as the user’s study.
3. User picks a candidate **or** uploads a file → candidate only.
4. Confirm-attach (later DC-BE-attach + DC-FE-gate) binds that source and sets `dataAttached`. classic-5 bytes load from `fixtures/classic-5/` (or `ECONPAPER_CLASSIC5_*`). Same admission / readiness path as upload, **not** `/demos/card`.
5. Snapshot shows `dataset` + `upload_readiness=READY` **and** `dataAttached`. Only then: preview → Table 1 pause → spec pause → estimate.
6. Provenance records catalog id `classic-5`, entry id, and that the file is catalog data. Do not write `teaching_case=card_1995`.

### 3.3 How it is not used

- Not a substitute for Card 1995 or course-panel
- Not vendored into `frontend/public/`
- Not `dataAttached` by mere suggest or highlight
- Not used after TITLE/TOPIC as a silent dataset swap (new candidate requires a new confirm-attach; clears `dataAttached` until re-confirmed)
- Not used to implement PREWRITE-PAUSE or WORD-FIX docx math samples
- Not a second product line
- Not committed private / restricted microdata (ADR-0010 CHARLS rule still holds)

---

## 4. Later parallel slices (do not implement in G0)

G0 owns **only** `docs/contracts/data-completion-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **DC-BE-suggest** | Backend TITLE/TOPIC → classic-5 candidate path (request/response, ranking, catalog read) | Confirm-attach mutation, `dataAttached` writes, FE, PREWRITE-PAUSE flags, export/docx, Card boot |
| **DC-BE-attach** | Backend attach + confirm-attach: bind user file or classic-5; stamp ingest readiness; project `dataAttached` | Suggest ranking, FE chrome, `table1Confirmed` / `specConfirmed`, `generate_title`, WORD-FIX samples, `/demos/card` |
| **DC-FE-step** | Formal attach-panel step UI: 找 / 选 / 传 / **确认挂接**; chat-first has no table before this panel | Backend routes, `dataAttached` enforcement, **Table1 / equation pause UI**, estimate run, docx export, Card desk CTA |
| **DC-FE-gate** | Frontend `dataAttached` wiring: disable / divert Table 1, spec confirm, direction, and estimate until confirm-attach; consume snapshot + `409 upload_not_ready` / `session_busy` | Backend, attach-panel chrome ownership, **implementing** `table1Confirmed` / `specConfirmed`, Word/math fixtures |

**DC-FE-step / DC-FE-gate alignment (frozen):** both sit on **confirm-attach**, which is **before** PREWRITE-PAUSE Table1 / estimate pauses. They must not render or enable those pauses while `dataAttached` is false.

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

---

## 5. Concurrent write-sets (stay out)

| External slice | Lives at | This contract must not touch |
|---|---|---|
| **PREWRITE-PAUSE** | After `dataAttached`: Table 1 confirm → equation/spec confirm → estimate; flags `table1Confirmed` + `specConfirmed`; `blockingDecision` | Implementing those flags, freeze/reveal, estimate-prep UI, hetero hard-block policy |
| **WORD-FIX** | docx math export samples (`export_docx`, OOXML/math fixtures on `fix/fm-e-build-math-1-docx-typesetting`) | Export nodes, math samples, chapter body fill, OLS lock / code-export |

Also do not reopen: upload-recovery plan (`docs/plans/2026-09-02-1324-fix-durable-upload-recovery-plan.md`), run-execution DESIGN, Card canonical / research lab, generic spine, localized-first-study.

Reuse, do not fork: `upload_readiness`, `409 upload_not_ready`, `directionGateForReadiness`, snapshot `dataset`. Add `dataAttached` as the confirm-attach product gate **in front of** PREWRITE-PAUSE — do not replace those flags.

Forbidden sketch slogans in later FE copy (from D-data SPEC; not implemented in G0): 鉴表 / 写章 / 带走 / 先见表.

---

## 6. G0 done rule

- File present: `docs/contracts/data-completion-contract.md`
- Folded: `dataAttached` confirm-attach; order attach → `table1Confirmed` + `specConfirmed` → estimate; DC-FE-step / DC-FE-gate before Table1/estimate pauses
- Sketch cited as draft only; no sketch HTML in this repo
- No backend / frontend / fixture / OpenAPI change in G0
- No pull request from this slice
- Later slices cite this file; they do not rewrite §1–§3 / §2a without a new serial contract

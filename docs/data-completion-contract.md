# Data-completion contract (TITLE/TOPIC only)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-DATA-COMPLETE-1` · slice **G0**  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `fix/fm-e-build-math-1-docx-typesetting` @ `af9056b4`  
Authority: this file freezes TITLE/TOPIC coverage, the attach gate, and classic-5 usage. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR and not an acceptance checklist. It is the serial write-set freeze so DC-BE-\* / DC-FE-\* can run in parallel without colliding with PREWRITE-PAUSE or WORD-FIX.

---

## 0. Product-line lock

In scope: the formal econpaper paper path — user states a **title/topic**, then must complete data before leaving that stage toward direction / prewrite.

Out of product line for this contract (do not extend, re-label, or reuse as classic-5):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets
- Agent spike (`/spike`), first-value marketing review, Copaper historical specs except as cited facts

Card remains a teaching / reproduction case (ADR-0015). This flow must not disguise classic-5 as the user’s own research, and must not route formal TITLE/TOPIC attach through `/demos/card`.

---

## 1. TITLE/TOPIC only — what this flow covers

### 1.1 Named stage (frozen)

**TITLE/TOPIC** is the formal-path session-start stage where the user has a research title or topic and has not yet been allowed to proceed to direction / prewrite.

Repo anchors (do not invent a new engine node):

| Layer | Anchor | Role in this flow |
|---|---|---|
| Empty desk | `DeskPage` `onConfirm(title)` → `setShapedQuestion` | Pre-session title/topic text |
| Journey | `_JOURNEY_STAGES[0]` **选题**; upload-only stays at stage 0 (`test_journey_upload_only_stays_at_topic`) | Engine-stage name for “topic chosen, not yet past data” |
| Workbench | `question` tab before a successful `POST /direction` | Post-session TITLE/TOPIC surface |
| Snapshot | `has_dataset`, `upload_readiness`, `dataset` on `GET /sessions/{id}` (ADR-0013) | Attach truth |

**TITLE/TOPIC is not** `generate_title` / `state.title_chapter`. That node writes the paper `\title{...}` **after** estimate / literature / robustness (`PRWRITE_SEQUENCE`). Data-completion must not move, rename, or gate that node.

### 1.2 Covers (data-completion at TITLE/TOPIC)

Given a formal-path title/topic, this flow only:

1. Lets the user **complete data** so the session becomes **attach-ready**.
2. May **suggest** a classic-5 catalog entry from the title/topic text (DC-BE-suggest; not in G0).
3. May **attach** either a user file or a classic-5 catalog entry (DC-BE-attach; not in G0).
4. **Blocks leaving TITLE/TOPIC** until attach-ready (attach gate below; FE wiring is DC-FE-gate).

“Complete data” here means **bind an analysis dataset to the session**. It does not mean finishing the eight cleaning sub-steps as a user-facing wizard. Cleaning stays on the existing `upload_pipeline` / `clean_data` path.

### 1.3 Does not cover

- Direction form semantics (question / dv / iv / controls / method / template) beyond “proceed requires attach-ready data”
- Direction → estimate confirm, `table1Confirmed`, `specConfirmed`, specification-space freeze (`frozen_at`) — **PREWRITE-PAUSE**
- Identification `hitl_pause`, outline chapter-pause, claim ledger, prepare-paper
- Estimate, robustness, literature, six-chapter write, code export
- Docx / math typesetting and export samples — **WORD-FIX**
- Card Evidence Lab, Surprise, Next-best Challenge, teaching seed
- New sessionStorage mirrors for dataset columns/name (ADR-0013 forbids them)
- A second upload lifecycle, a second readiness field, or a second snapshot truth model
- Implementation of DC-BE-suggest, DC-BE-attach, DC-FE-step, or DC-FE-gate

Desk shaping (`/desk/discuss`, `shapeQuestion`) may produce a title **without** data. That conversation is allowed. The gate fires only when the user **proceeds** off TITLE/TOPIC.

---

## 2. Attach gate — when / how attach is required or blocked

### 2.1 Required before proceed

On the formal econpaper path, **leaving TITLE/TOPIC requires an attach-ready dataset**.

Proceed means any of:

- `POST /sessions/{id}/direction` (prewrite admission)
- Any later formal-path action that assumes analysis data (estimate / prewrite consumers)

Attach-ready (frozen):

| Session class | Attach-ready iff |
|---|---|
| Upload-era / classic-5-era (this flow) | `upload_readiness === "READY"` **and** snapshot `has_dataset` / `dataset` is present |
| Legacy (no `upload_readiness` field) | Keep upload-recovery **KTD7**: existing usable-dataset rule. Do not break it. Do not use legacy-missing as the **new** formal TITLE/TOPIC path. |

New formal TITLE/TOPIC sessions created after this contract **must** be upload-era or classic-5-era: they get an explicit `upload_readiness`. They must not rely on the empty-field legacy hole to skip attach.

User-owned files still enter through `POST /upload` → `upload_pipeline` (202, idempotency, KTD1–KTD8). classic-5 attach (DC-BE-attach) must **terminate on the same readiness contract** (`PROCESSING` → `READY` | `FAILED` | `CANCELLED`). It must not invent `data_complete`, `attached`, or a parallel queue.

### 2.2 Blocked

Refuse proceed / refuse a new attach when:

| Condition | Existing or frozen refusal |
|---|---|
| No dataset bound | Block proceed. Formal TITLE/TOPIC is not attach-ready. |
| `upload_readiness ∈ {PROCESSING, FAILED, CANCELLED}` | Backend `409` `upload_not_ready` (keep code). Frontend reason via `directionGateForReadiness`. |
| Session already has an active durable run | Existing `409` `session_busy` + `run_id` (reattach; do not start a second attach). |
| Attach in flight | Do not admit a second upload or classic-5 attach until the active run is terminal. |
| classic-5 path used as a silent Card boot | Block. Card stays `/demos/card`. |
| Proceed into PREWRITE-PAUSE flags | Out of scope. This gate does not set or read `table1Confirmed` / `specConfirmed`. |

`FAILED` / `CANCELLED` keep the session visible and require a **new** attach intent (new idempotency key). They do not count as attach-ready.

### 2.3 Not blocked (explicit)

- Shaping or editing the title/topic text before proceed
- Opening Guide, switching UI language, login/register
- Refresh / snapshot restore of an already attach-ready session
- Reattach to the in-flight `upload_pipeline` (or future classic-5 attach run) via `active_run` / SSE
- Card teaching boot (other product path)
- PREWRITE-PAUSE and WORD-FIX surfaces

### 2.4 How attach is performed (contract, not G0 code)

Two legal sources, one readiness:

1. **User file** — `POST /upload` (existing). Idempotency-Key, `POST /upload/resolve`, no path leakage in public errors (R8).
2. **classic-5 catalog entry** — DC-BE-attach (later). Binds a catalog path/id into the session, then the same readiness + snapshot projection.

Suggest (DC-BE-suggest) **must not** attach. Attach **must not** invent ranking. Frontend step UI (DC-FE-step) **must not** be the gate. Frontend gate wiring (DC-FE-gate) consumes snapshot `upload_readiness` / `has_dataset` and the 409 codes above.

Truth owner remains Project Snapshot (ADR-0013). No new `econpaper_csv_meta` / column mirrors.

---

## 3. classic-5 usage

### 3.1 What classic-5 is

`classic-5` is the **named built-in catalog** for formal TITLE/TOPIC data-completion.

Frozen identifiers (G0 does not create files or loaders):

| Token | Meaning |
|---|---|
| Catalog id | `classic-5` |
| Reserved tree | `fixtures/classic-5/` |
| Attach source stamp | `source: "classic-5"` plus a stable entry id |
| Suggest scope | Rank **only** classic-5 entries against TITLE/TOPIC text (plus a non-catalog “use your own file” action) |

There is **no** classic-5 inventory in this repository today. G0 does **not** name five papers, vendor CSVs, or add fixtures. Entry list, hashes, and loaders belong to later slices (DC-BE-suggest / DC-BE-attach), still under this path and id.

### 3.2 How it is used in this flow

1. User is on TITLE/TOPIC with a title/topic string.
2. Suggest (later) may return classic-5 **candidates** labeled as built-in catalog data, not as the user’s study.
3. User picks a candidate **or** uploads a file.
4. Attach (later) binds that source. classic-5 bytes are loaded from `fixtures/classic-5/` (or an explicit env override owned by DC-BE-attach). They go through the same admission / readiness path as an upload, not through `/demos/card`.
5. Snapshot shows `dataset` + `upload_readiness=READY`. Proceed off TITLE/TOPIC is then allowed.
6. Provenance must record catalog id `classic-5`, entry id, and that the file is catalog data. Do not write `teaching_case=card_1995`.

### 3.3 How it is not used

- Not a substitute for Card 1995 or course-panel
- Not vendored into `frontend/public/`
- Not used after TITLE/TOPIC as a silent dataset swap (no mid-prewrite rebind without a new attach intent)
- Not used by PREWRITE-PAUSE, estimate confirm, or WORD-FIX docx math samples
- Not a second product line
- Not committed private / restricted microdata (ADR-0010 CHARLS rule still holds)

If a later slice needs an env override, the name must stay scoped (`ECONPAPER_CLASSIC5_*`). Do not reuse `ECONPAPER_CARD_CSV`.

---

## 4. Later parallel slices (do not implement in G0)

G0 owns **only** `docs/data-completion-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **DC-BE-suggest** | Backend TITLE/TOPIC → classic-5 candidate path (request/response, ranking against title/topic, catalog read) | Attach mutation, readiness writes, FE, PREWRITE-PAUSE flags, export/docx, Card boot |
| **DC-BE-attach** | Backend attach path: bind user file or classic-5 entry; stamp `upload_readiness`; snapshot `dataset` | Suggest ranking, FE chrome, `table1Confirmed` / `specConfirmed`, `generate_title`, WORD-FIX samples, `/demos/card` |
| **DC-FE-step** | Formal TITLE/TOPIC data-completion step UI (copy, candidate list, upload affordance) | Backend routes, gate enforcement, PREWRITE-PAUSE confirm UI, docx export, Card desk CTA |
| **DC-FE-gate** | Frontend proceed wiring: disable / reason from snapshot + 409 `upload_not_ready` / `session_busy` | Backend, step chrome ownership, direction→estimate confirm, Word/math fixtures |

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

---

## 5. Concurrent write-sets (stay out)

| External slice | Lives at | This contract must not touch |
|---|---|---|
| **PREWRITE-PAUSE** | direction → estimate confirm; `table1Confirmed` + `specConfirmed` | Those flags, freeze/reveal, estimate-confirm UI, prewrite pause policy |
| **WORD-FIX** | docx math export samples (`export_docx`, OOXML/math fixtures on `fix/fm-e-build-math-1-docx-typesetting`) | Export nodes, math samples, chapter body fill, OLS lock / code-export |

Also do not reopen: upload-recovery plan (`docs/plans/2026-09-02-1324-fix-durable-upload-recovery-plan.md`), run-execution DESIGN, Card canonical / research lab, generic spine, localized-first-study.

Reuse, do not fork: `upload_readiness`, `409 upload_not_ready`, `directionGateForReadiness`, snapshot `dataset`.

---

## 6. G0 done rule

- File present: `docs/data-completion-contract.md`
- No backend / frontend / fixture / OpenAPI change in G0
- No pull request from this slice
- Later slices cite this file; they do not rewrite §1–§3 without a new serial contract

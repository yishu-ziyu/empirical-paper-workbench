# DiD narrow-exception contract (DECIDE-5 A)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-DID-NARROW-1` · slice **G0**  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `feat/fm-e-build-data-complete-1` @ `20bd2026f733777fa2582638b63b0e5a788af9b8`  
Design input: **DECIDE-5 A** — DiD is a **narrow exception**, not a general TWFE unlock  
Authority: this file freezes `allow_did` (default false), the title/catalog-only setter, the treated×period hard-block, and the OLS-lock non-regression. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR and not an acceptance checklist. It is the serial write-set freeze so DID-BE-\* / DID-FE-hint can run without colliding with the OLS lock, WORD-FIX, HET-CODE-EXPORT, or CLASSIC-FIXTURES CSV bytes.

---

## 0. Product-line lock — DECIDE-5 A

**DECIDE-5 A (frozen):** the formal path stays OLS-locked. Difference-in-differences is allowed only as a **narrow, gated exception** for a classic Card–Krueger / minimum-wage style TITLE/TOPIC or catalog entry. It does **not** unlock two-way fixed effects, event-study, or staggered DiD for the rest of the product.

In scope: the formal econpaper paper path after TITLE/TOPIC — the same product line as `docs/data-completion-contract.md`.

Out of product line for this exception (do not extend, re-label, or treat as `allow_did`):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`, ADR-0015). Card 1995 is education / wages (OLS + IV), **not** Card–Krueger 1994 minwage DiD.
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets (including `agent/eval/tasks/undergrad_did_01`)
- Agent spike (`/spike`), first-value marketing review
- User-picked `method=did` / `method=panel` / `method=twfe` on the direction form
- Presence of `id_col` + `time_col`, `| entity + time` formula syntax, or `first_treat_col`
- Staggered adoption, Callaway–Sant'Anna, Goodman-Bacon, event-study leads/lags

`dataAttached` (data-completion) is a **different** gate. This contract does not attach data, does not skip confirm-attach, and does not replace PREWRITE-PAUSE flags.

---

## 1. Named gate — `allow_did` (default false)

### 1.1 Named flag (frozen)

Product gate name: **`allow_did`**.

| State | Meaning | `allow_did` |
|---|---|---|
| Default / unspecified / missing field | Formal path; OLS lock holds | `false` |
| Title or catalog is not Card–Krueger / minwage style | Ordinary TITLE/TOPIC or other classic-5 entry | `false` |
| User selected DiD / panel / TWFE in `MethodSelector` | Form method is not the setter | `false` |
| Title/catalog gate matched classic minwage-style entry | Only legal `true` | `true` |

`allow_did === true` iff the **title/catalog gate** (DID-BE-gate; not G0) accepted a classic Card–Krueger / minimum-wage style TITLE/TOPIC or catalog entry for the current formal session.

G0 does not add the field to snapshot, OpenAPI, or session state. Later slices may project it. Missing / null / absent **is** false. Fail closed.

### 1.2 Who may set `true`

**Only the title/catalog gate may set `allow_did = true`.**

Legal inputs to that gate (contract, not matcher code):

1. **TITLE/TOPIC text** on the formal path (desk / chat-first / open-fork question string).
2. **classic-5 catalog identity** after find/select — ranking metadata and `entry_id`, not CSV bytes.

Archetype: Card–Krueger 1994 New Jersey / Pennsylvania minimum-wage 2×2. In today's ranking catalog (`fixtures/classic-5/catalog.json`) the minwage-style token is `minimum-wage-employment` ("Minimum wage and employment"). G0 does **not** add entries, hashes, or CSV files. DID-BE-gate owns the matcher and may use title/topic text **and/or** that catalog identity. It must not invent a second catalog.

`schooling-wages` (education and wages) is **not** this exception. That family stays OLS-locked (Card 1995 teaching case remains `/demos/card`).

### 1.3 Who must not set `true`

These never flip `allow_did`:

- `MethodSelector` / `DirectionForm` choosing `DiD`
- `research_direction.method` or `main_specification.method` equal to `did` / `difference-in-differences` / `panel` / `twfe` / `event-study`
- `asked_panel_or_did()` / `norm_method(...) == "did"` in `agent/engine/ols_lock.py` or `agent/design/spec.py`
- Confirm-attach / `dataAttached` / classic-5 attach of a non-minwage entry
- User-file upload, even if the file is a panel
- PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Code export, chapter generate, estimate, robustness
- Card teaching boot, CHARLS, eval DiD tasks

Selecting DiD on the form while `allow_did` is false stays OLS-locked. The form label is not a TWFE key.

### 1.4 How the flag is used (contract, not G0 code)

```
TITLE/TOPIC (title/topic string; optional classic-5 candidate)
    → title/catalog gate  ⇒  allow_did   (DID-BE-gate; default false)
    → dataAttached (existing; independent)
    → PREWRITE-PAUSE table1Confirmed / specConfirmed
    → if allow_did: spec must name treated×period (DID-BE-spec)
    → estimate / write / export
```

`allow_did` does not skip `dataAttached`. `dataAttached` does not set `allow_did`.

---

## 2. When `allow_did`: force treated×period (hard block)

### 2.1 Required DiD main term (frozen)

If and only if `allow_did === true`, the confirmed spec **must** contain the **2×2 treated×period interaction** (or an equivalent DiD main term). That interaction is the identified object. It is not optional garnish.

**Counts as the main term** (any one):

- Explicit interaction: `treated:period`, `treated * period`, `treat × post`, `treat#post`
- A single constructed dummy that **is** that interaction (`treat_post`, `did`, NJ×after, and the same 2×2 cell)

**Does not count** (still missing → hard block, even if `allow_did`):

- Treated main effect alone, or period / post main effect alone
- `id_col` + `time_col` without the interaction
- `| entity + time` / TWFE absorb syntax as a substitute
- `first_treat_col`, staggered timing, Callaway–Sant'Anna, Goodman-Bacon
- Event-study lead/lag dummies without the 2×2 main term
- `method=did` with `y ~ treat` or pooled OLS

Two-way FE is **not** the exception. The exception is the Card–Krueger 2×2 interaction.

G0 does not freeze column names. DID-BE-spec binds whatever columns the session actually has (catalog or user file) to this shape. It must not emit a TWFE formula to “make DiD work.”

### 2.2 Hard block when the term is missing

If `allow_did === true` and the spec has no treated×period (or equivalent) main term:

| Surface | Frozen refusal |
|---|---|
| Spec confirm (`specConfirmed`) | Must not become true for this DiD exception. Return to equation / 题型→设定. |
| `POST /sessions/{id}/direction` that would run estimate | Refuse. Do not start estimate. |
| Estimate / `mainResults` | Do not run. Do not invent a coefficient. |
| Generate-chapter / six-chapter write | Do not write as if DiD ran. |
| Code export | Do not emit feols / xtreg / reghdfe / TWFE for this session. |

Fail closed. Same family as the heterogeneity × no-interaction hard-block (`qType === heterogeneity` ∩ no `educ×region`): missing required interaction **blocks**, it does not degrade to a silent OLS or silent TWFE.

DID-BE-spec owns the check. G0 does not add the error code.

### 2.3 When `allow_did` is false

OLS lock holds. Direction, estimate, prompts, generate-chapter, and export stay on OLS / regress / lm. They must not inject or claim 双向固定效应 / TWFE / feols / xtreg / reghdfe / felm.

A user who typed DiD on the form, or attached a panel CSV, still does not get TWFE.

### 2.4 Not blocked (explicit)

- Title/topic shaping and classic-5 suggest/select while `allow_did` is still false
- Confirm-attach / `dataAttached` (data-completion)
- Table 1 on an OLS-locked session
- IV / RD / SCM on their own existing paths (`method_triggers_ols_lock` already excludes them). This contract does not reopen those methods.
- Card teaching OLS/IV lab (other product path)
- After `allow_did` **and** a present treated×period term: later slices may run the narrow 2×2 exception
- WORD-FIX docx/math surfaces; HET-CODE-EXPORT; CLASSIC-FIXTURES CSV authorship

---

## 3. OLS lock elsewhere untouched

### 3.1 What stays frozen

`agent/engine/ols_lock.py` remains the default lock for the formal path:

- Public estimator label: OLS / regress / lm
- Forbidden under the lock: 双向固定效应, TWFE, feols, xtreg, reghdfe, felm, 「而是采用双向固定效应」, 「加入州固定效应与年份固定效应」, entity/time FE claims
- No negation window (issue #24)

This contract **does not** rewrite, relocate, or weaken that module. It does **not** treat `asked_panel_or_did()` as a product unlock.

### 3.2 Narrow exception, not general TWFE unlock

Today `method=did` (and several panel tokens) make `ols_lock_active` false. **DECIDE-5 A withdraws that as a product rule.** Later slices may read `allow_did` so the lock stays **on** unless the title/catalog gate set `true`. They must not:

- Add new panel / TWFE / event-study aliases that skip the lock
- Treat `| id + year` or guessed id/year columns as DiD
- Unlock staggered / CS / Bacon as part of this exception
- Change OLS six-chapter export (`regress` / `lm`, not `xtreg` / `feols`)

When `allow_did` is true and the 2×2 term is present, the session may name DiD **for that term**. That is the whole exception. It is not a license to write general TWFE.

IV / RD / SCM stay on their existing non-OLS paths. This file does not change them.

---

## 4. Later parallel slices (do not implement in G0)

G0 owns **only** `docs/did-narrow-exception-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **DID-BE-gate** | Title/catalog → `allow_did`. Default false. Only classic Card–Krueger / minwage style TITLE/TOPIC or catalog identity may set true. | Spec interaction check, FE chrome, OLS-lock rewrite, WORD-FIX, HET-CODE-EXPORT, classic-5 **CSV bytes**, Card boot |
| **DID-BE-spec** | When `allow_did`, require treated×period (or equivalent DiD main term). Missing → hard block (no estimate / no write-as-estimated). | Title/catalog matcher ownership, general TWFE / staggered unlock, FE beyond an optional one-line hint, export/docx, catalog CSV content |
| **DID-FE-hint** (optional) | **One line only** that the session is the minwage-style DiD exception (or that the interaction is required). | Second method picker, TWFE UI, spec editor, backend routes, OLS-lock copy beyond that one line |

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

**DID-FE-hint alignment (frozen):** optional, one line, no new chrome. Absence of the hint does not change the backend gates.

---

## 5. Concurrent write-sets (stay out)

| External slice | Lives at | This contract must not touch |
|---|---|---|
| **OLS lock** | `agent/engine/ols_lock.py`, generate-chapter / estimate / prompts; issue #24 | Rewriting the lock, adding TWFE aliases, sanitizer / prompt-lock edits |
| **WORD-FIX** (productize) | docx math export (`export_docx`, OOXML/math fixtures) | Export nodes, math samples, chapter body fill |
| **HET-CODE-EXPORT** | Heterogeneity × interaction code-export / hard-block productize | Hetero export scripts, `educ×region` policy, results-chapter lock |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking metadata (`catalog.json`) is cited only; G0 does not edit it. |
| **DATA-COMPLETE** | `docs/data-completion-contract.md`; `dataAttached`; DC-BE-\* / DC-FE-\* | Confirm-attach, suggest ranking, attach-panel chrome |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision` | Implementing those flags (DID-BE-spec may *refuse* spec confirm when the interaction is missing; it does not own the pause UI) |

Also do not reopen: Card canonical / research lab, generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `dataAttached`, snapshot `dataset`, existing `research_direction` / `main_specification` fields. Add `allow_did` as a **narrow** product flag — do not replace `method` and do not treat `method=did` as the gate.

---

## 6. G0 done rule

- File present: `docs/did-narrow-exception-contract.md`
- Folded: `allow_did` default **false**; only title/catalog gate may set **true** (classic Card–Krueger / minwage style); when `allow_did`, treated×period (or equivalent) is required or **hard block**; OLS lock elsewhere untouched
- Later slices named only: DID-BE-gate, DID-BE-spec, optional DID-FE-hint (one line)
- No backend / frontend / fixture / OpenAPI / OLS-lock / export change in G0
- No pull request from this slice
- Later slices cite this file; they do not rewrite §1–§3 without a new serial contract

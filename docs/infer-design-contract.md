# Infer-design contract (title-first; DECIDE-6)

Status: frozen (G0 serial contract)  
Task: `FM-E-BUILD-INFER-DESIGN-1` · slice **INF-G0**  
Product line: **formal econpaper only** (ADR-0010 web product; user study path)  
Baseline: `main` @ `79c9c91508f9f1479dc5cd8c6d85b3342f7c913d`  
Design input: **DECIDE-6** acceptance from Decide (via Firstmate) — title-first research-design inference; catalog is candidates only; **no gold body reads**  
Sister contracts (cited, not merged): `docs/data-completion-contract.md` (`FM-E-BUILD-DATA-COMPLETE-1` G0), `docs/did-narrow-exception-contract.md` (`FM-E-BUILD-DID-NARROW-1` G0)  
Authority: this file freezes the DECIDE-6 **order**, **locks**, and **accept bullets** below, plus **`session.design` draft vs confirmed** and the DiD rewrite that **deprecates catalog-token `allow_did`**. Later slices implement against it. G0 adds **this markdown only**.

This is not an ADR. It is the serial write-set freeze so INF-BE-\* / DID-BE-\* / DC-BE-suggest can run without colliding with DATA-COMPLETE attach, PREWRITE-PAUSE flags, or classic-5 CSV authorship. Acceptance is the DECIDE-6 bullets in §8 — **not** gold-body reads.

---

## 0. Product-line lock — DECIDE-6

**DECIDE-6 (frozen; Decide via Firstmate).** Encode the following **verbatim**:

**Order:** title/question → design propose (Y/X/interactions/method) → human confirm → data candidates → attach → prewrite pauses.

**Locks:**

- Fixtures/catalog = candidates only, never answer key.
- DiD only from confirmed `design.method=did` + treated×period; NO catalog-id `allow_did`.
- OLS default elsewhere; het interaction hard-block still.

Product-object name in this file is `session.design` (same object as `design` above). `Y` / `X` are outcome / treatment. Later slices must not evaluate by reading gold chapter bodies.

The engine proposes a research design from the **session title** (and any user-supplied research-question text) **first**. Classic fixtures / catalog entries are **candidates only**, never an answer key. The user must **confirm** a design before downstream gates treat it as locked (`session.design`). DiD is allowed only from that **confirmed** design (`design.method=did` or `norm_method` equivalent **and** the required treated×period interaction). Catalog id is never the DiD source of truth. OLS is the default elsewhere; the heterogeneity interaction hard-block still holds.

In scope: the formal econpaper paper path after TITLE/TOPIC — the same product line as `docs/data-completion-contract.md`.

Out of product line for this contract (do not extend, re-label, or treat as a confirmed design):

- Card teaching case (`POST /demos/card`, `research.teaching_case=card_1995`, ADR-0015)
- Guide / legacy course sample (`frontend/public/samples/course-panel.csv`)
- CHARLS wizard, CFPS fixture, spike CSVs, eval datasets (including `agent/eval/tasks/undergrad_did_01`)
- Agent spike (`/spike`), first-value marketing review, flow-sketch / draft-product chrome
- Sketch-only sample names (`sample_wage.csv`, `sample_panel_mini.csv`, `wage_panel.csv`)
- Catalog identity alone (`ck1994`, `ck1994_long`, `minimum-wage-employment`, `barro1991_growth`, …)
- Unconfirmed `MethodSelector` / `DirectionForm` picks, including a typed `DiD`
- Presence of `id_col` + `time_col`, `| entity + time` formula syntax, or `first_treat_col` without a confirmed DiD design + interaction

`dataAttached` (data-completion) and `table1Confirmed` / `specConfirmed` (PREWRITE-PAUSE) are **different** gates. This contract does not attach data, does not skip confirm-attach, and does not replace those flags. It **does** rewrite who may unlock DiD: confirmed `session.design`, not catalog-token `allow_did`.

---

## 1. Purpose and non-goals

### 1.1 Purpose (frozen)

Given a formal-path **session title** and optional research-question text, this flow only:

1. **Proposes** a research-design **draft** (`session.design.status = draft`).
2. Requires the user to **confirm** that draft before any downstream gate treats the design as locked.
3. On confirm, writes **`session.design`** as the authoritative design object (`status = confirmed`).
4. Lets DATA-COMPLETE **suggest** classic-5 entries that **match the confirmed design**. Suggest still lists candidates; it never auto-selects, never confirm-attaches, never writes gold chapter bodies.
5. Lets the DiD narrow exception proceed **only** from confirmed `method=did` (or equivalent) **plus** the required treated×period interaction. Missing interaction stays a **hard block** (DID-BE-spec).

### 1.2 Non-goals (frozen)

This contract does **not**:

- Generate, fill, lock, or **read** six-chapter / gold chapter bodies (acceptance is §8, not gold-body reads)
- Treat catalog → locked spec as a win path
- Treat catalog → `allow_did` as a win path
- Auto-succeed, auto-select, or prefill a fixture as the user’s study
- Attach a dataset or set `dataAttached`
- Set PREWRITE-PAUSE `table1Confirmed` / `specConfirmed`
- Run estimate, robustness, literature, `generate_title` / `state.title_chapter`, or export
- Merge `feat/fm-e-build-data-complete-1`, `feat/fm-e-build-did-narrow-1`, or other DC / DID implementation branches
- Implement application code, API routes, OpenAPI shapes, or frontend chrome (INF-G0 is markdown only)

`TITLE/TOPIC` here is the session-start title / topic string (desk `onConfirm(title)`, `shapedQuestion`, later `title_topic`). It is **not** `generate_title` / `state.title_chapter` (paper `\title{...}` after estimate / literature / robustness). Infer-design must not move, rename, or gate that node.

---

## 2. Named object — `session.design`

### 2.1 Named object (frozen)

Product object name: **`session.design`**.

This is the formal-path research-design record. It is **not** a catalog entry, **not** `dataAttached`, and **not** a chapter body.

Existing engine fields stay readable (`research_direction`, `main_specification`, `DirectionSpec` / `norm_method` in `agent/design/spec.py`). Later slices may **project** a confirmed `session.design` onto those fields. They must not treat an unconfirmed draft, a catalog id, or a form click as `set_direction` / locked spec.

G0 does not add the object to snapshot, OpenAPI, or session state. Later slices may project it. Missing / null / absent **is** unconfirmed. Fail closed.

### 2.2 Draft vs confirmed (frozen)

| `status` | Meaning | Downstream may treat as locked? |
|---|---|---|
| missing / null | No inference yet | No |
| `draft` | Engine proposal from title (+ optional RQ). User has not confirmed. | No |
| `confirmed` | User confirmed. This is `session.design` as used by later gates. | Yes |

| Flag | Meaning |
|---|---|
| `confirmed` | `true` iff `status === "confirmed"` |
| `proposed_at` | When the current draft was written |
| `confirmed_at` | When the user confirmed; `null` while draft / missing |

Re-propose after confirm writes a **new draft** and clears `confirmed` / `confirmed_at`. Downstream gates fall back to unconfirmed until the user confirms again. Confirm is the only transition that locks.

### 2.3 Field shape (frozen)

Normalize `method` with the existing `norm_method` map: display `OLS` / `DiD` / `IV` / `RD` / `SCM` → stored `ols` / `did` / `iv` / `rd` / `scm`. DiD aliases already in-repo (`difference-in-differences`, `diff-in-diff`, `difference_in_differences`) count as `did`.

```json
{
  "status": "draft",
  "confirmed": false,
  "proposed_at": "2026-09-15T12:00:00Z",
  "confirmed_at": null,
  "source": {
    "title": "最低工资对就业的影响",
    "question": ""
  },
  "method": "did",
  "outcome": "employment",
  "treatment": "min_wage",
  "controls": [],
  "group": "treated",
  "treated": "treated",
  "period": "post",
  "time_col": "",
  "id_col": "",
  "first_treat_col": "",
  "interactions": [
    {
      "kind": "did",
      "left": "treated",
      "right": "period",
      "term": "treated:period"
    }
  ],
  "qType": "causal",
  "heterogeneity_groups": [],
  "catalog_entry_id": null
}
```

| Field | Type | Required when | Meaning |
|---|---|---|---|
| `status` | `"draft"` \| `"confirmed"` | always once proposed | Draft vs locked |
| `confirmed` | bool | always once proposed | Must match `status` |
| `proposed_at` | ISO-8601 | once proposed | Draft timestamp |
| `confirmed_at` | ISO-8601 \| `null` | always once proposed | Confirm timestamp; null if draft |
| `source.title` | string | always | Session title / TITLE/TOPIC text used to propose |
| `source.question` | string | optional | User-supplied research-question text; empty if title-only |
| `method` | `ols` \| `did` \| `iv` \| `rd` \| `scm` | always once proposed | Same tokens as `DirectionSpec` / `ENGINE_METHODS` |
| `outcome` | string | preferred; empty allowed on draft | `dv` / `outcome` / `outcome_col` |
| `treatment` | string | preferred; empty allowed on draft | Treatment (form `iv` / `treatment` / `treatment_col` — **not** the IV instrument) |
| `controls` | string[] | optional | Same as `DirectionSpec.controls` |
| `group` / `treated` | string | `method=did` (draft may leave a named slot) | Treated / group indicator |
| `period` | string | `method=did` (draft may leave a named slot) | Post / period indicator |
| `time_col` / `id_col` / `first_treat_col` | string | optional | Existing DiD columns; **not** a substitute for the interaction |
| `interactions` | object[] | required before DiD or HET may pass their hard-blocks | See §2.4 |
| `qType` | `"average"` \| `"heterogeneity"` \| `"causal"` | optional; default from method | Same family as PREWRITE-PAUSE `qType` |
| `heterogeneity_groups` | string[] | when `qType=heterogeneity` | Existing `DirectionSpec.heterogeneity_groups` |
| `catalog_entry_id` | string \| `null` | must be `null` on propose/confirm | Catalog is not part of the locked design |

Method-specific extras already used in-repo stay optional on the object and are **not** confirm substitutes:

| `method` | Optional fields (existing) |
|---|---|
| `iv` | `endogenous`, `instruments` / `instrument` |
| `rd` | `running_var`, `cutoff` |
| `scm` | `unit_col`, `treated_unit`, `treatment_time` |
| any | `cluster`, `cluster_levels` |

**Must not** live on `session.design` as a win path: catalog id, `allow_did`, `dataAttached`, chapter bodies, gold-body hashes, fixture file paths.

### 2.4 Interaction terms (frozen)

`interactions[]` entries:

| Field | Type | Meaning |
|---|---|---|
| `kind` | `"did"` \| `"het"` | DiD 2×2 vs heterogeneity |
| `left` / `right` | string | Factors (e.g. `treated` / `period`, `educ` / `region`) |
| `term` | string | Canonical display: `treated:period`, `educ:region` |

**DiD main term** (`kind=did`) counts as present if any one of:

- Explicit interaction: `treated:period`, `treated * period`, `treat × post`, `treat#post`
- A single constructed dummy that **is** that interaction (`treat_post`, `did`, NJ×after, and the same 2×2 cell)

**Does not count** (still missing):

- Treated main effect alone, or period / post main effect alone
- `id_col` + `time_col` without the interaction
- `| entity + time` / TWFE absorb syntax as a substitute
- `first_treat_col`, staggered timing, Callaway–Sant'Anna, Goodman-Bacon
- Event-study lead/lag dummies without the 2×2 main term
- `method=did` with `y ~ treat` or pooled OLS

**HET term** (`kind=het`) stays the existing PREWRITE-PAUSE rule: `qType === heterogeneity` requires an interaction (`educ×region` / `educ:region` / `educ*region` or the groups named on the design). Infer-design does not own that hard-block; it must not weaken it.

G0 does not freeze column names to a catalog schema. Later slices bind whatever columns the session actually has (user file or a later confirm-attached candidate) to this shape.

---

## 3. Propose flow

### 3.1 Input / output (frozen)

**Input (only):**

1. Session **title** (TITLE/TOPIC / desk title / `shapedQuestion` / `title_topic.title`).
2. Optional user-supplied **research-question** text (`source.question`).

**Output:** a `session.design` object with `status=draft`, `confirmed=false`, `confirmed_at=null`, `catalog_entry_id=null`.

Propose reads title (+ RQ) **first**. It may use those strings to choose `method=ols` vs `method=did` vs other `norm_method` tokens and to name outcome / treatment / interaction **slots**. It must not require a catalog hit to emit a draft.

### 3.2 Must (propose)

- Write a draft only. Do not lock.
- Stamp `proposed_at` and `source.title` / `source.question`.
- If the title/RQ names a 2×2 DiD object, draft `method=did` **and** a treated×period interaction slot (names may be placeholders until data is attached).
- If the title/RQ names an average / levels association (e.g. schooling–wages, Barro growth), draft `method=ols` with no DiD interaction requirement.
- Leave `catalog_entry_id` null.

### 3.3 Must not (propose)

| Refusal | Frozen |
|---|---|
| Attach dataset / ingest | Must not call upload, classic-5 attach, or stamp snapshot `dataset`. |
| `dataAttached` | Must not set true. Propose is pre-attach. |
| Catalog as source of truth | Must not select `ck1994` / `ck1994_long` / `barro1991_growth` / any `classic-5` entry. |
| `allow_did` from catalog id | Must not set `allow_did` because an entry id matched. Catalog → `allow_did` is a **deprecated** win path (§7). |
| Locked spec | Must not write `status=confirmed`, must not treat the draft as `set_direction` / `main_specification` for estimate. |
| Gold / chapter bodies | Must not write chapter text, gold-body fixtures, or six-chapter fill. |
| PREWRITE-PAUSE flags | Must not set `table1Confirmed` or `specConfirmed`. |
| Estimate / export | Must not enqueue estimate or emit code/docx. |

A title that looks like Card–Krueger may produce a **DiD draft**. That draft is not permission to estimate DiD and not `allow_did=true`.

---

## 4. Confirm flow

### 4.1 Named transition (frozen)

**Confirm-design** is the only transition that locks `session.design`.

`session.design.status` becomes `confirmed` iff the user confirmed the current draft (or an edited draft) on the formal path.

| State | `session.design` | Downstream treats design as locked? |
|---|---|---|
| Nothing proposed | missing | No |
| Draft only | `status=draft` | No |
| User edited the draft, not confirmed | still `draft` | No |
| Confirm-design succeeded | `status=confirmed`, `confirmed=true`, `confirmed_at` set | Yes |

### 4.2 Must (confirm)

- Require an existing draft. Confirm with no draft fails closed.
- Lock the fields on the confirmed object (`method`, outcome / treatment / controls, DiD/HET slots, `interactions`).
- Stamp `confirmed_at`.
- Keep `catalog_entry_id` null. Confirming a design does **not** pick a fixture.
- After confirm, DATA-COMPLETE suggest / DID permission / estimate admission may proceed **under this contract’s rules**. They still owe their own gates (`dataAttached`, Table 1, spec confirm, DID-BE-spec interaction).

### 4.3 Must not (confirm)

- Attach data or set `dataAttached`
- Auto-select or confirm-attach `ck1994` / `barro1991` / any catalog entry
- Set `allow_did` from a catalog token
- Set `table1Confirmed` / `specConfirmed`
- Write chapter bodies or run estimate
- Skip DID-BE-spec: confirmed `method=did` **without** a treated×period term still **hard-blocks** spec confirm and estimate

Confirm-design is **not** confirm-attach and **not** spec confirm.

### 4.4 Who may consume the locked design

Only after `status=confirmed`:

| Consumer | Allowed use |
|---|---|
| DC-BE-suggest | Rank classic-5 **candidates** that match the confirmed design. Still candidates. |
| DID permission | Read `method` + `interactions` (see §7). Catalog id is irrelevant. |
| PREWRITE-PAUSE / `set_direction` | Project confirmed fields into direction / spec. Still requires `dataAttached` before Table 1 / spec / estimate. |
| Estimate / write / export | Only after `dataAttached` **and** PREWRITE-PAUSE **and** DID-BE-spec (if `method=did`). |

Without a confirmed design, those consumers fail closed or stay on candidates-only (§8).

---

## 5. Order vs DATA-COMPLETE and PREWRITE-PAUSE

### 5.1 Intended sequence (frozen)

DECIDE-6 order (verbatim):

```
title/question → design propose (Y/X/interactions/method) → human confirm → data candidates → attach → prewrite pauses
```

Mapped onto named gates already in this product line:

```
title/question
    → design propose (Y/X/interactions/method)  ⇒  session.design status=draft
    → human confirm                             ⇒  session.design status=confirmed (locked)
    → data candidates                           (DC-BE-suggest; fixtures = candidates, never answer key)
    → attach                                    ⇒  dataAttached
    → prewrite pauses                           table1Confirmed then specConfirmed
                                                (DID-BE-spec: method=did ⇒ interaction required;
                                                 het interaction hard-block still)
```

Propose → confirm happens **before** DATA-COMPLETE and PREWRITE-PAUSE treat the design as authoritative. No gold body reads on this path.

### 5.2 Rules

1. **Confirm-design first for design authority.** Suggest, DID permission, Table 1, spec confirm, and estimate must not treat a missing or draft design as locked `session.design`.
2. **`dataAttached` still first for data.** Confirm-design does not attach. Table 1 / spec / estimate still require `dataAttached` (`docs/data-completion-contract.md` §2 / §2a).
3. **PREWRITE-PAUSE still owns `table1Confirmed` and `specConfirmed`.** Infer-design does not implement those flags. Those flags must not become true against a missing or draft design, and must not become true for `method=did` when the interaction is missing (DID-BE-spec).
4. **Fail closed on crossed flags.** If `table1Confirmed` / `specConfirmed` / estimate are requested without a confirmed design, return to infer-design confirm. If they are requested without `dataAttached`, return to confirm-attach. Do not invent the missing gate.
5. **Independence.** `dataAttached` does not confirm a design. Confirming a design does not set `dataAttached`. A catalog highlight does not do either.

### 5.3 What may happen before confirm-design

- Shaping or pinning the title / RQ
- Emitting and editing a **draft**
- Opening an attach panel in a **candidates-only** mode (no ranked-as-authoritative match, no auto-select, no `dataAttached`)

What must not happen before confirm-design:

- DC suggest that claims a confirmed-design match or auto-selects a fixture
- Catalog → `allow_did` or catalog → locked spec
- `table1Confirmed` / `specConfirmed` / estimate / chapter write

---

## 6. Fixtures / classic-5 — candidates only

### 6.1 What catalog is after DECIDE-6

DECIDE-6 lock (verbatim): **Fixtures/catalog = candidates only, never answer key.**

`classic-5` remains the named built-in catalog for formal-path find/select (`docs/data-completion-contract.md` §3). Landed ranking tokens include `ck1994_long` (Card–Krueger minwage) and `barro1991_growth` (Barro growth), plus the other `fixtures/classic-5/catalog.json` ids. They are never an answer key, never a gold-body source, and never a DiD key.

After infer-design confirm, DC-BE-suggest **may list** those entries as **candidates matching the confirmed design** (method + topic / outcome / treatment slots, plus title/RQ text). Example: a confirmed DiD minwage design may list `ck1994_long`; a confirmed OLS growth design may list `barro1991_growth`.

### 6.2 How catalog must not be used

- Not auto-selected
- Not prefilled as success / as the user’s own study
- Not `dataAttached` by mere suggest or highlight
- Not a locked spec (`catalog → session.design.confirmed`)
- Not a DiD key (`catalog → allow_did`)
- Not a gold-body / six-chapter fill
- Not Card 1995 (`/demos/card`) and not `teaching_case=card_1995`
- Not committed private / restricted microdata

Suggest **must not** attach. Attach **must not** invent ranking. Selecting a candidate **must not** set `dataAttached` or confirm a design.

`session.design.catalog_entry_id` stays `null`. Provenance after a later confirm-attach may record `source: "classic-5"` + entry id on the **dataset**, not as the design lock.

---

## 7. DiD narrow-exception rewrite — deprecate catalog-token `allow_did`

### 7.1 What DECIDE-5 A froze, and what DECIDE-6 changes

`docs/did-narrow-exception-contract.md` (DECIDE-5 A) froze `allow_did` default false and allowed **only** a title/catalog gate (Card–Krueger / minwage TITLE/TOPIC or catalog identity `minimum-wage-employment` / `ck1994` / `ck1994_long`) to set true. Form `method=did` was **not** the setter.

**DECIDE-6 withdraws catalog identity (and catalog-token `allow_did`) as the source of truth.** Later DID-BE-gate slices must stop treating those tokens as a DiD unlock.

Unchanged from DECIDE-5 A (still frozen):

- Formal path stays OLS-locked **unless** this exception applies
- The exception is still **narrow 2×2 DiD**, not general TWFE / event-study / staggered / Callaway–Sant'Anna / Goodman-Bacon
- Card 1995 teaching case is **not** this exception
- `barro1991_growth` / schooling–wages / other classic-5 ids are **not** a DiD unlock
- When DiD is in play, treated×period (or equivalent) is required or **hard block**
- OLS lock elsewhere stays in `agent/engine/ols_lock.py` (issue #24); this file does not rewrite that module into a general TWFE unlock

### 7.2 New DiD permission (frozen)

DiD is allowed iff **all** of:

1. `session.design.status === "confirmed"`
2. Confirmed `design.method=did` (or an existing `norm_method` equivalent)
3. The confirmed design includes the required **treated×period** interaction (§2.4)

Otherwise DiD is not allowed. Fail closed.

| Input | DiD allowed? |
|---|---|
| Catalog `ck1994` / `ck1994_long` / `minimum-wage-employment` alone | No |
| Title/RQ matcher hit, design still draft | No |
| Confirmed `method=ols` (even if a minwage CSV is later attached) | No |
| Confirmed `method=did` **without** treated×period | No — **hard block** (DID-BE-spec) |
| Confirmed `method=did` **with** treated×period; catalog none / `barro1991_growth` / user file | Yes (narrow 2×2 only), still needs `dataAttached` + PREWRITE-PAUSE |
| Form / `research_direction.method=did` while design unconfirmed | No |
| `id_col` + `time_col` / `| entity + time` without confirmed DiD + interaction | No |

`allow_did` as a **derived projection** of the three conditions above is optional for later slices. Catalog-token `allow_did` (`catalog_identity_allows`, `MINWAGE_ENTRY_IDS`, `entry.allow_did` in `catalog.json`) is **deprecated** and must not be the setter.

### 7.3 Hard block — DID-BE-spec (unchanged duty, new trigger)

If confirmed `method=did` (or equivalent) and the spec / design has no treated×period (or equivalent) main term:

| Surface | Frozen refusal |
|---|---|
| Spec confirm (`specConfirmed`) | Must not become true. Return to equation / 题型→设定. |
| `POST /sessions/{id}/direction` that would run estimate | Refuse. Do not start estimate. |
| Estimate / `mainResults` | Do not run. Do not invent a coefficient. |
| Generate-chapter / six-chapter write | Do not write as if DiD ran. |
| Code export | Do not emit feols / xtreg / reghdfe / TWFE for this session. |

Fail closed. Same family as heterogeneity × no-interaction. Missing required interaction **blocks**; it does not degrade to silent OLS or silent TWFE.

DID-BE-spec owns the check. Trigger = **confirmed DiD design**, not catalog `allow_did`. G0 does not add the error code.

### 7.4 When DiD is not allowed

OLS lock holds. Direction, estimate, prompts, generate-chapter, and export stay on OLS / regress / lm. They must not inject or claim 双向固定效应 / TWFE / feols / xtreg / reghdfe / felm.

A user who typed DiD on the form, attached `ck1994_long`, or has a panel CSV, still does not get TWFE without a **confirmed** DiD design **and** the interaction.

IV / RD / SCM stay on their existing non-OLS paths. This file does not reopen them.

---

## 8. Acceptance criteria (DECIDE-6; verbatim)

G0 does not add tests. Later INF / DID / DC slices **must** implement and show these acceptance criteria. Text below is **verbatim** from Decide (via Firstmate). Do **not** evaluate by reading gold chapter bodies.

1. CK-class title only → engine proposes DiD with treated×period BEFORE any ck attach
2. Rename/remove fixture → still can propose; catalog id alone cannot open DiD
3. Level OLS title → proposes OLS; must not open DiD from catalog
4. Unconfirmed design cannot jump to gold/classic prefilled spec
5. After confirm → suggest matches design → attach → direction/pause continues

### 8.1 How later slices bind those bullets (not substitutes)

| # | Gate reading | Fail (unacceptable substitute) |
|---|---|---|
| 1 | Title/question only. Propose writes `design.method=did` plus a treated×period slot **before** any `ck1994` / `ck1994_long` attach, suggest-select, or `dataAttached`. | Wait for ck attach; catalog → `allow_did`; gold-body read; auto-confirm. |
| 2 | After the fixture is renamed or removed, title/question still proposes. Catalog id (`ck1994`, `ck1994_long`, `minimum-wage-employment`, …) alone cannot open DiD. | `catalog_identity_allows` / `allow_did_for(entry_id=…)` as the win path; propose requires the fixture file. |
| 3 | Level OLS title (schooling–wages, Barro growth, …) proposes `method=ols`. Catalog must not open DiD. | Catalog token flips DiD; OLS title emits `method=did`. |
| 4 | Missing or `status=draft` design cannot jump to gold / classic prefilled spec, gold chapter bodies, or locked `main_specification`. | Unconfirmed → gold-body read; classic prefill as success; `set_direction` from catalog. |
| 5 | After human confirm: suggest matches the **confirmed** design (candidates only, never answer key) → attach (`dataAttached`) → direction / prewrite pauses continue. | Suggest without confirm as authoritative match; skip attach; skip pauses; gold-body read. |

OLS remains the default when DiD is not allowed. Heterogeneity × no-interaction stays a hard block. Missing treated×period when `design.method=did` stays a DID-BE-spec hard block (§7.3).

---

## 9. Later parallel slices (do not implement in G0)

G0 owns **only** `docs/infer-design-contract.md`.

| Slice | Owns | Must not write |
|---|---|---|
| **INF-BE-propose** | Title (+ optional RQ) → `session.design` **draft**. Title-first. | Confirm lock, attach / `dataAttached`, catalog auto-select, `allow_did` from entry id, chapter bodies, FE chrome, PREWRITE-PAUSE flags |
| **INF-BE-confirm** | User confirm → lock `session.design`. Project onto direction/spec **only** as a confirmed object. | Propose ranking ownership, attach, catalog CSV bytes, estimate, gold bodies, `table1Confirmed` / `specConfirmed` |
| **INF-FE-review** (optional) | Show draft fields and the confirm CTA. | Second product line, sketch chrome, backend routes, attach-panel ownership, Table1 / equation pause UI |
| **DID-BE-gate** (rewrite) | DiD permission from **confirmed** `method=did` + interaction. Remove catalog-token `allow_did` as source of truth. | General TWFE unlock, classic-5 CSV bytes, FE beyond an optional one-line hint, WORD-FIX |
| **DID-BE-spec** | Confirmed DiD ⇒ require treated×period. Missing → hard block. | Catalog matcher ownership, staggered / CS / Bacon, export/docx |
| **DC-BE-suggest** (align) | Rank classic-5 **candidates** against the **confirmed** design. Without confirm: fail or candidates-only. | Confirm-attach, `dataAttached` writes, auto-select, gold bodies |

Slices stay **write-set-disjoint**. Shared types go through existing OpenAPI codegen (`make gen-api` / `check-api-drift`) when a slice changes a public shape. G0 changes no shapes.

**INF-FE-review alignment (frozen):** optional. Absence of the review chrome does not change the backend gates. Confirm is still required.

---

## 10. Concurrent write-sets (stay out)

| External slice | Lives at | This contract must not touch |
|---|---|---|
| **DATA-COMPLETE** | `docs/data-completion-contract.md`; `dataAttached`; DC-BE-attach / DC-FE-\* | Confirm-attach, upload readiness, attach-panel chrome. Suggest **alignment** is named only (§9). **Do not merge** those branches in G0. |
| **PREWRITE-PAUSE** | `table1Confirmed` + `specConfirmed`; `blockingDecision`; `docs/api/prewrite-confirm.md` | Implementing those flags, freeze/reveal, estimate-prep UI |
| **DID-NARROW (DECIDE-5 A code)** | `docs/did-narrow-exception-contract.md`; `backend/services/allow_did.py` on DID-BE-gate branches | Merging that branch; keeping catalog-token `allow_did` as truth. G0 documents the rewrite only. |
| **CLASSIC-FIXTURES** | `fixtures/classic-5/` CSV / DTA / XLSX **content** and hashes | Adding, editing, or renaming catalog **bytes**. Ranking ids are cited only. |
| **OLS lock** | `agent/engine/ols_lock.py`; generate-chapter / estimate / prompts; issue #24 | Rewriting the lock into general TWFE; sanitizer / prompt-lock edits |
| **HET-CODE-EXPORT** | Heterogeneity × interaction hard-block | `educ×region` policy ownership, results-chapter lock |
| **WORD-FIX** | docx math export samples | Export nodes, math samples, chapter body fill |
| **Card canonical** | `/demos/card`, ADR-0015 | Teaching seed, Evidence Lab |

Also do not reopen: generic spine, localized-first-study, upload-recovery, run-execution DESIGN.

Reuse, do not fork: `norm_method` / `DirectionSpec` field names, `dataAttached`, snapshot `dataset`, PREWRITE-PAUSE flag names. Add `session.design` as the design lock — do not replace `dataAttached`, and do not treat catalog id as `session.design`.

---

## 11. G0 done rule

- File present: `docs/infer-design-contract.md`
- Folded: DECIDE-6 order / locks / five accept bullets (verbatim, §0 + §8); title-first propose (Y/X/interactions/method) → human confirm → data candidates → attach → prewrite pauses; fixtures/catalog = candidates only, never answer key; DiD only from confirmed `design.method=did` + treated×period; NO catalog-id `allow_did`; OLS default elsewhere; het interaction hard-block still; **no gold body reads**
- No application code, API routes, frontend, fixtures, OpenAPI, or OLS-lock change in G0
- No merge of old DATA-COMPLETE / DID-NARROW implementation branches
- No pull request from this slice
- Later slices cite this file; they do not rewrite §2–§7 without a new serial contract

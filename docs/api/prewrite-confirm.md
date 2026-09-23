# Prewrite estimate confirm (FM-E-BUILD-PREWRITE-PAUSE-1)

Human pause **after direction is accepted** and **before estimate**.
StatsPAI / `estimate` code is unchanged; the workbench path only inserts a stop
gate plus the two FE confirm flags from FM-E-DESIGN-ENTRY-GUIDE-1.

## Sequence

1. `POST /sessions/{session_id}/direction` (existing, still 202 + durable run)
   - Runs `set_direction` → `identification_verify`.
   - If identification fails or is 0-star: stop as before. No estimate.
   - If identification accepts: compute **Table 1** descriptives and the
     **main specification equation text**, persist them, set
     `prewrite_gate = "awaiting_estimate"`, emit
     `table1Confirmed=false` / `specConfirmed=false` / `blockingDecision`,
     and **do not** run estimate → robustness → literature → title → outline.
2. Client shows Table 1, then the equation + 题型→设定 screen.
3. Person continues only after **both** CTAs:
   - Table 1 confirm → `table1Confirmed`
   - Equation / 题型→设定 confirm → `specConfirmed`
4. `POST /sessions/{session_id}/prewrite/confirm` records flags and, when both
   are true and not hard-blocked, enqueues estimate.

### Version binding (FORMAL-CONFIRMATION-CHAIN-2)

From this batch on, an approval names the object it approved:

- a confirm is only accepted when the generated **Table 1 and equation are the
  current preview**: `preview_identity = f(design projection, dataset
  revision, main specification, Table 1, equation)`. Confirmations carry that
  identity; a moved preview leaves them behind instead of silently approving
  the new one. There is no preview → **409 `preview_not_ready`**.
- the **sample (Table 1) confirmation comes first**; a setting confirmation
  without a current sample confirmation is **409
  `sample_confirmation_required`**.
- stored `table1Confirmed` / `specConfirmed` are **projections** of the
  version-bound records, so a `true` from an earlier preview cannot start an
  estimate: `continue_estimate` recomputes them and answers **409
  `confirmation_stale`** when approvals no longer name the current version.
- a new design draft (`POST /sessions/{id}/design/propose`), new data
  (`/attach`, `/upload`) or new cleaning/sample rules (`/transform`,
  `/filter`) revoke the affected approvals and clear the live preview
  (Table 1, equation, `awaiting_estimate`, both flags). The previous version
  is archived in the session's `formal_chain.history`, not deleted, and the
  direction must be re-run with the same content as the confirmed design
  (`POST /direction` answers **409 `design_execution_mismatch`** otherwise).
- `Idempotency-Key` is a delivery credential for each of these write
  endpoints: repeating the same intention returns the same run / the same
  recorded gate and never writes a second run or a second confirmation.
- `POST /sessions/{id}/design/confirm` optionally takes the draft revision the
  client was looking at: `{"expectedRevision": design.proposed_at}`. The lock is
  refused with **409 `design_revision_mismatch`** (`detail.expected` /
  `detail.submitted`) when the session now holds a different draft, so another
  window cannot make the user approve a version they never saw. Omitting the
  field keeps the previous behaviour.
- `#40` tri-state permission is consumed at the estimate entry:
  `forbid` never opens (hard block), `confirm` needs a risk decision —
  `{"action": "record_confirms", "riskConfirmed": true}` — bound to the
  **diagnosis and design it was made about** (**409
  `risk_confirmation_required`** otherwise), and an unknown assessment is
  `allow` and adds no gate of its own.

The LangGraph batch path (`graph.invoke`) still runs the full
`PRWRITE_SEQUENCE`. The workbench HITL path is `run_prewrite(until=…)` /
`run_prewrite(resume_from=…)`.

## How a person continues

```
POST /sessions/{session_id}/prewrite/confirm
Idempotency-Key: <client-generated, required, 1–200 chars>
Content-Type: application/json
```

### Record one CTA (200, estimate does **not** start)

Table 1 CTA:

```json
{
  "action": "record_confirms",
  "table1Confirmed": true
}
```

Equation + 题型→设定 CTA:

```json
{
  "action": "record_confirms",
  "specConfirmed": true,
  "qType": "heterogeneity",
  "specMode": "interaction"
}
```

### Run estimate (202) — both flags required

```json
{
  "action": "continue_estimate",
  "qType": "heterogeneity",
  "specMode": "interaction"
}
```

If both confirms were already **recorded and are still bound to the current
version**, `{ "action": "continue_estimate" }` is enough. Flags sent on this
call do not create an approval (that is what `record_confirms` is for); the
server recomputes both from the version-bound records.

| Field | Type | Required | Default | Meaning |
|-------|------|----------|---------|---------|
| `action` | `"record_confirms"` \| `"continue_estimate"` | no | `continue_estimate` | Record flags only, or enqueue estimate |
| `table1Confirmed` | bool | no | `false` | Table 1 CTA (records the sample confirmation, bound to the current preview) |
| `specConfirmed` | bool | no | `false` | Equation + 题型→设定 CTA (requires the sample confirmation first) |
| `riskConfirmed` | bool | no | `false` | Explicit #40 risk decision, bound to the current diagnosis + design |
| `qType` | `"average"` \| `"heterogeneity"` \| `"causal"` | no | persisted / direction | 题型 |
| `specMode` | `"interaction"` \| `"level"` | no | inferred from formula | 设定是否含交互 |
| `hasInteraction` | bool | no | inferred | Explicit educ×region / `*` / `:` / `×` |

Do **not** send outline edits here. Outline HITL remains
`POST /sessions/{session_id}/resume` with `{ "outline": [...] }`.

### Success

`record_confirms` → **200** `PrewriteGateResponse`:

```json
{
  "ok": true,
  "prewrite_gate": "awaiting_estimate",
  "table1Confirmed": true,
  "specConfirmed": false,
  "qType": "heterogeneity",
  "specMode": "level",
  "blockingDecision": {
    "blocked": true,
    "isBlock": true,
    "code": "heterogeneity_missing_interaction",
    "reason": "题型是异质性，但设定没有交互项（educ×region）。请改设定或改题型。",
    "qType": "heterogeneity",
    "specMode": "level",
    "hasInteraction": false
  },
  "table1": { "produced_by": "prewrite_preview", "columns": [], "rows": [] },
  "specification_equation": "ln_wage = β₀ + β₁ educ + ε"
}
```

`continue_estimate` → **202** same envelope as `POST /direction`:

```json
{
  "run_id": "…",
  "session_id": "…",
  "status": "PENDING",
  "events_url": "/api/runs/{run_id}/events"
}
```

### Hard block

`qType === heterogeneity` **and** the setting has no interaction
(`specMode !== "interaction"` and formula/equation has no `educ×region` /
`educ:region` / `educ*region`). Estimate does not run.

- Snapshot `blockingDecision.blocked` / `isBlock` = true
- `write_blockers` includes `heterogeneity_missing_interaction`
- `continue_estimate` and `specConfirmed: true` return **409**
  `code=estimate_blocked` with the same `blockingDecision`

Change `specMode` to `interaction` (or put an interaction in the formula), or
change `qType` away from `heterogeneity`, then confirm again.

### Errors

| Status | `detail.code` | When |
|--------|----------------|------|
| 409 | `confirms_incomplete` | continue without a sample + setting confirmation |
| 409 | `preview_not_ready` | no generated Table 1 / equation to confirm |
| 409 | `sample_confirmation_required` | setting confirmed before (or without) the current sample confirmation |
| 409 | `confirmation_stale` | stored confirms no longer name the current design/dataset/preview |
| 409 | `risk_confirmation_required` | `permissions.continue_to_estimate === "confirm"` and no current risk decision |
| 409 | `risk_confirmation_not_applicable` | risk decision without a diagnosis to bind it to |
| 409 | `design_execution_mismatch` | `/direction` payload contradicts the confirmed design (extra keys `field`, `expected`, `submitted`) |
| 409 | `estimate_blocked` | heterogeneity × no interaction (`blockingDecision` attached) |
| 409 | `prewrite_not_ready` | No direction, or identification never ran |
| 409 | `identification_blocked` | 0-star or `identification_failed` |
| 409 | `session_busy` | Another durable run is active |
| 404 | — | Session missing |
| 429 | — | Run queue full (`Retry-After: 5`) |

## Snapshot fields after direction

`GET /sessions/{session_id}` and a succeeded direction-run result include:

| Field | Meaning |
|-------|---------|
| `prewrite_gate` | `awaiting_estimate` after direction; `estimate_complete` after continue |
| `table1` | descriptives for spec columns |
| `specification_equation` | Display equation |
| `main_specification` | Spec from `set_direction` |
| `table1Confirmed` | Table 1 CTA recorded **for the current preview** |
| `specConfirmed` | Equation / 题型→设定 CTA recorded **for the current preview** |
| `riskConfirmed` | a current #40 risk decision is on file for this diagnosis + design |
| `permissions` | #40 tri-state permission per action (`allow` / `confirm` / `forbid`) |
| `session_kind` | `formal` / `legacy` / `card_teaching` (new sessions are stamped `formal`) |
| `qType` | `average` / `heterogeneity` / `causal` |
| `specMode` | `interaction` / `level` |
| `blockingDecision` | `{blocked, isBlock, code, reason, qType, specMode, hasInteraction}` |

## Agent API

```python
from agent.engine.prewrite import run_prewrite
from agent.engine.prewrite_gates import evaluate_blocking_decision

run_prewrite(state, until="identification_verify")
run_prewrite(state, resume_from="run_estimate")
evaluate_blocking_decision(state, {"qType": "heterogeneity", "specMode": "level"})
```

OpenAPI: `PrewriteConfirmRequest`, `PrewriteGateResponse`,
`BlockingDecisionResponse` on `POST /sessions/{session_id}/prewrite/confirm`.
Generate with `make gen-api`.

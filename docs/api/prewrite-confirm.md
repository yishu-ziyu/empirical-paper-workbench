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
  "table1Confirmed": true,
  "specConfirmed": true,
  "qType": "heterogeneity",
  "specMode": "interaction"
}
```

If both flags were already recorded, `{ "action": "continue_estimate" }` is enough.

| Field | Type | Required | Default | Meaning |
|-------|------|----------|---------|---------|
| `action` | `"record_confirms"` \| `"continue_estimate"` | no | `continue_estimate` | Record flags only, or enqueue estimate |
| `table1Confirmed` | bool | for continue | `false` | Table 1 CTA |
| `specConfirmed` | bool | for continue | `false` | Equation + 题型→设定 CTA |
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
| 409 | `confirms_incomplete` | continue without both `table1Confirmed` and `specConfirmed` |
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
| `table1Confirmed` | Table 1 CTA recorded |
| `specConfirmed` | Equation / 题型→设定 CTA recorded |
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

# Prewrite estimate confirm (FM-E-BUILD-PREWRITE-PAUSE-1)

Human pause **after direction is accepted** and **before estimate**.
StatsPAI / `estimate` code is unchanged; the workbench path only inserts a stop
gate. Design owns the confirm UI later. This note is the backend/agent contract.

## Sequence

1. `POST /sessions/{session_id}/direction` (existing, still 202 + durable run)
   - Runs `set_direction` → `identification_verify`.
   - If identification fails or is 0-star: stop as before. No estimate.
   - If identification accepts: compute **Table 1** descriptives and the
     **main specification equation text**, persist them, set
     `prewrite_gate = "awaiting_estimate"`, and **do not** run
     estimate → robustness → literature → title → outline.
2. Client reads `GET /sessions/{session_id}` (or the succeeded direction run
   result) and shows `table1` + `specification_equation`.
3. Person continues with `POST /sessions/{session_id}/prewrite/confirm`.
   That enqueues a second durable `prewrite` run that starts at `run_estimate`.

The LangGraph batch path (`graph.invoke`) still runs the full
`PRWRITE_SEQUENCE`. The workbench HITL path is `run_prewrite(until=…)` /
`run_prewrite(resume_from=…)`.

## How a person continues

```
POST /sessions/{session_id}/prewrite/confirm
Idempotency-Key: <client-generated, required, 1–200 chars>
Content-Type: application/json
```

### Request payload

```json
{
  "action": "continue_estimate"
}
```

| Field | Type | Required | Default | Meaning |
|-------|------|----------|---------|---------|
| `action` | `"continue_estimate"` | no | `continue_estimate` | Only supported confirm action. `{}` is accepted. |

Do **not** send outline edits here. Outline HITL remains
`POST /sessions/{session_id}/resume` with `{ "outline": [...] }`.

### Success (202)

Same envelope as `POST /direction`:

```json
{
  "run_id": "…",
  "session_id": "…",
  "status": "PENDING",
  "events_url": "/api/runs/{run_id}/events"
}
```

Subscribe to `events_url`. Terminal `GET /runs/{run_id}` result is the usual
instrument projection (`estimate`, `outline`, `prewrite_gate="estimate_complete"`).

### Errors

| Status | `detail.code` | When |
|--------|----------------|------|
| 409 | `prewrite_not_ready` | No direction, or identification never ran (`reason`: `no_direction` / `no_identification`) |
| 409 | `identification_blocked` | 0-star or `identification_failed` |
| 409 | `session_busy` | Another durable run is active (`run_id` attached) |
| 404 | — | Session missing |
| 429 | — | Run queue full (`Retry-After: 5`) |

## Snapshot fields after direction

`GET /sessions/{session_id}` and a succeeded direction-run result now include:

| Field | Meaning |
|-------|---------|
| `prewrite_gate` | `awaiting_estimate` after direction; `estimate_complete` after confirm |
| `table1` | `{produced_by, columns, rows, n, variables, reason?}` descriptives for spec columns |
| `specification_equation` | Display equation, e.g. `income = β₀ + β₁ age + ε` |
| `main_specification` | Spec written by `set_direction` (formula / method / columns) |

`table1.rows[]` columns: `variable`, `count`, `mean`, `std`, `min`, `max`,
`missing`, `role` (`outcome` / `treatment` / `control` / `instrument` / …).

## Agent API

```python
from agent.engine.prewrite import run_prewrite

# Workbench direction (facade.execute_prewrite default)
run_prewrite(state, until="identification_verify")

# Workbench confirm
run_prewrite(state, resume_from="run_estimate")

# Full sequence (graph / existing agent tests)
run_prewrite(state)
```

OpenAPI: `PrewriteConfirmRequest` on
`POST /sessions/{session_id}/prewrite/confirm`.
Generate with `make gen-api`.

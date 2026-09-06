# M2 implementer summary — Card Canonical Research Experience

Date: 2026-09-06  
Branch: `review/workbench-v2`  
Hard bar: C9–C16 programmatic parts in `docs/acceptance/card-canonical-research-experience.md`

## Change

After freeze, a researcher can enqueue one durable `spec_run` that executes the admissible Card specifications as immutable `SpecificationRun`s, see them in Evidence Lab (results space + choice matrix + compare), get a deterministic Surprise, and accept one Next-best Challenge. Preview/spec_run never writes `state.estimate`; only Promote (or existing prewrite) does.

## Files changed

Backend

- `backend/services/research_lab.py` — formula mapping, surprise, compare, promote/revert, lab merge, strip helper
- `backend/services/spec_run.py` — calls `_estimate_ols` / `_estimate_iv` on a temporary spec dict; IV F via `effective_f_test(..., exog=controls, vcov="HC1")`
- `backend/routers/research.py` — space run, spec run, compare, promote, revert, challenge accept
- `backend/run_repository.py` — `spec_run` kind; complete() strips canonical keys and merges `research_lab`
- `backend/runner.py` — dispatch `spec_run`
- `backend/models/run.py`, `backend/database.py` — CHECK includes `spec_run`
- `backend/schemas/responses.py`, `backend/routers/run_execution.py` — kinds + public spec_run result
- `backend/tests/test_card_spec_run.py`

Frontend

- `frontend/src/components/EvidenceLab.tsx` — SVG results space, matrix, compare, surprise, challenge
- `frontend/src/components/ResearchLabPanels.tsx` — Run specifications after freeze
- `frontend/src/components/WorkbenchArtifact.tsx` — Evidence Lab when lab runs exist
- `frontend/src/lib/workspace.ts` — run-space / spec / compare / promote / revert / challenge commands
- `frontend/src/App.tsx` — CTA after freeze; Unexpected after surprise
- tests: EvidenceLab; generated OpenAPI types

## Commands run

| Command | Result |
|---|---|
| `make gen-api` | pass |
| `make test-backend` | pass — 409 passed, 8 skipped (no new skip) |
| `make test-frontend` | pass — 328 passed |
| `make test-agent` | pass — 805 passed, 1 skipped |
| `make check-api-drift` | pass |
| `cd frontend && npm run build` | pass (`tsc -b && vite build`) |

## API payload examples

`POST /sessions/{id}/research/specification-space/run` (202, requires freeze):

```json
{
  "run_id": "<uuid>",
  "session_id": "<uuid>",
  "status": "PENDING",
  "events_url": "/api/runs/<run_id>/events"
}
```

Unfrozen → 409.

`GET /sessions/{id}/research` after the spec_run succeeds (excerpt):

```json
{
  "specification_runs": [
    {
      "id": "<producer_run_id>:ols_region_dummies",
      "spec_id": "ols_region_dummies",
      "choices": [{"dimension": "estimator", "value": "ols"}, "..."],
      "estimator": "statspai.feols",
      "formula": "lwage ~ educ + exper + expersq + black + smsa + south + smsa66 + reg661 + … + reg668",
      "covariance": "HC1",
      "analysis_dataset": {"path": "...", "hash": "...", "role": "raw"},
      "producer_run_id": "<uuid>",
      "coef": 0.0746,
      "se": 0.0035,
      "p": 0.0,
      "n": 3010,
      "status": "ok",
      "relation": "exploratory",
      "created_at": "2026-09-06T..."
    },
    {
      "spec_id": "iv_region_dummies",
      "estimator": "statspai.ivreg",
      "formula": "lwage ~ (educ ~ nearc4) + exper + expersq + black + smsa + south + smsa66 + … + reg668",
      "covariance": "nonrobust",
      "diagnostics": {
        "test": "effective_f_test",
        "F_eff": 14.14,
        "first_stage_F": 13.26,
        "covariance": "HC1",
        "controls": ["exper", "expersq", "black", "smsa", "south", "smsa66", "reg661", "…"]
      },
      "relation": "exploratory"
    }
  ],
  "surprise": {
    "status": "Unexpected",
    "kind": "ordering_mismatch",
    "expected": "IV may be smaller than OLS",
    "observed": "IV > OLS"
  },
  "next_challenge": {
    "id": "challenge.instrument_strength",
    "target": "instrument_strength",
    "status": "proposed"
  }
}
```

Exact coef / F are whatever `_estimate_ols` / `_estimate_iv` / `effective_f_test` return on the loaded extract. Tests recompute the same formula instead of pinning 0.0747 / 0.1315 / 14.214.

`POST .../research/compare` `{ "a": "ols_region_dummies", "b": "iv_region_dummies" }`:

```json
{
  "coef_a": 0.0746,
  "coef_b": 0.1315,
  "delta_abs": 0.0568,
  "delta_pct": 76.1,
  "changed": [{"dimension": "estimator", "a": "ols", "b": "iv"}, {"dimension": "identification", "a": "none", "b": "nearc4"}],
  "why_moved": "Identification strategy changed",
  "intent": "Identification strategy changed"
}
```

`POST .../research/preview/promote` `{ "run_id": "<specification_run id>" }` copies that run into `state.estimate` with `produced_by=estimate` and `source_run_id` of the spec_run. `POST .../preview/revert` restores the previous estimate from `canonical_history`.

`POST .../research/challenges/{id}/accept` enqueues a preview `spec_run` of the proposed spec.

## Checks

- C9: ≥2 real Card OLS/IV runs with required fields; independent recompute of the same formula.
- C10: seeded canonical estimate survives preview; poison result with top-level `estimate` is stripped before complete().
- C11: promote updates estimate + decision; revert restores the seed.
- C12: Evidence Lab renders points, matrix, compare from research payload.
- C13: compare changed choices include estimator/identification; intent is identification strategy.
- C14: surprise pure function — direction / ordering / magnitude; Card default → Unexpected / ordering_mismatch.
- C15: next_challenge present; accept produces a preview spec_run.
- C16: IV F from controlled `effective_f_test` (~14 on 34-col, not ~63); 9-col does not emit region dummy runs.

## Remaining risks

- `spec_run` complete() merges `research_lab` instead of generic CAS so expectation edits during the run are kept; concurrent spec_runs are still blocked by the single active-run index.
- OLS covariance label is recorded as `HC1` (feols default SEs in this stack); IV point-estimate covariance is `nonrobust` (ivreg default). F uses HC1 with spec controls.
- Browser journey (C25) is not this milestone.

## What this did not do

- M3 Agent Cursor / SemanticTargetRegistry (ids `evidence.spec.ols` / `evidence.spec.iv` are on the SVG points for later)
- M4 Claim Ledger / Paper Results rewrite
- Changing OLS/IV math in `agent/nodes/estimate.py`
- Frontend coefficient literals

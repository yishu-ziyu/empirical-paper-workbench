# M1 implementer summary — Card Canonical Research Experience

Date: 2026-09-06  
Branch: `review/workbench-v2`  
Hard bar: C1–C8 programmatic parts in `docs/acceptance/card-canonical-research-experience.md`

## Change

A researcher can leave the empty desk via `Try a real study · Card`, land in a real session whose Question, Expectation, and Admissible Specification Space live in `ResearchSession.state.research_lab`, and recover that lab from `GET /sessions/{id}` after refresh / clearing frontend storage (session id only).

## Files changed

Backend

- `backend/services/research_lab.py` — lab blob, Card seed, expectation versioning, freeze, re-attach helper
- `backend/services/card_demo.py` — Card extract loader + admit through existing upload pipeline
- `backend/routers/research.py` — `POST /demos/card`, `GET /sessions/{id}/research`, `PUT .../expectation`, `POST .../specification-space/freeze`
- `backend/routers/sessions.py` — additive `snapshot.research`
- `backend/schemas/responses.py` — research models on snapshot
- `backend/main.py` — mount research router
- `backend/runner.py` — re-attach `research_lab` if upload result dropped it
- `backend/tests/test_card_research_lab.py`

Frontend

- `frontend/src/pages/DeskPage.tsx` — `data-testid="desk-try-card"`
- `frontend/src/App.tsx` — wires `handleTryCard`
- `frontend/src/lib/workspace.ts` — demo boot (not `SAMPLE_CSV`), snapshot.research, expectation/freeze commands
- `frontend/src/components/WorkbenchArtifact.tsx` — question card, expectation editor, spec space / freeze
- `frontend/src/components/ResearchLabPanels.tsx`
- tests: DeskPage, App, SnapshotRecovery, WorkbenchArtifact, cardCanonicalLiterals
- generated: `frontend/openapi.json`, `frontend/src/types/api.ts`, `docs/api/openapi.json`

## Commands run

| Command | Result |
|---|---|
| `make gen-api` | pass |
| `make test-backend` | pass — 396 passed, 8 skipped (no new skip; +7 Card tests) |
| `make test-frontend` | pass — 327 passed |
| `make test-agent` | pass — 805 passed, 1 skipped |
| `make check-api-drift` | pass |
| `cd frontend && npm run build` | pass (`tsc -b && vite build`) |

C1 programmatic: `npx vitest run src/__tests__/DeskPage.test.tsx src/__tests__/App.test.tsx` covered in the frontend suite.

## API payload examples

`POST /demos/card` (202), `Idempotency-Key` required:

```json
{
  "session_id": "<uuid>",
  "run_id": "<uuid>",
  "status": "PENDING",
  "events_url": "/api/runs/<run_id>/events",
  "dataset_meta": {
    "name": "card_1995.csv",
    "rows": 3010,
    "columns": ["lwage", "educ", "nearc4", "exper", "expersq", "black", "smsa", "south"]
  }
}
```

`GET /sessions/{id}.research` / `GET /sessions/{id}/research` (same object when lab exists):

```json
{
  "teaching_case": "card_1995",
  "provenance": {
    "source": "statspai:papers/data_card1995.csv",
    "citation": "Card, D. (1995). Using Geographic Variation in College Proximity to Estimate the Return to Schooling.",
    "checksum": "<sha256>",
    "redistribution": "runtime load from StatsPAI dependency, no second public copy",
    "extract_kind": "wooldridge_card_34"
  },
  "question": {
    "prompt_en": "Does education increase earnings?",
    "prompt_zh": "教育是否提高工资?",
    "outcome": { "name": "lwage", "label": "Log wage", "gloss": "对数工资" },
    "treatment": { "name": "educ", "label": "Years of education", "gloss": "受教育年限" },
    "causal_threat": { "id": "ability_family", "label": "Ability and family background" },
    "identification": { "instrument": "nearc4", "label": "College proximity (nearc4)" },
    "estimand": { "ols": "OLS association: ...", "iv": "IV local causal return: ..." }
  },
  "expectation": {
    "text": "I expect OLS to be positive. If ability creates upward bias, IV may be smaller.",
    "confidence": "medium",
    "version": 1,
    "history": [{ "kind": "seed", "version": 1 }]
  },
  "specification_space": {
    "status": "proposed",
    "frozen_at": null,
    "frozen_before_results": false,
    "definitions": [/* 12 specs; region dummies unavailable on 9-col extract */]
  }
}
```

`PUT /sessions/{id}/research/expectation`:

```json
{ "text": "OLS positive; IV may be smaller if ability biases upward.", "confidence": "high", "locale": "en" }
```

`POST /sessions/{id}/research/specification-space/freeze` sets `frozen_at` and `frozen_before_results=true` when no spec runs exist.

## Architecture notes

- Truth owner is backend `state.research_lab`. No new database.
- Card bytes go through `admit_upload` / `upload_pipeline` (same as a normal CSV). Frontend subscribes to `events_url` the same way.
- Loader: `ECONPAPER_CARD_CSV` → StatsPAI `papers/data_card1995.csv` (34-col) → `statspai.datasets.card_1995(simulated=False)` (9-col). `ECONPAPER_CARD_EXTRACT=statspai_card_9` forces the 9-col path.
- If the upload worker result drops unknown keys, `runner.process_one_run` re-attaches `research_lab` from the admitted initial state (proven by test).
- `GET /sessions/{id}/evidence` is unchanged (canonical estimate only).

## Remaining risks

- Browser C8 walk (empty desk → freeze, 1280/1440, no new uncaught errors) is not executed here; programmatic C1–C8 are green.
- Cleaning still runs asynchronously after boot; lab is already on the session at admit, so refresh works before the upload run finishes.
- 34-col extract is a sibling StatsPAI file, not vendored. Machines without it still boot via the 9-col bundled extract; region dummy specs are `unavailable`, not fake-ran.
- Snapshot `research` is omitted (`null`) when no lab exists; GET `/research` returns an empty `ResearchLabResponse`. They match on Card sessions.

## What this milestone did not do

- spec_run execution / OLS-IV runs
- Evidence Lab charts / compare
- Surprise / Challenge engine
- Agent Cursor / SemanticTargetRegistry
- Claim Ledger / Paper consumption
- New npm dependencies, GSAP, new chart libs
- Estimate node behavior changes
- Vendoring CSV into `frontend/public/`
- Git commit

No product ambiguity required a second truth owner.

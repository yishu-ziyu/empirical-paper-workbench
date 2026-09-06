# M4 implementer summary — Card Canonical Research Experience

Date: 2026-09-06  
Branch: `review/workbench-v2`  
Hard bar: C21–C24 programmatic parts in `docs/acceptance/card-canonical-research-experience.md`

## Change

After comparable OLS/IV specification runs, the lab drafts one Claim Ledger object from the runs and fixed wording rules (no LLM). The researcher must Approve. Unapproved claims block grounded Results. Paper Results consume the approved wording plus SpecificationRun coefficients; a jump control returns to Claim/Evidence. Promote or re-draft marks the old results chapter stale / needs regeneration. Course-panel sessions without claims keep the old write gate. `GET /evidence` is unchanged.

Supported: `Education is positively associated with earnings.`  
Conditionally supported: `Under the college-proximity IV assumptions, IV estimates suggest a positive local causal return to schooling.`  
Unsupported: `One more year of education raises everyone's wage by 13%.`

## Files changed

Backend

- `backend/services/research_lab.py` — deterministic draft/approve, `claims[]`, current claim, stale marker
- `backend/services/spec_run.py` — auto-draft after space run if missing
- `backend/routers/research.py` — `POST .../claims/draft`, `POST .../claims/{id}/approve`; promote marks results stale
- `backend/schemas/responses.py` — `ClaimLedgerResponse`; chapter `stale` / `needs_regeneration` / `grounded`
- `backend/facade/__init__.py` — snapshot projects live `grounded` for results
- `backend/services/paper_draft.py` — unsupported wording numbers are not allowed tokens
- `backend/tests/test_card_claim_ledger.py`

Agent

- `agent/engine/readiness.py` — `claim_unapproved` when claims exist
- `agent/engine/bind.py` — claim wording + run facts into results kwargs
- `agent/prompts/results.py` — Claim Ledger writing boundary
- `agent/nodes/review_sources/grounding.py` — `wording_exceeds_evidence`
- `agent/nodes/generate_chapter.py` — clear stale; set `grounded`

Frontend

- `frontend/src/components/EvidenceLab.tsx` — Claim Ledger first, `data-testid="claim-approve"`
- `frontend/src/components/ChapterWriter.tsx` — stale banner + `paper-claim-link`
- `frontend/src/components/WorkbenchArtifact.tsx` — approve + jump to Evidence
- `frontend/src/components/AgentRail.tsx` — grounded badge requires approved claim
- `frontend/src/lib/workspace.ts` — `handleApproveClaim`
- tests: EvidenceLab, ChapterWriter, AgentRail
- generated: OpenAPI + `frontend/src/types/api.ts`

## Commands run

| Command | Result |
|---|---|
| `make gen-api` | pass |
| `make test-backend` | pass — 415 passed, 8 skipped (no new skip; +6) |
| `make test-frontend` | pass — 344 passed (was 340; +4; no new skip) |
| `make test-agent` | pass — 809 passed, 1 skipped (no new skip) |
| `make check-api-drift` | pass |
| `cd frontend && npx tsc --noEmit` | pass |
| `cd frontend && npm run lint` | pass (warnings only; no errors) |

C21: GET research after space run has supported / conditionally supported / unsupported wording, supporting run ids, unresolved assumptions, version, provenance.

C22: generate results 409 `claim_unapproved` until `POST .../approve`; then `approved_by_user=true`.

C23: bind includes supported wording and run coefs; unsupported sentence in results → `grounded=false`; Paper jump `data-testid="paper-claim-link"`.

C24: promote sets results `stale` / `needs_regeneration` and `grounded=false`; approve-chapter still works (`force` path in test).

No `0.0747` in `frontend/src`. Coefficients come from SpecificationRun payloads.

Browser 1280/1440 Claim → Paper still for the main agent (M5).

## API

`POST /sessions/{id}/research/claims/draft` → ResearchLab with `claims[]` + `claim`.

`POST /sessions/{id}/research/claims/{id}/approve` → `approved_by_user=true`.

Space run auto-drafts if no claim exists.

## Visual

Claim text is the one heavy serif line. Conditional and unsupported wording are de-emphasized (`text-wb-muted` / `text-wb-faint`). Approve is the single ink button. No extra cards.

# M1 P0 r2 implementer summary — ExpectationCriterion last-research semantics

Date: 2026-09-07  
Branch: `review/generic-research-spine-hardening` (not reset, not pushed, not merged)  
Contract: `docs/acceptance/generic-research-spine-hardening.md`  
Hard bar: C29–C37  
Contract Status: left as `external-review changes requested` (not closed)

## Change

A user-visible Expectation criterion is bound to exact Evidence (`spec_id`). Changing the direction control does not replace those refs with estimator-only constants. A later OLS preview cannot steal Surprise. Illegal kind/operator/right/tolerance combinations are HTTP 422. Unresolved criteria aggregate to Unevaluated / Inconclusive, never Expected. After reveal, criteria cannot be silently rewritten (409 `expectation_criterion_locked`).

## Not this

Estimator-only seed/UI refs, missing-spec fallback onto another OLS/IV run, Expected for unresolved, post-reveal silent criterion rewrite, fork/new hypothesis, M0/M2/M3/M4 work.

## What I changed (and why)

Kept the previous attempt (seed `spec_id`, fail-closed evaluator, Unevaluated/Inconclusive, 409 lock). Hostile-read remaining P0 holes and fixed those only.

| File | Why |
|---|---|
| `backend/schemas/responses.py` | Ordering+tolerance is not a legal combination; reject it. Docstring now says ordering has empty tolerance. |
| `backend/tests/test_card_research_lab.py` | Strengthen C29 (34-col literals when extract is wooldridge); C32 illegal list includes ordering+tolerance; PUT path must keep `spec_id` after `model_dump(exclude_none=True)`. |
| `frontend/src/components/ResearchLabPanels.tsx` | Delete `IV_METRIC` / `OLS_METRIC`. Never overwrite existing left/right. If fabricating a new criterion, bind comparable spec_ids from the lab (34-col `iv_region_dummies`/`ols_region_dummies`, else `iv_nearc4_full`/`ols_full_controls`). |
| `frontend/src/components/WorkbenchArtifact.tsx` | One-line `specificationSpace` pass so fabrication can bind lab comparable ids. |
| `frontend/src/components/__tests__/ResearchLabPanels.test.tsx` | Direction through sign/approx and back keeps `spec_id`; empty-criteria fabrication binds 34-col and 9-col ids, not estimator-only refs. |
| `frontend/openapi.json`, `docs/api/openapi.json`, `frontend/src/types/api.ts` | `make gen-api` after schema docstring change. |

PUT already used `item.model_dump(mode="json", exclude_none=True)` in `backend/routers/research.py`; r2 adds a regression test that spec_id survives that path. Evaluator already fail-closes on missing spec_id; not rewritten.

## What I did not change

M2 / M3 / M4 files were not edited:

- `frontend/src/components/AgentRail.tsx`
- `frontend/src/components/EvidenceLab.tsx`
- Agent Cursor runtime (`frontend/src/lib/agentCursor/`, `AgentCursorLayer.tsx`)
- spec-run state machine (`backend/services/spec_run.py`)
- recovery / boot-failure / new-study UX
- contract Status

`evaluate_surprise`, seed `spec_id` write, 409 lock, Unevaluated/Inconclusive UI copy from the previous attempt were kept.

## Commands run

C29–C36 (all pass):

| Command | Result |
|---|---|
| `python -m pytest backend/tests/test_card_research_lab.py -k "seed_expectation or nine_col_path" -q` | 2 passed, 17 deselected |
| `python -m pytest backend/tests/test_card_spec_run.py -k "surprise_binds_exact_spec or surprise_missing_spec_id or surprise_does_not_drift" -q` | 3 passed, 22 deselected |
| `cd frontend && npx vitest run src/components/__tests__/ResearchLabPanels.test.tsx -t "preserves exact spec_id"` | 2 passed, 11 skipped |
| `python -m pytest backend/tests/test_card_research_lab.py -k "invalid_criterion or empty_selector or negative_tolerance" -q` | 3 passed, 16 deselected |
| `python -m pytest backend/tests/test_card_spec_run.py -k "equality or zero_boundary" -q` | 2 passed, 23 deselected |
| `python -m pytest backend/tests/test_card_spec_run.py -k "surprise_unresolvable or surprise_inconclusive or surprise_without_criteria" -q` | 3 passed, 22 deselected |
| `python -m pytest backend/tests/test_card_research_lab.py -k "pre_reveal_criterion_history or post_reveal_criterion" -q` | 2 passed, 17 deselected |
| `cd frontend && npx vitest run src/components/__tests__/ResearchLabPanels.test.tsx -t "locked"` | 1 passed, 12 skipped |
| `cd frontend && npx vitest run src/components/__tests__/EvidenceLab.test.tsx src/components/__tests__/AgentRail.test.tsx` | 23 passed |
| extra: `-k "keeps_exact_spec_id or invalid_criterion"` | 2 passed |
| extra: full `ResearchLabPanels.test.tsx` | 13 passed |

C37 / quality gate (all 0 exit):

| Command | Result |
|---|---|
| `make gen-api` | pass |
| `make check-api-drift` | 3/3 ✅ |
| `make test` | agent **819 passed / 1 skipped**; backend **445 passed / 8 skipped**; frontend **393 passed**; no new skip |
| `cd frontend && npx tsc --noEmit` | 0 |
| `npm run lint` | 0 errors (5 pre-existing warnings, unchanged) |
| `npm run build` | 0 |

## Proofs against P0 text

1. **Seed spec_ids (C29)** — `seed_card_lab` builds definitions, then `comparable_spec_ids(definitions)` writes `left.spec_id` / `right.spec_id`. 34-col wooldridge: `iv_region_dummies` / `ols_region_dummies`. 9-col: `iv_nearc4_full` / `ols_full_controls`. estimator remains display metadata.
2. **Later preview non-drift (C30)** — comparable OLS=0.0747 / IV=0.1315 → Unexpected; after `ols_linear_exper` (coef 0.2000) re-evaluate, observed/status still 0.0747 / 0.1315. Missing spec_id with other OLS/IV runs → Unevaluated, no fallback.
3. **422 invalid combination (C32)** — legal (A)(B)(C) only. Added ordering+tolerance to the illegal list; empty selector and negative tolerance still 422; nothing stored.
4. **Equality / zero (C33)** — lt/gt equality is violated; positive/negative at 0 is violated.
5. **Unresolved Unevaluated (C34)** — `test_surprise_unresolvable_metric_stays_silent` asserts `status == "Unevaluated"` and `status != "Expected"`. Partial resolved + unresolved + no violation → Inconclusive. UI: 「尚未判定：所需证据还没有产生」; no Show me for Unevaluated/Inconclusive.
6. **Pre/post reveal history/lock (C35–C36)** — history stores full criteria snapshots including spec_ids; `expectation_set` records version, ids, kind/operator, left/right refs, `phase`. Post-reveal text-only PUT 200; criteria change 409 `expectation_criterion_locked`. UI select disabled with lock copy.
7. **UI refs (C31)** — direction change keeps existing left/right spec_id; sign/approx round-trip keeps them; new criterion fabrication binds lab comparable spec_ids, never estimator-only `IV_METRIC`/`OLS_METRIC`.

## Improve

Named leftover in-scope P0 defects at start of r2: 3 (frontend estimator-only constants; missing sign/approx spec_id test; ordering+tolerance accepted). After this round: **0**.

## Remaining defects I could not fix

None in M1 P0 scope. Estimator-only refs remain legal when the user explicitly submits them without `spec_id` (schema: spec_id **or** estimator). Seed and the UI fabrication path no longer emit that shape.

Validator still owns C29–C37 ACCEPT/REJECT. Parent pushes PR #31; this implementer did not commit, push, or merge.

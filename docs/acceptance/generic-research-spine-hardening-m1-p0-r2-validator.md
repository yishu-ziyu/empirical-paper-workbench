# M1 P0 r2 independent validator — C29–C37

Date: 2026-09-07  
Validator: independent (did not implement; did not treat implementer conversation or `generic-research-spine-hardening-m1-p0-r2-implementer.md` as proof)  
Repo: `/Users/mahaoxuan/Desktop/经济学论文/econpaper`  
Branch: `review/generic-research-spine-hardening`  
Contract: `docs/acceptance/generic-research-spine-hardening.md`  
Scope: C29–C37 only. C1–C28 not reopened.  
Contract Status: **not edited** (left as `external-review changes requested`).

## Verdict: ACCEPT

Every C29–C37 program this validator actually ran exited 0 with the expected assertions. Grep/source checks required by the briefing also hold. Browser walks were not run (orchestrator-owned).

No product code was modified. This file is the only write. No push, no merge, no commit.

## Commands run (this validator)

Backend wrapper (cwd econpaper):

```bash
PYTHONPATH="$(pwd):$(pwd)/backend" backend/.venv/bin/python -m pytest -q --tb=short -p no:cacheprovider --basetemp=$(mktemp -d /tmp/ep-backend-XXXXXX) <path> -k "<expr>"
```

| Check | Command | Exit | Copied result |
|---|---|---|---|
| C29 | `backend/tests/test_card_research_lab.py -k "seed_expectation or nine_col_path"` | 0 | `2 passed, 17 deselected in 6.78s` |
| C30 | `backend/tests/test_card_spec_run.py -k "surprise_binds_exact_spec or surprise_missing_spec_id or surprise_does_not_drift"` | 0 | `3 passed, 22 deselected in 9.52s` |
| C31 | `cd frontend && npx vitest run src/components/__tests__/ResearchLabPanels.test.tsx -t "preserves exact spec_id"` | 0 | `Tests  2 passed \| 11 skipped (13)` — names: `preserves exact spec_id refs when the direction control changes`; `preserves exact spec_id through sign and approx and back` |
| C32 | `backend/tests/test_card_research_lab.py -k "invalid_criterion or empty_selector or negative_tolerance"` | 0 | `3 passed, 16 deselected in 5.74s` |
| C33 | `backend/tests/test_card_spec_run.py -k "equality or zero_boundary"` | 0 | `2 passed, 23 deselected in 0.59s` |
| C34 backend | `backend/tests/test_card_spec_run.py -k "surprise_unresolvable or surprise_inconclusive or surprise_without_criteria"` | 0 | `3 passed, 22 deselected in 0.77s` |
| C34 frontend | `cd frontend && npx vitest run src/components/__tests__/EvidenceLab.test.tsx src/components/__tests__/AgentRail.test.tsx` | 0 | `Test Files  2 passed (2)` / `Tests  23 passed (23)` — EvidenceLab 11, AgentRail 12 |
| C35 | `backend/tests/test_card_research_lab.py -k "pre_reveal_criterion_history"` | 0 | `1 passed, 18 deselected in 5.04s` |
| C36 backend | `backend/tests/test_card_research_lab.py -k "post_reveal_criterion"` | 0 | `1 passed, 18 deselected in 5.12s` |
| C36 frontend | `cd frontend && npx vitest run src/components/__tests__/ResearchLabPanels.test.tsx -t "locked"` | 0 | `Tests  1 passed \| 12 skipped (13)` — `locked criterion select stays disabled after results are revealed` |
| C37 check-api-drift | first `make test` invocation (see note) | 0 for this stage | `✅ openapi.json 与后端代码同步` / `✅ docs/api/openapi.json 与后端代码同步` / `✅ types/api.ts 与 openapi.json 同步` |
| C37 agent | first `make test` invocation | 0 | `819 passed, 1 skipped, 4 warnings in 84.94s` |
| C37 backend | `make test-backend` (after combined `make test` hit validator 300s cap during backend) | 0 | `445 passed, 8 skipped, 32 warnings in 182.90s` |
| C37 frontend tests | `make test-frontend` | 0 | `Test Files  54 passed (54)` / `Tests  393 passed (393)` |
| C37 tsc | `cd frontend && npx tsc --noEmit` | 0 | no diagnostics |
| C37 lint | `cd frontend && npm run lint` (`oxlint`) | 0 | `Found 5 warnings and 0 errors.` / `Finished in 42ms on 135 files with 104 rules using 8 threads.` |
| C37 build | `cd frontend && npm run build` | 0 | `tsc -b && vite build` / `✓ 499 modules transformed.` / `✓ built in 1.69s` |

`make test` note: a single combined `make test` was started. `check-api-drift` and `test-agent` completed green. The invocation was killed at the validator tool’s 300s cap while `test-backend` was still printing dots (`................s....................................................... [ 79%]` / `...............................................sssssss..`). That was a harness timeout, not a pytest failure. This validator then ran the remaining Makefile targets (`make test-backend`, `make test-frontend`) plus the C37 frontend gates. All of those exited 0.

C37 skip inventory (no new skips vs prior C28 evidence of agent 1 skip / backend 8 env skips):

- agent: 1 skipped (same count as C28 evidence).
- backend 8 skipped (from `-rs` on a later backend run, still `445 passed, 8 skipped`):
  - `backend/tests/test_postgres_upload_recovery.py:30: requires an isolated PostgreSQL test database`
  - `backend/tests/test_s3.py:30` … `:91` (7 tests): `S3_ENDPOINT_URL not set — skipping S3 integration tests`
- frontend full suite: 0 skipped.

Pytest names actually collected for the C29–C36 `-k` expressions:

- C29: `test_nine_col_path_marks_region_specs_unavailable`, `test_seed_expectation_carries_single_structured_criterion`
- C30: `test_surprise_binds_exact_spec_and_ignores_later_ols_preview`, `test_surprise_missing_spec_id_does_not_fallback_to_estimator`, `test_surprise_does_not_drift_after_real_ols_linear_preview`
- C32: `test_expectation_put_rejects_invalid_criterion_combinations`, `test_expectation_put_rejects_empty_selector`, `test_expectation_put_rejects_negative_tolerance`
- C33: `test_surprise_equality_boundary_is_a_violation`, `test_surprise_zero_boundary_is_a_violation`
- C34: `test_surprise_without_criteria_stays_expected`, `test_surprise_unresolvable_metric_stays_silent`, `test_surprise_inconclusive_when_partially_resolved_without_violation`
- C35: `test_pre_reveal_criterion_history_keeps_full_snapshots`
- C36: `test_post_reveal_criterion_lock_allows_text_but_rejects_criteria_change`

## Per-check PASS/FAIL

### C29 PASS

Observed from `test_card_research_lab.py` (this validator’s pytest, exit 0, 2 passed):

- `seed_card_lab` writes seed criterion `left.spec_id` / `right.spec_id` from `comparable_spec_ids(definitions)` after definitions exist (`backend/services/research_lab.py` `seed_card_lab`: `definitions = card_specification_definitions(columns)` then `ols_id, iv_id = comparable_spec_ids(definitions)` then `"spec_id": iv_id` / `"spec_id": ols_id`).
- 9-col path asserts `left.spec_id == "iv_nearc4_full"` and `right.spec_id == "ols_full_controls"`.
- 34-col / wooldridge path asserts `iv_id == "iv_region_dummies"` and `ols_id == "ols_region_dummies"` when `extract == "wooldridge_card_34"`.
- `estimator` remains display metadata (`"iv"` / `"ols"`); spec_id is the bound selector.

### C30 PASS

Observed: 3 passed. Tests named above cover (1) comparable OLS=0.0747 / IV=0.1315 → Unexpected, (2) later same-estimator preview does not steal those values, (3) missing spec_id does not fall back to another OLS/IV run.

### C31 PASS

Observed: 2 passed (the `-t "preserves exact spec_id"` regex hits both direction-change tests). Direction control changes kind/operator/tolerance/label/source; existing `left`/`right` `spec_id` kept.

### C32 PASS

Observed: 3 passed — invalid combinations, empty selector, negative tolerance → 422, not persisted.

### C33 PASS

Observed: 2 passed — equality and zero are violations for lt/gt/positive/negative.

### C34 PASS

Observed backend: 3 passed, including `test_surprise_unresolvable_metric_stays_silent` (see grep-verify).  
Observed frontend: 23 passed. EvidenceLab asserts Unevaluated copy `尚未判定：所需证据还没有产生` and `not.toHaveTextContent('Expected')`; Inconclusive copy `部分判定：有的所需证据还没有产生` and `not.toHaveTextContent('Expected')`. AgentRail asserts Unevaluated and Inconclusive `queryByTestId('agent-cursor-show-me')` is null.

### C35 PASS

Observed: 1 passed — `test_pre_reveal_criterion_history_keeps_full_snapshots`.

### C36 PASS

Observed backend: 1 passed — `test_post_reveal_criterion_lock_allows_text_but_rejects_criteria_change` asserts `detail["code"] == "expectation_criterion_locked"`.  
Observed frontend: 1 passed — select disabled; copy `结果已经揭晓；本轮意外判定已锁定，不能事后改写。`

### C37 PASS

Quality gates this validator ran all exited 0:

- check-api-drift: three ✅ lines copied above
- agent: 819 passed, 1 skipped
- backend: 445 passed, 8 skipped (env: Postgres + S3; same 8-count class as prior C28)
- frontend tests: 393 passed, 0 skipped (prior C28 evidence was 384 passed; count increased, skips did not)
- `npx tsc --noEmit` exit 0
- `npm run lint` 0 errors (5 pre-existing `react(only-export-components)` warnings: `useT`, `ENGINE_METHODS`, `TEMPLATES`, `useAgentCursor`, `renderPaperMarkdown`)
- `npm run build` exit 0 (`tsc -b && vite build`, built in 1.69s)

M2/M3/M4 existing tests remained in the passing frontend/backend suites (ResearchLabPanels M2 run-state tests, AgentRail, EvidenceLab, agentCursor tests all collected and passed in the full frontend run).

## Grep / source verifies (this validator)

1. `test_surprise_unresolvable_metric_stays_silent` does **not** assert status == Expected. Live body:

```python
assert surprise["status"] == "Unevaluated"
assert surprise["status"] != "Expected"
```

2. Seed criterion left/right have `spec_id` (not estimator-only). Live seed:

```python
"left": { "metric": "estimate.coef", "estimator": "iv", "spec_id": iv_id, "label": "IV estimate" },
"right": { "metric": "estimate.coef", "estimator": "ols", "spec_id": ols_id, "label": "OLS estimate" },
```

Comment in source: `estimator is display metadata; spec_id is the authoritative selector.`

3. `_criterion_ref_value` returns None when spec_id is present but missing, without estimator fallback. Live:

```python
if isinstance(spec_id, str) and spec_id.strip():
    wanted_spec = spec_id.strip()
    for run in reversed(completed):
        if str(run.get("spec_id") or "") == wanted_spec:
            return _as_float(run.get("coef"))
    return None
```

Estimator matching only runs after that early return.

4. PUT 409 code is `expectation_criterion_locked` in `backend/services/research_lab.py` (`"code": "expectation_criterion_locked"`) and asserted in `backend/tests/test_card_research_lab.py` (`assert detail["code"] == "expectation_criterion_locked"`).

5. `IV_METRIC` / `OLS_METRIC` in `frontend/src/components/ResearchLabPanels.tsx`: **no matches**.

## r2 delta vs `origin/review/generic-research-spine-hardening` / working tree

`git status --short` + `git diff --stat origin/review/generic-research-spine-hardening` (this validator):

```
 M backend/schemas/responses.py
 M backend/tests/test_card_research_lab.py
 M docs/acceptance/generic-research-spine-hardening.md
 M docs/api/openapi.json
 M frontend/openapi.json
 M frontend/src/components/ResearchLabPanels.tsx
 M frontend/src/components/WorkbenchArtifact.tsx
 M frontend/src/components/__tests__/ResearchLabPanels.test.tsx
 M frontend/src/types/api.ts
 M runtime/STATE.md
 M runtime/tasks/20260907-m1-expectation-criterion-p0.md
?? docs/acceptance/generic-research-spine-hardening-m1-p0-r2-implementer.md
```

11 files changed, 193 insertions(+), 57 deletions(-) vs origin (plus untracked implementer report; this validator report is additional).

Working tree is M1 P0 files only:

- schema/OpenAPI/api.ts: ordering must not include tolerance
- ResearchLabPanels + tests: spec_id preservation / fabrication
- WorkbenchArtifact.tsx: **one line** `specificationSpace={ws.research.specification_space}` passed into the Expectation editor (M1 bind, not M2/M3/M4 product logic)
- runtime task/index notes
- contract markdown (this validator did not change Status)

M2/M3/M4 product files **not** in this r2 working-tree delta (confirmed by `git diff --stat`):

- `frontend/src/components/AgentRail.tsx`
- `frontend/src/components/EvidenceLab.tsx`
- `frontend/src/lib/agentCursor/`
- `frontend/src/components/AgentCursorLayer.tsx`
- `backend/services/spec_run.py`
- boot-failure / new-study / recovery UX files

`backend/services/research_lab.py` is also not in the uncommitted r2 delta (seed/`_criterion_ref_value`/409 lock already present on the branch HEAD this validator ran).

## What this validator did not run

- Browser walks (C7, C8–C11 browser, C13–C17, C19 browser, C20–C26, C25 clean journey). Orchestrator-owned.
- `make verify` (requires running frontend/backend; Agents.md: do not use it as a substitute when services are not the assigned gate).
- Push, merge, commit.
- Reopening C1–C28.

## Contract Status

Not edited. Still `external-review changes requested` in `docs/acceptance/generic-research-spine-hardening.md`. Orchestrator may close C29–C37 after this ACCEPT.

# M1 P0 r3 implementer summary — empty criteria must not be Expected

Date: 2026-09-07  
Branch: `review/generic-research-spine-hardening` (not committed, not pushed, not merged)  
HEAD: `1aa5e95cc66704d5755518eec099831e5c1c2b73`  
Contract: `docs/acceptance/generic-research-spine-hardening.md`  
Hard bar: C38–C42  
Contract Status: left as `external-review changes requested` (not closed)

## Change

When a research lab has completed runs but no structured ExpectationCriterion, Surprise is `Unevaluated` with `unevaluated_reason="no_criteria"`. It is never `Expected`. Free text is preserved on `expectation.text` and is not a judgment. GET / `public_research` fail-closes stale stored `Expected` payloads by calling the same `evaluate_surprise`. Card seed criteria still evaluate Unexpected at OLS 0.0747 / IV 0.1315.

## Not this

Auto-invented criteria, re-parsing free text, auto Show me, a second evaluator, i18n/terminology/marketing (phase B/C), M0/M2/M3/M4 rewrites, statistical coefficient changes, issue #30, merge/push/`main`.

## Files changed and why

| File | Why |
|---|---|
| `backend/services/research_lab.py` | Removed the empty-criteria Expected shortcut. No structured criteria (empty list, missing key, or items without `id`) → Unevaluated + `no_criteria`, `expected=None`. All unresolved structured criteria → Unevaluated + `unresolved_metrics`. `public_research` re-runs `evaluate_surprise` when completed runs exist so a stored Expected cannot leak. |
| `backend/schemas/responses.py` | Optional `unevaluated_reason: no_criteria \| unresolved_metrics`. |
| `backend/tests/test_card_spec_run.py` | Renamed `test_surprise_without_criteria_stays_expected`. Added empty-list, missing-key, unparsed, no-completed, write-run-read, Card non-regression, and stale GET tests. |
| `frontend/src/components/EvidenceLab.tsx` | Copy split only: `no_criteria` → 「尚未判定：尚未设置可检验的预期。」; other Unevaluated keeps 「尚未判定：所需证据还没有产生」. Neither shows Expected / Show me. |
| `frontend/src/components/__tests__/EvidenceLab.test.tsx` | Both Unevaluated explanations. |
| `frontend/src/components/__tests__/AgentRail.test.tsx` | `no_criteria` payload does not show Show me. |
| `frontend/openapi.json`, `docs/api/openapi.json`, `frontend/src/types/api.ts` | `make gen-api`. |
| `docs/acceptance/generic-research-spine-hardening.md` | C38–C42 evidence filled; Status not closed. |
| this file | Implementer summary. |

## Commands run (copied output)

C38:

```text
PYTHONPATH="$(pwd):$(pwd)/backend" backend/.venv/bin/python -m pytest -q --tb=short -p no:cacheprovider --basetemp=$(mktemp -d /tmp/ep-backend-XXXXXX) backend/tests/test_card_spec_run.py -k "surprise_without_criteria or surprise_missing_criteria or surprise_unparsed or surprise_unresolvable or surprise_inconclusive or surprise_expected_when or surprise_ordering_mismatch or surprise_no_completed"
........                                                                 [100%]
8 passed, 23 deselected in 0.39s
```

C39:

```text
cd frontend && npx vitest run src/components/__tests__/EvidenceLab.test.tsx src/components/__tests__/AgentRail.test.tsx
 Test Files  2 passed (2)
      Tests  25 passed (25)
```

C40:

```text
PYTHONPATH="$(pwd):$(pwd)/backend" backend/.venv/bin/python -m pytest -q --tb=short -p no:cacheprovider --basetemp=$(mktemp -d /tmp/ep-backend-XXXXXX) backend/tests/test_card_spec_run.py -k "empty_criteria_write_run_read or without_criteria_api"
...                                                                      [100%]
3 passed, 28 deselected in 6.06s
```

C41:

```text
make gen-api && make check-api-drift
[gen-api] openapi.json exported, schemas: 112
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
```

C42 / non-regression:

```text
backend C29–C33 / C35–C36 filter: 13 passed, 37 deselected in 6.01s
frontend ResearchLabPanels -t "preserves exact spec_id|locked": 3 passed | 10 skipped
make test:
  agent 819 passed, 1 skipped
  backend 451 passed, 8 skipped
  frontend 395 passed
  [test] agent + backend + frontend 全部通过
npx tsc --noEmit: exit 0
npm run lint: Found 5 warnings and 0 errors. (pre-existing)
npm run build: exit 0, built in 1.42s
```

## Proofs

1. **Empty list + completed runs** — `test_surprise_without_criteria_is_unevaluated`: `criteria=[]` → `status=Unevaluated`, `!= Expected`, `unevaluated_reason=no_criteria`, `criterion_ids=[]`, `expected=None`.
2. **Missing criteria key** — `test_surprise_missing_criteria_key_is_unevaluated`: legacy `{text, version}` with completed runs → same no_criteria payload.
3. **Unparsed items** — `test_surprise_unparsed_items_are_no_criteria`: list items without `id` are not criteria and are not re-parsed from free text → no_criteria.
4. **All unresolved** — `test_surprise_unresolvable_metric_stays_silent`: Unevaluated, `unevaluated_reason=unresolved_metrics` (not `no_criteria`), `unresolved_criterion_ids` non-empty.
5. **Inconclusive** — `test_surprise_inconclusive_when_partially_resolved_without_violation` unchanged.
6. **Expected** — `test_surprise_expected_when_criterion_holds` unchanged.
7. **Unexpected** — `test_surprise_ordering_mismatch_on_real_magnitudes` unchanged (0.0747 / 0.1315).
8. **No completed runs** — `test_surprise_no_completed_runs_returns_none`: empty runs and failed-only runs → `None`.
9. **Write → run → read** — `test_empty_criteria_write_run_read_is_unevaluated`: PUT `criteria=[]` with Chinese free text before reveal → freeze → specification-space run → GET: text preserved, `criteria==[]`, no auto-created criterion, Surprise Unevaluated + `no_criteria`.
10. **Stale GET coerce** — `test_without_criteria_api_stale_expected_is_not_served`: empty criteria + stored `{status: Expected}` does not leave `public_research` as Expected.
11. **Card non-regression** — `test_without_criteria_api_does_not_regress_seeded_card`: seeded criteria still Unexpected; observed contains 0.0747 and 0.1315.

## git status (not committed)

```text
 M backend/schemas/responses.py
 M backend/services/research_lab.py
 M backend/tests/test_card_spec_run.py
 M docs/acceptance/generic-research-spine-hardening.md
 M docs/api/openapi.json
 M frontend/openapi.json
 M frontend/src/components/EvidenceLab.tsx
 M frontend/src/components/__tests__/AgentRail.test.tsx
 M frontend/src/components/__tests__/EvidenceLab.test.tsx
 M frontend/src/types/api.ts
 M runtime/STATE.md
?? runtime/tasks/20260907-m1-empty-criteria-unevaluated.md
?? docs/acceptance/generic-research-spine-hardening-m1-p0-r3-implementer.md
review/generic-research-spine-hardening
1aa5e95cc66704d5755518eec099831e5c1c2b73
```

`runtime/STATE.md` and the task file were already dirty from the planner; this round did not edit them.

This repair does not prove every product capability is ready to ship.

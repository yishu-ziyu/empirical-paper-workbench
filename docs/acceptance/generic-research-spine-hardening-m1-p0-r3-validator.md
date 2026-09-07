# M1 P0 r3 independent validator — C38–C42

Date: 2026-09-07
Validator: independent (did not implement; did not treat implementer conversation or `generic-research-spine-hardening-m1-p0-r3-implementer.md` as proof)
Repo: `/Users/mahaoxuan/Desktop/经济学论文/econpaper`
Branch: `review/generic-research-spine-hardening`
HEAD: `1aa5e95cc66704d5755518eec099831e5c1c2b73` (`1aa5e95 fix(research): keep criterion spec_ids through UI and fail closed`)
Working tree: **dirty** (uncommitted M1 P0 r3 empty-criteria work; this validator did not commit, push, or merge)
Contract: `docs/acceptance/generic-research-spine-hardening.md`
Scope: C38–C42 only. C1–C37 historical; M0/M2/M3/M4 not reopened.
Contract Status: **not edited** (left as `external-review changes requested`).

## Verdict: ACCEPT

Every C38–C42 program this validator actually ran from this shell exited 0 with the expected assertions. Grep/source checks required by the briefing also hold.

No product code was modified. This file is the only write. No push, no merge, no commit.
This ACCEPT does not claim all product capabilities are ready to ship. It does not close the contract Status.

## Commands run (this validator)

Backend wrapper (cwd econpaper):

```bash
PYTHONPATH="$(pwd):$(pwd)/backend" backend/.venv/bin/python -m pytest -q --tb=short -p no:cacheprovider --basetemp=$(mktemp -d /tmp/ep-backend-XXXXXX) <path> -k "<expr>"
```

Frontend programs were run as `cd frontend && ...`. A first accidental vitest/`tsc` invocation from the repo root hit `document is not defined` / missing `package.json`; those were validator cwd mistakes, not product failures. The contract programs below are the `cd frontend` re-runs.

| Check | Command | Exit | Copied result |
|---|---|---|---|
| C38 | `backend/tests/test_card_spec_run.py -k "surprise_without_criteria or surprise_missing_criteria or surprise_unparsed or surprise_unresolvable or surprise_inconclusive or surprise_expected_when or surprise_ordering_mismatch or surprise_no_completed"` | 0 | quiet: `8 passed, 23 deselected in 0.70s`. verbose: 8 PASSED names listed below |
| C39 | `cd frontend && npx vitest run src/components/__tests__/EvidenceLab.test.tsx src/components/__tests__/AgentRail.test.tsx` | 0 | `Test Files  2 passed (2)` / `Tests  25 passed (25)` — AgentRail 13, EvidenceLab 12 |
| C40 | `backend/tests/test_card_spec_run.py -k "empty_criteria_write_run_read or without_criteria_api"` | 0 | quiet: `3 passed, 28 deselected in 6.67s`. verbose: 3 PASSED names listed below |
| C41 | `make check-api-drift` | 0 | `✅ openapi.json 与后端代码同步` / `✅ docs/api/openapi.json 与后端代码同步` / `✅ types/api.ts 与 openapi.json 同步` |
| C42 C29 | `backend/tests/test_card_research_lab.py -k "seed_expectation or nine_col_path"` | 0 | `2 passed, 17 deselected in 2.00s` |
| C42 C30 | `backend/tests/test_card_spec_run.py -k "surprise_binds_exact_spec or surprise_missing_spec_id or surprise_does_not_drift"` | 0 | `3 passed, 28 deselected in 5.58s` |
| C42 C31 | `cd frontend && npx vitest run src/components/__tests__/ResearchLabPanels.test.tsx -t "preserves exact spec_id"` | 0 | `Tests  2 passed \| 11 skipped (13)` |
| C42 C32 | `backend/tests/test_card_research_lab.py -k "invalid_criterion or empty_selector or negative_tolerance"` | 0 | `3 passed, 16 deselected in 2.20s` |
| C42 C33 | `backend/tests/test_card_spec_run.py -k "equality or zero_boundary"` | 0 | `2 passed, 29 deselected in 0.40s` |
| C42 C35 | `backend/tests/test_card_research_lab.py -k "pre_reveal_criterion_history"` | 0 | `1 passed, 18 deselected in 1.59s` |
| C42 C36 backend | `backend/tests/test_card_research_lab.py -k "post_reveal_criterion"` | 0 | `1 passed, 18 deselected in 1.59s` |
| C42 C36 frontend | `cd frontend && npx vitest run src/components/__tests__/ResearchLabPanels.test.tsx -t "locked"` | 0 | `Tests  1 passed \| 12 skipped (13)` |
| C42 quality | `make test` | 0 | check-api-drift 3/3; agent `819 passed, 1 skipped, 4 warnings in 40.01s`; backend `451 passed, 8 skipped, 32 warnings in 187.72s`; frontend `Test Files  54 passed (54)` / `Tests  395 passed (395)`; `[test] agent + backend + frontend 全部通过` |
| C42 tsc | `cd frontend && npx tsc --noEmit` | 0 | no diagnostics (`TSC_EXIT:0`) |
| C42 lint | `cd frontend && npm run lint` (`oxlint`) | 0 | `Found 5 warnings and 0 errors.` / `Finished in 30ms on 135 files with 104 rules using 8 threads.` |
| C42 build | `cd frontend && npm run build` | 0 | `tsc -b && vite build` / `✓ 499 modules transformed.` / `✓ built in 1.63s` |

C38 verbose names (this validator, `-v`):

```
backend/tests/test_card_spec_run.py::test_surprise_ordering_mismatch_on_real_magnitudes PASSED
backend/tests/test_card_spec_run.py::test_surprise_expected_when_criterion_holds PASSED
backend/tests/test_card_spec_run.py::test_surprise_without_criteria_is_unevaluated PASSED
backend/tests/test_card_spec_run.py::test_surprise_missing_criteria_key_is_unevaluated PASSED
backend/tests/test_card_spec_run.py::test_surprise_unparsed_items_are_no_criteria PASSED
backend/tests/test_card_spec_run.py::test_surprise_no_completed_runs_returns_none PASSED
backend/tests/test_card_spec_run.py::test_surprise_unresolvable_metric_stays_silent PASSED
backend/tests/test_card_spec_run.py::test_surprise_inconclusive_when_partially_resolved_without_violation PASSED
======================= 8 passed, 23 deselected in 0.17s =======================
```

C40 verbose names (this validator, `-v`):

```
backend/tests/test_card_spec_run.py::test_empty_criteria_write_run_read_is_unevaluated PASSED
backend/tests/test_card_spec_run.py::test_without_criteria_api_does_not_regress_seeded_card PASSED
backend/tests/test_card_spec_run.py::test_without_criteria_api_stale_expected_is_not_served PASSED
======================= 3 passed, 28 deselected in 9.70s =======================
```

C41 copied output:

```
[check-api-drift] ① 从后端代码重新导出 openapi.json
⚠ DEBUG: generated ephemeral JWT_SECRET_KEY for this process
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ② 重新生成 api.ts 并 diff
✨ openapi-typescript 7.13.0
🚀 openapi.json → /tmp/api.drift.ts [154.8ms]
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
```

C42 `make test` skip inventory (no new skips vs r2: agent 1 / backend 8 / frontend 0):

- agent: `819 passed, 1 skipped`
- backend: `451 passed, 8 skipped` (r2 was 445 passed / 8 skipped; skip count unchanged, 6 additional backend tests now pass)
- frontend: `395 passed` (r2 was 393; +2 tests, 0 skipped)

## Source checks (this validator)

- `grep -rn "stays_expected" backend/tests` → empty, `GREP_EXIT:1`. Old name `test_surprise_without_criteria_stays_expected` does not exist. Replacement is `test_surprise_without_criteria_is_unevaluated`.
- `evaluate_surprise` empty-criteria branch (`backend/services/research_lab.py` after `if not criteria:`) returns `"status": "Unevaluated"` and `"unevaluated_reason": "no_criteria"`. It does **not** return `Expected`.
- All-unresolved path sets `status = "Unevaluated"` and `unevaluated_reason = "unresolved_metrics"` (not `no_criteria`).
- OLS/IV 0.0747 / 0.1315 assertions still present in `backend/tests/test_card_spec_run.py` (ordering mismatch, exact-spec bind, empty-criteria seeded Card control) and `backend/tests/test_card_research_lab.py`.
- EvidenceLab product change is copy-split only (`frontend/src/components/EvidenceLab.tsx` `7 +-`): `no_criteria` → 「尚未判定：尚未设置可检验的预期。」; other Unevaluated → 「尚未判定：所需证据还没有产生」.
- `git diff --stat` does **not** include Agent Cursor runtime, spec_run state machine, boot-failure UX, new-study, or runner logging. Observed:

```
 backend/schemas/responses.py                       |   1 +
 backend/services/research_lab.py                   |  50 ++++++-
 backend/tests/test_card_spec_run.py                | 166 ++++++++++++++++++++-
 .../acceptance/generic-research-spine-hardening.md |  37 ++++-
 docs/api/openapi.json                              |  15 ++
 frontend/openapi.json                              |  15 ++
 frontend/src/components/EvidenceLab.tsx            |   7 +-
 .../src/components/__tests__/AgentRail.test.tsx    |  26 ++++
 .../src/components/__tests__/EvidenceLab.test.tsx  |  34 +++++
 frontend/src/types/api.ts                          |   2 +
 runtime/STATE.md                                   |   1 +
 11 files changed, 335 insertions(+), 19 deletions(-)
```

Untracked (not product runtime): `docs/acceptance/generic-research-spine-hardening-m1-p0-r3-implementer.md`, `runtime/tasks/20260907-m1-empty-criteria-unevaluated.md`.
- `SurpriseResponse.unevaluated_reason` is optional `no_criteria | unresolved_metrics | null` in `backend/schemas/responses.py`, `docs/api/openapi.json`, `frontend/openapi.json`, and `frontend/src/types/api.ts` (`unevaluated_reason?: ("no_criteria" | "unresolved_metrics") | null`).

## Per-check PASS/FAIL

### C38 PASS

Pytest exit 0, 8 passed. Assertions observed in the collected tests:

1. `criteria=[]` + completed runs → `status="Unevaluated"` and `!= "Expected"`, `unevaluated_reason="no_criteria"`, `criterion_ids=[]` (`test_surprise_without_criteria_is_unevaluated`).
2. Missing `criteria` key (free text only) → same (`test_surprise_missing_criteria_key_is_unevaluated`).
3. Unparsed items without `id` → same (`test_surprise_unparsed_items_are_no_criteria`).
4. Legal criterion, all unresolved → `Unevaluated` and `!= Expected`, `unevaluated_reason == "unresolved_metrics"` (`!= "no_criteria"`), `unresolved_criterion_ids` non-empty (`test_surprise_unresolvable_metric_stays_silent`).
5. Partial resolve, no violation → `Inconclusive` (`test_surprise_inconclusive_when_partially_resolved_without_violation`).
6. All resolved and satisfied → `Expected` (`test_surprise_expected_when_criterion_holds`).
7. Any violated → `Unexpected` with OLS 0.0747 / IV 0.1315 (`test_surprise_ordering_mismatch_on_real_magnitudes`).
8. No completed runs → `None` (`test_surprise_no_completed_runs_returns_none`).

Old name `test_surprise_without_criteria_stays_expected` is gone.

### C39 PASS

Vitest exit 0, 25 passed (`cd frontend`).

- `no_criteria` copy asserted as 「尚未判定：尚未设置可检验的预期。」; `data-status=Unevaluated`; no Expected; no unresolved-metrics copy (`test('no_criteria Unevaluated explains missing expectation, not missing evidence')`).
- unresolved Unevaluated copy 「尚未判定：所需证据还没有产生」 (`test('Unevaluated does not masquerade as Expected')`).
- AgentRail: `no_criteria` Unevaluated does not show Show me; unresolved Unevaluated does not show Show me; Inconclusive does not show Show me.

### C40 PASS

Pytest exit 0, 3 passed.

- `test_empty_criteria_write_run_read_is_unevaluated`: PUT `/research/expectation` with `criteria=[]` and free text → freeze → specification-space run → GET: text preserved, `criteria==[]`, `surprise.status=="Unevaluated"` and `!= "Expected"`, `unevaluated_reason=="no_criteria"`.
- `test_without_criteria_api_does_not_regress_seeded_card`: seeded Card still `Unexpected`, observed contains `0.0747` and `0.1315`.
- `test_without_criteria_api_stale_expected_is_not_served`: stored empty-criteria + `status=Expected` is not served; GET returns Unevaluated + `no_criteria`.

### C41 PASS

`make check-api-drift` exit 0, three sync checks green. `SurpriseResponse` has optional `unevaluated_reason` enum `no_criteria` / `unresolved_metrics`.

### C42 PASS

C29–C33 and C35–C36 original programs all exit 0 (13 backend + 3 frontend). `make test` exit 0. `tsc --noEmit`, lint (0 errors / 5 existing warnings), `npm run build` all exit 0. No new skips. M0/M2/M3/M4 source files not in the diff. OLS/IV 0.0747 / 0.1315 assertions remain.

Push of PR #31 was **not** performed: this validator is forbidden to commit, push, or merge. Working tree remains dirty on HEAD `1aa5e95cc66704d5755518eec099831e5c1c2b73`. That is process state, not a failing C38–C42 program.

## Notes

- C39/C42 frontend programs are only valid when run from `frontend/` (vitest 4.1.10 + jsdom). The same paths from repo root use a different vitest and fail with `ReferenceError: document is not defined`.
- This ACCEPT covers C38–C42 empty-criteria fail-closed behavior only. It does not reopen C1–C37, does not prove M0/M2/M3/M4 browser journeys, and does not claim the product is ready to ship.

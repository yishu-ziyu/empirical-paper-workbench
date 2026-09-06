# Validator report: workbench-v2 provenance lineage (C1–C6)

Date: 2026-09-06
Branch: `review/workbench-v2` (HEAD `b931b8bde673500ec994c09e5429abc0233c2882`; working tree has uncommitted provenance changes — not evaluated as C8)
Scope: independent ACCEPT/REJECT of C1–C6. C7 browser and C8 push are parent-owned and were not performed.

## Verdict: ACCEPT

C1–C6 all PASS. C7 and C8: PARENT / not evaluated.

Contract Evidence section is still the placeholder:

```
## Evidence

（收尾时填真实输出摘录、测试名、浏览器断言、commit SHA、CI job 状态。）
```

No archived C7 browser assertions/screenshots and no C8 push/CI-job evidence were present in the contract at validation time.

---

## C1 Run provenance — PASS

Command: `make test-backend`

```
[test-backend] backend/tests（backend/.venv）
...
389 passed, 8 skipped, 32 warnings in 97.38s (0:01:37)
```

Named re-run:

```
backend/tests/test_evidence.py::test_evidence_run_id_follows_older_producer_after_newer_prewrite
backend/tests/test_evidence.py::test_evidence_run_id_stays_on_specified_producer_after_later_run
.....                                                                    [100%]
5 passed in 1.65s
```

(The 5-test command also included C2/C3 evidence tests listed below; both C1 names were in that passing set.)

Grep: `rg latest_run backend/routers/evidence.py` → no matches.

`backend/routers/evidence.py` binds run identity from `estimate.source_run_id` via `_producer_run_id` / `_attach_producer_run`. Comment on `_attach_producer_run`: `Fill run identity from estimate.source_run_id only. Never the newest prewrite.` `latest_run` still exists as `RunRepository.latest_run` in `backend/run_repository.py:371`; Evidence does not call it.

---

## C2 Dataset provenance — PASS

Named backend tests (same 5-test command as C1):

- `test_evidence_dataset_points_at_cleaned_not_raw` — PASS
- `test_evidence_without_analysis_dataset_does_not_use_upload_metadata` — PASS

Agent test:

```
agent/tests/test_estimate.py::test_estimate_stamps_source_run_id_and_cleaned_dataset
.                                                                        [100%]
1 passed in 2.82s
```

`_dataset_from_estimate` reads `estimate.analysis_dataset` only (docstring: `Analysis-input identity stamped on the estimate — never upload metadata.`). Missing analysis_dataset → `provenance.dataset is None` even when upload metadata exists.

---

## C3 Code provenance — PASS

Backend: `test_evidence_code_artifacts_only_for_producer_run` — PASS (in the 5-test command).

Frontend (`cd frontend && npm test -- src/components/__tests__/EvidenceView.test.tsx ...`):

```
✓ src/components/__tests__/EvidenceView.test.tsx (2 tests)
  canExport-equivalent chapters without code artifact stay 5/6
  real code artifact for the producer run allows Fully traceable 6/6
```

Full suite: `make test-frontend` → `Test Files  47 passed (47)` / `Tests  322 passed (322)`.

Grep: `hasCode={ws.canExport}` — absent in frontend.
Grep: `hasCode=` — no matches in frontend.
`WorkbenchArtifact` still passes `canExport={submissionReady}` to `SubmissionStatus` (export readiness), not as Evidence Code present.

Note (not a C3 fail): EvidenceView tests emit React warning `Encountered two children with the same key, \`income ~ age\``. Tests still passed.

---

## C4 table_rows — PASS

`frontend/src/lib/__tests__/readoutTable.test.ts`:

- `normalizeEstimateTableSource joins string arrays`
- `normalizeEstimateTableSource keeps a string as-is`
- `normalizeEstimateTableSource maps null and unknown to null`

Targeted frontend run: `Test Files  3 passed (3)` / `Tests  10 passed (10)` including OverviewView.

`OverviewView.test.tsx`: `renders Key Results rows from array-shaped table_rows` — PASS.

Both views call `normalizeEstimateTableSource`:

- `EvidenceView.tsx` 111–112
- `OverviewView.tsx` 157–161

Grep `.replace` in `OverviewView.tsx` → no matches (parser uses `raw.replace` only after `normalizeEstimateTableSource` has produced a string, inside `parseEstimateRows` in `readoutTable.ts`).

---

## C5 CI venv — PASS

`.github/workflows/ci.yml` backend job:

```
backend/.venv/bin/pip install -r backend/requirements.txt -r agent/requirements.txt -r requirements-dev.txt
agent/.venv/bin/pip install -r agent/requirements.txt -r requirements-dev.txt
```

api-contract job also installs `-r requirements-dev.txt` into `backend/.venv`.

Makefile:

```
install-backend: pip install -r requirements.txt -r ../requirements-dev.txt
install-agent:   pip install -r requirements.txt -r ../requirements-dev.txt
```

`requirements-dev.txt`:

```
pytest>=8.0
pytest-asyncio>=0.24
```

Local venvs:

```
backend/.venv/bin/python -m pytest --version → pytest 9.1.1
agent/.venv/bin/python -m pytest --version    → pytest 9.1.1
backend pytest-asyncio 1.4.0
agent pytest-asyncio 1.4.0
```

`make test-backend` and the named agent pytest both used `.venv/bin/python -m pytest` (no global pytest).

---

## C6 docs — PASS

`docs/acceptance/workbench-v2-provenance-lineage.md` Change + C3 + C6: Fully traceable requires six real lineage layers (Result / Specification / Estimator / actual producer Run / actual analysis Dataset / actual Code artifact). Heuristic / latest / UI readiness / session-level guess must not count as present.

`docs/acceptance/workbench-v2-visual-phase.md` C3 now states:

```
Fully traceable 只在六层都有真实 lineage 时出现。heuristic、latest_run、UI readiness（含 canExport / 已生成章节）、session-level guess 任一存在都不得计为 present。旧表述「生成过章节 → 6/6」已被 `docs/acceptance/workbench-v2-provenance-lineage.md` 取代，不得再作为完成标准。
```

Visual-phase Evidence text records the old heuristic as superseded, not as the current bar.

---

## C7 / C8 — PARENT / not evaluated

- C7: validator did not run `make dev` or browser walkthrough. Contract Evidence is empty; no new provenance-lineage browser archive was found in the contract file.
- C8: validator did not push, merge, or inspect GitHub Actions job conclusion. Branch remained `review/workbench-v2`. Working tree is dirty relative to `origin/review/workbench-v2` (implementation + contract files uncommitted). That is parent-owned.

---

## Optional extra

`make check-api-drift`:

```
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
```

`make test-frontend`: 322 passed, 0 failed.

---

## Remaining in-scope notes (not C1–C6 failures)

1. EvidenceView duplicate React key `income ~ age` during C3 tests (stderr warning). Does not fail the 5/6 vs 6/6 assertions.
2. Contract Evidence block is still unfilled; C7/C8 remain for the parent agent.
3. `docs/acceptance/evidence-visual-phase/self-review.md` still narrates the old visual-phase “生成章节后有代码导出 → 6/6” walkthrough. C6 only requires this contract + visual-phase C3; those two files have superseded that bar.


# Implementer report: Workbench v2 provenance lineage (C1–C6)

Branch: `review/workbench-v2`. Did not checkout main, merge, push, or open a PR.

## Change

Evidence Fully traceable now requires six real lineage layers. Run identity comes from `estimate.source_run_id` (not latest prewrite). Dataset identity is the analysis CSV the estimator read. Code present only if a takeable artifact is registered under that producer run. Overview and Evidence share a safe `table_rows` parser. CI/local venvs install pytest from `requirements-dev.txt`.

## Provenance contract fields added

- `estimate.source_run_id` — producer run that wrote this estimate. Injected into prewrite `initial_state` as `source_run_id`; stamped by `estimate()`; persist fallback in `runner._stamp_estimate_producer` only when this run replaced the estimate.
- `estimate.analysis_dataset` — `{name, path, hash, role, rows, columns, version?}`. `role` is `cleaned` when `csv_path` matches `cleaned_datasets`, else `raw`. Evidence `provenance.dataset` reads this only; upload metadata is not a fallback.
- `provenance.code` — `EvidenceCodeArtifactResponse[]` for files under `runs/<session>/outputs/code/<producer_run_id>/`. `translate_code` writes takeable scripts there and registers them on the manifest. Empty placeholders are not takeable.

## Files changed

- `agent/nodes/estimate.py`
- `agent/nodes/translate_code.py`
- `agent/tests/test_estimate.py`
- `agent/tests/test_translate_code.py`
- `backend/runner.py`
- `backend/run_store.py`
- `backend/routers/evidence.py`
- `backend/schemas/responses.py`
- `backend/tests/test_evidence.py`
- `frontend/src/lib/readoutTable.ts`
- `frontend/src/lib/__tests__/readoutTable.test.ts`
- `frontend/src/components/EvidenceView.tsx`
- `frontend/src/components/OverviewView.tsx`
- `frontend/src/components/WorkbenchArtifact.tsx`
- `frontend/src/components/__tests__/EvidenceView.test.tsx` (new)
- `frontend/src/components/__tests__/OverviewView.test.tsx` (new)
- `frontend/src/types/api.ts` (via `make gen-api`)
- `frontend/openapi.json`, `docs/api/openapi.json`
- `Makefile`
- `.github/workflows/ci.yml`
- `requirements-dev.txt` (new)
- `docs/acceptance/workbench-v2-visual-phase.md` (C3 / Evidence text tightened; Status remains closed)

## Tests run

- `make test-backend` — 389 passed, 8 skipped
- `make test-agent` — 805 passed, 1 skipped
- `make test-frontend` — 322 passed
- `make gen-api` then `make check-api-drift` — pass

### New / retargeted tests (all pass)

Backend:

- `test_evidence_projects_main_estimate_and_provenance` (retargeted: seeds `source_run_id`)
- `test_evidence_without_analysis_dataset_does_not_use_upload_metadata` (replaces upload-as-analysis)
- `test_evidence_run_id_follows_older_producer_after_newer_prewrite`
- `test_evidence_run_id_stays_on_specified_producer_after_later_run`
- `test_evidence_dataset_points_at_cleaned_not_raw`
- `test_evidence_code_artifacts_only_for_producer_run`
- `test_stamp_estimate_producer_only_when_this_run_replaced_estimate`

Agent:

- `test_estimate_stamps_source_run_id_and_cleaned_dataset`
- `test_translate_code_persists_takeable_artifacts_for_producer_run`
- `test_empty_placeholder_translations_are_not_takeable`

Frontend:

- `normalizeEstimateTableSource joins string arrays`
- `normalizeEstimateTableSource keeps a string as-is`
- `normalizeEstimateTableSource maps null and unknown to null`
- `canExport-equivalent chapters without code artifact stay 5/6`
- `real code artifact for the producer run allows Fully traceable 6/6`
- `renders Key Results rows from array-shaped table_rows`

## Grep proof

```text
rg -n "latest_run" backend/routers/evidence.py
# (no matches)

rg -n "hasCode=\{ws.canExport\}" frontend/src
# (no matches)
```

`RunRepository.get(producer_id)` is the only run lookup on Evidence. WorkbenchArtifact no longer passes `hasCode`.

## Not done (parent-owned)

- C7 browser provenance walkthrough (`make dev` + five scenes)
- C8 push to PR #27 / GitHub Actions report

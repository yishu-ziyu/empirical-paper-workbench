# econpaper Codex Task State

- Task ID: FM-E-BUILD-FIX-ATTACH-404
- Status: active
- Git context（分支可选）: `fix/fm-e-build-attach-404-1` from `feat/fm-e-build-did-spec-recut-1` @ `bf695715`
- Goal: Restore attach + confirm-attach success paths (not 404). Product gate remains `dataAttached` after confirm-attach.
- Hard bar: `/sessions/{id}/attach` and `/sessions/{id}/confirm-attach` must not 404. Confirm-attach is the only setter of `dataAttached`. `/upload` is not the permanent attach path. No PR.
- Session / run ID:
- Current research stage: DATA-COMPLETE DC-BE-attach restore
- Current review / approval gate: implementing
- Verified facts:
  - Starting tip had DC-BE-suggest + infer-design but no attach router; CK-WRITE-1 404 was missing routes
  - Intended implementation lives on `feat/fm-e-build-data-complete-1-dc-be-attach` @ `25df49e`
- Current hypothesis: wiring DC-BE-attach onto the recut stack restores the DATA-COMPLETE / infer-design order without `/upload` as the hang path
- Changed files:
  - `backend/routers/attach.py`
  - `backend/services/data_attach.py`
  - `backend/services/classic5.py`
  - `backend/run_repository.py`
  - `backend/routers/sessions.py`
  - `backend/schemas/responses.py`
  - `backend/main.py`
  - `backend/tests/test_data_attach.py`
- Failed paths:
- Data / output evidence locations:
- Test evidence:
- Pending external state: no PR
- Next action: regen OpenAPI; run attach tests then `make test`
- Updated at: 2026-09-15

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。

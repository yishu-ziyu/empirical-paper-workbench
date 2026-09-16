# econpaper Codex Task State

> 复制为稳定 Task ID 文件。只保存新会话恢复下一步所需的当前工作集。

- Task ID: FM-E-BUILD-INFER-DESIGN-1 / INF-BE-confirm
- Status: complete
- Git context（分支可选）: `feat/fm-e-build-inf-be-confirm-1` from `feat/fm-e-build-infer-design-1` @ `2a663915`
- Goal: Human confirm locks `session.design` (draft → confirmed). Unconfirmed design must not unlock gold/classic prefilled spec.
- Hard bar: Confirm API only. No propose, suggest, attach, DID `allow_did`, chapters, FE chrome, or contract rewrite.
- Session / run ID:
- Current research stage: n/a (product lock, not a paper run)
- Current review / approval gate: confirm-design
- Verified facts:
  - `POST /sessions/{id}/design/confirm` stamps `status=confirmed`, `confirmed=true`, `confirmed_at`; rejects missing draft with 409 `design_not_proposed`.
  - Confirm does not set `dataAttached`, `allow_did`, `table1Confirmed`, `specConfirmed`, `main_specification`, or chapter bodies.
  - Gate hook for later integrate: `services.session_design.locked_design(state)` is None until confirm (accept bullet 4). After confirm it returns the locked object (accept bullet 5 hook; suggest not implemented).
- Current hypothesis:
- Changed files:
  - `backend/services/session_design.py`
  - `backend/routers/design.py`
  - `backend/facade/__init__.py`
  - `backend/routers/sessions.py`
  - `backend/schemas/responses.py`
  - `backend/main.py`
  - `backend/tests/test_session_design_confirm.py`
  - OpenAPI codegen (`docs/api/openapi.json`, `frontend/openapi.json`, `frontend/src/types/api.ts`)
- Failed paths:
- Data / output evidence locations:
- Test evidence: `make test` — agent 818 passed / 2 skipped; backend 483 passed / 8 skipped; frontend 431 passed; check-api-drift green. Confirm slice: 16 passed in `backend/tests/test_session_design_confirm.py`. `make verify` not run (services not up).
- Pending external state: no PR (slice instruction).
- Next action: DC-BE-suggest / DID-BE-gate / PREWRITE must call `locked_design()`; INF-BE-propose still owns draft write.
- Updated at: 2026-09-15

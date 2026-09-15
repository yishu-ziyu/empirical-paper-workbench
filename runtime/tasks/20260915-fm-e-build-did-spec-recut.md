# econpaper Codex Task State

- Task ID: FM-E-BUILD-DID-BE-SPEC re-cut (DECIDE-6)
- Status: active
- Git context（分支可选）: `feat/fm-e-build-did-spec-recut-1` from `feat/fm-e-build-find-merge-1` @ `9f154dda`. Parked tip `cursor/did-be-gate-8102` @ `71be39f1` is reference only.
- Goal: Hard-block missing treated×period when confirmed `design.method=did`. Force `y ~ treat * post` (or dummy) when the term is present. Do not revive catalog-id `allow_did` as source of truth.
- Hard bar: Trigger = confirmed method=did + interaction presence. Catalog `allow_did` is not the setter. OLS / confirmed non-did untouched. Het interaction hard-block still. No `| entity + time` substitute. No PR.
- Session / run ID:
- Current research stage: DID-BE-spec recut
- Current review / approval gate:
- Verified facts:
  - Gate on find-merge tip already exposes `confirmed_did_method` / `did_interaction_missing` / derived `allow_did`
  - Parked spec forced/blocked on stamped catalog `allow_did`; recut consumes confirmed design instead
- Current hypothesis: confirmed `method=did` is the only spec trigger
- Changed files:
  - `agent/engine/did_spec.py`
  - `agent/nodes/set_direction.py`
  - `agent/nodes/estimate.py`
  - `agent/engine/readiness.py`
  - `backend/routers/outline.py`
  - `agent/tests/test_did_spec.py`
  - `backend/tests/test_did_spec.py`
  - `docs/did-narrow-exception-contract.md`
- Failed paths:
- Data / output evidence locations:
- Test evidence:
- Pending external state: no PR
- Next action: run tests; push branch; no PR
- Updated at: 2026-09-15

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。

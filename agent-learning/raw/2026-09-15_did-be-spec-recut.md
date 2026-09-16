# econpaper Codex Run Record

- Date: 2026-09-15
- Task ID / state file: FM-E-BUILD-DID-BE-SPEC re-cut / `runtime/tasks/20260915-fm-e-build-did-spec-recut.md`
- Commit / Git context: `feat/fm-e-build-did-spec-recut-1`
- Model and tool environment: Cursor cloud agent
- Dataset class / research method（不含原始数据）: formal 2×2 DiD after confirmed design.method=did
- Task: Hard-block missing treated×period when confirmed method=did; force y ~ treat * post when the term is present. Do not revive catalog-id allow_did.
- Result: pass
- Session / run ID:
- Verification commands: `make test`
- Output evidence locations: `agent/engine/did_spec.py`; estimate / set_direction / POST /direction

## 成功动作

- Trigger is `confirmed_did_method`, not stamped/catalog `allow_did`.
- Missing 2×2 term → `did_missing_interaction`: no coefficient, no treatment_row, results `write_blocked`, POST /direction 409.
- Interaction present → force `treat * post` / `treat_post` / `did` / `nj_after`; never `| entity + time`.
- OLS / confirmed non-did / form method=did without confirm remain on the existing path.

## 失败动作与根因

- First force pass treated `design.treated` / `design.period` slots as bindable names. Those slots are not the interaction. Removed; empty `interactions` then hard-blocks.

## 可复现条件

Seed confirmed `design.method=did` with empty interactions and treat-only columns → 409 / estimate error. Same design with `treat * post` (or dummy) estimates the 2×2 OLS term.

## 候选模式

A derived product flag (`allow_did`) is not enough after DECIDE-6: the spec trigger is confirmed `design.method=did`, and the identified 2×2 object must still be present or the path fails closed.

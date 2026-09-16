# econpaper Codex Run Record

- Date: 2026-09-15
- Task ID / state file: 20260915-fm-e-build-did-narrow-1-did-be-spec / `runtime/tasks/20260915-fm-e-build-did-narrow-1-did-be-spec.md`
- Commit / Git context: `cursor/did-be-gate-8102`
- Model and tool environment: Cursor cloud agent
- Dataset class / research method（不含原始数据）: formal Card–Krueger / minwage 2×2 after allow_did
- Task: DID-BE-spec — force treated×period when allow_did; missing hard-blocks estimate and write-as-estimated
- Result: pass
- Session / run ID:
- Verification commands: `pytest agent/tests/test_did_spec.py backend/tests/test_did_spec.py backend/tests/test_allow_did.py backend/tests/test_outline.py`
- Output evidence locations: `agent/engine/did_spec.py`; estimate / set_direction / POST /direction

## 成功动作

- When `allow_did`, set_direction / estimate force `treat * post` or `treat_post`.
- Missing interaction → `did_missing_interaction`: no coefficient, no treatment_row, results write blocked, POST /direction 409.
- `method=did` without `allow_did` still uses the existing path (no TWFE unlock).
- allow_did setter and classic-5 CSV inventory not edited.

## 失败动作与根因

## 可复现条件

Title/catalog sets `allow_did`. Direction with `y ~ treat` and no post/dummy is refused. Direction or columns naming `treat * post` / `treat_post` estimates the 2×2 term.

## 候选模式

A named product gate (`allow_did`) is not enough: the identified object must be present on the spec, or the estimate/write path fails closed.

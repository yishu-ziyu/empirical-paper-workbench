# econpaper Codex Run Record

- Date: 2026-09-15
- Task ID / state file: FM-E-BUILD-FIX-OLS-LABEL · `runtime/tasks/20260915-fm-e-build-ols-label.md`
- Commit / Git context: `fix/fm-e-build-ols-label-1` from `4546e4de`
- Model and tool environment: Cursor cloud agent
- Dataset class / research method（不含原始数据）: OLS label path; CARD1995-class display
- Task: OLS user-visible estimate/engine label must say OLS, not `statspai.feols`
- Result: pass
- Session / run ID:
- Verification commands: targeted agent/frontend OLS-label tests; full agent 890 passed / 2 skipped; backend 550 passed / 8 skipped; frontend 434 passed (58 files); `check-api-drift` green. `make verify` not run (services not required).
- Output evidence locations: branch `fix/fm-e-build-ols-label-1`

## 成功动作

- Added `display_estimate_engine_label` / `displayEstimateEngineLabel`.
- OLS + *feols* displays as OLS on EvidenceView, StepTimeline, `_ok_table`, and `format_estimate_facts`.
- Stored `estimate.estimator` still records the engine that ran.

## 失败动作与根因

- Mapping every OLS engine to OLS broke the methods prompt contract that binds `statsmodels.ols`. Remap is *feols*-only.

## 可复现条件

Checkout `fix/fm-e-build-ols-label-1`. `make test`.

## 候选模式

User-facing method label and stored engine id stay separate. OLS must not claim feols; DiD may still show `statspai.feols`.

只记录可复核动作、去敏 ID 和证据位置；不得复制用户原始数据、论文正文、凭据、私人对话或隐藏推理。

# econpaper Codex Run Record

> 复制为 `YYYY-MM-DD_<short-task>.md` 后填写并保持不可变。完整 run 工件留在既有目录；本页只做去敏证据索引。

- Date: 2026-09-15
- Task ID / state file: FM-E-DATA-RIGOR-1 · `runtime/tasks/20260915-fm-e-data-rigor-1.md`
- Commit / Git context: `fix/fm-e-build-data-rigor-1` @ `810dfa7d2bb27986b8f17a6b136ba496c0dece3d`
- Model and tool environment: Cursor cloud agent
- Dataset class / research method（不含原始数据）: no user dataset; captain-local-real is an acquire stamp, not a bundled panel
- Task: Encode captain-local real panel upload as first-class acquire (`source=captain-local-real`); DATA-RIGOR P0 remains
- Result: pass
- Session / run ID:
- Verification commands: `make test` — agent 888 passed / 2 skipped; backend 550 passed / 8 skipped; frontend 431 passed (58 files). `check-api-drift` green. `make verify` not run (services not up).
- Output evidence locations: branch `fix/fm-e-build-data-rigor-1`; no PR

## 成功动作

- POST /upload of a non-toy file stamps `dataset_meta.source=captain-local-real`. Toys (`course-panel.csv`, `sanitized_sample.csv`, …) do not.
- Card demo provenance stays teaching-case; not captain-local-real.
- Find-data plan venues[0] and always-on candidate `source_id=captain-local-real` (`acquire=true`, `found=false`, url `/upload`).
- classic-5 `own_file.source=captain-local-real`.
- n<200 still `demo_success=false`. No Desktop auto-scan; no toy CSVs added.

## 失败动作与根因

- None after `make test`.

## 可复现条件

Checkout `fix/fm-e-build-data-rigor-1`. `make test`.

## 候选模式

Interim acquire for a real local CSV / Stata .dta (e.g. Desktop/经济学论文) is first-class and labeled `captain-local-real`. Teaching toys are never that source.

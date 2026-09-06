# 验收契约：Workbench v2 provenance 必须是真实 lineage，禁止 heuristic

Status: closed

前置：`workbench-v2-golden-path-rescue.md` 与 `workbench-v2-visual-phase.md` 已 closed。
本契约不重做视觉、不扩功能、不开新 PR；只修 PR #27（`review/workbench-v2`）上被外部验收打回的 provenance / runtime shape / CI 闸门。

## Change

Evidence 的「Fully traceable」只能在六层都有真实 lineage 时出现：Result、Specification、Estimator、Run（当前 estimate 的实际 producer run_id）、实际进入 estimator 的 analysis Dataset（可与 raw upload 区分）、实际存在并关联当前 run 的 Code artifact。任何一层是 latest / UI readiness / session-level guess，都不得计为 present。Overview 与 Evidence 对 `estimate.table_rows` 使用同一套安全 parser，真实 API 的 `string[]` 形状不再崩溃。远端 `make test-agent test-backend` 所用 venv 自带 pytest 等测试依赖。

## Not this

- 不算：继续用 `latest_run(session_id, kind="prewrite")` 填 Run 层，只是换了字段名。
- 不算：Evidence Dataset 仍只展示上传 metadata（name/rows/columns），没有估计实际读取的数据身份。
- 不算：`hasCode={ws.canExport}` 或任何「能导出论文 → Code present」的推断。
- 不算：只在 Evidence 修了 `table_rows`，Overview 仍 `as string` 后调用 `replace`。
- 不算：CI 靠开发机全局 pytest、或只在注释里写「记得装 pytest」。
- 不算：重做视觉、扩功能、开新 PR、改 main、合并 PR。

## Evaluator

validator 子代理独立复核程序化检查（只读契约 + 跑程序）。C7 浏览器实弹由主 agent 执行并把断言/截图归档；validator 复核归档证据与可重放测试。用户保留主观视觉最终验收权。本阶段不改视觉，不要求新视觉截图替代旧图。

## Checks

- [x] C1 Run provenance 精确关联 producer — 程序: `make test-backend`（新增回归）— 预期: 同一 session 存在两个 prewrite runs；当前 estimate 来自旧 run 或指定 run 时，即使另一个 run 更新，`GET /sessions/{id}/evidence` 的 `provenance.run_id` 仍等于 estimate 持久化时记录的实际 producer run_id。Evidence 不得调用 `latest_run(..., kind="prewrite")` 推断来源。代码检索：`backend/routers/evidence.py` 不再把 latest prewrite 当作当前 estimate 的 run。

- [x] C2 Dataset provenance 指向估计实际使用的数据 — 程序: `make test-backend`（新增回归）— 预期: 估计/prewrite 持久化时写入实际进入 estimator 的分析数据身份（复用 cleaned dataset / run artifact / manifest；至少含 artifact/path/version/hash 中可证明身份的稳定字段）。测试构造 raw upload 与 cleaned/transformed dataset 不同身份；Evidence `provenance.dataset` 指向 cleaned/分析版本，不得把 raw upload metadata 当成估计输入。

- [x] C3 Code provenance 只认真实 artifact — 程序: `make test-frontend` + `make test-backend`（两条前端用例 + 后端 provenance 字段）— 预期: Code 层 present 只来自 Evidence provenance 中实际存在、且关联当前 estimate producer run 的 code artifact / manifest entry。`canExport=true` 但没有 code artifact → 完整性卡为 5/6，不得显示 Fully traceable。实际 code artifact 存在并关联当前 run → 才允许 6/6 Fully traceable。`WorkbenchArtifact` 不再传 `hasCode={ws.canExport}`。

- [x] C4 `estimate.table_rows` 共享安全 parser — 程序: `make test-frontend`（共享 normalization 单测 + Overview fallback 用例）— 预期: 抽出单一 normalization/parser，安全接受 `string | string[] | null | unknown`；真实 API 的 `string[]` 形状可解析。Overview Key Results 走同一 parser，不再 `as string` 后调用 `replace`。新增测试：Overview 收到 array-shaped `table_rows` 时渲染行且不抛 `raw.replace is not a function`。

- [x] C5 CI venv 自带测试依赖 — 程序: 检查 `.github/workflows/ci.yml` + `make test-agent test-backend` 所用安装路径 — 预期: 存在明确的 test/dev requirements（或等价最小可靠安装），CI 的 backend+agent job 在创建 venv 后安装这些依赖；`agent/.venv/bin/python -m pytest` 与 `backend/.venv/bin/python -m pytest` 不再报 `No module named pytest`。不依赖开发机全局环境。

- [x] C6 Evidence 文档收紧 Fully traceable — 程序: 阅读本文件 + `docs/acceptance/workbench-v2-visual-phase.md` C3 — 预期: 明文规定 Fully traceable = 六层都有真实 lineage（Result / Specification / Estimator / 实际 producer Run / 实际 analysis Dataset / 实际 Code artifact）。heuristic、latest、UI readiness、session-level guess 任一存在都不得计为 present。视觉阶段旧表述「生成过章节 → 6/6」被本契约取代，不得再作为完成标准。

- [x] C7 浏览器 provenance 实弹 — 程序: `make dev`（DEBUG=true + ECONPAPER_LLM=mock）+ 浏览器走查，不是普通 Golden Path — 预期五场景：
  1. 同 session 连续两次 prewrite，当前 estimate 的 producer run 不串到后一次（若当前 estimate 仍来自第一次）或精确等于真正产生它的那次；
  2. raw dataset 与 cleaned dataset 可区分，Evidence Dataset 层指向估计实际使用的版本；
  3. code artifact 缺失时显示 5/6，即使能导出论文；
  4. code artifact 真正生成并关联当前 run 后才显示 6/6；
  5. Overview 使用 array-shaped `table_rows` 不崩；console 无 uncaught error。

- [x] C8 推送到原 PR，不改 main — 程序: `git status` + `git log` + `gh pr view 27` — 预期: 提交在 `review/workbench-v2`；push 到 origin 该分支；未 checkout/push main；未合并 PR #27；GitHub Actions 全部 job 最终状态可报告。

## Evidence

程序化（validator ACCEPT，`docs/acceptance/workbench-v2-provenance-lineage-validator.md`）：
- `make test-backend` 389 passed / 8 skipped；`make test-agent` 805 passed / 1 skipped；`make test-frontend` 322 passed；`make check-api-drift` 绿。
- C1 新测：`test_evidence_run_id_follows_older_producer_after_newer_prewrite`、`test_evidence_run_id_stays_on_specified_producer_after_later_run`。`rg latest_run backend/routers/evidence.py` 无匹配。
- C2 新测：`test_evidence_dataset_points_at_cleaned_not_raw`、`test_evidence_without_analysis_dataset_does_not_use_upload_metadata`、`test_estimate_stamps_source_run_id_and_cleaned_dataset`。
- C3 新测：`test_evidence_code_artifacts_only_for_producer_run`；`canExport-equivalent chapters without code artifact stay 5/6`；`real code artifact for the producer run allows Fully traceable 6/6`。`hasCode={ws.canExport}` 已删除。
- C4：`normalizeEstimateTableSource` 覆盖 array/string/null/unknown；Overview `renders Key Results rows from array-shaped table_rows`。
- C5：`requirements-dev.txt`（pytest + pytest-asyncio）；CI 与 `make install-*` 装进 agent/.venv 与 backend/.venv。
- C6：本文件 + visual-phase C3 收紧 Fully traceable 定义。

浏览器实弹（2026-09-06，DEBUG=true + ECONPAPER_LLM=mock，session `76ab8bd9-e109-4a60-ac70-d3a9df4c8e18`）：
1. 两次 prewrite：`891370a4-f64f-407f-a3d3-97751de25ff6` 与 `6fec93af-0e18-4ea4-8031-8829a7eb153e` 均 SUCCEEDED。当前 estimate.source_run_id 仍为第一次 `891370a4…`（第二次未替换 estimate）。Evidence UI run 链接 `891370a4-f64`，不串到 latest `6fec93af`。
2. Snapshot dataset = `course-panel.csv`（upload metadata，无 hash/path）。Evidence dataset = cleaned sidecar `…/05_filter_0.csv`，`role=cleaned`，sha256 `3b7a66fa614c…`，24 行 5 列。
3. 第一次 prewrite 完成后、code artifact 出现前：`data-fully-traceable=false`，文案「可溯源 5/6 层，还缺：Code · 代码」，Code 层「暂无」。console `__errors=[]`。
4. 真实 code 写入 `outputs/code/891370a4…/analysis.{py,do,R,m}` 并关联该 producer 后：`data-fully-traceable=true`，「Fully traceable」，`evidence-code-link` 出现。
5. Overview Key Results 用 API `table_rows: string[]` 渲染 age/treat 两行，无 `raw.replace`、无「面板渲染出错」。全程 `__errors=[]`。

C8：提交在 `review/workbench-v2`，push PR #27；未改 main、未合并。SHA 与 GitHub Actions 状态见该次 push 后的记录。

## Named relaxations

- R1 本阶段不重做视觉、不要求新的 1280/1440 视觉截图替代旧图；C7 以 DOM/API 断言与 console 错误收集为准，截图仅作辅助。
- R2 CI 基线债务（pytest 未装进 venv）不视为本 PR 引入的 regression，但必须在本契约内修好远端闸门。
- R3 浏览器走查使用 `ECONPAPER_LLM=mock`（DEBUG=true）：文案质量不在范围；estimate 必须是真实统计执行。
- R4 Dataset 身份字段允许在 artifact / path / version / hash 中取可证明的子集，不强制四者齐备；但必须能把 raw upload 与 cleaned/transformed 版本区分开。
- R5 若某次 prewrite 同时更新了 estimate，则「当前 estimate 的 producer」就是这次 run；C1/C7-1 的反例是「estimate 仍来自旧 run，后一次 run 已存在」。

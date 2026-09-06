# 验收契约：Workbench v2 收敛——唯一后端真相源 + Golden Path + 主界面重建

Status: closed

Baseline（2026-09-05，main@6883a91，工作树干净）：
- `make test` 全绿（frontend 45 文件 / 322 tests，agent + backend pytest 全过）
- `cd frontend && npm run build`（tsc -b + vite build）通过（781kB chunk 警告为既有）
- 已知架构事实：后端已有 durable Run 引擎（RunRepository/runner/SSE）、`facade.instrument_fields` 投影、
  `agent/engine/readiness.py` 写作门（TRUTH_KEYS）、run_store 工件（manifest/trace/checkpoints）、
  `GET /sessions/{id}/artifacts` 与 `/trace`；`RunRepository._active_run` 查询存在但无 HTTP 端点。
  前端 `workspace.ts`（1751 行）用 localStorage/sessionStorage 保存业务真相
  （LS_CSV_KEY/LS_COLS_KEY 数据集元信息、LS_ACTIVE_RUN_KEY run 句柄、LS_PENDING_RUN_KEY 整份 direction 表单）、
  自带 DeskSnapshot 重复类型；App.tsx 用布尔堆推导流程。

## Change

用户打开 econpaper 后面对唯一的工作台主路径：上传样例 CSV → 确认研究方向 → 真实估计 →
在 Evidence 视图看到 β/SE/p/N 及其完整来源链 → Results 章只用这个真实数字写作。
刷新页面（清掉前端存储也一样）后，工作台从后端 snapshot 恢复全部研究状态与进行中的 run。

## Not this

- 不算：只写了 ADR/组件搭了架子但浏览器里走不通 Golden Path。
- 不算：前端 mock/hardcode 一个系数让 Evidence「看起来有数字」。
- 不算：重写 StatsPAI/清洗管道/38 种方法 UI、引入新框架或新状态库。
- 不算：一次性删光 legacy 页面（允许保留代码但从主路径退位）。
- 不算：`make test` 里混入 skip/pending 掩盖失败。

## Evaluator

validator 子代理独立复核（只读契约 + 跑程序）。C3/C4/C7 的浏览器实弹部分由主 agent
用 ZCode 内置浏览器执行并把截图/断言结果归档到 Evidence 区；validator 复核归档证据与
可重放的程序化检查。用户保留主观视觉/交互的最终验收权。

## Checks

- [ ] C1 后端 Project Snapshot 是唯一研究状态读模型 — 程序: `make test-backend`（新增用例）+ `curl GET /api/sessions/{id}`（seeded session）— 预期: SessionInfoResponse（或等价既有端点）除既有字段外包含 `dataset`（name/rows/columns，来自后端）、`active_run`（{run_id,kind,status}|null，来自 RunRepository）、`degradations` 可见摘要；estimate/research_direction/outline/body_chapters/write_blockers 继续存在。前端不再为这些字段维护 sessionStorage 副本。
- [ ] C2 Evidence 读模型端点 — 程序: `make test-backend`（新增用例）— 预期: `GET /api/sessions/{id}/evidence` 返回 main-estimate 读模型：estimate 数字（coef/se/p/n/estimator/method/formula/treatment_row/table_rows/status）、specification（研究设定）、identification（star/failed/report）、robustness 状态、provenance（run_id+事件尾部或 trace、dataset 出处、artifacts 清单引用）。全部取自 facade state + run_store + RunRepository，不建第二存储；estimate 缺失时 `available=false` + blockers，不报 500。
- [ ] C3 刷新恢复走后端，不靠前端业务存储 — 程序: ① vitest 用例（清空 storage → 模拟恢复路径断言调用 session snapshot 并按 active_run 订阅）；② 浏览器实弹：prewrite run 进行中清 localStorage+sessionStorage 后刷新，运行中状态与完成后结果仍正确恢复 — 预期: 两处均过；`LS_ACTIVE_RUN_KEY`/`LS_CSV_KEY`/`LS_COLS_KEY` 不再作为恢复真相源（允许保留 pending command 的 idempotency key：`LS_PENDING_RUN_KEY`/`LS_PENDING_UPLOAD_KEY` 按「短期 command 投递」豁免，见 Named relaxations）。
- [ ] C4 Golden Path 浏览器实弹（真实估计）— 程序: ZCode 内置浏览器，`make dev`（DEBUG=true + ECONPAPER_LLM=mock）— 预期: 用样例入口上传 `course-panel.csv` → 提交样例方向 → Evidence 视图显示 β/SE/p/N；这些数字与 `statsmodels`/pandas 对同一 CSV 独立复算 `income ~ age + treat` OLS 结果一致（容差 1e-6），且与 `/api/sessions/{id}/evidence` 返回一致；Results 章生成成功且正文引用同一系数。console 无本次改动引入的 uncaught error。
- [ ] C5 数字先于正文（失败也要显式）— 程序: `make test-backend`（补 failure path 用例：estimate 失败/缺失时 direction run 的产物状态 + results 409）+ 前端用例 — 预期: 无 estimate 的 session 请求 results 章 → 409 write_blocked（readiness 门已有，须有测试覆盖且未被本次弱化）；estimate 失败时 UI 呈现明确失败/degraded 状态与下一步建议，无无限 loading、无伪造成功。
- [ ] C6 前端 workflow truth 收敛 — 程序: grep 断言 + `make test-frontend` — 预期: `workspace.ts` 不再持有 DeskSnapshot 式重复业务模型（改用后端 snapshot 类型）；run 生命周期真相来自后端（snapshot.active_run / run 端点），`workspaceRunRecovery.test.ts` 语义更新为后端恢复；App.tsx 的 blocking decision 仍可做 presentation 推导，但输入全部来自 snapshot 字段。`workspace.ts`+`App.tsx` 合计行数较 baseline（2652）显著下降或其内业务状态 owner 显著减少（validator 按结构判断，不以行数为硬门槛）。
- [ ] C7 Workbench v2 单一主路径与布局 — 程序: 浏览器截图 1280×800 与 1440×900 — 预期: 统一 Workspace Shell：顶部项目名+Run/Export；左栏研究对象清单（Question/Data/Design/Evidence/Literature/Paper，状态来自 snapshot）；中栏当前 artifact（Evidence 为一等视图）；右栏 Agent 当前在做什么/为什么/blocking decision/[Action]；底部 run 状态条。无横向 overflow、无 panel 崩坏。Desk 退为建项对话入口（不再内嵌第二套工作台面板），Guide 仅显式进入，Spike 仅 /spike 路由，均不与工作台竞争「产品本体」。
- [ ] C8 全局回归 + 决策记录 — 程序: `make test` + `cd frontend && npm run build` + `git diff` 审查 — 预期: 全绿（无 skip 掩盖）；build 通过；ADR 落盘 `docs/adr/0013-workbench-v2-truth-owner.md`（旧系统为何失控、truth owner=后端 Run Engine/SessionStore、前端允许保存什么、Snapshot 契约、Golden Path、退役/隐藏但未删的 legacy 面、明确 out-of-scope 清单）；无明显死代码/调试日志/临时文件残留。

## Evidence

浏览器实弹走查（2026-09-05，DEBUG=true + ECONPAPER_LLM=mock，`make dev`，ZCode 内置浏览器，
会话 1405ca2d-29da-4913-9d3e-84eb9351eb37）：

- **C1**：`GET /sessions/{id}` 返回 `dataset: {name: "course-panel.csv", rows: 24, columns: [id,year,income,treat,age]}`、
  `active_run`（运行中非空/完成后 null）、`degradations: []`、estimate/research_direction/outline（6 章）/
  body_chapters/write_blockers 全量。后端用例：`backend/tests/test_evidence.py` 9 条 + snapshot 用例，`make test-backend` 全过。
- **C2**：`GET /sessions/{id}/evidence` 返回 `available: true`、estimate
  `{coef: -0.06870135850794869, se: 0.008348243185348042, p: 5.218116339023027e-08, n: 24, estimator: statspai.feols, formula: "income ~ age + treat"}`
  + specification + identification/robustness + provenance（run_id 02cf5dad… SUCCEEDED、dataset、trace 尾部、artifacts 9 个）。
- **C3①**：`frontend/src/__tests__/SnapshotRecovery.test.tsx` 过（storage 清空→snapshot 恢复→按 active_run 订阅 SSE；
  `econpaper_active_run_id:*`/`econpaper_csv_meta`/`econpaper_data_columns` 均为 null）。
- **C3② 浏览器实弹**：提交方向后同一单元格内 `localStorage.clear()+sessionStorage.clear()`（仅回填 session id）→ reload：
  刷新后 0.4s 即显示「正在估计…」并持续到 8.8s run 结束转「空闲」，directionSummary「OLS · income ~ age」与读数全部恢复
  （DOM 轮询时间线记录）。运行结束后再次清存储刷新，完成态（estimate/readout/章节）同样恢复。
- **C4**：空桌 → 了解产品 → `guide-sample-btn` 上传 course-panel.csv → 清洗 8/8 成功 → 样例方向预填并提交 →
  prewrite run 真实执行。Evidence 视图（testid `evidence-view`）显示 β/SE/p/N，页面数值与 `/evidence` 端点及
  statsmodels 独立复算（`-0.06870135850794397`）差 ≈4.7e-12 < 1e-6。results 章生成成功（status=generated），
  正文确定性附带真实主表 `age | -0.0687 | 0.0083 | 0.0000`，grounding_failures=[]；mock LLM 文案部分
  `generation_degraded=true` 如实标注（见 R1）。
- **C5**：坏列方向（dv=no_such_column）→ estimate.status=error → `/evidence` 返回 `available: false, blockers: [estimate_failed]`
  （非 500）；UI 显式失败卡「估计没有跑成…下一步：修改研究设计或数据列后重新运行」+ `blockers: estimate_failed` +
  左栏「β —」，无无限 loading、无伪造成功。无 estimate 时 results 409 由 `test_results_chapter_stays_409_when_estimate_failed`
  覆盖（readiness 门未弱化）。
- **C6**：grep 断言 workspace.ts/App.tsx 中 `DeskSnapshot`/`LS_CSV_KEY`/`LS_COLS_KEY`/`LS_ACTIVE_RUN_KEY` 均为 0；
  workspace.ts+App.tsx 行数 2652 → 2352（另拆 EvidenceView/ResearchRail/WorkbenchArtifact 展示组件）；
  `workspaceRunRecovery.test.ts` 重写为后端恢复语义。46 个测试文件 / 322 tests 全过。
- **C7**：截图（docs/acceptance/evidence-workbench-v2/）：`paper-view-1280x800.png`、`evidence-view-1280x800.png`、
  `evidence-view-1440x900.png`。1280×800 与 1440×900 下 `documentElement.scrollWidth == clientWidth`（无文档级横向溢出），
  三栏 Shell（左研究对象清单 Question/Data/Design/Evidence/Literature/Paper、中 artifact、右 decision/进度、底 run 状态条）
  完整可操作；右栏研究结构树存在 ~10px 内层滚动余量，视觉无裁切（评估为非「明显 overflow」）。Desk 仅剩建项对话
  （内嵌工作台面板已删），Guide 仅显式进入，Spike 仅 /spike。
- **C8**：`make test` 全绿（check-api-drift 三段同步；agent 802 passed/1 skipped 既有、backend 384 passed/8 skipped 既有、
  frontend 46 文件/322 tests）；`npm run build`（tsc -b）通过；ADR `docs/adr/0013-workbench-v2-truth-owner.md` 落盘；
  git diff 复查无 console.log/debugger/临时文件。浏览器 console 全程 `window.__errors == []`（每次 reload 后重挂收集器）。

validator 报告：
- 第一轮（2026-09-05）：C1–C6、C8 全 PASS；C7 FAIL——归档的 evidence-view-1440x900.png 实际 1190×743 且右栏被裁
  （IAB 标签页 reload 后回落自由尺寸视口时抓取，归档操作缺陷，非应用布局缺陷）→ REJECT。
- 修复：以真实 1440×900 视口重截覆盖；sips 实测三张归档图（1440×900 / 1280×800 / 1280×800）逐像素与文件名一致，
  图内右栏完整、四卡数字与端点一致。
- 第二轮单项复核：C7 PASS，事实说明一条（重截时序中新 run 3c491df5 替代 02cf5dad，两次 run 四卡数字完全一致，
  恰证估计可复现，不构成矛盾）→ **总结论 ACCEPT**。检查项无弱化，Named relaxations R1–R5 全部核对通过。

## Named relaxations

- R1 C4 浏览器走查使用 `ECONPAPER_LLM=mock`（DEBUG=true）：文献/大纲/章节文本由 mock LLM 产生，其文案质量不在本次验收范围；但 estimate 必须是真实统计执行（statsmodels/pyfixest），数字必须与独立复算一致。
- R2 C3 允许 localStorage 保留「短期 command 投递」信息：`LS_PENDING_RUN_KEY`（idempotency key + 待重放 direction）、`LS_PENDING_UPLOAD_KEY`、`LS_GUIDE_KEY`（UI pref）。豁免理由：请求响应丢失后的重放必须凭客户端侧 key；这与「业务真相」的区别在 ADR 中记录。研究状态恢复（run 状态、数据集、方向、估计、章节）一律走后端。
- R3 C7 布局验收以截图 + DOM 断言（scrollWidth ≤ clientWidth、目标元素可见可点）为准；主观视觉密度由用户最终拍板。
- R4 C1/C2 字段名允许与现有命名约定对齐（如 `dataset_meta` vs `dataset`），以「前端不再维护 sessionStorage 副本」为实质门槛；openapi 契约变更须走 `make gen-api` 并过 `check-api-drift`。
- R5 C4 数字一致性比对分两层：`/evidence` 端点原始值与独立复算一致（容差 1e-6，已证 ≈4.7e-12）；UI 显示层为人读格式（β/SE 4 位小数、p<1e-4 用科学计数、N 千分位），精确值保留在元素 `title` 与端点中。显示值与复算的比对按显示精度归一（4 位小数半单位 ≈5e-5）。

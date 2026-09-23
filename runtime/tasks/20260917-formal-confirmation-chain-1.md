# econpaper Codex Task State

> 独立 review 更新（2026-09-17）：**REJECT / 需要修复**。下方验收矩阵保留执行者原报告，不代表评审接受；反例、逐项重判与下一步见 `docs/reviews/20260917-formal-confirmation-chain-independent-review.md`。17 个源文件与交付哈希一致，评审未修改实现。

> 复制为稳定 Task ID 文件。只保存新会话恢复下一步所需的当前工作集。

- Task ID: FORMAL-CONFIRMATION-CHAIN-1
- Status: review-rejected
- Git context（分支可选）: `feat/progressive-research-flow` @ `2d83c2c9c716c0708eb5303840e76f51749583d1` + 接手未提交修复（原样保留）+ 本批 19 个文件改动/新增（未提交、未推送）
- Goal: 按 `docs/acceptance/formal-confirmation-chain.md` 执行首批正式研究确认链：空桌建问题 → 同会话提出/编辑/确认设计 → 同会话数据接入 → 确认挂接（dataAttached）→ 方向核查与真实预览 → 确认样本（table1Confirmed）→ 确认设定（specConfirmed）→ 启动估计 → 真实结果可追溯。
- Hard bar: C1–C12 全过或有实证受阻说明；先 RED 后 GREEN；不伪造确认；不绕过后端门槛；浏览器真实三进程验证；不 commit/push/merge/rebase/部署；不装依赖、不调付费模型、不委派 Agent。
- Session / run ID: 浏览器验证会话 `f4af0ecc-677e-49fc-9529-4147270d5731`；估计 run `5d98aa04-78a…`（SUCCEEDED）；隔离运行库 `/tmp/fcc1-runtime/`（已停止进程，库文件仍在，可复跑）
- Current research stage: 首批确认链全链路打通（合成数据链路），等待独立 code review
- Current review / approval gate: 交独立评审，不自行标 ACCEPT
- Verified facts:
  - 接手基线：`../empirical-paper-workbench-evidence/formal-confirmation-chain-1/baseline/`（2026-09-17 19:18 +0800，1034 文件 + SHA-256）
  - 基线 `make test` 全绿：agent 1066 / backend 636 / frontend 504 / drift ✅
  - 最终 `make test` 全绿：agent 1066 / backend 645 / frontend 509 / drift ✅（`logs/green-make-test.log` EXIT=0）
  - 隔离 `make verify` PASS（backend :8471 / frontend :5317，`logs/verify-isolated.log`）
  - C10 真实估计：β=33.01819506147341, n=60；独立复算 β=33.01819506147328（容差 1e-6 相对误差内一致）
- inherited_changes: 接手的 14 个修改 + 11 个未跟踪文件全部保留未动（逐文件核对见 `final/incremental-diff-vs-baseline.patch`，其中不含对它们的回退）
- baseline_snapshot / baseline_manifest: `baseline/`（git/ + files/ + manifest-sha256.txt）
- incremental_diff: `final/incremental-diff-vs-baseline.patch`（1335 行，16 个文件：12 改 + 4 新）
- final_manifest: `final/manifest-sha256.txt`（1011 项）+ `final/changed-files-sha256.txt`（19 项）+ `final/HEAD.txt`（`2d83c2c2…`）
- what_changed: 见下「本批改动」
- checks: C1–C12 见下「验收矩阵」
- red_before_green_after: `logs/red-backend-gates.log`（BE 5 fail → 8 pass）、`logs/red-frontend-chain.log`（FE 6 fail → pass）
- runtime: 三进程隔离启动方式见下「隔离运行环境」
- known_gaps_or_disagreements: 见下「剩余问题」
- facts_vs_requests: 见下「事实与请求冲突」
- commits_pushed: none
- Next action: 按独立 review 建 FORMAL-CONFIRMATION-CHAIN-2 修复任务；原交付留作基线。新产品顺序按 docs/specs/research-intent-to-design.md，不把旧数据前锁定要求继续固化。
- Updated at: 2026-09-17 21:05 +0800

## 本批改动（what_changed）

后端（4 改 + 2 新）：
- `backend/services/formal_chain.py`（新）：正式路径 fail-closed 门槛。`require_confirm_attached`（仅对显式 upload_readiness 的上传/经典目录时代会话；legacy 无该字段不拦；Card teaching 不拦）、`require_design_confirmed`（design 对象存在且未确认即 409，missing 不拦）。
- `backend/routers/outline.py`：`set_direction_endpoint` 加两道门槛（C4）；`confirm_prewrite_endpoint` record/continue 前同样校验。
- `backend/facade/__init__.py`：`prepare_prewrite_confirm` 加同样的双门槛（continue_estimate 的 facade 层防线）。
- `backend/tests/test_formal_chain_gates.py`（新）：8 条门槛测试。
- `backend/tests/test_outline.py`：`test_direction_allows_ready_and_legacy_sessions` 改为按 confirm-attach/legacy 三分参数（READY 未挂接→409，理由写入注释：旧断言编码 pre-confirm-attach 语义，FE dataAttachedGate 早已拦同一情形）；`test_post_direction_endpoint` 补 confirm-attach（真实用户路径）。
- `backend/tests/test_ws.py`：`test_ws_streams_title_chunks` 补 confirm-attach。

前端（9 改 + 2 新）：
- `frontend/src/lib/workspace.ts`：design/prewrite-gate 状态与动作（proposeDesign/confirmDesign/attachCsvToSession/confirmAttach/recordPrewriteConfirms/continueEstimate）；全部确认事实只取后端响应 + snapshot 回读；operation ref 防重复投递；`takeCsv` 按「有设计的正式会话→同会话 attach，否则 legacy /upload」路由；`ensureSessionActive`；方向提交对 409 data_not_attached/design_unconfirmed 的专属提示。
- `frontend/src/components/AttachPanel.tsx`：移除「点击即已挂接」本地成功判定；新 props attached/confirming/confirmError；等待只显示等待；失败保留候选可重试。
- `frontend/src/components/DesignProposalCard.tsx`（新）：题目编辑 + 提出 draft + 确认设计；确认后显示设计锁摘要。
- `frontend/src/components/PrewriteConfirmCard.tsx`（新）：真实 Table 1 + 执行方程；样本/设定两段确认互不等代；blockingDecision 展示；202 才跟踪 run。
- `frontend/src/components/WorkbenchArtifact.tsx`：问题页接设计卡/挂接卡/确认卡；数据页挂同一 AttachPanel（被引导入口有同一动作）；DirectionForm 以已确认设计播种并加 remount key。
- `frontend/src/App.tsx`：空桌确认 → 建同一会话 + 自动提出设计草稿（失败可重试）；方向摘要不再把停在预览的人带去论文页。
- `frontend/src/lib/dataAttachedGate.ts`：消费端识别 data_not_attached/design_unconfirmed。
- `frontend/src/components/DirectionForm.tsx`：DirectionFormData 增可选 qType 透传。
- `frontend/src/lib/i18nWorkbench.ts`：中英文案键。
- 测试：`formalConfirmationChain.test.tsx`（新，3 条 App 级链路）、`AttachPanel.test.tsx`（改，后端真相语义）。

## 验收矩阵（checks）

- C1 PASS — 浏览器 01–03：空桌确认 → POST /sessions + design/propose → draft → 编辑重提 → confirm → 回读 snapshot 一致；持久化键写入，刷新恢复（见 C7）。
- C2 PASS（组件/集成级）— AttachPanel 新测试「clicking confirm without backend never shows 已挂接」「waiting/failure retry」；链路测试 C3 的 409 拒绝 + 输入保留 + 重试成功。
- C3 PASS — 浏览器 04–05：同会话 attach（请求 /sessions/{id}/attach，无 /upload；Idempotency-Key 携带）；READY≠已挂接；confirm-attach 后 已挂接 由后端响应决定；数据页同一动作可挂。
- C4 PASS — `test_formal_chain_gates.py` 8 条：未挂接/草稿设计/未确认设计时 direction 与 prewrite confirm 直接 API 均 409 且不入队；legacy 与 Card 边界不拦。
- C5 PASS — 浏览器 06：方向 run 停预览，真实 Table 1（N=60）+ 方程；仅确认样本不自动确认设定（链路测试断言）；启动按钮两项未齐时禁用。
- C6 PASS — 链路测试 + 浏览器 08：record 200 只回读标志不等待 run；continue 202 跟踪返回 run；重复点击有投递守卫；按钮 disabled 与 blockingDecision 一致。
- C7 PASS — 浏览器 10：刷新后同一 session、同一题目、已确认对象恢复；运行中刷新重接由渐进运行修复批次覆盖（其契约 C1/C2 已过）。
- C8 PASS（回归级）— 渐进运行修复批的 run 所有权/旧事件隔离测试全绿（make test）；本批未新增跨对象污染面。
- C9 PASS（回归级）— #40 契约测试（identification-state-gate C1–C9）全绿；估计页显示「识别：尚未核查（—）」未伪装通过（截图 09）。
- C10 PASS — 浏览器 + API：β=33.01819506147341 vs 独立复算 33.01819506147328，n=60 一致；声明容差 1e-6 相对误差；证据页 5/6 层可溯源（代码层未导出不计入本批）。合成数据链路，已标注。
- C11 PASS — 浏览器 11：320×568 无横向溢出（0px），「目录/进度」浮钮可达，导航 overlay 可见；键盘 Tab+Enter 完成样本确认（截图 07）。VoiceOver 真人读屏未验（单列）。
- C12 PASS — 基线→最终三套测试不降：agent 1066=1066，backend 636→645（新增），frontend 504→509（新增）；Card/legacy 语义测试原样通过。

## 修复前后测试记录（red_before_green_after）

- RED：`logs/red-backend-gates.log`（test_formal_chain_gates 5 fail 3 pass，2026-09-17 19:30）、`logs/red-frontend-chain.log`（AttachPanel 3 fail + 链路 3 fail，19:35）。
- GREEN：`logs/green-frontend.log`（509 pass）、`logs/green-make-test.log`（drift + 1066 + 645 + 509，EXIT=0）。

## 隔离运行环境（runtime）

- 启动：backend `uvicorn main:app --port 8471`、runner `python -m runner`（均 `PYTHONPATH=<repo>:<repo>/backend DEBUG=true ECONPAPER_LLM=mock` + 空 MINIMAX/OPENAI key 强制全 mock + `DATABASE_URL/UPLOAD_DIR/RUNS_DIR/SESSIONS_PATH` 指向 `/tmp/fcc1-runtime`）；frontend `ECONPAPER_BACKEND_URL=http://127.0.0.1:8471 npm run dev -- --port 5317 --strictPort`。
- 数据来源：明确标注的合成 CSV（`synth_wages_schooling.csv`，60 行，LCG 确定性）。
- 模型：全部 mock（ECONPAPER_LLM=mock）；desk 在空 key 下降级启发式两轮出 ready。
- 清理：三进程已停止，端口 8471/5317 已释放；运行库 `/tmp/fcc1-runtime` 保留可复跑。

## 剩余问题（known_gaps_or_disagreements）

- C2 的延迟/网络失败注入为组件与集成测试级证据，浏览器主路径未做人工网络故障注入。
- C8/C9 为本批未触碰面的回归级证据（对应契约各自独立验收过），未在浏览器复跑专用场景。
- VoiceOver 真人读屏未验（按规范单列）。
- 证据页「可溯源 5/6 层，还缺：代码」——代码导出不在本批范围。
- 浏览器验证期间发现并已修：DirectionForm 挂载后不随设计锁播种（加 remount key）；方向 run 停预览时被自动带去论文页（App effect 例外）。
- 环境事故（如实记录）：隔离后端首次启动时 desk 路由经 SSOT（~/.config/ai-providers/env.local）拿到了 MiniMax key，desk discuss 走了真实模型约 10 轮问答（router.py desk 覆盖不受 ECONPAPER_LLM=mock 约束）。发现后立即以空 key 重启杜绝；此前调用不可撤回，计入教训。本批代码未改该路由。
- `uploaded_session` 等 fixture 直发 /direction 的旧语义用例已按「真实用户路径需先 confirm-attach」更新并留注释理由。

## 事实与请求冲突（facts_vs_requests）

- `test_direction_allows_ready_and_legacy_sessions`（READY 放行）与冻结契约冲突：以冻结契约为准改测试，理由注释在测试内。
- 规范称 AttachPanel「挂载处没有传 onConfirmAttach」——接手代码实际两处挂载都没传，且无任何 /design、/prewrite、/confirm-attach 前端调用；与 core-flow-map 判断一致，按事实接线。

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。

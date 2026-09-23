# econpaper Codex Task State

> 复制为稳定 Task ID 文件。只保存新会话恢复下一步所需的当前工作集。

- Task ID: FORMAL-CONFIRMATION-CHAIN-2
- Status: review-rejected（2026-09-18 独立评审 REJECT；原实施记录保留，评审结论见文末）
- Git context（分支可选）: `feat/progressive-research-flow` @ `2d83c2c9c716c0708eb5303840e76f51749583d1` + 全部继承未提交改动原样保留（含 FORMAL-CONFIRMATION-CHAIN-1 交付）
- Goal: 按 `docs/reviews/20260917-formal-confirmation-chain-independent-review.md` 修复 REJECT 项：先 R7（显式 mock 被真实供应商覆盖 + 基线采集越界），再 R1–R6、R8 与第 3 节幂等/响应丢失缺口；遵循 `docs/specs/research-intent-to-design.md` 新顺序（不写死"接入数据前必须确认设计"）。
- Hard bar: 反例先 RED 后 GREEN；mock 为最高优先级且不读真实凭据；不 commit/push/merge/rebase/部署；不装依赖、不调付费模型；基线只按源码 allowlist 采集；完成后停止修改交独立 review。
- Session / run ID: —
- Current research stage: R1–R8 前后端修复完成，评审反例全翻转；全量 make test 收尾中
- Current review / approval gate: 交独立评审，不自行标 ACCEPT
- Verified facts:
  - 环境核对一致：pwd/Git 根目录=`/Users/mahaoxuan/Desktop/AI 产品/empirical-paper-workbench`，分支 `feat/progressive-research-flow`，HEAD `2d83c2c9c716…`；两份必读文件已落盘并实读。
  - R7 已修（未提交）：`agent/llm/router.py` —— 显式 mock 在 `from_env` 入口直接返回且不调用 `load_ssot()`；pytest 无显式角色配置时同样不读 SSOT；删除 desk 的 MiniMax 覆盖块；新增 `LLMRouter.assert_mock_isolation()`（`_load_from_env` 末尾调用，mock 下任何角色非 mock 即 RuntimeError）。`backend/main.py` —— 启动时 `ECONPAPER_LLM=mock` 跳过 `load_ssot()`。
  - R7 测试：`agent/tests/test_llm_router.py` 新增 6 条（全角色覆盖/不读 SSOT/reload/断言自身/非 pytest 子进程含 SSOT 未加载断言/网络阻断）。RED：对 HEAD 代码 5 failed（子进程实测 `NONMOCK:desk,desk:reload,ssot`）；GREEN：修复后 22 passed。关联回归：agent 侧 5 文件 88 passed、backend `test_production_llm_config`+`test_typed_review_dep_declared` 15 passed（正确 venv）。
  - 基线已按源码 allowlist 重建：`../empirical-paper-workbench-evidence/formal-confirmation-chain-2/baseline/`（files/ 1028 个文件 + manifest-sha256.txt + git/ 上下文）。排除全部 `.env*`、密钥/凭据模式；chain-2 已改 4 文件在基线中还原为修复前内容。
  - 待清理敏感副本（仅列明，未删除；清理范围待用户确认）：`../empirical-paper-workbench-evidence/formal-confirmation-chain-1/baseline/files/.env`、`.../baseline/files/.env.docker`、`.../baseline/files/frontend/.env.development.local`。
  - R1（后端，未提交）：`backend/services/formal_chain.py` 新增显式会话类别（`SESSION_KIND_FORMAL/LEGACY/CARD_TEACHING`、`read_session_kind`、`formal_category_fields`）并让 `require_design_confirmed` 在正式路径上对 missing/null/malformed/draft 四种形态一律 409；`facade.create_session` + `SessionStore.create(state=…)` 与 `RunRepository.admit_upload` 写入 `session_kind=formal`；快照新增 `session_kind`。新会话不再可能靠"字段缺失"被判成 legacy。
  - R2/R3/R6（后端，未提交）：新增 `backend/services/formal_binding.py` —— design 执行投影指纹、dataset revision+fingerprint、preview identity（design+dataset+main_specification+Table 1+方程）、diagnosis identity；确认记录按 identity 绑定；`supersede*` 撤销并归档（`formal_chain.history`）；`align_direction` 保证执行内容=已确认版本；`run_binding` + `RunRepository.complete` 旧版本 run 结果只进历史；`record_confirms` 消费样本→设定顺序与 risk 决定；`prepare_prewrite_confirm` 消费 #40 三档许可；`record_prewrite_confirms` 的旗标改为版本绑定记录的投影。
  - R3 数据/样本变更：`RunRepository.admit_session_upload`、`admit_upload`、`facade.transform_variables`/`filter_sample` 都会撤销旧预览与旧确认。
  - 幂等（后端，未提交）：`RunRepository.find_run_by_key` 让 `/direction` 与 `continue_estimate` 以同一 Idempotency-Key 接回原 run；record 路径新增请求台账（同 key 同意图重放不写第二条确认）。
  - 测试：`backend/tests/test_formal_chain_gates.py`（R1，RED 8 failed → GREEN 26 passed）、新增 `backend/tests/test_formal_chain_binding.py`（R2/R3/R6/幂等，RED 17 failed → GREEN 23 passed，含样本规则变更后 +1 = 24 passed）。日志在 `../empirical-paper-workbench-evidence/formal-confirmation-chain-2/logs/`（`r1-red/r1-green/r2r3r6-red/r2r3r6-green/backend-baseline/backend-full-green/agent-suite-*`，均含日期）。
  - 全量：backend 687 passed / 8 skipped（基线 645 passed / 8 skipped）；agent 1072 passed / 2 skipped（用 `make test-agent` 的 PYTHONPATH；不带 PYTHONPATH 时 1 项 checkpointer 测试假失败，非回归）。`make check-api-drift` 通过（已 `make gen-api` 同步 `frontend/openapi.json`、`docs/api/openapi.json`、`frontend/src/types/api.ts`——生成物，未手改前端逻辑）。
  - 评审 7 个后端反例探针重跑全部翻转（`logs/backend-probes-rerun-20260917.log`）：missing design 409 不入队、无预览确认 409 旗标不变、锁 age 提 schooling 409、重提后旧确认失效旧方向 409、换数据清旧预览与旗标、confirm 许可无风险决定 409、显式 mock 下 generate/review/desk 全 mock。
- Current hypothesis: —
- Changed files: `backend/services/formal_chain.py`、`backend/services/formal_binding.py`(新)、`backend/facade/__init__.py`、`backend/facade/session_store.py`、`backend/routers/outline.py`、`backend/routers/design.py`、`backend/routers/sessions.py`、`backend/run_repository.py`、`backend/schemas/responses.py`、`backend/tests/test_formal_chain_gates.py`、`backend/tests/test_formal_chain_binding.py`(新)、`backend/tests/test_outline.py`、`backend/tests/test_did_spec.py`、`backend/tests/test_ws.py`、`backend/tests/test_facade.py`、`docs/api/prewrite-confirm.md`、`frontend/openapi.json`、`docs/api/openapi.json`、`frontend/src/types/api.ts`（后三者为 `make gen-api` 生成物）；R7：`agent/llm/router.py`、`backend/main.py`、`agent/tests/test_llm_router.py`；另 `runtime/STATE.md`、本任务文件（均未提交）
- Failed paths: 系统 python 跑 agent/backend 测试有环境噪音（缺 langchain 等）；必须用 `agent/.venv` / `backend/.venv`（Makefile 同款）。agent 套件还必须带 Makefile 的 `PYTHONPATH=<repo>:<repo>/backend`（否则 `test_checkpointer` 假失败）。
- Data / output evidence locations: 证据根目录 `../empirical-paper-workbench-evidence/formal-confirmation-chain-2/`
- Test evidence: 见 Verified facts 的测试/全量条目；日志目录 `.../formal-confirmation-chain-2/logs/`
- Pending external state: 继承改动全部未提交；不得 commit/push。chain-1 基线含敏感副本待用户确认清理范围。前端 R4/R5/R8 与 API 新字段对接由前端任务处理。
- Next action: 交独立 review（后端 R1/R2/R3/R6 + 幂等）；R4/R5/R8 及前端 API 对接另派
- Updated at: 2026-09-17

## 前端侧（R4/R5/R6 前端侧/R8 + 幂等 + 模块收束）—— 同日第二执行者

- 新模块 `frontend/src/lib/confirmationCommands.ts`：确认命令的所有权（`sessionId` + epoch + 对象版本，`isOwned`/`isCurrent`）、意图投递凭证（`intentKey` 环，sessionStorage，同意图重试复用同一 key）、409 码 → i18n 键映射（`refusalMessageKey`）、`classifyCommandFailure`（确定拒绝 vs 未知投递）、`readContinuePermission`（#40 三档）、`prewritePendingStep`（唯一待办事实）、`designRevisionOf`/`previewVersionOf`/`attachIntentSignature`。
- `frontend/src/lib/workspace.ts`：design propose/confirm、attach、confirm-attach、prewrite record、continue_estimate 全部改用该注册表；每个 await 后核对归属；`invalidateSessionWork` 清 operation/busy 与许可；快照消费 `riskConfirmed`、`permissions.continue_to_estimate`、`session_kind`；`confirmDesign(expectedRevision)`；`recordPrewriteConfirms('risk')`；`continueEstimate` 在响应丢失时回读 `active_run` 并用 `waitForTrackedRun` 接回；成功/回读不一致/确定拒绝三分支分开处理。
- 组件：`DesignProposalCard`（dirty 未保存不得确认旧草稿 + 确认携带 `expectedRevision` + 确认后显式修订入口）、`PrewriteConfirmCard`（三档许可、风险决定动作、顺序门、文案不冒充核查结果）、`App.tsx` 右栏下一步消费同一 `prewriteStep`、`i18nWorkbench.ts`/`i18n.tsx` 中英双键。
- 后端极小对接（R5 明确允许）：`backend/routers/design.py` 的 confirm 接受可选 `expectedRevision`，与当前草稿 `proposed_at` 不符返回 409 `design_revision_mismatch`（含 expected/submitted）；`make gen-api` 重生成 openapi.json ×2 与 `frontend/src/types/api.ts`（生成物，未手改），`make check-api-drift` 通过。`docs/api/prewrite-confirm.md` 补一段说明。
- 证据：`../empirical-paper-workbench-evidence/formal-confirmation-chain-2/logs/` —— `frontend-r4r5r6r8-idempotency-red-run1-20260917.log`（初版 RED 27 failed）、`frontend-r4-ownership-red-20260917.log`（终版 R4 8/8 RED）、`frontend-r4r5r6r8-idempotency-red-20260917.log`（终版全套 RED 29 failed/1 passed，用 chain-2 基线还原修复前源码跑出，跑完已按 sha256 复原）、`frontend-r4r5r6r8-idempotency-green-20260917.log`（43 passed）、`frontend-archived-reviewer-probes-20260917.log`（chain-1 评审的 5 条独立反例全部 GREEN）、`frontend-full-final-20260917.log`（75 files / 553 passed）、`backend-design-expected-revision-green-20260917.log`（临时探针，跑完已删）、`backend-full-chain2-frontend-task-20260917.log`（688 passed / 8 skipped）。
- 未解决点：`expectedRevision` 的校验是 router 内「读 state → 比较 → confirm」两步，不是与锁定同一事务（极小对接范围内）；`readContinuePermission` 的 `allow` 与 `unknown` 在前端都不过滤，只影响文案；前端没有消费 `session_kind` 做行为分支（仅投影保存）。

## 独立评审追加（2026-09-18）

结论 **REJECT，修复后重审**。报告：`docs/reviews/20260917-formal-confirmation-chain-2-independent-review.md`。

37 项交付指纹在评审开始时全部匹配。独立 153 项既有测试通过，桌面三进程正常路径已跑通；但五项新增 API 反例揭示用户所见版本未核验、秒级设计版本碰撞、方法特有执行参数未锁、数据替换后旧结果仍为当前、幂等键跨动作误接回。数据替换问题另有真实浏览器复现。

320×568 已完成确认动作，首轮估计 90 秒超时；同一 run 后续经过 4 次领取约 201 秒后成功，重新打开同一研究可恢复。保留超时和后续恢复两份证据，根因尚未定位，不归咎于小屏布局。真人 VoiceOver、全程 Tab 顺序和页面代码溯源未完整验收。

评审未修改产品实现。按报告在当前目录修复 S1–S5 并补证，不进入下一批意图优先实现；修复前重新保存去敏接手基线。旧敏感副本保持未读取、未清理。

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。

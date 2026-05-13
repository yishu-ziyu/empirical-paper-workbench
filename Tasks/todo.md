# Todo

## 当前目标

把实证系统从静态阶段页推进到真实执行过程可观察：前端能选择/展示真实 run_id，读取 observability API，并渲染 run steps、events、HITL gates、产物证据、执行者和证据等级。

## 状态机

- [x] 读取项目 AGENTS.md、architecture-v2 契约、Kimi handoff、Phase A BDD
- [x] 运行基线测试：`python3 -m unittest discover -s tests -v`
- [x] 阅读 StatsPAI Agent 时代文章及其关键子链接
- [x] 固化 StatsPAI/CoPaper 方法论到项目设计依据
- [x] 为 P0 可观察执行页写 BDD 行为
- [x] 为 P0 前端行为写失败测试：首次运行 6 条失败，后续新增历史 run 缺观测文件边界测试先失败
- [x] 实现最小前端闭环：选择/展示 run_id、加载 observability、渲染 steps/events/gates/artifacts/evidence
- [x] 运行相关测试并确认通过
- [x] 启动本地服务，用浏览器验证真实页面
- [x] 更新 handoff、manifest、decision-log、review
- [x] P1 后端：增加 gate resolve API 的 BDD、失败测试和最小实现
- [x] P1-A 前端：写 HITL gate resolve 行为文档
- [x] P1-A 前端：补失败测试，覆盖 confirm/reject/adjust、note、刷新和错误提示
- [x] P1-A 前端：实现 gate resolve 最小交互
- [x] P1-A 前端：运行单测、全量回归、JS/Python 编译检查
- [x] P1-A 前端：浏览器手动验收真实 run 的 gate resolve
- [x] P1-A 交接：更新 handoff、manifest、decision-log、review
- [x] P1-B 规划：写数据集选择 -> 启动真实 run -> 查看报告 BDD
- [x] P1-B 测试：覆盖 datasets API 本地文件证据、run dataset_source、非法路径拒绝、前端数据集启动按钮
- [x] P1-B 实现：datasets API 扫描 Data 目录并标记 local_file；run 创建接收 dataset_path 并持久化 dataset_source
- [x] P1-B 前端：数据与变量页显示本地数据文件、路径、shape、role、evidence，并可启动试运行
- [x] P1-B 验证：单测、全量回归、Python/JS 语法检查、浏览器手动验收
- [x] P1-B 交接：更新 handoff、manifest、decision-log、review
- [x] P1-C 规划：写 run 数据源进入实证执行页的 BDD
- [x] P1-C 测试：覆盖 observability 顶层 dataset_source、CSV shape、执行页数据源面板
- [x] P1-C 实现：observability 返回 run 级 dataset_source，run source 增加 row_count/column_count/role
- [x] P1-C 前端：实证执行页显示 Run 数据源、路径、shape、file_type、role、evidence
- [x] P1-C 验证：目标测试、全量回归、Python/JS 语法检查、浏览器手动验收
- [x] P1-C 交接：更新 handoff、manifest、decision-log、review
- [x] P1-D 规划：写变量角色确认面板 BDD
- [x] P1-D 测试：覆盖 observability 顶层 variable_roles、gate 状态绑定、前端变量角色面板
- [x] P1-D 实现：从 dataset_intake step 提取 key_variables，并绑定 gate_dataset_fields 状态
- [x] P1-D 前端：实证执行页显示 outcome/treatment/controls/instruments 与确认 gate 状态
- [x] P1-D 验证：目标测试、全量回归、Python/JS 语法检查、浏览器手动验收
- [x] P1-D 交接：更新 handoff、manifest、decision-log、review
- [x] P1-UI 规划：写实证执行页紧凑控制台 BDD，回应当前面板过于糟糕的问题
- [x] P1-UI 测试：先让紧凑控制台布局测试失败，再实现最小 UI 修正
- [x] P1-UI 实现：运行选择、run 摘要、数据源、变量角色合并为紧凑执行上下文；执行页改用 scoped system font、小圆角、低内边距
- [x] P1-UI 验证：前端测试、全量回归、Python/JS 语法检查、桌面/移动浏览器验收
- [x] P1-UI 交接：更新 handoff、manifest、decision-log、review
- [x] 产品重置：暂停继续堆 P1-E 实现，重新梳理端到端实证论文工作台主流程
- [x] 产品重置：新增 `docs/architecture-v2/product-flow-reset-2026-05-12.md`
- [x] 产品重置下一步：写 `docs/architecture-v2/product-workflow-contract-bdd.md`，定义 canonical stages、next action、状态转移和 run blocking 行为
- [x] 产品重置实现：后端 `GET /overview` 返回 `workflow_contract`，包含 canonical stages、next action、run readiness blockers
- [x] 产品重置前端：一阶导航收敛为 5 个工作区，首页显示下一步研究决策和 workflow spine
- [x] 产品重置前端：Data & Design 先进入变量角色确认，不再从数据卡片直接启动 run
- [x] 产品重置前端：Execution 先显示 Run Plan 预检和阻塞项，再显示 run 证据
- [x] 产品重置验证：目标行为测试、全量回归、Python/JS 语法检查、桌面/移动浏览器验收
- [x] 产品重置交接：更新 handoff、manifest、decision-log、review
- [x] P1-E 规划：写 VariableRoleSet 确认闭环 BDD，把变量角色作为产品级状态对象
- [x] P1-E TDD：新增 API/前端契约测试，并确认首次失败原因是 API 404 和前端编辑器缺失
- [x] P1-E 实现：新增 VariableRoleSet 读取/保存服务与 API
- [x] P1-E 实现：让 `workflow_contract` 读取已确认 VariableRoleSet 并解除 `variable_roles_unconfirmed`
- [x] P1-E 前端：Data & Variables 显示变量角色编辑器，保存后刷新 contract
- [x] P1-E 验证：目标测试、回归测试、全量 unittest、py_compile、node --check、浏览器验收
- [x] P1-E 交接：更新 handoff、manifest、decision-log、review
- [x] P1-F 规划：DesignSpec 确认 API + UI + 持久化状态，使 workflow contract 从 `confirm_design_spec` 推进到 RunPlan
- [x] P1-F/P1-G BDD：新增 DesignSpec/RunPlan 状态机行为文档
- [x] P1-F/P1-G TDD：新增 API/前端契约测试，并确认首次失败是缺少 design-spec/run-plan API 与 UI
- [x] P1-F/P1-G 实现：新增 DesignSpec/RunPlan 产品状态服务与 API
- [x] P1-F/P1-G 实现：`workflow_contract` 读取 DesignSpec/RunPlan approval，并推进到 `start_full_run`
- [x] P1-F/P1-G 前端：Data & Design 增加 DesignSpec 编辑器，Execution 增加 RunPlan 编辑器
- [x] P1-F/P1-G 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、浏览器验收
- [x] P1-F/P1-G 交接：更新 handoff、manifest、decision-log、review
- [x] P1-H 规划：把 `start_full_run` 接到真实 full run 路径，读取 approved RunPlan 并生成 `local_execution` 证据
- [x] P1-H BDD：新增 full run from RunPlan 行为文档，明确 Feynman 只作为 callable external research engine 参考
- [x] P1-H TDD：新增 API/前端契约测试，并确认首次失败是 `/runs/full` 405 和前端缺 full-run 主按钮
- [x] P1-H 实现：新增 `POST /api/v1/projects/{project_id}/runs/full`
- [x] P1-H 实现：full run 读取 approved RunPlan，写入 `plan_binding`、`research_engine`、`execution_evidence_level`
- [x] P1-H 前端：Execution ready 后显示“启动完整实证执行”主按钮并调用 full-run API
- [x] P1-H 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、浏览器真实 full-run 验收
- [x] P1-H 交接：更新 handoff、manifest、decision-log、review
- [x] P1-I 规划：把 full-run 结果推进到 Results & Draft，形成 FindingCard / Draft evidence binding 的最小闭环
- [x] P1-I BDD：新增 Results & Draft evidence binding 行为文档，明确没有 successful full-run 时不得伪造结果
- [x] P1-I TDD：新增 API/前端契约测试，并确认首次失败是 `/results-draft` 404 和前端缺 evidence binding 容器
- [x] P1-I 实现：新增 `GET /api/v1/projects/{project_id}/results-draft`
- [x] P1-I 实现：从最新 successful full-run 读取 `Results/json/analysis_result.json` 和 run manifest，生成最小 FindingCard
- [x] P1-I 前端：Results & Draft 页面显示 FindingCard 和 DraftSection evidence binding
- [x] P1-I 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、浏览器验收
- [x] P1-J 规划：基于 FindingCard 增加 claim review / accept-for-writing 状态，决定哪些结果可以进入论文正文
- [x] P1-K 规划：让 Manuscript 阶段只消费 `can_write_to_draft=true` 的 approved FindingCard，生成可审阅段落而不是直接覆盖正文
- [x] P1-K BDD：新增 Manuscript consumption 行为文档，定义 approved finding、provenance、空状态和前端容器
- [x] P1-K TDD：新增失败测试，确认首次失败是 `/manuscript-candidates` API 404 和前端缺少 candidate 容器/API/渲染函数
- [x] P1-K 实现：新增 Manuscript candidate 服务和 API，从 approved FindingCard 派生正文候选
- [x] P1-K 前端：Results & Draft 显示 Manuscript candidates 和 source/result/review provenance
- [x] P1-K 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、API 和浏览器验收
- [x] P1-L 规划：给 Manuscript candidate 增加人工审阅/确认状态，再考虑 promote/write-back/export
- [x] P1-L BDD：新增 Manuscript candidate review 行为文档，定义 candidate review、can_promote、非法 action/candidate 和前端操作
- [x] P1-L TDD：扩展 `tests/test_manuscript_consumption.py`，确认首次失败是缺少 `review_status/can_promote`、review API 404、前端缺少 candidate review 操作
- [x] P1-L 实现：新增 candidate review 持久化到 `state/product/manuscript_candidate_reviews.json`
- [x] P1-L 前端：Manuscript candidate 卡片显示 review_status/can-promote、审阅备注和 approve/needs_revision/reject 操作
- [x] P1-L 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、API 和浏览器验收
- [ ] P1-M 规划：approved candidate 的 promote/write-back/export preflight

## Review

- 新增 `tests/test_observable_execution_frontend.py`，覆盖 7 条 P0 前端行为。
- 扩展 `tests/test_observable_execution.py`，覆盖 P1 gate resolve 写回 gates、追加 events、更新 manifest、拒绝非法 action。
- P1-A 扩展 `tests/test_observable_execution_frontend.py` 到 10 条行为，覆盖 gate resolve 前端交互。
- 最终回归：`python3 -m unittest discover -s tests -v`，59 tests OK，skipped=1，最终一次耗时 5.570s。
- P1-B 最终回归：`python3 -m unittest discover -s tests -v`，65 tests OK，skipped=1，耗时 11.121s。
- P1-C 最终回归：`python3 -m unittest discover -s tests -v`，67 tests OK，skipped=1，耗时 36.309s。
- P1-D 最终回归：`python3 -m unittest discover -s tests -v`，69 tests OK，skipped=1，耗时 8.408s。
- P1-UI 最终回归：`python3 -m unittest discover -s tests -v`，70 tests OK，skipped=1，耗时 5.553s。
- Python 编译检查和 JS 语法检查通过。
- 浏览器验收使用 `http://127.0.0.1:8877`，真实 run `run_3ffe1e6c1f53` 可渲染完整 observability；历史 run `run_c617f095b232` 缺少观测文件时显示可恢复提示。
- 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1a`，真实 run `run_3ffe1e6c1f53` 的 `gate_dataset_fields` 已通过页面 confirm，显示 action/note/resolved_at，并刷新出 resolved 事件。
- P1-B 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1b3`：数据页显示 `analysis_sample.csv`、`本地文件`、`12 行 · 4 列 · csv · configured_final_dataset`、`Data/Final/analysis_sample.csv`；点击“用此数据启动试运行”后生成 `run_fc725d15b3c0`，manifest 写入 `dataset_source.evidence_level=local_file`。
- P1-C 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1c`：从数据页启动新 run `run_641c9770a1a8`，实证执行页 Run 数据源显示 `analysis_sample.csv`、`Data/Final/analysis_sample.csv`、`本地文件`、`12 行 · 4 列`、`csv`、`configured_final_dataset`；console errors/warnings=0。
- P1-D 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1d`：`run_641c9770a1a8` 的变量角色确认面板显示 `gate=gate_dataset_fields · status=open`、`outcome=wage`、`treatment=trained`、`controls=edu, experience`、`instruments=未识别`；console errors/warnings=0。
- P1-UI 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1ui3`：执行页 font 为 `-apple-system` 系统字体、panel radius `8px`、padding `12px`、桌面无横向溢出；移动端 390x844 下 `overflowCount=0`，metadata 使用 `pre-wrap`。
- 产品重置 TDD 失败证据：`python3 -m unittest tests.test_product_workflow_contract -v` 最初 2 条 API 测试因 `KeyError: workflow_contract` 报错，4 条前端测试因缺少 5 个工作区、`renderWorkflowContract`、`data-open-design-action`、`renderExecutionPreflight` 失败。
- 产品重置目标测试：`python3 -m unittest tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend -v`，23 tests OK。
- 产品重置最终回归：`python3 -m unittest discover -s tests -v`，76 tests OK，skipped=1，耗时 6.385s。
- 产品重置编译/语法：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 产品重置浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-flow2`：Workspace Home 显示 5 个工作区、下一步 `confirm_variable_roles`、9 个 workflow spine 阶段；Data & Design 显示 `analysis_sample.csv` 和“检查并确认变量角色”，无“用此数据启动试运行”；Execution 显示 `can_start_full_run=false` 和 `variable_roles_unconfirmed/design_unconfirmed/run_plan_missing`，桌面和 390x844 移动端均无横向溢出，console errors/warnings=0。
- P1-E TDD 失败证据：`python3 -m unittest tests.test_variable_role_confirmation -v` 首次 5 条失败，原因是 `GET/PUT /api/v1/projects/{project_id}/variable-roles` 返回 404，且前端缺少 `variable-role-confirmation-form`、`renderVariableRoleEditor` 和保存 API。
- P1-E 目标测试：`python3 -m unittest tests.test_variable_role_confirmation -v`，5 tests OK。
- P1-E 目标回归：`python3 -m unittest tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，39 tests OK。
- P1-E 最终回归：`python3 -m unittest discover -s tests -v`，81 tests OK，skipped=1，耗时 8.594s。
- P1-E 编译/语法：`python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过；`node --check Product/web/assets/app.js` 通过。
- P1-E 浏览器验收使用 `http://127.0.0.1:8765/?v=20260513-p1e`：Data & Variables 显示 VariableRoleSet 编辑器，保存后状态为 `approved · local_file`，`workflow_contract.next_action.id=confirm_design_spec`，blockers 只剩 `design_unconfirmed/run_plan_missing`；Execution preflight 仍正确阻止 full run；console errors/warnings=0，桌面无横向溢出。
- P1-F/P1-G TDD 失败证据：`python3 -m unittest tests.test_design_run_plan_state_machine -v` 首次 7 条失败；5 条 API 测试因 `/design-spec`、`/run-plan` 返回 404，2 条前端测试因缺少 DesignSpec/RunPlan 表单、渲染函数和保存 API 失败。
- P1-F/P1-G 目标测试：`python3 -m unittest tests.test_design_run_plan_state_machine -v`，7 tests OK。
- P1-F/P1-G 目标回归：`python3 -m unittest tests.test_design_run_plan_state_machine tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，46 tests OK。
- P1-F/P1-G 编译/语法：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/design_spec_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过。
- P1-F/P1-G 浏览器验收使用 `http://127.0.0.1:8765/?v=20260513-p1fg`：保存 DesignSpec 后状态为 `approved · local_file`，`workflow_contract.next_action.id=confirm_run_plan`，blockers 只剩 `run_plan_missing`；保存 RunPlan 后状态为 `approved · local_file`，`next_action.id=start_full_run`，blockers 为空，`can_start_full_run=true`；console errors/warnings=0，执行页无横向溢出。
- P1-F/P1-G 最终回归：`python3 -m unittest discover -s tests -v`，88 tests OK，skipped=1，耗时 83.833s。
- P1-H TDD 失败证据：`python3 -m unittest tests.test_full_run_from_run_plan -v` 首次 3 条失败；2 条 API 测试因 `POST /runs/full` 返回 405，1 条前端测试因缺少 `observable-run-full-button`、`v2api.runs.startFull`、`createFullRunFromPlan` 失败。
- P1-H 目标测试：`python3 -m unittest tests.test_full_run_from_run_plan -v`，3 tests OK。
- P1-H 目标回归：`python3 -m unittest tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_v1_local tests.test_observable_execution tests.test_observable_execution_frontend tests.test_product_workflow_contract -v`，39 tests OK。
- P1-H 编译/语法：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/project_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py Product/backend/observability_service.py` 通过。
- P1-H 浏览器验收使用 `http://127.0.0.1:8765/?v=20260513-p1h`：Execution preflight 显示 `start_full_run` ready；点击“启动完整实证执行”生成 `run_c424d6a11af7`，run mode=`full-run`、status=`succeeded`、`execution_evidence_level=local_execution`；manifest 写入 `run_plan_binding.evidence_level=local_file` 和 `research_engine.embedded=false/integration_mode=callable_external`；console errors/warnings=0。
- P1-H 最终回归：`python3 -m unittest discover -s tests -v`，91 tests OK，skipped=1，耗时 6.591s。
- P1-I TDD 失败证据：`python3 -m unittest tests.test_results_draft_evidence_binding -v` 首次有效失败为 4 条；3 条 API 测试因 `/api/v1/projects/{project_id}/results-draft` 返回 404，1 条前端测试因缺少 `results-findings-list`、`draft-evidence-sections`、`v2api.resultsDraft.get`、`renderResultsDraftEvidence` 失败。
- P1-I 目标测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v`，4 tests OK。
- P1-I 目标回归：`python3 -m unittest tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，31 tests OK。
- P1-I 编译/语法：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- P1-I API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/results-draft` 返回 `latest_run_id=run_c424d6a11af7`、`findings[0].treatment=trained`、`estimate=1.8505076802915557`、`artifact_path=Results/json/analysis_result.json`、`draft_sections` 绑定 `claim_evidence_level=local_execution`。
- P1-I 浏览器验收使用 `http://127.0.0.1:8765/?v=20260513-p1i`：Results & Draft 显示 `trained effect on wage`、`run_id=run_c424d6a11af7`、`run_plan_version=1`、`Results/json/analysis_result.json`；Draft evidence binding 显示 `Manuscripts/generated/paper_draft.md`、本地文件证据和真实执行证据；overflowCount=0，console errors/warnings=0。
- P1-I 全量回归：`python3 -m unittest discover -s tests -v`，95 tests OK，skipped=1，耗时 6.788s。

## 2026-05-13 P1-E VariableRoleSet 确认闭环

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-variable-role-confirmation-bdd.md`，把变量角色确认定义为真实产品对象。
- [x] TDD：新增 API/前端契约测试，先确认失败原因是功能未实现。
- [x] 实现：新增 VariableRoleSet 读取/保存服务与 API。
- [x] 实现：让 `workflow_contract` 读取已确认 VariableRoleSet 并解除 `variable_roles_unconfirmed`。
- [x] 实现：Data & Variables 显示变量角色编辑器，保存后刷新 contract。
- [x] 验证：运行目标测试、全量 unittest、py_compile、node --check、浏览器验收。

## 2026-05-13 P1-F/P1-G DesignSpec 与 RunPlan 状态机

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-design-run-plan-bdd.md`，定义 DesignSpec/RunPlan 的产品级确认行为。
- [x] TDD：新增 `tests/test_design_run_plan_state_machine.py`，先确认 API 404 和前端缺表单/函数的失败。
- [x] 实现：新增 `Product/backend/design_spec_service.py`，读写 `state/product/design_spec.json` 与 `state/product/run_plan.json`。
- [x] 实现：新增 `GET/PUT /api/v1/projects/{project_id}/design-spec` 和 `GET/PUT /api/v1/projects/{project_id}/run-plan`。
- [x] 实现：`workflow_contract` 读取 approved VariableRoleSet、DesignSpec、RunPlan，依次推进到 `confirm_design_spec`、`confirm_run_plan`、`start_full_run`。
- [x] 前端：Data & Design 增加 DesignSpec 确认表单；Execution 增加 RunPlan 确认表单。
- [x] 验证：目标测试 7 OK、目标回归 46 OK、全量回归 88 OK、Python/JS 静态检查通过、浏览器保存链路通过。

## 2026-05-13 P1-H Full Run From RunPlan

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-full-run-from-run-plan-bdd.md`，定义 full run 必须从 approved RunPlan 启动。
- [x] TDD：新增 `tests/test_full_run_from_run_plan.py`，先确认 `/runs/full` 和前端 full-run 主按钮未实现。
- [x] 实现：新增 `execute_full_run_from_run_plan()` 和 `POST /api/v1/projects/{project_id}/runs/full`。
- [x] 实现：full run response 与 manifest 绑定 `plan_binding`、`research_engine`、`execution_evidence_level`。
- [x] 前端：Execution 页面新增 `observable-run-full-button`，ready 后调用 `v2api.runs.startFull()`。
- [x] 验证：目标测试 3 OK、目标回归 39 OK、全量回归 91 OK、Python/JS 静态检查通过、浏览器真实 full-run 通过。

## 2026-05-13 P1-I Results & Draft Evidence Binding

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-results-draft-evidence-binding-bdd.md`，定义 FindingCard / DraftSection evidence binding。
- [x] TDD：新增 `tests/test_results_draft_evidence_binding.py`，先确认 API 404 和前端缺少 evidence binding 容器/渲染函数。
- [x] 实现：新增 `Product/backend/results_draft_service.py`，从最新 successful full-run、`analysis_result.json`、`paper_draft.md` 组装 evidence binding。
- [x] 实现：新增 `GET /api/v1/projects/{project_id}/results-draft`，无 full-run 时返回 409 `full_run_required`。
- [x] 前端：Results & Draft 页面显示 FindingCard 与 DraftSection evidence binding，区分 `local_execution` 与 `local_file`。
- [x] 验证：目标测试 4 OK、目标回归 31 OK、全量回归 95 OK、Python/JS 静态检查通过、浏览器真实结果绑定通过。

## 2026-05-13 P1-J Claim Review / Accept-for-writing

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-claim-review-bdd.md`，定义 FindingCard 人工审阅与 accept-for-writing 行为。
- [x] TDD：扩展 `tests/test_results_draft_evidence_binding.py`，先确认缺少 `review_status`、review API 404、前端缺少 review 操作。
- [x] 实现：扩展 `Product/backend/results_draft_service.py`，把 review 状态保存到 `state/product/finding_reviews.json`。
- [x] 实现：新增 `PUT /api/v1/projects/{project_id}/results-draft/findings/{finding_id}/review`，支持 `approve`、`reject`、`needs_revision`。
- [x] 前端：FindingCard 显示 `review_status`、`accept-for-writing`、审阅备注、approve/needs_revision/reject 操作。
- [x] 验证：目标测试 8 OK、目标回归 35 OK、全量回归 99 OK、Python/JS 静态检查通过、浏览器真实 approve 验收通过。
- [x] P1-K 规划：让 Manuscript 阶段只消费 `can_write_to_draft=true` 的 approved FindingCard，生成可审阅段落而不是直接覆盖正文。

## 2026-05-13 P1-K Manuscript Consumption

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-manuscript-consumption-bdd.md`，定义 Manuscript candidate 只消费 approved FindingCard。
- [x] TDD：新增 `tests/test_manuscript_consumption.py`，首次运行 5 条失败，原因是 `/api/v1/projects/{project_id}/manuscript-candidates` 返回 404，前端缺少 `manuscript-candidates-list`、`v2api.manuscriptCandidates.get`、`renderManuscriptCandidates`。
- [x] 实现：新增 `Product/backend/manuscript_candidate_service.py`，从 `GET /results-draft` 的 `can_write_to_draft=true`、`review_status=approved` FindingCard 派生正文候选。
- [x] 实现：新增 `GET /api/v1/projects/{project_id}/manuscript-candidates`，空状态返回 `approved_finding_required`，不修改 `Manuscripts/generated/paper_draft.md`。
- [x] 前端：Results & Draft 页面新增 `manuscript-candidates-list`，显示候选段落、finding/run/run_plan 绑定，以及 `source_draft`、`result_artifact`、`review_decision` provenance。
- [x] 验证：目标测试 5 OK、相邻回归 40 OK、全量回归 104 OK、Python/JS 静态检查通过、API 和浏览器真实验收通过。
- [x] P1-L：新增 Manuscript candidate review/promote 状态机。

## 2026-05-13 P1-L Manuscript Candidate Review

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-manuscript-candidate-review-bdd.md`，定义正文候选必须独立人工审阅。
- [x] TDD：扩展 `tests/test_manuscript_consumption.py` 到 10 条行为；首次运行失败原因是 candidate 缺少 `review_status`、review API 404、前端缺少 candidate review 操作。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `save_project_manuscript_candidate_review()`、`load_candidate_reviews()` 和 `candidate_review` provenance。
- [x] 实现：新增 `PUT /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/review`。
- [x] 前端：Results & Draft candidate 卡片显示 `review_status`、`can-promote`、candidate review 备注与 approve/needs_revision/reject 操作。
- [x] 验证：目标测试 10 OK、相邻回归 45 OK、全量回归 109 OK、Python/JS 静态检查通过、API 和浏览器真实验收通过。
- [x] P1-M：approved candidate 的 promote/write-back/export preflight。
- [x] P1-N：ready_for_export candidate 生成 write-back preview 和 export package manifest，不直接覆盖源草稿。

## 2026-05-13 P1-M Manuscript Promote Preflight

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-manuscript-promote-preflight-bdd.md`，定义 promote 只是导出前检查，不直接覆盖 `paper_draft.md`。
- [x] TDD：扩展 `tests/test_manuscript_consumption.py` 到 15 条行为；首次运行失败原因是 `/promote` API 404、前端缺少 `promotion_status`、`promoteManuscriptCandidate` 和 `data-candidate-promote-action`。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `save_project_manuscript_candidate_promotion()`、promotion state 读写和 `promotion_state` provenance。
- [x] 实现：新增 `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/promote`，未 approved candidate 返回 409 `candidate_review_required`。
- [x] 前端：Results & Draft candidate 卡片显示 `promotion_status`、`can_write_back`、promotion evidence 和“进入导出前检查”操作。
- [x] 验证：目标测试 15 OK、相邻回归 50 OK、全量回归 114 OK、Python/JS 静态检查通过、API 和浏览器真实验收通过。
- [x] P1-N：为 `ready_for_export` candidate 设计 write-back draft / export package manifest，不直接覆盖源草稿。

## 2026-05-13 P1-N Export Preflight Preview

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-export-preflight-bdd.md`，定义 export preflight 只生成预览和 manifest。
- [x] TDD：扩展 `tests/test_manuscript_consumption.py` 到 19 条行为；首次运行失败原因是 `/export-preflight` API 404、前端缺少 `export_status`、`preview_ready`、`writeback_preview_path`、`exportPreflightManuscriptCandidate` 和 `data-candidate-export-preflight-action`。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `save_project_manuscript_candidate_export_preflight()`、preview 文件生成、export package manifest 读写和 `export_package` provenance。
- [x] 实现：新增 `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/export-preflight`，未 `ready_for_export` candidate 返回 409 `candidate_promotion_required`。
- [x] 前端：Results & Draft candidate 卡片显示 `export_status`、`writeback_preview_path`、`export_manifest_path`、export evidence 和“生成写回预览”操作。
- [x] 验证：目标测试 19 OK、相邻回归 54 OK、全量回归 118 OK、Python/JS 静态检查通过、API 验收通过；浏览器插件最终传输中断，已用 API/DOM/static fallback 复核。
- [x] P1-O：把 export preflight 接入 Review & Export 页面，形成导出包验收台、evaluator checks 和 Frontier-Eng iteration log。

## 2026-05-13 P1-O Review & Export Package Workbench

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-review-export-package-bdd.md`，定义 Review & Export 必须读取 `preview_ready` export package，并显示 evaluator、证据路径和下一轮迭代。
- [x] TDD：新增 `tests/test_review_export_package.py`；首次运行 4 条失败，失败原因是 `/api/v1/projects/{project_id}/export-package` 404，前端缺少 `export-package-workbench`、`export-evaluator-checks`、`frontier-iteration-log` 和返回 Results & Draft 的入口。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `get_project_export_package()`，把 export preflight manifest 组装为 Review & Export 包。
- [x] 实现：扩展 `Product/app.py`，新增 `GET /api/v1/projects/{project_id}/export-package`。
- [x] 前端：Review & Export 页面新增 `export-package-workbench`，显示 candidate/run/section、`export_status=preview_ready`、`evaluator=passed`、writeback preview、manifest、result artifact、`can_write_back=false`。
- [x] 前端：新增 Frontier-Eng 式 `objective -> baseline -> evaluator -> feedback -> next_iteration` 迭代日志，并提供“回到 Results & Draft 查看候选来源”。
- [x] 验证：目标测试 4 OK、相邻回归 31 OK、全量回归 122 OK、Python/JS 静态检查通过、Chrome 可视化验收通过。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

- [x] 中文化 BDD：新增 `docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`，定义用户可见页面文案改为同义中文，API 字段和证据枚举不翻译。
- [x] 中文化 TDD：新增 `tests/test_frontend_chinese_copy.py`，并更新相邻前端契约测试，先锁定一级导航、阶段标题、执行/导出页面中文文案。
- [x] 中文化实现：更新 `Product/web/index.html` 与 `Product/web/assets/app.js`，把核心页面、按钮、状态说明和 workflow 文案切换为中文展示。
- [x] 档案界面 BDD：新增 `docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`，定义研究档案身份、相邻笔记、证据图例、收藏架和交互状态。
- [x] 档案界面 TDD：新增 `tests/test_archive_interface_visual_contract.py`；首次运行 4 条失败，原因是页面缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态标识。
- [x] 实现：在 `Product/web/index.html` 增加 `archive-shell` 和右侧 `archive-inspector`；在 `Product/web/assets/app.js` 增加 `archivePageNotes`、`mountArchiveInspector()`、`updateArchiveInspector()`；在 `Product/web/assets/styles.css` 增加纸张网格、档案条目、相邻笔记、证据 ledger、hover/focus/loading/empty/error 状态。
- [x] 验证：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 5 tests OK；`python3 -m unittest discover -s tests -v` 132 tests OK，skipped=1；`node --check Product/web/assets/app.js` 通过；Python 编译检查通过；Safari 可视化验收 `http://127.0.0.1:8765/?v=20260513-archive1` 通过。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

## 2026-05-13 P1-P Writeback Approval + DOCX Preflight

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-writeback-docx-preflight-bdd.md`，定义显式写回审批、docx 导出预检和 Review & Export 证据验收台。
- [x] TDD：扩展 `tests/test_review_export_package.py` 到 9 条行为；首次运行失败原因是导出包缺少 `writeback_approval`/`docx_preflight` 状态、POST API 404、前端缺少 clean evidence bench 结构。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `writeback_approvals.json` 与 `docx_export_preflight.json` 两类本地状态；审批只写状态，不覆盖 `Manuscripts/generated/paper_draft.md`。
- [x] 实现：扩展 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/export-package/{candidate_id}/writeback-approval` 与 `POST /api/v1/projects/{project_id}/export-package/{candidate_id}/docx-preflight`。
- [x] 前端：把 Review & Export 改成 `review-export-evidence-bench`，用证据表、写回审批面板、docx 预检面板替代拥挤的路径卡片堆。
- [x] 验证：目标测试 9 OK；相邻回归 36 OK；全量回归 142 OK，skipped=1；Python 编译和 JS 语法检查通过。
- [x] 可视化验收：重启 8765 旧服务后，Safari + Computer Use 验证“批准写回 -> 运行 docx 预检”闭环，页面显示 `写回：已审批` 和 `预检通过`。
- [x] 交接：更新 handoff、manifest、decision-log、review。

## 2026-05-13 P1-R Clean Workbench Visual Pass

- [x] 参考研究：读取 JupyterLab / Grafana / OpenMetadata 的公开产品文档，提炼为“主工作区 + 属性检查器 + 信息面板/记录，而不是装饰卡片堆叠”。
- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`，定义清洁工作台、变量角色入口不重叠、右侧属性检查器、record/list 替代大卡片。
- [x] TDD：新增 `tests/test_clean_workbench_visual_contract.py`；首次运行 4 失败 1 通过，失败原因是仍存在纸格背景、auto 双列、右侧档案索引过重、缺少 record/list 结构。
- [x] 实现：去掉 archive shell 的纸格噪声和厚重阴影，右侧 `archive-inspector` 调整为 `inspector-rail`，变量角色确认入口改为单列 `research-record-card` + `research-step-list`。
- [x] 实现：修复截图中的重叠根因，`.variable-role-workflow-layout` 不再使用 `minmax(0, 1fr) auto`，长路径使用 `overflow-wrap:anywhere`。
- [x] 验证：目标视觉契约测试 15 OK，全量回归 137 OK，Python 编译检查通过，`node --check Product/web/assets/app.js` 通过。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，数据与设计页变量角色入口无重叠，右侧为属性检查器，整体背景变干净。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

## 2026-05-13 P1-R Clean Workbench Visual Pass

- [x] 参考研究：读取 JupyterLab / Grafana / OpenMetadata 的公开产品文档，提炼为“主工作区 + 属性检查器 + 信息面板/记录，而不是装饰卡片堆叠”。
- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`，定义清洁工作台、变量角色入口不重叠、右侧属性检查器、record/list 替代大卡片。
- [x] TDD：新增 `tests/test_clean_workbench_visual_contract.py`；首次运行 4 失败 1 通过，失败原因是仍存在纸格背景、auto 双列、右侧档案索引过重、缺少 record/list 结构。
- [x] 实现：去掉 archive shell 的纸格噪声和厚重阴影，右侧 `archive-inspector` 调整为 `inspector-rail`，变量角色确认入口改为单列 `research-record-card` + `research-step-list`。
- [x] 实现：修复截图中的重叠根因，`.variable-role-workflow-layout` 不再使用 `minmax(0, 1fr) auto`，长路径使用 `overflow-wrap:anywhere`。
- [x] 验证：目标视觉契约测试 15 OK，全量回归 137 OK，Python 编译检查通过，`node --check Product/web/assets/app.js` 通过。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，数据与设计页变量角色入口无重叠，右侧为属性检查器，整体背景变干净。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

- [x] 中文化 BDD：新增 `docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`，定义用户可见页面文案改为同义中文，API 字段和证据枚举不翻译。
- [x] 中文化 TDD：新增 `tests/test_frontend_chinese_copy.py`，并更新相邻前端契约测试，先锁定一级导航、阶段标题、执行/导出页面中文文案。
- [x] 中文化实现：更新 `Product/web/index.html` 与 `Product/web/assets/app.js`，把核心页面、按钮、状态说明和 workflow 文案切换为中文展示。
- [x] 档案界面 BDD：新增 `docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`，定义研究档案身份、相邻笔记、证据图例、收藏架和交互状态。
- [x] 档案界面 TDD：新增 `tests/test_archive_interface_visual_contract.py`；首次运行 4 条失败，原因是页面缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态标识。
- [x] 实现：在 `Product/web/index.html` 增加 `archive-shell` 和右侧 `archive-inspector`；在 `Product/web/assets/app.js` 增加 `archivePageNotes`、`mountArchiveInspector()`、`updateArchiveInspector()`；在 `Product/web/assets/styles.css` 增加纸张网格、档案条目、相邻笔记、证据 ledger、hover/focus/loading/empty/error 状态。
- [x] 验证：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 5 tests OK；`python3 -m unittest discover -s tests -v` 132 tests OK，skipped=1；`node --check Product/web/assets/app.js` 通过；Python 编译检查通过；Safari 可视化验收 `http://127.0.0.1:8765/?v=20260513-archive1` 通过。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

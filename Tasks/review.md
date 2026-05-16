# Review

## 验证记录

- 2026-05-12：`python3 -m unittest discover -s tests -v`，48 tests OK，skipped=1。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend -v`，先失败，原因是 P0 前端 DOM/JS/CSS 还没有真实 observability 元素和函数。
- 2026-05-12：补第 7 条历史 run 边界后，`python3 -m unittest tests.test_observable_execution_frontend -v` 先失败，原因是缺少 `handleMissingRunObservability` 和 404 恢复态。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend -v`，7 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution -v`，2 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_agent_cluster_frontend_interactions -v`，10 tests OK。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：`python3 -m unittest discover -s tests -v`，55 tests OK，skipped=1，最终一次耗时 4.065s。
- 2026-05-12：本地服务 `python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8877` 启动成功；浏览器打开 `http://127.0.0.1:8877`。
- 2026-05-12：浏览器点击“实证执行”后，真实 run `run_3ffe1e6c1f53` 渲染 Step Board、Event Stream、Human-in-the-loop、Artifacts / Evidence。
- 2026-05-12：浏览器切换到历史 run `run_c617f095b232`，页面显示“缺少可观察执行轨迹”和“点击启动试运行”的恢复提示。
- 2026-05-12：浏览器量测 Step 卡片宽度 368.8px，小于 387.8px 容器宽度，修复长 metadata 撑破面板的问题。
- 2026-05-12：API 验证 `GET /api/v1/projects/proj_undergraduate_thesis/runs/run_3ffe1e6c1f53/observability` 返回 `_meta.evidence_level=local_execution`、7 个 steps、24 个 events、2 个 gates。
- 2026-05-12：新增 P1 gate resolve 测试后先失败，`POST /api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve` 返回 404，确认失败原因是路由/服务未实现。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution.ObservableExecutionTests.test_bdd_3_gate_resolve_api_updates_gate_event_and_manifest -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution -v`，3 tests OK。
- 2026-05-12：最终回归 `python3 -m unittest discover -s tests -v`，56 tests OK，skipped=1，耗时 5.193s。
- 2026-05-12：新增 P1-A 前端行为 5-8 后，`python3 -m unittest tests.test_observable_execution_frontend -v` 先失败 4 条，原因是前端缺少 gate resolve 控件、API client、刷新和 resolved 展示。
- 2026-05-12：实现 P1-A 前端后，`python3 -m unittest tests.test_observable_execution_frontend -v`，10 tests OK。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：最终回归 `python3 -m unittest discover -s tests -v`，59 tests OK，skipped=1，耗时 5.570s。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1a`，实证执行页显示 confirm/reject/adjust 和 note。
- 2026-05-12：浏览器填写 `gate_dataset_fields` 处理说明并点击确认后，页面显示 `action=confirm`、note、resolved_at；事件流包含 resolved 事件；console errors=0。
- 2026-05-12：P1-B 新增/扩展数据入口测试后先失败，失败原因包括 datasets API 仍为 `mock`、run response 缺少 `dataset_source`、前端缺少数据集启动按钮和 `dataset_path` payload。
- 2026-05-12：`python3 -m unittest tests.test_api_contract_v2.ApiContractV2Tests.test_bdd_3_datasets_list_local_files_as_local_file_evidence -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_product_v1_local.ProductV1LocalTests.test_run_endpoint_records_selected_dataset_source -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_product_v1_local.ProductV1LocalTests.test_run_endpoint_rejects_invalid_dataset_source -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_dataset_frontend -v`，4 tests OK。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m py_compile Product/backend/overview_service.py Product/backend/project_service.py Product/app.py Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py`，通过。
- 2026-05-12：`python3 -m unittest discover -s tests -v`，65 tests OK，skipped=1，耗时 11.121s。
- 2026-05-12：API 验证 `GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `analysis_sample.csv`，`row_count=12`、`column_count=4`、`role=configured_final_dataset`、`evidence_level=local_file`。
- 2026-05-12：API 验证 `POST /api/v1/projects/proj_undergraduate_thesis/runs` 携带 `dataset_path=Data/Final/analysis_sample.csv` 后生成 `run_b87d95f7d053`，response 与 manifest 都包含 `dataset_source`。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1b3`，数据页显示真实本地数据文件；点击“用此数据启动试运行”生成 `run_fc725d15b3c0`，manifest 包含 `dataset_source.evidence_level=local_file`；console errors/warnings=0。
- 2026-05-12：P1-C 新增 observability 顶层 dataset_source 测试后先失败，原因是 API 只在 `manifest.dataset_source` 中返回；新增前端数据源面板测试后先失败，原因是 HTML/JS/CSS 缺少 `observable-dataset-source`。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution.ObservableExecutionTests.test_bdd_3_observability_exposes_dataset_source_as_run_evidence -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend.ObservableExecutionFrontendTests.test_bdd_11_execution_page_shows_run_dataset_source -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution -v`，4 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend -v`，11 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_product_v1_local.ProductV1LocalTests.test_run_endpoint_records_selected_dataset_source -v`，通过。
- 2026-05-12：`python3 -m py_compile Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m unittest discover -s tests -v`，67 tests OK，skipped=1，耗时 36.309s。
- 2026-05-12：API 验证 `GET /api/v1/projects/proj_undergraduate_thesis/runs/run_641c9770a1a8/observability` 返回顶层 `dataset_source` 和 `manifest.dataset_source`，均包含 `path=Data/Final/analysis_sample.csv`、`evidence_level=local_file`、`role=configured_final_dataset`、`row_count=12`、`column_count=4`。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1c`，从数据页启动 `run_641c9770a1a8`，执行页 Run 数据源面板显示 `analysis_sample.csv`、相对路径、本地文件、12 行 4 列、csv、configured_final_dataset；console errors/warnings=0。
- 2026-05-12：P1-D 新增 variable_roles API 测试后先失败，原因是 observability 顶层缺少 `variable_roles`；新增前端测试后先失败，原因是缺少 `observable-variable-roles`。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution.ObservableExecutionTests.test_bdd_5_observability_exposes_variable_roles_and_confirmation_gate -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend.ObservableExecutionFrontendTests.test_bdd_12_execution_page_shows_variable_roles_confirmation -v`，通过。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution -v`，5 tests OK。
- 2026-05-12：`python3 -m unittest tests.test_observable_execution_frontend -v`，12 tests OK。
- 2026-05-12：`python3 -m py_compile Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：`python3 -m unittest discover -s tests -v`，69 tests OK，skipped=1，耗时 8.408s。
- 2026-05-12：API 验证 `GET /api/v1/projects/proj_undergraduate_thesis/runs/run_641c9770a1a8/observability` 返回 `variable_roles.evidence_level=local_execution`、`confirmation_gate_id=gate_dataset_fields`、`confirmation_status=open`。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1d`，变量角色确认面板显示 `outcome=wage`、`treatment=trained`、`controls=edu, experience`、`instruments=未识别`；console errors/warnings=0。
- 2026-05-12：P1-UI 新增紧凑控制台行为后，`python3 -m unittest tests.test_observable_execution_frontend.ObservableExecutionFrontendTests.test_bdd_13_execution_page_uses_dense_console_layout -v` 先失败，原因是缺少 `execution-control-panel`。
- 2026-05-12：实现 P1-UI 后，`python3 -m unittest tests.test_observable_execution_frontend -v`，13 tests OK。
- 2026-05-12：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py`，通过。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：最终回归 `python3 -m unittest discover -s tests -v`，70 tests OK，skipped=1，耗时 5.553s。
- 2026-05-12：浏览器打开 `http://127.0.0.1:8765/?v=20260512-p1ui3`，实证执行页桌面 computed style：system font、panel radius 8px、padding 12px、context grid 两列、overflowCount=0。
- 2026-05-12：移动端 390x844 验收：上下文网格折叠单列、toolbar 为 column、metadata `pre-wrap`、overflowCount=0。
- 2026-05-12：产品重置新增 `tests/test_product_workflow_contract.py` 后先失败：2 条 API 测试因 `KeyError: workflow_contract` 报错，4 条前端测试因缺少 5 个工作区、`renderWorkflowContract`、`data-open-design-action`、`renderExecutionPreflight` 失败。
- 2026-05-12：实现产品重置后，`python3 -m unittest tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend -v`，23 tests OK。
- 2026-05-12：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/app.py`，通过。
- 2026-05-12：`node --check Product/web/assets/app.js`，通过。
- 2026-05-12：最终回归 `python3 -m unittest discover -s tests -v`，76 tests OK，skipped=1，耗时 6.385s。
- 2026-05-12：重启 8765 后浏览器打开 `http://127.0.0.1:8765/?v=20260512-flow2`；Workspace Home 显示 5 个工作区、`confirm_variable_roles` 下一步、9 个 workflow spine 阶段；console errors/warnings=0。
- 2026-05-12：Data & Design 浏览器验收显示 `analysis_sample.csv`、`Data/Final/analysis_sample.csv`、`本地文件`、`12 行 · 4 列 · csv · configured_final_dataset` 和“检查并确认变量角色”，页面文本不再包含“用此数据启动试运行”。
- 2026-05-12：Execution 浏览器验收显示 `can_start_full_run=false`、`variable_roles_unconfirmed`、`design_unconfirmed`、`run_plan_missing`，并保留当前 run evidence；桌面和 390x844 移动端均无横向溢出。
- 2026-05-13：P1-E 新增 `tests/test_variable_role_confirmation.py` 后，`python3 -m unittest tests.test_variable_role_confirmation -v` 首次 5 条失败；失败原因为变量角色 API 404、前端缺少 `variable-role-confirmation-form`、`renderVariableRoleEditor` 与保存 API。
- 2026-05-13：实现 P1-E 后，`python3 -m unittest tests.test_variable_role_confirmation -v`，5 tests OK。
- 2026-05-13：P1-E 目标回归 `python3 -m unittest tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，39 tests OK。
- 2026-05-13：P1-E 编译/语法 `python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 2026-05-13：P1-E 最终回归 `python3 -m unittest discover -s tests -v`，81 tests OK，skipped=1，耗时 8.594s。
- 2026-05-13：浏览器打开 `http://127.0.0.1:8765/?v=20260513-p1e`；Data & Variables 显示 VariableRoleSet 编辑器，初始 draft 为 `outcome=wage`、`treatment=trained`、`controls=edu, experience`。
- 2026-05-13：浏览器填写 note 并保存后，VariableRoleSet 状态为 `approved · local_file`，meta 为 `Data/Final/analysis_sample.csv · version=1 · evidence_level=local_file`，`state/product/variable_roles.json` 写入真实本地状态。
- 2026-05-13：保存后 Overview API 显示 `workflow_contract.next_action.id=confirm_design_spec`，blockers 只剩 `design_unconfirmed`、`run_plan_missing`；Execution preflight 继续显示 `CAN_START_FULL_RUN=FALSE`，console errors/warnings=0。
- 2026-05-13：交接收尾后复查 `python3 -m unittest tests.test_variable_role_confirmation -v`，5 tests OK；`node --check Product/web/assets/app.js` 通过；`curl http://127.0.0.1:8765/` 确认 CSS/JS 版本为 `20260513-p1e`；`curl /overview` 确认 `confirm_design_spec` 和 `design_unconfirmed/run_plan_missing`，未出现 `variable_roles_unconfirmed`。
- 2026-05-13：P1-F/P1-G 新增 `tests/test_design_run_plan_state_machine.py` 后，`python3 -m unittest tests.test_design_run_plan_state_machine -v` 首次 7 条失败；失败原因为 DesignSpec/RunPlan API 返回 404，前端缺少 `design-spec-confirmation-form`、`run-plan-confirmation-form`、`renderDesignSpecEditor`、`renderRunPlanEditor` 和保存 API。
- 2026-05-13：实现 P1-F/P1-G 后，`python3 -m unittest tests.test_design_run_plan_state_machine -v`，7 tests OK。
- 2026-05-13：P1-F/P1-G 目标回归 `python3 -m unittest tests.test_design_run_plan_state_machine tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，46 tests OK。
- 2026-05-13：P1-F/P1-G 编译/语法 `node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/design_spec_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过。
- 2026-05-13：浏览器打开 `http://127.0.0.1:8765/?v=20260513-p1fg`；初始 `workflow_contract.next_action.id=confirm_design_spec`，blockers 为 `design_unconfirmed/run_plan_missing`，页面存在 DesignSpec 与 RunPlan 表单。
- 2026-05-13：浏览器保存 DesignSpec 后，页面状态为 `approved · local_file`，Overview API 显示 `workflow_contract.next_action.id=confirm_run_plan`，blockers 只剩 `run_plan_missing`，`state/product/design_spec.json` 写入真实本地状态。
- 2026-05-13：浏览器保存 RunPlan 后，页面状态为 `approved · local_file`，Overview API 显示 `workflow_contract.next_action.id=start_full_run`、blockers 为空、`can_start_full_run=true`，`state/product/run_plan.json` 写入真实本地状态；console errors/warnings=0，Execution 页面无横向溢出。
- 2026-05-13：P1-F/P1-G 最终回归 `python3 -m unittest discover -s tests -v`，88 tests OK，skipped=1，耗时 83.833s。
- 2026-05-13：P1-H 新增 `tests/test_full_run_from_run_plan.py` 后，`python3 -m unittest tests.test_full_run_from_run_plan -v` 首次 3 条失败；失败原因为 `POST /api/v1/projects/{project_id}/runs/full` 返回 405，前端缺少 `observable-run-full-button`、`v2api.runs.startFull`、`createFullRunFromPlan`。
- 2026-05-13：实现 P1-H 后，`python3 -m unittest tests.test_full_run_from_run_plan -v`，3 tests OK。
- 2026-05-13：P1-H 目标回归 `python3 -m unittest tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_v1_local tests.test_observable_execution tests.test_observable_execution_frontend tests.test_product_workflow_contract -v`，39 tests OK。
- 2026-05-13：P1-H 编译/语法 `node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/project_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py Product/backend/observability_service.py` 通过。
- 2026-05-13：重启 8765 后浏览器打开 `http://127.0.0.1:8765/?v=20260513-p1h`；Overview API 显示 `next_action=start_full_run`、blockers 为空、`can_start_full_run=true`；Execution 页面完整执行按钮存在且未禁用。
- 2026-05-13：浏览器点击“启动完整实证执行”后生成 `run_c424d6a11af7`；run store 显示 `mode=full-run`、`status=succeeded`、`execution_evidence_level=local_execution`、`plan_binding.run_plan_version=1`、`research_engine.embedded=false`。
- 2026-05-13：`GET /api/v1/projects/proj_undergraduate_thesis/runs/run_c424d6a11af7/observability` 返回 `_meta.evidence_level=local_execution`，manifest 包含 `run_plan_binding.evidence_level=local_file` 与 `research_engine.integration_mode=callable_external`。
- 2026-05-13：浏览器 console errors/warnings=0；run selector 选中 `run_c424d6a11af7 · succeeded · full-run`。
- 2026-05-13：P1-H 最终回归 `python3 -m unittest discover -s tests -v`，91 tests OK，skipped=1，耗时 6.591s。

## 风险

- `run_3ffe1e6c1f53` 的 `gate_dataset_fields` 已在浏览器验收中被处理；继续验收开放 gate 时使用 `gate_research_question` 或重新启动试运行。
- `Product/serve_product.py` 直接执行会因为顶层包导入路径失败，后续应单独补测试修复。
- Playwright 选择下拉时一次 `browser_select_option` 权限审核超时，改用页面内 JS 派发 change 事件完成验收。
- 当前数据入口只支持项目内相对路径，不支持 multipart 上传或任意外部路径。
- VariableRoleSet 已可结构化编辑并持久化，但 `state/product/variable_roles.json` 当前是本地 runtime artifact，未决定是否纳入版本控制或迁移为 fixture。
- DesignSpec/RunPlan 已可结构化确认并持久化，但 `state/product/design_spec.json`、`state/product/run_plan.json` 当前是本地 runtime artifacts，未决定是否纳入版本控制或迁移为 fixture。
- P1-UI 只修正了实证执行页，没有重做数据页、研究设计页和 Agent 控制台的视觉一致性。
- `workflow_contract` 已读取真实已确认 VariableRoleSet、DesignSpec、RunPlan 状态；`start_full_run` 已接入非开发式完整执行按钮与后端路径。
- full run 仍复用当前 `Program/run_paper.py` 本地 pipeline；Feynman 目前只作为 callable external research engine metadata 和后续 provider 设计方向，并未实际调用 Feynman CLI。

## 未完成项

- P1-I 已完成：Results & Draft 能从 `run_c424d6a11af7` 生成最小 FindingCard 和 DraftSection evidence binding。
- multipart 上传或外部文件导入。
- `Product/serve_product.py` 直接执行入口修复。
- 继续把 CoPaper/StatsPAI 的步骤方法论落到“用户调整变量角色 -> 系统重跑识别/建模 -> 产物更新”的闭环。
- Findings / Manuscript / Artifacts / Agents 还未展开为完整 8 板块工作台；现在 Results & Draft 已有最小 evidence binding，下一步应做 claim review / accept-for-writing 状态。

## 2026-05-13 P1-I Results & Draft Evidence Binding

- 失败测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v` 首次有效失败为 API 404 和前端缺少 `results-findings-list`、`draft-evidence-sections`、`v2api.resultsDraft.get`、`renderResultsDraftEvidence`。
- 目标测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v`，4 tests OK。
- 目标回归：`python3 -m unittest tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，31 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/results-draft` 返回 `latest_run_id=run_c424d6a11af7`，FindingCard 绑定 `Results/json/analysis_result.json`，DraftSection 绑定 `Manuscripts/generated/paper_draft.md` 和 `claim_evidence_level=local_execution`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1i` 的 Results & Draft 页面显示 `trained effect on wage`、`run_id=run_c424d6a11af7`、`run_plan_version=1`、`Results/json/analysis_result.json`；草稿章节显示 `本地文件` 和 `真实执行`；overflowCount=0，console errors/warnings=0。
- 全量回归：`python3 -m unittest discover -s tests -v`，95 tests OK，skipped=1，耗时 6.788s。

## 2026-05-13 P1-J Claim Review / Accept-for-writing

- 失败测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v` 首次 P1-J 失败为 `KeyError: review_status`、review API 404、前端缺少 `reviewFinding` / `data-finding-review-action`。
- 目标测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v`，8 tests OK。
- 目标回归：`python3 -m unittest tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，35 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- API 验收：`PUT /api/v1/projects/proj_undergraduate_thesis/results-draft/findings/finding_trained_effect/review` 返回 `review_status=approved`、`evidence_level=local_file`、`run_id=run_c424d6a11af7`、`artifact_path=Results/json/analysis_result.json`、`can_write_to_draft=true`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1j` 的 Results & Draft 页面显示 `review_status=approved`、`accept-for-writing=yes`、approve/needs_revision/reject 三个操作、审阅备注和 `review evidence: 本地文件`；overflowCount=0，console errors/warnings=0。
- 全量回归：`python3 -m unittest discover -s tests -v`，99 tests OK，skipped=1，耗时 13.177s。

## 2026-05-13 P1-K Manuscript Consumption

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 首次 5 条失败；API 测试因 `/api/v1/projects/{project_id}/manuscript-candidates` 返回 404，前端测试因缺少 `manuscript-candidates-list`、`v2api.manuscriptCandidates.get`、`renderManuscriptCandidates`、provenance 渲染标识失败。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，5 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，40 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，104 tests OK，skipped=1，耗时 5.858s。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates` 返回 `latest_run_id=run_c424d6a11af7`，1 个 candidate `manuscript_candidate_finding_trained_effect_results`，正文包含 `trained`、`wage`、`1.8505`、`0.0573`、`9.18e-10`、`12`，并绑定 `source_draft`、`result_artifact`、`review_decision` provenance。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1k` 的 Results & Draft 页面显示 1 个 Manuscript candidate；页面不存在 `overwrite-paper-draft` 写回按钮；candidate 卡片横向溢出数量为 0；console errors/warnings=0。

## 2026-05-13 P1-L Manuscript Candidate Review

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 扩展后首次 5 条失败；失败原因为 candidate 缺少 `review_status`，candidate review API 返回 404，非法 action 未结构化拒绝，前端缺少 `can-promote`、`candidate_review`、`reviewManuscriptCandidate` 和 `data-candidate-review-action`。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，10 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，45 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，109 tests OK，skipped=1，耗时 7.453s。
- API 验收：`PUT /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates/manuscript_candidate_finding_trained_effect_results/review` 返回 `review_status=approved`、`evidence_level=local_file`、`can_promote=true`；再次 `GET /manuscript-candidates` 返回 `candidate_review.path=state/product/manuscript_candidate_reviews.json`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1l` 的 Results & Draft 页面显示 `review_status=approved`、`can-promote=yes`、candidate review provenance、approve/needs_revision/reject 操作；页面无 `overwrite-paper-draft`，overflowCount=0，console errors/warnings=0。

## 风险更新

- P1-J 已完成：FindingCard 有持久化 review 状态，approved 才允许后续写入正文。
- P1-K 已完成：Manuscript candidates 只消费 `can_write_to_draft=true` 的 approved finding，仍不直接覆盖源草稿。
- P1-L 已完成：Manuscript candidate 有独立审阅/确认状态，approved 后 `can_promote=true`。
- 下一步 P1-M 应设计 promote/write-back/export preflight，仍不要直接覆盖源草稿。
- `state/product/finding_reviews.json` 是浏览器/API 验收创建的本地状态，后续提交前需决定保留、迁移 fixture，或作为 runtime artifact。
- `state/product/manuscript_candidate_reviews.json` 是浏览器/API 验收创建的本地状态，后续提交前需决定保留、迁移 fixture，或作为 runtime artifact。

## 2026-05-13 P1-M Manuscript Promote Preflight

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 扩展后首次失败；失败原因为 `/api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/promote` 返回 404，前端缺少 `promotion_status`、`ready_for_export`、`can_write_back`、`promoteManuscriptCandidate` 和 `data-candidate-promote-action`。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，15 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，50 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，114 tests OK，skipped=1，耗时 8.459s。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates/manuscript_candidate_finding_trained_effect_results/promote` 返回 `promotion_status=ready_for_export`、`evidence_level=local_file`、`can_export=true`、`can_write_back=false`，并写入 `state/product/manuscript_candidate_promotions.json`。
- 浏览器验收：`http://127.0.0.1:8765/?v=20260513-p1m` 的 Results & Draft 页面显示 `ready_for_export`、`can_write_back=no`、`promotion_state`、`promotion evidence` 和“进入导出前检查”按钮；页面无 `overwrite-paper-draft`，overflowCount=0，console errors/warnings=0。

## 风险更新

- P1-M 已完成：approved Manuscript candidate 可以进入 `ready_for_export`，但仍不会直接覆盖 `paper_draft.md`。
- P1-N 已完成：`ready_for_export` candidate 可以生成 write-back preview 和 export package manifest，但仍不会直接覆盖 `paper_draft.md`。
- 下一步 P1-O 应把 export preflight 接入 Review & Export 页面，设计最终导出包浏览、docx 预检或显式写回审批。
- `state/product/manuscript_candidate_promotions.json` 是浏览器/API 验收创建的本地状态，后续提交前需决定保留、迁移 fixture，或作为 runtime artifact。
- `state/product/export_package_manifest.json` 和 `Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md` 是 API 验收创建的本地状态，后续提交前需决定保留、迁移 fixture，或作为 runtime artifact。

## 2026-05-13 P1-N Export Preflight Preview

- 失败测试：`python3 -m unittest tests.test_manuscript_consumption -v` 扩展后首次失败；失败原因为 `/api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/export-preflight` 返回 404，前端缺少 `export_status`、`preview_ready`、`writeback_preview_path`、`exportPreflightManuscriptCandidate`、`data-candidate-export-preflight-action` 和 `export_package`。
- 目标测试：`python3 -m unittest tests.test_manuscript_consumption -v`，19 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，54 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/manuscript_candidate_service.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，118 tests OK，skipped=1，耗时 8.764s。
- 收尾复查：更新 `Tasks/` 状态文件后再次运行 `python3 -m unittest discover -s tests -v`，118 tests OK，skipped=1，耗时 6.338s。
- API 验收：`POST /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates/manuscript_candidate_finding_trained_effect_results/export-preflight` 返回 `export_status=preview_ready`、`preview_path=Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md`、`manifest_path=state/product/export_package_manifest.json`、`can_write_back=false`。
- 产物验收：preview 文件保留原 draft 内容并追加 `writeback_preview: do not overwrite source draft automatically` 标记、candidate/run/run_plan 信息和 proposed results paragraph；manifest 记录 `source_draft_path`、`writeback_preview_path`、`candidate_promotion_path`、`result_artifact_path`、`evidence_level=local_file`、`can_write_back=false`。
- 前端验收：`curl http://127.0.0.1:8765/` 确认 CSS/JS 版本为 `20260513-p1n`；JS 静态检查确认 `export_status`、`preview_ready`、`writeback_preview_path`、`v2api.manuscriptCandidates.exportPreflightCandidate`、`exportPreflightManuscriptCandidate`、`data-candidate-export-preflight-action`、`export_package` 均存在，且没有 `overwrite-paper-draft`。Playwright 最终浏览器传输中断，未完成 P1-N 的截图级复验。

## 2026-05-13 P1-O Review & Export Package Workbench

- 失败测试：`python3 -m unittest tests.test_review_export_package -v` 首次 4 条失败；失败原因为 `/api/v1/projects/{project_id}/export-package` 返回 404，前端缺少 `export-package-workbench`、`export-evaluator-checks`、`frontier-iteration-log`、`data-open-results-draft`。
- 目标测试：`python3 -m unittest tests.test_review_export_package -v`，4 tests OK。
- 目标回归：`python3 -m unittest tests.test_manuscript_consumption tests.test_results_draft_evidence_binding tests.test_review_export_package -v`，31 tests OK。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/backend/manuscript_candidate_service.py Product/app.py` 通过。
- 全量回归：`python3 -m unittest discover -s tests -v`，122 tests OK，skipped=1，耗时 9.485s。
- 全量编译：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/manuscript_candidate_service.py Product/app.py` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/export-package` 返回 `_meta.evidence_level=local_file`、`export_status=preview_ready`、`evaluator_status=passed`、`can_write_back=false`、5 个 passed evaluator checks 和 Frontier-Eng iteration log。
- Chrome 可视化验收：`http://127.0.0.1:8765/?v=20260513-p1o` 点击 `Review & Export` 后显示“导出包验收台”、导出包路径、evaluator checks、Frontier-Eng iteration log；点击“回到 Results & Draft 查看候选来源”可返回候选来源页。截图：`/tmp/empirical-workbench-review-export-p1o.png`。

## 风险更新

- P1-O 已完成：Review & Export 现在能作为可视化 evaluator checkpoint 展示导出包是否可验收。
- 下一步 P1-P 应单独设计显式写回审批或 docx 导出预检；仍不能默认覆盖 `Manuscripts/generated/paper_draft.md`。
- `state/product/export_package_manifest.json`、`Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md` 和 `/tmp/empirical-workbench-review-export-p1o.png` 是本地验收产物；后续提交前需要决定哪些进入 fixture、哪些保留为 runtime artifact。
- 本轮 Browser 插件连接不稳定，最终使用 Chrome + Computer Use 完成可视化验收。

## 2026-05-13 P1-R Clean Workbench Visual Pass

- 参考来源：JupyterLab 的主工作区/侧栏/属性检查器、Grafana 的 dashboard panel、OpenMetadata 的数据质量/可观测性视角。
- 失败测试：`python3 -m unittest tests.test_clean_workbench_visual_contract -v` 首次 4 失败 1 通过；失败原因为仍存在纸格背景、变量入口 auto 双列、右侧档案栏过重、缺少 record/list 结构。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_archive_interface_visual_contract tests.test_frontend_chinese_copy -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，137 tests OK，skipped=1，耗时 8.495s。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 可视化验收：Browser via Node REPL 超时、Playwright MCP `Transport closed`；已使用 Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，点击“数据与设计”后确认变量角色确认入口无重叠，右侧为属性检查器。

## 风险更新

- P1-R 已解决截图中的重叠和视觉噪声问题，但它是第一轮 clean pass，不代表全部页面已经达到最终产品质感。
- Browser/Playwright 自动化链路仍需后续修复；当前视觉验收采用 Safari + Computer Use fallback。
- 后续不要再把“档案气质”理解成纸格背景和卡片堆叠，应继续围绕研究对象、证据等级、属性检查器、审计时间线迭代。

## 2026-05-13 P1-R Clean Workbench Visual Pass

- 参考来源：JupyterLab 的主工作区/侧栏/属性检查器、Grafana 的 dashboard panel、OpenMetadata 的数据质量/可观测性视角。
- 失败测试：`python3 -m unittest tests.test_clean_workbench_visual_contract -v` 首次 4 失败 1 通过；失败原因为仍存在纸格背景、变量入口 auto 双列、右侧档案栏过重、缺少 record/list 结构。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_archive_interface_visual_contract tests.test_frontend_chinese_copy -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，137 tests OK，skipped=1，耗时 8.495s。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 可视化验收：Browser via Node REPL 超时、Playwright MCP `Transport closed`；已使用 Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，点击“数据与设计”后确认变量角色确认入口无重叠，右侧为属性检查器。

## 风险更新

- P1-R 已解决截图中的重叠和视觉噪声问题，但它是第一轮 clean pass，不代表全部页面已经达到最终产品质感。
- Browser/Playwright 自动化链路仍需后续修复；当前视觉验收采用 Safari + Computer Use fallback。
- 后续不要再把“档案气质”理解成纸格背景和卡片堆叠，应继续围绕研究对象、证据等级、属性检查器、审计时间线迭代。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

- 失败测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 首次 4 条失败；失败原因是页面缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态标识。
- 目标测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v`，5 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，132 tests OK，skipped=1，耗时 11.797s。
- 静态检查：`node --check Product/web/assets/app.js` 通过。
- 编译检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过。
- 静态服务验收：`curl --max-time 5 'http://127.0.0.1:8765/?v=20260513-archive1'` 返回新版 HTML 和 `20260513-archive1` asset version。
- 可视化验收：Safari 打开 `http://127.0.0.1:8765/?v=20260513-archive1`，页面显示 `个人研究档案`、`档案索引`、`相邻笔记`、`证据图例`、`收藏架`；点击右侧 `数据与设计` 后切换到变量角色集编辑器，右侧当前档案说明同步为 `数据与设计`。

## 风险更新

- P1-Q 已完成：页面不再以英文内部对象和普通 SaaS 卡片为主要气质，已经有中文研究档案身份、右侧相邻笔记和证据图例。
- 当前右侧 `archive-inspector` 仍是第一版静态档案索引，不是真正 backlinks / graph。
- 当前收藏架条目未绑定真实 artifacts/export package API，后续应把导出包、run manifest、paper draft 等产物接成可浏览 shelf。
- Browser/IAB 和 Playwright 本轮连接异常；已通过 Safari + Computer Use 做可视化 fallback。

## 2026-05-13 P2-A Dataset Quality Profile

- 目标：把 CoPaper/StatsPAI 式流程里的“数据引入与质量理解”做成可见、可验证的研究对象，避免在变量角色、DesignSpec 或 RunPlan 阶段对不透明数据直接选方法。
- BDD：新增 `docs/architecture-v2/codex-phase-p2-data-quality-profile-bdd.md`，覆盖 datasets API 返回质量画像、缺失值进入 `needs_review`、干净 CSV 进入 `ready`、未解析格式进入 `not_profiled`、前端展示质量画像。
- 失败测试：`python3 -m unittest tests.test_dataset_quality_profile -v` 首次有效失败为 `KeyError: 'quality_profile'` 和前端缺少 `data-quality-profile-panel`，说明目标行为尚未实现。
- 目标测试：`python3 -m unittest tests.test_frontend_chinese_copy tests.test_dataset_quality_profile -v`，11 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，148 tests OK，skipped=1，耗时 6.502s。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `analysis_sample.csv`，`quality_profile.evidence_level=local_file`、`readiness_status=ready`、`row_count=12`、`column_count=4`、`missing_rate=0`、`numeric_column_count=4`。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2a`，进入“数据与设计”后可见 `analysis_sample.csv`、`数据质量画像`、样本 12、缺失率 0%、字段画像和中文操作标签；布局为纵向 clean workbench，不再出现两列挤压。

## 风险更新

- P2-A 已解决“方法选择前看不见数据质量”的问题，但当前质量画像只做轻量 CSV schema、缺失值和类型推断；还不是完整 StatsPAI 描述统计、平衡性检查或因果方法诊断。
- `.dta`、`.xlsx`、`.parquet` 等格式当前保留 `evidence_level=local_file` 并标记 `readiness_status=not_profiled`，后续需要接入真实解析器或 StatsPAI/Stata 侧 profiling。
- Playwright MCP 本轮仍出现 `Transport closed`；自动化视觉链路未修复前，继续使用 Safari + Computer Use、API 和静态资源检查组合验收。

## 2026-05-13 P1-P Writeback Approval + DOCX Preflight

- 失败测试：`python3 -m unittest tests.test_review_export_package -v` 首次出现 4 failures、1 error；失败原因是导出包缺少 `writeback_approval`，两个新 POST API 返回 404，前端缺少 `review-export-evidence-bench`、`writeback-approval-panel`、`docx-preflight-panel` 和 `export-evidence-table`。
- 目标测试：`python3 -m unittest tests.test_review_export_package -v`，9 tests OK。
- 相邻回归：`python3 -m unittest tests.test_review_export_package tests.test_manuscript_consumption tests.test_results_draft_evidence_binding -v`，36 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，142 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/manuscript_candidate_service.py Product/app.py Product/backend/project_service.py Product/backend/results_draft_service.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：旧 8765 服务一开始返回 404；确认是旧 uvicorn 进程后重启服务，`POST /writeback-approval` 返回 200 并写入 `state/product/writeback_approvals.json`。
- 可视化验收：Browser plugin 运行超时且 Playwright MCP `Transport closed`；已用 Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p1p`，进入“审阅与导出”，确认 `导出包验收台`、证据表、写回审批面板和 docx 预检面板可见；点击 `运行 docx 预检` 后显示 `预检通过`、`源草稿存在`、`写回预览存在`、`docx 导出命令已声明`、`docx 目标路径已声明`。

## 风险更新

- P1-P 已完成：Review & Export 现在可以承接用户显式审批，并把 docx 导出前条件写成可追溯本地状态。
- 本阶段没有真正生成 docx，也没有覆盖 `Manuscripts/generated/paper_draft.md`；这是有意保留的安全边界。
- 旧本地服务进程可能继续缓存旧路由；如果页面按钮返回 404，先重启 `python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8765`。
- Browser/Playwright 自动化链路仍需后续修复；当前验收证据来自 Safari + Computer Use 和 API/tests。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

- 失败测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 首次 4 条失败；失败原因是页面缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态标识。
- 目标测试：`python3 -m unittest tests.test_archive_interface_visual_contract -v`，5 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，132 tests OK，skipped=1，耗时 11.797s。
- 静态检查：`node --check Product/web/assets/app.js` 通过。
- 编译检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过。
- 静态服务验收：`curl --max-time 5 'http://127.0.0.1:8765/?v=20260513-archive1'` 返回新版 HTML 和 `20260513-archive1` asset version。
- 可视化验收：Safari 打开 `http://127.0.0.1:8765/?v=20260513-archive1`，页面显示 `个人研究档案`、`档案索引`、`相邻笔记`、`证据图例`、`收藏架`；点击右侧 `数据与设计` 后切换到变量角色集编辑器，右侧当前档案说明同步为 `数据与设计`。

## 风险更新

- P1-Q 已完成：页面不再以英文内部对象和普通 SaaS 卡片为主要气质，已经有中文研究档案身份、右侧相邻笔记和证据图例。
- 当前右侧 `archive-inspector` 仍是第一版静态档案索引，不是真正 backlinks / graph。
- 当前收藏架条目未绑定真实 artifacts/export package API，后续应把导出包、run manifest、paper draft 等产物接成可浏览 shelf。
- Browser/IAB 和 Playwright 本轮连接异常；已通过 Safari + Computer Use 做可视化 fallback。
## 2026-05-13 P2-B Method Skill Catalog

- 失败测试：`python3 -m unittest tests.test_method_skill_catalog -v` 首次失败，主要失败为 `method_catalog` 缺失、RunPlan task 缺少 `method_id`、前端缺少 `method-skill-catalog-panel`。
- 目标测试：`python3 -m unittest tests.test_method_skill_catalog tests.test_clean_workbench_visual_contract -v`，9 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，152 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/design_spec_service.py Product/app.py Product/backend/project_service.py Product/backend/overview_service.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/run-plan` 返回 `method_catalog`，包含 OLS/DID/IV/RDD/PSM/DML；DID/IV/RDD 分别暴露缺面板时间、工具变量、断点运行变量。
- 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2b-clean`，研究设计细节页展示纵向方法技能集证据清单，无双列卡片挤压。

## 风险更新

- P2-B 已完成方法准入目录，但还不是 CoPaper/StatsPAI 的真实方法执行器。
- 当前 PSM/DML 的 ready 判断较粗，只证明有 outcome/treatment/controls，不证明估计策略充分。
- 下一步 P2-C 应优先把 OLS baseline 跑成 `local_execution` 证据，再逐步扩展 DID/IV/RDD/PSM/DML。
- Playwright MCP 仍不稳定；可视化验收当前以 Safari + Computer Use 为准。

## 2026-05-13 P2-C OLS Execution Adapter

- 目标：把 P2-B 的 OLS ready 方法从 `local_file` 级准入判断推进到 `local_execution` 级本地方法执行结果。
- BDD：新增 `docs/architecture-v2/codex-phase-p2-ols-execution-adapter-bdd.md`，覆盖 approved OLS 执行、RunPlan/数据/公式绑定、manifest 记录、unsupported method 拒绝、不可估数据结构化失败。
- 失败测试：`python3 -m unittest tests.test_ols_execution_adapter -v` 首次有效失败为缺少 `Results/json/method_execution_result.json`、`run.method_execution` 和 manifest `method_execution`；随后发现测试 fixture 共线并改为可估样本。
- 目标测试：`python3 -m unittest tests.test_ols_execution_adapter -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_ols_execution_adapter tests.test_full_run_from_run_plan tests.test_method_skill_catalog tests.test_results_draft_evidence_binding -v`，20 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，157 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/backend/design_spec_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- API 验收：重启 8765 后，`POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_4c62f1721afb`，输出 `status=succeeded`、`plan_binding.tasks[0].method_id=ols`、`method_execution.evidence_level=local_execution`、`treatment_coefficient=1.8505076803`。
- 可视化验收：Playwright MCP 仍 `Transport closed`；使用 Safari + Computer Use 验证本地页面可正常加载，研究设计细节页仍显示方法技能集。P2-C 的结果展示尚未进入页面。

## 风险更新

- P2-C 已完成最小本地 OLS 执行证据，但它不是完整 StatsPAI/Stata 引擎；当前没有稳健标准误、p 值、固定效应、聚类或模型诊断。
- `Results & Draft` 仍主要读取 `Results/json/analysis_result.json`；P2-D 应把 `method_execution_result.json` 接入 Execution / Findings。
- DID/IV/RDD/PSM/DML 仍不能执行；后续每个方法都需要独立 BDD/TDD 和真实产物。

## 2026-05-13 P2-D Method Execution Evidence UI

### 行为覆盖

- [x] Observability API 暴露顶层 `method_execution`，证据等级为 `local_execution`。
- [x] “实证执行”页面显示方法执行证据，包含 adapter、artifact、公式、样本量、处理变量和系数。
- [x] 缺少方法执行产物时，页面显示可恢复空状态，不伪造执行证据。
- [x] Results & Draft API 把方法执行证据绑定到 FindingCard。
- [x] “结果与草稿”页面的结果论断卡显示方法证据来源。

### 测试覆盖

- 测试文件：`tests/test_observable_execution.py`、`tests/test_observable_execution_frontend.py`、`tests/test_results_draft_evidence_binding.py`。
- 目标测试：4 OK。
- Results Draft 回归：10 OK。
- 相邻回归：38 OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，161 OK，skipped=1。
- 静态检查：Python 编译、`node --check Product/web/assets/app.js`、`git diff --check` 均通过。

### 手动验收

- API：`/observability` 和 `/results-draft` 都返回 `engine=python_ols_adapter`、`formula=wage ~ trained + edu + experience`、`nobs=12`、`treatment_coefficient=1.8505076803`。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2d-method`，点击“实证执行”可见方法执行证据；点击“结果与草稿”可见 FindingCard 方法证据。

### 剩余风险

- 方法执行结果还没有标准误、p 值、置信区间、稳健或聚类标准误。
- Finding approve 还没有强制依赖 evaluator verdict。
- Playwright MCP 本轮仍为 `Transport closed`，视觉验收使用 Safari + Computer Use fallback。

## 2026-05-13 P2-E OLS Evaluator Evidence

### 行为覆盖

- [x] OLS 方法执行结果包含标准误、t 统计量、p 值、95% 置信区间和残差诊断。
- [x] OLS 方法执行结果包含命名 evaluator checks：样本量、模型矩阵可估、处理变量系数存在、推断诊断可用。
- [x] Results Draft API 把 evaluator 状态、标准误、p 值和置信区间绑定到 FindingCard。
- [x] Results & Draft 页面以中文紧凑摘要展示方法 evaluator 证据。
- [ ] 未覆盖：稳健标准误、聚类标准误、固定效应、DID/IV/RDD/PSM/DML 的方法级 evaluator。

### 测试覆盖

- 目标测试：`python3 -m unittest tests.test_ols_execution_adapter tests.test_results_draft_evidence_binding -v`，19 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，165 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/results_draft_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_a3674e9e78c6`，status=`succeeded`。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/runs/run_a3674e9e78c6/observability` 返回 `p_values.trained=8.83354660202e-133`、`standard_errors.trained=0.0754664205`、`evaluator.status=passed`，四项 evaluator checks 全部 passed。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/results-draft` 返回 `finding.method_evidence.evaluator_status=passed` 和 `confidence_interval.low=1.7025934962/high=1.9984218644`。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2e-eval`，点击“结果与草稿”，可见 `ols · n=12 · β=1.8505 · 标准误=0.0755 · p=8.83e-133 · 95% 置信区间 1.7026 ~ 1.9984 · 评估器通过`。

### 剩余风险

- 当前 p 值使用 `normal_approximation`，不是有限样本 t 分布；已在产物里显式标记 `p_value_method=normal_approximation`。
- 当前 OLS 标准误不是 robust/clustered；下一轮若进入真实论文口径，应先增加稳健/聚类标准误选项和 evaluator 阻断条件。
- 当前真实数据仍主要使用项目内 `Data/Final/analysis_sample.csv` 样例；用户提供的 `/Users/mahaoxuan/Desktop/实证数据库` 已初步确认包含 `CHARLS.csv`、CFPS、CLDS、CGSS 等材料，下一轮应选一个可解析数据源做真实数据接入验收。
- Playwright MCP 本轮仍不稳定；视觉验收继续使用 Safari + Computer Use fallback。

## 2026-05-13 P2-F Real Data Candidate Pool

### 行为覆盖

- [x] datasets API 返回只读 `external_catalog`，不把外部文件混入项目内 `items`。
- [x] 外部 CSV 候选数据返回最多 200 行轻量质量画像，证据等级为 `local_file`。
- [x] DTA 等暂未画像格式仍保留在候选池，并明确 `readiness_status=not_profiled`。
- [x] “数据与设计”页面把真实数据候选池和当前项目数据分开展示。
- [x] 未配置真实数据库时，前端提供空状态，不伪造数据。

### 测试覆盖

- 目标测试：`python3 -m unittest tests.test_external_data_catalog -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，11 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，170 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `external_catalog.exists=true`、`root=/Users/mahaoxuan/Desktop/实证数据库`、`total_count=223`、`items[0].evidence_level=local_file`。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2f-realdata2`，点击“数据与设计”，可见 `真实数据候选池`、`223`、真实根目录、6 张 CFPS 候选卡、`本地文件`、`尚未画像`、`只读`。
- Browser 插件路径：Node REPL 连接 in-app Browser 超时；本轮可视化验收使用 Safari + Computer Use fallback。

### 剩余风险

- 当前仅 CSV 做轻量预览画像；DTA/XLSX/Parquet 只登记文件，不读取变量字典。
- 外部候选数据还不能导入或绑定到当前项目；变量角色、RunPlan 和 OLS 执行仍使用 `Data/Final/analysis_sample.csv`。
- 下一步 P2-G 需要显式导入/绑定预检：记录来源路径、目标路径、复制/链接策略、证据等级、用户动作和失败原因。

## 2026-05-14 P2-G Real Dataset Bind Preflight

### 行为覆盖

- [x] 用户选择真实候选池内文件时，后端生成 `ready_for_review` 导入/绑定预检。
- [x] 预检记录包含源路径、目标建议路径、策略、文件大小、证据等级、manifest 路径和检查项。
- [x] 预检拒绝候选池之外的本地路径，避免绕过 provenance 边界。
- [x] datasets API 返回最新 `external_import_preflight`，前端可回显上一条预检。
- [x] “数据与设计”页面提供候选文件预检按钮和独立预检面板。
- [ ] 未覆盖：真正 apply/import、哈希记录、DTA/XLSX/Parquet 深度变量字典、搜索/过滤候选池。

### 测试覆盖

- 目标测试：`python3 -m unittest tests.test_external_dataset_bind_preflight -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，16 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，175 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `external_catalog.exists=true`、`total_count=223`。
- API：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/external-bind-preflight` 对 CFPS DTA 候选文件返回 `status=ready_for_review`、`evidence_level=local_file`、`target.path=Data/Raw/cfps2010adult_202008.dta`、`will_create_project_file=false`、`will_mutate_source=false`。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2g-bind1`，点击“数据与设计”，点击候选文件“生成导入/绑定预检”，预检面板显示 `待人工确认`、源文件、目标路径、策略、4 项 passed checks 和只读说明。

### 剩余风险

- 当前只是预检，没有真实导入/绑定；用户还不能把 CFPS 文件变成项目内可分析数据。
- 当前没有文件哈希，无法证明预检后文件未变化；P2-H apply/import 应补 SHA256。
- DTA/XLSX/Parquet 变量字典仍未解析；P2-H 或 P2-I 应先做安全读取和字段预览。
- Browser 插件路径仍不稳定；本轮可视化验收使用 Safari + Computer Use fallback。

## 2026-05-14 P2-H Real Dataset Import Apply

### 行为覆盖

- [x] 本地版用户确认后可把 `ready_for_review` 预检复制到项目 `Data/Raw/<filename>`，并记录目标大小和 SHA256。
- [x] 本地版用户可选择“只绑定引用”，不复制大文件，只记录外部路径、大小、SHA256 和 provenance。
- [x] 用户可取消预检，状态变为 `cancelled`，不会创建项目文件。
- [x] 线上/云端 runtime 拒绝本地路径 apply，返回 `cloud_upload_required`。
- [x] “数据与设计”页面显示三类人工动作按钮，并在 apply 后回显结果。
- [ ] 未覆盖：上传到云对象存储、DTA/XLSX/Parquet 字段读取、移动源文件后的失效提示。

### 测试覆盖

- 目标测试：`python3 -m unittest tests.test_external_dataset_import_apply -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，21 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，180 tests OK，skipped=1。
- 静态检查：`python3 -m py_compile Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`POST /api/v1/projects/{project_id}/datasets/external-bind-preflight/{preflight_id}/apply` 支持 `copy_to_project_raw`、`bind_external_reference`、`cancel`。
- API：`runtime_mode=cloud` 返回 409 `cloud_upload_required`，不创建本地项目文件。
- 页面：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2h-import1`，点击“数据与设计”，对 CFPS 预检点击“只绑定引用”，预检面板显示 `已接入`、`已绑定外部引用`、`动作：只绑定引用 · 模式：local` 和 SHA256。
- Browser 插件路径：Node REPL 连接 in-app Browser 超时；本轮可视化验收使用 Safari + Computer Use fallback。

### 剩余风险

- 当前只是“接入数据源”，不是“解析变量字典”；下一步 P2-I 必须先做安全字段画像，再允许变量角色确认消费真实数据。
- 只绑定引用依赖本地文件路径不变；后续画像/执行前必须重新检查文件存在性和 SHA256。
- 云端版本还缺上传、对象存储、隐私/脱敏、远端执行队列和云模型配置。

## 2026-05-14 P2-I Dataset Import Field Profile

### 行为覆盖

- [x] 已复制到项目的 CSV import 可以生成字段画像，字段来自真实文件，证据等级为 `local_file`。
- [x] 只绑定外部引用的 CSV import 可以生成字段画像，但仍保留外部路径依赖和哈希校验。
- [x] DTA/XLSX/Parquet 等暂未接入安全读取器的格式不会伪造字段，而是返回 `blocked/not_profiled`。
- [x] 外部绑定文件哈希变化时拒绝画像，返回 `dataset_import_source_changed`。
- [x] 已取消或未 apply 的 import 不能画像，返回 `dataset_import_not_profileable`。
- [x] 前端显示“生成字段画像”和字段画像面板，并明确不会改写 VariableRoleSet、DesignSpec 或 RunPlan。
- [ ] 未覆盖：DTA 安全变量字典读取、XLSX sheet/字段预览、Parquet schema 读取、云端上传对象画像。

### 测试覆盖

- RED：`python3 -m unittest tests.test_external_dataset_import_profile -v` 首次 6 条失败，失败原因为 profile API 404、前端缺少画像入口和画像面板。
- 目标测试：`python3 -m unittest tests.test_external_dataset_import_profile -v`，6 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_profile tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，27 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，186 tests OK，skipped=1，最终复查耗时 27.137s。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/overview_service.py` 通过；`node --check Product/web/assets/app.js` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/imports/dataset_import_e9d864229be8/profile` 返回 `status=blocked`、`readiness_status=not_profiled`、`fields=[]`、`blocking_reason=dta 暂未接入安全字段读取器。`、`can_feed_variable_roles=false`。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/datasets` 返回 `external_import_profile.status=blocked`、`external_import_profile.readiness_status=not_profiled`、`fields=0`。
- 页面静态资源：`curl http://127.0.0.1:8765/?v=20260514-p2i-profile1` 确认 `dataset-import-profile-panel` 和新版 asset version 已加载。
- 可视化验收：`npx playwright screenshot --wait-for-timeout=3000 'http://127.0.0.1:8765/?v=20260514-p2i-profile1' /tmp/empirical-workbench-p2i-home-loaded.png` 成功生成首页截图。
- 点击级可视化验收：临时使用 `/tmp/empirical-pw/node_modules` 中的 Playwright，打开页面、点击“数据与设计”、点击“生成字段画像”，生成 `/tmp/empirical-workbench-p2i-data-profile.png`；截图中显示 `字段画像 / 变量字典预览`、`dataset_import_id=dataset_import_e9d864229be8 · not_profiled`、`dta 暂未接入安全字段读取器。` 和 `不会改写 VariableRoleSet、DesignSpec 或 RunPlan`。
- Browser 工具限制：Playwright MCP 仍返回 `Transport closed`；Computer Use 对当前 in-app browser URL 返回不允许操作。本轮通过 Playwright CLI fallback 完成截图级验收。

### 剩余风险

- 当前真实 CFPS `.dta` 仍只能进入 `blocked/not_profiled`，还不能查看变量标签和 Stata 类型。
- 线上版还没有上传/云对象入口；本地绑定路径不能直接迁移到线上。
- 字段画像结果还未进入 VariableRoleSet 确认器，下一步必须先做人工确认边界，而不是自动填充研究状态。

## 2026-05-14 P2-J Stata DTA Field Profile

### 行为覆盖

- [x] 有效 DTA import 可以生成 metadata-only 字段画像，返回 `profiled/ready`。
- [x] 字段画像保留 Stata 语义：字段名、变量标签、Stata 类型、display format。
- [x] DTA 画像不读取整张大表，`row_count_source=metadata_only`。
- [x] 损坏或无法解析的 DTA 返回 `blocked/not_profiled`，不伪造字段、不抛 500。
- [x] DTA 字段画像仍不改写 VariableRoleSet、DesignSpec 或 RunPlan。
- [ ] 未覆盖：DTA 值标签 value labels、缺失值统计、抽样预览、真实 Stata do-file 执行、StatsPAI 方法执行。

### 测试覆盖

- RED：`python3 -m unittest tests.test_external_dataset_import_profile -v` 首次 3 条失败，失败原因是有效 DTA 仍 blocked、损坏 DTA 阻塞原因不精确、前端缺少变量标签/Stata 类型。
- 目标测试：`python3 -m unittest tests.test_external_dataset_import_profile -v`，7 tests OK。
- 相邻回归：`python3 -m unittest tests.test_external_dataset_import_profile tests.test_external_dataset_import_apply tests.test_external_dataset_bind_preflight tests.test_external_data_catalog tests.test_dataset_quality_profile -v`，28 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，187 tests OK，skipped=1，耗时 44.366s。
- 静态检查：`node --check Product/web/assets/app.js`、`python3 -m py_compile Product/app.py Product/backend/overview_service.py`、`git diff --check` 均通过。

### API / 可视化验收

- API：`POST /api/v1/projects/proj_undergraduate_thesis/datasets/imports/dataset_import_e9d864229be8/profile` 返回 `status=profiled`、`readiness_status=ready`、`row_count=1279`、`column_count=723`、`row_count_source=metadata_only`、`fields=723`、`can_feed_variable_roles=false`、`blocking_reason=None`。
- API 字段样例：`pid=个人id`、`fid=家户号`、`provcd=省国标码`、`countyid=区县顺序码`、`cid=村居五位码`、`indnum=户内顺序号`。
- 页面：Playwright CLI 打开 `http://127.0.0.1:8765/?v=20260514-p2j-dta1`，点击“数据与设计”，截图 `/tmp/empirical-workbench-p2j-dta-profile.png` 显示 `已画像`、`1279 行 · 723 列`、`变量标签`、`Stata 类型`、`个人id` 和“不改写研究状态”说明。
- Browser 插件限制：Playwright MCP 仍返回 `Transport closed`；本轮继续用 Playwright CLI fallback 完成点击级验收。

### 剩余风险

- 现在只是变量字典级画像，不是实证分析；后续要接 StatsPAI/StatsAPI、StataMCP 或 Python 执行器做严格估计、诊断和稳健性。
- DTA value labels、缺失统计和抽样预览还没读取；当前只证明字段结构和样本规模。
- 字段画像尚未进入人工 VariableRoleSet 候选生成状态机；下一步 P2-K 必须先做人工审阅边界。
- 线上版仍缺上传/云对象抽象，本地 `/Users/...` 绑定不能直接用于云端。

## 2026-05-14 P2-K Rigorous Empirical Execution Contract

### 行为覆盖

- [x] full run 必须声明当前真实执行后端，不能把未调用的 StatsPAI/StataMCP 冒充为执行证据。
- [x] full run 必须列出候选实证后端，并标明可用性、角色和证据等级。
- [x] OLS 方法执行必须记录数据预检：读取行数、可用数值行、丢弃行数、必需字段和自由度检查。
- [x] OLS 方法执行必须记录可复现入口：run_id、公式、RunPlan/DesignSpec 版本、结果文件和源码入口。
- [x] Execution 页面必须把严谨执行契约、数据预检和可复现入口显示给用户。
- [ ] 未覆盖：真实 StatsPAI `sp.*` 调用、Stata do-file/log 执行、robust/cluster 标准误、固定效应、跨后端数值交叉验证。

### 测试覆盖

- RED：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend -v` 首次 3 条新增行为失败，失败原因为缺少 `execution_contract`、`data_preflight` 和前端契约展示。
- 目标测试：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend -v`，24 tests OK。
- 相邻回归：`python3 -m unittest tests.test_ols_execution_adapter tests.test_observable_execution_frontend tests.test_observable_execution tests.test_results_draft_evidence_binding tests.test_product_api_integration -v`，42 tests OK，skipped=1。
- 全量回归：`python3 -m unittest discover -s tests -v`，190 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js`、`python3 -m py_compile Product/app.py Product/backend/project_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py Product/backend/observability_service.py`、`git diff --check` 均通过。

### API / 可视化验收

- API：`POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_5ac7052232c8`，状态 `succeeded`，engine `python_ols_adapter`。
- API：`execution_contract.active_backend=python_ols_adapter`；StatsPAI/StatsAPI 与 StataMCP/Stata 为 candidate backend，其中 StataMCP 检测到本地 Stata 路径。
- API：`data_preflight.rows_read=12`、`usable_numeric_rows=12`、`dropped_rows=0`、`required_fields=["wage","trained","edu","experience"]`。
- API：`reproducibility.result_artifact_path=Results/json/method_execution_result.json`、`source_entrypoint=Product/backend/project_service.py::execute_ols_task`。
- 页面：Playwright CLI 打开 `http://127.0.0.1:8765/?v=20260514-p2k-rigorous4`，进入“实证执行”，确认 `严谨执行契约`、`当前执行后端`、StatsPAI、StataMCP、`数据预检`、`可复现入口` 均可见，`visibleOverflowCount=0`。
- 截图：`/tmp/empirical-workbench-p2k-rigorous-execution.png`。

### 剩余风险

- 当前仍是最小 Python OLS adapter，不是完整 StatsPAI/Stata 统计引擎。
- StatsPAI 和 StataMCP 已作为候选能力展示，但尚未实际运行、产生日志或写出独立结果文件。
- 当前 p 值仍是 normal approximation；严谨论文场景需要 robust/cluster 标准误、固定效应、样本筛选日志和跨后端复核。
- 下一步应先补字段审阅 / VariableRoleSet 候选生成状态机，再把真实 StatsPAI 或 Stata do-file 执行接入为可替换后端。

## 2026-05-14 P2-L Variable Role Candidate Review

### 行为覆盖

- [x] 已完成字段画像的真实 DTA import 可以生成 `VariableRoleCandidate`，证据等级为 `local_file`。
- [x] 候选生成必须写入 `state/product/variable_role_candidates.json`，保留数据源、字段画像 id、候选角色、候选字段表和 review event。
- [x] 候选生成和 review 不能写回正式 `state/product/variable_roles.json`。
- [x] 未画像或未 ready 的 import 不能生成候选，返回 409 `field_profile_required`。
- [x] 非法 review 动作返回 400 `invalid_variable_role_candidate_action`。
- [x] 前端“字段审阅”面板明确显示 `不会写入正式变量角色集`，并提供“候选已确认 / 需要调整 / 驳回候选”按钮。
- [ ] 未覆盖：候选字段的人工搜索/编辑、多候选比较、value labels/缺失率参与评分、把确认后的候选显式提升为正式 VariableRoleSet。

### 测试覆盖

- RED：`python3 -m unittest tests.test_variable_role_candidates -v` 首次 5 条失败，失败原因是候选 API 404 和前端缺少候选审阅面板。
- 目标测试：`python3 -m unittest tests.test_variable_role_candidates -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_variable_role_candidates tests.test_external_dataset_import_profile tests.test_variable_role_confirmation -v`，17 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，195 tests OK，skipped=1，耗时 8.095s。
- 静态检查：`python3 -m py_compile Product/app.py Product/backend/variable_role_service.py Product/backend/overview_service.py Product/backend/project_service.py` 通过；`node --check Product/web/assets/app.js` 通过。

### API / 可视化验收

- API：`GET /api/v1/projects/proj_undergraduate_thesis/variable-role-candidates` 返回 200。
- 页面：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260515-p2l-candidates1`，点击“数据与设计”，页面显示真实 CFPS `.dta` 字段画像、723 个字段和“字段审阅”面板。
- 页面：点击“生成变量角色候选”后，面板显示 `待人工审阅`、`evidence_level=local_file`、`候选边界 不会写入正式变量角色集`、候选 outcome/treatment/controls/instruments 和候选字段表。
- 页面：点击“候选已确认”后，按钮状态显示 `候选已确认`，review event 记录 `approve_candidate`。
- 文件边界：确认前后 `state/product/variable_roles.json` SHA256 均为 `bc8bedca4d1638d2556ad77957de146eda170cef521db24eeb7ffde5c2e94649`，mtime 均为 `1778605951`。
- Candidate 状态：最新 `variable_role_candidate_1fbe9c0ee659` 为 `approved_candidate`，`does_not_mutate_variable_role_set=true`。
- Browser 插件限制：Playwright MCP 仍返回 `Transport closed`；Node Browser client 超时。本轮使用 Chrome + Computer Use 完成点击级验收。

### 剩余风险

- 当前变量角色推断是启发式，真实 CFPS 上把 `countyid` 猜为结果变量、`kt3_a_1` 猜为处理变量；这只能证明产品状态机，不可直接用于论文。
- 正式变量角色编辑器仍使用 `analysis_sample.csv` 作为已批准数据源；下一步必须让真实 candidate 进入可编辑正式确认流程。
- DTA value labels、缺失统计和抽样预览还没参与候选建议。
- StatsPAI/StataMCP 尚未实际执行，下一阶段仍需独立日志、结果文件、evaluator checks 和跨后端验证。

## 2026-05-14 P2-M Candidate Promotion to Formal VariableRoleSet

### 行为覆盖

- [x] 未确认、需调整或被驳回的 VariableRoleCandidate 不能写入正式 VariableRoleSet。
- [x] 已确认 candidate 可以进入正式变量角色编辑器，用户编辑后的 outcome/treatment/controls/instruments 以编辑器内容为准。
- [x] 后端写回正式 VariableRoleSet 时必须保存 `candidate_id`、`dataset_import_id`、`dataset_import_profile_id`、数据来源、绑定方式和 provenance。
- [x] 成功写回后 candidate 状态必须变为 `applied_to_variable_roles`，并记录正式角色集 version。
- [x] 前端必须明确显示候选边界：载入编辑器后仍可调整，保存后才写入正式变量角色集。
- [ ] 未覆盖：多候选对比、字段搜索、value labels/缺失统计参与建议、保存后自动重建 DesignSpec/RunPlan。

### 测试覆盖

- RED：`python3 -m unittest tests.test_variable_role_candidates -v` 首次新增行为失败，原因是旧保存逻辑仍把真实候选数据路径当作非法本地数据路径，前端也没有 `pendingVariableRoleCandidateId`。
- 目标测试：`python3 -m unittest tests.test_variable_role_candidates -v`，8 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，198 tests OK，skipped=1，耗时 8.854s。
- 静态检查：`python3 -m py_compile Product/backend/variable_role_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。

### API / 可视化验收

- 页面：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2m`，进入“数据与设计”。
- 页面：已确认 CFPS `.dta` candidate 显示 `候选已确认`、`候选边界 不会写入正式变量角色集`、`后续动作 可进入正式变量角色集编辑器`。
- 页面：点击“载入正式编辑器”后，变量角色编辑器显示 `draft_from_candidate · local_file`、真实 DTA 路径、`candidate_id=variable_role_candidate_495092cb7af2`、`结果变量 countyid`、控制变量候选和确认说明。
- 保护性验收：没有点击“保存变量角色集”，因为当前 CFPS 候选仍是启发式，直接保存会覆盖演示项目的 `analysis_sample.csv` 已批准变量角色。

### 剩余风险

- 当前真实 CFPS candidate 仍由启发式生成，不能直接用于论文；下一步需要字段搜索、变量标签、缺失统计和样本预览辅助人工选择。
- DesignSpec/RunPlan 还没有基于 candidate 写回后的正式 VariableRoleSet 自动刷新。
- StatsPAI/StataMCP 仍是候选后端，尚未实际执行并生成独立日志、结果文件和 evaluator checks。
- 线上版仍需要上传/云对象路径抽象；本地版可以绑定 `/Users/...`，云端不能执行本地路径。

## 2026-05-14 P2-N/P2-O StatsPAI Validation 与 LLM Supervisor

### 行为覆盖

- [x] CSV OLS full run 在 StatsPAI 可用时必须真实执行独立 validation，而不是只展示候选后端。
- [x] StatsPAI validation 必须写出独立 JSON 产物，供审计和复现。
- [x] 实证执行页必须展示独立后端验证状态、adapter、artifact、证据等级和交叉验证。
- [x] workflow contract 必须显式声明 LLM Supervisor 层，不能只靠工程状态机推进。
- [x] 首页必须展示本地 Codex Supervisor readiness、执行开关、阻塞原因和派工计划。
- [ ] 未覆盖：启用本地 Codex 后真实生成 supervisor plan artifact；Stata do-file/log 执行；StatsPAI 对 DTA/面板/IV/DID/RDD 等方法的执行。

### 测试覆盖

- RED：StatsPAI 行为首次失败为缺少 `backend_validations` 和 `Results/json/statspai_execution_result.json`；LLM Supervisor 行为首次失败为缺少 `workflow_contract.intelligence_layer` 和 `llm-supervisor-panel`。
- 目标测试：`python3 -m unittest tests.test_clean_workbench_visual_contract tests.test_ols_execution_adapter tests.test_observable_execution_frontend tests.test_product_workflow_contract -v`，40 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，203 tests OK，skipped=1，耗时 12.235s。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/backend/overview_service.py Product/backend/project_service.py Product/app.py` 通过。

### API / 可视化验收

- API：`GET /api/v1/providers/local-codex` 返回 `available=true`、`path=/Users/mahaoxuan/.local/bin/codex`、`version=codex-cli 0.130.0`、`execution_enabled=false`。
- API：`GET /api/v1/projects/proj_undergraduate_thesis/overview` 返回 `workflow_contract.intelligence_layer.status=blocked`，blocker 为 `local_codex_execution_not_enabled`。
- 页面：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2n-supervisor1`，首页显示“智能中控”“本地 Codex Supervisor 未启用”“允许执行=否”和派工计划。
- API / 页面：点击“启动完整实证执行”后，最终复核 run `run_bb423547439c` 的 observability 返回 `独立后端验证`、`passed`、`statspai.regress`、`Results/json/statspai_execution_result.json`。

### 剩余风险

- 本地 Codex 还没有真正进入执行层；当前只是 provider readiness + workflow contract + UI。下一步必须实现 plan artifact 和 gated execution。
- StatsPAI 只完成当前 CSV OLS 独立验证；真实 CFPS `.dta`、StataMCP、DID/IV/RDD/PSM/DML 和稳健标准误还没完成。
- LLM 输出需要持久化、审计和人工确认；不能让 Supervisor 输出直接覆盖 VariableRoleSet、DesignSpec、RunPlan 或论文正文。
- 本地版和线上版要继续分离：本地版可接 Codex、本地数据和本地统计后端；线上版必须走云模型、上传数据和云执行队列。

## 2026-05-16 P2-P Local Codex SupervisorPlan

### 行为覆盖

- [x] 未启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 时，SupervisorPlan 生成必须阻断，不能创建伪计划。
- [x] 启用本地 Codex 后，系统必须把计划持久化为 `state/product/supervisor_plan.json`，并标记 `status=needs_review`、`evidence_level=local_execution`。
- [x] SupervisorPlan 只能读取并引用 approved VariableRoleSet、DesignSpec、RunPlan，不得直接改写这些正式研究状态。
- [x] GET API 必须返回已保存的同一份 SupervisorPlan，支持跨 Session 恢复。
- [x] 首页必须展示 SupervisorPlan 审阅台、生成入口、证据要求、风险和子 Agent 分工。
- [ ] 未覆盖：真实 Codex subprocess 在持久 app 中生成一份生产计划；SupervisorPlan approve/reject 状态机；approved plan 到任务队列的真实派工。

### 测试覆盖

- RED：`python3 -m unittest tests.test_supervisor_plan -v` 首次 5 条失败，失败点为 API 404 和前端缺少 `supervisor-plan-panel`。
- 目标测试：`python3 -m unittest tests.test_supervisor_plan -v`，5 tests OK。
- 相邻回归：`python3 -m unittest tests.test_supervisor_plan tests.test_product_workflow_contract tests.test_design_run_plan_state_machine -v`，20 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，208 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/backend/supervisor_plan_service.py Product/backend/codex_provider.py Product/app.py Product/backend/overview_service.py` 通过；`git diff --check` 通过。

### API / 可视化验收

- API：`GET /api/v1/projects/proj_undergraduate_thesis/supervisor-plan` 返回 `status=empty`、`provider.available=true`、`execution_enabled=false`、`next_action.label=生成 SupervisorPlan`。
- API：默认环境调用 `POST /api/v1/projects/proj_undergraduate_thesis/supervisor-plan` 返回 409 `local_codex_execution_not_enabled`。
- 页面：当前工作树服务打开 `http://127.0.0.1:8767/?v=20260516-p2p-supervisor-plan`；headless Chrome DOM 检测到 `SupervisorPlan 审阅台`、`生成 SupervisorPlan`、`本地 Codex SupervisorPlan`、`local_codex_execution_not_enabled`。
- 截图：`artifacts/ui-checks/p2p-supervisor-plan-overview.png`，1440x1100。

### 剩余风险

- SupervisorPlan 仍是待审计划，不是自动执行编排；下一步需要 approve/reject/needs_revision。
- 本轮未在真实 app 中启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 调用真实 Codex，避免在默认验收中产生不可控模型输出。
- 子 Agent 分工目前是计划字段，还没有真正拉起执行者或写入运行队列。
- StatsPAI 只恢复并验证 OLS CSV 路径；DTA、StataMCP 和更多实证方法族仍未完成。

## 2026-05-16 P2-P1 Home Progressive Disclosure

### 行为覆盖

- [x] 智能中控首屏只显示本地 Codex Supervisor 状态、证据等级、阻塞数量和派工角色数量。
- [x] Provider、可用性、允许执行、版本、阻塞项和派工计划默认折叠，点击 `查看中控详情` 后展开。
- [x] SupervisorPlan 审阅台首屏只显示状态、主按钮、人工确认说明和下一步摘要。
- [x] 版本、写入边界、阶段计划、子 Agent 分工、证据要求和风险默认折叠，点击 `查看计划详情` 后展开。
- [x] 使用原生 `details/summary`，默认不 `open`，支持键盘 focus。
- [ ] 未覆盖：移动视口截图；执行页和 Review & Export 页面同类高密度内容的进一步折叠。

### 测试覆盖

- RED：`python3 -m unittest tests.test_supervisor_plan tests.test_product_workflow_contract -v` 首次新增 2 条失败，原因是缺少 `supervisor-plan-progressive-disclosure`、`intelligence-progressive-disclosure` 和对应 summary 文案。
- 目标测试：`python3 -m unittest tests.test_supervisor_plan tests.test_product_workflow_contract -v`，15 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，210 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/app.py` 通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-home-progressive-disclosure-bdd.md`：新增本轮信息架构行为说明。
- `tests/test_supervisor_plan.py`：锁定 SupervisorPlan 详情默认折叠。
- `tests/test_product_workflow_contract.py`：锁定智能中控详情默认折叠。
- `Product/web/assets/app.js`：重排 `renderIntelligenceLayer()` 和 `renderSupervisorPlan()`，把高噪声明细移入 `details/summary`。
- `Product/web/assets/styles.css`：新增折叠控件、决策信号行和 focus 样式。
- `Product/web/index.html`：更新资源版本。

### 手动验收

1. 打开右侧 Codex 内置浏览器：`http://127.0.0.1:8767/?v=20260516-p2p-disclosure1`。
2. 在“工作台首页”查看“智能中控”：默认只显示状态和摘要；点击 `查看中控详情` 后显示 Provider、执行开关、阻塞项、派工计划。
3. 查看 `SupervisorPlan 审阅台`：默认只显示状态、生成按钮和下一步摘要；点击 `查看计划详情` 后显示版本、边界、阶段计划、子 Agent 分工、证据要求和风险。
4. 本轮截图：`artifacts/ui-checks/p2p-home-progressive-disclosure.png`。

### 剩余风险

- 这次解决的是首页局部信息密度，不代表所有页面已经完成 clean workbench 收敛。
- SupervisorPlan 仍然只是 `needs_review` 产物；下一步必须做审批状态机。
- 详情内容仍会在 DOM text 中存在，这是原生 `details` 的正常行为；视觉和交互上默认折叠。

## 2026-05-16 P2-Q Topic-first Home

### 行为覆盖

- [x] 首页第一屏先让用户输入或选择研究选题，不再默认摊开展示所有执行/Agent/风险模块。
- [x] 用户可以点击 `从已有选题继续`，用 overview 中已有研究问题进入判断环节。
- [x] 用户可以点击 `从真实数据候选池开始`，直接进入“数据与设计”页，但不会自动绑定数据或写入变量角色。
- [x] 选题确认前，`下一步研究决策`、智能中控、SupervisorPlan 和证据 banner 默认隐藏。
- [x] 选题确认后，研究判断区展开并显示后续执行入口。
- [ ] 未覆盖：后端持久化 ResearchQuestion/TopicSession；选题绑定 SupervisorPlan 审批；线上版上传数据入口。

### 测试覆盖

- RED：`python3 -m unittest tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v` 首次新增 3 条失败，失败原因为缺少 `research-topic-intake`、`research-workbench-after-topic` 和 `data-topic-start-action`。
- 目标测试：`python3 -m unittest tests.test_product_workflow_contract.ProductWorkflowFrontendContractTests -v`，9 tests OK。
- 相邻回归：`python3 -m unittest tests.test_product_workflow_contract tests.test_supervisor_plan -v`，18 tests OK。
- 全量回归：`python3 -m unittest discover -s tests -v`，213 tests OK，skipped=1。
- 静态检查：`node --check Product/web/assets/app.js` 通过；Python 编译检查通过；`git diff --check` 通过。

### 实现范围

- `docs/architecture-v2/codex-phase-p2-topic-first-home-bdd.md`：新增本轮 BDD 行为契约。
- `tests/test_product_workflow_contract.py`：锁定首页先选题、确认后展开和数据候选入口。
- `Product/web/index.html`：新增选题入口并重组首页工作台区域。
- `Product/web/assets/app.js`：新增选题状态和交互。
- `Product/web/assets/styles.css`：新增选题入口与窄视口降噪样式。

### 手动验收

1. 打开右侧 Codex 内置浏览器：`http://127.0.0.1:8767/?v=20260516-p2q-topic1`。
2. 首屏应看到 `开始一项实证研究` 和选题输入框，而不是直接看到所有执行与 Agent 面板。
3. 输入一个选题，例如“机器人应用是否影响劳动力市场匹配效率？”，点击 `进入研究判断`。
4. 页面应显示已确认选题，并展开 `下一步研究决策`、智能中控和 SupervisorPlan。
5. 刷新后可用 `从已有选题继续` 恢复本地确认状态；点击 `从真实数据候选池开始` 应切到“数据与设计”。

### 剩余风险

- 选题目前是前端本地状态，不是后端审计对象；下一步需要 ResearchQuestion/TopicSession。
- 右侧内置浏览器截图捕获超时；本轮以 DOM 检查和实际可见交互作为验收证据。
- 这轮只调整首页入口，没有完成 SupervisorPlan approve/reject/needs_revision 审批。

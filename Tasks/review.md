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

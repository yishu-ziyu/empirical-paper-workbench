# Manifest

## 长程状态文件

- `Tasks/todo.md`：当前任务状态机
- `Tasks/handoff.md`：跨 Session 接手说明
- `Tasks/decision-log.md`：关键决策与不要重复探索的理由
- `Tasks/manifest.md`：关键产物路径
- `Tasks/review.md`：验证、风险、未完成项

## 关键开发文件

- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `Product/app.py`
- `Product/backend/project_service.py`
- `Product/backend/observability_service.py`
- `Product/backend/overview_service.py`
- `Product/backend/variable_role_service.py`
- `Product/backend/design_spec_service.py`
- `Product/backend/manuscript_candidate_service.py`

## 关键测试文件

- `tests/test_observable_execution.py`
- `tests/test_observable_execution_frontend.py`
- `tests/test_agent_cluster_frontend_interactions.py`
- `tests/test_api_contract_v2.py`
- `tests/test_product_v1_local.py`
- `tests/test_dataset_frontend.py`
- `tests/test_variable_role_confirmation.py`
- `tests/test_design_run_plan_state_machine.py`
- `tests/test_full_run_from_run_plan.py`
- `tests/test_manuscript_consumption.py`

## 新增设计/方法论文件

- `docs/architecture-v2/statspai-methodology-synthesis-2026-05-12.md`
- `docs/architecture-v2/codex-phase-p0-observable-ui-bdd.md`
- `docs/architecture-v2/codex-phase-p1-gate-resolve-bdd.md`
- `docs/architecture-v2/codex-phase-p1-gate-resolve-frontend-bdd.md`
- `docs/architecture-v2/codex-phase-p1-dataset-run-bdd.md`
- `docs/architecture-v2/codex-phase-p1-run-dataset-source-ui-bdd.md`
- `docs/architecture-v2/codex-phase-p1-variable-roles-bdd.md`
- `docs/architecture-v2/codex-phase-p1-observable-console-density-bdd.md`
- `docs/architecture-v2/product-flow-reset-2026-05-12.md`
- `docs/architecture-v2/product-workflow-contract-bdd.md`
- `docs/architecture-v2/codex-phase-p1-variable-role-confirmation-bdd.md`
- `docs/architecture-v2/codex-phase-p1-design-run-plan-bdd.md`
- `docs/architecture-v2/codex-phase-p1-full-run-from-run-plan-bdd.md`
- `docs/architecture-v2/codex-phase-p1-manuscript-consumption-bdd.md`
- `docs/architecture-v2/codex-phase-p1-manuscript-candidate-review-bdd.md`
- `docs/architecture-v2/codex-phase-p1-manuscript-promote-preflight-bdd.md`
- `docs/architecture-v2/codex-phase-p1-export-preflight-bdd.md`
- `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`
- `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`

## 新增/扩展 API

- `GET /api/v1/projects/{project_id}/runs/{run_id}/observability`
- `POST /api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve`
- `GET /api/v1/projects/{project_id}/datasets`
- `POST /api/v1/projects/{project_id}/runs` accepts optional `dataset_path`
- `GET /api/v1/projects/{project_id}/runs/{run_id}/observability` returns top-level `dataset_source`
- `GET /api/v1/projects/{project_id}/runs/{run_id}/observability` returns top-level `variable_roles`
- `GET /api/v1/projects/{project_id}/overview` returns top-level `workflow_contract` with `canonical_stages`, `next_action`, and `run_readiness`
- `GET /api/v1/projects/{project_id}/variable-roles` returns draft or saved VariableRoleSet with `evidence_level=local_file`
- `PUT /api/v1/projects/{project_id}/variable-roles` saves approved VariableRoleSet to `state/product/variable_roles.json`
- `GET /api/v1/projects/{project_id}/overview` reads approved VariableRoleSet and advances `workflow_contract.next_action` to `confirm_design_spec`
- `GET /api/v1/projects/{project_id}/design-spec` returns draft or saved DesignSpec based on approved VariableRoleSet
- `PUT /api/v1/projects/{project_id}/design-spec` saves approved DesignSpec to `state/product/design_spec.json`
- `GET /api/v1/projects/{project_id}/run-plan` returns draft or saved RunPlan based on approved DesignSpec
- `PUT /api/v1/projects/{project_id}/run-plan` saves approved RunPlan to `state/product/run_plan.json`
- `GET /api/v1/projects/{project_id}/overview` reads approved DesignSpec and RunPlan, advances `workflow_contract.next_action` to `confirm_run_plan` or `start_full_run`, and sets `run_readiness.can_start_full_run=true` only after RunPlan approval
- `POST /api/v1/projects/{project_id}/runs/full` starts a product-level full run from approved RunPlan
- `GET /api/v1/projects/{project_id}/runs/{run_id}` returns `plan_binding`, `research_engine`, and `execution_evidence_level` for full runs
- `GET /api/v1/projects/{project_id}/runs/{run_id}/observability` exposes full-run manifest fields including `run_plan_binding` and `research_engine`
- `GET /api/v1/projects/{project_id}/results-draft` returns latest successful full-run findings and draft evidence bindings
- `Product/backend/results_draft_service.py` reads `Results/json/analysis_result.json`, `Manuscripts/generated/paper_draft.md`, and run manifest metadata to build `FindingCard` and `DraftSection` payloads
- `PUT /api/v1/projects/{project_id}/results-draft/findings/{finding_id}/review` persists claim review decisions to `state/product/finding_reviews.json`
- `GET /api/v1/projects/{project_id}/manuscript-candidates` returns draft manuscript section candidates derived only from approved FindingCards with `can_write_to_draft=true`
- `Product/backend/manuscript_candidate_service.py` builds Manuscript candidates and binds `source_draft`, `result_artifact`, and `review_decision` provenance
- `PUT /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/review` persists candidate review decisions to `state/product/manuscript_candidate_reviews.json`
- `GET /api/v1/projects/{project_id}/manuscript-candidates` returns `review_status`, `can_promote`, `review`, and `candidate_review` provenance when candidate review exists
- `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/promote` persists promotion preflight state to `state/product/manuscript_candidate_promotions.json`
- `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/export-preflight` persists export preflight state to `state/product/export_package_manifest.json` and creates a write-back preview under `Manuscripts/generated/previews/`
- `GET /api/v1/projects/{project_id}/manuscript-candidates` returns `promotion_status`, `export_status`, `writeback_preview_path`, `export_manifest_path`, `can_write_back=false`, and `export_package` provenance when those states exist

## 新增/扩展前端能力

- `Product/web/assets/app.js`：`v2api.runs.resolveGate(projectId, runId, gateId, action, note)`
- `Product/web/assets/app.js`：`resolveObservableGate(gateId, action)`
- `Product/web/assets/app.js`：开放 gate 显示 confirm/reject/adjust 和 note；resolved gate 显示 resolution。
- `Product/web/assets/app.js`：数据页显示本地数据集 `path`、`role`、`row_count`、`column_count`、`file_type`、`evidence_level`。
- `Product/web/assets/app.js`：`startObservableRunForDataset(datasetPath)` 从数据页带 `dataset_path` 启动可观察 run。
- `Product/web/assets/app.js`：`renderObservableDatasetSource()` 在执行页显示 run 数据源证据。
- `Product/web/assets/app.js`：`renderObservableVariableRoles()` 在执行页显示 outcome/treatment/controls/instruments 和 HITL 确认状态。
- `Product/web/index.html`：执行页新增 `execution-control-panel` 和 `execution-context-grid`，把运行控制、run 摘要、数据源、变量角色合并为紧凑执行上下文。
- `Product/web/assets/styles.css`：`#view-empirical-execution` 使用 scoped system font、8px 控制台卡片、紧凑列表和移动端无横向溢出规则。
- `Product/web/index.html`：CSS 使用 `?v=20260512-p1ui3`，JS 使用 `?v=20260512-p1d` 版本 query，避免本地缓存旧静态资源。
- `Product/web/index.html`：一阶导航收敛为 `Workspace Home / Data & Design / Execution / Results & Draft / Review & Export`。
- `Product/web/assets/app.js`：`renderWorkflowContract(contract)` 渲染首页下一步研究决策和 9 阶段 workflow spine。
- `Product/web/assets/app.js`：`renderVariableRoleWorkflow(items)` 和 `openDesignAction(datasetPath)` 让数据页先进入变量角色确认。
- `Product/web/assets/app.js`：`renderExecutionPreflight()` 渲染 `can_start_full_run` 与 `variable_roles_unconfirmed/design_unconfirmed/run_plan_missing`。
- `Product/web/index.html`：CSS 使用 `?v=20260512-flow1`，JS 使用 `?v=20260512-flow1` 版本 query，避免本地缓存旧静态资源。
- `Product/web/assets/app.js`：`v2api.variableRoles.get(projectId)` 和 `v2api.variableRoles.save(projectId, payload)` 读写产品级 VariableRoleSet。
- `Product/web/assets/app.js`：`renderVariableRoleEditor()` 渲染 outcome/treatment/controls/instruments/fixed_effects/cluster_by/note 编辑器。
- `Product/web/assets/app.js`：`handleSaveVariableRoles(event)` 保存变量角色后重新读取 VariableRoleSet 与 overview contract。
- `Product/web/index.html`：Data & Variables 新增 `variable-role-confirmation-form`。
- `Product/web/index.html`：CSS/JS 静态资源版本更新到 `?v=20260513-p1e`。
- `Product/web/assets/app.js`：`v2api.designSpec.get/save` 与 `v2api.runPlan.get/save` 读写产品级 DesignSpec/RunPlan。
- `Product/web/assets/app.js`：`renderDesignSpecEditor()` 和 `handleSaveDesignSpec(event)` 渲染并保存研究问题、识别策略、模型设定和固定效应。
- `Product/web/assets/app.js`：`renderRunPlanEditor()` 和 `handleSaveRunPlan(event)` 渲染并保存执行任务、产出清单和 RunPlan note。
- `Product/web/index.html`：Data & Design 新增 `design-spec-confirmation-form`；Execution 新增 `run-plan-confirmation-form`。
- `Product/web/index.html`：CSS/JS 静态资源版本更新到 `?v=20260513-p1fg`。
- `Product/web/assets/app.js`：`v2api.runs.startFull(projectId)` 调用 `POST /runs/full`。
- `Product/web/assets/app.js`：`createFullRunFromPlan()` 启动完整执行后刷新项目、overview、run selector 和 observability。
- `Product/web/assets/app.js`：`renderExecutionPreflight()` 在 `start_full_run` ready 后启用完整执行按钮，并保留 dry-run 为开发捷径。
- `Product/web/index.html`：Execution 控制区新增 `observable-run-full-button`。
- `Product/web/index.html`：CSS/JS 静态资源版本更新到 `?v=20260513-p1h`。
- `Product/web/assets/app.js`：`v2api.resultsDraft.get(projectId)` 调用 `GET /results-draft`。
- `Product/web/assets/app.js`：`v2api.resultsDraft.reviewFinding(projectId, findingId, payload)` 调用 `PUT /results-draft/findings/{finding_id}/review`。
- `Product/web/assets/app.js`：`renderResultsDraftEvidence()` 渲染 FindingCard 和 DraftSection evidence binding。
- `Product/web/assets/app.js`：`reviewFinding(findingId, action)` 保存 FindingCard claim review，并刷新 Results & Draft。
- `Product/web/assets/app.js`：`v2api.manuscriptCandidates.get(projectId)` 调用 `GET /manuscript-candidates`。
- `Product/web/assets/app.js`：`v2api.manuscriptCandidates.reviewCandidate(projectId, candidateId, payload)` 调用 `PUT /manuscript-candidates/{candidate_id}/review`。
- `Product/web/assets/app.js`：`renderManuscriptCandidates()` 渲染 approved FindingCard 派生的正文候选和空状态 `approved_finding_required`。
- `Product/web/assets/app.js`：`renderCandidateProvenance(label, item)` 渲染 `source_draft`、`result_artifact`、`review_decision` 三类 provenance。
- `Product/web/assets/app.js`：`reviewManuscriptCandidate(candidateId, action)` 保存正文候选审阅状态并刷新 candidates。
- `Product/web/assets/app.js`：`renderCandidateReviewPanel(candidate)` 渲染 candidate 审阅备注和 approve/needs_revision/reject 操作。
- `Product/web/assets/app.js`：`v2api.manuscriptCandidates.promoteCandidate(projectId, candidateId, payload)` 调用 `POST /manuscript-candidates/{candidate_id}/promote`。
- `Product/web/assets/app.js`：`promoteManuscriptCandidate(candidateId)` 保存 promotion preflight 并刷新 candidates。
- `Product/web/assets/app.js`：`renderCandidatePromotePanel(candidate)` 渲染 `ready_for_export`、`can_write_back` 和 promotion evidence。
- `Product/web/assets/app.js`：`v2api.manuscriptCandidates.exportPreflightCandidate(projectId, candidateId, payload)` 调用 `POST /manuscript-candidates/{candidate_id}/export-preflight`。
- `Product/web/assets/app.js`：`exportPreflightManuscriptCandidate(candidateId)` 生成 write-back preview / export package manifest 并刷新 candidates。
- `Product/web/assets/app.js`：`renderCandidateExportPreflightPanel(candidate)` 渲染 `preview_ready`、`writeback_preview_path`、`manifest_path` 和 export preflight evidence。
- `Product/web/index.html`：Results & Draft 新增 `results-findings-list` 和 `draft-evidence-sections`。
- `Product/web/index.html`：Results & Draft 新增 `manuscript-candidates-list`。
- `Product/web/assets/styles.css`：新增 finding/draft evidence binding 的行内换行与布局样式。
- `Product/web/assets/styles.css`：新增 `claim-review-actions`、`finding-review-panel`、`review-status` 样式。
- `Product/web/assets/styles.css`：新增 `manuscript-candidates-panel`、`manuscript-candidate-body`、`candidate-provenance` 样式。
- `Product/web/assets/styles.css`：新增 `candidate-review-panel` 样式。
- `Product/web/assets/styles.css`：新增 `candidate-promote-panel` 样式。
- `Product/web/assets/styles.css`：新增 `candidate-export-panel` 样式。
- `Product/web/index.html`：CSS/JS 静态资源版本更新到 `?v=20260513-p1n`。
- `Product/web/index.html`：全局 shell 增加 `clean-workbench-shell`，静态资源版本更新到 `?v=20260513-clean1`。
- `Product/web/index.html`：右侧 `archive-inspector` 同时作为 `inspector-rail`，文案调整为“属性检查器”。
- `Product/web/assets/app.js`：`renderVariableRoleWorkflow()` 改为 `research-record-card`、`record-meta-grid`、`research-step-list`、`compact-action-row`，避免变量角色确认入口重叠。
- `Product/web/assets/styles.css`：新增 `--surface-clean`、`inspector-rail`、`research-record-card`、`record-meta-grid`、`record-path`、`research-step-list`、`compact-action-row`；移除 archive shell 的纸格背景和厚重渐变阴影。
- `Product/web/index.html`：全局 shell 增加 `clean-workbench-shell`，静态资源版本更新到 `?v=20260513-clean1`。
- `Product/web/index.html`：右侧 `archive-inspector` 同时作为 `inspector-rail`，文案调整为“属性检查器”。
- `Product/web/assets/app.js`：`renderVariableRoleWorkflow()` 改为 `research-record-card`、`record-meta-grid`、`research-step-list`、`compact-action-row`，避免变量角色确认入口重叠。
- `Product/web/assets/styles.css`：新增 `--surface-clean`、`inspector-rail`、`research-record-card`、`record-meta-grid`、`record-path`、`research-step-list`、`compact-action-row`；移除 archive shell 的纸格背景和厚重渐变阴影。

## 手动验收产物

- `state/runs/run_3ffe1e6c1f53/run_manifest.json`
- `state/runs/run_3ffe1e6c1f53/run_steps.json`
- `state/runs/run_3ffe1e6c1f53/run_events.jsonl`
- `state/runs/run_3ffe1e6c1f53/gates.json`
- `state/runs/run_fc725d15b3c0/run_manifest.json`
- `state/runs/run_641c9770a1a8/run_manifest.json`
- `state/product/variable_roles.json`
- `state/product/design_spec.json`
- `state/product/run_plan.json`
- `state/product/finding_reviews.json`
- `state/product/manuscript_candidate_reviews.json`
- `state/product/manuscript_candidate_promotions.json`
- `state/product/export_package_manifest.json`
- `state/runs/run_c424d6a11af7/run_manifest.json`
- `state/runs/run_c424d6a11af7/run_steps.json`
- `state/runs/run_c424d6a11af7/run_events.jsonl`
- `state/runs/run_c424d6a11af7/gates.json`
- `state/runs/run_c424d6a11af7.json`
- `Results/json/analysis_result.json`
- `Manuscripts/generated/paper_draft.md`
- `Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md`

说明：上述 run 产物为本地验收生成，当前被 gitignore 忽略；P1-A 浏览器验收已将 `gate_dataset_fields` resolve 为 confirm，剩余开放 gate 可用于继续手动验收。需要全新开放 gate 时可重新点击“启动试运行”。
P1-B 浏览器验收生成 `run_fc725d15b3c0`，其 manifest 已包含 `dataset_source.path=Data/Final/analysis_sample.csv` 和 `dataset_source.evidence_level=local_file`。
P1-C 浏览器验收生成 `run_641c9770a1a8`，其 observability 顶层和 manifest 都包含 `dataset_source.row_count=12`、`dataset_source.column_count=4`。
P1-D 复用 `run_641c9770a1a8` 验证 `variable_roles.confirmation_gate_id=gate_dataset_fields`、`confirmation_status=open`。
P1-E 浏览器验收创建 `state/product/variable_roles.json`，其中 `status=approved`、`evidence_level=local_file`、`dataset_path=Data/Final/analysis_sample.csv`、`roles.outcome=wage`、`roles.treatment=trained`、`roles.controls=edu, experience`。
P1-F 浏览器验收创建 `state/product/design_spec.json`，其中 `status=approved`、`evidence_level=local_file`、`identification_strategy.name=baseline_ols`、`model.formula=wage ~ trained + edu + experience`。
P1-G 浏览器验收创建 `state/product/run_plan.json`，其中 `status=approved`、`evidence_level=local_file`、`tasks[0].id=baseline_regression`、`outputs` 包含 `regression_table`、`run_manifest`、`run_events`、`paper_draft_section`。
P1-H 浏览器验收创建 full run `run_c424d6a11af7`，其中 run store `mode=full-run`、`status=succeeded`、`execution_evidence_level=local_execution`；manifest 包含 `run_plan_binding.evidence_level=local_file`、`research_engine.name=Feynman-compatible research engine`、`research_engine.embedded=false`、`research_engine.integration_mode=callable_external`。
P1-I 浏览器验收读取 `run_c424d6a11af7`，Results & Draft 显示 FindingCard `trained effect on wage`，估计值 `1.8505`、SE `0.0573`、p `9.18e-10`、n `12`，并把草稿章节绑定到 `Manuscripts/generated/paper_draft.md` 和 `Results/json/analysis_result.json`。
P1-J 浏览器验收对 `finding_trained_effect` 执行 `approve`，创建 `state/product/finding_reviews.json`；Results & Draft 显示 `review_status=approved`、`accept-for-writing=yes`、`review evidence=local_file`，并保留 `run_id=run_c424d6a11af7` 和 `artifact_path=Results/json/analysis_result.json`。
P1-K API 验收读取 `GET /api/v1/projects/proj_undergraduate_thesis/manuscript-candidates`，返回 `manuscript_candidate_finding_trained_effect_results`，正文候选绑定 `run_c424d6a11af7`、`finding_trained_effect`、`run_plan_version=1`，provenance 包含 `Manuscripts/generated/paper_draft.md`、`Results/json/analysis_result.json`、`state/product/finding_reviews.json`。
P1-K 浏览器验收打开 `http://127.0.0.1:8765/?v=20260513-p1k`，Results & Draft 页面显示 1 个 Manuscript candidate，无 `overwrite-paper-draft` 写回按钮，候选卡片横向溢出数量为 0，console errors/warnings=0。
P1-L API 验收对 `manuscript_candidate_finding_trained_effect_results` 执行 `approve`，创建 `state/product/manuscript_candidate_reviews.json`；再次读取 candidates 显示 `review_status=approved`、`can_promote=true`、`candidate_review.evidence_level=local_file`。
P1-L 浏览器验收打开 `http://127.0.0.1:8765/?v=20260513-p1l`，Results & Draft 页面显示 `review_status=approved`、`can-promote=yes`、candidate review provenance 和 approve/needs_revision/reject 操作；无 `overwrite-paper-draft`，overflowCount=0，console errors/warnings=0。
P1-M API 验收对 `manuscript_candidate_finding_trained_effect_results` 执行 `promote`，创建 `state/product/manuscript_candidate_promotions.json`；再次读取 candidates 显示 `promotion_status=ready_for_export`、`can_export=true`、`can_write_back=false`、`promotion_state.evidence_level=local_file`。
P1-M 浏览器验收打开 `http://127.0.0.1:8765/?v=20260513-p1m`，Results & Draft 页面显示 `ready_for_export`、`can_write_back=no`、`promotion_state`、`promotion evidence` 和“进入导出前检查”按钮；无 `overwrite-paper-draft`，overflowCount=0，console errors/warnings=0。
P1-N API 验收对 `manuscript_candidate_finding_trained_effect_results` 执行 `export-preflight`，创建 `state/product/export_package_manifest.json` 和 `Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md`；再次读取 candidates 显示 `export_status=preview_ready`、`writeback_preview_path=Manuscripts/generated/previews/manuscript_candidate_finding_trained_effect_results.md`、`export_manifest_path=state/product/export_package_manifest.json`、`can_write_back=false`、`export_package.evidence_level=local_file`。
P1-N 静态/API 验收确认 `http://127.0.0.1:8765/?v=20260513-p1n` 返回新静态资源版本；Playwright 最终浏览器传输中断，已用 API、HTML asset 和 JS identifier fallback 复核，无 `overwrite-paper-draft` 标识。
P1-R Safari + Computer Use 验收确认 `http://127.0.0.1:8765/?v=20260513-clean1` 可打开；进入“数据与设计”后变量角色确认入口为单列记录布局，显示 `analysis_sample.csv`、`Data/Final/analysis_sample.csv`、两条研究步骤和“检查并确认变量角色”按钮，未再出现截图中的文本重叠。
P1-R Safari + Computer Use 验收确认 `http://127.0.0.1:8765/?v=20260513-clean1` 可打开；进入“数据与设计”后变量角色确认入口为单列记录布局，显示 `analysis_sample.csv`、`Data/Final/analysis_sample.csv`、两条研究步骤和“检查并确认变量角色”按钮，未再出现截图中的文本重叠。

## 外部方法论来源

- `https://www.statspai.com/zh/blog/statspai-agent-era-statistics-ecosystem`
- `https://www.statspai.com/`
- `https://www.statspai.com/zh/blog`
- `https://www.copaper.ai/`
- `https://github.com/brycewang-stanford/StatsPAI`

## 2026-05-13 P1-O Review & Export Package Workbench

### 新增/扩展文件

- `docs/architecture-v2/codex-phase-p1-review-export-package-bdd.md`
- `tests/test_review_export_package.py`
- `Product/backend/manuscript_candidate_service.py`
- `Product/app.py`
- `Product/web/index.html`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`

## 2026-05-13 P2-C OLS Execution Adapter

### 新增/扩展文件

- `docs/architecture-v2/codex-phase-p2-ols-execution-adapter-bdd.md`
- `tests/test_ols_execution_adapter.py`
- `tests/test_full_run_from_run_plan.py`
- `Product/backend/project_service.py`
- `Product/app.py`

### 新增/扩展 API 与产物

- `POST /api/v1/projects/{project_id}/runs/full`：approved OLS RunPlan 成功执行后返回 `method_execution`。
- `Results/json/method_execution_result.json`：本地 OLS 方法执行结果，`engine=python_ols_adapter`，`evidence_level=local_execution`。
- `state/runs/{run_id}/run_manifest.json`：新增 `method_execution` 段，指向方法执行产物。
- 结构化错误：unsupported method 返回 409 `unsupported_run_plan_method`；数据不足、公式不可估或共线设计返回 409 `method_execution_failed`。

### 手动验收产物

- `state/runs/run_4c62f1721afb.json`
- `state/runs/run_4c62f1721afb/run_manifest.json`
- `Results/json/method_execution_result.json`

说明：P2-C API 验收创建 full run `run_4c62f1721afb`，其中 `method_execution.artifact_path=Results/json/method_execution_result.json`、`engine=python_ols_adapter`、`evidence_level=local_execution`、`methods[0].method_id=ols`、`nobs=12`、`treatment_coefficient=1.8505076803`；`plan_binding.tasks[0].method_id=ols`。

### 新增/扩展 API

- `GET /api/v1/projects/{project_id}/export-package`

### 新增/扩展前端能力

- `Product/web/index.html`：Review & Export 新增 `export-package-workbench`，静态资源版本更新到 `?v=20260513-p1o`。
- `Product/web/assets/app.js`：新增 `v2api.exportPackage.get(projectId)`。
- `Product/web/assets/app.js`：新增 `renderExportPackageWorkbench()`，渲染导出包验收台、evaluator checks、Frontier-Eng iteration log、source return action 和 disabled write-back approval。
- `Product/web/assets/styles.css`：新增 `export-package-panel`、`export-package-summary`、`export-evaluator-checks`、`frontier-iteration-log` 等样式。

### 手动验收产物

- `/tmp/empirical-workbench-review-export-p1o.png`

说明：P1-O API 验收确认 `GET /api/v1/projects/proj_undergraduate_thesis/export-package` 返回 `export_status=preview_ready`、`evaluator_status=passed`、5 个 evaluator checks、Frontier-Eng iteration log 和 `can_write_back=false`。Chrome 可视化验收打开 `http://127.0.0.1:8765/?v=20260513-p1o`，点击 `Review & Export` 后显示“导出包验收台”、`evaluator=passed`、writeback preview/manifest/result artifact 路径、Frontier-Eng iteration log，并可点击“回到 Results & Draft 查看候选来源”。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`
- `docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`

### 新增/扩展测试

- `tests/test_frontend_chinese_copy.py`
- `tests/test_archive_interface_visual_contract.py`
- 已同步更新相邻 UI 契约测试中的中文文案期望。

### 新增/扩展前端能力

- `Product/web/index.html`：静态资源版本更新到 `?v=20260513-archive1`；全局壳改为 `archive-shell`；新增右侧 `archive-inspector`，包含 `研究档案`、`相邻笔记`、`证据图例`、`收藏架`。
- `Product/web/assets/app.js`：新增 `archivePageNotes`、`mountArchiveInspector()`、`updateArchiveInspector()`；右侧相邻笔记按钮通过 `data-inspector-view` 切换现有一级页面。
- `Product/web/assets/styles.css`：新增 archive interface layer；包含纸张网格背景、档案条目、证据 ledger、收藏架、hover、focus-visible、loading、empty、error 和响应式 inspector。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-archive1`

说明：Safari 可视化验收确认首页显示 `个人研究档案`、`本地证据`、右侧 `档案索引`、`相邻笔记`、`证据图例`、`收藏架`。点击右侧 `数据与设计` 后页面切换到变量角色集编辑器，右侧当前档案说明同步为 `数据与设计`。Browser/IAB 与 Playwright 本轮连接异常，已使用 Safari + Computer Use 作为可视化 fallback。

## 2026-05-13 P2-A Dataset Quality Profile

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-data-quality-profile-bdd.md`

### 新增/扩展测试

- `tests/test_dataset_quality_profile.py`
- `tests/test_frontend_chinese_copy.py`

### 新增/扩展后端能力

- `Product/backend/overview_service.py`：`list_project_datasets()` 为每个数据文件附加 `quality_profile`；新增 CSV 读取、字段类型推断、缺失率统计和 `readiness_status` 计算。

### 新增/扩展前端能力

- `Product/web/index.html`：静态资源版本更新到 `?v=20260513-p2a`；数据与设计页新增 `data-quality-profile-panel`。
- `Product/web/assets/app.js`：新增 `renderDatasetQualityProfile()`、`qualityReadinessLabel()`、`qualityColumnTypeLabel()`、`qualityCheckIcon()`、`formatQualityRate()`，数据卡片可点击“查看质量画像”。
- `Product/web/assets/styles.css`：新增 `data-quality-profile`、`quality-profile-grid`、`quality-check-list`、`quality-column-list` 等样式；`data-intake-grid` 强制单列，避免面板挤压。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-p2a`

说明：Safari + Computer Use 验收确认“数据与设计”页显示 `数据质量画像`、`analysis_sample.csv`、样本 12、缺失率 0%、字段画像和中文可见标签；Playwright MCP 仍出现 `Transport closed`，本轮用 Safari/接口/静态资源检查作为可视化 fallback。

## 2026-05-13 P1-P Writeback Approval + DOCX Preflight

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p1-writeback-docx-preflight-bdd.md`

### 新增/扩展测试

- `tests/test_review_export_package.py`

### 新增/扩展后端能力

- `Product/backend/manuscript_candidate_service.py`：新增写回审批状态、docx 预检状态、导出包状态聚合和拒绝/未审批阻断。
- `Product/app.py`：新增 writeback approval 与 docx preflight POST API。

### 新增/扩展前端能力

- `Product/web/assets/app.js`：Review & Export 新增证据表、写回审批面板、docx 预检面板、审批/预检 API 调用和交互状态。
- `Product/web/assets/styles.css`：新增 `review-export-evidence-bench`、`export-evidence-table`、`export-decision-panel`、`docx-preflight-checks` 等 clean workbench 样式。

### Runtime 产物

- `state/product/writeback_approvals.json`：显式写回审批状态，本地运行产物，不提交。
- `state/product/docx_export_preflight.json`：docx 导出预检状态，本地运行产物，不提交。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-p1p`

说明：重启 8765 的 uvicorn 服务后，Safari + Computer Use 可视化验收确认 Review & Export 显示“导出包验收台”，审批后显示 `写回：已审批`，点击 `运行 docx 预检` 后显示 `预检通过` 和四项检查。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`
- `docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`

### 新增/扩展测试

- `tests/test_frontend_chinese_copy.py`
- `tests/test_archive_interface_visual_contract.py`
- 已同步更新相邻 UI 契约测试中的中文文案期望。

### 新增/扩展前端能力

- `Product/web/index.html`：静态资源版本更新到 `?v=20260513-archive1`；全局壳改为 `archive-shell`；新增右侧 `archive-inspector`，包含 `研究档案`、`相邻笔记`、`证据图例`、`收藏架`。
- `Product/web/assets/app.js`：新增 `archivePageNotes`、`mountArchiveInspector()`、`updateArchiveInspector()`；右侧相邻笔记按钮通过 `data-inspector-view` 切换现有一级页面。
- `Product/web/assets/styles.css`：新增 archive interface layer；包含纸张网格背景、档案条目、证据 ledger、收藏架、hover、focus-visible、loading、empty、error 和响应式 inspector。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-archive1`

说明：Safari 可视化验收确认首页显示 `个人研究档案`、`本地证据`、右侧 `档案索引`、`相邻笔记`、`证据图例`、`收藏架`。点击右侧 `数据与设计` 后页面切换到变量角色集编辑器，右侧当前档案说明同步为 `数据与设计`。Browser/IAB 与 Playwright 本轮连接异常，已使用 Safari + Computer Use 作为可视化 fallback。
## 2026-05-13 P2-B Method Skill Catalog

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-method-skill-catalog-bdd.md`

### 新增/扩展测试

- `tests/test_method_skill_catalog.py`

### 新增/扩展后端能力

- `Product/backend/design_spec_service.py`：新增 RunPlan `method_catalog`、方法前置条件判断、`method_id` 规范化和默认 OLS baseline task。

### 新增/扩展前端能力

- `Product/web/index.html`：研究设计页新增 `method-skill-catalog-panel`，静态资源版本更新到 `20260513-p2b-clean`。
- `Product/web/assets/app.js`：新增 `renderMethodSkillCatalog()`、方法/要求状态文案映射和 RunPlan 读取。
- `Product/web/assets/styles.css`：新增方法技能集目录、状态标签、前置要求和阻塞原因样式；方法卡片使用纵向单列布局。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-p2b-clean`

说明：Safari + Computer Use 验收确认“工具：研究设计细节”页显示 `方法技能集`、`StatsPAI/CoPaper methodology index`、OLS/PSM/DML ready、DID/IV/RDD blocked 和对应阻塞原因；当前是 `local_file` 方法准入目录，不是 StatsPAI 真实执行。

## 2026-05-13 P2-D Method Execution Evidence UI

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-method-execution-ui-bdd.md`

### 新增/扩展测试

- `tests/test_observable_execution.py`
- `tests/test_observable_execution_frontend.py`
- `tests/test_results_draft_evidence_binding.py`

### 新增/扩展后端能力

- `Product/backend/observability_service.py`：读取 run manifest / `Results/json/method_execution_result.json`，在 run observability response 中暴露顶层 `method_execution`。
- `Product/backend/results_draft_service.py`：读取同一方法执行产物，在 results-draft response 中暴露顶层 `method_execution`，并为 FindingCard 增加 `method_evidence`。

### 新增/扩展前端能力

- `Product/web/index.html`：新增 `observable-method-execution` 面板，静态资源版本更新到 `20260513-p2d-method`。
- `Product/web/assets/app.js`：新增 `renderObservableMethodExecution()` 和 `renderFindingMethodEvidence()`，把方法、公式、样本量、处理变量系数、执行引擎和 artifact 路径渲染到页面。
- `Product/web/assets/styles.css`：新增方法执行证据面板、方法证据网格和 FindingCard 方法证据样式。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-p2d-method`

说明：Safari + Computer Use 验收确认“实证执行”页显示 `方法执行证据`、`python_ols_adapter`、`wage ~ trained + edu + experience`、样本量 `12`、处理变量系数 `1.8505`、`Results/json/method_execution_result.json`；“结果与草稿”页的结果论断卡也显示同一方法证据。

## 2026-05-13 P2-E OLS Evaluator Evidence

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-ols-evaluator-bdd.md`

### 新增/扩展测试

- `tests/test_ols_execution_adapter.py`
- `tests/test_results_draft_evidence_binding.py`

### 新增/扩展后端能力

- `Product/backend/project_service.py`：`python_ols_adapter` 现在生成 `standard_errors`、`t_statistics`、`p_values`、`p_value_method`、`confidence_intervals`、`diagnostics` 和 `evaluator`；新增 `fit_ols_model()`、`normal_two_sided_p_value()`、`round_significant()`、`build_ols_evaluator()`。
- `Product/backend/results_draft_service.py`：FindingCard 的 `method_evidence` 绑定 OLS evaluator 状态、标准误、p 值和置信区间。

### 新增/扩展前端能力

- `Product/web/index.html`：静态资源版本更新到 `20260513-p2e-eval2`。
- `Product/web/assets/app.js`：FindingCard 方法证据展示改为中文紧凑审阅摘要；新增/使用 evaluator 状态和置信区间展示。
- `Product/web/assets/styles.css`：新增 `method-evidence-summary`，移除 FindingCard 内部窄网格展示带来的拥挤。

### Runtime 产物

- `Results/json/method_execution_result.json`：最新真实运行写入 OLS 推断指标和 evaluator 结果。
- `state/runs/run_a3674e9e78c6/run_manifest.json`：最新 full run manifest，包含 `method_execution` artifact。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-p2e-eval`

说明：Safari + Computer Use 验收确认“结果与草稿”页结果论断卡显示 `ols · n=12 · β=1.8505 · 标准误=0.0755 · p=8.83e-133 · 95% 置信区间 1.7026 ~ 1.9984 · 评估器通过`，并绑定 `run_a3674e9e78c6`。

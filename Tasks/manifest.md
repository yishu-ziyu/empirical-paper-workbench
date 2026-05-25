# Manifest

## 长程状态文件

- `Tasks/todo.md`：当前任务状态机
- `Tasks/handoff.md`：跨 Session 接手说明
- `Tasks/decision-log.md`：关键决策与不要重复探索的理由
- `Tasks/manifest.md`：关键产物路径
- `Tasks/review.md`：验证、风险、未完成项
- `Tasks/round-log.md`：长程研发轮次账本，记录平台期、瓶颈、策略跃迁和证据路径

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

- `docs/architecture-v2/codex-phase-p2-auto-research-cli-bdd.md`
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
- `docs/architecture-v2/long-run-optimization-protocol.md`

## 新增/扩展 API

- CLI：`python3 Product/cli.py auto-research --topic "<研究题目>" --mode auto --max-depth 2 --max-iterations 5`
- `GET /api/v1/projects/{project_id}/runs/{run_id}/observability`
- `PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/dispatch-review` records human dispatch review for a queued Agent task.
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
- `GET /api/v1/projects/{project_id}/research-question/current` returns the current ResearchQuestion / TopicSession state, falling back to project seed without creating a state file.
- `PUT /api/v1/projects/{project_id}/research-question/current` persists the confirmed ResearchQuestion to `state/product/research_question.json`.
- `GET /api/v1/projects/{project_id}/overview` returns `research_question_state` and updates the ResearchQuestion canonical stage from that state.

## 新增/扩展前端能力

- `Product/web/index.html`：工作台首页恢复 topic-first 入口；`research-topic-intake` 负责输入/确认研究问题，`research-workbench-after-topic` 默认隐藏高噪声工作台细节。
- `Product/web/index.html`：Agent Console 移除主工作区重复详情面板，新增/保留右侧 `agent-detail-drawer` 作为唯一深层详情展开层。
- `Product/web/assets/app.js`：Agent 行支持 click / Enter / Space 打开 drawer；`openAgentDetail()`、`closeAgentDetailDrawer()`、`navigateToPrevAgent()`、`navigateToNextAgent()` 管理右侧抽屉。
- `Product/web/assets/app.js`：`renderAgentArtifactPreview()`、`openAgentArtifactPreview()` 为 drawer 内嵌产物预览提供 loading / empty / error 状态。
- `Product/web/assets/styles.css`：新增 `agent-detail-drawer`、`agent-row.is-active`、`agent-detail-preview-*` 样式。
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
- `Product/web/assets/app.js`：`v2api.researchQuestion.get/save` 读写 ResearchQuestion / TopicSession 状态。
- `Product/web/assets/app.js`：`confirmResearchTopic()` 保存首页选题到后端 ResearchQuestion API，再刷新 overview。
- `Product/web/assets/app.js`：`loadResearchQuestionState()` 让刷新后的页面从后端 confirmed state 恢复选题，而不是只依赖 localStorage。
- `Product/web/index.html`：CSS/JS 静态资源版本更新到 `?v=20260516-p2r-topic-session1`。
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

- `workspace/runs/run_20260524T172441Z_c063b7/`：P2-AB Auto Research CLI 手动验收生成的本地运行目录，包含 `run_manifest.json`、`research_report.md`、`paper_draft_exploratory.md`、候选变量/方法和文献线索。
- `journey-final-verify.png`：P2-AB 首页/工作台浏览器验收截图。
- `journey-agent-drawer-clean-verify.png`：P2-AB Agent drawer 浏览器验收截图，确认详情只在右侧抽屉展开。
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

## 2026-05-17 P2-V 新增关键产物

- `docs/architecture-v2/codex-phase-p2-dispatch-audit-bdd.md`
- `tests/test_agent_task_dispatch_audit.py`
- `Product/backend/task_dispatch_service.py`
- `Product/backend/agent_task_queue_service.py`
- `Product/app.py`
- `Product/web/assets/app.js`
- `Product/web/assets/styles.css`
- `state/product/agent_task_queue.json`：浏览器验收时生成的本地运行状态，gitignored，不提交。
- `/tmp/p2v-dispatch-audit.png`：浏览器自动化验收截图。

## 2026-05-17 Pipeline MVP Review 新增关键产物

- `Product/web/assets/app.js`：新增 `supervisorHumanReviewLabel()`，修复 approved SupervisorPlan 显示为未审批的问题；Review & Export 可通过稳定按钮 id 检查 docx 最终导出状态。
- `Product/web/index.html`：静态资源版本更新到 `20260517-pipeline-mvp-review`。
- `tests/test_supervisor_plan.py`：新增 approved SupervisorPlan 前端状态兼容测试。
- `tests/test_verifier_export_gates.py`：新增 `verifier-final-export-button` 静态契约测试。
- `artifacts/ui-checks/pipeline-mvp-home.png`
- `artifacts/ui-checks/pipeline-mvp-data-variables.png`
- `artifacts/ui-checks/pipeline-mvp-execution.png`
- `artifacts/ui-checks/pipeline-mvp-review-export.png`
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

## 2026-05-13 P2-F Real Data Candidate Pool

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-real-data-catalog-bdd.md`

### 新增/扩展测试

- `tests/test_external_data_catalog.py`

### 新增/扩展后端能力

- `Product/backend/overview_service.py`：`list_project_datasets()` 现在返回 `external_catalog`；新增 `build_external_data_catalog()`、`external_data_library_roots()`、`build_external_dataset_preview()`、`read_csv_preview_rows()` 和 `build_dataset_quality_profile_from_rows()`。
- 默认真实数据根目录：`/Users/mahaoxuan/Desktop/实证数据库`。
- 可覆盖环境变量：`EMPIRICAL_DATA_LIBRARY_ROOT`。

### 新增/扩展前端能力

- `Product/web/index.html`：数据与设计页新增 `external-data-library-panel`，静态资源版本更新到 `20260513-p2f-realdata2`。
- `Product/web/assets/app.js`：新增 `renderExternalDataLibrary()`、`renderExternalDatasetCard()`、`formatBytes()`；首屏只显示 6 个真实候选文件，并显示总数。
- `Product/web/assets/styles.css`：新增真实数据候选池、候选数据卡、只读说明和响应式布局样式。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-p2f-realdata2`

说明：点击“数据与设计”，可见 `真实数据候选池`，计数 `223`，根目录 `/Users/mahaoxuan/Desktop/实证数据库`，前 6 个 CFPS 候选文件显示 `本地文件`、文件大小、`尚未画像` 和 `只读`；下方项目内数据仍显示 `analysis_sample.csv`，两者没有混同。

## 2026-05-14 P2-G Real Dataset Bind Preflight

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-dataset-bind-preflight-bdd.md`

### 新增/扩展测试

- `tests/test_external_dataset_bind_preflight.py`

### 新增/扩展后端能力

- `Product/backend/overview_service.py`：新增 `save_external_dataset_bind_preflight()`、`build_external_dataset_bind_preflight()`、`validate_external_source_path()`、`build_dataset_preflight_id()`、`latest_external_import_preflight()`、`load_dataset_import_preflight_manifest()`、`write_dataset_import_preflight_manifest()`。
- `Product/app.py`：新增 `ExternalDatasetBindPreflightPayload` 和 `POST /api/v1/projects/{project_id}/datasets/external-bind-preflight`。
- Runtime manifest：`state/product/dataset_import_preflights.json`，记录预检对象；不提交为源码，不代表真实导入完成。

### 新增/扩展前端能力

- `Product/web/index.html`：数据与设计页新增 `external-bind-preflight-panel`，静态资源版本更新到 `20260513-p2g-bind1`。
- `Product/web/assets/app.js`：新增 `v2api.datasets.bindPreflight()`、`requestExternalBindPreflight()`、`renderExternalBindPreflight()`；候选数据卡新增 `data-external-bind-preflight-action`。
- `Product/web/assets/styles.css`：新增导入/绑定预检面板、检查清单和说明样式。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260513-p2g-bind1`

说明：点击“数据与设计”，在“真实数据候选池”中点击候选文件的“生成导入/绑定预检”，页面显示 `待人工确认`、真实源路径、目标 `Data/Raw/<filename>`、策略 `copy_to_project_raw`、`尚未导入/绑定 · 源文件只读` 和 4 项通过检查。

## 2026-05-14 P2-H Real Dataset Import Apply

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-dataset-import-apply-bdd.md`

### 新增/扩展测试

- `tests/test_external_dataset_import_apply.py`

### 新增/扩展后端能力

- `Product/backend/overview_service.py`：新增 `apply_external_dataset_bind_preflight()`、`file_sha256()`、`CloudUploadRequiredError`、`DatasetPreflightStateError`；apply 会更新 `state/product/dataset_import_preflights.json` 中的预检状态和 `dataset_import` 记录。
- `Product/app.py`：新增 `ExternalDatasetPreflightApplyPayload` 和 `POST /api/v1/projects/{project_id}/datasets/external-bind-preflight/{preflight_id}/apply`。
- 支持动作：`copy_to_project_raw`、`bind_external_reference`、`cancel`。
- 云端边界：`runtime_mode=cloud` 返回 `cloud_upload_required`，提示必须上传或使用云对象。

### 新增/扩展前端能力

- `Product/web/index.html`：静态资源版本更新到 `20260514-p2h-import1`。
- `Product/web/assets/app.js`：新增 `v2api.datasets.applyPreflight()`、`requestExternalPreflightApply()`、三类 apply 按钮和导入结果回显。
- `Product/web/assets/styles.css`：新增 `.preflight-action-row`、`.external-import-result`。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260514-p2h-import1`

说明：点击“数据与设计”，在“导入/绑定预检”面板中可见 `确认导入到项目`、`只绑定引用`、`取消预检`。点击 `只绑定引用` 后，页面显示 `已接入`、`已绑定外部引用`、`动作：只绑定引用 · 模式：local`、目标 `Data/Raw/...` 和 SHA256。

## 2026-05-14 P2-I Dataset Import Field Profile

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-dataset-import-profile-bdd.md`

### 新增/扩展测试

- `tests/test_external_dataset_import_profile.py`

### 新增/扩展后端能力

- `Product/backend/overview_service.py`：新增 `DatasetImportProfileStateError`、`DatasetImportSourceChangedError`、`profile_external_dataset_import()`、`resolve_dataset_import_profile_path()`、`expected_dataset_import_hash()`、`build_dataset_import_profile()`、`latest_external_import_profile()`。
- `Product/app.py`：新增 `DatasetImportProfilePayload` 和 `POST /api/v1/projects/{project_id}/datasets/imports/{dataset_import_id}/profile`。
- Runtime manifest：`state/product/dataset_import_preflights.json` 中新增 `dataset_import_profiles`、`latest_import_profile_id`，并在 `dataset_import.field_profile` 中记录画像摘要。

### 新增/扩展前端能力

- `Product/web/index.html`：数据与设计页新增 `dataset-import-profile-panel`，静态资源版本更新到 `20260514-p2i-profile1`。
- `Product/web/assets/app.js`：新增 `v2api.datasets.profileImport()`、`requestExternalImportProfile()`、`renderDatasetImportProfile()`，并在已接入结果中显示“生成字段画像”。
- `Product/web/assets/styles.css`：新增字段画像面板、字段表、阻塞提示和检查项样式。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260514-p2i-profile1`

说明：点击“数据与设计”，在“导入/绑定预检”已接入结果中点击“生成字段画像”。当前真实 CFPS `.dta` 绑定会显示 `暂未画像`、`dta 暂未接入安全字段读取器。`、`fields=0` 和 `不会改写 VariableRoleSet、DesignSpec 或 RunPlan`；CSV 在测试夹具中会返回字段表。

## 2026-05-14 P2-J Stata DTA Field Profile

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-dta-field-profile-bdd.md`

### 新增/扩展测试

- `tests/test_external_dataset_import_profile.py`：新增有效 DTA metadata-only 画像、损坏 DTA 阻塞画像、前端变量标签/Stata 类型展示约束。

### 新增/扩展后端能力

- `Product/backend/overview_service.py`：新增 `build_dta_metadata_profile()`、`blocked_dta_metadata_profile()`、`infer_stata_field_type()`；`build_dataset_import_profile()` 现在支持 `.dta` metadata-only 字段画像。
- 可选依赖：`pyreadstat`。当前本机已安装；缺失时服务返回 blocked 画像而不是 500。

### 新增/扩展前端能力

- `Product/web/index.html`：静态资源版本更新到 `20260514-p2j-dta1`。
- `Product/web/assets/app.js`：字段画像表显示 `字段 / 变量标签 / Stata 类型 / 缺失率`。
- `Product/web/assets/styles.css`：字段画像表列宽按变量字典优化，并取消自动大写表头。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260514-p2j-dta1`
- 截图证据：`/tmp/empirical-workbench-p2j-dta-profile.png`

说明：点击“数据与设计”，在“字段画像 / 变量字典预览”面板可见 `cfps2011adult_202202(1).dta`、`已画像`、`1279 行 · 723 列 · row_limit=200`、`metadata-only 字段画像，未读取完整数据表`，字段表显示 `pid / 个人id / double`、`fid / 家户号 / double` 等真实 Stata 变量字典。

## 2026-05-14 P2-K Rigorous Empirical Execution Contract

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-rigorous-empirical-execution-bdd.md`

### 新增/扩展测试

- `tests/test_ols_execution_adapter.py`
- `tests/test_observable_execution_frontend.py`

### 新增/扩展后端能力

- `Product/backend/project_service.py`：新增 `build_empirical_execution_contract()`、`read_numeric_formula_rows_with_preflight()`、`build_ols_reproducibility()`。
- `method_execution_result.json` 现在包含：
  - `execution_contract.active_backend=python_ols_adapter`
  - `execution_contract.available_backends[]`，列出 Python、StatsPAI/StatsAPI、StataMCP/Stata 的角色、可用性和证据等级。
  - `data_preflight`，记录读取行数、可用数值行、丢弃行数、必需字段和预检结果。
  - `reproducibility`，记录 run_id、公式、RunPlan/DesignSpec 版本、结果文件路径和源码入口。

### 新增/扩展前端能力

- `Product/web/assets/app.js`：新增 `renderMethodExecutionContract()`、`renderMethodDataPreflight()`、`renderMethodReproducibility()`。
- `Product/web/assets/styles.css`：新增严谨执行契约、候选后端、数据预检和可复现入口样式，并修复 Execution 页面可见溢出。
- `Product/web/index.html`：静态资源版本更新到 `20260514-p2k-rigorous1`。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260514-p2k-rigorous4`
- 截图证据：`/tmp/empirical-workbench-p2k-rigorous-execution.png`

说明：点击“实证执行”，查看“方法执行证据”下的“严谨执行契约”“数据预检”“可复现入口”。页面应显示当前执行后端 `python_ols_adapter`，候选后端 StatsPAI/StatsAPI 与 StataMCP/Stata，数据预检 `12 / 12 / 0`，以及源码入口 `Product/backend/project_service.py::execute_ols_task`。

## 2026-05-14 P2-L Variable Role Candidate Review

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-variable-role-candidate-review-bdd.md`

### 新增/扩展测试

- `tests/test_variable_role_candidates.py`

### 新增/扩展后端能力

- `Product/backend/variable_role_service.py`：新增变量角色候选状态机，支持从已画像 dataset import 生成 `VariableRoleCandidate`，并支持 `approve_candidate`、`request_changes`、`reject_candidate` 三类 review 动作。
- `Product/app.py`：新增候选列表、候选生成和候选 review API。
- Runtime 状态：`state/product/variable_role_candidates.json`，记录 candidate、latest candidate、review events 和 `does_not_mutate_variable_role_set=true`。

### 新增/扩展前端能力

- `Product/web/index.html`：数据与设计页新增 `variable-role-candidate-panel`，静态资源版本更新到 `20260515-p2l-candidates1`。
- `Product/web/assets/app.js`：新增 `v2api.variableRoleCandidates`、`renderVariableRoleCandidateReview()`、`generateVariableRoleCandidate()`、`reviewVariableRoleCandidate()`。
- `Product/web/assets/styles.css`：新增候选审阅面板、候选字段表、角色摘要和 review 按钮布局。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260515-p2l-candidates1`

说明：点击“数据与设计”，在“字段审阅”面板点击“生成变量角色候选”，页面应显示 `待人工审阅`、`不会写入正式变量角色集`、候选 outcome/treatment/controls/instruments 和候选字段表。点击“候选已确认”后，按钮状态变为 `候选已确认`，但正式 `state/product/variable_roles.json` 的哈希与 mtime 不变。

## 2026-05-14 P2-M Candidate Promotion to Formal VariableRoleSet

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-variable-role-candidate-promote-bdd.md`

### 新增/扩展测试

- `tests/test_variable_role_candidates.py`：新增未确认候选禁止写回、已确认候选可带编辑结果写回、前端必须把 candidate 载入正式编辑器的行为约束。

### 新增/扩展后端能力

- `Product/backend/variable_role_service.py`：
  - 新增 `VariableRoleCandidateApprovalRequiredError`。
  - `save_project_variable_roles()` 支持 `candidate_id`。
  - 从 candidate 保存时保留 `candidate_id`、`dataset_import_id`、`dataset_import_profile_id`、`source`、`binding`、`provenance`。
  - 保存成功后把 candidate 标记为 `applied_to_variable_roles`，并记录写入的 VariableRoleSet version。
- `Product/app.py`：
  - `VariableRolePayload` 新增 `candidate_id`。
  - `POST /api/v1/projects/{project_id}/variable-roles` 现在能处理 candidate 写回，并对未确认候选返回 409。

### 新增/扩展前端能力

- `Product/web/assets/app.js`：
  - 新增 `state.pendingVariableRoleCandidateId`。
  - 字段审阅卡片新增 `载入正式编辑器`。
  - `loadVariableRoleCandidateIntoEditor()` 把 approved candidate 的真实数据路径、角色候选、candidate id 和说明载入正式变量角色编辑器。
  - 保存变量角色集时携带 `candidate_id`，保存后刷新候选、变量角色和 overview。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260514-p2m`

说明：点击“数据与设计”，在“字段审阅”面板找到已确认候选，点击“载入正式编辑器”。编辑器应显示 `draft_from_candidate · local_file`、真实 CFPS DTA 路径、`candidate_id=...`、结果变量/控制变量候选和说明“保存后才写入正式变量角色集”。本轮未点击最终保存，避免覆盖演示项目的已批准变量角色。

## 2026-05-14 P2-N StatsPAI Independent OLS Validation

### 新增/扩展文档

- `docs/architecture-v2/codex-phase-p2-statspai-execution-validation-bdd.md`

### 新增/扩展测试

- `tests/test_ols_execution_adapter.py`
- `tests/test_observable_execution_frontend.py`

### 新增/扩展后端能力

- `Product/backend/project_service.py`：新增 `execute_statspai_ols_validation()`、`write_json_artifact()`、`statspai_series_to_float_dict()`、`json_safe_value()`。
- full run 的 `method_execution` 现在包含 `backend_validations`。
- StatsPAI 可用且数据为 CSV 时写出 `Results/json/statspai_execution_result.json`。

### 新增/扩展前端能力

- `Product/web/assets/app.js`：新增 `renderMethodBackendValidations()`。
- `Product/web/assets/styles.css`：新增 `.method-validation-list`、`.method-validation-item`。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260514-p2n-supervisor1`

说明：进入“实证执行”，点击“启动完整实证执行”。最终 API 复核 run `run_bb423547439c` 的 observability 中，方法执行证据包含 `独立后端验证`、`passed`、`statspai.regress`、`Results/json/statspai_execution_result.json`。

## 2026-05-14 P2-O LLM Supervisor Readiness Contract

### 新增/扩展测试

- `tests/test_product_workflow_contract.py`

### 新增/扩展后端能力

- `Product/backend/overview_service.py`：新增 `build_intelligence_layer_contract()`，并把 `intelligence_layer` 写入 `workflow_contract`。
- 依赖已有 `Product/app.py` / provider endpoint 的 `local_codex_status()`。

### 新增/扩展前端能力

- `Product/web/index.html`：首页新增 `llm-supervisor-panel`，静态资源版本更新到 `20260514-p2n-supervisor1`。
- `Product/web/assets/app.js`：新增 `renderIntelligenceLayer()`，在 `renderWorkflowContract()` 中渲染智能中控状态。
- `Product/web/assets/styles.css`：新增 `.llm-supervisor-panel`、`.llm-supervisor-card`、`.llm-provider-grid`、`.llm-dispatch-plan`。

### 手动验收入口

- `http://127.0.0.1:8765/?v=20260514-p2n-supervisor1`

说明：进入“工作台首页”，应显示“智能中控”“本地 Codex Supervisor 未启用”、`provider=local_codex`、`可用=是`、`允许执行=否`、`local_codex_execution_not_enabled` 和阶段派工计划。

## 2026-05-16 P2-P Local Codex SupervisorPlan

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-supervisor-plan-bdd.md`
- `tests/test_supervisor_plan.py`

### 新增/扩展后端能力

- `Product/backend/supervisor_plan_service.py`：生成、读取、规范化并持久化 `SupervisorPlan`。
- `Product/backend/codex_provider.py`：新增 `run_local_codex_prompt()`，用于把任意 prompt 交给本地 Codex 并读取输出文件。
- `Product/app.py`：新增 `SupervisorPlanPayload`、`GET /api/v1/projects/{project_id}/supervisor-plan`、`POST /api/v1/projects/{project_id}/supervisor-plan`。

### 新增/扩展前端能力

- `Product/web/index.html`：首页新增 `supervisor-plan-panel`，静态资源版本更新到 `20260516-p2p-supervisor-plan`。
- `Product/web/assets/app.js`：新增 `v2api.supervisorPlan.get/generate`、`renderSupervisorPlan()`、`handleGenerateSupervisorPlan()`。
- `Product/web/assets/styles.css`：新增 `.supervisor-plan-panel`、`.supervisor-plan-card`、`.supervisor-plan-grid` 等审阅台样式。

### 新增运行时产物契约

- `state/product/supervisor_plan.json`：真实生成后保存 normalized SupervisorPlan，`evidence_level=local_execution`、`status=needs_review`。
- `state/product/supervisor_plan.raw.md`：保存本地 Codex 原始输出，供解析失败或审计时追溯。
- `artifacts/ui-checks/p2p-supervisor-plan-overview.png`：本轮 headless Chrome 可视化验收截图。

### 手动验收入口

- `http://127.0.0.1:8767/?v=20260516-p2p-supervisor-plan`

说明：首页应显示 `SupervisorPlan 审阅台`、`生成 SupervisorPlan`、`本地 Codex SupervisorPlan`。默认环境未设置 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`，点击生成或调用 POST 应返回 409 `local_codex_execution_not_enabled`，不会写入 `state/product/supervisor_plan.json`。

## 2026-05-16 P2-P1 Home Progressive Disclosure

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-home-progressive-disclosure-bdd.md`
- `tests/test_supervisor_plan.py`：新增 SupervisorPlan 审阅台默认折叠行为。
- `tests/test_product_workflow_contract.py`：新增智能中控默认折叠行为。

### 新增/扩展前端能力

- `Product/web/index.html`：静态资源版本更新到 `20260516-p2p-disclosure1`。
- `Product/web/assets/app.js`：`renderIntelligenceLayer()` 和 `renderSupervisorPlan()` 改为首屏摘要 + `details/summary` 按需展开。
- `Product/web/assets/styles.css`：新增 `.progressive-disclosure`、`.disclosure-panel`、`.decision-signal-row`，保留键盘 focus 状态。

### 新增验收产物

- `artifacts/ui-checks/p2p-home-progressive-disclosure.png`：右侧内置浏览器点击展开后的可视化验收截图。

### 手动验收入口

- `http://127.0.0.1:8767/?v=20260516-p2p-disclosure1`

说明：打开“工作台首页”，智能中控与 SupervisorPlan 先只显示摘要。点击 `查看中控详情` 后可看到 Provider、执行开关、阻塞项和派工计划；点击 `查看计划详情` 后可看到版本、写入边界、阶段计划、子 Agent 分工、证据要求和风险。

## 2026-05-16 P2-Q Topic-first Home

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-topic-first-home-bdd.md`
- `tests/test_product_workflow_contract.py`：新增首页选题入口、工作台默认隐藏、真实数据候选入口契约。

### 新增/扩展前端能力

- `Product/web/index.html`：静态资源版本更新到 `20260516-p2q-topic1`；首页新增 `research-topic-intake`，原工作台区域包进 `research-workbench-after-topic`。
- `Product/web/assets/app.js`：新增选题状态、localStorage key、确认选题、使用已有选题、跳转数据候选页和确认后滚动到研究判断区。
- `Product/web/assets/styles.css`：新增 topic intake、topic form、确认态、工作台隐藏态和窄视口降噪样式。

### 手动验收入口

- `http://127.0.0.1:8767/?v=20260516-p2q-topic1`

说明：首页默认应先显示 `开始一项实证研究`、选题输入框、`进入研究判断`、`从已有选题继续`、`从真实数据候选池开始`。确认选题前不显示下一步研究决策和 SupervisorPlan 细节；确认后才展开研究判断区。

## 2026-05-16 P2-S SupervisorPlan Topic Binding

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-supervisor-plan-topic-binding-bdd.md`
- `tests/test_supervisor_plan.py`：新增 ResearchQuestion 必填、prompt 绑定、输入证据和前端展示测试。

### 新增/扩展后端能力

- `Product/backend/supervisor_plan_service.py`：
  - 生成前读取 `state/product/research_question.json`。
  - 缺少 confirmed ResearchQuestion 时返回 `research_question_required`。
  - Codex prompt 增加 `confirmed_research_question`。
  - `supervisor_plan.json` 增加 `input_research_question`、`research_question_version` 和 `research_question_path`。

### 新增/扩展前端能力

- `Product/web/assets/app.js`：SupervisorPlan 审阅台显示 `绑定选题`、`TopicSession`、`ResearchQuestion 版本`。
- `Product/web/index.html`：静态资源版本更新到 `20260516-p2s-supervisor-topic1`。

### 手动验收入口

- `http://127.0.0.1:8767/?v=20260516-p2s-supervisor-topic1`

说明：在已有 confirmed ResearchQuestion 的项目中，SupervisorPlan 审阅台应显示绑定选题；展开详情后应显示 TopicSession 和 ResearchQuestion 版本。默认未启用本地 Codex 执行时，点击生成仍应被 `local_codex_execution_not_enabled` 阻断。

### 新增验收产物

- `artifacts/ui-checks/p2s-supervisor-topic-binding.png`

## 2026-05-16 P2-T SupervisorPlan Review State Machine

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-supervisor-plan-review-bdd.md`
- `tests/test_supervisor_plan.py`：新增 approve / needs_revision / reject、缺失计划、非法 action、不可篡改研究状态和前端按钮契约。

### 新增/扩展后端能力

- `Product/backend/supervisor_plan_service.py`：
  - 新增 `review_project_supervisor_plan()`。
  - 新增 `InvalidSupervisorPlanReviewActionError`。
  - 审批动作写入 `status`、`human_review`、`can_dispatch`、`next_action` 和 `decision_events`。
  - 审批只保存 `state/product/supervisor_plan.json`。
- `Product/app.py`：
  - 新增 `SupervisorPlanReviewPayload`。
  - 新增 `PUT /api/v1/projects/{project_id}/supervisor-plan/review`。
  - 缺少计划返回 409 `supervisor_plan_required`；非法 action 返回 400 `invalid_supervisor_plan_review_action`。

### 新增/扩展前端能力

- `Product/web/assets/app.js`：新增 `v2api.supervisorPlan.review()`、`handleReviewSupervisorPlan()`、审批按钮和派工状态显示。
- `Product/web/assets/styles.css`：新增 `.supervisor-plan-review-bar` 和 `.supervisor-plan-review-actions`；保持单列 clean workbench 布局，避免窄视口文字重叠。

### 手动验收入口

- `http://127.0.0.1:8767/?v=20260516-p2t-supervisor-review1`

说明：当前真实项目还没有 `state/product/supervisor_plan.json`，所以页面正确显示 `尚未生成` 和 `生成 SupervisorPlan`。生成计划后，审阅台会出现 `批准计划`、`要求修改`、`驳回计划`；只有批准后的计划显示 `可进入任务队列`。

### 新增验收产物

- `artifacts/ui-checks/p2t-supervisor-review-page.png`

## 2026-05-17 P2-U Agent Task Queue

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-agent-task-queue-bdd.md`
- `tests/test_agent_task_queue.py`

### 新增/扩展后端能力

- `Product/backend/agent_task_queue_service.py`：
  - 新增 `get_project_agent_task_queue()`。
  - 新增 `create_project_agent_task_queue()`。
  - 新增 `AgentTaskQueueBlockedError`。
  - 新增运行时状态文件契约 `state/product/agent_task_queue.json`。
- `Product/app.py`：
  - 新增 `AgentTaskQueuePayload`。
  - 新增 `GET /api/v1/projects/{project_id}/agent-task-queue`。
  - 新增 `POST /api/v1/projects/{project_id}/agent-task-queue`。

### 新增/扩展前端能力

- `Product/web/index.html`：首页新增 `agent-task-queue-panel` 和 `agent-task-queue-body`。
- `Product/web/assets/app.js`：
  - 新增 `state.agentTaskQueueData` 和 `state.creatingAgentTaskQueue`。
  - 新增 `v2api.agentTaskQueue.get/create`。
  - 新增 `renderAgentTaskQueue()`、`renderAgentTaskQueueItem()`、`handleCreateAgentTaskQueue()`。
  - 首页加载 overview 时同步读取 Agent Task Queue。
- `Product/web/assets/styles.css`：新增 `.agent-task-queue-*`、`.agent-task-item`、`.agent-task-detail-grid`，保持摘要优先和详情折叠布局。

### 新增运行时产物契约

- `state/product/agent_task_queue.json`：仅由 approved SupervisorPlan 生成，`evidence_level=local_file`，记录 source SupervisorPlan、summary、tasks、blockers、ui_contract 和 next_action。

### 手动验收入口

- `http://127.0.0.1:8768/?v=20260517-p2u-final-browser`

说明：当前真实项目没有 approved `state/product/supervisor_plan.json`，所以页面正确显示 `缺少 SupervisorPlan` 且 `创建 Agent 任务队列` 按钮 disabled。受控 approved-plan 浏览器验收截图保存到 `/tmp/empirical-workbench-agent-task-queue-p2u-approved.png`，显示 2 个任务、详情默认折叠。

### 新增验收产物

- `/tmp/empirical-workbench-agent-task-queue-p2u-final.png`
- `/tmp/empirical-workbench-agent-task-queue-p2u-approved.png`

## 2026-05-17 P2-W Real VariableRoleCandidate Promotion

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-real-variable-role-promotion-bdd.md`
- `tests/test_real_variable_role_promotion.py`

### 新增/扩展后端能力

- `Product/backend/variable_role_service.py`：
  - 新增 `VARIABLE_ROLE_DRAFT_PATH = state/product/variable_roles_drafts.json`。
  - 新增 `promote_project_variable_role_candidate()`，把 approved candidate 转成 `variable_role_set_draft`。
  - 新增 draft state 读写和 `mark_variable_role_draft_applied()`。
  - 正式 `PUT /variable-roles` 保存时会记录 `source_variable_roles_draft_id` 和 `variable_roles_draft_path` provenance。
- `Product/app.py`：
  - 新增 `VariableRoleCandidatePromotePayload`。
  - 新增 `POST /api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/promote`。

### 新增/扩展前端能力

- `Product/web/assets/app.js`：
  - 新增 `v2api.variableRoleCandidates.promote()`。
  - 新增 `promoteVariableRoleCandidate(candidateId)`。
  - 候选卡新增 `data-promote-variable-candidate-action`。
  - 正式编辑器显示 `正式变量角色`，并保留旧的 `仅载入编辑器` 路径。
- `Product/web/assets/styles.css`：
  - 新增 `.variable-role-draft` 视觉边界。

### 新增运行时产物契约

- `state/product/variable_roles_drafts.json`：promotion 后写入，记录 `pending_variable_roles_draft`、`latest_draft_id`、draft roles、source candidate、source dataset 和 decision events；gitignored，不提交。

### 手动验收入口

- `http://127.0.0.1:8768/?v=20260517-p2w-real-variable-promotion`

说明：页面应同时显示 `候选建议` 和 `正式变量角色`。点击 `基于候选创建变量角色草稿` 后，只创建草稿并把内容载入正式编辑器；只有再点击保存正式变量角色，才会改写 `state/product/variable_roles.json`。

### 新增验收产物

- `/tmp/p2w-real-variable-promotion-clean.png`

## 2026-05-17 P2-X Method Workflow Checklist

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-method-workflow-checklist-bdd.md`
- `tests/test_method_workflow_checklist.py`
- `tests/test_ols_execution_adapter.py`：blocked IV 现在在 RunPlan approval 阶段被拒绝。

### 新增/扩展后端能力

- `Product/backend/method_workflow_service.py`：
  - 新增 `get_project_method_workflows()`。
  - 新增 `assert_run_plan_methods_ready()`。
  - 新增 `MethodWorkflowBlockedError`。
  - 生成 OLS/DID/IV/RDD/PSM/DML 的 readiness、required inputs、diagnostics、blockers、evidence binding。
- `Product/backend/design_spec_service.py`：
  - `save_project_run_plan()` 保存前执行方法工作流准入检查。
  - blocked 方法返回 `method_workflow_blocked`，不写入 `state/product/run_plan.json`。
- `Product/app.py`：
  - 新增 `GET /api/v1/projects/{project_id}/method-workflows`。
  - `PUT /api/v1/projects/{project_id}/run-plan` 对 `MethodWorkflowBlockedError` 返回 409，并在 `details.blocked_methods` 中说明原因。

### 新增/扩展前端能力

- `Product/web/index.html`：Research Design 与 Execution 页面新增 `method-workflow-panel`。
- `Product/web/assets/app.js`：
  - 新增 `state.methodWorkflowsData`。
  - 新增 `v2api.methodWorkflows.get()`。
  - 新增 `renderMethodWorkflows()` 和 `renderMethodWorkflowsBody()`。
  - 保存 DesignSpec/RunPlan 后刷新方法工作流。
- `Product/web/assets/styles.css`：新增 `.method-workflow-*` 和折叠详情样式。

### API 契约

- `GET /api/v1/projects/{project_id}/method-workflows`
- `PUT /api/v1/projects/{project_id}/run-plan` blocked response：
  - status: `409`
  - code: `method_workflow_blocked`
  - details: `blocked_methods[]`

### 手动验收入口

- `http://127.0.0.1:8768/?v=20260517-p2x-method-workflow`

说明：Research Design 页面显示 `OLS：可执行`、`DID：缺少时间变量、处理时点`、`IV：缺少工具变量`、`RDD：缺少断点运行变量`、`PSM：可预检`、`DML：可预检`；`查看方法要求` 默认折叠，点击后显示前置条件、诊断和阻塞原因。

### 新增验收产物

- `/tmp/p2x-method-workflow.png`

## 2026-05-17 P2-Y Reviewer Scorecard

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-reviewer-scorecard-bdd.md`
- `tests/test_reviewer_scorecard.py`

### 新增/扩展后端能力

- `Product/backend/reviewer_score_service.py`：
  - 新增 `get_project_reviewer_scorecard()`。
  - 新增 `generate_project_reviewer_scorecard()`。
  - 新增 `state/product/reviewer_scorecard.json` 状态文件契约。
  - 从 `get_project_results_draft()` 读取 latest run、FindingCard 和 draft evidence，生成五维 `deterministic_baseline` scorecard。
- `Product/app.py`：
  - 新增 `ReviewerScorecardPayload`。
  - 新增 `GET /api/v1/projects/{project_id}/reviewer-scorecard`。
  - 新增 `POST /api/v1/projects/{project_id}/reviewer-scorecard`。

### 新增/扩展前端能力

- `Product/web/index.html`：Review & Export 页面新增 `reviewer-scorecard-panel`。
- `Product/web/assets/app.js`：
  - 新增 `state.reviewerScorecardData`。
  - 新增 `v2api.reviewerScorecard.get/generate`。
  - 新增 `renderReviewerScorecard()` 和 `renderReviewerScorecardRow()`。
  - 新增 `generateReviewerScorecard()` 和 `acceptReviewerTaskSuggestion()`。
- `Product/web/assets/styles.css`：新增 `.reviewer-scorecard-*` 样式，保持摘要优先和 details 折叠详情。

### API 契约

- `GET /api/v1/projects/{project_id}/reviewer-scorecard`
- `POST /api/v1/projects/{project_id}/reviewer-scorecard`
- 无 successful full run 时返回 409 `full_run_required`。

### 手动验收入口

- `http://127.0.0.1:8768/?v=20260517-p2y-reviewer-scorecard`

### 新增验收产物

- `/tmp/p2y-reviewer-scorecard.png`

## 2026-05-17 P2-Z Verifier Gates For Results, Manuscript, And Export

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-verifier-export-gates-bdd.md`
- `tests/test_verifier_export_gates.py`

### 新增/扩展后端能力

- `Product/backend/verifier_service.py`：
  - 新增 `get_project_verifier_checks()`。
  - 新增 `run_project_verifier_checks()`。
  - 新增 `state/product/verifier_checks.json` 状态文件契约。
  - 核验 export candidate、result binding、repro manifest、run plan artifact、analysis result artifact、method execution artifact、draft preview、evidence levels 和 docx export preflight。
- `Product/app.py`：
  - 新增 `GET /api/v1/projects/{project_id}/verifier-checks`。
  - 新增 `POST /api/v1/projects/{project_id}/verifier-checks/run`。
  - 无 export candidate 时返回 409 `export_candidate_required`。

### 新增/扩展前端能力

- `Product/web/index.html`：Review & Export 页面新增 `verifier-gate-panel`，位置在 Reviewer Scorecard 和 Export Package Workbench 之间。
- `Product/web/assets/app.js`：
  - 新增 `state.verifierChecksData` 和 `state.runningVerifierChecks`。
  - 新增 `v2api.verifierChecks.get/run`。
  - 新增 `renderVerifierGates()`、`verifierCheckStatusText()`、`runVerifierChecks()`。
  - `docx 最终导出` 按钮只读取 `can_export_docx`，不能从 export package 是否存在推断。
- `Product/web/assets/styles.css`：新增 `.verifier-gate-*` 样式，保持摘要优先、失败项明确、最终导出动作受控。

### API 契约

- `GET /api/v1/projects/{project_id}/verifier-checks`
- `POST /api/v1/projects/{project_id}/verifier-checks/run`
- `status`：`passed`、`blocked`、`failed`。
- `can_export_docx=false` 时最终 docx 导出按钮必须 disabled。

### 手动验收入口

- `http://127.0.0.1:8768/?v=20260517-p2z-verifier-gates`

### 新增验收产物

- `/tmp/p2z-verifier-gates.png`

## 2026-05-25 P2-AB Topic-first Auto Research CLI

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p2-auto-research-cli-bdd.md`
- `tests/test_auto_research_cli.py`

### 新增/扩展后端能力

- `Product/backend/auto_research_service.py`：
  - 新增 `run_auto_research()`。
  - 创建 `workspace/runs/{run_id}` 运行目录。
  - 写入 `00_intake/research_intent.json`、`01_sources/recursive_search_plan.json`、`02_literature/literature_clues.jsonl`、`03_strategy/variable_candidates.json`、`03_strategy/method_candidates.json`、`03_strategy/evidence_gaps.json`、`06_writing/research_report.md`、`06_writing/paper_draft_exploratory.md` 和 `run_manifest.json`。
  - 写入全局候选池 `state/orchestration/literature_clues.jsonl`。
  - 记录 `local_data`、`statspai`、`cnki`、`web_search`、`agentmemory`、`llm_supervisor` 的能力状态。
- `Product/backend/registry.py`：
  - 新增 `get_project_by_id_or_transient()`，让临时本地项目可以走治理层但不污染全局项目 registry。
- `Product/backend/identity_service.py`、`Product/backend/permission_service.py`、`Product/backend/capability_registry.py`、`Product/backend/cost_service.py`：
  - 改用 transient runtime project 解析，支持 CLI 对未注册本地项目执行。

### 新增/扩展 CLI 能力

- `Product/cli.py`：
  - 新增 `auto-research` 子命令。
  - 关键参数：`--project-root`、`--topic`、`--mode auto|dry-run`、`--max-depth`、`--max-iterations`。

### 手动验收入口

- `python3 Product/cli.py auto-research --topic "人工智能是否影响劳动收入差距" --mode auto --max-depth 2 --max-iterations 5`

### 预期输出

- CLI stdout 返回 JSON manifest。
- 本地运行目录：`workspace/runs/{run_id}`。
- 所有自动生成研究产物均为 `exploratory` / `draft` / `needs_human_review`，`can_promote=false`。

## 2026-05-25 P3 React Input And Slide Tabs

### 新增/扩展设计与测试

- `docs/architecture-v2/codex-phase-p3-react-input-tabs-bdd.md`
- `tests/test_p3_react_input_tabs.py`

### 新增 React 前端入口

- `Product/web-react/package.json`
- `Product/web-react/package-lock.json`
- `Product/web-react/index.html`
- `Product/web-react/vite.config.ts`
- `Product/web-react/tsconfig.json`
- `Product/web-react/src/main.tsx`
- `Product/web-react/src/App.tsx`
- `Product/web-react/src/lib/cn.ts`
- `Product/web-react/src/components/ResearchCommandInput.tsx`
- `Product/web-react/src/components/SlideTabs.tsx`
- `Product/web-react/src/components/DottedSurface.tsx`
- `Product/web-react/src/styles.css`

### 构建产物与预览入口

- `Product/web-dist/index.html`
- `Product/web-dist/assets/`
- `Product/app.py`：新增 `/react` 与 `/react/` 预览入口；构建 assets 存在时挂载 `/react/assets`。

### 手动验收入口

- `python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8769`
- `http://127.0.0.1:8769/react/`

### 验收截图

- `artifacts/ui-checks/p3-react-input-tabs.png`
- `artifacts/ui-checks/p3-react-dotted-surface.png`

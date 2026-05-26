# Todo

## 2026-05-26 North Star：CLI-first Real Empirical Flow + Journal Skill Registry

- [x] 明确主线：先把本地 CLI 高效工作流跑通，再把同一套状态和证据模型接到云端产品。
- [x] 新增北极星计划：`docs/architecture-v2/north-star-cli-first-research-os-plan-2026-05-26.md`。
- [x] 新增真实数据 CLI 行为文档：`docs/architecture-v2/codex-phase-p2-real-data-cli-full-run-bdd.md`。
- [x] 让 `Program/run_paper.py` 支持 `--paper-config`，避免真实数据运行覆盖默认 `paper.yaml` 输出。
- [x] 新增真实 CFPS/机器人配置：`Program/config/paper_real_cfps_robot.yaml`。
- [x] 完成真实 CLI live run：`run_cli_real_cfps_robot_20260526_isolated`。
- [x] 真实运行写出独立 state、results index、snapshot、analysis result、run log、Markdown/LaTeX 草稿和 observability。
- [x] 修复 Auto Research 数据选择：题目包含 CFPS/机器人时优先选择 `Data/Final/cfps_robot_reallocation.csv`，不再使用 demo `analysis_sample.csv`。
- [x] 修复启发式变量匹配：不再把 `ln_wage` 因为包含 `age` 而误放入 controls。
- [x] 新增 Journal Skill Registry 设计：`docs/architecture-v2/journal-skill-registry-design-2026-05-26.md`。
- [x] 新增方法库边界：`Program/methodology/README.md`。
- [x] 新增 AER-like proposal 入口：`Program/methodology/proposals/2026-05-26-aer-skills-import/proposal.yml`。
- [ ] 下一步实现 `JournalSkillRegistry` 读取器：能区分 proposal 和 canonical，并保证 proposal 不能阻断 formal export。
- [ ] 下一步实现 `state/product/journal_review.json` 的读写服务和 API。
- [ ] 下一步把 Task Brief 的“审稿标准：AER-like 顶刊标准”选择接入后端状态。
- [ ] 下一步把 Method Design 的缺失证据提示接入 Journal Skill rules。
- [ ] 下一步把 Review & Export 的 verifier gates 扩展为 journal-aware gates。

## 2026-05-26 P4-A Paper Package Quality Upgrade

- [x] 记录用户修正：研究产出按“草稿 -> 审阅 -> 终稿”推进，不再使用防御式自我贬低措辞。
- [x] 新增论文包质量标准：`docs/architecture-v2/paper-package-quality-standard-2026-05-26.md`。
- [x] 新增文献综述闭环方案：`docs/architecture-v2/literature-review-closed-loop-2026-05-26.md`。
- [x] 新增方法规范门方案：`docs/architecture-v2/method-gate-standard-2026-05-26.md`。
- [x] P4-A BDD：写 `docs/architecture-v2/codex-phase-p4-paper-package-quality-bdd.md`，锁定长篇正文、文献包、方法门、修订记录、PDF 导出质量报告和 LLM Supervisor 上下文包。
- [x] P4-A TDD：新增 CLI quality report / paper package 测试，先证明当前 `run_paper.py/export_pdf.py` 只证明导出链路，不足以证明论文包完整。
- [x] P4-A 实现：增加 `Program/workbench/paper_quality.py`，读取草稿、bibliography、method gate、manifest 并写出 `Results/json/paper_quality_report.json`。
- [x] P4-A 实现：增加 `Program/paper_package.py` 和 `Program/workbench/paper_package.py`，生成 `paper_expansion_plan.json`、结构化论文包草稿和 `paper_supervisor_context.json`。
- [x] P4-A 真实运行：对 `Manuscripts/generated/cfps_robot_paper_draft.md` 生成质量报告、扩写计划、结构化草稿和 LLM Supervisor 上下文包。
- [x] P4-A 架构边界：明确 Python/StatsPAI/StataMCP 是执行层，local Codex / LLM Supervisor 是研究中控和 Agent 派工层。
- [x] P4-A LLM 中控入口：新增 `Program/paper_supervisor.py` 和 `Program/workbench/paper_supervisor.py`，启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 后调用本地 Codex 生成可审阅 Supervisor 运行产物。
- [x] P4-A 真实 Supervisor 运行：生成 `Results/json/paper_supervisor_run.json` 和 `docs/workflows/paper_package_supervisor/supervisor_round.md`，状态为 `needs_human_review`，不改写正式层 `research_question/variable_roles/design_spec/run_plan`。
- [x] P4-A Agent Team 调度记录：确认后续 P4 阶段必须写明并行 Agent Team 介入点、回收点和主线集成验收点，避免串行低效和多 Agent 各自写散。
- [x] P4-B：完成 DataAgent 变量角色调和，把真实 CFPS/机器人研究线索与旧 `wage/trained` 合成样例拆开；输出 proposal，不直接覆盖正式 `variable_roles.json`。
- [x] P4-B BDD/TDD：新增行为 9 和 `tests/test_variable_role_reconciliation.py`，先确认缺少 CLI 入口的 RED，再实现最小 proposal CLI。
- [x] P4-B 实现：新增 `Program/variable_role_reconcile.py` 和 `Program/workbench/variable_role_reconcile.py`，写出 `state/proposals/variable_role_reconciliation.json` 与 `Results/json/variable_role_reconciliation_report.json`。
- [x] P4-B 真实运行：识别当前正式层两个冲突：旧 dataset `Data/Final/analysis_sample.csv` 与真实 dataset `Data/Final/cfps_robot_reallocation.csv` 冲突；旧 roles `wage/trained/edu/experience` 与真实 roles `ln_wage/ln_robot/female/age/edu_last/urban/bartik_iv/year/provcd` 冲突。
- [x] P4-B Agent Team 调度：并行调用 DataAgent 做状态/数据映射，调用 Method/Literature sidecar 做变量证据门调研；回收后由主 Agent 集成到 proposal 的 `agent_team_schedule` 和 `role_evidence_matrix`。
- [x] P4-C：实现 LiteratureAgent 的 `candidate_literature.csv`、`verified_bibliography.csv`、`contribution_matrix.md` 最小闭环。
- [x] P4-C BDD/TDD：新增行为 10 和 `tests/test_literature_package.py`，先确认缺少 `Program/literature_package.py` 的 RED，再实现最小文献包 CLI。
- [x] P4-C Agent Team 调研：调用 Literature sidecar 做英文核心文献、DOI/官方来源、证据角色和 CNKI 人工检索队列；回收后并入 seed literature package。
- [x] P4-C 实现：新增 `Program/literature_package.py` 和 `Program/workbench/literature_package.py`，生成 9 条候选/已校验英文文献、贡献矩阵、CNKI 人工检索队列和 Agent Team 调用节奏。
- [x] P4-C 真实运行：写出 `Data/literature/processed/candidate_literature.csv`、`verified_bibliography.csv`、`contribution_matrix.md`、`Results/json/literature_package_report.json`；`paper_quality_after_literature_package.json` 显示 `citation_status=passed`、`verified_count=9`、`closest_or_method_count=6`。
- [x] P4-D：实现 MethodGate baseline 报告，把当前 Bartik IV/2SLS 设计写成 `green/yellow/red` 审阅报告。
- [x] P4-D BDD/TDD：新增行为 11 和 `tests/test_method_gate_cli.py`，先确认缺少 `Program/method_gate.py` 的 RED，再实现最小方法门 CLI。
- [x] P4-D Agent Team 调研：并行调用 MethodAgent、ExecutionAgent explorer、ReviewerAgent sidecar；MethodAgent 给出 IV/Bartik 缺失证据，ExecutionAgent 定位执行层挂载点，ReviewerAgent 给出审稿式 scorecard 接入点。
- [x] P4-D 实现：新增 `Program/method_gate.py` 和 `Program/workbench/method_gate.py`，读取已批准 `DesignSpec` / `RunPlan`，只写 `Results/json/method_gate_report.json`，不改写正式层。
- [x] P4-D 真实运行：当前 Bartik IV 方法门为 `yellow`，已记录 first-stage F 和 partial R2，同时列出 reduced form、弱工具稳健推断、shift-share 诊断、Rotemberg weights、leave-one-out 等下一轮证据要求。
- [ ] P4-D2：扩展 MethodGate 到 DID/RDD/PSM/DML 的专属 `green/yellow/red` 规则，并接入 Journal Skill Registry / AER-like 方法规则。
- [ ] P4-E：让 PDF export manifest 读取 quality report，导出后显示“论文包审阅入口”和下一轮自动任务。

### Agent Team 调用节奏

- P4-B 已执行并行介入：DataAgent 读取真实数据字段和现有变量角色；Method/Literature sidecar 调研变量角色最低证据门、IV 风险和复现规范。三路只提供证据，不直接写正式层。
- P4-B 已执行回收点：主 Agent 汇总 sidecar 输出，形成 `state/proposals/variable_role_reconciliation.json` 和 `Results/json/variable_role_reconciliation_report.json`；正式 `state/product/variable_roles.json`、`design_spec.json`、`run_plan.json` 未被改写。
- P4-C 已执行并行介入：LiteratureAgent 调研英文核心文献、DOI、官方来源、证据角色和 CNKI 人工检索路径；主 Agent 同步写 BDD/TDD 和 CLI 契约，没有等待在原地。
- P4-C 已执行回收点：主 Agent 将调研结果收敛为 processed 文献包，生成 `candidate_literature.csv`、`verified_bibliography.csv`、`contribution_matrix.md` 和 `literature_package_report.json`；未改写 `state/product` 正式层。
- P4-D 已执行并行介入：MethodAgent 跑 IV/Bartik 方法规范门；ExecutionAgent explorer 定位执行层挂载点和只写报告的边界；ReviewerAgent 准备审稿式 scorecard 接入方式。三路共享已批准 `DesignSpec` / `RunPlan`，但不直接写正式层。
- P4-D 已执行回收点：主 Agent 将三路结果收敛为 `Results/json/method_gate_report.json`，把当前 Bartik IV 标为 `yellow`，并写入下一轮 Agent Team 调用节奏。
- P4-D2 下一轮并行介入：ExecutionAgent 执行 reduced form、弱工具稳健推断、shift-share 诊断和 leave-one-out；ReviewerAgent 同步把 MethodGate 结果转成 scorecard；MethodAgent 只在诊断结果回收后再次复核方法门状态。
- P4-D2 下一轮回收点：主 Agent 对齐方法诊断产物、Reviewer scorecard 和 paper quality report，再决定是否进入 ManuscriptAgent 扩写与 PDF 预检。
- P4-E 串行收口：ManuscriptAgent 只在方法门和文献包存在后生成草稿层章节；ExportAgent 只在 reviewer scorecard 通过后生成 PDF/README/manifest 预检包。

## 2026-05-22 Long-run Optimization Protocol

- [x] 定位项目根目录：`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`。
- [x] 读取项目 `AGENTS.md`、`Tasks/workflow.md`、`Tasks/long-run-iteration-plan.md`、`Tasks/manifest.md`、`Tasks/decision-log.md`，确认本轮只做流程文档固化。
- [x] 新增 `docs/architecture-v2/long-run-optimization-protocol.md`，定义平台期触发、策略跃迁、打破-修复和证据验收规则。
- [x] 新增 `Tasks/round-log.md`，作为长程研发轮次账本。
- [x] 将协议挂载到 `Tasks/long-run-iteration-plan.md`、`Tasks/workflow.md`、`Tasks/manifest.md`、`Tasks/decision-log.md`。
- [ ] 下一轮 P2-AA、方法执行、论文生成或产品状态机任务开始前，按 `Tasks/round-log.md` 模板记录本轮目标、平台期判断和策略选择。

## 2026-05-25 P2-AB 质量收口：Topic-first Auto Research + 前端契约修复

- [x] 按 BDD/TDD 完成 `auto-research` CLI：用户只给研究题目即可生成本地 Auto Research Run。
- [x] Auto Mode 默认 `best_available`，写入 `local_data`、`statspai`、`cnki`、`web_search`、`agentmemory`、`llm_supervisor` 能力状态；不可用能力显式记录原因。
- [x] 自动产出 `research_report.md` 和 `paper_draft_exploratory.md`，但标记 `needs_human_review` / `can_promote=false`，不能静默覆盖正式层。
- [x] 修复前端契约漂移：工作台首页恢复 topic-first 产品路径，工作台细节在确认选题后展开。
- [x] 修复 Agent Console 交互：Agent 行支持点击/键盘激活，详情只在右侧 drawer 展开，不再在主工作区重复铺开。
- [x] 浏览器验收：Playwright 截图 `journey-final-verify.png`、`journey-agent-drawer-clean-verify.png`；drawer 打开后 `inlinePanelsAfter=0`、`drawerOpen=true`。
- [x] 全量验证：`python3 -m unittest discover -s tests -v`，282 tests OK，skipped=1；`node --check Product/web/assets/app.js`、Python 编译和 scoped `git diff --check` 通过。
- [ ] 下一步 P2-AC：把 Auto Research Run 的候选层接到真实执行后端选择，优先实现 StatsPAI/Python execution adapter 的“计划 -> 执行 -> evaluator checks -> 人工审阅”闭环。

## 2026-05-25 P3 React Input And Slide Tabs

- [x] 按用户指定的两个 UI 参考，先只做研究输入器和阶段滑动导航，不扩展其他模块。
- [x] 新增 BDD：`docs/architecture-v2/codex-phase-p3-react-input-tabs-bdd.md`，锁定黑白灰、输入器、附件预览、模式选择、阶段导航和独立 React 入口。
- [x] 新增 RED 测试：`tests/test_p3_react_input_tabs.py` 首次 5 failures，原因是 `Product/web-react`、输入器、SlideTabs、样式和 App 组合入口不存在。
- [x] 新增独立 React/Vite 前端：`Product/web-react`，构建输出 `Product/web-dist`，旧 `Product/web` 保留。
- [x] 实现 `ResearchCommandInput`：题目输入、文件选择/拖拽、长文本粘贴卡片、模式选择和提交状态。
- [x] 实现 `SlideTabs`：任务书、递归搜索、数据变量、方法设计、执行实验；支持点击、hover 和键盘方向键。
- [x] 新增 `/react` FastAPI 预览入口，避免覆盖旧首页。
- [x] 视觉约束：新增 React CSS 只使用黑白灰色阶，不引入彩色强调色。
- [x] 验证：P3 单测、`npm run build`、`Product/app.py` 编译、scoped `git diff --check`、Playwright 视觉截图和全量回归通过。
- [x] 用户反馈修正：删除首屏解释性长句和“React 切片/不展开 Agent”防守性文案，改成更少、更产品化的状态提示。
- [x] 用户反馈修正：把黑白灰对比从纯黑纯白降到柔和灰阶，并接入 Three.js `DottedSurface` 点阵背景。
- [x] P3-B：新增 React Workbench 设计契约，先规范其余模块的 UI / 交互规则，再接具体业务工作流。
- [x] P3-B 设计契约锁定 10 个模块：研究入口、任务队列、递归搜索、数据与变量、方法设计、执行实验、结果解释、论文草稿、复现导出、Agent 审计。
- [x] P3-B 设计契约锁定信息披露规则：主屏只承载当前决策，默认只显示 3-5 个关键信号，详情进入右侧 Drawer 或按需展开。
- [x] P3-B 设计契约锁定视觉规则：黑白灰、低对比、DottedSurface、禁止防守性文案、不做普通 SaaS landing page。
- [x] P3-D 审阅：用 Kimi WebBridge 恢复真实浏览器检查，并用 Playwright 复现 Task Brief 页。
- [x] P3-D 审阅：确认当前 Task Brief 页的主要问题是缺少“下一步决策引导”，而不是单纯视觉 polish。
- [x] P3-D 交接：新增 `docs/architecture-v2/p3-task-brief-guided-action-review-2026-05-25.md`，把返工方向交给 Gemini/Kimi。
- [ ] 下一步 P3-C：按设计契约实现右侧审计 Drawer 和任务队列首个真实模块，不把 Agent 队列、证据台、全模块 IA 一次性铺开。

## 当前目标

把实证系统从静态阶段页推进到真实执行过程可观察：前端能选择/展示真实 run_id，读取 observability API，并渲染 run steps、events、HITL gates、产物证据、执行者和证据等级。

## 2026-05-17 P2-V Human Dispatch Audit For Agent Task Queue

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dispatch-audit-bdd.md`，定义 Agent Task Queue item 必须先经过人工派工审阅。
- [x] TDD：新增 `tests/test_agent_task_dispatch_audit.py`，先确认缺少 `can_execute`、dispatch-review API 404、前端缺少 `reviewDispatch` 的 RED。
- [x] 后端：新增 `Product/backend/task_dispatch_service.py`，支持 `approve`、`reject`、`needs_revision` 三种派工审阅动作。
- [x] 后端：扩展 `Product/backend/agent_task_queue_service.py`，让新旧队列都显式包含 `can_execute=false`、`next_action`、`dispatch_readiness`、`dispatch_review`。
- [x] API：新增 `PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/dispatch-review`。
- [x] 前端：在首页 Agent Task Queue 中显示派工审阅区，默认折叠输入证据、输出要求、风险和审计日志。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python/JS 静态检查、`git diff --check` 和浏览器自动化点击验收通过。
- [x] 安全边界：批准派工只进入 `reviewed_for_dispatch`，仍然 `can_execute=false`，不会直接调用 StatsPAI/StataMCP/Python 或改写研究状态。
- [x] P2-W：把真实 CFPS 字段候选推进到正式 VariableRoleSet 草稿链路；正式写入仍需用户在变量角色编辑器中保存。
- [x] P2-X：给 DesignSpec/RunPlan 增加方法工作流 checklist，区分 OLS/DID/IV/RDD/PSM/DML 的可执行前置条件。
- [x] P2-Y：把审稿意见产品化为 Reviewer Scorecard；评分理由和后续任务默认折叠，低分建议不会自动写入 Agent Task Queue。

## 2026-05-17 P2-W Real VariableRoleCandidate Promotion

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-real-variable-role-promotion-bdd.md`，定义真实字段候选只能先生成可编辑草稿，不能直接成为正式研究状态。
- [x] TDD：新增 `tests/test_real_variable_role_promotion.py`，先确认 promote API 404、正式状态未受保护、前端候选/正式区分缺失的 RED。
- [x] 后端：扩展 `Product/backend/variable_role_service.py`，新增 `state/product/variable_roles_drafts.json` 读写、promotion、draft applied 标记和 provenance。
- [x] API：新增 `POST /api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/promote`，返回 `201` 和 `variable_role_set_draft`。
- [x] 前端：在候选卡上新增 `基于候选创建变量角色草稿`，保留 `仅载入编辑器` 兼容路径；正式编辑器显示 `正式变量角色`，保存时才写入 `state/product/variable_roles.json`。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python/JS 静态检查、`git diff --check` 和浏览器自动化点击验收通过。
- [x] 安全边界：promotion 只写 draft 状态；不覆盖 approved VariableRoleSet，不重建 DesignSpec/RunPlan，不触发执行后端。

## 2026-05-17 P2-X Method Workflow Checklist

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-method-workflow-checklist-bdd.md`，定义 OLS/DID/IV/RDD/PSM/DML 的前置条件、诊断和阻塞规则。
- [x] TDD：新增 `tests/test_method_workflow_checklist.py`，先确认 `/method-workflows` API 404、blocked DID RunPlan 仍可保存、前端缺少方法工作流面板的 RED。
- [x] 后端：新增 `Product/backend/method_workflow_service.py`，把已确认 DesignSpec 转换为方法工作流 readiness、required inputs、diagnostics、blockers。
- [x] API：新增 `GET /api/v1/projects/{project_id}/method-workflows`，并让 `PUT /api/v1/projects/{project_id}/run-plan` 对 blocked 方法返回 409 `method_workflow_blocked`。
- [x] 前端：在 Research Design 和 Execution 页面显示方法工作流卡片；摘要显示可执行/缺什么，诊断和要求默认折叠在 `查看方法要求`。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python/JS 静态检查、`git diff --check` 和 Playwright 浏览器验收通过。
- [x] 安全边界：P2-X 只做方法准入 checklist；DID/IV/RDD/PSM/DML 没有真实 StatsPAI/StataMCP/Python 执行产物，不标记 `local_execution`。

## 2026-05-17 P2-Y Reviewer Scorecard And Follow-Up Task Suggestions

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-reviewer-scorecard-bdd.md`，定义审稿意见必须结构化为评分、证据、理由和后续任务建议。
- [x] TDD：新增 `tests/test_reviewer_scorecard.py`，先确认缺少 `/reviewer-scorecard` API、状态文件和前端评分面板的 RED。
- [x] 后端：新增 `Product/backend/reviewer_score_service.py`，从 successful full run 的 `results-draft` 生成 `deterministic_baseline` Reviewer Scorecard。
- [x] API：新增 `GET /api/v1/projects/{project_id}/reviewer-scorecard` 和 `POST /api/v1/projects/{project_id}/reviewer-scorecard`。
- [x] 前端：Review & Export 页面新增 `审稿评分` 面板；五个维度摘要默认可扫读，理由、证据和后续任务通过 `查看理由与后续任务` 按需展开。
- [x] 安全边界：后续任务只显示 `加入任务队列草案` 入口提示，不自动改写 `state/product/agent_task_queue.json`。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python/JS 静态检查、`git diff --check` 和 Playwright 浏览器验收通过。

## 2026-05-17 P2-Z Verifier Gates For Results, Manuscript, And Export

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-verifier-export-gates-bdd.md`，定义最终导出前必须显式通过结果绑定、复现产物、正文证据和 docx 预检。
- [x] TDD：新增 `tests/test_verifier_export_gates.py`，先确认 `/verifier-checks` API 404、缺少状态文件和前端 verifier 面板的 RED。
- [x] 后端：新增 `Product/backend/verifier_service.py`，从 export package、run plan、method execution、result artifact、draft preview 和 evidence levels 生成 verifier checks。
- [x] API：新增 `GET /api/v1/projects/{project_id}/verifier-checks` 和 `POST /api/v1/projects/{project_id}/verifier-checks/run`；没有 export package 时返回 409 `export_candidate_required`。
- [x] 前端：Review & Export 页面新增 `导出核验门` 面板，放在评分卡之后、导出包之前；每个 gate 显示状态、证据和下一步，docx 最终导出按钮受 `can_export_docx` 控制。
- [x] 安全边界：preview-ready export package 不能等同于最终导出；docx 预检仍 blocked 时，最终 docx 导出按钮保持 disabled。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python 编译、JS 语法、`git diff --check` 和 Playwright 浏览器验收通过。

## 2026-05-17 Pipeline MVP Review

- [x] 全量回归：`python3 -m unittest discover -s tests -v` 已通过，258 tests OK，skipped=1。
- [x] 静态检查：`python3 -m py_compile Product/app.py Product/backend/*.py`、`node --check Product/web/assets/app.js`、`git diff --check` 已通过。
- [x] 浏览器验收：Playwright 打开 `http://127.0.0.1:8768/?v=20260517-pipeline-mvp-review-final2`，10 项主流程检查全部通过，`errors=[]`、`badResponses=[]`。
- [x] 截图留档：`artifacts/ui-checks/pipeline-mvp-home.png`、`pipeline-mvp-data-variables.png`、`pipeline-mvp-execution.png`、`pipeline-mvp-review-export.png`。
- [x] UI 修复：approved SupervisorPlan 即使缺旧版 `human_review.action`，前端也显示 `人工审批 已批准`，不再误显示 `尚未审批`。
- [x] UI 修复：`docx 最终导出` 按钮新增稳定 id `verifier-final-export-button`，浏览器验收可直接确认 disabled 状态。
- [x] 缓存治理：`Product/web/index.html` 静态资源版本更新为 `20260517-pipeline-mvp-review`。
- [ ] 下一步 P2-AA：把已人工派工审阅的 Agent Task Queue 接到真实执行后端选择；优先做 StatsPAI/Python/StataMCP backend selection BDD/TDD，仍不得自动改写变量角色、研究设计、RunPlan 或论文正文。

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
- [ ] P2-L：把字段画像推进为“字段审阅 / VariableRoleSet 候选生成”状态机，但仍必须人工确认，不允许自动改写研究状态。

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

## 2026-05-16 P2-R ResearchQuestion / TopicSession 持久化

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-research-question-topic-session-bdd.md`，定义首页确认选题后必须生成可跨 Session 恢复的 ResearchQuestion 状态。
- [x] TDD：新增 `tests/test_research_question_topic_session.py`，并扩展 `tests/test_product_workflow_contract.py`，首次运行失败原因是 `/research-question/current` API 404 和前端只依赖本地状态。
- [x] 实现：新增 `Product/backend/research_question_service.py`，读写 `state/product/research_question.json`，未确认时只返回 project seed draft，不创建状态文件。
- [x] 实现：新增 `GET/PUT /api/v1/projects/{project_id}/research-question/current`。
- [x] 实现：`GET /overview` 暴露 `research_question_state`，并让 `workflow_contract` 中 ResearchQuestion 阶段按 confirmed 状态推进。
- [x] 前端：首页“进入研究判断”调用后端保存 ResearchQuestion，保存后刷新 overview；静态资源版本更新到 `20260516-p2r-topic-session1`。
- [x] 验证：目标测试 15 OK，核心回归 36 OK，全量回归 219 OK、skipped=1，Python/JS 静态检查通过，浏览器验收通过。
- [x] 交接：更新 `Tasks/handoff.md`、`Tasks/decision-log.md`、`Tasks/manifest.md`、`Tasks/review.md`。
- [ ] P2-S：把 ResearchQuestion 作为 SupervisorPlan 输入，生成人工可审阅的 plan artifact，不自动改写 VariableRoleSet、DesignSpec 或 RunPlan。

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
## 2026-05-13 P2-A Dataset Quality Profile

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-data-quality-profile-bdd.md`，定义数据集必须先生成本地文件证据级质量画像，再进入变量角色/研究设计。
- [x] TDD：新增 `tests/test_dataset_quality_profile.py`；首次运行失败原因是 `/datasets` 返回的数据集缺少 `quality_profile`，前端缺少数据质量画像面板。
- [x] 实现：扩展 `Product/backend/overview_service.py`，CSV 数据集返回 `quality_profile`，包含行列数、缺失单元格、缺失率、数值/文本字段数、字段画像和检查项；暂不支持的真实文件保留 `evidence_level=local_file` 并标记 `not_profiled`。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，数据与设计页新增“数据质量画像”，并把数据集、质量画像、变量角色编辑器改成纵向 clean workbench 顺序，避免与右侧属性检查器挤压。
- [x] 中文化修正：扩展 `tests/test_frontend_chinese_copy.py`，防止 `dataset_quality_profile` / `confirm_variable_roles` 这类内部标签重新出现在可见 eyebrow 文案。
- [x] 验证：`python3 -m unittest discover -s tests -v`，148 tests OK，skipped=1；Python 编译检查通过；`node --check Product/web/assets/app.js` 通过。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2a`，进入“数据与设计”后可见 `analysis_sample.csv`、`数据质量画像`、样本 12、缺失率 0%、字段画像和中文标签；布局不再出现两列挤压。
- [x] P2-B：设计 StatsPAI/CoPaper 式方法技能集目录，把 OLS/DID/IV/RDD/PSM/DML 等方法的前置变量要求和可执行状态接入 RunPlan。

## 2026-05-13 P2-B Method Skill Catalog

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-method-skill-catalog-bdd.md`，定义 RunPlan 必须暴露方法技能集、前置变量、阻塞原因和默认可执行方法。
- [x] TDD：新增 `tests/test_method_skill_catalog.py`；首次运行失败原因是 RunPlan 缺少 `method_catalog`、任务缺少 `method_id`、前端缺少 `method-skill-catalog-panel`。
- [x] 实现：扩展 `Product/backend/design_spec_service.py`，从已确认 DesignSpec / VariableRoleSet 派生 OLS、DID、IV、RDD、PSM、DML 方法目录；所有条目标记 `evidence_level=local_file`。
- [x] 实现：默认 RunPlan 只加入当前 ready 的 OLS baseline 任务，DID/IV/RDD 等方法只展示阻塞原因，不伪装为已执行。
- [x] 前端：研究设计页新增“方法技能集”，显示 StatsPAI/CoPaper 前置条件、方法可执行状态、执行者、证据等级、前置要求和阻塞原因。
- [x] 视觉修正：方法目录改为纵向 clean workbench 证据清单，避免双列卡片在 Safari 中继续拥挤。
- [x] 验证：`python3 -m unittest discover -s tests -v`，152 tests OK，skipped=1；Python 编译和 JS 语法检查通过；API / Safari 可视化验收通过。
- [x] P2-C：把方法目录推进到真实方法执行适配器设计，优先选择一个最小 OLS/StatsPAI/Stata 执行路径，并把结果写成 `local_execution` 证据。

## 2026-05-13 P2-C OLS Execution Adapter

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-ols-execution-adapter-bdd.md`，定义 approved OLS RunPlan 必须生成本地方法执行结果、绑定 RunPlan/数据集/公式、写入 manifest，并拒绝 unsupported 方法。
- [x] TDD：新增 `tests/test_ols_execution_adapter.py`；首次运行 4 条中 3 条失败，原因是 `Results/json/method_execution_result.json`、`run.method_execution` 和 manifest `method_execution` 尚不存在；unsupported method 已在实现初版后通过。
- [x] 实现：扩展 `Product/backend/project_service.py`，新增本地 `python_ols_adapter`，从 approved RunPlan 读取 OLS task、公式和本地 CSV，计算 OLS 系数并写入 `Results/json/method_execution_result.json`。
- [x] 实现：扩展 `Product/app.py`，对 unsupported method 返回 409 `unsupported_run_plan_method`，对数据不足、公式不可估、共线设计返回 409 `method_execution_failed`，避免后端 500。
- [x] 契约修复：`run.plan_binding.tasks[].method_id` 现在回退到 estimator，真实样例不会再出现 `method_id=null`。
- [x] 验证：目标测试 5 OK；相邻回归 20 OK；全量回归 157 OK，skipped=1；Python 编译和 JS 语法检查通过。
- [x] API 验收：真实项目 `POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_4c62f1721afb`，status=`succeeded`，`plan_binding.tasks[0].method_id=ols`，`method_execution.evidence_level=local_execution`，`treatment_coefficient=1.8505076803`。
- [x] 可视化验收：Safari + Computer Use 打开本地页面，研究设计细节页可正常加载；P2-C 为后端执行证据能力，下一步需要把 `method_execution` 更清晰地接入 Execution / Findings UI。
- [x] P2-D：把 `Results/json/method_execution_result.json` 接入 Execution / Findings，把 OLS 结果作为方法执行证据展示，而不是只停留在 API response。

## 2026-05-13 P2-D Method Execution Evidence UI

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-method-execution-ui-bdd.md`，定义方法执行证据在 observability、Execution 页面和 Results/FindingCard 中必须可见。
- [x] TDD：扩展 `tests/test_observable_execution.py`、`tests/test_observable_execution_frontend.py`、`tests/test_results_draft_evidence_binding.py`；首次失败原因符合预期：后端缺少 `method_execution`，前端缺少 `observable-method-execution` 和 FindingCard 方法证据渲染。
- [x] 实现：扩展 `Product/backend/observability_service.py` 和 `Product/backend/results_draft_service.py`，从 run manifest / artifact 读取 `Results/json/method_execution_result.json`，并把方法、公式、样本量、处理变量系数和证据等级返回给页面。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，在“实证执行”新增“方法执行证据”，在“结果与草稿”的 FindingCard 内新增方法执行证据块。
- [x] 验证：目标测试 4 OK；Results Draft 回归 10 OK；相邻回归 38 OK；全量回归 161 OK，skipped=1；Python 编译、`node --check` 和 `git diff --check` 通过。
- [x] API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/runs/run_4c62f1721afb/observability` 和 `/results-draft` 均返回 `method_execution.evidence_level=local_execution`、`engine=python_ols_adapter`、`formula=wage ~ trained + edu + experience`、`nobs=12`、`treatment_coefficient=1.8505076803`。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2d-method`，在“实证执行”和“结果与草稿”均可看到 OLS 方法执行证据、artifact 路径、公式、样本量和处理变量系数。
- [x] P2-E：扩展方法执行 evaluator，补齐标准误、t 统计量、p 值、95% 置信区间、残差诊断和命名 evaluator checks，并把结果绑定到 FindingCard 方法证据。

## 2026-05-13 P2-E OLS Evaluator Evidence

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-ols-evaluator-bdd.md`，定义 OLS 方法执行必须产出推断指标、诊断项、evaluator verdict，并在 Results & Draft 显示。
- [x] TDD：扩展 `tests/test_ols_execution_adapter.py` 和 `tests/test_results_draft_evidence_binding.py`；首次失败为 `KeyError: standard_errors/evaluator/evaluator_status`，符合“尚未实现 evaluator 证据”的预期。
- [x] 实现：扩展 `Product/backend/project_service.py`，本地 OLS adapter 计算标准误、t 统计量、normal approximation p 值、95% 置信区间、残差自由度、残差标准误和 evaluator checks。
- [x] 实现：扩展 `Product/backend/results_draft_service.py`，FindingCard 的 `method_evidence` 绑定 `standard_error`、`p_value`、`confidence_interval`、`evaluator_status` 和完整 evaluator。
- [x] 前端：扩展 `Product/web/assets/app.js` 和 `Product/web/assets/styles.css`，把 FindingCard 的方法证据改为紧凑中文审阅摘要，避免窄卡片网格拥挤；`Product/web/index.html` asset version 更新到 `20260513-p2e-eval2`。
- [x] 验证：目标测试 19 OK；全量回归 165 OK，skipped=1；Python 编译、`node --check Product/web/assets/app.js` 和 `git diff --check` 通过。
- [x] API 验收：真实 full run `run_a3674e9e78c6` succeeded；`p_value_trained=8.83354660202e-133`、`standard_error_trained=0.0754664205`、`evaluator_status=passed`，四项 evaluator checks 全部 passed。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2e-eval`，点击“结果与草稿”，结果论断卡显示 `ols · n=12 · β=1.8505 · 标准误=0.0755 · p=8.83e-133 · 95% 置信区间 1.7026 ~ 1.9984 · 评估器通过`。
- [x] P2-F：使用 `/Users/mahaoxuan/Desktop/实证数据库` 中的真实数据源做数据接入验收，先以只读候选池方式把真实数据 inventory/profile 接到 Data & Design。

## 2026-05-13 P2-F Real Data Candidate Pool

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-real-data-catalog-bdd.md`，定义真实数据仓库必须以只读候选池进入产品，而不是直接伪装成项目内数据。
- [x] TDD：新增 `tests/test_external_data_catalog.py`；首次失败覆盖 `external_catalog` 缺失、外部 CSV 画像缺失、DTA 可见性缺失和前端候选池面板缺失。
- [x] 实现：扩展 `Product/backend/overview_service.py`，`GET /datasets` 返回 `external_catalog`；默认读取 `/Users/mahaoxuan/Desktop/实证数据库`，也可用 `EMPIRICAL_DATA_LIBRARY_ROOT` 覆盖。
- [x] 实现：外部候选数据全部标记 `evidence_level=local_file`、`read_only=true`、`role=external_candidate_dataset`；CSV 做最多 200 行轻量预览画像，DTA/XLSX/Parquet 等暂标 `not_profiled` 但保留可见。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，在“数据与设计”页新增 `真实数据候选池`，与项目内 `analysis_sample.csv` 分开展示；首屏只渲染 6 张候选卡，避免重新拥挤。
- [x] 真实数据验收：本机 `/Users/mahaoxuan/Desktop/实证数据库` 扫描到 223 个候选数据文件；Safari 页面显示 CFPS DTA 文件、`本地文件`、`尚未画像`、`只读` 和真实根目录。
- [x] 验证：目标测试 5 OK；相邻数据画像测试 11 OK；全量回归 170 OK，skipped=1；Python 编译、`node --check`、`git diff --check` 通过。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow，并同步 `Tasks/` 到 `tasks/`。
- [x] P2-G：设计“从真实候选池导入/绑定数据集”的显式预检。导入前记录来源、目标路径、文件大小、证据等级和用户动作；预检阶段不移动、不复制、不绑定外部原始数据。

## 2026-05-14 P2-G Real Dataset Bind Preflight

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dataset-bind-preflight-bdd.md`，定义真实候选数据进入项目之前必须先生成导入/绑定预检，而不是直接复制或喂给变量角色、DesignSpec、RunPlan。
- [x] TDD：新增 `tests/test_external_dataset_bind_preflight.py`；首次运行失败原因符合预期：API 返回 404，前端缺少 `external-bind-preflight-panel` 和候选数据预检按钮。
- [x] 实现：扩展 `Product/backend/overview_service.py` 和 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/datasets/external-bind-preflight`，只接受 `/Users/mahaoxuan/Desktop/实证数据库` 候选池内的数据文件，写入 `state/product/dataset_import_preflights.json`。
- [x] 实现：预检结果包含 `status=ready_for_review`、`evidence_level=local_file`、源文件路径、目标建议路径 `Data/Raw/<filename>`、策略、文件大小、4 项检查和 `will_mutate_source=false` / `will_create_project_file=false`。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，在“真实数据候选池”候选卡上新增“生成导入/绑定预检”，并在“导入/绑定预检”面板显示待人工确认、来源、目标、策略、检查项和只读说明。
- [x] 验证：目标测试 5 OK；相邻数据测试 16 OK；全量回归 175 OK，skipped=1；Python 编译、`node --check` 和 `git diff --check` 通过。
- [x] API 验收：`GET /datasets` 返回外部候选池 223 个文件；`POST /datasets/external-bind-preflight` 对 CFPS DTA 候选文件返回 `ready_for_review`、目标 `Data/Raw/...dta` 和 4 项 passed checks。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2g-bind1`，点击“数据与设计”，点击候选文件“生成导入/绑定预检”，页面显示 `待人工确认`、源路径、目标路径、`尚未导入/绑定 · 源文件只读` 和 4 项通过检查。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow，并同步 `Tasks/` 到 `tasks/`。
- [x] P2-H：实现显式 apply/import workflow。只有用户确认后才允许把预检记录变成项目内 `Data/Raw/...` 文件或绑定记录；同时必须记录人工动作、目标 artifact、哈希/大小和失败回滚语义。

## 2026-05-14 P2-H Real Dataset Import Apply

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dataset-import-apply-bdd.md`，明确本地版可复制/绑定真实数据，线上版不能读取用户桌面路径，必须走上传或云对象。
- [x] TDD：新增 `tests/test_external_dataset_import_apply.py`；首次运行失败符合预期：apply API 返回 404，前端没有三类人工动作按钮。
- [x] 实现：扩展 `Product/backend/overview_service.py` 和 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/datasets/external-bind-preflight/{preflight_id}/apply`。
- [x] 实现：支持 `copy_to_project_raw`、`bind_external_reference`、`cancel` 三种动作；记录 `dataset_import`、SHA256、大小、目标路径、runtime mode、人工动作和状态。
- [x] 产品边界：`runtime_mode=cloud` 对本地路径返回 409 `cloud_upload_required`，避免线上应用假装能读取本机文件。
- [x] 前端：扩展“导入/绑定预检”面板，显示“确认导入到项目 / 只绑定引用 / 取消预检”及按钮解释；apply 后回显“已接入”、动作、local 模式和 SHA256。
- [x] 验证：目标测试 5 OK；相邻数据测试 21 OK；全量回归 180 OK，skipped=1；Python 编译、`node --check`、`git diff --check` 通过。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2h-import1`，点击“数据与设计”，对 CFPS 预检点击“只绑定引用”，页面显示 `已接入`、`已绑定外部引用`、`模式：local` 和 SHA256。
- [x] P2-I：对已复制或已绑定的真实数据做安全字段画像/变量字典预览，尤其是 DTA/XLSX/Parquet；完成前不得让新数据进入 VariableRoleSet、DesignSpec 或 RunPlan。

## 2026-05-14 P2-I Dataset Import Field Profile

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dataset-import-profile-bdd.md`，定义真实数据接入后的字段画像/变量字典预览边界。
- [x] TDD：新增 `tests/test_external_dataset_import_profile.py`；首次运行 6 条失败，原因是缺少 profile API、前端画像入口和画像面板。
- [x] 实现：新增 dataset import profile 服务，读取已 apply 的 CSV 字段结构并持久化画像结果。
- [x] 实现：DTA/XLSX/Parquet 暂不伪造字段，返回 `blocked/not_profiled` 和阻塞原因。
- [x] 前端：导入/绑定预检结果区增加“生成字段画像”和画像预览面板，明确不会改写 VariableRoleSet、DesignSpec 或 RunPlan。
- [x] 验证：目标测试 6 OK；相邻回归 27 OK；全量回归 186 OK，skipped=1；Python/JS 静态检查、`git diff --check`、API 和页面静态资源验收通过。

## 2026-05-14 P2-J Stata DTA Field Profile

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dta-field-profile-bdd.md`，定义 DTA metadata-only 字段画像、损坏文件阻塞、不改写研究状态。
- [x] TDD：扩展 `tests/test_external_dataset_import_profile.py`；首次运行 3 条失败，原因是有效 DTA 仍返回 blocked、损坏 DTA 阻塞原因不精确、前端缺少变量标签/Stata 类型。
- [x] 实现：扩展 `Product/backend/overview_service.py`，用 `pyreadstat.read_dta(..., metadataonly=True)` 读取 Stata 元数据，返回字段名、变量标签、Stata 类型、display format、样本数和字段数。
- [x] 实现：损坏 DTA 或缺少读取器时返回 `blocked/not_profiled`、空字段和 `DTA 读取失败...`，不抛 500、不伪造字段。
- [x] 前端：字段画像表从“样本值”改为“变量标签 / Stata 类型”，并修正字段表列宽和表头大小写。
- [x] 真实验收：`dataset_import_e9d864229be8` 绑定的 `cfps2011adult_202202(1).dta` 返回 `profiled/ready`、`row_count=1279`、`column_count=723`、`row_count_source=metadata_only`，前 6 个字段含 `pid=个人id`、`fid=家户号`、`provcd=省国标码`。
- [x] 验证：目标测试 7 OK；相邻回归 28 OK；全量回归 187 OK，skipped=1；Python/JS 静态检查和 `git diff --check` 通过；Playwright CLI 截图 `/tmp/empirical-workbench-p2j-dta-profile.png`。
- [x] P2-K：按用户最新要求，优先建立严谨实证执行契约；full run 必须声明当前真实执行后端、候选 StatsPAI/StataMCP 后端、数据预检和可复现入口。
- [x] P2-K：Execution 页面显示“严谨执行契约 / 数据预检 / 可复现入口”，明确 StatsPAI/StataMCP 目前是候选后端，不能冒充 `local_execution`。
- [x] P2-L：把字段画像推进为“字段审阅 / VariableRoleSet 候选生成”状态机，但仍必须人工确认，不允许自动改写研究状态。
- [x] P2-M：先完成 approved candidate 到正式 VariableRoleSet 的显式写回链路；候选必须载入正式编辑器并允许人工调整，保存后才写入正式研究状态。
- [ ] P2-N：接入真实 StatsPAI/StatsAPI 或 StataMCP 执行器，要求生成独立日志、结果文件、evaluator checks、交叉验证和 `local_execution` evidence。

## 2026-05-14 P2-K Rigorous Empirical Execution Contract

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-rigorous-empirical-execution-bdd.md`，定义“严谨实证执行契约”。
- [x] TDD：扩展 `tests/test_ols_execution_adapter.py` 和 `tests/test_observable_execution_frontend.py`；首次运行失败原因为缺少 `execution_contract`、`data_preflight` 和前端展示。
- [x] 实现：`Product/backend/project_service.py` 的 full run 现在写入 `execution_contract`，并把 active backend 固定为真实执行过的 `python_ols_adapter`。
- [x] 实现：StatsPAI/StatsAPI 与 StataMCP/Stata 只作为候选后端展示，除非未来实际调用并产生日志/产物，否则不标记为 `local_execution`。
- [x] 实现：OLS 任务写入 `data_preflight`，包含读取行数、可用数值行、丢弃行数、必需字段和自由度预检。
- [x] 实现：OLS 任务写入 `reproducibility`，包含 run_id、RunPlan/DesignSpec 版本、公式、结果文件路径和源码入口。
- [x] 前端：Execution 页面新增“严谨执行契约”“数据预检”“可复现入口”三块，用户能直接看到 Python/StatsPAI/StataMCP 的真实状态边界。
- [x] 验证：目标测试 24 OK；相邻回归 42 OK；全量回归 190 OK，skipped=1；Python/JS 静态检查和 `git diff --check` 通过；Playwright CLI 可视化检查无横向溢出。

## 2026-05-14 P2-L Variable Role Candidate Review

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-variable-role-candidate-review-bdd.md`，定义真实 DTA 字段画像只能生成可审阅候选，不能自动写入正式 VariableRoleSet。
- [x] TDD：新增 `tests/test_variable_role_candidates.py`；首次运行 5 条失败，原因是候选 API 404、前端缺少 `variable-role-candidate-panel` 和候选 review 操作。
- [x] 实现：扩展 `Product/backend/variable_role_service.py`，新增 `state/product/variable_role_candidates.json` 候选状态机，支持生成、确认候选、标记需调整和驳回。
- [x] 实现：扩展 `Product/app.py`，新增候选列表、生成和 review API，并对未画像 import 返回 409 `field_profile_required`，对非法动作返回 400 `invalid_variable_role_candidate_action`。
- [x] 前端：扩展“数据与设计”页，新增“字段审阅”面板；用户可以从真实字段画像生成变量角色候选，并看到 `不会写入正式变量角色集` 的边界说明。
- [x] 验证：目标测试 5 OK；相邻回归 17 OK；全量回归 195 OK，skipped=1；Python 编译和 JS 语法检查通过。
- [x] 可视化验收：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260515-p2l-candidates1`，进入“数据与设计”，真实 CFPS `.dta` 显示 723 个字段；点击“生成变量角色候选”后显示 `待人工审阅`、候选角色、候选字段表和 `state/product/variable_role_candidates.json`；点击“候选已确认”后候选状态为 `approved_candidate`。
- [x] 安全边界验收：确认前后 `state/product/variable_roles.json` SHA256 均为 `bc8bedca4d1638d2556ad77957de146eda170cef521db24eeb7ffde5c2e94649`，mtime 未变化，证明候选 review 没有写回正式变量角色集。
- [ ] P2-M：把 approved candidate 之后的真实变量选择流程做成可编辑确认，不再依赖启发式猜测；随后接 StatsPAI/StataMCP/Python 严格执行器。

## 2026-05-14 P2-M Candidate Promotion to Formal VariableRoleSet

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-variable-role-candidate-promote-bdd.md`，定义候选进入正式变量角色集的边界：未确认候选不能写入，已确认候选也必须先载入正式编辑器，保存后才写入。
- [x] TDD：扩展 `tests/test_variable_role_candidates.py`；首次运行失败符合预期：后端仍按旧本地数据路径校验拒绝真实候选，前端缺少 `pendingVariableRoleCandidateId`。
- [x] 实现：扩展 `Product/backend/variable_role_service.py`，`save_project_variable_roles(..., candidate_id=...)` 支持从 approved candidate 写入正式 VariableRoleSet，并保留 `candidate_id`、`dataset_import_id`、`dataset_import_profile_id`、`source`、`binding` 和 provenance。
- [x] 实现：未确认、需调整或被驳回的候选返回 409 `variable_role_candidate_approval_required`，不能写入正式研究状态。
- [x] 实现：保存成功后候选状态更新为 `applied_to_variable_roles`，并记录 `applied_variable_role_set_version`，避免同一个候选被误认为仍待写回。
- [x] 前端：字段审阅卡片新增“载入正式编辑器”；点击后编辑器切换为 `draft_from_candidate · local_file`，带入 `candidate_id`、真实数据路径和候选角色，提示“保存后才写入正式变量角色集”。
- [x] 可视化验收：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2m`，进入“数据与设计”，点击“载入正式编辑器”后确认编辑器显示 `candidate_id=variable_role_candidate_495092cb7af2`、`draft_from_candidate · local_file`、真实 CFPS DTA 路径和候选字段。
- [x] 保护性验收：本轮没有点击“保存变量角色集”，避免把当前演示项目已批准的 `analysis_sample.csv` 变量角色覆盖成 CFPS 启发式候选。
- [x] 验证：目标测试 8 OK；全量回归 198 OK，skipped=1；Python 编译和 JS 语法检查通过。
- [x] P2-N：接入 StatsPAI/StatsAPI 作为 OLS 独立验证后端，生成独立结果文件、交叉验证检查和 `local_execution` evidence。
- [x] P2-O：把本地 Codex Supervisor 作为智能中控层显式接入 workflow contract 和首页，展示 provider readiness、执行开关、阻塞原因和派工计划。
- [ ] P2-P：实现真实 Supervisor plan artifact。启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 后，由本地 Codex 生成/审阅阶段计划并写入可审计产物；未启用时必须继续显示 blocked，不允许伪装智能派工。

## 2026-05-14 P2-N StatsPAI Independent OLS Validation

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-statspai-execution-validation-bdd.md`，定义 StatsPAI 必须真实执行并写出独立验证产物。
- [x] TDD：扩展 `tests/test_ols_execution_adapter.py`；首次失败原因是 full run 只有 Python OLS adapter，没有 `backend_validations` 和 `Results/json/statspai_execution_result.json`。
- [x] 实现：扩展 `Product/backend/project_service.py`，新增 `execute_statspai_ols_validation()`；当 StatsPAI 可用且数据为 CSV 时调用 `statspai.regress()`，输出系数、标准误、p 值、t 统计、诊断和 cross-check。
- [x] 前端：扩展 `Product/web/assets/app.js` 和 `Product/web/assets/styles.css`，在实证执行页“方法执行证据”中新增“独立后端验证”，显示 StatsPAI adapter、状态、产物路径、证据等级和交叉检查。
- [x] 可视化/API 验收：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2n-supervisor1`；最终 API 复核启动完整实证执行生成 `run_bb423547439c`，observability 返回 `独立后端验证`、`passed`、`statspai.regress` 和 `Results/json/statspai_execution_result.json`。
- [x] 验证：目标测试和全量回归均通过；最新全量为 `python3 -m unittest discover -s tests -v`，203 tests OK，skipped=1。

## 2026-05-14 P2-O LLM Supervisor Readiness Contract

- [x] BDD：扩展 `tests/test_product_workflow_contract.py`，定义 workflow contract 必须显式声明 LLM Supervisor 层，首页必须展示本地大模型中控状态。
- [x] TDD：首次失败原因是 `workflow_contract` 缺少 `intelligence_layer`，前端缺少 `llm-supervisor-panel` 和 `renderIntelligenceLayer()`。
- [x] 实现：扩展 `Product/backend/overview_service.py`，新增 `build_intelligence_layer_contract()`，读取 `local_codex_status()`，返回 `supervisor_agent_id=pipeline_supervisor`、provider、ready/blocked 状态、blockers 和派工计划。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，首页新增“智能中控”面板，显示本地 Codex Supervisor、Provider、可用性、执行开关、阻塞原因和阶段派工计划。
- [x] 可视化验收：页面显示 `本地 Codex Supervisor 未启用`、`provider=local_codex`、`可用=是`、`允许执行=否`、`local_codex_execution_not_enabled` 和四个派工方向。
- [ ] 未完成：当前只是 Supervisor readiness contract，不是实际 LLM 派工执行。真实派工必须等 P2-P 持久化 `supervisor_plan` 并在执行开关启用时调用本地 Codex。

## 2026-05-16 P2-P Local Codex SupervisorPlan Artifact

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-supervisor-plan-bdd.md`，定义本地 Codex Supervisor 只能生成可审阅计划，不能直接改写正式研究状态。
- [x] TDD：新增 `tests/test_supervisor_plan.py`；首次运行 5 条失败，原因是 `/supervisor-plan` API 返回 404，前端缺少 `supervisor-plan-panel`。
- [x] 实现：新增 `Product/backend/supervisor_plan_service.py`，在 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 时调用本地 Codex 生成计划，并持久化到 `state/product/supervisor_plan.json`。
- [x] 实现：扩展 `Product/backend/codex_provider.py`，新增通用 `run_local_codex_prompt()`，保留 provider readiness 与显式执行开关。
- [x] 实现：扩展 `Product/app.py`，新增 `GET/POST /api/v1/projects/{project_id}/supervisor-plan`。
- [x] 前端：首页新增 `SupervisorPlan 审阅台`，显示计划状态、风险、证据要求、子 Agent 分工、人工确认 gate 和生成按钮。
- [x] 边界：未启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 时返回 409 `local_codex_execution_not_enabled`，不会创建 `supervisor_plan.json`，也不会伪装智能派工。
- [x] 保护性验证：测试确认生成 SupervisorPlan 前后 `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json` 不变。
- [x] 验证：目标测试 5 OK；相邻回归 20 OK；全量回归 208 OK，skipped=1；Python 编译、JS 语法和 `git diff --check` 通过。
- [x] 可视化/API 验收：当前工作树服务运行在 `http://127.0.0.1:8767/?v=20260516-p2p-supervisor-plan`；DOM 显示 `SupervisorPlan 审阅台`、`生成 SupervisorPlan`、`本地 Codex SupervisorPlan` 和默认阻断 `local_codex_execution_not_enabled`；截图保存到 `artifacts/ui-checks/p2p-supervisor-plan-overview.png`。
- [ ] 下一步 P2-Q：把 SupervisorPlan approval 做成显式人工确认状态，然后让 approved SupervisorPlan 驱动下一轮执行任务队列；仍不能自动改写 VariableRoleSet、DesignSpec 或 RunPlan。

## 2026-05-16 P2-P1 Home Progressive Disclosure

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-home-progressive-disclosure-bdd.md`，定义首页智能中控和 SupervisorPlan 的细节默认折叠。
- [x] TDD：扩展 `tests/test_supervisor_plan.py` 和 `tests/test_product_workflow_contract.py`；首次运行 2 条新增前端行为失败，原因是页面没有 `progressive-disclosure`、`查看中控详情`、`查看计划详情`。
- [x] 实现：首页“智能中控”首屏只显示启用状态、证据等级、阻塞数量和派工角色数量；Provider、执行开关、阻塞项和派工计划进入可展开详情。
- [x] 实现：首页 `SupervisorPlan 审阅台` 首屏只显示状态、主按钮、人工确认说明和下一步摘要；版本、写入边界、阶段计划、子 Agent 分工、证据要求和风险进入可展开详情。
- [x] 可访问性：使用原生 `details/summary`，默认不加 `open`，并补齐 focus-visible 样式。
- [x] 验证：目标测试 15 OK；全量回归 210 OK，skipped=1；Python 编译、JS 语法、`git diff --check` 通过。
- [x] 右侧内置浏览器验收：`http://127.0.0.1:8767/?v=20260516-p2p-disclosure1` 中两个详情块初始关闭；点击后 `Provider` 和 `SupervisorPlan` 明细可见；截图保存到 `artifacts/ui-checks/p2p-home-progressive-disclosure.png`。
- [ ] 下一步 P2-Q：实现 SupervisorPlan approve/reject/needs_revision 审批状态机，并把 approved plan 作为后续任务队列的输入。

## 2026-05-16 P2-Q Topic-first Home

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-topic-first-home-bdd.md`，定义首页必须先让用户输入或选择研究选题，再进入具体判断环节。
- [x] TDD：扩展 `tests/test_product_workflow_contract.py`；首次运行 3 条新增行为失败，原因是页面缺少 `research-topic-intake`、`research-workbench-after-topic` 和 `data-topic-start-action`。
- [x] 实现：首页新增“开始一项实证研究”入口，包含选题输入、从已有选题继续、从真实数据候选池开始。
- [x] 实现：原首页中的下一步研究决策、智能中控、SupervisorPlan、风险和执行概览默认进入 `research-workbench-after-topic`，确认选题后才展开。
- [x] 实现：选题只保存为前端本地状态，不写回 VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。
- [x] 视觉收敛：窄视口下隐藏右侧 inspector、压缩侧栏和间距，保证选题入口能在首屏可见。
- [x] 验证：目标前端契约测试 9 OK；相邻回归 18 OK；全量回归 213 OK，skipped=1；Python 编译、JS 语法、`git diff --check` 通过。
- [x] 右侧内置浏览器验收：`http://127.0.0.1:8767/?v=20260516-p2q-topic1` 初始只显示选题入口；输入选题并点击 `进入研究判断` 后，才显示 `下一步研究决策`、`智能中控` 和 `SupervisorPlan`。
- [ ] 下一步 P2-R：把确认后的研究选题升级为后端 `ResearchQuestion` / `TopicSession` 审计对象，再做 SupervisorPlan approve/reject/needs_revision 审批状态机。

## 2026-05-16 P2-S SupervisorPlan Topic Binding

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-supervisor-plan-topic-binding-bdd.md`，定义 SupervisorPlan 必须基于 confirmed ResearchQuestion / TopicSession。
- [x] TDD：扩展 `tests/test_supervisor_plan.py`；首次运行 5 条失败，原因是 Codex prompt 缺少 confirmed research question、无选题时没有提前返回 `research_question_required`、前端审阅台不显示绑定选题。
- [x] 实现：`Product/backend/supervisor_plan_service.py` 在生成 SupervisorPlan 前读取 `state/product/research_question.json`，只接受 `status=confirmed`。
- [x] 实现：SupervisorPlan 输出新增 `input_research_question`、`input_state_versions.research_question_version`、`input_evidence.research_question_path`。
- [x] 实现：传给本地 Codex 的 prompt 新增 `confirmed_research_question`，包含 question、version、topic_session_id、evidence_level 和 path。
- [x] 前端：`SupervisorPlan 审阅台` 摘要显示 `绑定选题`，详情显示 `TopicSession` 和 `ResearchQuestion 版本`。
- [x] 验证：目标测试 8 OK；相邻回归 23 OK；全量回归 221 OK，skipped=1；Python 编译、JS 语法和 `git diff --check` 通过。
- [x] 可视化验收：`http://127.0.0.1:8767/?v=20260516-p2s-supervisor-topic1` 显示已确认选题和 SupervisorPlan 审阅台绑定选题；console error=0；截图保存到 `artifacts/ui-checks/p2s-supervisor-topic-binding.png`。
- [x] 下一步 P2-T：已实现 SupervisorPlan approve/reject/needs_revision 审批 API 和前端操作；只有 approved plan 才能进入 Agent Task Queue。

## 2026-05-16 P2-T SupervisorPlan Review State Machine

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-supervisor-plan-review-bdd.md`，定义 SupervisorPlan 人工审批、阻断派工和不可篡改研究状态的行为。
- [x] TDD：扩展 `tests/test_supervisor_plan.py`；首次目标测试失败，原因是缺少 `/supervisor-plan/review` API、review 状态持久化和前端审批按钮。
- [x] 实现：`PUT /api/v1/projects/{project_id}/supervisor-plan/review` 支持 `approve`、`needs_revision`、`reject`，写入 `human_review`、`can_dispatch` 和下一步动作。
- [x] 实现：审批只更新 `state/product/supervisor_plan.json`，不会改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。
- [x] 前端：首页 `SupervisorPlan 审阅台` 在存在计划时显示 `批准计划`、`要求修改`、`驳回计划`，并用 `可进入任务队列` / `不可派工` 明确结果。
- [x] 保护性验证：目标测试 13 OK；相邻回归 28 OK；全量回归 226 OK，skipped=1；Python 编译、JS 语法、`git diff --check` 通过。
- [x] 可视化验收：本地服务运行在 `http://127.0.0.1:8767/?v=20260516-p2t-supervisor-review1`；当前真实项目尚未生成 `supervisor_plan.json`，页面正确显示 `尚未生成` 和 `生成 SupervisorPlan`；截图保存到 `artifacts/ui-checks/p2t-supervisor-review-page.png`。
- [ ] 下一步 P2-U：把 approved SupervisorPlan 拆成 Agent Task Queue，显示 owner agent、输入证据、输出要求、阻塞项和状态；未 approved 的计划必须继续阻断。

## 2026-05-17 P2-U Agent Task Queue

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-agent-task-queue-bdd.md`，定义 approved SupervisorPlan 才能创建可审阅任务队列。
- [x] TDD：新增 `tests/test_agent_task_queue.py`；首次目标测试 8 条失败，失败原因是缺少 API、持久化服务和前端队列面板。
- [x] 实现：新增 `Product/backend/agent_task_queue_service.py`，从 `status=approved` 且 `can_dispatch=true` 的 SupervisorPlan 生成 `state/product/agent_task_queue.json`。
- [x] 实现：扩展 `Product/app.py`，新增 `GET/POST /api/v1/projects/{project_id}/agent-task-queue`；未生成计划、未批准计划和空 `subagent_dispatch` 都返回结构化 409。
- [x] 实现：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，首页新增 `Agent 任务队列`，默认展示摘要、阻塞、负责人和任务状态，任务详情用 `details/summary` 按需展开。
- [x] 保护性边界：创建队列只写 `state/product/agent_task_queue.json`，不执行子 Agent，不改写 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。
- [x] 自动验证：`python3 -m unittest tests.test_agent_task_queue -v` 8 tests OK；`python3 -m unittest discover -s tests -v` 234 tests OK，skipped=1；Python 编译、JS 语法和 `git diff --check` 通过。
- [x] 浏览器验收：真实项目在无 approved SupervisorPlan 时显示 `缺少 SupervisorPlan` 且创建按钮 disabled；受控 approved-plan 场景点击创建后显示 2 个任务、2 个详情默认折叠、无 console error；截图保存到 `/tmp/empirical-workbench-agent-task-queue-p2u-final.png` 和 `/tmp/empirical-workbench-agent-task-queue-p2u-approved.png`。
- [ ] 下一步 P2-V：把 approved Agent Task Queue 推进到“人工派工 / 执行前审计”状态；仍不能自动启动子 Agent 或绕过任务级人工检查。

## 2026-05-25 P2-AB Topic-first Auto Research CLI

- [x] BDD：锁定 `auto-research` 本地高效工作流主入口，默认追求 best-available execution，而不是 fallback-first dry-run。
- [x] 边界：CNKI / Web / Zotero / StatsPAI / LLM Supervisor / agentmemory 都是可用则启用；不可用时局部降级并写入 capability evidence，不能静默失败。
- [x] 边界：所有自动产物默认 `exploratory` / `draft` / `needs_human_review`，不能自动晋升正式变量、正式设计、正式 RunPlan 或正式引用。
- [x] TDD：新增 `tests/test_auto_research_cli.py`；首次 RED 失败原因为 `Product/cli.py` 尚无 `auto-research` 子命令。
- [x] 实现：新增 `Product.backend.auto_research_service.run_auto_research()`，复用 `create_run_workspace()` 和现有 evidence inventory。
- [x] CLI：新增 `python3 Product/cli.py auto-research --topic ... --mode auto --max-depth 2 --max-iterations 5`。
- [x] 兼容：治理层新增 transient runtime project 解析，允许 CLI 直接指向未注册本地项目，同时不污染 Product 全局 registry。
- [x] 验证：目标测试、相邻 CLI 回归、Python 编译检查通过。
- [ ] 全量风险：`python3 -m unittest discover -s tests -v` 当前 282 tests 中 17 个前端契约失败，集中在旧 Agent Drawer、首页产品工作区锚点、中文导航契约和 SupervisorPlan 前端面板；需另开前端契约修复轮。

## 2026-05-25 P3-C Intake To Analysis Workspace

- [x] BDD：修订 `docs/architecture-v2/codex-phase-p3-semantic-glow-cards-bdd.md`，锁定“入口页只做输入，提交后才进入分析工作台”的产品规则。
- [x] TDD：新增/修订 `tests/test_p3_semantic_glow_cards.py` 与 `tests/test_p3_react_input_tabs.py`；首次按新规则运行失败，原因是语义卡仍挂在入口页。
- [x] 实现：`App.tsx` 拆成 `task === null` 的 intake screen 与 `analysis-workspace` 两个状态；首屏只保留标题和研究输入器。
- [x] 实现：新增 `SemanticGlowCards.tsx`，提交后把题目拆成研究对象、数据线索、方法线索、证据缺口和下一步任务五张 draft-only 卡。
- [x] 实现：`ResearchCommandInput` 支持 `onDraftChange`，但输入器内部不渲染语义卡，避免入口页信息过载。
- [x] 视觉：GlowCard 改为黑白灰低对比 spotlight，卡片只在分析页出现；分析页标题收敛为工作台标题尺寸。
- [x] 类型：补齐 `@types/react`、`@types/react-dom`、`@types/three`，让 React 子项目可跑 `npx tsc --noEmit`。
- [x] 验证：目标 React 契约 12 tests OK；`npx tsc --noEmit` 通过；`npm run build` 通过；Playwright 入口页 `initialCards=0`、提交后 `analysisCards=5`。
- [ ] 下一步 P3-D：把分析页拆成真正的阶段页面容器；不同阶段再接不同 UI 组件和真实工作流，不再把所有分析塞在一个页面。

## 2026-05-25 P3-D Task Brief Demo

- [x] 写 BDD：任务书阶段页、右侧 Inspector、语义卡后置、draft-only 边界。
- [x] 写失败测试：`tests/test_p3_task_brief_demo.py`。
- [x] 实现 `TaskBriefDemo` 低保真阶段页。
- [x] App 增加 `activeStage`，默认进入任务书；切换到其他阶段后才显示语义卡。
- [x] 增加黑白灰 task brief / inspector 样式。
- [x] 运行目标测试、类型检查、build 和 Playwright 验收。
- [ ] 下一步：围绕“任务书页”进入 grill-me，确认主屏 5 个信号是否合适、右侧 Inspector 是否应该改成抽屉或固定栏。

# P4-A Paper Package Quality BDD

日期：2026-05-26

## 目标

把真实数据 CLI 运行产物升级为可审阅的论文包。

一个 paper package 至少包含：

- 长篇论文草稿。
- PDF 或 PDF 预检结果。
- 文献综述闭环产物。
- 方法规范门报告。
- 复现脚本和 manifest。
- 质量报告。

## 行为 1：CLI 必须生成 paper quality report

**Given** 用户已经运行真实 `run_paper.py` 并生成 Markdown / Quarto 草稿  
**When** 用户运行 paper package quality check  
**Then** 系统写出 `Results/json/paper_quality_report.json`  
**And** 报告包含 `profile`、`word_count`、`format_checks`、`section_checks`、`citation_checks`、`method_gate_checks`、`revision_checks`、`verdict`  
**And** 报告写入 manifest 或导出预检可以读取的位置。

业务规则：PDF 是否生成成功只代表导出链路可用；paper quality report 才回答这篇论文包现在差什么。

## 行为 1.1：AER-like 档位必须启用投稿元数据硬门

**Given** 用户或 Supervisor 将论文包目标设为 `aer_like`  
**When** 系统生成 quality report  
**Then** `format_checks` 必须检查摘要是否超过 100 words  
**And** 必须检查 JEL codes、keywords、Data Availability Statement  
**And** 如果缺失或超限，`verdict` 包含 `format_gate_required`  
**And** `recommended_next_tasks` 包含 `fix_submission_metadata`。

业务规则：AER-like 不是一句口号，而是一个会改变 CLI 验收结果的质量档。

## 行为 2：长度和结构必须进入质量报告

**Given** 草稿正文短于 working paper 门槛  
**When** 系统生成 quality report  
**Then** `verdict` 包含 `too_thin`  
**And** `section_checks` 明确列出缺失章节或过短章节  
**And** `recommended_next_tasks` 包含扩写 Introduction、Literature、Data、Empirical Strategy、Results 或 Robustness 的任务。

业务规则：论文可以先生成短草稿，但短草稿必须自动进入扩写队列。

## 行为 2.1：章节存在但篇幅不足也必须进入质量门

**Given** 草稿总字数已经超过 working paper 最低门槛
**And** Literature、Data、Empirical Strategy、Results 或 Robustness 等核心章节只是占位文本
**When** 系统生成 quality report
**Then** `section_length_checks` 必须逐章给出英文词数、中文字符数、目标区间和状态
**And** 低于章节最低门槛的章节状态为 `too_short`
**And** `verdict` 包含 `section_length_gate_required`
**And** `recommended_next_tasks` 包含 `expand_underdeveloped_sections`，并列出需要扩写的具体章节
**And** 该任务必须包含 `section_expansion_packet`，把每个薄弱章节的目标篇幅、证据要求、草案输出路径和正式层写回边界交给 ManuscriptAgent。
**And** `paper_package.py` 必须把 `section_expansion_packet` 原样带入 `paper_expansion_plan.json.agent_task_queue`
**And** `paper_expansion_plan.json.manuscript_section_task_packets` 必须展开出每个薄弱章节的 ManuscriptAgent 草案任务，供后续章节写作 worker 直接消费。

业务规则：论文不能靠堆长某一个章节通过验收；每个核心研究章节都要达到可审阅的最小厚度。

## 行为 3：文献综述必须检查 bibliography 闭环

**Given** 项目存在或缺失 `verified_bibliography.csv` 与 `contribution_matrix.md`  
**When** 系统生成 quality report  
**Then** `citation_checks` 必须显示 Zotero / DOI / CNKI / local PDF 的校验状态  
**And** 如果缺少已校验文献，`verdict` 包含 `needs_literature_review`  
**And** 报告给出 LiteratureAgent 下一步任务。

业务规则：文献综述章节需要引用库和贡献矩阵支撑，不能只靠自然语言生成。

## 行为 4：方法规范门必须进入主链路

**Given** RunPlan 使用 OLS、DID、IV、RDD、PSM 或 DML  
**When** 系统生成 quality report  
**Then** `method_gate_checks` 读取或生成对应方法门状态  
**And** 如果方法门缺失，`verdict` 包含 `method_gate_required`  
**And** 报告列出需要补的 pre-checks 和 diagnostics。

业务规则：方法门在正式估计之前发生，也必须在论文包导出前可见。

## 行为 5：审稿式修订循环必须留下记录

**Given** 系统已经生成 draft、finding、reviewer scorecard 或 export preflight  
**When** 系统生成 quality report  
**Then** `revision_checks` 必须记录当前是否存在 reviewer scorecard、revision log、writeback preflight  
**And** 如果缺少审稿记录，报告给出 ReviewerAgent 下一步任务。

业务规则：论文草稿进入更高水平版本，需要审稿意见、修订记录和再次生成。

## 行为 6：PDF 导出必须读取 paper quality report

**Given** `paper_quality_report.json` 已存在  
**When** 用户运行 `Program/export_pdf.py --preflight-only` 或正式导出  
**Then** export manifest 包含 paper quality report 的路径和 verdict  
**And** 复现脚本包含重新运行 quality check 的命令。

业务规则：PDF 是论文包的展示物，必须绑定质量报告和复现命令。

## 行为 7：论文包主链路必须生成 LLM Supervisor 上下文包

**Given** paper quality report 已经指出论文包还缺文献、方法门、审稿循环或章节扩写  
**When** 用户运行 `Program/paper_package.py`  
**Then** 系统必须写出 `Results/json/paper_supervisor_context.json`  
**And** 上下文包必须列出 quality report、扩写计划、结构化草稿、ResearchQuestion、DesignSpec、RunPlan 和真实执行结果等可用来源  
**And** 上下文包必须明确 `local_codex` 是研究中控，`statspai`、`python`、`stata_mcp` 是执行后端  
**And** 上下文包必须生成可交给本地 Codex Supervisor 的任务提示词和 Agent Task Queue。

业务规则：Python 脚本不替代 AI 中控。脚本负责整理证据、质量门和可复现执行；LLM Supervisor 负责研究路线、派工、文献判断、方法升级、审稿式修订和写作推进。

## 行为 8：本地 Codex Supervisor 执行必须显式开关、持久化、可审阅

**Given** `Results/json/paper_supervisor_context.json` 已经存在  
**When** 用户运行 `Program/paper_supervisor.py`  
**Then** 如果未启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`，系统必须结构化阻断，不能写出假的 Supervisor 结果  
**And** 如果执行开关已启用，本地 Codex 必须读取上下文包并生成 `docs/workflows/paper_package_supervisor/supervisor_round.md`  
**And** 系统必须写出 `Results/json/paper_supervisor_run.json`，记录 provider、上下文路径、原始输出路径、Agent Task Queue、verdict、人工确认状态和正式层写回边界  
**And** 该命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。

业务规则：LLM Supervisor 是研究中控入口，但它的第一层输出仍是草案层和 proposal 层；正式变量、设计、运行计划和论文正式层必须通过后续人工确认或显式写回命令。

## 行为 9：变量角色调和只能生成 proposal，不能静默改写正式层

**Given** 用户已经确认 ResearchQuestion，项目同时存在已批准的 VariableRoleSet、DesignSpec 和 RunPlan  
**And** VariableRoleSet 仍指向旧样本或旧变量角色，但 DesignSpec / RunPlan 已指向真实研究数据和真实方法设定  
**When** 用户运行 variable role reconciliation  
**Then** 系统必须写出 `state/proposals/variable_role_reconciliation.json` 和 `Results/json/variable_role_reconciliation_report.json`  
**And** proposal 必须列出正式变量角色与 DesignSpec / RunPlan / 数据字段之间的冲突  
**And** proposal 必须给出建议变量角色、证据来源、缺失证据、方法风险和 Agent Team 后续分工  
**And** proposal 的状态必须是 `needs_human_review`，`formal_state_write.can_promote` 必须为 `false`  
**And** 命令不得改写 `state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。

业务规则：Auto Mode 可以根据真实字段和专家方法库提出变量角色修订建议，但不能把启发式或中控模型判断直接写成正式研究设定。正式变量角色必须经过人工确认或显式 promotion 命令。

## 行为 10：LiteratureAgent 必须生成可被质量门读取的文献包

**Given** 用户已经确认 ResearchQuestion，项目存在 DesignSpec、RunPlan 或变量角色调和 proposal  
**When** 用户运行 literature package builder  
**Then** 系统必须写出 `Data/literature/processed/candidate_literature.csv`、`Data/literature/processed/verified_bibliography.csv`、`Data/literature/processed/contribution_matrix.md` 和 `Results/json/literature_package_report.json`  
**And** `verified_bibliography.csv` 至少包含 5 条 `verification_status != needs_manual_review` 的文献记录  
**And** `contribution_matrix.md` 必须把 `source_id` 绑定到贡献角色、使用章节、变量/方法证据和与本研究的差异  
**And** literature package report 必须列出 CNKI 人工辅助检索队列、Zotero/DOI/OpenAlex 等校验线索、缺失证据和 Agent Team 调用节奏  
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。

业务规则：文献综述不是一段自然语言，而是一组可追踪来源、贡献矩阵和引用证据。第一版可以用 seed literature package 启动，但必须把 CNKI / Zotero / DOI 校验状态和人工补证路径显式写出。

## 行为 11：MethodAgent 必须把 IV / Bartik 方法规范门写成可审阅报告

**Given** 用户已经确认 DesignSpec 和 RunPlan，并且 RunPlan 使用 Bartik / shift-share 风格 IV  
**When** 用户运行 method gate builder  
**Then** 系统必须写出 `Results/json/method_gate_report.json`  
**And** 报告必须包含 `method_family`、`method_subtype`、`gate_status`、`variables`、`pre_checks`、`diagnostics`、`required_evidence`、`blocking_items`、`recommended_next_tasks` 和 `agent_team_schedule`  
**And** 对当前 Bartik IV，如果一阶段 F 和 partial R² 已存在但 reduced form、弱工具稳健推断、shift-share 专项诊断和排除限制人工审阅仍缺失，`gate_status` 必须是 `yellow`  
**And** 报告必须声明 Agent Team 的调用、收回和再次调用节奏  
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。

业务规则：方法门不是简单判断“能不能跑回归”，而是把可机器检查的前置条件、需要执行补证的诊断、必须人工/LLM 审阅的识别假设分开。第一版 MethodGate 只写草案层报告，让 paper quality、ReviewerAgent 和后续执行器读取，不直接改正式研究设定。

## 行为 12：ExecutionAgent 必须把 MethodGate 的 yellow 缺口推进为真实方法诊断产物

**Given** 用户已经确认 DesignSpec 和 RunPlan，并且 MethodGate 对 Bartik IV 给出 `yellow` 状态
**When** 用户运行 method diagnostics builder
**Then** 系统必须写出 `Results/json/method_diagnostics_report.json`
**And** 报告必须包含 `method_family`、`method_subtype`、`variables`、`dataset_profile`、`diagnostics`、`source_artifacts`、`reproducibility`、`formal_state_write` 和 `agent_team_schedule`
**And** 系统必须真实估计 `baseline_iv_2sls_binding`、`first_stage_relevance`、`reduced_form`、`ols_comparison`、`sample_consistency` 和 `artifact_binding`
**And** 对当前只有聚合后 `bartik_iv` 的数据，`shift_share_identification_diagnostics`、`shift_share_rotemberg_weights` 和行业级 `leave_one_out` 必须保留为可审阅缺口，而不能用省份级稳健性伪装成 shift-share 专项诊断
**And** 报告必须声明 Agent Team 的第一次调用、执行诊断后的收回、以及 ReviewerAgent 二次审阅的再次调用节奏
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。

业务规则：方法诊断执行层负责把“能从当前数据真实跑出来的诊断”落成可复跑产物；需要文献判断、share/shock 原始组件或人工识别叙事的部分保留为审阅任务。这个阶段推进草稿层证据质量，但不静默提升正式研究设定。

## 行为 13：ReviewerAgent 必须读取真实方法诊断并生成审稿评分卡

**Given** `method_diagnostics_report.json` 和 `method_gate_report.json` 已存在
**When** 用户运行 reviewer scorecard builder
**Then** 系统必须写出 `Results/json/reviewer_scorecard_report.json`
**And** 评分卡必须覆盖 `execution_binding`、`instrument_relevance`、`weak_iv_and_inference_robustness`、`bartik_identification_credibility`、`sample_and_reporting_transparency`
**And** `reduced_form`、`first_stage_relevance`、`artifact_binding` 已完成时不得继续列为缺失
**And** 弱工具稳健区间、Bartik share/shock 组件、Rotemberg weights、leave-one-out、排他性论证和样本流失解释必须转成 revision tasks
**And** 当前 yellow 状态允许继续草稿层，但必须阻断不带 caveat 的强因果表述和正式导出
**And** 评分卡必须声明 Agent Team 的调用、收回和再次调用节奏
**And** 命令不得写入 `state/product/reviewer_scorecard.json` 或自动改写 Agent Task Queue。

业务规则：审稿评分卡不是空泛评价。它必须把真实诊断产物转成“可以写草稿 / 不可正式声称 / 下一轮谁来补证据”的产品状态。

## 行为 14：PDF 导出预检必须绑定论文质量门和审稿评分卡

**Given** `paper_quality_report.json` 和 `reviewer_scorecard_report.json` 已存在
**When** 用户运行 `Program/export_pdf.py --preflight-only` 或正式导出
**Then** export manifest 必须包含 paper quality report 的路径、verdict 和 recommended next tasks
**And** manifest 必须包含 reviewer scorecard 的路径、总分、总体判定、正式导出阻断状态和 revision tasks
**And** 当 scorecard 标记 `blocks_export_or_formal_claims=true` 或 quality report 仍存在质量门缺口时，manifest 必须写出 `export_gate.can_export_pdf=false`
**And** manifest 必须合并写出下一轮 `next_review_tasks`，作为 ManuscriptAgent / ReviewerAgent / VerifierAgent 后续任务入口
**And** PDF review doc 必须显示“论文包审阅入口”、质量报告、审稿评分卡和下一轮任务
**And** manifest 必须声明 Agent Team 调用节奏：ExportAgent 在预检前调用 ReviewerAgent / VerifierAgent；manifest 写出后收回；只有进入正式写回或最终导出前才再次调用。

业务规则：PDF 预检不只是排版检查。它要把“现在能否进入正式论文包”和“下一轮谁补什么证据”写成可复核的产品状态。

## 行为 15：PDF 预检的下一轮任务必须进入 Supervisor / Agent 队列

**Given** PDF export manifest 已经写出 `next_review_tasks`、`export_gate` 和 `agent_team_schedule`
**When** 用户运行 `Program/paper_package.py --source-manifest <manifest>`
**Then** `paper_expansion_plan.json` 必须把 manifest 中的 `next_review_tasks` 合并进 `agent_task_queue`
**And** 每个来自 manifest 的任务必须保留 `source=pdf_export_manifest`、`source_artifact`、负责人 Agent、输入证据、动作建议和审阅状态
**And** `paper_supervisor_context.json` 必须把 export manifest 加入 `context_sources`
**And** Supervisor 上下文必须声明 Agent Team 调用节奏：读取 export manifest 前调用 ReviewerAgent / VerifierAgent；合并到 expansion plan 和 supervisor context 后收回；进入正式层写回前再次调用。

业务规则：上一轮 PDF 预检不能停留在“报告已经指出问题”。它必须把问题转成下一轮可派工任务，让 LiteratureAgent、MethodAgent、ManuscriptAgent、ReviewerAgent 和 VerifierAgent 各自处理自己的缺口。

## 行为 16：Supervisor / Agent 队列必须生成审稿式修订轮次

**Given** `paper_expansion_plan.json` 已经包含 `agent_task_queue` 和 `agent_team_schedule`
**And** `paper_supervisor_context.json` 已经列出 LLM Supervisor 上下文来源和正式层写回边界
**When** 用户运行 `Program/paper_revision_round.py`
**Then** 系统必须写出 `Results/json/paper_revision_round.json` 和 `Reviews/paper_revision_round.md`
**And** revision round 必须按 Agent 分组生成 `agent_packets`，每个任务保留来源、输入证据、动作建议、验收证据和状态
**And** 每个任务必须进入 `queued_for_revision`，不能停留在一段自然语言建议
**And** revision round 必须声明 `draft_layer_only=true`、`formal_writeback_allowed=false`
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`
**And** revision round 必须写明 Agent Team 调用节奏：生成 revision round 前调用 ReviewerAgent / VerifierAgent / MethodAgent；写出 round manifest 和 review doc 后收回；执行任务或正式层写回前再次调用。

业务规则：Agent Task Queue 不是最终工作成果。它必须被转换成一轮可审阅、可派工、可验收的 revision round，后续 P4-H/P5 才能消费这些任务并产出真实补证材料。

## 行为 16.1：薄弱章节必须生成 ManuscriptAgent 章节工单

**Given** `paper_expansion_plan.json` 已经包含 `manuscript_section_task_packets`
**When** 用户运行 `Program/paper_revision_round.py`
**Then** `paper_revision_round.json` 必须写出 `manuscript_section_work_orders`
**And** 每个章节工单必须保留章节名、草案输出路径、所需证据、写作指令、验收条件和来源任务
**And** 系统必须写出 `Reviews/agent_packets/manuscriptagent/sections/{section}.md`
**And** 章节工单必须声明 `draft_layer_only=true`、`formal_writeback_allowed=false`、`can_write_product_state=false`
**And** 命令不得改写 `state/product/*` 正式层文件。

业务规则：章节扩写不能停在 JSON 里的嵌套字段。ManuscriptAgent 需要拿到一份能打开、能审阅、能逐项验收的章节工单，然后再进入下一轮真实写作或证据绑定。

## 行为 16.2：章节工单必须生成草案层章节入口

**Given** `paper_revision_round.json` 已经包含 `manuscript_section_work_orders`
**And** 每个工单已经给出 `draft_output_path`、所需证据、写作指令和验收条件
**When** 用户运行 `Program/manuscript_section_scaffold.py`
**Then** 系统必须写出 `Results/json/manuscript_section_scaffold_report.json`
**And** 系统必须写出 `Reviews/manuscript_section_scaffold.md`
**And** 系统必须为每个章节写出 `Manuscripts/sections/{section}.md`
**And** 每个章节文件必须保留章节标题、来源工单、证据清单、验收条件和 `## 草案正文`
**And** scaffold report 必须声明 `status=section_scaffolds_ready`、`draft_layer_only=true`、`formal_writeback_allowed=false`
**And** report 必须写明 Agent Team 调用节奏：章节入口 manifest 写出后调用 ManuscriptAgent；章节草案文件写出后收回；证据绑定扩写前再次调用 ManuscriptAgent
**And** 命令不得改写 `state/product/*` 正式层文件。

业务规则：章节工单只是任务说明，章节入口才是 ManuscriptAgent 真正工作的文件表面。P6-G5 只把工单落到草案层章节文件，让后续扩写、证据绑定和人工审阅都能围绕稳定文件推进。

## 行为 16.3：章节入口必须绑定到真实证据或显式缺口

**Given** `paper_revision_round.json` 已经包含 `manuscript_section_work_orders`
**And** `manuscript_section_scaffold_report.json` 已经写出章节入口
**And** 项目中已经存在部分章节所需的真实 artifact，例如回归表、approved finding、文献包、方法门或变量画像
**When** 用户运行 `Program/manuscript_section_evidence_bindings.py`
**Then** 系统必须写出 `Results/json/manuscript_section_evidence_bindings.json`
**And** 系统必须写出 `Reviews/manuscript_section_evidence_bindings.md`
**And** 每个章节都必须列出 required evidence 的绑定结果：已找到的证据给出路径、bytes、sha256 和 evidence level；未找到的证据进入 `missing_evidence`
**And** Main Results 等能找到主表和 approved findings 的章节必须把 `main_regression_table`、`approved_findings`、`coefficient_interpretation` 绑定到真实本地 artifact
**And** report 必须声明 `draft_layer_only=true`、`formal_writeback_allowed=false`
**And** report 必须写明 Agent Team 调用节奏：证据绑定报告写出后调用 ManuscriptAgent / VerifierAgent；章节证据缺口审阅后收回；章节扩写前再次调用 ManuscriptAgent
**And** 命令不得改写 `state/product/*` 正式层文件，也不得把缺失证据伪装成已找到。

业务规则：章节草案扩写前要先知道“每段话能引用什么证据”。P6-G6a 不写正文，只建立章节到真实 artifact 的证据索引，并把缺口留给后续 Agent 或人工补证。

## 行为 16.4：章节草案扩写必须只消费已绑定证据

**Given** `manuscript_section_evidence_bindings.json` 已经把 Main Results 的主表、approved findings 和系数解释绑定到真实 artifact
**When** 用户运行 `Program/manuscript_section_draft_expansion.py --section "Main Results"`
**Then** 系统必须更新 `Manuscripts/sections/main-results.md` 的草案正文
**And** 系统必须写出 `Results/json/manuscript_section_draft_expansion_report.json`
**And** 系统必须写出 `Reviews/manuscript_section_draft_expansion.md`
**And** 该章节必须声明 `status=section_draft_expanded`、`draft_layer_only=true`、`formal_writeback_allowed=false`
**And** 草案必须列出它实际消费的 evidence id、路径和 hash，不能把未绑定证据写成既成结论
**And** 如果目标章节仍有 `missing_evidence`，该章节必须阻断扩写并进入人工补证
**And** 该节点仍然不能改写 `state/product/*`

业务规则：章节扩写是 ManuscriptAgent 的草案层写作动作。它可以把真实证据整理成可审阅段落，但每个论断都必须能回到 evidence binding；正式层写回仍等待人工确认。

## 行为 16.5：章节语义核验必须反查草案论断和已消费证据

**Given** `manuscript_section_draft_expansion_report.json` 已经写出 Main Results 的草案扩写记录
**And** `Manuscripts/sections/main-results.md` 已经列出 consumed evidence 和草案正文
**When** 用户运行 `Program/manuscript_section_semantic_review.py --section "Main Results"`
**Then** 系统必须写出 `Results/json/manuscript_section_semantic_review.json`
**And** 系统必须写出 `Reviews/manuscript_section_semantic_review.md`
**And** review 必须声明 `draft_layer_only=true`、`formal_writeback_allowed=false`
**And** review 必须逐条检查已消费证据是否在章节中声明、章节是否仍停留草案层、核心 claim 是否能回到已绑定 evidence id
**And** review 必须给出 `passed` / `needs_revision` 的 section verdict 和下一步建议
**And** 该节点不得改写章节正文或 `state/product/*` 正式层文件。

业务规则：扩写完不能直接继续堆正文。VerifierAgent 要先把“这段话是否有证据来源”讲清楚，防止 ManuscriptAgent 把草案写得越来越像正式结论却缺少反查路径。

## 行为 16.6：通过语义核验的章节必须生成可审阅论断账本

**Given** `manuscript_section_semantic_review.json` 已经声明 Main Results 通过语义核验
**And** Main Results 章节草案仍停留在草案层
**When** 用户运行 `Program/manuscript_section_claim_ledger.py --section "Main Results"`
**Then** 系统必须写出 `Results/json/manuscript_section_claim_ledger.json`
**And** 系统必须写出 `Reviews/manuscript_section_claim_ledger.md`
**And** 每条 claim 必须包含 claim text、section、source finding、bound evidence ids、review status 和 next action
**And** ledger 必须声明 `draft_layer_only=true`、`formal_writeback_allowed=false`
**And** ledger 不得改写章节正文或 `state/product/*` 正式层文件。

业务规则：论文写作不能只靠一段自然语言草案往前滚。通过核验的章节要沉淀成“论断-证据-下一步”的账本，后续扩写、审稿和 PDF 预检都从同一份账本读取。

## 行为 16.7：缺少已审批论断文本时不得编造 claim

**Given** `approved_findings.json` 中存在已审批 finding
**But** 该 finding 还没有 `claim` 或 `claim_text`
**And** Main Results 章节草案仍停留在草案层
**When** 用户运行 `Program/manuscript_section_claim_ledger.py --section "Main Results"`
**Then** 系统必须写出 claim ledger
**And** ledger 必须进入 `claim_ledger_needs_revision`
**And** 对应 section 必须记录 `no_approved_finding_claim_detected_in_section`
**And** 系统不得从章节正文或回归表里自动编造 claim
**And** ledger 不得改写章节正文或 `state/product/*` 正式层文件。

业务规则：真实项目里 approved finding 可能先有运行证据和审批状态，但还没沉淀成一句可进入论文的论断。此时系统要暴露缺口，让 VerifierAgent / ManuscriptAgent 回到草案层补齐，而不是替用户生成正式论断。

## 行为 16.8：缺少已审批论断文本时必须生成草案论断提案

**Given** `approved_findings.json` 中存在已审批 finding
**But** 该 finding 还没有 `claim` 或 `claim_text`
**And** 章节语义核验已经通过
**And** 已消费证据中存在主回归表，包含处理变量系数、标准误、p 值和样本量
**When** 用户运行 `Program/manuscript_section_claim_ledger.py --section "Main Results"`
**Then** claim ledger 必须保留 `claim_ledger_needs_revision`
**And** section 必须生成 `claim_proposals`
**And** 每条 proposal 必须包含 proposed claim text、source finding、source table、coefficient、standard error、p value、nobs 和 bound evidence ids
**And** proposal 的 `review_status` 必须是 `needs_human_review`
**And** proposal 不得进入 `claims`
**And** ledger 不得改写章节正文或 `state/product/*` 正式层文件。

业务规则：缺 claim 不能让流程停在“发现问题”。系统应把真实回归证据整理成可审阅的草案论断提案，让用户或 VerifierAgent 判断是否批准为正式 finding claim。提案不是正式结论，必须保留人工审阅门。

## 行为 16.9：草案论断提案必须经过显式人工审阅才能进入下一步

**Given** `manuscript_section_claim_ledger.json` 中存在 `claim_proposals`
**And** proposal 的 `review_status` 是 `needs_human_review`
**When** 用户显式提交 `approve`、`reject` 或 `needs_revision` 审阅动作
**Then** 系统必须写出独立的 claim proposal review ledger
**And** ledger 必须记录 proposal id、审阅动作、审阅人、审阅备注、来源 finding、来源表和 proposed claim text
**And** `approve` 只能把 proposal 标记为 `approved_for_promotion`
**And** 本步骤不得把 proposal 直接写入 `claims`
**And** 本步骤不得改写 `approved_findings.json`、章节草案或 `state/product/*` 正式层文件。

业务规则：人工同意是进入下一步的门槛，不等于本节点已经完成正式论断写回。这样可以把“人类判断”变成可审计的状态，而不是在代码里静默把草案升格成正式结论。

## 行为 16.10：已批准草案论断只能先生成正式层补丁提案

**Given** `manuscript_claim_proposal_review.json` 的状态是 `claim_proposal_approved_for_promotion`
**And** `promotion_allowed` 是 `true`
**When** 系统准备把该 proposal 进入正式 finding claim
**Then** 系统必须先写出独立的 claim promotion patch
**And** patch 必须记录目标文件、目标 finding、proposal id、来源表、拟写入 claim 文本和人工审阅证据
**And** 本步骤不得直接修改 `approved_findings.json`
**And** 本步骤不得改写章节草案或 `state/product/*` 正式层文件。

业务规则：`approve` 之后进入的是“可应用补丁”，不是静默写回。论文状态像 Git 一样先产生 patch，再由后续显式 apply 节点进入正式层。

## 行为 17：审稿式修订轮次必须生成可验收证据包

**Given** `paper_revision_round.json` 已经包含多个 `queued_for_revision` Agent task
**And** 部分 task 能绑定到存在的本地 artifact、hash、schema 或可定位字段
**And** 部分 task 只有 `reason`、`recommended_action` 或 handoff 文本，尚未绑定真实证据
**When** 用户运行 `Program/paper_revision_evidence_packets.py`
**Then** 系统必须写出 `Results/json/paper_revision_evidence_packets.json`
**And** 每个 task 都必须写出 `Reviews/agent_packets/{agent}/{task_id}.md` 草案层证据包
**And** 能绑定真实 artifact 的 task 状态必须是 `evidence_packet_ready`
**And** 只有自然语言建议、缺少 artifact/hash/schema/字段证据的 task 状态必须是 `needs_manual_review`
**And** manifest 必须声明 `draft_layer_only=true`、`formal_writeback_allowed=false`
**And** 命令不得改写原始 `paper_revision_round.json`
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`
**And** manifest 必须写明 Agent Team 调用节奏：证据包执行前调用各任务归属 Agent；证据包写出后收回；重跑质量门、方法门、审稿门或正式写回前再次调用 ReviewerAgent / VerifierAgent。

业务规则：revision round 不是一组待办事项。进入下一轮质量门之前，每条任务都必须变成可打开、可追溯、可判定的证据包；没有真实证据的任务也要明确标成需要人工审阅，而不是用写得像证据的建议文本蒙混过关。

## 行为 18：修订证据包必须进入质量门复核账本

**Given** `paper_revision_evidence_packets.json` 已经列出每条修订任务的 evidence packet 状态
**And** 每条任务都声明了下一轮质量门、方法门、审稿门或导出预检需要读取的 `gate_recompute_inputs`
**When** 用户运行 `Program/paper_revision_gate_recompute.py`
**Then** 系统必须写出 `Results/json/paper_revision_gate_recompute.json`
**And** 每条任务必须被标记为 `cleared`、`still_blocking` 或 `manual_review_required`
**And** `needs_manual_review` 的 evidence packet 必须进入 `manual_review_required`
**And** gate 输入缺失的任务必须进入 `still_blocking`
**And** 证据包 ready、gate 输入完整、且当前质量门/审稿门/导出门不再引用该任务时必须进入 `cleared`
**And** gate 输入齐全且证据包 ready 的任务必须进入 `cleared`
**And** 命令不得改写 `paper_revision_evidence_packets.json`
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`
**And** 复核账本必须写明 Agent Team 调用节奏：重跑 gate 前调用 ReviewerAgent / VerifierAgent；账本写出后收回；正式层写回预检前再次调用。

业务规则：P4-I 不是继续生成更多建议，而是把 P4-H 的证据包变成下一轮门控判断。系统必须明确哪些任务已具备进入正式写回预检的证据，哪些仍阻塞，哪些需要人工补证。旧质量门、审稿门或导出门里保留的历史任务引用，不能在证据包已就绪后继续形成重复阻塞。

## 行为 19：下一轮任务生产器必须消费质量门复核账本

**Given** `paper_revision_gate_recompute.json` 已经写出上一轮修订任务的复核结果
**And** PDF export manifest 或 paper quality report 仍包含上一轮任务 id
**When** 用户运行 `Program/paper_package.py --source-manifest <manifest>`
**Then** `paper_expansion_plan.json` 的 `agent_task_queue` 不得重新加入已有 `previous_status=evidence_packet_ready` 的任务
**And** `manual_review_required` 的任务必须保留在 `agent_task_queue`
**And** 被保留的人工任务必须标明来源是 `paper_revision_gate_recompute`
**And** `paper_supervisor_context.json` 必须把 `Results/json/paper_revision_gate_recompute.json` 加入 `context_sources`
**And** 任务生产器不得改写 `paper_revision_gate_recompute.json`
**And** 任务生产器不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`

业务规则：P4-I1 的复核账本必须真的进入下一轮生产器。系统不能一边生成证据包，一边在下一轮又把同一批已具备证据的任务重新塞回队列；但需要人工补证的任务必须继续留在队列里。

## 行为 20：证据包必须识别文献包的 canonical 路径

**Given** `build_literature_package` 的任务输入仍使用短文件名 `verified_bibliography.csv` 与 `contribution_matrix.md`
**And** 文献包已经写入 canonical 草案路径 `Data/literature/processed/verified_bibliography.csv` 与 `Data/literature/processed/contribution_matrix.md`
**When** 用户运行 `Program/paper_revision_evidence_packets.py`
**Then** `paper_revision_evidence_packets.json` 中 `build_literature_package` 必须进入 `evidence_packet_ready`
**And** 证据项路径必须指向 `Data/literature/processed/verified_bibliography.csv` 与 `Data/literature/processed/contribution_matrix.md`
**And** `missing_evidence` 必须为空
**And** 命令不得改写正式层 `state/product/*`

业务规则：P4-C 已经把文献包写入 `Data/literature/processed/`。P4-H/P4-I 不能因为历史任务输入使用短文件名，就误判文献证据缺失；证据收集层必须把短文件名映射到 canonical 草案路径。

### Behavior 21: Gate recompute consumes stale task references once evidence packets are ready

**Given** `paper_revision_evidence_packets.json` 中上一轮修订任务均为 `evidence_packet_ready`
**And** 旧 `paper_quality_report.json`、`reviewer_scorecard_report.json` 或 PDF export manifest 仍在结构化任务列表中保留这些 task id
**When** 用户运行 `Program/paper_revision_gate_recompute.py`
**Then** gate 输入齐全的任务必须标记为 `cleared`
**And** 旧 gate 引用必须写入 `consumed_gate_matches` 作为审计线索
**And** `gate_matches` 不得再把这些旧引用当作阻塞项
**And** 系统不得改写正式层 `state/product/*.json`
**And** 下一步必须进入 `formal_writeback_preflight`

业务规则：当证据包已经准备好，旧 gate 里的 task id 只说明“当时要求过这项修订”，不等于“现在仍阻塞”。P4-I4 的职责是消费这些历史引用，形成可审计账本，并把真正的正式写回检查留给独立 preflight 节点。

### Behavior 22: Formal writeback preflight creates a human-reviewable writeback preview without changing formal state

**Given** `paper_revision_gate_recompute.json` 的状态是 `ready_for_formal_writeback_preflight`
**And** 每条上一轮修订任务都已经是 `cleared`
**When** 用户运行 `Program/formal_writeback_preflight.py`
**Then** 系统必须写出 `Results/json/formal_writeback_preflight.json`
**And** 系统必须写出 `Reviews/formal_writeback_preflight.md`
**And** 系统必须写出草案层 `Manuscripts/generated/previews/formal_writeback_preflight.md`
**And** 预检账本必须列出将进入正式层人工审批的章节扩写、引用/文献、方法叙述、结果表与复现说明
**And** 预检账本必须声明 `draft_layer_only=true`、`formal_writeback_allowed=false`、`requires_human_approval=true`
**And** 命令不得改写 `paper_revision_gate_recompute.json`
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`
**And** 预检账本必须写明 Agent Team 调用节奏：正式写回预检前调用 ReviewerAgent / VerifierAgent；预检账本写出后收回；人工批准后才进入 P5 formal package。

业务规则：P4-J 不是直接把草稿写进正式论文，而是把“将要写什么、证据在哪里、还有哪些正式审批条件”列成可审阅预览。用户确认后才进入 P5 的正式 paper package。

### Behavior 23: Human approval records a formal package entry decision without writing formal state

**Given** `formal_writeback_preflight.json` 的状态是 `ready_for_human_approval`
**And** 预检账本已经列出章节扩写、引用/文献、方法叙述、结果表与复现说明的写回范围
**When** 用户运行 `Program/formal_writeback_approval.py --action approve`
**Then** 系统必须把批准记录写入 `state/product/writeback_approvals.json`
**And** 系统必须写出 `Results/json/formal_writeback_approval.json`
**And** 系统必须写出 `Reviews/formal_writeback_approval.md`
**And** 批准账本必须声明 `can_enter_p5=true`
**And** 批准账本必须保留旧的候选段落写回审批键 `approvals`
**And** 命令不得改写 `formal_writeback_preflight.json`
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`
**And** 如果用户选择 `needs_revision` 或 `reject`，账本必须声明 `can_enter_p5=false`
**And** 如果预检账本没有 ready，系统必须阻断批准并说明阻断原因。

业务规则：P5-A 是正式包入口的人工批准账本。它只记录“是否允许进入 P5”，不生成正式论文、不导出 docx、不改写正式层状态；这样后续 P5 节点可以用同一条批准记录作为正式包生成和导出预检的入口凭证。

### Behavior 24: Formal package manifest builds an approved package skeleton without writing final outputs

**Given** `formal_writeback_approval.json` 的状态是 `approved_for_p5`
**And** `state/product/writeback_approvals.json` 中存在 `formal_preflight_approvals.formal_writeback_preflight.status=approved`
**When** 用户运行 `Program/formal_paper_package_manifest.py`
**Then** 系统必须写出 `Results/json/formal_paper_package_manifest.json`
**And** 系统必须写出 `Reviews/formal_paper_package_manifest.md`
**And** 系统必须创建 `Submissions/formal_package/` 的空包骨架目录
**And** manifest 必须把章节扩写、引用/文献、方法叙述、结果表与复现说明映射到正式包目录
**And** manifest 必须声明 `can_build_package=true`
**And** manifest 必须声明本命令没有生成最终 PDF、docx 或正式正文
**And** 命令不得改写 `formal_writeback_approval.json`
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`
**And** 如果批准报告或批准账本缺失、拒绝或不一致，系统必须阻断正式包骨架生成并说明原因。

业务规则：P5-B 是正式 paper package 的目录和清单入口。它把人工批准后的写回范围组织成可复核的包结构，但仍不写最终论文、不导出 PDF/docx，也不改研究设定。

### Behavior 25: Formal manuscript source assembly maps package sections into source placeholders without exporting the paper

**Given** `formal_paper_package_manifest.json` 的状态是 `formal_package_manifest_ready`
**And** manifest 声明 `can_build_package=true`
**When** 用户运行 `Program/formal_manuscript_source_assembly.py`
**Then** 系统必须写出 `Results/json/formal_manuscript_source_map.json`
**And** 系统必须写出 `Reviews/formal_manuscript_source_map.md`
**And** 系统必须写出 `Submissions/formal_package/manuscript/section_sources.json`
**And** 系统必须为正式论文必需章节创建草案源占位文件
**And** 每个章节源必须声明目标长度、负责 Agent、输入证据和当前状态
**And** 源装配清单必须声明本命令没有生成最终 PDF、docx 或正式正文
**And** 命令不得改写 `formal_paper_package_manifest.json`
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`
**And** 如果 manifest 缺失、不 ready、或正式包目录结构不完整，系统必须阻断源装配并说明原因。

业务规则：P5-C 把 P5-B 的正式包骨架推进到“可以被 ManuscriptAgent / LiteratureAgent / MethodAgent / ExecutionAgent 分工填写”的源文件层。它只创建章节源清单和占位文件，方便下一步 PDF 预检识别缺口；它不生成最终 PDF/docx，也不把草案内容写成正式论文。

### Behavior 26: Formal PDF export preflight checks manuscript sources and evidence before rendering

**Given** `formal_manuscript_source_map.json` 的状态是 `formal_manuscript_sources_ready`
**And** `section_sources.json` 已列出正式论文必需章节
**When** 用户运行 `Program/formal_pdf_export_preflight.py`
**Then** 系统必须写出 `Results/json/formal_pdf_export_preflight.json`
**And** 系统必须写出 `Reviews/formal_pdf_export_preflight.md`
**And** 系统必须写出 `Submissions/formal_package/reproducibility/pdf_export_preflight_tasks.json`
**And** 预检必须逐章检查章节源是否仍是占位、目标长度是否声明、必需证据是否存在
**And** 预检必须把缺失章节内容、缺失证据和复现缺口转成下一轮 Agent 任务
**And** 当任一章节仍是占位或任一必需证据缺失时，`can_export_pdf_candidate=false`
**And** 当所有章节源和必需证据通过时，`can_export_pdf_candidate=true`
**And** 命令不得生成最终 PDF、docx 或正式正文
**And** 命令不得改写 `formal_manuscript_source_map.json`、`section_sources.json` 或正式研究状态文件
**And** 如果 source map 缺失、不 ready、或章节源索引缺失，系统必须阻断 PDF 预检并说明原因。

业务规则：P5-D 是 PDF-first 导出前的证据验收台。它决定“现在能不能进入 PDF 导出审阅”，并把不能导出的原因拆成 Agent 可执行任务；它不渲染 PDF，也不把草案变成正式终稿。

### Behavior 27: Formal evidence registry resolver maps existing artifacts before asking agents to recreate evidence

**Given** `formal_pdf_export_preflight.json` 的状态是 `blocked_by_source_gaps`
**And** 预检报告中存在 `required_evidence_missing`
**When** 用户运行 `Program/formal_evidence_registry_resolver.py`
**Then** 系统必须写出 `Results/json/formal_evidence_registry_resolution.json`
**And** 系统必须写出 `Reviews/formal_evidence_registry_resolution.md`
**And** 系统必须写出 `Submissions/formal_package/reproducibility/evidence_registry_patch_proposal.json`
**And** resolver 必须把缺失证据分为 `direct_alias_available`、`derivable_from_existing_artifact`、`missing_after_scan`
**And** resolver 必须优先识别当前仓库中已经存在的正式状态、审稿账本、方法执行结果、文献包和质量报告
**And** resolver 只能生成 patch proposal，不得直接改写 PDF 预检报告、章节源、正式研究状态或 canonical evidence registry
**And** 每个 patch proposal 必须声明建议绑定路径、证据来源、负责 Agent 和是否需要人工确认。

业务规则：P5-E1 先减少无谓返工。系统在要求 Agent 补证据前，必须先扫描当前仓库已有产物，把“其实已经存在但名字没对上”的材料登记成可审查提案；真正缺失的证据才进入后续生成节点。

### Behavior 28: Formal evidence materializer writes high-confidence evidence files without mutating formal state

**Given** `evidence_registry_patch_proposal.json` 已经把 `variable_role_set`、`sample_profile` 和 `regression_tables` 标记为可直接绑定或可由现有产物派生
**When** 用户运行 `Program/formal_evidence_materializer.py --evidence-ids variable_role_set,sample_profile,regression_tables`
**Then** 系统必须写出 `Results/json/formal_evidence_materialization_report.json`
**And** 系统必须写出 `Reviews/formal_evidence_materialization.md`
**And** 系统必须写出 `Submissions/formal_package/evidence/variable_role_set.json`
**And** 系统必须写出 `Results/json/sample_profile.json`
**And** 系统必须写出 `Results/json/regression_tables.json`
**And** `variable_role_set` 证据只能从现有 `state/product/variable_roles.json` 或 proposal 派生为正式包证据副本，不得改写 `state/product/variable_role_set.json`
**And** 如果变量角色数据路径与真实方法执行数据路径不一致，报告必须写出 `variable_role_dataset_mismatch` warning 并保留人工审阅状态
**And** `sample_profile` 必须从真实 `method_execution_result` 的 `data_preflight` 和样本量派生
**And** `regression_tables` 必须从真实 `method_execution_result` 的系数、标准误、统计量、诊断和公式派生
**And** 报告必须声明 `this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`。

业务规则：P5-E2a 只把最高置信、可从现有真实产物派生的证据落成目标文件，让 PDF 预检能读取；正式变量角色和研究设定仍由人工确认或后续显式写回命令处理。

### Behavior 29: Formal evidence materializer turns method diagnostics into reviewable figure, robustness and limitation evidence

**Given** `evidence_registry_patch_proposal.json` 已经把 `figure_manifest`、`robustness_matrix` 和 `limitations_register` 标记为可由现有产物派生
**And** 当前仓库已经存在方法诊断、方法门、审稿评分和结果目录
**When** 用户运行 `Program/formal_evidence_materializer.py --evidence-ids figure_manifest,robustness_matrix,limitations_register`
**Then** 系统必须写出 `Results/json/figure_manifest.json`
**And** 系统必须写出 `Results/json/robustness_matrix.json`
**And** 系统必须写出 `Results/json/limitations_register.json`
**And** `figure_manifest` 必须显式记录当前是否已有真实图表文件；如果没有图表文件，状态必须是可审阅的 `no_rendered_figures_registered`，而不是伪造图表
**And** `robustness_matrix` 必须从真实 `method_diagnostics_report`、`method_gate_report` 和可用稳健性产物派生，通过项、黄灯项、人工审阅项必须分开记录
**And** `limitations_register` 必须从真实 `reviewer_scorecard_report` 和 `method_gate_report` 派生，保留 formal claim / export blocker 与人工确认标记
**And** 报告必须声明 `this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`
**And** 命令不得改写正式研究状态、章节源、最终 PDF/docx 或 canonical evidence registry。

业务规则：P5-E2b 把“已有方法诊断和审稿意见”沉淀成 PDF 预检可以读取的正式包证据。它不补跑新回归，不替用户确认局限，也不把没有生成的图表说成已经存在；它只把现有真实证据整理成可审阅、可追踪、可进入下一轮任务分解的结构化文件。

### Behavior 30: Formal evidence materializer turns approved reviews and literature package into reviewable finding, citation and context evidence

**Given** `evidence_registry_patch_proposal.json` 已经把 `approved_findings`、`citation_verification_log`、`domain_notes` 和 `verified_context_sources` 标记为可由现有产物派生
**And** 当前仓库已经存在 finding review、文献包、verified bibliography、candidate literature、source registry 和研究问题状态
**When** 用户运行 `Program/formal_evidence_materializer.py --evidence-ids approved_findings,citation_verification_log,domain_notes,verified_context_sources`
**Then** 系统必须写出 `Results/json/approved_findings.json`
**And** 系统必须写出 `Results/json/citation_verification_log.json`
**And** 系统必须写出 `Results/json/domain_notes.json`
**And** 系统必须写出 `Results/json/verified_context_sources.json`
**And** `approved_findings` 必须只从已批准 finding review 和对应产物路径派生，不得把未批准发现写成正式可用结论
**And** `citation_verification_log` 必须从 verified bibliography 和文献包派生，保留 DOI、验证状态和人工复核状态
**And** `domain_notes` 必须把研究问题、数据语境、方法语境、CNKI 人工检索队列和文献缺口整理成可审阅领域笔记
**And** `verified_context_sources` 必须登记本地数据根目录、Zotero/PDF/CNKI 等来源通道和候选文献/已验证书目的计数
**And** 报告必须声明 `this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`
**And** 命令不得改写正式研究状态、章节源、最终 PDF/docx 或 canonical evidence registry。

业务规则：P5-E2c 把“已经过审的发现、文献验证和上下文来源”接入 PDF 预检读取路径。它不生成新文献结论，不把 CNKI 人工队列说成已完成，也不替用户批准正式引用；它只把现有真实材料整理成可审阅证据文件。

### Behavior 31: Formal section source drafter turns placeholders into evidence-bound draft sources

**Given** PDF 导出预检已经只剩 `section_source_placeholders_remaining` 阻断
**And** `formal_manuscript_source_map.json` 与 `section_sources.json` 已经列出全部必需章节源
**And** 每个章节要求的证据文件已经存在于 evidence registry 对应路径
**When** 用户运行 `Program/formal_section_source_drafter.py`
**Then** 系统必须写出 `Results/json/formal_section_source_draft_report.json`
**And** 系统必须写出 `Reviews/formal_section_source_draft.md`
**And** 系统必须把 `Submissions/formal_package/manuscript/section_sources.json` 中全部章节状态更新为 `source_draft_ready`
**And** 系统必须把每个章节 markdown 从占位内容改写为绑定证据路径的章节源草案
**And** 每个章节 markdown 不得保留 `source_placeholder_ready` 或 `章节源占位`
**And** `formal_manuscript_source_map.json` 中的章节状态必须同步为 `source_draft_ready`
**And** 报告必须列出每个章节的 evidence bindings、Agent 分工和下一步 PDF preflight 动作
**And** 报告必须声明 `this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`
**And** 命令不得改写 `state/product/*` 正式状态、不得生成最终 PDF/docx、不得批准 canonical 方法库或正式论文层。

业务规则：P5-E2d 把“已齐备证据 + 章节源占位”推进为可预检的章节源草案。它让 PDF-first 候选渲染有真实章节输入，但仍把正式论文写回、最终 PDF/docx 和 canonical 规则合并留给后续人工确认节点。

### Behavior 32: Formal PDF candidate renderer turns approved draft sources into a review PDF candidate

**Given** `formal_pdf_export_preflight.json` 已经声明 `can_export_pdf_candidate=true`
**And** `formal_manuscript_source_map.json` 与 `section_sources.json` 已经列出全部 `source_draft_ready` 章节源
**And** 每个章节源已经绑定所需 evidence paths
**When** 用户运行 `Program/formal_pdf_candidate.py`
**Then** 系统必须写出 `Results/json/formal_pdf_candidate_report.json`
**And** 系统必须写出 `Reviews/formal_pdf_candidate.md`
**And** 系统必须写出 `Submissions/formal_package/manuscript/paper_candidate.qmd`
**And** 在本机 PDF 工具链可用时，系统必须写出 `Submissions/formal_package/paper_candidate.pdf`
**And** 系统必须写出可复跑脚本 `Submissions/formal_package/reproducibility/render_pdf_candidate.sh`
**And** 报告必须列出 preflight report、source map、章节源、QMD 候选稿、PDF 候选稿、渲染日志和人工审阅入口
**And** 如果预检未通过，命令必须阻断渲染并写出 `blocked_by_pdf_preflight` 报告
**And** 报告必须声明 `candidate_layer_only=true`、`this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`
**And** 命令不得改写 `state/product/*` 正式状态、不得批准最终 PDF/docx、不得合并 canonical 方法库。

业务规则：P5-E3 把“章节源草案 + PDF 预检通过”推进为可人工验收的 PDF 候选稿。它解决的是审阅和排版闭环，不替用户批准正式层，不把候选 PDF 宣称为最终投稿稿。

### Behavior 33: Formal PDF candidate review creates a final-writeback preflight without promotion

**Given** `formal_pdf_candidate_report.json` 的状态是 `pdf_candidate_ready`
**And** `paper_candidate.pdf` 与 `paper_candidate.qmd` 已经存在
**And** 候选报告声明 `candidate_layer_only=true`、`this_command_wrote_formal_state=false`
**When** 用户运行 `Program/formal_pdf_candidate_review.py`
**Then** 系统必须写出 `Results/json/formal_pdf_candidate_review.json`
**And** 系统必须写出 `Reviews/formal_pdf_candidate_review.md`
**And** 系统必须写出 `Results/json/formal_pdf_final_writeback_preflight.json`
**And** review report 必须登记 PDF 候选稿、QMD 候选源、原始 candidate report、PDF metadata、章节清单、机器审阅检查和人工审阅入口
**And** final-writeback preflight 必须声明 `requires_human_approval=true`、`final_writeback_allowed=false`、`can_request_final_approval=true`
**And** 如果候选 PDF 缺失、候选报告未 ready 或正式层 guard 已变化，命令必须阻断为 `blocked_by_pdf_candidate_review`
**And** 报告必须声明 `candidate_layer_only=true`、`this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`
**And** 命令不得改写 `state/product/*` 正式状态、不得移动或复制候选 PDF 为最终 PDF、不得批准最终 PDF/docx、不得合并 canonical 方法库。

业务规则：P5-E4 把“PDF 候选稿已经生成”推进为“可进入最终批准讨论”的审阅证据，而不是直接发布最终论文。它给用户和 Reviewer/Verifier 留出明确验收入口，并为下一节点的最终批准或修订建立结构化 preflight。

### Behavior 34: Human final approval authorizes final writeback without creating final outputs

**Given** `formal_pdf_final_writeback_preflight.json` 的状态是 `ready_for_human_final_approval`
**And** 预检账本声明 `can_request_final_approval=true`、`requires_human_approval=true`、`final_writeback_allowed=false`
**And** 候选 PDF 与候选 QMD 已经存在
**When** 用户运行 `Program/formal_pdf_final_approval.py --action approve`
**Then** 系统必须把批准记录写入 `state/product/writeback_approvals.json`
**And** 系统必须保留旧的候选段落写回审批键 `approvals`
**And** 系统必须写出 `Results/json/formal_pdf_final_approval.json`
**And** 系统必须写出 `Reviews/formal_pdf_final_approval.md`
**And** 批准账本必须声明 `status=approved_for_final_writeback`、`can_enter_p6=true`、`final_writeback_authorized=true`
**And** 批准账本必须声明 `this_command_wrote_final_outputs=false`、`this_command_wrote_formal_state=false`
**And** 命令不得移动、复制或重命名 `paper_candidate.pdf`
**And** 命令不得生成最终 `paper.pdf`、`paper.docx` 或正式正文
**And** 命令不得改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/variable_role_set.json`、`state/product/design_spec.json`、`state/product/run_plan.json`、`state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json`
**And** 如果用户选择 `needs_revision` 或 `reject`，账本必须声明 `can_enter_p6=false`、`final_writeback_authorized=false`
**And** 如果最终写回预检没有 ready，系统必须阻断批准并说明阻断原因。

业务规则：P5-E5 是最终 PDF/docx 写回前的人工批准账本。它解决的是“是否允许下一节点写最终产物”，不是自己写最终产物。这样 P6-A 可以只认一条显式批准记录，而不会把候选 PDF 审阅通过误当成最终输出授权。

### Behavior 35: Final PDF writeback promotes the approved candidate into the final package

**Given** `formal_pdf_final_approval.json` 的状态是 `approved_for_final_writeback`
**And** `state/product/writeback_approvals.json` 中 `final_pdf_approvals.formal_pdf_candidate.status=approved`
**And** 候选 PDF 与候选 QMD 路径和最终写回预检一致
**When** 用户运行 `Program/formal_pdf_final_writeback.py`
**Then** 系统必须把 `Submissions/formal_package/paper_candidate.pdf` 复制为 `Submissions/formal_package/paper.pdf`
**And** 系统必须写出 `Results/json/formal_pdf_final_writeback.json`
**And** 系统必须写出 `Reviews/formal_pdf_final_writeback.md`
**And** 报告必须记录候选 PDF 与最终 PDF 的 sha256、bytes 和路径
**And** 报告必须声明 `status=final_pdf_written`、`final_writeback_authorized=true`
**And** 报告必须声明 `this_command_wrote_final_pdf=true`、`this_command_wrote_docx=false`、`this_command_wrote_formal_state=false`
**And** 命令不得修改 `paper_candidate.pdf`、`paper_candidate.qmd`、P5 审批账本或正式研究状态
**And** 命令不得生成 `paper.docx`
**And** 如果最终批准缺失、未通过或候选路径与批准账本不一致，系统必须阻断写回，并不得生成最终 PDF。

业务规则：P6-A 是 PDF-first 的最终产物写回节点。它只把已经人工批准的候选 PDF 晋升到最终包，给用户一个稳定、可打开、可验收的正式 PDF 文件；docx 导出、投稿包压缩和云端同步继续拆到后续节点。

### Behavior 36: Final docx export preflight checks the toolchain without generating docx

**Given** `formal_pdf_final_writeback.json` 的状态是 `final_pdf_written` 或 `final_pdf_already_written`
**And** 最终 PDF、候选 QMD、最终批准报告和批准账本均存在
**And** `pandoc` 工具链可用
**When** 用户运行 `Program/formal_docx_export_preflight.py`
**Then** 系统必须写出 `Results/json/formal_docx_export_preflight.json`
**And** 系统必须写出 `Reviews/formal_docx_export_preflight.md`
**And** 报告必须记录最终 PDF、候选 QMD、预期 docx 路径、导出命令、pandoc 路径和版本
**And** 报告必须声明 `status=ready_for_docx_export`、`can_export_docx=true`
**And** 报告必须声明 `this_command_wrote_docx=false`、`this_command_wrote_formal_state=false`
**And** 命令不得生成 `Submissions/formal_package/paper.docx`
**And** 命令不得修改 `paper.pdf`、`paper_candidate.qmd`、P5/P6 审批账本或正式研究状态
**And** 如果最终 PDF 写回报告未通过、最终 PDF 缺失、候选 QMD 缺失或 `pandoc` 不可用，系统必须阻断为对应状态，并不得生成 docx。

业务规则：P6-B 只回答“能不能进入 docx 导出执行”。它把投稿兼容格式的工具链、输入源和目标路径讲清楚，但不在预检节点实际生成 docx。这样 P6-C 可以只认一份可审计预检报告来执行导出。

### Behavior 37: Final docx export materializes the approved formal docx package

**Given** `formal_docx_export_preflight.json` 的状态是 `ready_for_docx_export`
**And** `can_export_docx=true`
**And** 最终 PDF 与候选 QMD 均存在
**When** 用户运行 `Program/formal_docx_export.py`
**Then** 系统必须生成 `Submissions/formal_package/paper.docx`
**And** 系统必须写出 `Results/json/formal_docx_export.json`
**And** 系统必须写出 `Reviews/formal_docx_export.md`
**And** 报告必须记录预检报告、最终 PDF、候选 QMD、最终 docx、pandoc 日志、docx sha256、bytes 和导出命令
**And** 报告必须声明 `status=docx_exported`
**And** 报告必须声明 `this_command_wrote_docx=true`、`this_command_wrote_pdf=false`、`this_command_wrote_formal_state=false`
**And** 命令不得修改 `paper.pdf`、`paper_candidate.qmd`、P5/P6 审批账本或正式研究状态
**And** 如果 docx 预检未 ready、最终 PDF 缺失、候选 QMD 缺失或 pandoc 导出失败，系统必须写出 blocker 报告，并不得回滚 P6-A 的最终 PDF。

业务规则：P6-C 是正式包的投稿兼容格式导出节点。它只把已经通过 P6-B 预检的候选 QMD 渲染为最终 `paper.docx`，并留下可复核的命令、日志和文件指纹；PDF-first 的正式成果保持不变。

### Behavior 38: Formal submission manifest summarizes the final package for manual acceptance

**Given** `formal_pdf_final_writeback.json` 的状态是 `final_pdf_written` 或 `final_pdf_already_written`
**And** `formal_docx_export_preflight.json` 的状态是 `ready_for_docx_export`
**And** `formal_docx_export.json` 的状态是 `docx_exported`
**And** `Submissions/formal_package/paper.pdf` 与 `Submissions/formal_package/paper.docx` 均存在
**When** 用户运行 `Program/formal_submission_package_manifest.py`
**Then** 系统必须写出 `Results/json/formal_submission_package_manifest.json`
**And** 系统必须写出 `Reviews/formal_submission_package_acceptance.md`
**And** 系统必须写出投稿包内 `Submissions/formal_package/manifest.json`
**And** 报告必须记录 PDF/docx 的路径、bytes、sha256 和来源报告
**And** 报告必须记录 P6-A/P6-B/P6-C 的状态、schema version、阻断原因和一致性检查
**And** 报告必须声明 `status=formal_submission_package_ready`
**And** 报告必须声明 `this_command_rendered_pdf=false`、`this_command_rendered_docx=false`、`this_command_wrote_final_outputs=false`、`this_command_wrote_formal_state=false`
**And** 命令不得修改 `paper.pdf`、`paper.docx`、`paper_candidate.pdf`、`paper_candidate.qmd`、P6-A/P6-B/P6-C 报告、P5/P6 审批账本或正式研究状态
**And** 如果 PDF/docx 缺失、P6-A/P6-B/P6-C 任一报告未 ready/exported，或文件指纹与来源报告不一致，系统必须写出 blocker 报告，并不得写投稿包内 manifest。

业务规则：P6-D 是正式投稿包的“验收清单”节点。它不再生成论文文件，而是把最终 PDF、最终 docx、来源报告、文件指纹、复现命令和人工打开检查合并到一份可审阅 manifest，让用户知道这一包文件是否可以进入人工验收和产品层展示。

### Behavior 39: Formal package summary exposes a compact product acceptance entry point

**Given** `formal_submission_package_manifest.json` 的状态是 `formal_submission_package_ready`
**And** `Submissions/formal_package/manifest.json` 已写入
**And** `paper.pdf` 与 `paper.docx` 的 bytes 和 sha256 与 manifest 记录一致
**When** 用户运行 `Program/formal_submission_package_summary.py`
**Then** 系统必须写出 `Results/json/formal_submission_package_summary.json`
**And** 系统必须写出 `state/product/formal_submission_package_summary.json`
**And** 系统必须写出 `Reviews/formal_submission_package_summary.md`
**And** summary 必须声明 `status=ready_for_manual_acceptance`
**And** summary 必须包含产品层可直接展示的 `visible_summary`、`open_targets`、`manual_acceptance`、`source_manifest`、`consistency_checks` 和 `blocking_reasons`
**And** `open_targets` 必须分别给出 PDF 与 DOCX 的路径、类型、bytes、sha256 和本地打开命令
**And** `manual_acceptance.status` 必须是 `pending_manual_acceptance`
**And** 命令必须声明 `this_command_opened_files=false`、`this_command_rendered_pdf=false`、`this_command_rendered_docx=false`、`this_command_wrote_final_outputs=false`、`this_command_wrote_formal_research_state=false`
**And** 命令不得打开文件、重渲染 PDF/docx、改写最终产物、改写 P6-D manifest 或改写正式研究状态
**And** 如果 P6-D manifest 未 ready、最终文件缺失、包内 manifest 缺失或 PDF/docx 指纹与 manifest 不一致，系统必须写出 blocker summary，并不得给出可点击验收入口。

业务规则：P6-E1 是正式包进入产品层之前的“入口卡片”节点。它只把 P6-D 的长 manifest 归一化为用户能看懂、UI/API 能消费的紧凑验收状态，告诉用户下一步该打开哪两个文件、核对什么证据；真实 HTTP 接口和页面挂载留到 P6-F。

### Behavior 40: Product API exposes the formal package summary as a read-only acceptance surface

**Given** `state/product/formal_submission_package_summary.json` exists
**And** the summary status is `ready_for_manual_acceptance`
**When** the frontend requests `GET /api/v1/projects/{project_id}/formal-submission-package-summary`
**Then** the API must return the summary fields needed by the product acceptance surface: `visible_summary`, `open_targets`, `manual_acceptance`, `source_manifest`, `consistency_checks`, and `blocking_reasons`
**And** the response must mark `service=formal_submission_package_service` and `mode=read_only`
**And** the API must not regenerate PDF/docx, open local files, or mutate `state/product/formal_submission_package_summary.json`

**Given** `state/product/formal_submission_package_summary.json` does not exist
**When** the frontend requests the same API
**Then** the API must return structured `409 formal_submission_package_summary_required`
**And** the error message must direct the caller to generate the P6-E1 summary first.

业务规则：P6-F1 只把已生成的正式包验收摘要接到产品 API，给前端一个确定的读取入口；它不是导出器、审批器、质量评审器，也不改写正式层。

### Behavior 41: React workbench renders the formal package summary as a read-only acceptance bench

**Given** `GET /api/v1/projects/{project_id}/formal-submission-package-summary` returns a summary with `status=ready_for_manual_acceptance`
**And** the summary contains PDF and DOCX `open_targets`
**When** the user reaches the post-execution acceptance surface in the React workbench
**Then** the page must render a formal package acceptance bench
**And** the bench must display visible summary rows, PDF and DOCX open targets, manual acceptance checklist, consistency checks, and blocking reasons
**And** the bench must mark itself as read-only and must not expose a button that approves, rewrites, regenerates, or opens files silently
**And** if the API returns `409 formal_submission_package_summary_required`, the bench must show a recoverable waiting state that tells the user to generate the P6-E1 summary first
**And** the bench must not fake a ready state from mock data when the API is unavailable.

业务规则：P6-F2 把 P6-F1 的只读 API 接到产品页面，让用户在内置浏览器里看见“正式包现在能不能验收、打开哪两个文件、按什么清单验收、有没有阻断原因”。它仍然不是审批节点，不打开本地文件，不重新导出 PDF/docx，也不改写正式层。

## 边界条件

- 没有 Zotero 或 CNKI 权限时，可以生成 literature gap，不阻塞草稿生成。
- AER-like 规则没有被用户选择时，不阻断普通草稿；一旦进入 `aer_like` profile，摘要、JEL、关键词、数据可得性说明进入 hard gate。
- 没有 PDF 工具链时，仍可生成 PDF preflight 和 quality report。
- 真实数据文件不默认复制进 Git；只记录路径、hash、shape 和来源。
- LLM Supervisor 可以生成草案层计划、章节草稿、patch proposal 和审稿意见；正式层论文、canonical 方法库和最终 PDF 必须经过人工确认后写回。
- 本地 Codex 执行默认关闭；CLI 必须把关闭状态作为可解释 blocker，而不是静默降级成 mock。
- Agent Team 调用节奏必须写入 proposal：主线程负责状态合并；DataAgent、MethodAgent、LiteratureAgent 可以并行提出证据包；收回阶段只合并为 proposal 和报告，不直接写正式层。
- 文献包的 Agent Team 调用节奏必须写入 report：候选文献生成后调用 LiteratureAgent、MethodAgent、DataAgent；正式书目被 ManuscriptAgent 引用前收回；主线程只合并为 processed 文献包和质量报告，不直接写正式论文层。
- 方法门的 Agent Team 调用节奏必须写入 report：DesignSpec / RunPlan approved 后调用 MethodAgent、DataAgent 和 ExecutionAgent；method gate report 写出后收回；真实诊断执行后再次调用 MethodAgent 和 ReviewerAgent；主线程只合并为方法门报告和质量报告，不直接写正式层。
- 方法诊断的 Agent Team 调用节奏必须写入 report：MethodGate yellow 且没有 red blockers 后调用 ExecutionAgent；method diagnostics report 写出后收回；MethodAgent 与 ReviewerAgent 只读取摘要和缺口，不接管执行产物或正式层写回。
- 审稿评分的 Agent Team 调用节奏必须写入 report：method diagnostics 写出后再次调用 MethodAgent 和 ReviewerAgent；scorecard report 写出后收回；下一次只在进入 ManuscriptAgent 扩写或 ExportAgent 预检前再次调用 ReviewerAgent/VerifierAgent。
- PDF 导出预检的 Agent Team 调用节奏必须写入 manifest：ExportAgent 在 preflight 前调用 ReviewerAgent/VerifierAgent 读取 quality report 和 scorecard；manifest、review doc 和 reproduce scripts 写出后收回；下一次只在用户批准正式层写回或最终 PDF export 前再次调用。
- 审稿式修订轮次的 Agent Team 调用节奏必须写入 revision round：ReviewerAgent/VerifierAgent/MethodAgent 在 round build 前调用；round manifest 和 review doc 写出后收回；任务执行或正式层写回前再次调用，复核每个 queued task 是否已有验收证据。
- 审稿式修订证据包必须把“建议文本”和“本地结构化证据”分开：存在 artifact/hash/schema/字段引用的任务才能进入 `evidence_packet_ready`；缺少关键证据的任务必须进入 `needs_manual_review`，等待 P4-I 或人工补证。
- 质量门复核账本不能把 `manual_review_required` 任务提升为 `cleared`；人工补证、正式层写回预检和最终导出必须在后续节点处理。

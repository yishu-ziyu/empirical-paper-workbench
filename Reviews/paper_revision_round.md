# 审稿式修订轮次

- Round: `paper_revision_round_e3549c037b`
- Profile: `aer_like`
- 正式层写回：关闭
- 当前状态：等待人工审阅

## Agent Team 调用节奏

- call_when: before_revision_round_build
- called_agents: ['DataAgent', 'ExecutionAgent', 'ExportAgent', 'LiteratureAgent', 'ManuscriptAgent', 'MethodAgent', 'ReviewerAgent', 'VerifierAgent']
- recall_when: after_revision_round_manifest_written
- next_call_when: before_revision_task_execution_or_formal_writeback
- boundary: 生成 revision round 前调用 ReviewerAgent/VerifierAgent/MethodAgent 复核任务、证据和正式层边界；round manifest 和 review doc 写出后收回；执行任务或正式层写回前再次调用，确认验收证据已补齐。

## Agent Packets

### DataAgent

- 任务数：2
- 草案输出目录：`Reviews/agent_packets/dataagent`

#### recover_bartik_share_shock_components

- 来源：pdf_export_manifest
- 来源产物：`Submissions/cfps_robot_pdf_export_manifest.json`
- 动作：恢复或构造 Bartik share/shock 原始组件，避免把聚合 bartik_iv 当作完整 shift-share 诊断。
- 状态：queued_for_revision
- 输入：Submissions/cfps_robot_pdf_export_manifest.json, Results/json/reviewer_scorecard_report.json
- 草案产物：`Reviews/agent_packets/dataagent/recover-bartik-share-shock-components.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed

#### explain_missing_drop_and_analysis_sample

- 来源：pdf_export_manifest
- 来源产物：`Submissions/cfps_robot_pdf_export_manifest.json`
- 动作：解释 raw rows 到 usable rows 的样本流失、缺失处理和外部有效性边界。
- 状态：queued_for_revision
- 输入：Submissions/cfps_robot_pdf_export_manifest.json, Results/json/reviewer_scorecard_report.json
- 草案产物：`Reviews/agent_packets/dataagent/explain-missing-drop-and-analysis-sample.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed

### ExecutionAgent

- 任务数：1
- 草案输出目录：`Reviews/agent_packets/executionagent`

#### add_leave_one_out_or_alternative_shock_check

- 来源：pdf_export_manifest
- 来源产物：`Submissions/cfps_robot_pdf_export_manifest.json`
- 动作：补充 leave-one-out 或 alternative shock 稳健性，不能用普通省级稳健性替代。
- 状态：queued_for_revision
- 输入：Submissions/cfps_robot_pdf_export_manifest.json, Results/json/reviewer_scorecard_report.json
- 草案产物：`Reviews/agent_packets/executionagent/add-leave-one-out-or-alternative-shock-check.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed

### LiteratureAgent

- 任务数：1
- 草案输出目录：`Reviews/agent_packets/literatureagent`

#### build_literature_package

- 来源：paper_quality_report
- 来源产物：`Results/json/paper_expansion_plan.json`
- 动作：补齐 Zotero/CNKI/DOI 证据和贡献矩阵。
- 状态：queued_for_revision
- 输入：verified_bibliography.csv, contribution_matrix.md
- 草案产物：`Reviews/agent_packets/literatureagent/build-literature-package.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed
  - human_review_decision_recorded

### ManuscriptAgent

- 任务数：2
- 草案输出目录：`Reviews/agent_packets/manuscriptagent`

#### expand_working_paper_sections

- 来源：paper_quality_report
- 来源产物：`Results/json/paper_expansion_plan.json`
- 动作：正文结构或篇幅还没有达到 working paper 初稿区间。
- 状态：queued_for_revision
- 输入：Abstract, Introduction, Literature and Contribution, Institutional Background / Theory / Context, Conclusion
- 草案产物：`Reviews/agent_packets/manuscriptagent/expand-working-paper-sections.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed
  - human_review_decision_recorded

#### fix_submission_metadata

- 来源：paper_quality_report
- 来源产物：`Results/json/paper_expansion_plan.json`
- 动作：补齐摘要、JEL、关键词和数据可得性说明，使草稿进入目标投稿规范。
- 状态：queued_for_revision
- 输入：missing_jel, missing_keywords, missing_data_availability_statement
- 草案产物：`Reviews/agent_packets/manuscriptagent/fix-submission-metadata.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed
  - human_review_decision_recorded

### MethodAgent

- 任务数：4
- 草案输出目录：`Reviews/agent_packets/methodagent`

#### run_method_gate

- 来源：paper_quality_report
- 来源产物：`Results/json/paper_expansion_plan.json`
- 动作：在正式估计和论文导出前生成方法规范门报告。
- 状态：queued_for_revision
- 输入：DesignSpec, RunPlan, method_family
- 草案产物：`Reviews/agent_packets/methodagent/run-method-gate.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed
  - human_review_decision_recorded

#### add_weak_iv_robust_interval_or_caveat

- 来源：pdf_export_manifest
- 来源产物：`Submissions/cfps_robot_pdf_export_manifest.json`
- 动作：补充 AR/CLR 等弱工具稳健区间；若当前 exactly identified 设定无法给出，则在主结论中加入因果表述 caveat。
- 状态：queued_for_revision
- 输入：Submissions/cfps_robot_pdf_export_manifest.json, Results/json/reviewer_scorecard_report.json
- 草案产物：`Reviews/agent_packets/methodagent/add-weak-iv-robust-interval-or-caveat.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed

#### add_rotemberg_weights_review

- 来源：pdf_export_manifest
- 来源产物：`Submissions/cfps_robot_pdf_export_manifest.json`
- 动作：在 share/shock 组件可用后计算或审阅 Rotemberg weights。
- 状态：queued_for_revision
- 输入：Submissions/cfps_robot_pdf_export_manifest.json, Results/json/reviewer_scorecard_report.json
- 草案产物：`Reviews/agent_packets/methodagent/add-rotemberg-weights-review.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed

#### write_exclusion_and_shock_exogeneity_review

- 来源：pdf_export_manifest
- 来源产物：`Submissions/cfps_robot_pdf_export_manifest.json`
- 动作：补写排他性限制和 shock exogeneity 的审稿式论证。
- 状态：queued_for_revision
- 输入：Submissions/cfps_robot_pdf_export_manifest.json, Results/json/reviewer_scorecard_report.json
- 草案产物：`Reviews/agent_packets/methodagent/write-exclusion-and-shock-exogeneity-review.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed

### ReviewerAgent

- 任务数：1
- 草案输出目录：`Reviews/agent_packets/revieweragent`

#### run_reviewer_revision_loop

- 来源：paper_quality_report
- 来源产物：`Results/json/paper_expansion_plan.json`
- 动作：形成审稿意见、修订记录和再次生成路径。
- 状态：queued_for_revision
- 输入：paper_draft, paper_quality_report
- 草案产物：`Reviews/agent_packets/revieweragent/run-reviewer-revision-loop.md`
- 验收证据：
  - updated_section_or_diagnostic_artifact
  - reviewer_scorecard_task_cleared
  - export_gate_recomputed
  - human_review_decision_recorded

## 正式层保护

- changed: `False`
- protected paths:
  - `state/product/research_question.json`
  - `state/product/variable_roles.json`
  - `state/product/variable_role_set.json`
  - `state/product/design_spec.json`
  - `state/product/run_plan.json`
  - `state/product/supervisor_plan.json`
  - `state/product/agent_task_queue.json`

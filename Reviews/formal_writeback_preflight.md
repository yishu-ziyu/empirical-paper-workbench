# P4-J 正式写回预检

- Source gate recompute: `Results/json/paper_revision_gate_recompute.json`
- Status: `ready_for_human_approval`
- 正式层写回：关闭
- 人工批准：必需

## 写回范围

### 章节扩写

- Category: `sections`
- Approval status: `pending_human_approval`
- Task ids: expand_working_paper_sections, fix_submission_metadata
- Evidence refs:
  - `Reviews/agent_packets/manuscriptagent/expand-working-paper-sections.md` (local_file)
  - `Reviews/agent_packets/manuscriptagent/fix-submission-metadata.md` (local_file)
  - `Manuscripts/generated/paper_package_draft.md` (local_file)

### 引用与文献

- Category: `citations`
- Approval status: `pending_human_approval`
- Task ids: build_literature_package
- Evidence refs:
  - `Reviews/agent_packets/literatureagent/build-literature-package.md` (local_file)
  - `Data/literature/processed/verified_bibliography.csv` (local_file)
  - `Data/literature/processed/contribution_matrix.md` (local_file)

### 方法叙述

- Category: `method_narrative`
- Approval status: `pending_human_approval`
- Task ids: run_method_gate, add_weak_iv_robust_interval_or_caveat, add_rotemberg_weights_review, write_exclusion_and_shock_exogeneity_review
- Evidence refs:
  - `Reviews/agent_packets/methodagent/run-method-gate.md` (local_file)
  - `Reviews/agent_packets/methodagent/add-weak-iv-robust-interval-or-caveat.md` (local_file)
  - `Reviews/agent_packets/methodagent/add-rotemberg-weights-review.md` (local_file)
  - `Reviews/agent_packets/methodagent/write-exclusion-and-shock-exogeneity-review.md` (local_file)
  - `Results/json/method_gate_report.json` (local_file)
  - `Results/json/method_diagnostics_report.json` (local_file)

### 结果表与样本说明

- Category: `result_tables`
- Approval status: `pending_human_approval`
- Task ids: add_leave_one_out_or_alternative_shock_check, recover_bartik_share_shock_components, explain_missing_drop_and_analysis_sample
- Evidence refs:
  - `Reviews/agent_packets/executionagent/add-leave-one-out-or-alternative-shock-check.md` (local_file)
  - `Reviews/agent_packets/dataagent/recover-bartik-share-shock-components.md` (local_file)
  - `Reviews/agent_packets/dataagent/explain-missing-drop-and-analysis-sample.md` (local_file)
  - `Results/json/method_execution_result.json` (local_file)
  - `Results/json/project_snapshot.json` (local_file)

### 复现说明

- Category: `reproducibility`
- Approval status: `pending_human_approval`
- Task ids: run_reviewer_revision_loop
- Evidence refs:
  - `Reviews/agent_packets/revieweragent/run-reviewer-revision-loop.md` (local_file)
  - `Results/json/reviewer_scorecard_report.json` (local_file)
  - `Submissions/cfps_robot_pdf_export_manifest.json` (local_file)
  - `Results/json/paper_quality_report.json` (local_file)

## Agent Team 调用节奏

- call_when: before_formal_writeback_preflight
- called_agents: ['ReviewerAgent', 'VerifierAgent', 'ManuscriptAgent', 'LiteratureAgent', 'MethodAgent', 'ExecutionAgent', 'ExportAgent']
- recall_when: after_formal_writeback_preflight_written
- next_call_when: after_human_approval_before_p5_formal_package
- boundary: Agent Team 只复核写回范围、证据和风险；正式写回由 P5 在人工批准后执行。

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

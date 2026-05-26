# P4-I 质量门复核账本

- Source evidence manifest: `Results/json/paper_revision_evidence_packets.json`
- Status: `needs_revision_work`
- 正式层写回：关闭

## 状态计数

- cleared: 0
- still_blocking: 10
- manual_review_required: 1

## Task Results

### expand_working_paper_sections

- Agent: `ManuscriptAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: paper_quality_report, pdf_export_manifest
- Missing gate inputs: none
- Missing evidence: 0

### fix_submission_metadata

- Agent: `ManuscriptAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: paper_quality_report, pdf_export_manifest
- Missing gate inputs: none
- Missing evidence: 0

### build_literature_package

- Agent: `LiteratureAgent`
- Previous status: `needs_manual_review`
- Recompute status: `manual_review_required`
- Reason: Evidence packet still requires human or external-source review.
- Blocking sources: none
- Missing gate inputs: none
- Missing evidence: 2

### run_method_gate

- Agent: `MethodAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: paper_quality_report, pdf_export_manifest
- Missing gate inputs: none
- Missing evidence: 0

### run_reviewer_revision_loop

- Agent: `ReviewerAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: paper_quality_report, pdf_export_manifest
- Missing gate inputs: none
- Missing evidence: 0

### add_weak_iv_robust_interval_or_caveat

- Agent: `MethodAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: pdf_export_manifest, reviewer_scorecard_report
- Missing gate inputs: none
- Missing evidence: 0

### recover_bartik_share_shock_components

- Agent: `DataAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: pdf_export_manifest, reviewer_scorecard_report
- Missing gate inputs: none
- Missing evidence: 0

### add_rotemberg_weights_review

- Agent: `MethodAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: pdf_export_manifest, reviewer_scorecard_report
- Missing gate inputs: none
- Missing evidence: 0

### add_leave_one_out_or_alternative_shock_check

- Agent: `ExecutionAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: pdf_export_manifest, reviewer_scorecard_report
- Missing gate inputs: none
- Missing evidence: 0

### write_exclusion_and_shock_exogeneity_review

- Agent: `MethodAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: pdf_export_manifest, reviewer_scorecard_report
- Missing gate inputs: none
- Missing evidence: 0

### explain_missing_drop_and_analysis_sample

- Agent: `DataAgent`
- Previous status: `evidence_packet_ready`
- Recompute status: `still_blocking`
- Reason: Current gate artifacts still reference this revision task.
- Blocking sources: pdf_export_manifest, reviewer_scorecard_report
- Missing gate inputs: none
- Missing evidence: 0

## Agent Team 调用节奏

- call_when: before_revision_gate_recompute
- called_agents: ['DataAgent', 'ExecutionAgent', 'LiteratureAgent', 'ManuscriptAgent', 'MethodAgent', 'ReviewerAgent', 'VerifierAgent']
- recall_when: after_revision_gate_recompute_written
- next_call_when: before_formal_writeback_preflight
- boundary: P4-I1 只把 P4-H evidence packet 与当前质量门、方法门、审稿门、导出门产物对齐；各 Agent 的修复任务、外部文献补证和正式层写回放到后续节点。

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

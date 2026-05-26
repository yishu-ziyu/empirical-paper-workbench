# P4-H 证据包汇总

- Source revision round: `Results/json/paper_revision_round.json`
- Status: `ready_for_gate_recompute`
- 正式层写回：关闭

## 状态计数

- evidence_packet_ready: 10
- needs_manual_review: 1

## Agent Team 调用节奏

- call_when: before_revision_evidence_execution
- called_agents: ['DataAgent', 'ExecutionAgent', 'LiteratureAgent', 'ManuscriptAgent', 'MethodAgent', 'ReviewerAgent', 'VerifierAgent']
- recall_when: after_revision_evidence_packets_written
- next_call_when: before_quality_gate_recompute_or_formal_writeback
- boundary: 按 revision round 的 Agent packet 并行生成 evidence packet；每个 Agent 只写自己的草案层证据包；MainAgent 收回后合并 manifest，进入质量门重跑或正式层写回前再调用 ReviewerAgent / VerifierAgent 复核。

## Task Results

### expand_working_paper_sections

- Agent: `ManuscriptAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/manuscriptagent/expand-working-paper-sections.md`
- Evidence items: 3
- Missing evidence: 0

### fix_submission_metadata

- Agent: `ManuscriptAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/manuscriptagent/fix-submission-metadata.md`
- Evidence items: 3
- Missing evidence: 0

### build_literature_package

- Agent: `LiteratureAgent`
- Status: `needs_manual_review`
- Evidence packet: `Reviews/agent_packets/literatureagent/build-literature-package.md`
- Evidence items: 2
- Missing evidence: 2

### run_method_gate

- Agent: `MethodAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/methodagent/run-method-gate.md`
- Evidence items: 4
- Missing evidence: 0

### run_reviewer_revision_loop

- Agent: `ReviewerAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/revieweragent/run-reviewer-revision-loop.md`
- Evidence items: 5
- Missing evidence: 0

### add_weak_iv_robust_interval_or_caveat

- Agent: `MethodAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/methodagent/add-weak-iv-robust-interval-or-caveat.md`
- Evidence items: 4
- Missing evidence: 0

### recover_bartik_share_shock_components

- Agent: `DataAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/dataagent/recover-bartik-share-shock-components.md`
- Evidence items: 4
- Missing evidence: 0

### add_rotemberg_weights_review

- Agent: `MethodAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/methodagent/add-rotemberg-weights-review.md`
- Evidence items: 4
- Missing evidence: 0

### add_leave_one_out_or_alternative_shock_check

- Agent: `ExecutionAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/executionagent/add-leave-one-out-or-alternative-shock-check.md`
- Evidence items: 4
- Missing evidence: 0

### write_exclusion_and_shock_exogeneity_review

- Agent: `MethodAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/methodagent/write-exclusion-and-shock-exogeneity-review.md`
- Evidence items: 4
- Missing evidence: 0

### explain_missing_drop_and_analysis_sample

- Agent: `DataAgent`
- Status: `evidence_packet_ready`
- Evidence packet: `Reviews/agent_packets/dataagent/explain-missing-drop-and-analysis-sample.md`
- Evidence items: 4
- Missing evidence: 0

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

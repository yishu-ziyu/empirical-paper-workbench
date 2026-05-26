# Formal Writeback Preview

这份预览只用于人工审阅，不写入正式层。

## 章节扩写

- 审批问题：是否把扩写后的章节结构纳入正式 paper package？
- 当前状态：pending_human_approval
- 证据：
  - `Reviews/agent_packets/manuscriptagent/expand-working-paper-sections.md`
  - `Reviews/agent_packets/manuscriptagent/fix-submission-metadata.md`
  - `Manuscripts/generated/paper_package_draft.md`

## 引用与文献

- 审批问题：是否接受当前文献清单、贡献矩阵和引用边界？
- 当前状态：pending_human_approval
- 证据：
  - `Reviews/agent_packets/literatureagent/build-literature-package.md`
  - `Data/literature/processed/verified_bibliography.csv`
  - `Data/literature/processed/contribution_matrix.md`

## 方法叙述

- 审批问题：是否把方法门诊断和识别边界写入正式方法章节？
- 当前状态：pending_human_approval
- 证据：
  - `Reviews/agent_packets/methodagent/run-method-gate.md`
  - `Reviews/agent_packets/methodagent/add-weak-iv-robust-interval-or-caveat.md`
  - `Reviews/agent_packets/methodagent/add-rotemberg-weights-review.md`
  - `Reviews/agent_packets/methodagent/write-exclusion-and-shock-exogeneity-review.md`
  - `Results/json/method_gate_report.json`
  - `Results/json/method_diagnostics_report.json`

## 结果表与样本说明

- 审批问题：是否把当前结果表、样本口径和数据诊断纳入正式结果章节？
- 当前状态：pending_human_approval
- 证据：
  - `Reviews/agent_packets/executionagent/add-leave-one-out-or-alternative-shock-check.md`
  - `Reviews/agent_packets/dataagent/recover-bartik-share-shock-components.md`
  - `Reviews/agent_packets/dataagent/explain-missing-drop-and-analysis-sample.md`
  - `Results/json/method_execution_result.json`
  - `Results/json/project_snapshot.json`

## 复现说明

- 审批问题：是否进入 P5 正式包并生成复现交付材料？
- 当前状态：pending_human_approval
- 证据：
  - `Reviews/agent_packets/revieweragent/run-reviewer-revision-loop.md`
  - `Results/json/reviewer_scorecard_report.json`
  - `Submissions/cfps_robot_pdf_export_manifest.json`
  - `Results/json/paper_quality_report.json`

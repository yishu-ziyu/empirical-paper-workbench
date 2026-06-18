# 章节证据绑定索引

- 状态：`section_evidence_bindings_ready`
- 来源 round：`Results/json/paper_revision_round.json`
- 来源 scaffold：`Results/json/manuscript_section_scaffold_report.json`
- 正式层写回：关闭

## 汇总

- 章节数：9
- 已绑定证据：27
- 缺失证据：0

## Agent Team 调用节奏

- call_when: after_evidence_binding_report_written
- called_agents: ['ManuscriptAgent', 'VerifierAgent']
- recall_when: after_section_evidence_gaps_reviewed
- next_call_when: before_section_draft_expansion
- boundary: 证据索引已准备；下一步只允许基于 bound evidence 扩写草案，对 missing evidence 先补证或人工确认。

## 章节

### Abstract

- 状态：`evidence_bound`
- `approved_findings`: `bound` -> `Results/json/approved_findings.json`
- `method_gate_report`: `bound` -> `Results/json/method_gate_report.json`
- `verified_bibliography.csv`: `bound` -> `Data/literature/processed/verified_bibliography.csv`

### Introduction

- 状态：`evidence_bound`
- `research_question`: `bound` -> `state/product/research_question.json`
- `contribution_matrix.md`: `bound` -> `Data/literature/processed/contribution_matrix.md`
- `approved_findings`: `bound` -> `Results/json/approved_findings.json`

### Literature and Contribution

- 状态：`evidence_bound`
- `verified_bibliography.csv`: `bound` -> `Data/literature/processed/verified_bibliography.csv`
- `contribution_matrix.md`: `bound` -> `Data/literature/processed/contribution_matrix.md`
- `closest_papers`: `bound` -> `Data/literature/processed/contribution_matrix.md`

### Institutional Background / Theory / Context

- 状态：`evidence_bound`
- `domain_notes`: `bound` -> `Results/json/domain_notes.json`
- `mechanism_hypotheses`: `bound` -> `Results/json/domain_notes.json`
- `literature_context`: `bound` -> `Results/json/literature_package_report.json`

### Conclusion

- 状态：`evidence_bound`
- `approved_findings`: `bound` -> `Results/json/approved_findings.json`
- `limitations_register`: `bound` -> `Results/json/limitations_register.json`
- `reviewer_scorecard_report`: `bound` -> `Results/json/reviewer_scorecard_report.json`

### Data and Measurement

- 状态：`evidence_bound`
- `dataset_profile`: `bound` -> `Results/json/sample_profile.json`
- `variable_dictionary`: `bound` -> `Results/json/variable_role_reconciliation_report.json`
- `sample_construction_log`: `bound` -> `Results/json/sample_profile.json`

### Empirical Strategy

- 状态：`evidence_bound`
- `design_spec`: `bound` -> `state/product/design_spec.json`
- `run_plan`: `bound` -> `state/product/run_plan.json`
- `method_gate_report`: `bound` -> `Results/json/method_gate_report.json`

### Main Results

- 状态：`evidence_bound`
- `main_regression_table`: `bound` -> `Results/json/regression_tables.json`
- `approved_findings`: `bound` -> `Results/json/approved_findings.json`
- `coefficient_interpretation`: `bound` -> `Results/json/approved_findings.json`

### Robustness / Mechanisms / Heterogeneity

- 状态：`evidence_bound`
- `robustness_matrix`: `bound` -> `Results/json/robustness_matrix.json`
- `mechanism_or_heterogeneity_results`: `bound` -> `Results/json/robustness_matrix.json`
- `method_gate_report`: `bound` -> `Results/json/method_gate_report.json`

## 正式层保护

- changed: `False`

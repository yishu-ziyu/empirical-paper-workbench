# P5-D PDF 导出预检

- Status: `blocked_by_source_gaps`
- Can export PDF candidate: `false`
- Source map: `Results/json/formal_manuscript_source_map.json`
- Section source index: `Submissions/formal_package/manuscript/section_sources.json`
- 正式层写回：未发生
- 未生成最终 PDF/docx

## 阻断原因

- `section_source_placeholders_remaining`

## 章节源检查

- `Abstract`: `failed` (section_source_placeholder)
- `Introduction`: `failed` (section_source_placeholder)
- `Literature and Contribution`: `failed` (section_source_placeholder)
- `Institutional Background / Theory / Context`: `failed` (section_source_placeholder)
- `Data and Measurement`: `failed` (section_source_placeholder)
- `Empirical Strategy`: `failed` (section_source_placeholder)
- `Main Results`: `failed` (section_source_placeholder)
- `Robustness / Mechanisms / Heterogeneity`: `failed` (section_source_placeholder)
- `Conclusion`: `failed` (section_source_placeholder)
- `References`: `failed` (section_source_placeholder)

## 证据检查

- `approved_findings`: `passed`
- `citation_verification_log`: `passed`
- `contribution_matrix`: `passed`
- `data_profile`: `passed`
- `design_spec`: `passed`
- `domain_notes`: `passed`
- `figure_manifest`: `passed`
- `limitations_register`: `passed`
- `method_diagnostics_report`: `passed`
- `method_execution_result`: `passed`
- `method_gate_report`: `passed`
- `regression_tables`: `passed`
- `research_question`: `passed`
- `reviewer_scorecard_report`: `passed`
- `robustness_matrix`: `passed`
- `sample_profile`: `passed`
- `variable_role_set`: `passed`
- `verified_bibliography`: `passed`
- `verified_context_sources`: `passed`

## 待处理任务

- `fill_section_abstract` / ManuscriptAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_introduction` / ManuscriptAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_literature_and_contribution` / LiteratureAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_institutional_background_theory_context` / DomainAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_data_and_measurement` / DataAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_empirical_strategy` / MethodAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_main_results` / ExecutionAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_robustness_mechanisms_heterogeneity` / MethodAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_conclusion` / ManuscriptAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。
- `fill_section_references` / LiteratureAgent: 补写章节源，移除占位内容，并绑定目标长度与证据。

## 下一步

- `resolve_pdf_export_preflight_tasks`：先处理章节源占位、缺失证据或源清单问题，再重新运行 PDF 导出预检。

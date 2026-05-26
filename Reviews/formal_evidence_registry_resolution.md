# P5-E1 证据注册表解析

- Status: `evidence_registry_patch_proposed`
- Source preflight: `Results/json/formal_pdf_export_preflight.json`
- Missing evidence count: `10`
- 正式层写回：未发生
- PDF 预检报告写回：未发生

## 解析结果

- `approved_findings`: `derivable_from_existing_artifact` / `state/product/finding_reviews.json`, `state/product/manuscript_candidate_reviews.json`
- `citation_verification_log`: `derivable_from_existing_artifact` / `Results/json/literature_package_report.json`, `Data/literature/processed/verified_bibliography.csv`
- `domain_notes`: `derivable_from_existing_artifact` / `Results/json/literature_package_report.json`, `state/product/research_question.json`
- `figure_manifest`: `derivable_from_existing_artifact` / `Submissions/cfps_robot_pdf_export_manifest.json`, `Submissions/export_manifest.json`
- `limitations_register`: `derivable_from_existing_artifact` / `Results/json/reviewer_scorecard_report.json`, `Results/json/method_gate_report.json`
- `regression_tables`: `derivable_from_existing_artifact` / `Results/json/method_execution_result.json`
- `robustness_matrix`: `derivable_from_existing_artifact` / `Results/json/method_diagnostics_report.json`, `Results/json/method_gate_report.json`
- `sample_profile`: `derivable_from_existing_artifact` / `Results/json/method_execution_result.json`, `Results/json/project_snapshot.json`, `Results/json/cfps_robot_project_snapshot.json`
- `variable_role_set`: `direct_alias_available` / `state/product/variable_roles.json`, `state/proposals/variable_role_reconciliation.json`
- `verified_context_sources`: `derivable_from_existing_artifact` / `Results/json/literature_package_report.json`, `Data/literature/processed/candidate_literature.csv`

## Patch proposal 摘要

- Total: `10`
- `derivable_from_existing_artifact`: `9`
- `direct_alias_available`: `1`

## 下一步

- `review_evidence_registry_patch_proposal`：先确认可绑定或可派生的本地产物，再生成目标 evidence files 并重跑 PDF 预检。

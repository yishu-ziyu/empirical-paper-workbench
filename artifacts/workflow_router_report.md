# Workflow Router Report

Registry: `workflows/registry.json`
Artifact registry: `Tasks/artifact-registry.md`

## Artifact Status

- present: 3
- partial: 0
- missing: 0
- external: 0

## Recommendation

Next workflow: `02_literature` / 文献检索与综述

Reason:
- query_plan.json: not found at litreview/query_plan.json
- literature_candidates.csv: not found at litreview/literature_candidates.csv
- references.bib: not found at references.bib
- contribution_matrix.md: not found at litreview/contribution_matrix.md

## Open Workflow Issues

### `02_literature` / 文献检索与综述
- query_plan.json: not found at litreview/query_plan.json
- literature_candidates.csv: not found at litreview/literature_candidates.csv
- references.bib: not found at references.bib
- contribution_matrix.md: not found at litreview/contribution_matrix.md

### `03_paper_reading` / 论文阅读与拆解
- lit_reading_notes/: not found at litreview/notes/compressed/
- span_index.json: not found at litreview/notes/span_index.json
- reading_state.md: not found at litreview/notes/reading_state.md

### `04_data_gate` / 数据获取与清洗
- data_contract.md: not found at artifacts/data_contract.md
- sample_attrition.csv: not found at artifacts/sample_attrition.csv
- variable_dictionary.csv: not found at artifacts/variable_dictionary.csv
- analysis_ready.*: not found at artifacts/did_sample.pkl
- data_gate_report.md: not found at artifacts/data_gate_report.md

### `05_causal_analysis` / 统计分析与因果推断
- tables/: not found at tables/
- figures/: not found at figures/
- model_log.md: not found at model_log.md
- robustness_report.md: not found at robustness_report.md

### `06_writing` / 论文写作
- paper.tex: not found at paper.tex
- paper.pdf: not found at paper.pdf

### `07_revision` / 论文修改与润色
- review_report.md: not found at review_report.md
- revision_plan.md: not found at revision_plan.md
- draft_revised.*: not found at draft_revised.*

### `08_format_citation` / 引用管理与排版
- verified_bibliography.csv: not found at verified_bibliography.csv
- paper.pdf: not found at paper.pdf

### `09_replication` / 论文复现与可复现研究
- run_manifest.json: not found at run_manifest.json
- repro_report.md: not found at repro_report.md
- replication/README.md: not found at replication/README.md

### `10_defense` / 审稿回复与学术答辩
- response_matrix.md: not found at response_matrix.md
- defense_qa.md: not found at defense_qa.md
- revision_log.md: not found at revision_log.md

### `05x_policy_rollout_data_layer` / 政策 rollout 数据层
- urbmi_ncms_rollout_sources.csv: not found at data/policy/urbmi_ncms_rollout_sources.csv
- policy_rollout_clean.csv: not found at data/policy/policy_rollout_clean.csv
- policy_rollout_merge_report.md: not found at artifacts/policy_rollout_merge_report.md

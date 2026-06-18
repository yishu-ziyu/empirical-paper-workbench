# Workflow Runbook Report

Registry: `workflows/registry.json`
Agent specs: `workflows/agents`
Artifact registry: `Tasks/artifact-registry.md`
JSON state: `artifacts/workflow_runbook_state.json`

## Current Route

NEXT `02_literature` / 文献检索与综述

## Artifact Status

- present: 3
- partial: 0
- missing: 0
- external: 0

## Workflow Table

| Workflow | Agents | Gates | Failure codes | Current issues |
|---|---|---|---|---|
| `01_design` | `ResearchDesignAgent`<br>`DesignAuditor` | one_sentence_design<br>artifact_presence=`python3 scripts/21_route_next_workflow.py` | `DESIGN_TREATMENT_UNCLEAR`<br>`DESIGN_OUTCOME_UNCLEAR`<br>`DESIGN_NO_CONTRIBUTION`<br>`DESIGN_DATA_NOT_SUPPORTING`<br>`DESIGN_HUMAN_REQUIRED` | none |
| `02_literature` | `LiteratureSearchAgent`<br>`MetadataVerifier`<br>`PDFFetchAgent` | metadata_verified=`python3 scripts/15_verify_bibliography.py`<br>closest_papers_selected | `LIT_NO_CLOSEST_PAPERS`<br>`LIT_METADATA_UNVERIFIED`<br>`LIT_FULLTEXT_BLOCKED`<br>`LIT_REVIEW_IS_LIST`<br>`LIT_HUMAN_CLOSEST_REQUIRED` | query_plan.json: not found at litreview/query_plan.json<br>literature_candidates.csv: not found at litreview/literature_candidates.csv<br>references.bib: not found at references.bib<br>contribution_matrix.md: not found at litreview/contribution_matrix.md |
| `03_paper_reading` | `PaperReadingAgent`<br>`EvidenceAuditor` | source_spans_bound<br>literature_role_confirmed | `READING_FULLTEXT_MISSING`<br>`READING_ABSTRACT_ONLY`<br>`READING_SPAN_MISSING`<br>`READING_CLAIM_UNBOUND` | lit_reading_notes/: not found at litreview/notes/compressed/<br>span_index.json: not found at litreview/notes/span_index.json<br>reading_state.md: not found at litreview/notes/reading_state.md |
| `04_data_gate` | `DataPreparationAgent`<br>`DataGateAuditor` | data_gate_script=`python3 scripts/04_data_gate.py`<br>variable_mapping_confirmed | `DATA_RAW_MISSING`<br>`DATA_KEY_VARIABLE_MISSING`<br>`DATA_SAMPLE_ATTRITION_UNEXPLAINED`<br>`DATA_PANEL_INVALID`<br>`DATA_HUMAN_VARIABLE_REQUIRED` | data_contract.md: not found at artifacts/data_contract.md<br>sample_attrition.csv: not found at artifacts/sample_attrition.csv<br>variable_dictionary.csv: not found at artifacts/variable_dictionary.csv<br>analysis_ready.*: not found at artifacts/did_sample.pkl<br>data_gate_report.md: not found at artifacts/data_gate_report.md |
| `05_causal_analysis` | `CausalAnalysisAgent`<br>`IdentificationAuditor`<br>`RobustnessAuditor` | rerun_core_models=`python3 scripts/05_event_study.py && python3 scripts/06_table2.py && python3 scripts/08_robustness.py`<br>claim_strength_confirmed | `CAUSAL_ESTIMAND_UNCLEAR`<br>`CAUSAL_PLACEBO_FAILS`<br>`CAUSAL_RESULT_OVERCLAIMED`<br>`CAUSAL_ROLLOUT_DATA_INCOMPLETE`<br>`CAUSAL_HUMAN_CLAIM_REQUIRED` | tables/: not found at tables/<br>figures/: not found at figures/<br>model_log.md: not found at model_log.md<br>robustness_report.md: not found at robustness_report.md |
| `06_writing` | `WritingAgent`<br>`ClaimBinder` | latex_compile=`xelatex -interaction=nonstopmode paper.tex`<br>main_claim_confirmed | `WRITING_CLAIM_UNBOUND`<br>`WRITING_OVERCLAIMED_RESULT`<br>`WRITING_CONTRIBUTION_UNCLEAR`<br>`WRITING_SECTION_MISMATCH`<br>`WRITING_HUMAN_CLAIM_REQUIRED` | paper.tex: not found at paper.tex<br>paper.pdf: not found at paper.pdf |
| `07_revision` | `ReviewerAgent`<br>`RevisionPlanner`<br>`PolishAgent` | major_concerns_resolved<br>paper_compile_after_revision=`xelatex -interaction=nonstopmode paper.tex` | `REVISION_LANGUAGE_ONLY`<br>`REVISION_RESULT_MISMATCH`<br>`REVISION_MAJOR_UNRESOLVED`<br>`REVISION_NEW_ANALYSIS_UNVERIFIED`<br>`REVISION_HUMAN_DECISION_REQUIRED` | review_report.md: not found at review_report.md<br>revision_plan.md: not found at revision_plan.md<br>draft_revised.*: not found at draft_revised.* |
| `08_format_citation` | `CitationFormatAgent`<br>`ReferenceVerifier`<br>`LayoutAgent` | bibliography_verified=`python3 scripts/15_verify_bibliography.py`<br>layout_clean | `FORMAT_FAKE_CITATION`<br>`FORMAT_MISSING_CITATION`<br>`FORMAT_UNUSED_REFERENCE`<br>`FORMAT_TABLE_UNREADABLE`<br>`FORMAT_LAYOUT_WARNING` | verified_bibliography.csv: not found at verified_bibliography.csv<br>paper.pdf: not found at paper.pdf |
| `09_replication` | `ReproAgent`<br>`EnvironmentAgent`<br>`ArtifactAuditor` | repro_hash_check=`python3 verify_repro.py`<br>data_release_boundary | `REPRO_HASH_DRIFT`<br>`REPRO_PATH_PRIVATE`<br>`REPRO_OUTPUT_UNTRACED`<br>`REPRO_DATA_BOUNDARY_UNCLEAR`<br>`REPRO_ENV_UNDOCUMENTED` | run_manifest.json: not found at run_manifest.json<br>repro_report.md: not found at repro_report.md<br>replication/README.md: not found at replication/README.md |
| `10_defense` | `DefenseAgent`<br>`EvidenceRouter`<br>`ResponseWriter` | all_comments_answered<br>evidence_paths_exist | `DEFENSE_COMMENT_UNANSWERED`<br>`DEFENSE_NO_MANUSCRIPT_EDIT`<br>`DEFENSE_EVIDENCE_MISSING`<br>`DEFENSE_OVERDEFENDED`<br>`DEFENSE_NEW_ANALYSIS_UNREPRODUCED` | response_matrix.md: not found at response_matrix.md<br>defense_qa.md: not found at defense_qa.md<br>revision_log.md: not found at revision_log.md |

## Spec Coverage

- all 10 core workflow specs present

## Human Checkpoints

### `01_design`
- 题目是否值得继续
- 贡献是否足以成文
- 识别假设是否可以接受

### `02_literature`
- closest papers 是否选对
- 本文真正 gap 是什么

### `03_paper_reading`
- 每篇核心文献在本文里承担什么角色

### `04_data_gate`
- 变量替代是否合理
- 数据限制是否要求改题

### `05_causal_analysis`
- 结果是否足以支撑主张
- 是否回退改设计

### `06_writing`
- 论文主线
- 贡献表述
- 结论保守程度

### `07_revision`
- 哪些问题接受
- 哪些风险写成局限
- 是否需要新增分析

### `08_format_citation`
- 目标期刊或学校格式是否接受

### `09_replication`
- 哪些数据能公开
- 哪些只能写访问说明

### `10_defense`
- 哪些让步
- 哪些坚持
- 最终答辩口径

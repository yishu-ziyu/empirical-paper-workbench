# CGSS 审稿式修订任务队列

- schema：`p6.cgss_revision_task_queue.v2`
- 状态：`needs_human_revision_queue_review`
- 草案层：`true`
- 正式层写回：`false`

## 方法门风险
- `reverse_causality`
- `omitted_variables`

## 任务
### writer.expand_core_sections_to_formal_length
- Agent：`WriterAgent`
- 标题：扩写核心章节到正式论文长度
- 输出：`Manuscripts/generated/cgss_social_capital_happiness_paper_rev1.md`
- 状态：`queued_for_human_reviewed_revision`
- 写入正式层：否

### literature.verify_candidate_citations
- Agent：`LiteratureAgent`
- 标题：核验候选引用和中文文献来源
- 输出：`Reviews/cgss_social_capital_happiness_literature_verification_queue.md`
- 状态：`queued_for_human_reviewed_revision`
- 写入正式层：否

### data.add_variable_table_and_sample_flow
- Agent：`DataAgent`
- 标题：补齐变量表、样本筛选和描述性统计
- 输出：`Reviews/cgss_social_capital_happiness_data_variable_revision.md`
- 状态：`queued_for_human_reviewed_revision`
- 写入正式层：否

### method.address_reverse_causality_and_omitted_variables
- Agent：`MethodAgent`
- 标题：处理反向因果与遗漏变量风险的文字和补证计划
- 输出：`Reviews/cgss_social_capital_happiness_endogeneity_revision.md`
- 状态：`queued_for_human_reviewed_revision`
- 写入正式层：否

### writer.expand_robustness_and_mechanism_plan
- Agent：`WriterAgent`
- 标题：扩写稳健性、异质性和机制检验计划
- 输出：`Manuscripts/generated/cgss_social_capital_happiness_paper_rev1.md`
- 状态：`queued_for_human_reviewed_revision`
- 写入正式层：否

### reviewer.audit_result_interpretation_wording
- Agent：`ReviewerAgent`
- 标题：审计结果解释和因果措辞边界
- 输出：`Reviews/cgss_social_capital_happiness_reviewer_report.md`
- 状态：`queued_for_human_reviewed_revision`
- 写入正式层：否

## 验收检查
- `reviewer_report_read_by_human`
- `revision_queue_approved_or_revised`
- `no_formal_manuscript_writeback`
- `candidate_citations_remain_marked_for_verification`

# CGSS 完整探索性论文草稿

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- 状态：`needs_human_exploratory_paper_review`
- 论文文件：`Manuscripts/generated/cgss_social_capital_happiness_paper.md`
- 正式层写回：`false`
- 草案层：`true`

## 篇幅与结构
- 中文字符数：5399
- 最低要求：5000
- 组装章节数：4

## 组装章节
- 文献综述与研究贡献：`Manuscripts/generated/cgss_social_capital_happiness_sections/03-literature-and-contribution.md`
- 数据与变量：`Manuscripts/generated/cgss_social_capital_happiness_sections/04-data-and-measurement.md`
- 实证策略：`Manuscripts/generated/cgss_social_capital_happiness_sections/05-empirical-strategy.md`
- 主要实证结果：`Manuscripts/generated/cgss_social_capital_happiness_sections/06-main-results.md`

## 证据账本
- `cgss_literature_review_draft_packet`
- `cgss_manuscript_section_package`
- `cgss_minimal_model`
- `cgss_ordered_robustness`
- `cgss_results_evidence_package`
- `citation_binding_placeholders`
- `ordered_method_gate`
- `verified_bibliography_candidates`

## 人工审阅清单
- 逐节确认是否符合论文结构和最低字数
- 确认候选文献是否允许进入正式参考文献
- 确认 OLS 与 Ordered Logit 结果解释是否准确
- 确认稳健性、异质性和内生性任务优先级
- 确认是否进入 PDF 预检和审稿式修订循环

## Agent Team 调用节奏
- call_when: before_full_paper_assembly_and_pdf_preflight
- called_agents: ['ManuscriptAgent', 'VerifierAgent', 'MethodAgent', 'LiteratureAgent']
- recall_when: after_paper_markdown_is_assembled_and_before_pdf_preflight
- next_call_when: after_human_reviews_exploratory_paper
- boundary: 完整稿仍为草案层；Agent Team 只检查结构、证据、方法门和引用候选，不提升正式层。

## 下一步
- `human_review_exploratory_paper`
- `run_pdf_export_preflight`
- `build_aer_like_method_gate`
- `generate_reviewer_report_and_revision_queue`

# CGSS 论文分节草案包

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- 状态：`needs_human_manuscript_section_review`
- 正式层写回：`false`
- 草案层：`true`

## 汇总
- 章节数：4
- 可审阅章节：4
- 阻断章节：0
- 中文字符合计：2996

## 章节
### 文献综述与研究贡献
- 文件：`Manuscripts/generated/cgss_social_capital_happiness_sections/03-literature-and-contribution.md`
- 状态：`section_draft_ready_for_review`
- 字数：1260 / 最低 1200 / 目标 1600
- 证据：`cgss_literature_review_draft_packet`, `verified_bibliography_candidates`, `citation_binding_placeholders`
- 引用：`bourdieu_1986`, `ferrer_i_carbonell_frijters_2004`, `oecd_2025`, `putnam_2000`, `world_bank_2004`, `xu_zhang_huang_2023`, `zhang_wan_2020`

### 数据与变量
- 文件：`Manuscripts/generated/cgss_social_capital_happiness_sections/04-data-and-measurement.md`
- 状态：`section_draft_ready_for_review`
- 字数：594 / 最低 520 / 目标 900
- 证据：`cgss_results_evidence_package`, `cgss_minimal_model`, `cgss_ordered_robustness`
- 引用：`cgss_official_source_placeholder`

### 实证策略
- 文件：`Manuscripts/generated/cgss_social_capital_happiness_sections/05-empirical-strategy.md`
- 状态：`section_draft_ready_for_review`
- 字数：581 / 最低 560 / 目标 1000
- 证据：`cgss_results_evidence_package`, `ordered_method_gate`, `cgss_literature_review_draft_packet`
- 引用：`ferrer_i_carbonell_frijters_2004`

### 主要实证结果
- 文件：`Manuscripts/generated/cgss_social_capital_happiness_sections/06-main-results.md`
- 状态：`section_draft_ready_for_review`
- 字数：561 / 最低 560 / 目标 1000
- 证据：`cgss_results_evidence_package`, `cgss_minimal_model`, `cgss_ordered_robustness`
- 引用：本地结果证据

## Agent Team 调用节奏
- call_when: after_results_evidence_and_literature_draft_packets_are_ready
- called_agents: ['ManuscriptAgent', 'VerifierAgent']
- recall_when: after_human_reviews_manuscript_sections
- next_call_when: before_full_paper_assembly_and_pdf_preflight
- boundary: 章节只进入草案层；VerifierAgent 需要逐节核对证据绑定、引用占位和字数门槛。

## 下一步
- `human_review_manuscript_sections`
- `approve_or_revise_literature_citation_bindings`
- `assemble_exploratory_paper_draft`
- `run_pdf_export_preflight`

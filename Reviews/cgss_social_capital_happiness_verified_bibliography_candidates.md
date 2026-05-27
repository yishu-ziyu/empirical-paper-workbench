# CGSS 可核验参考文献候选

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- 状态：`needs_human_bibliography_approval`
- 写入正式参考文献：否
- 写入正式论文：否

## 当前需要处理
- `human_bibliography_approval_required`
- `browser_or_database_verification_required`

## 可进入人工审阅的参考文献候选
### S03 Bowling Alone: The Collapse and Revival of American Community
- 作者/机构：Robert D. Putnam
- 年份：2000
- 候选 citation key：`putnam_2000`
- 来源证据：`publisher_page_opened`
- 链接：https://www.simonandschuster.com/books/Bowling-Alone-Revised-and-Updated/Robert-D-Putnam/9781982130848
- 论文中用途：组织信任、规范和网络三类社会资本维度。
- 人工批准后才写入正式参考文献：是

### S04 The Forms of Capital
- 作者/机构：Pierre Bourdieu
- 年份：1986
- 候选 citation key：`bourdieu_1986`
- 来源证据：`public_pdf_opened`
- 链接：https://web.stanford.edu/~eckert/PDF/Bourdieu1986.pdf
- 论文中用途：补充社会资本作为可动员关系资源的理论解释。
- 人工批准后才写入正式参考文献：是

### S06 OECD Guidelines on Measuring Subjective Well-being
- 作者/机构：OECD
- 年份：2025
- 候选 citation key：`oecd_2025`
- 来源证据：`official_guideline_page_opened`
- 链接：https://www.oecd.org/en/publications/oecd-guidelines-on-measuring-subjective-well-being-2025-update_9203632a-en.html
- 论文中用途：说明主观幸福感测量应区分生活评价、情感体验和其他福利指标。
- 人工批准后才写入正式参考文献：是

### S07 Measuring Social Capital: An Integrated Questionnaire
- 作者/机构：World Bank
- 年份：2004
- 候选 citation key：`world_bank_2004`
- 来源证据：`official_repository_page_opened`
- 链接：https://openknowledge.worldbank.org/entities/publication/634c867c-cbc8-536a-8446-a2703177bc7c
- 论文中用途：为信任、网络、集体行动和信息沟通等社会资本维度提供测量参照。
- 人工批准后才写入正式参考文献：是

### S08 Social trust, social capital, and subjective well-being of rural residents
- 作者/机构：Xu，Zhang，Huang
- 年份：2023
- 候选 citation key：`xu_zhang_huang_2023`
- 来源证据：`journal_page_opened`
- 链接：https://www.nature.com/articles/s41599-023-01532-1
- 论文中用途：提供 CGSS 语境下社会信任、社会资本与主观幸福感的实证参照。
- 人工批准后才写入正式参考文献：是

### S09 机会不均等、社会资本与农民主观幸福感
- 作者/机构：张彤进，万广华
- 年份：2020
- 候选 citation key：`zhang_wan_2020`
- 来源证据：`journal_page_opened`
- 链接：https://qks.shufe.edu.cn/J/ArticleQuery/f824063e-2826-4256-90f5-e5ff8aa79e7a/CN
- 论文中用途：作为中文 CGSS 幸福感研究和社会资本机制的候选中文文献。
- 人工批准后才写入正式参考文献：是

### S10 How Important is Methodology for the estimates of the determinants of Happiness?
- 作者/机构：Ferrer-i-Carbonell，Frijters
- 年份：2004
- 候选 citation key：`ferrer_i_carbonell_frijters_2004`
- 来源证据：`doi_or_repository_page_opened`
- 链接：https://doi.org/10.1111/j.1468-0297.2004.00235.x
- 论文中用途：支撑幸福感有序变量建模和 OLS/有序模型稳健性讨论。
- 人工批准后才写入正式参考文献：是

## 仍需人工或数据库辅助核验
- S01 CGSS 项目概况：需要记录官方页面访问日期，并确认 CGSS2023 使用说明。 动作：`open_official_source_and_record_access_date`。
- S02 Social Capital in the Creation of Human Capital：需要补齐 DOI 页面元数据、期刊卷期页码或 Zotero 条目。 动作：`verify_doi_or_zotero_metadata`。
- S05 Subjective Well-Being：需要核验 DOI 元数据，并决定是否还需要更适合幸福感测量的近年综述。 动作：`verify_doi_or_zotero_metadata`。

## 引用绑定候选
- S03 -> `literature_review`：social capital as trust, norms, and networks；位置：社会资本理论定义段。
- S04 -> `literature_review`：social capital as mobilizable relational resources；位置：社会资本理论扩展段。
- S06 -> `data_and_measurement`：subjective wellbeing measurement limits；位置：主观幸福感变量说明段。
- S07 -> `data_and_measurement`：social capital measurement dimensions；位置：社会资本指数构造说明段。
- S08 -> `literature_review`：CGSS social capital subjective wellbeing empirical context；位置：CGSS 相关经验研究段。
- S09 -> `literature_review`：Chinese CGSS social capital happiness evidence；位置：中文研究脉络段。
- S10 -> `empirical_strategy`：ordered outcome happiness method robustness；位置：有序因变量方法说明段。

## 人工批准后才会写入
- `Data/literature/processed/verified_bibliography.csv`
- `Data/literature/processed/contribution_matrix.md`
- `Results/json/cgss_social_capital_happiness_citation_bindings.json`

## 下一步
- `human_review_verified_bibliography_candidates`
- `write_verified_bibliography_after_approval`
- `draft_cgss_literature_review_section`

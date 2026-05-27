# CGSS 文献来源校验预检

- 题目：社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析
- 状态：needs_source_verification
- 写入正式参考文献：否
- 写入正式论文：否

## 当前阻断
- `manual_source_review_required`
- `manual_cnki_verification_required`
- `zotero_or_scholar_metadata_required`

## 候选参考文献
### S01 CGSS 项目概况
- citation key seed：`中国人民大学中国调查与数据中心_nd`
- 来源类型：`official_data`
- 校验动作：`open_official_source`, `record_access_date`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://cgss.ruc.edu.cn/xmjs/xmgk.htm

### S02 Social Capital in the Creation of Human Capital
- citation key seed：`coleman_1988`
- 来源类型：`classic_theory`
- 校验动作：`verify_doi_or_publisher_page`, `lookup_zotero_or_scholar_metadata`, `record_access_date`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://www.journals.uchicago.edu/doi/10.1086/228943

### S03 Bowling Alone: The Collapse and Revival of American Community
- citation key seed：`putnam_2000`
- 来源类型：`classic_theory`
- 校验动作：`verify_doi_or_publisher_page`, `lookup_zotero_or_scholar_metadata`, `record_access_date`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://www.simonandschuster.com/books/Bowling-Alone-Revised-and-Updated/Robert-D-Putnam/9781982130848

### S04 The Forms of Capital
- citation key seed：`bourdieu_1986`
- 来源类型：`classic_theory`
- 校验动作：`verify_doi_or_publisher_page`, `lookup_zotero_or_scholar_metadata`, `record_access_date`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://web.stanford.edu/~eckert/PDF/Bourdieu1986.pdf

### S05 Subjective Well-Being
- citation key seed：`diener_1984`
- 来源类型：`measurement_standard`
- 校验动作：`verify_doi_or_publisher_page`, `lookup_zotero_or_scholar_metadata`, `record_access_date`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://doi.org/10.1037/0033-2909.95.3.542

### S06 OECD Guidelines on Measuring Subjective Well-being
- citation key seed：`oecd_2025`
- 来源类型：`measurement_standard`
- 校验动作：`verify_doi_or_publisher_page`, `lookup_zotero_or_scholar_metadata`, `record_access_date`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://www.oecd.org/en/publications/oecd-guidelines-on-measuring-subjective-well-being-2025-update_9203632a-en/full-report/measuring-subjective-well-being_b4b53f27.html

### S07 Measuring Social Capital: An Integrated Questionnaire
- citation key seed：`bank_2004`
- 来源类型：`measurement_standard`
- 校验动作：`verify_doi_or_publisher_page`, `lookup_zotero_or_scholar_metadata`, `record_access_date`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://openknowledge.worldbank.org/entities/publication/634c867c-cbc8-536a-8446-a2703177bc7c

### S08 Social trust, social capital, and subjective well-being of rural residents
- citation key seed：`xu_2023`
- 来源类型：`cgss_empirical_study`
- 校验动作：`open_journal_page`, `lookup_zotero_or_scholar_metadata`, `confirm_wave_and_sample`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://www.nature.com/articles/s41599-023-01532-1

### S09 机会不均等、社会资本与农民主观幸福感
- citation key seed：`张彤进_2020`
- 来源类型：`chinese_literature_seed`
- 校验动作：`cnki_or_journal_page_check`, `record_chinese_metadata`, `confirm_cssci_or_journal_level_if_needed`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://qks.shufe.edu.cn/J/ArticleQuery/f824063e-2826-4256-90f5-e5ff8aa79e7a/CN

### S10 How Important is Methodology for the estimates of the determinants of Happiness?
- citation key seed：`ferrer-i-carbonell_2004`
- 来源类型：`method_reference`
- 校验动作：`verify_doi_or_publisher_page`, `lookup_zotero_or_scholar_metadata`, `record_access_date`
- 可引用状态：`candidate_needs_source_check`
- 链接：https://doi.org/10.1111/j.1468-0297.2004.00235.x

## CNKI / 中文文献人工队列
- `社会资本 主观幸福感 CGSS`：确认中文核心文献中社会资本与幸福感的变量定义和常用控制变量。 输出：`candidate_cnki_record_with_title_authors_year_journal_url_or_note`。
- `社会信任 居民幸福感 CGSS 有序Logit`：核验 CGSS 幸福感题项、社会信任题项和有序 Logit 写法。 输出：`candidate_cnki_record_with_title_authors_year_journal_url_or_note`。
- `社会参与 社会网络 主观幸福感 中国综合社会调查`：补充分维度社会资本机制，避免只使用社会信任解释所有结果。 输出：`candidate_cnki_record_with_title_authors_year_journal_url_or_note`。
- `机会不均等、社会资本与农民主观幸福感 张彤进`：核验中文文献元数据、期刊来源和可引用页面。 输出：`verified_chinese_bibliography_candidate_or_reject_reason`。

## Zotero / Scholar 元数据队列
- `Diener 1984 Subjective Well-Being` -> `zotero_or_scholar`：doi_or_stable_url_and_bibtex_candidate。
- `Coleman 1988 Social Capital in the Creation of Human Capital` -> `zotero_or_scholar`：doi_or_stable_url_and_bibtex_candidate。
- `Ferrer-i-Carbonell Frijters 2004 determinants of happiness methodology` -> `zotero_or_scholar`：doi_or_stable_url_and_bibtex_candidate。
- `Social Capital in the Creation of Human Capital 1988` -> `zotero_or_scholar`：metadata_match_or_reject_reason。
- `Bowling Alone: The Collapse and Revival of American Community 2000` -> `zotero_or_scholar`：metadata_match_or_reject_reason。
- `The Forms of Capital 1986` -> `zotero_or_scholar`：metadata_match_or_reject_reason。
- `Subjective Well-Being 1984` -> `zotero_or_scholar`：metadata_match_or_reject_reason。
- `OECD Guidelines on Measuring Subjective Well-being 2025` -> `zotero_or_scholar`：metadata_match_or_reject_reason。
- `Measuring Social Capital: An Integrated Questionnaire 2004` -> `zotero_or_scholar`：metadata_match_or_reject_reason。
- `Social trust, social capital, and subjective well-being of rural residents 2023` -> `zotero_or_scholar`：metadata_match_or_reject_reason。
- `How Important is Methodology for the estimates of the determinants of Happiness? 2004` -> `zotero_or_scholar`：metadata_match_or_reject_reason。

## 下一步
- `open_official_sources_and_record_access_dates`
- `run_cnki_manual_verification`
- `lookup_zotero_or_scholar_metadata`
- `build_verified_bibliography_candidates`
- `bind_sources_to_literature_review_claims`

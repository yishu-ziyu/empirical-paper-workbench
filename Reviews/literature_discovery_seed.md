# Literature Discovery Seed Review

- 题目：工业机器人对劳动力市场匹配效率的影响
- 状态：needs_human_literature_discovery_review
- 正式 bibliography 写回：否
- 正式论文写回：否

## 查询计划
- `Q01` [zh/core_topic]: 工业机器人 劳动力市场 匹配效率
- `Q02` [zh/core_topic]: 工业机器人 就业匹配 劳动力配置效率
- `Q03` [zh/core_topic]: 机器人采用 就业 工资 中国
- `Q04` [zh/core_topic]: 工业机器人 劳动力市场 中国 微观数据
- `Q05` [en/core_topic]: industrial robots labor market matching efficiency
- `Q06` [en/core_topic]: automation labor market matching China
- `Q07` [en/core_topic]: robot adoption worker firm matching labor market
- `Q08` [en/core_topic]: industrial robots employment wages China
- `Q09` [en/dataset_index]: IFR industrial robots labor allocation China
- `Q10` [en/dataset_index]: CLDS industrial robots employment China
- `Q11` [en/dataset_index]: CFPS automation employment China
- `Q12` [en/dataset_index]: CMDS labor mobility automation China
- `Q13` [en/dataset_index]: CGSS automation labor market attitudes China

## 来源注册表
- `local_pdf_or_zotero_import`: import_user_local_pdf_or_zotero_metadata_and_fulltext -> `candidate`
- `openalex_metadata`: discover_cross_discipline_metadata_and_citation_links -> `candidate`
- `crossref_metadata`: verify_doi_publisher_metadata -> `metadata_verified`
- `semantic_scholar_metadata`: discover_related_papers_abstracts_and_citation_graph -> `candidate`
- `open_fulltext_discovery`: locate_available_fulltext_from_open_repository_author_page_or_user_import -> `fulltext_located`
- `cnki_manual_review_queue`: queue_chinese_database_search_terms_for_human_or_browser_review -> `candidate`
- `google_scholar_manual_queue`: queue_broad_scholar_search_terms_for_browser_or_human_review -> `candidate`
- `user_uploaded_fulltext`: promote_user_uploaded_fulltext_to_source_span_extraction -> `fulltext_located`

## Bibliography 状态链
candidate -> metadata_verified -> fulltext_located -> source_span_extracted -> citation_use_proposed -> needs_human_review -> approved_for_project_bibliography

## 候选检索记录
- `LQ001` 工业机器人 劳动力市场 匹配效率 | state=candidate | strong_claims=False
- `LQ002` 工业机器人 就业匹配 劳动力配置效率 | state=candidate | strong_claims=False
- `LQ003` 机器人采用 就业 工资 中国 | state=candidate | strong_claims=False
- `LQ004` 工业机器人 劳动力市场 中国 微观数据 | state=candidate | strong_claims=False
- `LQ005` industrial robots labor market matching efficiency | state=candidate | strong_claims=False
- `LQ006` automation labor market matching China | state=candidate | strong_claims=False
- `LQ007` robot adoption worker firm matching labor market | state=candidate | strong_claims=False
- `LQ008` industrial robots employment wages China | state=candidate | strong_claims=False
- `LQ009` IFR industrial robots labor allocation China | state=candidate | strong_claims=False
- `LQ010` CLDS industrial robots employment China | state=candidate | strong_claims=False
- `LQ011` CFPS automation employment China | state=candidate | strong_claims=False
- `LQ012` CMDS labor mobility automation China | state=candidate | strong_claims=False
- `LQ013` CGSS automation labor market attitudes China | state=candidate | strong_claims=False

## 下一步
- `run_literature_metadata_search`
- `dedupe_literature_candidates`
- `locate_available_fulltext`
- `extract_source_spans_for_used_claims`
- `human_review_project_bibliography_candidates`

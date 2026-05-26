# Literature Review Closed Loop

日期：2026-05-26

## 产品目标

文献综述不是让 Agent 临时编一段背景，而是形成一个可复查的文献资产闭环：

```text
研究题目
-> 关键词与同义词扩展
-> 中英文文献检索
-> 元数据校验
-> Zotero / 本地文献库归档
-> 文献分组与贡献定位
-> 写入综述段落
-> 引文和参考文献预检
```

第一版目标是让 CLI 能生成一个 `literature package`，供后续论文草稿和 Reviewer 使用。

## 工具分工

### Zotero

Zotero 是 canonical bibliography。

职责：

- 保存最终进入论文的文献条目。
- 保存 PDF 附件、笔记、tag、collection。
- 生成 BibTeX / CSL JSON / RIS。
- 为论文中的引用提供稳定 `zotero_key`。

Zotero 条目不是简单缓存；它是正式引用库。论文正文引用必须能回到 Zotero 条目，或者明确标记为待导入。

### CNKI

CNKI 第一版采用人工辅助检索和浏览器辅助，不把它当作稳定 API。

职责：

- 查中文核心文献、学位论文、CSSCI / 北大核心相关资料。
- 提供中国制度背景、中文政策讨论和本土变量定义。
- 通过人工导出或浏览器记录进入项目。

CNKI 条目的证据要求：

- 标题。
- 作者。
- 期刊 / 学位授予单位 / 会议。
- 年份、卷期、页码。
- CNKI 链接或检索页面证据。
- 如有 DOI，进入 Crossref / DOI 校验；如无 DOI，保持 `cnki_verified_manual`。

### Google Scholar

Google Scholar 是发现入口，不是批量数据源。

职责：

- 发现英文核心文献。
- 追踪高被引文献、相关文献、引用链。
- 辅助识别缺失关键词。

结果进入项目时必须再经过 Zotero、DOI、Crossref、OpenAlex 或人工校验。

### Crossref / DOI / OpenAlex / Semantic Scholar

这些用于机器可验证元数据。

职责：

- DOI 解析。
- 作者、年份、期刊、标题匹配。
- 补全 metadata。
- 发现开放引用和相关文献。

如果 Crossref 找不到，不等于文献不存在；中文文献可以保留 `cnki_verified_manual`。

## 目录与产物

每次 research run 应写出：

```text
workspace/runs/<run_id>/02_literature/
  search_plan.yml
  candidate_literature.csv
  verified_bibliography.csv
  literature_groups.yml
  contribution_matrix.md
  review_gap_log.md
  citation_preflight.json
```

项目级汇总：

```text
state/product/literature_review.json
state/product/bibliography_index.json
```

## 统一字段

`candidate_literature.csv` 和 `verified_bibliography.csv` 至少包含：

```text
source_id
title
authors
year
venue
volume_issue_pages
doi
cnki_url
publisher_url
google_scholar_url
openalex_id
semantic_scholar_id
zotero_key
pdf_hash
acquisition_source
verification_status
verification_notes
topic_relevance
method_relevance
data_relevance
contribution_role
```

`verification_status`：

- `zotero_verified`
- `doi_verified`
- `crossref_verified`
- `openalex_verified`
- `cnki_verified_manual`
- `local_pdf_verified`
- `needs_manual_review`

`contribution_role`：

- `closest_paper`
- `method_reference`
- `data_reference`
- `institutional_background`
- `contrasting_result`
- `review_source`

## 文献综述写作门槛

生成 Literature and Contribution 章节前，必须满足：

- 至少 8 条候选文献。
- 至少 5 条通过元数据或人工校验。
- 至少 3 条属于 `closest_paper` 或 `method_reference`。
- 每条正文引用能映射到 `verified_bibliography.csv`。
- 贡献矩阵必须说明：本文和最接近文献在数据、识别、样本、机制或结论上的差异。

如果不满足，CLI 不停止写作，但 `quality_report.verdict` 必须显示：

```json
{
  "citation_checks": {
    "status": "needs_literature_review",
    "missing": ["closest_papers", "verified_bibliography"]
  }
}
```

## CNKI 手动辅助流程

第一版 CNKI 流程：

1. `LiteratureAgent` 根据题目生成中文检索式。
2. 用户或浏览器辅助打开 CNKI。
3. 用户选择核心条目，导出 EndNote / RIS / NoteExpress / GB/T 7714，或保存页面信息。
4. 系统解析导出文件或手动记录。
5. 写入 `candidate_literature.csv`。
6. 通过 DOI / 标题 / 作者 / 年份进行去重。
7. 进入 Zotero 或标记为 `cnki_verified_manual`。

## 去重规则

优先级：

1. DOI 完全一致。
2. Zotero key 一致。
3. 标题规范化后高度一致，且第一作者和年份一致。
4. 中文题名与英文题名人工映射。

去重后保留最完整条目，其他来源写入 `verification_notes`。

## 主链路接入

```text
Topic Brief
-> LiteratureAgent: search_plan.yml
-> CNKI / Zotero / Scholar / Crossref
-> verified_bibliography.csv
-> contribution_matrix.md
-> PaperPackage quality report
-> Manuscript literature section
```

文献闭环完成后，结果解释页和论文草稿页可以读取：

- 本研究最接近的文献是谁。
- 本文增量是什么。
- 哪些引用尚未校验。
- 哪些文献只作为线索，尚未进入正式引用库。


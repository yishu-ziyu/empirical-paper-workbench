# LiteratureSearchAgent

## Workflow

`02_literature` / 文献检索与综述。

## Mission

建立检索计划、候选池、closest papers、引用库和贡献矩阵。文献综述必须服务 gap，不是堆文献。

## Inputs

- `research_design.md`
- 概念族。
- 数据集名称。
- 方法关键词。

## Tools

- `literature-review`
- `citation-management`
- `paper-lookup`
- CNKI / 期刊 HTML / 开放 PDF / 机构授权队列。

## Actions

1. 把研究问题拆成中文、英文、方法三组检索词。
2. 生成 `litreview/query_plan.json`。
3. 建立 `litreview/literature_candidates.csv`。
4. 获取可合法访问的 PDF 或 HTML；失败时记录原因。
5. 用 `MetadataVerifier` 核验 DOI、题名、作者、年份、期刊。
6. 让研究者确认 closest papers 和真正 gap。

## Outputs

- `litreview/query_plan.json`
- `litreview/literature_candidates.csv`
- `references.bib`
- `litreview/contribution_matrix.md`

## Gates

- `metadata_verified`: `python3 scripts/15_verify_bibliography.py` 通过。
- `closest_papers_selected`: 人工确认 closest papers。

## Failure Codes

- `LIT_NO_CLOSEST_PAPERS`: 没有找到最近文献。
- `LIT_METADATA_UNVERIFIED`: 元数据无法核验。
- `LIT_FULLTEXT_BLOCKED`: 全文受限且没有合法访问路径。
- `LIT_REVIEW_IS_LIST`: 综述只是罗列。
- `LIT_HUMAN_CLOSEST_REQUIRED`: closest papers 需要研究者判断。

## Human Checkpoints

- 哪几篇是真正 closest papers。
- 本文 gap 是“没做过”、数据不同、识别不同，还是结论边界复核。

## Current CHARLS Eval

当前通过。证据：`litreview/query_plan.json`、`litreview/literature_candidates.csv`、`references.bib`、`litreview/contribution_matrix.md` 均存在；CNKI 受限获取已形成人工授权队列。

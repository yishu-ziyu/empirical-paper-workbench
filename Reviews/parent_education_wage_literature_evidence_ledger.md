# P1-A 文献证据账本

- 题目：父母受教育水平对子女工资收入的影响
- 状态：`needs_external_literature_verification`
- verified_count：0
- 写入正式 bibliography：否
- 写入正式论文：否

## 当前阻塞
- `external_or_manual_literature_search_required`
- `human_bibliography_approval_required`

## 检索 seed
- `PEW-Q01` 父母教育、家庭背景与子女工资收入 | status=seed
- `PEW-Q02` 代际人力资本传递与教育回报 | status=seed
- `PEW-Q03` 中国家庭追踪调查或类似微观数据中的工资与教育测量 | status=seed
- `PEW-Q04` 义务教育、教育扩张或家庭教育背景的识别策略 | status=seed

## Citation Records
- `PEW-S01` query=PEW-Q01 | status=seed | claims=false
- `PEW-S02` query=PEW-Q02 | status=seed | claims=false
- `PEW-S03` query=PEW-Q03 | status=seed | claims=false
- `PEW-S04` query=PEW-Q04 | status=seed | claims=false

## 正式层边界
- `Manuscripts/references.bib`
- `Manuscripts/paper.md`
- `Manuscripts/generated/paper_draft.md`
- `Data/literature/processed/verified_bibliography.csv`
- `Data/literature/processed/contribution_matrix.md`

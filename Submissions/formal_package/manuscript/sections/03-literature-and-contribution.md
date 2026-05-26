# Literature and Contribution

- Status: `source_draft_ready`
- Agent: `LiteratureAgent`
- Target length: `1000-1800 English words / 2-4 pages`
- Source map: `Results/json/formal_manuscript_source_map.json`
- Draft layer: `true`
- Final paper write: `false`

## 本节任务

把相邻文献、方法文献和本文增量绑定到可核验证据。

## 已绑定证据

- `verified_bibliography` -> `Data/literature/processed/verified_bibliography.csv`
- `contribution_matrix` -> `Data/literature/processed/contribution_matrix.md`
- `citation_verification_log` -> `Results/json/citation_verification_log.json`

## 章节源草案

本节已经绑定可追溯证据，下一步可以由对应 Agent 按目标长度扩写为候选论文段落。正式写回前仍保留人工审阅入口。

## 审阅事项

- 检查本节证据是否覆盖写作目标。
- 扩写时保留数据、方法、结果和文献来源的可追溯路径。

# References

- Status: `source_draft_ready`
- Agent: `LiteratureAgent`
- Target length: `Verified bibliography only`
- Source map: `Results/json/formal_manuscript_source_map.json`
- Draft layer: `true`
- Final paper write: `false`

## 本节任务

只接纳经过 Zotero/CNKI/DOI/OpenAlex/S2 核验的条目。

## 已绑定证据

- `verified_bibliography` -> `Data/literature/processed/verified_bibliography.csv`
- `citation_verification_log` -> `Results/json/citation_verification_log.json`

## 章节源草案

本节已经绑定可追溯证据，下一步可以由对应 Agent 按目标长度扩写为候选论文段落。正式写回前仍保留人工审阅入口。

## 审阅事项

- 只从 verified bibliography 和 citation verification log 生成引用清单。

# Abstract

- Status: `source_draft_ready`
- Agent: `ManuscriptAgent`
- Target length: `100 English words or concise Chinese equivalent`
- Source map: `Results/json/formal_manuscript_source_map.json`
- Draft layer: `true`
- Final paper write: `false`

## 本节任务

用最短篇幅交代问题、数据、方法和核心发现。

## 已绑定证据

- `approved_findings` -> `Results/json/approved_findings.json`
- `method_gate_report` -> `Results/json/method_gate_report.json`
- `verified_bibliography` -> `Data/literature/processed/verified_bibliography.csv`

## 章节源草案

本节已经绑定可追溯证据，下一步可以由对应 Agent 按目标长度扩写为候选论文段落。正式写回前仍保留人工审阅入口。

## 审阅事项

- 压缩为目标摘要长度。
- 只引用已批准 finding 和已验证文献。

# P5-B 正式 paper package manifest

- Status: `formal_package_manifest_ready`
- Can build package: `true`
- Package root: `Submissions/formal_package`
- 本命令写正式层：否
- 本命令生成最终 PDF/docx/正文：否

## 包结构

- `sections` -> `Submissions/formal_package/manuscript`：章节扩写
- `citations` -> `Submissions/formal_package/literature`：引用与文献
- `method_narrative` -> `Submissions/formal_package/methods`：方法叙述
- `result_tables` -> `Submissions/formal_package/results`：结果表与样本说明
- `reproducibility` -> `Submissions/formal_package/reproducibility`：复现说明

## 下一步

- `assemble_formal_manuscript_sources`：读取正式包 manifest，开始把已批准的章节、文献、方法、结果和复现说明装配为正式源文件。

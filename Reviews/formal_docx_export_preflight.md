# P6-B docx 导出预检

## 当前状态

- 状态：`ready_for_docx_export`
- 可执行 docx 导出：`true`
- 最终 PDF：`Submissions/formal_package/paper.pdf`
- 候选 QMD：`Submissions/formal_package/manuscript/paper_candidate.qmd`
- 预期 docx：`Submissions/formal_package/paper.docx`
- pandoc：`pandoc 3.9` (`/opt/homebrew/bin/pandoc`)
- 写入 docx：`false`
- 写入正式研究状态：`false`

## 计划导出命令

```bash
python3 Program/export_docx.py --project-root . --source Submissions/formal_package/manuscript/paper_candidate.qmd --output Submissions/formal_package/paper.docx
```

## 阻断原因

- 无

## 下一步

- `run_formal_docx_export`：docx 预检已通过。下一节点可以读取本报告并生成 formal package 的 paper.docx。

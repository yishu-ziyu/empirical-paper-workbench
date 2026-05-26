# P6-C 正式 docx 导出

## 当前状态

- 状态：`docx_exported`
- 候选 QMD：`Submissions/formal_package/manuscript/paper_candidate.qmd`
- 最终 PDF：`Submissions/formal_package/paper.pdf`
- 最终 docx：`Submissions/formal_package/paper.docx`
- docx sha256：`77964d6a73a3be4abf9d128c17d61dd50e18eb0982c963b838e4c049cf7129cc`
- docx bytes：`14457`
- 导出日志：`Results/logs/formal_docx_export.log`
- 通用导出 manifest：`Submissions/export_manifest.json`
- 写入 docx：`true`
- 写入 PDF：`false`
- 写入正式研究状态：`false`

## 执行命令

```bash
python3 Program/export_docx.py --project-root /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板 --source Submissions/formal_package/manuscript/paper_candidate.qmd --output Submissions/formal_package/paper.docx
```

## 阻断原因

- 无

## 下一步

- `assemble_submission_package_manifest`：正式 PDF 和 docx 已生成。下一节点可以汇总 manifest、复现命令和人工验收说明。

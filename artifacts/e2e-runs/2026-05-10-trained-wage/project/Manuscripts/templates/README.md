# templates

模板文件放这里。

- `paper.md.j2`：Markdown 草稿模板
- `paper.tex.j2`：LaTeX 草稿模板
- `reference.docx`：后续用于稳定 Word 样式的 Pandoc 参考模板

如果 `reference.docx` 暂时不存在，`Program/export_docx.py` 会先用 Pandoc 默认样式导出。


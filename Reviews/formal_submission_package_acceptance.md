# P6-D 正式投稿包人工验收

## 当前状态

- 状态：`formal_submission_package_ready`
- 包目录：`Submissions/formal_package`
- 包内 manifest：`Submissions/formal_package/manifest.json`
- 包内 manifest 已写入：`true`
- 渲染 PDF：`false`
- 渲染 DOCX：`false`
- 写最终产物：`false`
- 写正式研究状态：`false`

## 最终文件

- `paper_pdf`：`Submissions/formal_package/paper.pdf` / bytes=107169 / sha256=`1dc03960fb232e198d64a60807d510939986b2905f504dd8d379f2edfbdf7ff0`
- `paper_docx`：`Submissions/formal_package/paper.docx` / bytes=14457 / sha256=`77964d6a73a3be4abf9d128c17d61dd50e18eb0982c963b838e4c049cf7129cc`

## 人工验收清单

- [ ] 打开 PDF，确认页面可读、标题和章节存在
- [ ] 打开 DOCX，确认正文、标题和引用字段可读
- [ ] 核对 PDF/DOCX sha256 与 manifest 一致
- [ ] 复核 P6-A/P6-B/P6-C 报告均为 ready/exported
- [ ] 确认本节点没有改写正式研究状态

## 复现命令

- `python3 Program/formal_pdf_final_writeback.py --project-root .`
- `python3 Program/formal_docx_export_preflight.py --project-root .`
- `python3 Program/formal_docx_export.py --project-root .`
- `python3 Program/formal_submission_package_manifest.py --project-root .`

## 阻断原因

- 无

## 下一步

- `manual_submission_package_acceptance`：打开 PDF 和 DOCX，按 manifest 核对文件指纹、来源报告和复现命令。

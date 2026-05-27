# P6-E 正式包产品验收入口

## 当前状态

- 状态：`ready_for_manual_acceptance`
- 可进入人工验收：`true`
- 来源 manifest：`Results/json/formal_submission_package_manifest.json`
- 打开文件：`false`
- 渲染 PDF：`false`
- 渲染 DOCX：`false`
- 写正式研究状态：`false`

## 产品可见摘要

- **正式包状态**：可进入人工验收
- **最终文件**：PDF 107169 bytes / DOCX 14457 bytes
- **来源**：Submissions/formal_package/manifest.json
- **权威稿**：Submissions/formal_package/paper.pdf 是当前正式包权威稿；Submissions/formal_package/paper_candidate.pdf 标记为 historical_candidate_or_next_draft
- **一致性**：文件指纹与 manifest 一致
- **下一步**：打开 PDF 和 DOCX，按验收清单逐项确认

## 打开入口

- `paper_pdf`：`Submissions/formal_package/paper.pdf` / bytes=107169 / sha256=`1dc03960fb232e198d64a60807d510939986b2905f504dd8d379f2edfbdf7ff0`
- `paper_docx`：`Submissions/formal_package/paper.docx` / bytes=14457 / sha256=`77964d6a73a3be4abf9d128c17d61dd50e18eb0982c963b838e4c049cf7129cc`

## 人工验收清单

- [ ] 打开 PDF，确认页面可读、标题和章节存在
- [ ] 打开 DOCX，确认正文、标题和引用字段可读
- [ ] 核对 PDF/DOCX sha256 与 manifest 一致
- [ ] 复核 P6-A/P6-B/P6-C 报告均为 ready/exported
- [ ] 确认本节点没有改写正式研究状态

## 阻断原因

- 无

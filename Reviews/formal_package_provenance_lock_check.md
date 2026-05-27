# P6-H1 正式包来源锁校验

## 当前状态

- 状态：`ready_for_manual_acceptance_with_provenance_warning`
- 可继续人工验收：`true`
- 候选来源锁：`drifted`
- 最终产物锁：`consistent`
- 写正式产物：`false`
- 写正式研究状态：`false`

## 候选稿指纹

- 路径：`Submissions/formal_package/paper_candidate.pdf`
- 记录 bytes：`107169`
- 当前 bytes：`107169`
- 记录 sha256：`1dc03960fb232e198d64a60807d510939986b2905f504dd8d379f2edfbdf7ff0`
- 当前 sha256：`07bcaebc586f445a01fc34b95bb63bec82e5ac57ff465ea4770149da2d38ca88`

## 阻断项

- 无

## 警告项

- `candidate_pdf_drifted_from_final_writeback_source`
- `candidate_pdf_same_size_but_hash_changed`

## 下一步选项

- `freeze_approved_candidate_snapshot`：冻结已批准候选稿快照。把最终写回时使用的候选稿指纹作为权威快照保存，当前候选稿另列为后续草案。
- `rerun_short_final_writeback_chain`：重跑短链路写回。如果当前候选稿才是新的权威草案，重新走最终批准、PDF 写回、DOCX 导出和 manifest 生成。
- `demote_current_candidate_as_historical`：把当前候选稿降级为历史草案。保留当前 paper_candidate.pdf，但明确它不是本次 formal package 的来源。

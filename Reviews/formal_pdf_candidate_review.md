# P5-E4 PDF 候选稿审阅

## 当前状态

- 状态：`ready_for_final_approval_review`
- 候选 PDF：`Submissions/formal_package/paper_candidate.pdf`
- 候选 QMD：`Submissions/formal_package/manuscript/paper_candidate.qmd`
- PDF 页数：`10`
- PDF 可读状态：`readable`
- 最终写回预检：`Results/json/formal_pdf_final_writeback_preflight.json`
- 正式层写回：`false`
- 最终产物写回：`false`

## 机器审阅检查

- [x] `candidate_report_ready`
- [x] `candidate_layer_only`
- [x] `candidate_did_not_write_formal_state`
- [x] `candidate_did_not_write_final_outputs`
- [x] `candidate_formal_state_guard_clean`
- [x] `candidate_pdf_exists`
- [x] `candidate_qmd_exists`
- [x] `candidate_pdf_readable`
- [x] `candidate_has_sections`
- [x] `candidate_render_succeeded`

## 章节清单

- Abstract：`Submissions/formal_package/manuscript/sections/01-abstract.md`
- Introduction：`Submissions/formal_package/manuscript/sections/02-introduction.md`
- Literature and Contribution：`Submissions/formal_package/manuscript/sections/03-literature-and-contribution.md`
- Institutional Background / Theory / Context：`Submissions/formal_package/manuscript/sections/04-institutional-background-theory-context.md`
- Data and Measurement：`Submissions/formal_package/manuscript/sections/05-data-and-measurement.md`
- Empirical Strategy：`Submissions/formal_package/manuscript/sections/06-empirical-strategy.md`
- Main Results：`Submissions/formal_package/manuscript/sections/07-main-results.md`
- Robustness / Mechanisms / Heterogeneity：`Submissions/formal_package/manuscript/sections/08-robustness-mechanisms-heterogeneity.md`
- Conclusion：`Submissions/formal_package/manuscript/sections/09-conclusion.md`
- References：`Submissions/formal_package/manuscript/sections/10-references.md`

## 人工审阅入口

- 先审阅候选 PDF 的章节顺序、表图引用、证据边界、页眉页脚、引用列表和复现说明。
- 通过后进入 `human_review_pdf_candidate`。
- 当前命令不会把候选 PDF 晋升为最终 PDF，也不会写入正式状态。

## Agent Team 调用节奏

- 调用点：候选 PDF 审阅前调用 ReviewerAgent / VerifierAgent / ExportAgent。
- 当前会话结果：`blocked_by_agent_thread_limit`
- 收回点：审阅报告和最终写回预检写出后收回，由主线程集成状态。

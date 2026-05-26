# P5-E3 PDF 候选稿

## 当前状态

- 状态：`pdf_candidate_ready`
- 候选层：`true`
- QMD 候选源：`Submissions/formal_package/manuscript/paper_candidate.qmd`
- PDF 候选稿：`Submissions/formal_package/paper_candidate.pdf`
- PDF 是否存在：`true`
- 复跑脚本：`Submissions/formal_package/reproducibility/render_pdf_candidate.sh`
- 正式层写回：`false`
- 最终产物写回：`false`

## 章节来源

- Abstract：`Submissions/formal_package/manuscript/sections/01-abstract.md`，agent=ManuscriptAgent
- Introduction：`Submissions/formal_package/manuscript/sections/02-introduction.md`，agent=ManuscriptAgent
- Literature and Contribution：`Submissions/formal_package/manuscript/sections/03-literature-and-contribution.md`，agent=LiteratureAgent
- Institutional Background / Theory / Context：`Submissions/formal_package/manuscript/sections/04-institutional-background-theory-context.md`，agent=DomainAgent
- Data and Measurement：`Submissions/formal_package/manuscript/sections/05-data-and-measurement.md`，agent=DataAgent
- Empirical Strategy：`Submissions/formal_package/manuscript/sections/06-empirical-strategy.md`，agent=MethodAgent
- Main Results：`Submissions/formal_package/manuscript/sections/07-main-results.md`，agent=ExecutionAgent
- Robustness / Mechanisms / Heterogeneity：`Submissions/formal_package/manuscript/sections/08-robustness-mechanisms-heterogeneity.md`，agent=MethodAgent
- Conclusion：`Submissions/formal_package/manuscript/sections/09-conclusion.md`，agent=ManuscriptAgent
- References：`Submissions/formal_package/manuscript/sections/10-references.md`，agent=LiteratureAgent

## 渲染记录

- 渲染模式：`auto`
- 渲染日志：`Results/logs/formal_pdf_candidate_render.log`
- 阻断原因：`[]`

## Agent Team 调用节奏

- 调用点：候选 PDF 渲染前调用 ExportAgent / VerifierAgent 做只读复核。
- 当前会话结果：`blocked_by_agent_thread_limit`
- 收回点：候选报告、审阅文档和复跑脚本写出后收回，由主线程集成状态。

## 人工审阅

下一步是人工审阅 PDF 候选稿：检查章节顺序、排版、证据边界、表图引用和正式层写回条件。

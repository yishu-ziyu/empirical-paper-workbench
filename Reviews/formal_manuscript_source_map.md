# P5-C 正式稿源装配清单

- Status: `formal_manuscript_sources_ready`
- Can prepare PDF preflight: `true`
- Source manifest: `Results/json/formal_paper_package_manifest.json`
- Section source index: `Submissions/formal_package/manuscript/section_sources.json`
- 正式层写回：未发生
- 最终 PDF/docx：未生成

## 章节源

- `Abstract` -> `Submissions/formal_package/manuscript/sections/01-abstract.md` (ManuscriptAgent, 100 English words or concise Chinese equivalent)
- `Introduction` -> `Submissions/formal_package/manuscript/sections/02-introduction.md` (ManuscriptAgent, 1800-3000 English words / 4-6 pages)
- `Literature and Contribution` -> `Submissions/formal_package/manuscript/sections/03-literature-and-contribution.md` (LiteratureAgent, 1000-1800 English words / 2-4 pages)
- `Institutional Background / Theory / Context` -> `Submissions/formal_package/manuscript/sections/04-institutional-background-theory-context.md` (DomainAgent, 800-1500 English words / 2-4 pages)
- `Data and Measurement` -> `Submissions/formal_package/manuscript/sections/05-data-and-measurement.md` (DataAgent, 800-1500 English words / 2-3 pages)
- `Empirical Strategy` -> `Submissions/formal_package/manuscript/sections/06-empirical-strategy.md` (MethodAgent, 1200-2000 English words / 3-5 pages)
- `Main Results` -> `Submissions/formal_package/manuscript/sections/07-main-results.md` (ExecutionAgent, 2000-3500 English words / 4-7 pages)
- `Robustness / Mechanisms / Heterogeneity` -> `Submissions/formal_package/manuscript/sections/08-robustness-mechanisms-heterogeneity.md` (MethodAgent, 1500-3000 English words / 3-6 pages)
- `Conclusion` -> `Submissions/formal_package/manuscript/sections/09-conclusion.md` (ManuscriptAgent, 500-800 English words / 1-2 pages)
- `References` -> `Submissions/formal_package/manuscript/sections/10-references.md` (LiteratureAgent, Verified bibliography only)

## 下一步

- `run_pdf_export_preflight`：检查章节源、文献、方法、结果和复现说明是否足够进入 PDF-first 导出。

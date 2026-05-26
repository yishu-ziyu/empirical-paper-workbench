# Codex Phase PDF-First Export BDD

## 背景

用户确认探索性研究包先追求 PDF 版本，因为 PDF 更适合本地审阅、归档和复现包交付。但 PDF 不能成为唯一真相源：正式源文件仍应保留为 QMD/Markdown、结构化 JSON、代码和日志。

## 行为用例

### 行为 1：真实数据执行后生成 QMD 稿源

Given 用户用 `Program/run_paper.py` 跑完一次真实或 dry-run 研究流程  
When 系统写出 Markdown 与 LaTeX 草稿  
Then 系统也必须写出同主题的 QMD 稿源，供 PDF/DOCX/HTML 多格式导出复用

业务规则：PDF-first 不是 PDF-only，QMD 是可审阅、可重跑、可转换的稿件源。

### 行为 2：导出前必须做 PDF 预检

Given QMD 稿源已经存在  
When 用户运行 PDF 导出 CLI  
Then 系统必须检查 QMD、Quarto、PDF 引擎和输出路径，并把检查结果写入 manifest

业务规则：导出失败必须可诊断，不能只给一个空的 PDF 按钮或口头失败。

### 行为 3：PDF 导出必须留下可复现证据

Given PDF 预检通过  
When 用户执行 PDF 导出  
Then 系统必须生成 PDF、日志和 manifest，并记录实际执行命令、输入源、输出路径和工具链状态

业务规则：PDF 是审阅/归档产物，manifest 和 log 是复现证据。

### 行为 4：缺工具或缺源文件时不能假装成功

Given QMD 稿源缺失，或本机缺少 Quarto / LaTeX PDF 引擎  
When 用户执行 PDF 导出  
Then 系统必须阻断导出并写明失败检查项

业务规则：严肃实证系统宁可明确阻断，也不能生成伪成功状态。

### 行为 5：DOCX 保持可选协作导出

Given 当前项目已有 DOCX 导出链路  
When 新增 PDF-first 导出  
Then 系统不能破坏已有 `Program/export_docx.py`，DOCX 仍作为后续协作/投稿兼容格式

业务规则：PDF 是 MVP 默认交付面，DOCX 是兼容面，不互相替代。

### 行为 6：PDF-first 包必须给出可复现入口和审阅文档

Given PDF 导出 CLI 已完成预检或导出  
When 用户打开 `Submissions/` 下的交付产物  
Then 系统必须提供一个可一键重跑 PDF 导出的 shell 脚本，以及一个面向人工审阅的 Markdown 结果说明

业务规则：研究包不是一个孤立 PDF，必须让用户知道如何复跑、审阅哪些文件、当前产物处于什么证据等级。

### 行为 7：PDF-first 包必须支持真实配置到 PDF 的完整链路复跑

Given PDF 导出 CLI 知道本轮使用的 `paper_config`  
When 用户要求生成完整链路复跑脚本  
Then 系统必须写出一个从 `Program/run_paper.py` 到 `Program/export_pdf.py` 的 shell 脚本，并在 manifest 与审阅文档中登记

业务规则：只从 QMD 重跑 PDF 只能证明排版可复现，不能证明“真实数据输入 -> 草案源 -> PDF”的研究链路可复现。MVP 必须保留这两个层级的复现入口。

## 已确认边界

- 默认审阅/归档产物：PDF。
- 默认稿源：QMD，同时保留 Markdown/LaTeX。
- DOCX：保留但不作为本轮主线。
- 当前产物等级：exploratory / draft / needs_human_review，不自动进入正式论文层。
- 可复现入口：本轮同时提供两个脚本。`reproduce_pdf_first.sh` 只重跑 PDF 导出；`reproduce_pdf_first_full_chain.sh` 从真实配置重新执行 `run_paper.py` 后再导出 PDF。

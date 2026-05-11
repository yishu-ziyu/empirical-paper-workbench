# 端到端验收报告：用户数据集到实践报告

日期：2026-05-10

验收目标：验证当前项目是否能从用户输入数据集开始，形成选题判断，执行实证分析，并产出一篇可检查的研究/实践报告。

## 1. 输入数据

本次没有使用截图或前端 mock，而是在隔离目录中复制了一份真实可运行项目，模拟用户上传数据集。

- 验收目录：`artifacts/e2e-runs/2026-05-10-trained-wage/`
- 用户输入数据：`artifacts/e2e-runs/2026-05-10-trained-wage/input/user_uploaded_dataset.csv`
- 项目运行数据：`artifacts/e2e-runs/2026-05-10-trained-wage/project/Data/Final/analysis_sample.csv`

数据集字段：

- `trained`：处理变量，0/1
- `wage`：结果变量
- `edu`：控制变量
- `experience`：控制变量

数据规模：12 行，4 列。

## 2. 选题生成与筛选

当前代码库已经有候选题评分能力，但还没有产品级的“上传数据后自动生成多个选题并让用户选择”的完整流程。

本次用现有评分函数对候选题进行了验证：

候选题：`effect of trained on wage`

评分结果：

- 综合分：59.5
- 是否接受：false
- 数据可行性：0.95
- 识别可信度：0.45
- 文献新颖性：0.35
- 结果稳定性：0.55
- 机制清晰度：0.40
- 写作匹配度：0.70

解释：系统能识别这是一个可运行的观察性 OLS 题目，但由于识别可信度和新颖性不足，该题目没有达到自动接受阈值。因此，本次继续执行它，是为了验收“端到端执行链路”，不是把它认定为合格论文选题。

## 3. 真实实证分析执行

执行命令：

```bash
python3 Program/run_paper.py --project-root artifacts/e2e-runs/2026-05-10-trained-wage/project
```

运行模式：live

输出日志：

- `artifacts/e2e-runs/2026-05-10-trained-wage/project/Results/logs/run_paper.log`

日志确认：

- `mode=live`
- `dataset_exists=True`
- `engine=statspai`
- `analysis_executed=True`

核心结果文件：

- `artifacts/e2e-runs/2026-05-10-trained-wage/project/Results/json/analysis_result.json`
- `artifacts/e2e-runs/2026-05-10-trained-wage/project/Results/json/project_snapshot.json`
- `artifacts/e2e-runs/2026-05-10-trained-wage/project/Results/index.json`

模型结果：

- 模型：OLS
- 因变量：`wage`
- 样本量：12
- 处理变量：`trained`
- `trained` 系数：1.8505
- 标准误：0.0573
- p 值：9.1791e-10
- 95% CI：1.7184 到 1.9826
- R-squared：0.9929

解释边界：这是观察性 OLS 结果，只能作为流程验收和探索性分析结果，不能直接宣称因果效应。

## 4. 报告产出

系统生成了 Markdown、LaTeX 和 Word 三类报告产物。

Markdown 草稿：

- `artifacts/e2e-runs/2026-05-10-trained-wage/project/Manuscripts/generated/paper_draft.md`

LaTeX 草稿：

- `artifacts/e2e-runs/2026-05-10-trained-wage/project/Manuscripts/generated/paper_draft.tex`

Word 文件：

- `artifacts/e2e-runs/2026-05-10-trained-wage/project/Submissions/paper_draft.docx`

Word 导出命令：

```bash
python3 Program/export_docx.py --project-root artifacts/e2e-runs/2026-05-10-trained-wage/project
```

导出清单：

- `artifacts/e2e-runs/2026-05-10-trained-wage/project/Submissions/export_manifest.json`

导出状态：`docx_exists=true`

## 5. 多 Agent 工作台编排

执行命令：

```bash
python3 Product/cli.py run-workbench --project-root artifacts/e2e-runs/2026-05-10-trained-wage/project --mode dry-run --user-goal "端到端验收：从用户上传训练-工资数据集开始，生成选题、运行实证分析、产出实践报告"
```

运行 ID：

- `run_20260510T083228Z_d3d1a1`

运行目录：

- `artifacts/e2e-runs/2026-05-10-trained-wage/project/workspace/runs/run_20260510T083228Z_d3d1a1/`

编排链路包括：

- PreparationAgent
- LiteratureAgent
- ResearchStrategistAgent
- ModelingAgent
- VisualizationAgent
- WritingAgent
- ReviewerAgent
- FormatterAgent

产物目录包括：

- `00_intake/`
- `01_sources/`
- `02_literature/`
- `03_strategy/`
- `04_modeling/`
- `05_results/`
- `06_writing/`
- `07_review/`
- `08_final/`

注意：该链路当前以 `dry-run` 跑通，能证明多 Agent 产物目录和阶段结构，但不能证明所有 Agent 已经调用真实研究能力。

## 6. 审稿结果

ReviewerAgent 给出的结论：

- decision：`revise_major`

审稿报告：

- `artifacts/e2e-runs/2026-05-10-trained-wage/project/workspace/runs/run_20260510T083228Z_d3d1a1/07_review/review_report.md`

主要问题：

- 写作源边界需要统一
- 匹配效率、匹配质量、错配结果的概念边界需要更清晰
- CLDS 机制结果不能和主识别同等因果等级
- Bartik 排他性不能被写成天然外生
- 核心结论需要挂到表格、图形或结果索引

这些审稿意见来自项目既有论文主题约束，和本次 `trained/wage` 小样本数据并不完全匹配，说明 reviewer 规则仍然绑定旧论文主题，需要后续做项目上下文隔离。

## 7. 当前真实能力判断

已经跑通：

- 从 CSV 数据进入项目运行目录
- 自动读取 `paper.yaml` 和数据集
- 执行 live StatsPAI/OLS 分析
- 生成结构化 JSON 结果
- 生成 Markdown 草稿
- 生成 LaTeX 草稿
- 通过 Pandoc 导出 Word
- 跑通 dry-run 多 Agent 工作台目录和产物链路

没有完全跑通：

- 前端 UI 中的真实“上传数据集”入口
- 上传后自动生成多个候选选题
- 候选题与数据字段、文献库、识别策略的完整联动
- 用户在 UI 中确认选题后触发真实执行
- Agent 控制台展示真实执行成本、权限和日志
- 多 Agent 链路中的每个 Agent 调用真实研究适配器
- V2 产品界面与本次真实 `Program/run_paper.py` 链路打通

## 8. 结论

当前项目不是只能看静态页面。底层研究执行链路可以真实读取 CSV，执行 OLS 分析，并产出 Markdown、LaTeX、Word 文件。

但它还不是完整的“实证操作系统”。真正缺口在产品编排层：数据上传、选题生成、选题确认、真实 Agent 执行、报告交付、审稿回路和前端状态展示之间还没有完全接成一个用户可操作的闭环。

下一阶段应优先把已有 `Program/run_paper.py` 真实执行能力接到 Product API 和前端流程，而不是继续增加静态展示页面。

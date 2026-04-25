# 实证论文项目模板

这个模板把 AER 风格的 replication package 结构、Git 版本控制、以及和 Agent 协作时的最小约束放在一起。

## 目录原则

- `Data/`：只管数据真源。
- `Program/`：只管可重复运行的程序。
- `Results/`：只管程序导出的结果。
- `Manuscripts/`：只从 `Results/` 或明确的编辑层取数字和图表。
- `Submissions/`：投稿时导出自包含材料包。
- `Reference/`：文献、制度材料、阅读资料。
- `docs/`：项目说明、方案、规范。
- `Tasks/`：当前阶段、待办、Agent 协作记录。

## Data 规则

- `Data/Raw/`：原始数据，保留原貌，不手改。
- `Data/Interim/`：中间数据，记录处理过程。
- `Data/Final/`：正式分析输入，只认这里的成品数据。
- `Program/Clean/` 负责从 `Raw` 生成 `Interim` 和 `Final`。

## Program 规则

- `Program/setup.do`：统一路径配置。
- `Program/master.do`：主链路入口，一键串联全流程。
- `Program/Clean/`：清洗、变量构造、样本筛选。
- `Program/Analysis/`：读取 `Data/Final/`，导出表格和图表。
- `Program/temp/`：临时试错代码。
- `Program/discarded/`：放弃但保留的旧脚本。

## Results 规则

- `Results/tab/`：正式表格。
- `Results/fig/`：正式图形。
- `Results/temp/`：临时输出和调试产物。
- 手稿正文只从 `Results/` 或明确的编辑层取数字。

## Git 规则

- 主线仓库保持干净。
- 稳健性检验、修稿、Agent 试验优先走分支。
- 大体量数据、投稿打包、编辑器缓存、Stata 和 LaTeX 中间产物默认不进仓库。

## 推荐启动顺序

1. 把原始数据放进 `Data/Raw/`。
2. 在 `Program/Clean/` 写清洗脚本，生成 `Data/Final/`。
3. 在 `Program/Analysis/` 写主分析和稳健性分析脚本。
4. 统一从 `Program/master.do` 运行。
5. 结果落到 `Results/tab/` 和 `Results/fig/`。
6. 手稿只读取这些最终结果。

## 和 Agent 协作

- 当前阶段写进 `Tasks/current-stage.md`。
- 新任务先说明改的是 `Data`、`Program`、`Results`、还是 `Manuscripts`。
- 临时试验先放 `Program/temp/`，验证后再迁回正式目录。

## Phase A 运行入口

- 项目定义：`paper.yaml`
- 分析配置：`Program/config/analysis_config.yaml`
- 统一入口：`python3 Program/run_paper.py --project-root . --dry-run`

第一次运行后应至少生成：

- `state/project_state.json`
- `Results/index.json`
- `Results/json/project_snapshot.json`
- `Results/logs/run_paper.log`
- `Manuscripts/generated/paper_draft.md`
- `Manuscripts/generated/paper_draft.tex`

Word 导出入口：

- `python3 Program/export_docx.py --project-root .`

导出后应至少生成：

- `Submissions/paper_draft.docx`
- `Submissions/export_manifest.json`
- `Results/logs/export_docx.log`

## Product Shell

C 版本产品骨架位于 `Product/`。

本地启动：

- `python3 Product/serve_product.py`

启动后打开：

- `http://127.0.0.1:8765`

当前已支持：

- 多项目注册表
- 项目创建向导
- Dashboard / Projects / Workflow / Artifacts / Drafts 五个视图
- 调用 `run_paper.py` 执行 dry/live
- 调用 `export_docx.py` 导出 Word

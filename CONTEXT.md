# CONTEXT — econpaper

本文件是 econpaper 项目的领域术语表（glossary），只定义术语，不写实现细节、不写 spec、不做决策记录（决策走 ADR）。

## 数据层

- **Dataset** — 用户上传的原始数据集（CSV/Excel），由 `upload_data` 节点接收，记录在 `state.uploaded_datasets`。
- **Cleaned Dataset** — 经过 `clean_data` 8 子步骤处理后的数据集，存为 `.cleaned.csv` 副本，原始数据不覆写。
- **Dataset Profile** — 数据集元信息（列名、类型、缺失率等），由 `profiling` 子步骤生成，用于后续变量映射。profiling 遍历所有 datasets + merge 后再 profile 合并结果。
- **CleaningStep** — 清洗管道子步骤的统一 Protocol（`agent/cleaning/step.py`），签名 `run(datasets, config) → (datasets, step_report)`，`name` 属性标识步骤。8 个实现：ProfilingStep / MergeStep / MissingStep / OutliersStep / TransformStep / FilterStep / BalanceStep / AuditStep。
- **StepReport** — 单个清洗步骤的产物记录（TypedDict），字段：`name` / `status`（success/failed/skipped/paused）/ `started_at` / `duration` / `report`。聚合到 `cleaning_report.steps: list[StepReport]`。
- **CleaningPipeline** — 8 个 CleaningStep 的有序编排（`clean_data` 节点），orchestrator 统一 try/except + 聚合 StepReport，每步写独立 sidecar（`<workspace>/<order>_<step_name>_<index>.csv`）。
- **Step Sidecar** — 每步产物的独立 CSV 文件，dataset meta 的 `step_paths: list[str]` 按步骤顺序追加路径，不再链式覆盖 `path` 字段。

## 论文结构

- **Title Chapter** — 论文标题章节，单数，对应 `state.title_chapter`。由 `generate_title` 节点写入，只含标题文本（`\title{...}`），不参与章节循环。
- **Body Chapter** — 正文章节（intro / lit_review / methods / results / conclusion / discussion），复数，对应 `state.body_chapters`（6 项 List）。由 `generate_chapter` 节点按索引循环生成。
- **Chapter Index** — `body_chapters` 的 0-5 索引，与 `outline` 列表顺序对齐。`current_chapter_index` 表示下一个要生成的正文章节索引。
- **Outline** — 6 章的输入契约，由 `generate_outline` 节点产出，前端可拖拽调整后通过 HITL resume 写入 `user_adjusted_outline`。Outline 是输入，body_chapters 是产物，两者分离。
- **Chapter Version** — 单个章节的版本历史，`versions[0]` 是最新版本，regenerate 时 prepend 新版本，rollback 用 `version_index` 取回旧版本。

## 流程节点

- **upload_data** — 接收 CSV 上传，写入 `uploaded_datasets`，初始化 session。
- **clean_data** — 8 子步骤数据清洗管道（profiling → merge → missing → outliers → transform → filter → balance → audit），含 HITL 暂停点。
- **generate_title** — 生成论文标题，写入 `title_chapter`（不写 `body_chapters`）。
- **set_direction** — 用户设定研究方向，写入 `research_direction`。
- **generate_outline** — 生成 6 章大纲，写入 `outline` + 初始化 `current_chapter_index=0`。
- **generate_chapter** — 按 `current_chapter_index` 从 `outline` 取章节类型，生成正文，写入 `body_chapters[idx]`，`current_chapter_index += 1`。
- **approve_chapter** — 用户审批章节，`body_chapters[idx].status` 转为 "approved"。
- **rollback** — 取回章节旧版本，`versions[version_index]` prepend 回 `versions[0]`。
- **translate_code** — Python 代码翻译为 Stata / R / EViews，写入 `code_translations`。
- **export_docx** — LaTeX 模板渲染 + PDF 编译 + docx 转换，从 `title_chapter` + `body_chapters` 提取内容。

## 导出

- **Export Template** — LaTeX 模板名，四选一：`cn_journal` / `undergraduate` / `master_thesis` / `english_submission`。
- **Compile PDF** — 优先 `latexmk -xelatex`，fallback 到 `xelatex` 跑两次。失败时返回 `degraded=True`，`latex_source` 始终可用。
- **Convert docx** — `pandoc` 把 `.tex` 转 `.docx`，不可用时返回 None。

## 状态

- **Session** — 一次论文生成会话，`session_id` 作为 LangGraph thread_id 隔离状态。
- **HITL Pause** — Human-in-the-Loop 暂停点，用户审阅后 resume。当前设在 `clean_data` 后和 `generate_outline` 后。
- **Degraded** — 降级标识，某子功能不可用时（如 latexmk 缺失），主流程继续，对应字段返回 None。

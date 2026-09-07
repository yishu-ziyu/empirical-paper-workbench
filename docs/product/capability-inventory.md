# 产品能力盘点（Localized first study · C1）

日期：2026-09-07  
依据：当前仓库源码、既有验收记录（Card canonical / generic spine / workbench v2）、本轮将跑的质量门。  
未在本轮独立用真实用户数据跑通的能力，不标成「已在明确范围验证」。

硬规则（写进每条相关限制）：

- StatsPAI 方法数 ≠ 工作台已完成同等研究体验。
- Card 教学案例成功 ≠ 用户自带数据全部可用。
- 可下载脚本 ≠ 所有语言已完成数值复现。
- Docker 能构建 ≠ 已有经过验收的生产服务。
- 不编完成百分比。无关缺陷只记录，不在本轮顺手全修。

状态只能是：

- 已在明确范围验证
- 已有实现但缺完整端到端证据
- 仅特定案例可用
- 规划中或尚未找到实现证据

Card 系数：**本地 OLS/IV 约 0.0747 / 0.1315，CI 约 0.0740 / 0.1323。记为「复现待核」。不归因为已核实的平台浮点误差，本轮不改估计器。**

文稿语言：后端 `expectation.locale` 可随预期文本存储，**没有独立的「文稿语言」开关**，切换界面语言也不会改论文正文语言。见「界面语言」。

---

## 数据导入和清洗

- **用户任务**：把 CSV / Stata / Excel 送进研究会话，看到类型与清洗留痕。
- **界面入口**：空桌「使用自己的数据」；工作台 Data；拖放 `CsvDropZone`。
- **生产执行路径**：`POST /uploads` → `upload_pipeline` run → 清洗八步（profiling → merge → missing → outliers → transform → filter → balance → audit）。
- **持久化对象**：session dataset、cleaning report、run 档案、provenance（来源/校验和在 Card 种子上更完整）。
- **已有验证**：`backend/tests/test_upload.py`、`test_clean.py`、`test_postgres_upload_recovery.py`；前端 `CsvDropZone` / `CleanWizard` 测。
- **适用范围**：网页工作台；开发与测试环境。
- **依赖条件**：已登录（或 DEV bypass）；文件被接收为数据文件。
- **限制**：自带数据的完整「清洗→识别→稳健→成文」浏览器旅程弱于 Card。CHARLS 向导是特化路径。Excel/Stata 有导入实现，缺与 Card 同等的公开案例旅程。
- **允许对外使用的描述**：可以上传 CSV、Stata 或 Excel，系统记录变量类型并做清洗留痕。
- **下一步**：用一份非 Card 的真实用户表走完导入→清洗→方向，补端到端证据。
- **状态**：已有实现但缺完整端到端证据（Card 种子数据经同一管道：**仅特定案例可用**的完整验证）。

## 数据探索

- **用户任务**：看描述统计、相关、分布，辅助设变量。
- **界面入口**：工作台 Data / EDA 侧栏。
- **生产执行路径**：`/sessions/{id}` 数据集元数据；EDA 相关 API。
- **持久化对象**：dataset columns、EDA 计算结果（会话内）。
- **已有验证**：`backend/tests/test_eda.py`、`EdaSidebar.test.tsx`。
- **适用范围**：已有数据集的会话。
- **依赖条件**：上传或 Card 种子已就绪。
- **限制**：Card 主路径会尽快进入研究问题，不把 EDA 当必经教程。
- **允许对外使用的描述**：数据就绪后可以打开探索面板看变量与描述统计。
- **下一步**：在自带数据旅程里把探索与方向表单的衔接截图归档。
- **状态**：已有实现但缺完整端到端证据。

## 研究问题

- **用户任务**：写下或确认要回答的问题、结果变量、处理、识别威胁。
- **界面入口**：空桌对话成形；工作台「研究问题」；Card 教学问题卡；非教学案例的方向表单。
- **生产执行路径**：Card 由 `seed_card_lab` 写入 `research.question`；用户方向走 `handleDirectionSubmit` / 研究方向 API。
- **持久化对象**：`research.question`（含 `prompt_en` / `prompt_zh`）、direction record。
- **已有验证**：Card M1 浏览器与 `ResearchLabPanels` / `WorkbenchArtifact` 测；方向表单单测。
- **适用范围**：Card 教学案例完整；用户自填方向存在。
- **依赖条件**：会话已有数据（教学案例由 `/demos/card` 注入）。
- **限制**：双语 prompt 是教学内容，不是界面语言。切换 UI 语言不得改写已存判据或问题对象。
- **允许对外使用的描述**：先确认研究问题，再运行估计。
- **下一步**：用户自填问题与 Card 问题卡在信息架构上对齐（不扩新对象）。
- **状态**：仅特定案例可用（Card 已验证）；用户自填为已有实现但缺完整端到端证据。

## 预期

- **用户任务**：在看到结果前写下预期，并设置可检验判定。
- **界面入口**：研究问题页 `ExpectationEditor`。
- **生产执行路径**：`PUT /sessions/{id}/research/expectation`；揭晓后 criteria 锁定（409 `expectation_criterion_locked`）。
- **持久化对象**：`expectation.text` / `confidence` / `criteria` / `version` / `history` / 可选 `locale`。
- **已有验证**：generic spine C29–C42；`test_card_research_lab.py`、`test_card_spec_run.py`、`ResearchLabPanels.test.tsx`。
- **适用范围**：Card 种子默认 IV&lt;OLS 判据；用户可改（揭晓前）。
- **依赖条件**：research lab 已建立。
- **限制**：无判据 ≠ Expected，为 Unevaluated + `no_criteria`。自由文本不重猜判据。`locale` 不是文稿语言开关。
- **允许对外使用的描述**：在揭晓前写下预期，并显式选择意外判定。
- **下一步**：无。本轮只做展示语言。
- **状态**：已在明确范围验证（Card + 空判据语义）。

## 分析方案

- **用户任务**：在看比较结果前，确认拟纳入的估计设定。
- **界面入口**：工作台 Design；冻结按钮。
- **生产执行路径**：`POST .../specification-space/freeze`；`frozen_before_results`。
- **持久化对象**：`specification_space.definitions` / `frozen_at` / `revealed`。
- **已有验证**：Card M1 freeze；backend research lab 测。
- **适用范围**：Card 6–12 条设定。
- **依赖条件**：teaching case 或已有 specification space。
- **限制**：用户自带数据未必自动得到同等 admissible space。冻结前不应出现比较结果。
- **允许对外使用的描述**：先确认分析方案，再看比较。
- **下一步**：为非 Card 会话定义是否生成方案空间（规划，不在本轮做）。
- **状态**：仅特定案例可用。

## 单次估计

- **用户任务**：跑一条或一组真实回归，看到系数、标准误、样本。
- **界面入口**：确认方案后「运行分析方案」；非 Card 方向提交后的主估计。
- **生产执行路径**：`specification-space` run / direction estimate agent；StatsPAI / pyfixest 在沙箱执行。
- **持久化对象**：`specification_runs[]`、`state.estimate`、run artifacts、provenance。
- **已有验证**：Card OLS/IV 真实系数；`test_card_spec_run.py`。
- **适用范围**：Card 已验证；方向表单 OLS 等有实现。
- **依赖条件**：数据 + 冻结或已提交方向。
- **限制**：StatsPAI 目录里的方法远多于工作台可走完的体验。本地与 CI 系数差见文首「复现待核」。
- **允许对外使用的描述**：工作台会真实跑估计，而不是填展示数字。
- **下一步**：记录复现待核，不改估计器。
- **状态**：仅特定案例可用（Card）；其余方法为已有实现但缺完整端到端证据或规划中。

## 多方案比较

- **用户任务**：选两条设定，看系数移动、改变了什么、没改变什么。
- **界面入口**：结果与证据 · 比较。
- **生产执行路径**：`POST .../research/compare`。
- **持久化对象**：比较读模型（changed/unchanged/delta）；不另建第二套结果。
- **已有验证**：Card Evidence Lab 测与浏览器旅程。
- **适用范围**：已有 ≥2 条 specification_runs。
- **依赖条件**：方案已运行。
- **限制**：不是规格曲线产品的完整替代。
- **允许对外使用的描述**：可以并排比较两条真实设定。
- **下一步**：无（本轮只改文案）。
- **状态**：仅特定案例可用。

## 诊断与稳健性

- **用户任务**：看工具变量强度等诊断，或跑稳健性。
- **界面入口**：结果与证据的 Next-best challenge；工作台稳健性动作；识别报告。
- **生产执行路径**：identification / spec diagnostics；robustness run。
- **持久化对象**：challenge、diagnostics、robustness_status。
- **已有验证**：Card instrument strength（Effective F 来自诊断，非常量）；稳健性 API 测存在。
- **适用范围**：Card IV 诊断已验证；DiD/RD/SCM 工作台体验未与引擎方法数对齐。
- **依赖条件**：对应估计已产生。
- **限制**：**该诊断不能单独证明工具变量有效。** 引擎有更多方法 ≠ 工作台已提供同等研究体验。
- **允许对外使用的描述**：可以查看本案例的强度诊断；诊断本身不能证明工具有效。
- **下一步**：不在本轮实现 DiD。
- **状态**：仅特定案例可用（Card IV）；其他方法规划中或尚未找到实现证据（就工作台体验而言）。

## 文献

- **用户任务**：看到与方向相关的文献来源，而不是空白承诺。
- **界面入口**：工作台 Literature；方向提交时检索。
- **生产执行路径**：`search_literature`（Crossref / Semantic Scholar / Apodex 等，带降级标签）。
- **持久化对象**：`literature_source`、引用列表。
- **已有验证**：`agent/tests/test_search_literature.py`。
- **适用范围**：方向提交路径；Card 教学旅程不把文献当主路径。
- **依赖条件**：外部检索可用或显式降级。
- **限制**：检索失败必须可见，不能假装已引用。
- **允许对外使用的描述**：提交方向时会检索文献；来源会标明。
- **下一步**：Card 旅程是否展示文献来源，保持可选，不强制导览。
- **状态**：已有实现但缺完整端到端证据（相对 Card 主路径）。

## Agent 演示

- **用户任务**：在意外结果后，按需看 OLS/IV 差异与一次预览，而不是被强制教程。
- **界面入口**：结果与证据侧栏「演示这一步」；可暂停/继续/退出。
- **生产执行路径**：semantic-target Agent Cursor；preview spec_run 不改 canonical。
- **持久化对象**：preview `specification_runs`（relation=preview）；canonical 不变直到用户设为主分析。
- **已有验证**：Card M3；`AgentCursorLayer` / `agentCursor` 测。
- **适用范围**：Card Unexpected 之后。
- **依赖条件**：用户主动触发；`prefers-reduced-motion` 有行为。
- **限制**：不是八步导览。Point/演示不改研究状态。
- **允许对外使用的描述**：可以跳过。演示是可选的。
- **下一步**：无。
- **状态**：已在明确范围验证（Card，opt-in）。

## 结论确认

- **用户任务**：在支持 / 有条件支持 / 不支持三种措辞里确认一条研究结论。
- **界面入口**：结果与证据 · 研究结论；批准。
- **生产执行路径**：claim draft / approve API；`approved_by_user`。
- **持久化对象**：claim ledger 条目、version、supporting_run_ids、unresolved_assumptions。
- **已有验证**：`test_card_claim_ledger.py`；Card M4。
- **适用范围**：Card。
- **依赖条件**：已有 runs；用户批准前结果章不得标 grounded。
- **限制**：不是自动发表结论。
- **允许对外使用的描述**：结论需要你确认；三种措辞都在。
- **下一步**：无。
- **状态**：仅特定案例可用。

## 章节编辑/回滚

- **用户任务**：按章生成、改、批准、回滚。
- **界面入口**：论文 Writing；`ChapterWriter` / 评审闸。
- **生产执行路径**：generate_chapter → review_gate → approve / regenerate / rollback。
- **持久化对象**：chapters、versions、review 记录、bypass 留痕。
- **已有验证**：`test_chapter.py`、`test_rollback.py`、`test_review.py`、`ChapterWriter.test.tsx`。
- **适用范围**：六章结构；结果章另受证据门约束。
- **依赖条件**：主结果（及 Card 上已批准结论）到位后才能写结果章。
- **限制**：不是「完全自动写论文」。每章会停。
- **允许对外使用的描述**：按章写，每章停下确认；可以回滚。
- **下一步**：无。
- **状态**：已有实现但缺完整端到端证据（Card 结果章有旅程证据；全六章自带数据旅程不足）。

## 证据关联

- **用户任务**：从结果章回到支撑证据；证据更新后知道要重核。
- **界面入口**：关联证据栏；结论「证据已更新，请重新核对」；结果章跳转。
- **生产执行路径**：`evidence_revision`、claim `based_on_evidence_revision`、chapter `grounded` / `stale`。
- **持久化对象**：上述字段 + provenance。
- **已有验证**：Card M4/M5；`AgentRail` grounded 测。
- **适用范围**：Card 与有 claim 的结果章。
- **依赖条件**：批准的结论与当前主分析一致。
- **限制**：证据更新不会被界面语言切换触发。
- **允许对外使用的描述**：正文应连着当前证据；证据变了要重新核对。
- **下一步**：无。
- **状态**：仅特定案例可用。

## 文档和代码导出

- **用户任务**：导出 Word / LaTeX / PDF 与 Python / Stata / R / EViews 脚本。
- **界面入口**：工作台导出按钮；`DocExportDialog` / `CodeExportDialog`。
- **生产执行路径**：`/export`、`/code-export`。
- **持久化对象**：导出文件（会话产出）。
- **已有验证**：`test_doc_export.py`、`test_code_export.py`、对应前端测。
- **适用范围**：已写出可导出章节。
- **依赖条件**：pandoc / latexmk 影响 PDF/Word；缺依赖须降级说明。
- **限制**：**可下载脚本 ≠ 所有语言已复现数值。** 导出代码适配语法，不证明跨语言逐位一致。
- **允许对外使用的描述**：可以下载论文文档和对应语法的分析代码；数值以工作台本次运行为准。
- **下一步**：若要对 Stata/R 数值复现做主张，需单独验收。
- **状态**：已有实现但缺完整端到端证据（跨语言数值）。

## 会话恢复

- **用户任务**：刷新或重开后回到同一研究，而不是从头编状态。
- **界面入口**：同一 origin + 已存 session id。
- **生产执行路径**：`GET /sessions/{id}` snapshot；`active_run` 重新订阅。
- **持久化对象**：后端 snapshot；浏览器只存 session id 与短命令键。
- **已有验证**：`SnapshotRecovery.test.tsx`；upload recovery 测。
- **适用范围**：同一账号可访问的会话。
- **依赖条件**：后端仍有该 session。
- **限制**：清空 session id 等于新研究。界面语言在 `localStorage econpaper_lang`，不是研究状态。
- **允许对外使用的描述**：刷新后研究状态从服务器恢复。
- **下一步**：无。
- **状态**：已在明确范围验证（Card 与上传恢复范围内）。

## 登录与归属

- **用户任务**：注册/登录后，会话属于该账号。
- **界面入口**：登录/注册页；工作台退出。
- **生产执行路径**：JWT / cookie 鉴权；session owner 检查。
- **持久化对象**：user、session owner。
- **已有验证**：`test_auth.py`、`AppAuth.test.tsx`。
- **适用范围**：非 DEV_AUTH_BYPASS。
- **依赖条件**：后端密钥配置。
- **限制**：开发 bypass 不是生产归属。
- **允许对外使用的描述**：登录后研究属于你的账号。
- **下一步**：生产部署时关闭 bypass。
- **状态**：已有实现但缺完整端到端证据（生产环境）。

## 界面语言

- **用户任务**：用中文或英文看系统文案，不在同一句里堆叠两种界面语言。
- **界面入口**：空桌与工作台语言切换（`LangSwitch` / `LangPills`）。
- **生产执行路径**：`I18nProvider` / `useT`；`localStorage econpaper_lang`；`document.documentElement.lang` 为 `zh-CN` 或 `en`。
- **持久化对象**：仅浏览器语言偏好。研究对像不因切换而重写。
- **已有验证**：本契约 C3–C4 测试（本轮补）。
- **适用范围**：系统 chrome。变量名、公式、用户原文、专名、OLS/IV 可保持原样。
- **依赖条件**：无。
- **限制**：**文稿语言未实现。** 没有「论文用中文/英文写」的开关。切换界面语言不得 PUT 翻译后的 criterion label，不得改 claim / canonical / evidence_revision。
- **允许对外使用的描述**：界面可在中文与英文之间切换；只改变显示。
- **下一步**：本轮完成核心路径分流。
- **状态**：本轮目标为已在明确范围验证（核心路径）；实施前为已有实现但缺完整端到端证据。

## 上手入口

- **用户任务**：从空桌进入一项真实公开研究，或使用自己的数据；已有会话不被宣传页拦住。
- **界面入口**：空桌主按钮「体验一项真实研究」+ 旁注；第二入口「使用自己的数据」（范围见本盘点「数据导入和清洗」）；「了解产品」进既有说明页，可返回。
- **生产执行路径**：`POST /api/demos/card`；普通上传。`deskOpen && !sessionId` 才展示空桌。
- **持久化对象**：新 session（Card 或上传）。
- **已有验证**：`DeskPage.test.tsx`、`App.test.tsx` 空桌/Guide/Card boot；既有 empty-desk-not-in-front-of-session。
- **适用范围**：未打开会话时。
- **依赖条件**：无强制八步；Agent 演示可跳过。
- **限制**：第二入口的能力边界必须用本盘点的状态描述，不能写成与 Card 同等。
- **允许对外使用的描述**：可以从公开教育–工资案例开始，或上传自己的数据（后者完整路径尚未同等验证）。
- **下一步**：本轮改文案与范围标注。
- **状态**：已在明确范围验证（入口存在与不拦会话）；文案本轮更新。

## 运行部署

- **用户任务**：在本机或容器里打开工作台。
- **界面入口**：无（运维）。
- **生产执行路径**：`make dev`（5173/8000）；`make docker-up`。
- **持久化对象**：`.env`、Postgres（生产）、本地 runs。
- **已有验证**：`make test` / `make check-api-drift`；Docker 文件存在。
- **适用范围**：开发机；Docker 合成。
- **依赖条件**：Python 3.12、Node、可选 latexmk/pandoc、LLM key。
- **限制**：**Docker 构建 ≠ 生产服务。** 未在本轮做生产 SLA、备份、多租户验收。
- **允许对外使用的描述**：可以用 make dev 在本机跑；容器配置存在，但不等于已上线生产。
- **下一步**：独立部署验收。
- **状态**：已有实现但缺完整端到端证据（生产）。

---

## 复现待核（不改估计器）

| 环境 | OLS | IV | 处理 |
|---|---|---|---|
| 本地 Card 种子量级 | 0.0747 | 0.1315 | 作为当前工作台量级记录 |
| CI 记录量级 | 0.0740 | 0.1323 | 差异记「复现待核」 |

不得写成已证实的平台浮点误差。不得为贴参考值改结果。

## 未在本轮修复的无关缺陷（只记录）

- issue #30 BrokenPipe（明确排除）。
- 用户指南 `docs/user-guide.md` 仍有过时「自动生成完整论文」表述（文档，非本轮 C 阶段重写）。
- StatsPAI 方法目录与工作台体验不对齐（见上，不在本轮扩方法）。
- 课设样例「年龄与收入」与 Card 教学案例并存，易混；本轮只改空桌主入口文案，不删样例。

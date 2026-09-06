# 验收契约：Workbench v2 视觉实现——专业研究工具质感（目标图三张）

Status: closed

前置：上一阶段契约 `workbench-v2-golden-path-rescue.md`（已 closed，validator ACCEPT）的全部能力是本阶段的
回归底线：后端 Snapshot/Evidence 端点、刷新恢复、Golden Path 真实估计、results 写作门、失败显式化——
本阶段只动呈现层与信息架构，不许伤它们。

## Change

用户打开工作台看到的是三张目标图（`docs/specs/targets/target-{overview,paper,evidence}.png`）那个谱系的
专业研究工具：左侧项目导航 sidebar、面包屑+项目标题+Run/Export 动作区、真实数据的 Overview（统计卡+研究进度
stepper+主结果表）、升级后的 Evidence（主张句+设定 chips+回归表+设定详情+右侧溯源链时间线）、Paper 视图
（Writing/Preview/History + 右侧 Linked Evidence 证据绑定栏）、右侧 Agent 栏（当前任务+下一步决策）、底部
run 状态条。安静、高密度、克制的动效——像长期工作的桌面工具，不像 AI 落地页。

**目标图是 screenshot-level 验收参照，不是像素级复制。信息架构与真实数据优先。**

## Not this

- 不算：为了像目标图编造数据——CHARLS/14382 行/四列规格表/更多系数，都只是图里的示例数据；econpaper 只渲染
  真实 session 的真实 estimate/robustness/章节。
- 不算：渲染无后端支撑的死控件（全局搜索 ⌘K、Share、通知铃、Project Notes、项目切换器、多开 project）。
  图里有但产品没有的功能：不做假 UI，直接不放（记入 ADR）。
- 不算：全仓 shadcn migration、引入第二套动画栈、为采用组件库重写已工作的组件（ResizableWorkspace 保留 restyle）。
- 不算：大面积 glassmorphism、渐变、发光、粒子、背景装饰动画、dashboard card soup。
- 不算：动了 Desk（对话建项）与 Guide（落地页）的既有定稿风格。

## Evaluator

validator 子代理独立复核程序化检查项；主 agent 负责浏览器实弹（逐界面截图 + 十维度自审 + Golden Path 回归）
并把证据归档；用户保留主观视觉/交互质感的最终验收权。

## Checks

- [ ] C1 Shell 信息架构 — 程序: 浏览器截图 1280×800 + 1440×900（归档 `docs/acceptance/evidence-visual-phase/`）+ DOM 断言 — 预期: 左侧项目 sidebar（Overview / Research Question / Data / Design·Specification / Evidence / Literature / Paper，当前项高亮，可折叠）；主区顶部面包屑 + 项目标题（研究问题）+ 动作区（Run / 导出论文 / 导出代码）；右侧 Agent 栏；底部 run 状态条。旧顶部 tab（paper/data/format）与左研究轨被 sidebar+视图吸收，不再有双重导航。1280/1440 无文档级横向溢出，右栏无崩坏。
- [ ] C2 Overview 页（真实数据）— 程序: 浏览器实弹（样例 Golden Path 会话）+ DOM 断言 — 预期: 统计卡行（Dataset 名/行数、Sample 行数、Main method、Last run 状态/时间）全部来自 snapshot；研究进度 stepper 六站（Data cleaned→Design specified→Main estimate→Robustness→Literature→Paper）状态与 snapshot 真相一致（如 robustness_status="ran"→完成、estimate error→红色受阻态、方向未提交→前两站后 pending）；Key Results 表渲染真实 estimate.table_rows；点击 stepper/卡片能跳对应视图。验证手段：跑两次方向（成功一次、坏列失败一次）stepper 状态必须跟着变。
- [ ] C3 Evidence 视图升级 — 程序: 浏览器实弹 + DOM 断言 + curl 对照 — 预期: 标题为主张句（真实 claim）；chips 来自真实 spec（method/公式）；回归表渲染真实 table_rows；Specification Details 来自真实 research_direction；右侧溯源链时间线六层（Result 数字→Specification→Estimator→实际 producer Run（run_id 可点）→实际 analysis Dataset→实际 Code artifact）。Fully traceable 只在六层都有真实 lineage 时出现。heuristic、latest_run、UI readiness（含 canExport / 已生成章节）、session-level guess 任一存在都不得计为 present。旧表述「生成过章节 → 6/6」已被 `docs/acceptance/workbench-v2-provenance-lineage.md` 取代，不得再作为完成标准。某层无数据显式「暂无」，可溯源完整性卡片如实反映（能追几层写几层，不无脑写 Fully traceable）。
- [ ] C4 Paper 视图 + Linked Evidence — 程序: 浏览器实弹 + DOM 断言 — 预期: Writing / Preview / History 三个 tab 可用（Preview 走既有 LaTeX 渲染、History 走既有章节版本）；右侧 Linked Evidence 栏：真实主结果摘要卡（β/SE/p/N）+「基于证据」徽标——该徽标由 snapshot 写作门状态驱动（results 被阻时显示未 grounded 与缺失项），点击可跳 Evidence 视图。
- [ ] C5 Agent 栏语义 — 程序: 浏览器实弹（run 进行中/完成/失败三态）+ DOM 断言 — 预期: run 进行中→当前任务区显示运行中任务与说明；出现需要决策的事→下一步决策卡（amber 语义色）；空闲→无任务不空转；run 失败→显式失败与下一步。动效只出现在状态/空间变化处。
- [ ] C6 十维度自审归档 — 程序: `docs/acceptance/evidence-visual-phase/self-review.md` — 预期: 每个主要界面（Shell+Overview / Evidence / Paper）一段十维度自审（hierarchy、typography、spacing rhythm、information density、state clarity、unnecessary cards/borders、motion purpose、provenance readability、desktop resize behavior、专业工具感 vs AI landing page 感），附修改前后截图路径；无 card soup（内容面优先 plain surface，层级靠 typography/spacing/alignment/dividers 而非 shadow 堆叠）、无大面积玻璃。
- [ ] C7 动效纪律（Emil 规则）— 程序: grep 断言 + reduced-motion 检查 — 预期: 无 `transition: all`、无 `scale(0)` 入场、无 UI 元素 `ease-in`、UI 过渡 ≤300ms ease-out 系、按压态 scale(0.95–0.98)、键盘高频操作无动画；`prefers-reduced-motion` 全局降级保留且新增动效不绕过它。违例逐条列出或为零。
- [ ] C8 回归底线 + 决策记录 — 程序: `make test` + `cd frontend && npm run build` + 浏览器 Golden Path 复走（样例上传→方向→Evidence 数字与 statsmodels 复算一致）+ `git diff` 审查 — 预期: 全绿无新增 skip；上一阶段契约的恢复测试（SnapshotRecovery/workspaceRunRecovery）原样通过；console 零新增 uncaught error；ADR（新增 0014 或扩 0013）记录：视觉决策、目标图与真实数据的差异处理、被否的依赖（react-resizable-panels 不采用——自研 ResizableWorkspace 已满足并 restyle；TanStack Table 缓期——当前表为只读小表，语义 table 足够；shadcn 只选择性参考源码不做 migration；Vaul 不引入）、图中有而本阶段不做的功能清单。

## Evidence

浏览器实弹走查（2026-09-06，DEBUG=true + ECONPAPER_LLM=mock，`make dev`，ZCode 内置浏览器；新会话
7264a66f-9a47-4740-96ac-0c01ec343f2d 由空桌全新走通，旧会话 1405ca2d 用于失败态）：

- **C1 Shell**：sidebar（Overview/Research Question/Data/Design·Specification/Evidence/Literature/Paper，`workbench-sidebar`，
  `rail-*` 锚点保留）、面包屑（`项目 › OLS · income ~ age › Evidence`）、研究问题标题+方向副标题、动作区 Run/导出论文/
  导出代码；旧顶部 tab 与左研究轨已移除（无双重导航）。截图：`overview-1280x800.png`、`evidence-1440x900.png`、
  `overview-iab-freesize.png`（1190 第三宽度）；1280/1440/1190 三档 DOM 断言 scrollWidth==clientWidth 全过。
- **C2 Overview**：统计卡（course-panel.csv·5列 / N 24 / OLS / 上次运行）全来自 snapshot；六站 stepper 与真相一致——
  正常态 5/6（data✓ design✓ estimate✓ robustness✓ literature✓ paper:active，截图 overview-1280x800.png）；
  失败态主结果站红 `!` + β — + 4/6（`overview-failed-1280x800.png`，DOM `data-status=blocked`）；Key Results 表渲染
  真实回归行（age -0.0687 / 0.0083 / 0.0000；treat 0.2031 / 0.1461 / 0.1789）。
- **C3 Evidence**：标题「当前主张：相关」（真实 claim 走 claimLabel）；chips OLS · income ~ age + treat · controls treat；
  回归表真实两行；设定详情（income/age/treat/OLS/undergrad）来自 research_direction；溯源链六层
  （Result→Specification→Estimator→Run(run_id 可点)→Dataset→Code），新会话 Code 层「暂无」→ 完整性卡如实
  「可溯源 5/6 层」。视觉阶段曾把「生成过章节」计为 Code present / 6/6 Fully traceable；该 heuristic
  已被 `workbench-v2-provenance-lineage.md` 取代：Code 层只认关联当前 estimate producer run 的真实
  code artifact，缺 artifact 即使能导出论文也只能 5/6。数字与
  `GET /sessions/{id}/evidence`（coef -0.06870135850794869, se 0.008348243185348042, n 24, table_rows 在端点中原样存在）
  及 statsmodels 独立复算（coef -0.06870135850794397，差 ≈4.7e-12）一致。
- **C4 Paper**：Writing/Preview/History 三 tab（`paper-tab-*`）可用：Preview 渲染已保存正文纸面、History 渲染真实版本
  列表；Linked Evidence 栏（`linked-evidence`）徽标 data-grounded=true「基于证据」+ 真实 β/SE/p/N + 跳 Evidence
  （截图 paper-1280x800.png）。审批流 approve/edit/rollback 未动。
- **C5 Agent 栏**：进行中 data-busy=true「正在估计主结果…」+ Run 按钮进度态 + 底栏蓝点（`agent-rail-busy-1280x800.png`，
  DOM 实录）；空闲显静默一行不空转；失败后 stepper/Key Results/侧栏三处显式失败。全程 console `window.__errors == []`。
- **C6 十维度自审**：`evidence-visual-phase/self-review.md` 已定稿（含走查发现 5 条）；7 张截图 sips 逐张核验像素与
  文件名一致。发现的显示打磨（p 值 `< 0.0001`、claim 标题中文化）与一处**真实运行时崩溃**（table_rows 数组被强转
  string → `raw.replace is not a function`，ErrorBoundary 兜底）已由主 agent 当场修复并回归。
- **C7 动效纪律**：新增 CSS 全部具名属性 transition、≤300ms、ease-out 系；按压 scale(0.97)@160ms；无 scale(0)、
  无 ease-in、无 transition:all（既有 auth 页 2 处属 R5 不动范围）；全局 prefers-reduced-motion 钳制未绕过。
- **C8 回归**：`make test` 全绿（agent 802+1skip 既有 / backend 384+8skip 既有 / frontend 316——减少的 6 个为随
  PaperPath 组件删除而移除的其专属测试，0 skip）；`npm run build` 通过；Golden Path 全新复走（空桌→样例上传→方向→
  Evidence 真实数字）成立；SnapshotRecovery/workspaceRunRecovery 测试原样通过；ADR `docs/adr/0014-workbench-v2-visual-phase.md`
  落盘（被否依赖：react-resizable-panels/TanStack/shadcn migration/Vaul；未做功能清单）；git diff 无 console.log/
  debugger/临时文件。

validator 报告（2026-09-06）：
- 第一轮即 **ACCEPT**：C1–C8 全 PASS。程序化项全部重跑（make test / build / C7 grep / diff 审查）；
  7 张截图 sips 逐张核验名实一致（上一阶段「名 1440 实 1190」矛盾未复现）；数据真实性经
  agent/nodes/estimate.py 溯源证明数字源自真实 statsmodels 拟合链；无死控件、无硬编码系数、
  零新增依赖、无玻璃/渐变。
- 具名豁免两条：W1 Overview@1440 专拍缺失（IAB 截图通道间歇故障，self-review 已披露；以
  evidence-1440x900 + 三档溢出断言 + overview-iab-freesize.png 替代）；W2 动态项以
  Evidence 实录 × 代码事实 × 截图三方自洽核验替代重放。
- 一处 ADR 文字偏差（table_rows 表述）已按 validator 指出修正：该字段存在于 estimate
  payload，渲染层做形状归一，非功能缺陷。

## Named relaxations

- R1 目标图为方向参照：布局语法、组件密度、状态语义向它对齐；间距/配色/字号允许在自身 token 体系内微调；真实数据比图少（如只有 2 个系数、24 行）时按真实数据渲染，不凑数。
- R2 图中有而产品无后端的功能（全局搜索、Share、通知、Notes、项目切换、多列规格对比）本阶段不渲染死 UI，列入 ADR「未做清单」；未来补后端后再上。
- R3 十个维度里属主观质感的项目（专业感、密度舒适度）以主 agent 自审 + 用户最终验收为准；validator 只守客观项（溢出、死控件、动效纪律、数据真实）。
- R4 依赖纪律：默认零新增依赖；若确需交互 primitive，只允许 Base UI 一个栈且须在实现报告里写明不可替代的理由；motion 沿用现有 `motion@12`，不新增动画库。
- R5 配色范围：新 token 只作用于 Workbench 主路径（sidebar+主区+Agent 栏+状态条）；Desk 与 Guide 保持既有纸墨风格不动；字体族（Instrument Sans/Serif、JetBrains Mono、Noto Serif SC）沿用。
- R6 上阶段已闭环的检查（snapshot 字段、evidence 端点契约、恢复协议、409 门）只要求「不回归」，不要求本阶段重写测试；回归以既有测试全绿 + Golden Path 复走为准。

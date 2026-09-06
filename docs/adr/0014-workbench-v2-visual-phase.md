# ADR 0014 — Workbench v2 视觉实现：IA 重排、token 分域与被否的依赖

- **Status:** Accepted（2026-09-05，随验收契约 `docs/acceptance/workbench-v2-visual-phase.md` 实施）
- **Date:** 2026-09-05
- **Related:** ADR-0013（snapshot 唯一真相）、验收契约 workbench-v2-visual-phase（R1–R6 放宽）、`docs/specs/design-sources.md`

---

## Context

三张目标图（`docs/specs/targets/target-{overview,paper,evidence}.png`）确立了产品谱系：
专业研究工具，不是 AI 落地页。落地时必须回答四类问题：信息架构怎么重排、目标图里
有而后端没有的东西怎么办、配色/动效按什么纪律、要不要引组件库。

## Decision

### 1. 信息架构（C1）

- 左侧 **项目 sidebar**（Overview / Research Question / Data / Design·Specification /
  Evidence / Literature / Paper 七项，当前项白底高亮 + 状态点）取代旧「研究对象左轨 +
  顶部 paper/data 标签」的双重导航；sidebar 仍是 ResizableWorkspace 的左栏
  （236px 默认宽，208–300 可调，可折叠，布局存 localStorage `econpaper.workbench.layout.v3`），
  ReadingFocus / 恢复逻辑零改动。
- 主区顶部 **面包屑（项目 › 项目名 › 当前视图）+ 研究问题标题 + 方向摘要副标题 +
  Run / 导出论文 / 导出代码动作区**；上传、登录、语言切换收进面包屑行右端，安静可见。
- 右栏统一为 **Agent 栏**：当前任务（只在 uploading / directionBusy / writeBusy /
  snapshot.active_run 时出现，空闲显示一行静默文案，不空转）+ 下一步决策卡（amber）+
  非阻塞建议。旧 ResearchComputer（研究进度树 / paper-path）由 Overview stepper 与
  Evidence 溯源链吸收，组件删除。
- Overview 成为刷新恢复后的默认落地视图——**仅当 snapshot 已推进到研究方向及以上**
  （`snapshotHasResearchContent`）；只有数据集（刚上传）仍停在研究问题表单，
  避免把正在填方向的用户甩到仪表盘。

### 2. 目标图 vs 真实数据的差异处理（R1/R2）

- Overview 统计卡不含「Last run 2 hours ago」式时间戳：snapshot 没有 last-run 时间
  字段，宁显状态（运行中 / 主结果已生成 / 暂无运行）不伪造时间。
- 主结果表数据源 = `evidence.results` / `estimate.results`，回退
  `estimate.treatment_row`。`estimate.table_rows`（字符串数组，`agent/nodes/estimate.py`
  写入 estimate payload、evidence 端点原样嵌出）在渲染层做了形状归一：数组 join 后
  交给同一个表格解析器，三种来源（results 字符串 / table_rows 数组 / treatment_row
  单行）都能渲染出真实管道表格。
- 目标图中的 Product Notes、Recent Activity 完整活动流、全局搜索 ⌘K、Share、通知铃、
  项目切换器（My Projects / New Project）、多列规格对比表（图 3 的 (1)–(4) 列）：
  **一律不做假 UI**。Overview 的「最近记录」只显示真实 degradations 与运行失败；
  Key Results 只渲染当前唯一设定的真实表。
- Evidence 规格表只有一列真实结果，不画四列规格对比；可溯源卡按 6 层
  （Result/Specification/Estimator/Run/Dataset/Code）如实计数，缺层列出名字，
  只有 6/6 才显示 Fully traceable。
- Paper Preview 渲染**已保存章节正文的纸面预览**（journal-page），不是 LaTeX 源；
  LaTeX/PDF/docx 由「导出论文」对话框的既有管道生成。目标图里的 Regenerate /
  Info 按钮不渲染（后端对应能力挂在章节审批流里，已有入口）。

### 3. 配色与质感（R5）

- 新 token 域 `--wb-*`（tailwind `wb-*` 类）：近白中性面 `#fafafa`（canvas）/
  `#ffffff`（surface）/ `#f5f5f4`（subtle）+ 发丝线 `rgba(28,25,23,0.08)`；
  语义信号色 primary 蓝 `#2563eb`（Run / 链接 / 进行中）、success 绿 `#15803d`、
  warning amber `#b45309`、danger 红 `#b91c1c`。层级靠 typography / spacing /
  hairline divider，不靠 shadow 堆叠（唯一 shadow 是 sidebar 活动项 1px 投影）。
  无玻璃、无渐变、无大面积发光。
- 旧纸墨 token（`--bg/--accent/--ink`）与其上构建的 Desk / Guide / 写作链路内部组件
  （WriteLoop、ChapterWriter、DirectionForm、EdaSidebar、InstrumentReadout、
  StepTimeline 等）**本阶段不动**；它们作为内容面嵌在 wb 中性面上，
  色差为纸白对纯白，可接受，待下一阶段统一。

### 4. 动效纪律（C7，Emil 规则）

- 只动四类：视图切换入场（`wb-pane-in`，200ms 强 ease-out 曲线
  `cubic-bezier(0.23,1,0.32,1)`）、统计卡 stagger（220ms + 40ms 步进，装饰性不阻塞
  交互）、按压反馈（`wb-press`，160ms ease-out，`:active scale(0.97)`）、运行状态点
  呼吸（1.4s opacity）。全部命名属性，无 `transition: all`、无 `scale(0)` 入场、
  无 UI `ease-in`、全部 ≤300ms。`prefers-reduced-motion` 全局钳制原样覆盖新增动画。

### 5. 被否的依赖与未做清单（R4/R2）

- **react-resizable-panels 不采用**：自研 ResizableWorkspace（326 行）已满足
  拖宽/折叠/键盘 resize/localStorage 持久化，本轮只做了 restyle，引库纯增风险。
- **TanStack Table 缓期**：当前两张表都是只读小表（1–8 行），语义 `<table>` 足够。
- **shadcn 不做 migration**：需要的基础件（按钮/卡片/details）自研成本低于迁移；
  仅选择性参考其源码写法。
- **Vaul 不引入**：本阶段没有 drawer 需求；对话框沿用既有组件。
- 零新增 npm 依赖；motion@12 仍是唯一动画栈（本轮甚至没用到它，全部 CSS transition/
  animation，保证被全局 reduced-motion 钳制覆盖）。
- 未做（等后端能力）：全局搜索、Share、通知、Project Notes、项目切换/多开、
  规格对比多列、Paper 页 Regenerate 快捷键。未来补后端后再上，不做假 UI。

## Consequences

- 双重导航消失；任何视图一跳可达（sidebar ≤7 项），Evidence 从 Overview /
  Linked Evidence / 决策建议三处可进入。
- `rail-*`、`decision-*`、`run-state`、`evidence-coef/se/p/n`、`evidence-run-link`
  等语义锚点全部保留，新增 `overview-*` / `paper-tab-*` / `linked-evidence` /
  `agent-current-task` / `evidence-traceability` 锚点供验收断言。
- 旧测试同步更新（App.test / integration / ThreeColumn），无 skip 掩盖；
  恢复类测试（SnapshotRecovery / workspaceRunRecovery）原样通过。

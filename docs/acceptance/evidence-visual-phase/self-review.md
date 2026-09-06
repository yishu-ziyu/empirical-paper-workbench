# C6 十维度自审（定稿）— Workbench v2 视觉实现

> 状态：主 agent 浏览器实弹后定稿（2026-09-06）。截图全部 sips 核对像素与视口一致。
> 「修改前」基线为上一阶段 golden-path 版工作台（`docs/acceptance/evidence-workbench-v2/` 为其存档）。

## 截图归档（实际文件，sips 已核）

- `overview-1280x800.png`（1280×800）Shell+Overview 全貌，真实样例数据
- `evidence-1280x800.png`（1280×800）Evidence 视图（修复 raw.replace 崩溃后）
- `evidence-1440x900.png`（1440×900）Evidence 视图 1440（含「可溯源 5/6 层」诚实降级态）
- `paper-1280x800.png`（1280×800）Paper Writing tab + Linked Evidence 栏（基于证据徽标）
- `agent-rail-busy-1280x800.png`（1280×800）run 进行中：Agent 栏任务卡 data-busy=true + Run 按钮进度态 + 底栏蓝点
- `overview-failed-1280x800.png`（1280×800）估计失败态：stepper 主结果站红色 ！+ β — + Key Results 失败卡 + Run CTA
- `overview-iab-freesize.png`（1190×743，如实命名）IAB 自由尺寸第三宽度：overflow=false，resize 行为佐证

注：Overview@1440 专拍因 IAB 截图通道间歇故障（视口回落自由尺寸）未能以 1440 落档；
1440 尺寸布局行为由 evidence-1440x900.png + DOM 断言（1280/1440/1190 三档 scrollWidth==clientWidth）覆盖。

## 浏览器实弹发现（主 agent 走查记录）

1. **真实运行时崩溃（已修）**：Evidence 视图首走即 ErrorBoundary「面板渲染出错：raw.replace is not a function」
   ——`estimate.table_rows`（字符串数组）被强转 string 传入 `parseEstimateRows`。jsdom 测试未覆盖真实端点形状。
   修复：tableSource 类型收窄（数组 join/逐类型判断）；修复后 316 tests 全绿、浏览器无 uncaught error。
2. **显示打磨（已修）**：p 值卡 `5.22e-8` 在窄卡折行 → 统一 `< 0.0001`（论文惯例，精确值保留在 title）；
   Evidence 标题裸 token `association` → 走既有 claimLabel 映射（`当前主张：相关`）。
3. **诚实降级实拍**：新会话未生成章节时 Code 层「暂无」→ 溯源卡如实「可溯源 5/6 层，还缺：Code·代码」；
   上一会话生成章节后有代码导出 → 6/6 Fully traceable。两种状态均截图/断言在案。
4. **状态矩阵实拍**：进行中（busy=true + 正在估计主结果 + Run 按钮「正在估计主结果并检索文献…」）/ 完成（5/6、
   steppers 全 ✓）/ 失败（主结果站红 ！、β —、Key Results 虚线失败卡 + Run CTA、侧栏 Evidence β —）三态齐全，
   与 snapshot 真相一致。
5. **待打磨（不阻塞，记 ADR 0014）**：失败后「最近记录」文案仍泛化（「主结果已生成」措辞未随失败切换）；
   统计卡「上次运行」无时间戳字段时以「—」占位略生硬；语言切换 pill 悬浮位置孤立；内层写作链组件仍纸墨 token。

## 界面一：Shell + Overview

| 维度 | 自审 |
| --- | --- |
| hierarchy | 面包屑（12px muted）→ 研究问题标题（21px 衬线 semibold，-0.01em）→ 方向摘要（mono 12px）三级递减明确；页面内统计卡行 → stepper → 主结果 → 最近记录按信息价值降序。改进空间：标题与统计卡之间的间距 rhythm 可再收紧。 |
| typography | 标题用 Instrument Serif + 负 tracking（大字号收紧）；数字全 JetBrains Mono + tabular-nums；标签 mono 小字大写间距 0.14em。正文中文回落 Noto Serif SC 未动。 |
| spacing rhythm | 卡内 16px、卡间 12–16px、区块间 16px，4px 网格为主；sidebar 项 7px 垂直内距。 |
| information density | Overview 四卡一行 + 六站一行 + 一张表 + 一段记录，1280×800 单屏内完成，无滚动即得全貌；空白处不再堆卡。 |
| state clarity | stepper 四态（✓ 绿 / ● 蓝呼吸 / ! 红 / 数字 灰）+ data-status 属性可断言；「X / 6 完成」计数显式；不确定的状态一律 pending，不虚报。 |
| unnecessary cards/borders | 无 card soup：内容面统一白底发丝线，层级靠 typography/spacing/alignment/dividers；唯一 shadow 是 sidebar 活动项 1px。无玻璃、无渐变、无装饰图。 |
| motion purpose | 视图入场 200ms fade+4px 上移（空间定位）；统计卡 40ms stagger（引导扫视顺序，装饰性）；无其他运动。 |
| provenance readability | 主结果表 →「为什么？看证据」一键跳 Evidence 溯源链；数字 mono 呈现。 |
| desktop resize behavior | 1280 与 1440 均无文档级横向溢出（中栏 min-w-0 + 表格 overflow-x-auto + sidebar/rail 定宽可折叠）；900px 以下走既有 compact 覆盖层。 |
| 专业工具感 vs AI landing 感 | 无首屏大标题营销文案、无 emoji 图标、无粒子/流光；命名具体（数据集/样本行数/主方法/上次运行），不做「智能助手」人设话术。 |

## 界面二：Evidence

| 维度 | 自审 |
| --- | --- |
| hierarchy | 主张句是标题（衬线 1.3rem）→ chips → 数字卡 → 回归表 → 设定详情；溯源链右栏独立成区，视线动线「数字 → 从哪来」一栏之隔。 |
| typography | 数字/公式/变量全 mono tabular；层标题 12px medium，细节 11px muted。 |
| spacing rhythm | 左右两栏 16px 间隙，层内 12px；时间线层间距 12px 与连接线对齐。 |
| information density | β/SE/p/N 四小卡 + 全量回归表 + 5 行设定 + 6 层溯源，高密度但分栏清晰；无重复信息（主张只在标题出现一次）。 |
| state clarity | 失败（红）/ 缺失（灰）/ 降级（amber）三态显式；溯源层 `data-present` 可断言；可溯源卡如实写「可溯源 N/6 层 + 缺哪几层」，6/6 才写 Fully traceable。 |
| unnecessary cards/borders | 时间线用圆形节点+竖线，不用每层一张卡；chips 无色底仅发丝线。 |
| motion purpose | 仅视图入场动画；溯源链无逐层入场动画（克制——它是常查的读数区，不是演示）。 |
| provenance readability | run_id 可点（保留 evidence-run-link 链到 run events）；Code 层可点开代码导出，没有就写「暂无」；dataset 层显示名/行/列。 |
| desktop resize behavior | 左右分栏 `lg:grid-cols-[minmax(0,1fr)_240px]`，窄栏时溯源链落到表下方，表格 overflow-x-auto。 |
| 专业工具感 vs AI landing 感 | 溯源链编号+竖线是审计工具语法；失败态文案给下一步动作而非道歉式文案。 |

## 界面三：Paper（Writing / Preview / History + Linked Evidence）

| 维度 | 自审 |
| --- | --- |
| hierarchy | tab 行（Writing/Preview/History）→ 提交门 → 章节导航 → 步骤卡 → 写作流；右栏 Linked Evidence 顶部对齐 tab 行。 |
| typography | tab 13px medium；纸面预览沿用 journal-page 衬线 1.9 行高（既有定稿）。 |
| spacing rhythm | 沿用写作链路既有节奏；新增部分（tab 行、章节导航卡）遵守 4px 网格。 |
| information density | Writing 保持既有密度；History 每章一卡（状态 + 版本列表 + 选中版预览），无空占位卡。 |
| state clarity | Linked Evidence 徽标 data-grounded true/false：绿「基于证据」/ amber「未 grounded + 缺失项」；点击「查看完整证据」跳 Evidence 视图。审批流（approve/edit/rollback）语义未动。 |
| unnecessary cards/borders | 章节导航收进一张卡；History 版本预览用既有 VersionHistory，不再造第二套版本 UI。 |
| motion purpose | tab 切换 200ms 入场；无其他新增动效。键盘高频操作（章节切换、审批按钮）无动画延迟。 |
| provenance readability | 徽标由 write_blockers/estimate 状态驱动，与写作门同源；未 grounded 时列出前 3 条缺失项。 |
| desktop resize behavior | 右栏 252–400px 可调，Linked Evidence 卡在窄栏下纵向堆叠不溢出；中栏纸面预览 max-w 42em 保持阅读行宽。 |
| 专业工具感 vs AI landing 感 | Preview 是纸面而不是「生成中」动效秀；History 是版本留档不是「AI 时间线」。 |

## 动效纪律核对（C7 关联）

- `transition: all`：新增代码 0 处（既有 auth 页 2 处属 Desk/Guide 范围，R5 不动）。
- `scale(0)` 入场：0 处；按压态 scale(0.97)@160ms ease-out。
- UI `ease-in`：0 处（新增）；全局 reduced-motion 钳制覆盖全部新增 CSS 动画。

## 遗留与下一步（给主 agent）

- ~~浏览器实弹~~：已完成（见「浏览器实弹发现」）。
- 内层写作链路组件（WriteLoop/ChapterWriter/DirectionForm/EdaSidebar/InstrumentReadout/StepTimeline）仍持旧纸墨 token，作为下一阶段的统一收尾项（ADR 0014 §3）。

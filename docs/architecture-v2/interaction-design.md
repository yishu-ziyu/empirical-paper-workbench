# 交互设计文档 v2 —— 研究旅程重塑

日期：2026-05-10
读者：Kimi（前端设计）
来源：CoPaper 竞品调研 + 现有产品架构

---

## 1. 设计原则

### 1.1 核心原则

1. **研究旅程优先**：用户看到的不是技术模块，而是从数据到论文的清晰路径
2. **关键节点暂停**：每个重要决策都必须经过用户确认（HITL），系统不黑箱运行
3. **产物可追溯**：任何产物都必须能展示"谁做的、用什么能力、花了多少成本"
4. **状态可见**：用户随时知道当前在哪、还差多少、下一步做什么

### 1.2 视觉约束（继承现有设计系统）

```css
/* 设计 Token —— 不可变更 */
--bg: #f5f0e7;           /* 暖象牙背景 */
--panel: rgba(255, 250, 244, 0.92);
--line: rgba(107, 81, 44, 0.18);
--text: #1b1712;         /* 深褐文字 */
--muted: #6b5b45;        /* 次要文字 */
--accent: #1e6f62;       /* 翡翠绿 —— 主强调 */
--accent-2: #a14a18;     /* 古铜 —— 次强调/警告 */
--danger: #c0392b;       /* 失败/错误 */
--success: #27ae60;      /* 完成/成功 */
--warning: #e67e22;      /* 警告/需要确认 */

font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
layout: 300px sidebar + 1fr main;
breakpoints: 1100px, 600px;
```

### 1.3 交互约束

- 不引入新前端框架，继续使用 vanilla JS + CSS
- 所有动画使用 CSS transitions，不用 JS 动画库
- 页面切换不使用路由刷新，使用 view 切换（现有模式）
- 轮询策略：3 秒间隔（与现有 Agent Cluster 一致）

---

## 2. 信息架构

### 2.1 一阶导航（侧边栏）

```
侧边栏（300px 固定宽度）
├── Logo + 产品名："实证研究 OS"
├── 项目选择器（下拉）
├── 主导航（7项）
│   ├── 研究总览      ← 新增，合并 Dashboard + Workflow
│   ├── 数据与变量    ← 新增
│   ├── 研究设计      ← 新增
│   ├── 实证执行      ← 新增
│   ├── 论文草稿      ← 升级现有 Drafts
│   ├── 产物与复现    ← 升级现有 Artifacts
│   └── Agent 控制台  ← 重塑现有 Agent Cluster
│
├── 分隔线
├── 二级导航（保留现有，折叠态）
│   ├── 项目列表
│   ├── 工作流触发
│   ├── 智能体集群（旧版 fallback）
│   └── 产物浏览（旧版 fallback）
│
└── 底部：当前项目状态摘要
```

### 2.2 页面级信息架构

每个页面的通用结构：

```
Main Area（flex: 1）
├── 研究旅程条（固定顶部，60px 高）
│   └── [数据]→[变量]→[识别]→[模型]→[稳健性]→[图表]→[正文]→[审阅]→[导出]
│
├── 页面标题区（80px 高）
│   ├── 页面标题
│   ├── 副标题/描述
│   └── 操作按钮（主操作 + 次要操作）
│
├── 页面内容区（flex: 1，可滚动）
│   └── 各页面具体内容（见下文）
│
└── HITL Gate 浮动栏（条件显示，固定底部，80px 高）
    ├── 暂停原因说明
    ├── [拒绝并修改] [确认继续]
    └── 倒计时/超时提示
```

---

## 3. 全局组件规范

### 3.1 研究旅程条（Journey Bar）

**位置**：固定在所有页面的顶部（研究总览页内嵌，其他页面固定在 main area 顶部）
**高度**：60px
**背景**：`--panel` + 底部 1px `border-bottom: 1px solid var(--line)`
**滚动行为**：页面滚动时保持固定

**阶段节点设计**：

```
每个节点：
├── 状态圆点（16px 直径）
│   ├── 未开始 ○：空心圆，stroke: var(--line)
│   ├── 进行中 →：实心圆，fill: var(--accent)，内部有旋转指示器
│   ├── 已完成 ✓：实心圆，fill: var(--success)，内部白色 ✓
│   ├── 需要确认 ⚠：实心圆，fill: var(--warning)，内部白色 !
│   └── 失败 ✗：实心圆，fill: var(--danger)，内部白色 ✗
│
├── 阶段名称（12px，下方）
│   └── 未开始: var(--muted) / 其他: var(--text)
│
└── 连接线（到下一个节点）
    └── 已完成阶段之间的线: var(--success)
        其他: var(--line)
```

**交互**：
- Hover 节点 → 显示 tooltip：阶段描述 + 当前状态 + 预计耗时
- Click 节点 → 如果该阶段页面存在，跳转到对应页面
- Click 已完成的节点 → 跳转到该阶段页面并定位到相关区域

**响应式**：
- < 1100px：阶段名称隐藏，只显示图标；tooltip 显示完整名称
- < 600px：旅程条收缩为进度条 + 当前阶段名称

### 3.2 HITL Gate（人机确认门）

**触发条件**：系统到达关键决策节点时自动弹出
**位置**：固定底部（80px 高），覆盖在内容区上方
**背景**：`--panel` + 顶部阴影 `box-shadow: 0 -4px 20px rgba(0,0,0,0.08)`

**布局**：
```
HITL Gate Bar
├── 左侧：暂停图标 + 暂停原因
│   └── "系统在 [模型设定] 节点暂停，等待确认"
├── 中间：决策详情摘要（可选展开）
│   └── 例如："建议识别策略：Bartik IV，理由：..."
└── 右侧：操作按钮
    ├── [查看详情]（次要按钮）
    ├── [拒绝并修改]（次强调按钮，accent-2）
    └── [确认继续]（主按钮，accent）
```

**交互**：
- "查看详情" → 展开详情面板（覆盖在页面中间）
- "拒绝并修改" → 弹出修改输入框，用户输入后 Agent 重新执行
- "确认继续" → 关闭 gate，workflow 继续
- 超时处理：30 分钟无操作 → 自动保存为"待确认"状态，workflow 暂停

### 3.3 阶段摘要卡片（Stage Summary Card）

**用途**：在研究总览页和其他页面中复用
**尺寸**：响应式网格，最小 280px 宽

```
Stage Card
├── 卡片头部（40px）
│   ├── 阶段图标（20px）
│   ├── 阶段名称
│   └── 状态徽章（未开始/进行中/已完成/需确认/失败）
│
├── 卡片内容
│   ├── 关键指标（1-3 个数字）
│   │   └── 例如："3 个数据集 | 47 个变量 | 98.2% 完整度"
│   ├── 进度条（如果适用）
│   └── 下一步提示
│
└── 卡片底部（可选）
    └── [进入此阶段] 链接
```

**状态样式**：
- 未开始：`opacity: 0.7`
- 进行中：左侧 3px 边框 `var(--accent)`
- 已完成：左侧 3px 边框 `var(--success)`
- 需要确认：左侧 3px 边框 `var(--warning)`，轻微 pulse 动画
- 失败：左侧 3px 边框 `var(--danger)`

### 3.4 Agent 身份卡片

**用途**：在 Agent 控制台和页面中复用
**尺寸**：固定 240px 宽，高度自适应

```
Agent Identity Card
├── 头像区（48px 圆形）
│   ├── 背景色（按角色分配）
│   └── 首字母或图标
├── 身份区
│   ├── Agent 名称（16px bold）
│   ├── 角色标签（12px，muted）
│   └── 状态圆点 + 状态文字
├── 能力区
│   └── 能力标签列表（最多 3 个，overflow 用 +N）
├── 成本区
│   └── 累计耗时 + 累计调用次数
└── 操作区
    └── [查看详情] [暂停] [替换 Provider]
```

---

## 4. 页面级详细设计

### 4.1 研究总览（Research Overview）

**页面 ID**：`#view-research-overview`
**URL 对应**：主导航第一项

**布局**：
```
研究总览页
├── 研究旅程条（顶部固定）
├── 研究问题卡片（全宽，120px 高）
│   ├── 左侧：研究问题文本（可点击编辑）
│   └── 右侧：项目元数据（创建时间、最后更新、当前阶段）
│
├── 主要内容区（CSS Grid：3 列，gap 20px）
│   ├── 阶段摘要卡片 × 6（2行 × 3列）
│   │   ├── 数据与变量
│   │   ├── 研究设计
│   │   ├── 实证执行
│   │   ├── 论文草稿
│   │   ├── 产物与复现
│   │   └── Agent 活动
│   │
│   └── 底部跨列区域
│       ├── 关键风险列表（左半）
│       │   └── 风险项：图标 + 描述 + 严重程度 + [去处理]
│       └── 下一步建议（右半）
│           └── 建议项：序号 + 描述 + [执行]
│
└── 右侧边栏（300px，可选，可折叠）
    └── Agent 活动时间线
        └── 最近 20 条事件
```

**阶段卡片内容详细说明**：

| 阶段卡片 | 显示内容 | 关键指标 |
|---------|---------|---------|
| 数据与变量 | 数据集数量、总变量数、样本量、缺失值比例 | `3 数据集 \| 47 变量 \| 15,230 样本` |
| 研究设计 | 识别策略、因变量、自变量、控制变量数 | `Bartik IV \| ln_wage ~ robot_density` |
| 实证执行 | 已完成任务数/总任务数、当前运行状态 | `12/18 完成 \| 2 运行中` |
| 论文草稿 | 各章节完成度、总字数 | `5/7 章完成 \| 8,420 字` |
| 产物与复现 | 产物总数、已审核数、可导出状态 | `24 产物 \| 18 已审核` |
| Agent 活动 | 活跃 Agent 数、最近完成事件 | `3 活跃 \| 2 分钟前完成` |

**交互**：
- 点击研究问题 → 进入编辑模式（inline textarea）
- 点击阶段卡片 → 跳转到对应页面
- 卡片上有"需确认"徽章时 → 点击直接打开 HITL gate
- 风险列表项 → 点击"去处理"跳转到对应页面并定位
- 建议项 → 点击"执行"直接触发对应操作

### 4.2 数据与变量（Data & Variables）

**页面 ID**：`#view-data-variables`

**布局**：
```
数据与变量页
├── 研究旅程条
├── 页面标题："数据与变量" + [上传数据集]
│
└── 三栏布局（CSS Grid：280px 1fr 320px）
    ├── 左侧面板：数据集列表
    │   ├── 数据集卡片列表
    │   │   └── 每个卡片：名称、行数、列数、上传时间、状态图标
    │   ├── 拖拽上传区域（底部）
    │   └── [从 cleaning session 导入]（如有）
    │
    ├── 中间主区域：Schema 预览
    │   ├── 工具栏：搜索、筛选、排序
    │   └── 变量表格
    │       ├── 表头：变量名、类型、缺失率、均值/频数、操作
    │       └── 每行可展开 → 分布可视化
    │           ├── 数值变量：直方图（CSS/Canvas）
    │           └── 分类变量：频数条形图
    │
    └── 右侧面板：变量定义编辑器
        ├── 因变量（目标变量）选择
        ├── 自变量（处理变量）选择
        ├── 控制变量多选
        ├── 工具变量选择（如适用）
        ├── 固定效应层级选择
        └── 每个变量的中文定义输入框
```

**数据集卡片**：
```
Dataset Card
├── 文件类型图标（CSV/Excel/Stata/JSON）
├── 数据集名称
├── 元数据行（行数 × 列数 × 文件大小）
├── 数据质量徽章（完整度百分比）
└── 操作按钮：[查看] [删除]
```

**变量表格行展开后**：
```
Expanded Row
├── 统计摘要（数值：min/max/mean/std；分类：top 5 频数）
├── 分布可视化（200px 高）
├── 缺失值模式（热力图小图）
└── [标记为因变量] [标记为自变量] [标记为控制变量]
```

**交互**：
- 拖拽文件到上传区 → 触发上传，显示进度
- Excel 多 sheet → 上传后弹出 sheet 选择对话框
- 点击变量行 → 展开/收起分布可视化
- 变量定义变更 → 自动保存，显示"已保存"toast
- 变量定义变更 → 如果影响研究设计，显示警告："此变更将需要重新确认研究设计"

### 4.3 研究设计（Research Design）

**页面 ID**：`#view-research-design`

**布局**：
```
研究设计页
├── 研究旅程条
├── 页面标题："研究设计" + [AI 辅助推断]
│
└── 三栏布局（CSS Grid：1fr 1fr 320px）
    ├── 左侧面板：研究问题 + DAG
    │   ├── 研究问题输入框（顶部）
 │   ├── DAG 可视化区（主要区域，300px+ 高）
    │   │   ├── 节点：变量（圆形）+ 标签
    │   │   ├── 边：因果关系（实线箭头）+ 混淆（虚线）
    │   │   └── 图例和操作提示
    │   └── [重新生成 DAG] [手动编辑]
    │
    ├── 中间面板：识别策略 + 模型设定
    │   ├── 识别策略推荐卡片（垂直列表）
    │   │   └── 每个卡片：方法名、适用性评分、理由、推荐标签
    │   ├── 已选识别策略详情
    │   │   └── 假设清单（每个可展开查看检验方法）
    │   └── 模型设定表单
    │       ├── 标准误聚类层级
    │       ├── 固定效应选择
    │       └── 控制变量确认
    │
    └── 右侧面板：Paper Outline
        ├── Outline 树结构
        │   └── 每章：标题 + 状态 + 字数
        ├── 每章可展开看到小节
        └── 每章旁有 [确认] / [编辑] 按钮
```

**DAG 可视化（Phase A 可用文本替代）**：

Phase A 实现方式（简化版）：
```
DAG Text Representation
├── 变量关系列表
│   └── 每行："变量A → 变量B [因果]"
│   └── 每行："变量C ~~ 变量D [相关]"
└── 关键路径高亮
```

Phase B+ 实现方式（图形版）：
- 使用 SVG 或简单 Canvas 绘制
- 节点可拖拽（可选）
- 点击节点 → 显示变量详情

**识别策略推荐卡片**：
```
Method Card
├── 方法名称（如 "Bartik IV"）
├── 适用性评分（1-10，颜色编码）
├── 推荐理由（2-3 句话）
├── 关键假设列表（3-5 项）
├── [查看详情] 链接
└── [选择此方法] 按钮（主操作）
```

**交互**：
- 输入研究问题 → 点击"AI 辅助推断"→ 显示 loading → 推荐识别策略列表
- 选择识别策略 → DAG 更新建议、假设清单更新
- 任何模型设定变更 → 弹出 HITL gate："此变更将影响已跑模型，是否继续？"
- Outline 章节确认 → 锁定图标出现，章节标为"已确认"

### 4.4 实证执行（Empirical Execution）

**页面 ID**：`#view-empirical-execution`

**布局**：
```
实证执行页
├── 研究旅程条
├── 页面标题："实证执行" + [开始执行] [暂停] [取消]
│   └── 执行状态徽章（idle / running / paused / failed）
│
└── 三栏布局（CSS Grid：320px 1fr 360px）
    ├── 左侧面板：任务队列树
    │   ├── Baseline Model
    │   │   └── 子任务列表（可展开/收起）
    │   ├── Robustness Battery
    │   ├── Mechanism Analysis
    │   └── Heterogeneity Analysis
    │   └── 每个任务：状态图标 + 名称 + 负责人 Agent + 耗时
    │
    ├── 中间主区域：代码预览
    │   ├── 代码文件标签（多个文件可切换）
    │   ├── 代码内容（语法高亮，只读）
    │   └── 当前执行行高亮（黄色背景）
    │
    └── 右侧面板：结果摘要
        ├── 回归表（关键系数、标准误、显著性星标）
        ├── 诊断信息（R²、F 统计量、样本量）
        └── 假设检验结果
```

**任务队列树节点**：
```
Task Node
├── 状态图标
│   ├── ○ 等待中
│   ├── → 运行中（带旋转动画）
│   ├── ✓ 已完成
│   └── ✗ 失败
├── 任务名称
├── 负责人 Agent（头像 + 名字）
├── 预计/实际耗时
└── [查看日志] [重跑]（hover 显示）
```

**代码预览区**：
- 使用 Prism.js 或 highlight.js 进行语法高亮（如未引入，可用 CSS 类模拟）
- Python 代码为主，支持 Stata/R 切换
- 当前执行行有黄色高亮背景
- 代码区域可滚动

**交互**：
- 点击"开始执行"→ 创建 workflow，分配 Agent，任务队列开始更新
- 任务运行中 → 代码区实时滚动显示当前执行代码
- 任务到达 HITL gate → 自动暂停，底部弹出 HITL gate bar
- 用户"拒绝"→ 弹出修改建议输入框
- 任务失败 → 任务节点标红，显示失败原因 tooltip，提供"查看日志"和"重跑"

### 4.5 论文草稿（Paper Draft）

**页面 ID**：`#view-paper-draft`

**布局**：
```
论文草稿页
├── 研究旅程条
├── 页面标题："论文草稿" + [导出 DOCX] [审阅全文]
│
└── 三栏布局（CSS Grid：240px 1fr 300px）
    ├── 左侧面板：章节树
    │   ├── 章节列表
    │   │   └── 每章：序号 + 标题 + 状态 + 字数
    │   │       └── 状态：草稿 / 已确认 / 已修改
    │   └── [生成新章节] [重新排序]
    │
    ├── 中间主区域：Markdown 编辑器
    │   ├── 编辑/预览切换标签
    │   ├── 编辑器（textarea，支持 Markdown 语法）
    │   └── 预览区（实时渲染，支持 LaTeX）
    │
    └── 右侧面板：修改建议
        ├── AI 审阅建议列表
        │   └── 每条：位置 + 建议内容 + [接受]/[拒绝]
        └── 引用面板（可切换）
            └── Zotero 引用列表，可拖拽插入
```

**章节树节点**：
```
Chapter Node
├── 章节序号（如 "1."）
├── 章节标题
├── 状态图标
│   ├── 草稿：空心圆
│   ├── 已确认：锁定图标
│   └── 已修改：铅笔图标
├── 字数
└── [确认章节] [解锁]（根据状态显示）
```

**交互**：
- 点击章节树节点 → 加载对应 markdown 到编辑器
- 编辑器内容变更 → 自动保存（debounce 2 秒）
- 点击"确认章节"→ 锁定该章，后续 AI 修改需先解锁
- AI 建议"接受"→ 自动应用到正文，记录到修改历史
- 图表占位符语法：`![Figure 1](placeholder:figure_1)` → 渲染时替换为实际图表

### 4.6 产物与复现（Artifacts & Replication）

**页面 ID**：`#view-artifacts-replication`

**布局**：
```
产物与复现页
├── 研究旅程条
├── 页面标题："产物与复现" + [生成复现包] [全部导出]
│
├── 分类标签栏
│   └── [全部] [数据] [代码] [结果] [图表] [稿件] [复现包]
│
└── 两栏布局（CSS Grid：1fr 380px）
    ├── 左侧主区域：产物网格
    │   └── 产物卡片（CSS Grid，响应式）
    │       └── 每个卡片：
    │           ├── 文件类型图标
    │           ├── 文件名
    │           ├── 创建者（Agent 头像 + 名字）
    │           ├── 创建时间
    │           └── provenance 图标（点击展开）
    │
    └── 右侧边栏：产物详情
        ├── 预览区（根据文件类型）
        │   ├── Markdown → 渲染预览
        │   ├── CSV → 表格预览（前 10 行）
        │   ├── 图片 → 缩略图
        │   └── 其他 → 元数据显示
        ├── Provenance 溯源链
        │   └── 时间线：数据来源 → 处理步骤 → 生成代码 → 输出
        ├── 审核状态
        └── 操作按钮
            ├── [推送到项目目录]
            ├── [下载]
            └── [删除]
```

**产物卡片 provenance 展开**：
```
Provenance Popup（点击卡片上的 🔗 图标）
├── 溯源链时间线
│   └── 每步：图标 + 描述 + 时间 + 负责人
├── 数据来源
│   └── 原始数据集链接
├── 使用的 Capabilities
│   └── 能力列表（带链接到能力详情）
└── 成本摘要
    └── 生成此产物消耗的 wall time / 调用次数
```

**交互**：
- 点击分类标签 → 筛选产物网格
- 点击产物卡片 → 右侧显示详情和预览
- 点击 provenance 图标 → 弹出溯源链面板
- "生成复现包"→ 打包所有产物 + README + 依赖清单 → 下载 zip
- "推送到项目目录"→ 选择目标目录（Manuscripts/Results/Submissions）

### 4.7 Agent 控制台（Agent Console）

**页面 ID**：`#view-agent-console`

**布局**：
```
Agent 控制台页
├── 研究旅程条
├── 页面标题："Agent 控制台"
│
├── Supervisor 状态卡片（全宽，80px 高）
│   ├── 当前计划摘要
│   ├── 总体进度条
│   └── 预算消耗：已用 / 总预算
│
└── 三栏布局（CSS Grid：260px 1fr 340px）
    ├── 左侧面板：Agent 角色列表
    │   ├── Pipeline Roles 分组
    │   │   └── preparation / modeling / visualization / writing / review / export
    │   └── Research Dimension Agents 分组
    │       └── literature / data / variable / identification / robustness / ...
    │   └── 每个 Agent：头像 + 名字 + 状态 + 当前任务
    │
    ├── 中间主区域：Agent 详情面板
    │   ├── 身份卡片（头像、ID、创建者、状态）
    │   ├── 权限清单（可展开每项的详细说明）
    │   ├── 能力注册表（表格：能力名、来源、风险等级）
    │   ├── 产物列表（该 Agent 生成的所有产物）
    │   ├── 成本明细（按 capability 分组的柱状图/表格）
    │   └── 审计日志（时间线，最近 50 条）
    │
    └── 右侧面板：实时活动流
        ├── 筛选器：按 Agent / 按项目 / 按 capability / 按状态
        └── 活动事件列表
            └── 每条：时间 + Agent + 操作 + 结果 + 耗时
```

**Agent 列表项**：
```
Agent List Item
├── 头像（48px 圆形，角色色背景）
├── 名称 + 角色标签
├── 状态圆点（active / paused / error / idle）
├── 当前任务（如有，truncated）
├── 累计成本（时间或次数）
└── [暂停] [详情]（hover 显示）
```

**成本明细可视化**：
- Phase A：纯 CSS 横向条形图（Tufte 原则，不用图表库）
- 每个 capability 一行：名称 + 数值条形 + 具体数字

**交互**：
- 点击 Agent 列表项 → 中间面板加载该 Agent 详情
- 权限清单中每项 hover → 显示该权限允许/禁止的具体操作列表
- 产物卡片 → 点击跳转到产物详情页
- "暂停 Agent"→ 弹出确认对话框，说明影响
- "替换 Provider"→ 下拉选择 local-codex / StatsPAI / 其他
- 审计日志 → 可导出 CSV

---

## 5. 状态与动效规范

### 5.1 加载态

```
Skeleton Loader
├── 灰色背景脉冲动画（pulse: opacity 0.5 → 1 → 0.5, 1.5s）
├── 圆角 4px
└── 颜色：rgba(107, 81, 44, 0.1)
```

页面首次加载时，所有数据区域显示 skeleton，API 返回后淡入（opacity 0 → 1, 300ms）。

### 5.2 过渡动画

```css
/* 页面切换 */
.view-transition {
  transition: opacity 200ms ease;
}

/* 卡片 hover */
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transition: all 200ms ease;
}

/* HITL gate 弹出 */
.hitl-gate {
  animation: slideUp 300ms ease;
}
@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

/* 需要确认状态的 pulse */
.status-pending {
  animation: pulse 2s infinite;
}
```

### 5.3 空状态

每个列表/网格区域必须有空状态：

```
Empty State
├── 图标（48px，muted 色）
├── 标题："暂无数据"
├── 描述：说明为什么没有数据 + 如何创建
└── [创建/上传/开始] 按钮（主操作）
```

### 5.4 错误状态

```
Error State
├── 错误图标（accent-2 色）
├── 错误标题
├── 错误描述（用户友好的说明）
├── [重试] 按钮
└── [查看详情] 链接（展开技术详情）
```

---

## 6. 响应式规则

### 6.1 ≥ 1100px（桌面）

- 完整三栏布局
- 研究旅程条显示完整阶段名称
- 侧边栏 300px 固定

### 6.2 600px - 1099px（平板）

- 三栏 → 两栏或单栏（主要内容 + 可折叠侧边栏）
- 研究旅程条阶段名称隐藏，只显示图标
- 侧边栏可收起为图标栏（60px）

### 6.3 < 600px（手机）

- 单栏布局
- 研究旅程条收缩为：进度条 + "当前：XX 阶段"
- 侧边栏变为底部标签栏或汉堡菜单
- HITL gate 全宽显示

---

## 7. 与后端的接口约定

### 7.1 每个页面需要的 API 端点

| 页面 | GET（读取） | POST/PUT（操作） |
|------|-----------|----------------|
| 研究总览 | `/api/v1/projects/{id}/overview` | - |
| 数据与变量 | `/api/v1/projects/{id}/datasets`, `/api/v1/datasets/{id}/schema` | `POST /api/v1/projects/{id}/datasets`（上传） |
| 研究设计 | `/api/v1/projects/{id}/design`, `/api/v1/projects/{id}/outline` | `POST /api/v1/projects/{id}/design/confirm` |
| 实证执行 | `/api/v1/workflows/{id}`, `/api/v1/workflows/{id}/tasks` | `POST /api/v1/workflows/{id}/start`, `POST /api/v1/hitl/confirm` |
| 论文草稿 | `/api/v1/projects/{id}/drafts` | `POST /api/v1/drafts/{id}/sections/{id}/confirm` |
| 产物与复现 | `/api/v1/projects/{id}/artifacts`, `/api/v1/artifacts/{id}` | `POST /api/v1/artifacts/{id}/promote` |
| Agent 控制台 | `/api/v1/agents`, `/api/v1/agents/{id}/details` | `POST /api/v1/agents/{id}/pause` |

### 7.2 数据模型（前端使用的简化模型）

```typescript
// JourneyStage —— 旅程条状态
interface JourneyStage {
  id: string;           // "data", "variables", "identification", ...
  name: string;         // "数据"
  status: "not_started" | "in_progress" | "completed" | "pending_confirmation" | "failed";
  progress: number;     // 0-1
  href: string;         // 对应页面 ID
}

// StageSummary —— 阶段摘要卡片
interface StageSummary {
  stageId: string;
  stageName: string;
  status: JourneyStage["status"];
  metrics: { label: string; value: string }[];
  nextStepHint: string;
  hasPendingAction: boolean;
}

// HITLGate —— 人机确认门
interface HITLGate {
  workflowId: string;
  taskId: string;
  stage: string;
  reason: string;
  details: string;
  suggestedAction?: string;
  timeoutAt: string;    // ISO timestamp
}

// AgentIdentity —— Agent 身份信息
interface AgentIdentity {
  id: string;
  displayName: string;
  role: string;
  roleType: "pipeline" | "dimension";
  status: "active" | "paused" | "error" | "idle";
  avatar: { initial: string; color: string };
  capabilities: string[];
  currentTask?: string;
  totalCost: { wallSeconds: number; invocationCount: number };
}
```

---

## 8. 文件位置与分工

### Kimi 负责的文件

| 文件 | 操作 |
|------|------|
| `Product/web/index.html` | 修改：更新导航结构，新增 4 个 view 容器 |
| `Product/web/assets/styles.css` | 修改：新增旅程条、HITL gate、阶段卡片等样式 |
| `Product/web/assets/app.js` | 修改：新增页面路由、渲染逻辑、状态管理 |

### Codex 负责的文件

| 文件 | 操作 |
|------|------|
| `Product/backend/overview_service.py` | 新建：研究总览数据聚合 |
| `Product/backend/dataset_service.py` | 新建：数据集管理 |
| `Product/backend/design_service.py` | 新建：研究设计管理 |
| `Product/backend/draft_service.py` | 新建：论文草稿管理 |
| `Product/backend/hitl_service.py` | 新建：HITL gate 管理 |
| `Product/app.py` | 修改：注册新路由 |

---

## 9. 验收标准

### 视觉验收

- [ ] 所有 7 个页面能正确切换和渲染
- [ ] 研究旅程条在所有页面可见且状态一致
- [ ] 设计 token 全部使用正确，无硬编码颜色
- [ ] 空状态、加载态、错误态全部实现
- [ ] 响应式布局在 1100px/600px 断点正确切换

### 交互验收

- [ ] 点击旅程条节点正确跳转对应页面
- [ ] 阶段卡片点击正确跳转并定位
- [ ] HITL gate 弹出/关闭动画正确
- [ ] Agent 控制台能显示身份、权限、能力、成本
- [ ] 产物 provenance 能展开显示溯源链

### 数据验收

- [ ] 所有页面从 API 获取数据（mock 亦可）
- [ ] 研究旅程条状态在各页面间一致
- [ ] Mock 数据标记 `evidence_level: "mock"`

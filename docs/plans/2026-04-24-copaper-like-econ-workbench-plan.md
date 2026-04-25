# CoPaper-Like Econ Workbench Implementation Plan

**Goal:** 以 `C` 为终局设计一个本地优先的经济学实证研究工作台，按 `A -> B -> C` 分阶段推进，第一阶段就形成可用于你毕业论文的真实闭环。

**Architecture:** 用四层架构推进：项目结构层、工作流路由层、计量执行层、论文装配层。A 阶段先做本地单用户闭环，B 阶段加入可演示的任务状态和统一入口，C 阶段再升级为网页化产品雏形。

**Tech Stack:** Python, StatsPAI, 本地项目目录结构, Git, Markdown/LaTeX/docx 导出链路, 可选 Stata 兼容层。

---

## 1. 总体阶段规划

### Phase A: Personal Research Workbench

目标：

- 让你自己真的能用它推进毕业论文。
- 跑通研究问题到论文草稿骨架的最小闭环。

必须产出：

- 项目状态文件
- 研究计划文件
- StatsPAI 统一运行入口
- 结果导出规范
- 论文草稿装配入口

验收标准：

- 能在一个真实项目目录上运行。
- 能落地产物到 `Results/` 和 `Manuscripts/`。
- 能记录当前阶段和下一步任务。

### Phase B: Demoable Prototype

目标：

- 形成可演示的统一入口和状态流。
- 不仅能跑，还能清楚展示“系统在做什么”。

必须产出：

- 统一 CLI 或本地 Web 面板
- 任务状态机
- 每步失败原因和恢复建议
- 项目仪表盘

验收标准：

- 陌生人看一遍就能理解主链路。
- 系统运行状态、产物和下一步建议可视化。

### Phase C: Product-Grade Prototype

目标：

- 接近 CoPaper 的产品体验。
- 多项目管理。
- 结构化输入与自然语言输入并存。

必须产出：

- 项目创建向导
- 多项目面板
- 研究链路编排器
- 论文生成入口
- 导出和归档能力

验收标准：

- 不依赖作者本人解释，也能让目标用户上手。
- 具备可持续扩展能力。

## 2. 核心工作包

### Workstream 1: 项目状态与元数据系统

目标：

- 让系统知道“当前项目是什么、做到哪一步了、缺什么”。

需要创建：

- `paper.yaml`
- `state/project_state.json`
- `Tasks/workflow.md`

核心内容：

- 研究题目
- 研究问题
- 当前阶段
- 数据路径
- 核心变量定义
- 方法选择
- 已生成结果
- 下一步任务

为什么先做：

- 没有状态层，后面的分析和写作只能靠聊天上下文，无法产品化。

### Workstream 2: 研究工作流路由

目标：

- 把 `Awesome-Agent-Skills-for-Empirical-Research` 的方法论吸收进本地系统。

需要创建：

- `workflow/stages.py`
- `workflow/router.py`
- `workflow/prompts/`
- `docs/workflow-map.md`

阶段建议：

- question-definition
- data-readiness
- identification-design
- baseline-estimation
- robustness
- interpretation
- manuscript-drafting
- submission-prep

输出形式：

- 当前阶段判断
- 下一步建议
- 推荐调用的分析模块
- 推荐产物清单

### Workstream 3: StatsPAI 分析执行入口

目标：

- 用统一接口调用 StatsPAI，而不是让项目直接散落多个分析脚本。

需要创建：

- `Program/run_paper.py`
- `Program/config/analysis_config.yaml`
- `Program/Analysis/python/`
- `Results/logs/`

能力边界：

- 读取 `paper.yaml`
- 读取 `Data/Final/`
- 选择估计方法
- 运行基准模型
- 运行稳健性分析
- 导出结构化结果摘要

第一批必须覆盖：

- 描述统计
- OLS / FE
- DID
- IV
- 基本稳健性框架

### Workstream 4: 结果标准化

目标：

- 所有结果都以统一格式进入 `Results/`，供手稿层调用。

需要创建：

- `Results/tab/`
- `Results/fig/`
- `Results/json/`
- `Results/logs/`
- `Results/index.json`

结果类型：

- 表格文件
- 图形文件
- 模型摘要 JSON
- 运行日志
- 结果索引

关键要求：

- 手稿不直接读临时输出。
- 每个结果都能追溯到一次分析运行。

### Workstream 5: 论文装配器

目标：

- 让系统不是只会“跑模型”，还会把结果组织成论文骨架。

需要创建：

- `Manuscripts/templates/`
- `Manuscripts/generated/`
- `Program/compose_draft.py`
- `Program/export_docx.py`

第一阶段装配内容：

- 标题页元信息
- 摘要骨架
- 研究问题与识别策略骨架
- 数据说明骨架
- 结果章节骨架
- 稳健性章节骨架
- 结论章节骨架

关键原则：

- 先生成结构化中间稿，再导出 `docx`
- 不直接在 Word 里黑箱拼接全部逻辑

### Workstream 6: Git 与可复现治理

目标：

- 让整个系统天然服务可复现性。

需要创建或完善：

- `.gitignore`
- `README.md`
- `docs/reproducibility.md`
- `docs/branching-strategy.md`

规则重点：

- 结果可追溯
- 数据边界清晰
- 试验分支和主线分支分开
- 日志和临时产物不污染主仓库

## 3. 第一阶段实施顺序

### Sprint 1: 状态层与配置层

交付：

- `paper.yaml`
- `project_state.json`
- `workflow.md`
- 目录扩充与 README 更新

为什么先做：

- 先让系统有“脑子”，知道项目是什么。

### Sprint 2: StatsPAI 统一入口

交付：

- `run_paper.py`
- 统一配置读取
- 基准分析入口
- 稳健性分析入口

为什么第二个做：

- 没有分析入口，就没有真实闭环。

### Sprint 3: 结果标准化

交付：

- 结果索引
- 结果摘要 JSON
- 统一导出位置和命名规范

为什么第三个做：

- 手稿层只能建立在稳定结果层之上。

### Sprint 4: 论文装配器

交付：

- 自动生成论文骨架
- 可导出到结构化中间稿
- 为 `docx` 导出做准备

为什么第四个做：

- 这是从“分析工具”走向“论文工作台”的关键一步。

### Sprint 5: Demo 层

交付：

- 统一命令入口
- 当前阶段展示
- 任务和产物面板

为什么最后做：

- 前四步先保证系统真能干活，再包装成可演示体验。

## 4. 关键风险与应对

### 风险 1：范围膨胀

问题：

- 很容易从“先服务自己的一篇论文”膨胀到“覆盖所有研究场景”。

应对：

- 第一阶段只优化经济学实证因果主链路。
- 其他能力设计上兼容，但不抢实现优先级。

### 风险 2：输出很强但不可解释

问题：

- 系统可能会给出好看的文本，却无法说明依据。

应对：

- 所有结论都必须绑定数据版本、方法配置、结果索引。

### 风险 3：过度依赖某个单一模型或单一外部服务

问题：

- 一旦外部服务不可用，整个系统瘫痪。

应对：

- 本地项目状态和分析流水线必须独立存在。
- 在线服务只作为增强层。

### 风险 4：Word 导出成为最后一公里瓶颈

问题：

- 学校最终交付现实上常常是 `docx`。

应对：

- 内部始终维护结构化中间稿。
- `docx` 作为导出层，而不是内部真实数据结构。

## 5. 第一阶段的明确定义

第一阶段完成，不代表产品完成。它代表：

- 你已经拥有一个真正能帮助毕业论文推进的“研究工作台”
- 不是纯手工，不是纯聊天，不是纯脚本散装
- 它已经具备向 CoPaper-like 产品演化的骨架

## 6. 执行建议

建议的推进方式：

1. 先在当前模板仓库里实现 A 阶段闭环。
2. 用你的真实毕业论文作为第一试点项目。
3. 每个 Sprint 完成后都用真实研究任务做回归测试。
4. 不为演示牺牲内核质量。

## 7. 下一步

下一步不是继续讨论愿景，而是进入 Phase A 的实现计划拆分。优先拆：

- `paper.yaml` 和状态层
- StatsPAI 统一运行入口
- 结果标准化索引
- 论文骨架生成器


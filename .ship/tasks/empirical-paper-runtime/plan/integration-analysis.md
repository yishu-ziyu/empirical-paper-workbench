# Integration Analysis: 实证论文项目模板 × 当前 Empirical Paper Runtime

> 日期：2026-06-22
> 来源：系统性读取 实证论文项目模板（10,272 文件）后输出
> 目的：评估两个项目融合的可能性和具体方案

## 1. 项目架构总结

### 1.1 实证论文项目模板（两个月项目）

```
实证论文项目模板/
├── workflows/
│   ├── registry.json          ← 10 步 workflow 定义（JSON）
│   ├── orchestrator_policy.json
│   ├── tool_adapters.json
│   ├── skill_subagent_registry.json
│   └── agents/                ← Agent 规范文件
├── scripts/
│   ├── 20-33_*.py             ← 11 个 runtime 验证脚本
│   ├── auto_mode_*.py         ← 30+ 个自动模式脚本（复杂已跑通）
│   ├── cgss_*.py              ← CGSS 论文专用脚本
│   └── parent_education_wage_*.py ← 父母教育demo专用脚本
├── Program/
│   ├── run_paper.py           ← 主入口（13KB）
│   ├── workbench/             ← 80+ 个 Python 模块
│   ├── config/                ← YAML 配置
│   └── auto_mode_*.py         ← 自动模式链路
├── Product/
│   ├── app.py                 ← FastAPI 后端（135KB）
│   ├── backend/               ← 75 个子目录
│   ├── web-react/             ← React 前端
│   ├── state/                 ← 项目状态 JSON
│   └── workspaces/            ← 工作区
├── Tasks/
│   ├── todo.md                ← 完整任务历史（P0-P18）
│   ├── current-stage.md       ← 当前状态
│   └── *.bdd.md               ← 50+ 个 BDD 任务文件
├── evidence/
│   ├── claim_register.md
│   ├── evidence_bank.md
│   └── integrity_audit_*.md   ← 8 个审计文件
├── artifacts/
│   ├── orchestrator_run_state.json
│   ├── workflow_runbook_state.json
│   └── *_validation_report.md ← 12 个验证报告
└── state/product/            ← Headless 状态文件
```

**核心数据流**：

```
用户输入 (paper.yaml + 数据)
  ↓
run_paper.py 读取配置
  ↓
workflow_runbook_state.json 决定当前步骤
  ↓
scripts/ 执行对应步骤
  ↓
artifacts/ 产出中间结果
  ↓
state/product/ 更新 headless 状态
  ↓
Product/app.py 暴露 API
  ↓
React 前端展示
```

### 1.2 当前 Empirical Paper Runtime（CHARLS 样例）

```
StatspAI_跑通一次_CHARLS_DID/
├── runtime/
│   ├── pipeline.py            ← 核心引擎（271 行）
│   ├── state.py               ← 状态持久化（119 行）
│   ├── checkpoints.py         ← Human checkpoint（64 行）
│   ├── cli.py                 ← CLI 入口（54 行）
│   └── README.md
├── workflows/
│   └── registry.json          ← 10 步 workflow 定义
├── scripts/
│   ├── 01-12_*.py             ← 12 个分析脚本（已跑通）
│   └── 21-33_*.py             ← 11 个验证脚本
├── artifacts/
│   ├── pipeline_state.json    ← 运行时状态
│   ├── pipeline_report.md     ← 执行报告
│   └── *.pkl / *.csv / *.tex  ← 39 个产物
└── workbench/
    └── index.html             ← 单文件工作台（被用户评为 1/100 分）
```

**核心数据流**：

```
用户输入 (causal_question.yaml + 数据路径)
  ↓
runtime/cli.py 解析参数
  ↓
runtime/pipeline.py 读取 workflows/registry.json
  ↓
按 step 顺序执行，处理 human checkpoint
  ↓
runtime/state.py 持久化状态
  ↓
scripts/ 执行对应步骤
  ↓
artifacts/ 产出结果
  ↓
workbench/index.html 静态展示
```

### 1.3 关键相似点

| 维度 | 项目模板 | CHARLS 样例 | 说明 |
|------|----------|-------------|------|
| Workflow 定义 | `workflows/registry.json` | `workflows/registry.json` | **完全相同**（10 步，相同 ID） |
| 脚本编号 | `scripts/01-33_*.py` | `scripts/01-33_*.py` | **相同编号体系** |
| 状态文件 | `artifacts/workflow_runbook_state.json` | `artifacts/pipeline_state.json` | 格式不同 |
| Human checkpoint | 有（JSON 定义） | 有（Python 代码） | 实现方式不同 |
| 产物检查 | 有（required_outputs） | 有（required_outputs） | **完全相同** |
| 门控机制 | 有（gates） | 有（gates） | **完全相同** |

### 1.4 关键差异点

| 维度 | 项目模板 | CHARLS 样例 | 融合影响 |
|------|----------|-------------|----------|
| Runtime 实现 | 30+ auto_mode_*.py 脚本 | 1 个 pipeline.py（271 行） | **需要统一** |
| 复杂度 | 极高（P0-P18，50+ BDD 文件） | 极简（4 个核心文件） | 需要取舍 |
| 产品界面 | FastAPI + React（135KB 后端） | 静态 HTML（被毙） | React 保留，workbench 重建 |
| 状态管理 | JSON 文件 + headless state | JSON 文件 + pipeline_state | 可统一为 JSON |
| 证据系统 | 完善（claim register + integrity audit） | 缺失 | **需要移植** |
| 测试覆盖 | 1214 项测试 | 无 | **需要移植** |
| 数据适配 | CFPS/CGSS/CLDS | CHARLS only | 需要抽象化 |

## 2. 融合方案

### 2.1 核心策略

**以 CHARLS 的 runtime/pipeline.py 为基础，吸收项目模板的丰富特性**。

原因：
1. CHARLS 版**已跑通**（11 步，全部 pass）
2. CHARLS 版**极简**（4 个核心文件，~500 行），易于理解和修改
3. 项目模板版**过于复杂**（30+ auto_mode_*.py，难以维护）
4. 两者共享相同的 workflow registry 格式（可直接复用）

### 2.2 具体融合步骤

#### Step 1: Runtime 统一（P0）

**目标**：用 CHARLS 的 `runtime/pipeline.py` 替换项目模板的 `auto_mode_*.py`。

**方案**：
```
实证论文项目模板/
├── runtime/                          ← 从 CHARLS 复制
│   ├── pipeline.py                   ← 核心引擎
│   ├── state.py                      ← 状态持久化
│   ├── checkpoints.py                ← Human checkpoint
│   ├── cli.py                        ← CLI 入口
│   └── README.md
├── workflows/
│   ├── registry.json                 ← 保留（10 步定义）
│   └── ...
├── scripts/
│   ├── 01-12_*.py                    ← 保留（分析脚本）
│   ├── 21-33_*.py                    ← 保留（验证脚本）
│   └── runtime_runner.py             ← 新增：调用 runtime/pipeline.py
└── ...
```

**改动点**：
1. 复制 CHARLS 的 `runtime/` 到项目模板
2. 修改 `runtime/pipeline.py` 中的 `ROOT` 路径，使其兼容项目模板的目录结构
3. 修改 `runtime/state.py` 读写 `artifacts/pipeline_state.json`（而非项目模板的 `workflow_runbook_state.json`）
4. 新增 `scripts/runtime_runner.py`：调用 `runtime/cli.py`，统一入口
5. 保留项目模板的 `auto_mode_*.py` 作为 legacy，但不作为主路径

**风险**：
- 低：runtime/pipeline.py 已跑通，只改路径和状态文件位置
- 中：项目模板的 1214 项测试可能依赖 auto_mode_*.py，需要适配

#### Step 2: 跨题验证（P0）

**目标**：用 CFPS 最低工资消费效应题目跑通 10 步 workflow。

**方案**：
```
StatspAI_第二个样例_最低工资消费效应/
├── causal_question.yaml             ← 已有
├── research_design.md               ← 已有
├── scripts/
│   ├── 01_data_contract.py          ← 已有（已验证）
│   ├── 02_sample_construct.py       ← 已有（已验证，60,754 条观测）
│   ├── 03-10_*.py                   ← 待写（描述统计 → 审稿回复）
├── artifacts/
│   ├── analysis_ready.pkl           ← 已有
│   ├── feasibility_report.md        ← 已有
│   └── pipeline_state.json          ← 待生成
└── runtime/                          ← 从项目模板复制
```

**关键改动**：
1. 复制项目模板的 `runtime/` 到这个项目
2. 写 `scripts/03_descriptive_stats.py` → `scripts/10_defense.py`
3. 用 `runtime/cli.py --mode execute` 跑通 10 步

**验收标准**：
- `python3 runtime/cli.py --mode execute` 输出 `pipeline_report.md`
- 10 步全部 pass，状态 `done`
- 产物：`paper.pdf` + `tables/` + `figures/` + `repro_report.md`

#### Step 3: 工作台重建（P1）

**目标**：重建高质量工作台，替代 CHARLS 的 1/100 分版本。

**方案**：
```
项目模板/
├── workbench/
│   ├── index.html                   ← 单文件，自包含
│   ├── api.py                       ← 可选：动态 API
│   └── serve.py                     ← 可选：静态 JSON server
└── Product/
    └── web-react/src/
        └── components/
            └── Workbench.tsx        ← React 版本（嵌入产品壳）
```

**设计参考**：
1. 调研 3 个高质量工作台设计（GitHub、Linear、Notion 的 timeline）
2. 用 React + Tailwind 实现（与现有产品壳一致）
3. 关键交互：点击卡片展开详情、hover 动效、响应式布局

**不采用**：
- 纯静态 HTML（CHARLS 版已证明不够好）
- 复杂前端框架（保持与现有 React 壳一致）

#### Step 4: StatsPAI DID 适配器（P1）

**目标**：在 runtime 中接入 DID 方法。

**方案**：
```
项目模板/
├── runtime/
│   └── adapters/
│       ├── did_adapter.py          ← 新增
│       ├── event_study.py          ← 从 scripts/05_event_study.py 提取
│       └── base_adapter.py         ← 基类
└── scripts/
    └── 05_causal_analysis.py        ← 修改为调用 did_adapter
```

**关键改动**：
1. 提取 CHARLS 的 `scripts/05_event_study.py` + `scripts/06_table2.py` 核心逻辑
2. 包装成通用 `did_adapter.py`，输入标准数据集，输出 tables/figures/model_log
3. 在 `runtime/pipeline.py` 中注册为 Step 5 的执行器

### 2.3 不融合的部分

以下特性**保留在项目模板**，不迁移到 runtime：

| 特性 | 原因 |
|------|------|
| P0-P18 任务链 | 过于复杂，只在一个 demo 上验证，跨题未验证 |
| auto_mode_*.py | 30+ 脚本，命名混乱，维护成本高 |
| Headless state | 项目模板特有，与 runtime 解耦 |
| React 产品壳 | 独立存在，不依赖 runtime |
| 证据审计系统 | 项目模板特有，后续作为 runtime 的输出消费者 |

### 2.4 数据流融合图

```
用户输入 (causal_question.yaml + 数据)
  ↓
runtime/cli.py                    ← 从 CHARLS 复制
  ↓
runtime/pipeline.py               ← 从 CHARLS 复制（修改路径）
  ↓
workflows/registry.json           ← 项目模板已有（10 步定义）
  ↓
scripts/01-10_*.py                ← 项目模板已有（分析脚本）
  ↓
runtime/adapters/did_adapter.py   ← 新增（DID 方法）
  ↓
artifacts/                        ← 产物（统一格式）
  ↓
workbench/index.html              ← 重建（可视化）
  ↓
Product/app.py                    ← 项目模板已有（FastAPI）
  ↓
React 前端                        ← 项目模板已有
```

## 3. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Runtime 统一破坏现有测试 | 中 | 1214 项测试失败 | 先复制 runtime/，不改动现有代码，测试通过后再迁移 |
| 跨题验证发现 workflow 定义有问题 | 中 | 需要修改 registry.json | 保留 rollback_to 机制，失败时回退 |
| 工作台设计再被用户评为低分 | 中 | 浪费时间 | 先调研 3 个参考设计，再做，不 guess |
| StatsPAI DID 适配器依赖 Stata | 中 | 需要 Stata 环境 | 先用 Python pandas/statsmodels 实现，Stata 版后续 |
| 项目模板代码质量参差不齐 | 高 | 融合后难以维护 | 只融合已跑通的部分，未跑通的先不迁移 |

## 4. 推荐执行顺序

### Week 1（2026-06-22 → 2026-06-29）

1. **Day 1-2**：复制 CHARLS 的 `runtime/` 到项目模板，修改路径，跑通 dry-run
2. **Day 3-4**：用 CFPS 最低工资题目跑通 10 步 workflow（跨题验证）
3. **Day 5**：修复跨题验证中发现的问题，更新 registry.json

### Week 2（2026-06-30 → 2026-07-06）

1. **Day 1-2**：调研工作台设计，重建高质量版本
2. **Day 3-4**：实现 StatsPAI DID 适配器
3. **Day 5**：用 DID 适配器重跑 Step 5，验证产出

## 5. 结论

**两个项目可以融合，而且应该融合。**

理由：
1. 两者共享相同的 workflow registry 格式（10 步，相同 ID）
2. CHARLS 的 runtime 极简可执行，项目模板的生态丰富但复杂
3. 融合后既能保留项目模板的丰富特性（证据审计、React 产品壳、1214 项测试），又能获得 CHARLS 的可执行 runtime
4. 跨题验证是必经之路——只在一个 demo 上跑通不算产品

**核心原则**：
- Runtime 层：用 CHARLS 的极简实现
- 产品层：保留项目模板的 FastAPI + React
- 脚本层：保留项目模板的 30+ 脚本，但通过 runtime 统一调用
- 工作台：重建高质量版本，嵌入 React 产品壳

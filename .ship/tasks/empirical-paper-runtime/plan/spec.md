# Spec: 全自动论文机产品化

> 日期：2026-06-22
> 项目：实证论文项目模板 + StatspAI_跑通一次_CHARLS_DID
> 阶段：Design Phase 0

## 项目架构分析

### 实证论文项目模板（两个月项目，10,272 个文件）

**三层架构**：

- Layer 1: CLI Pipeline (`Program/run_paper.py`) — 输入 paper.yaml → 跑 StatsPAI → 输出 Markdown/LaTeX/Quarto
- Layer 2: Agent Workflow (`workflows/registry.json` + `scripts/`) — 10 步 workflow，两套 runtime（auto_mode_* 30+ 脚本 + runtime/pipeline.py 简洁版）
- Layer 3: Product Shell (`Product/`) — FastAPI 后端（135KB）+ React 前端 + Headless State

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

**已完成的工作**：
- P0-P18 在"父母受教育水平对子女工资收入的影响"demo 上全部跑通
- 1214 项测试通过
- 产出：paper_draft.docx + final_paper.pdf + 交付包 + 证据审计
- 当前推进线：CGSS 互联网使用与幸福感论文

### CHARLS 样例（当前 runtime）

**简洁架构**：

```
runtime/
├── pipeline.py            ← 核心引擎（271 行）
├── state.py               ← 状态持久化（119 行）
├── checkpoints.py         ← Human checkpoint（64 行）
├── cli.py                 ← CLI 入口（54 行）
└── README.md

workflows/
└── registry.json          ← 10 步 workflow 定义（与项目模板完全相同）

scripts/
└── 01-33_*.py             ← 33 个分析/验证脚本
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

### 关键相似点

| 维度 | 项目模板 | CHARLS 样例 | 说明 |
|------|----------|-------------|------|
| Workflow 定义 | `workflows/registry.json` | `workflows/registry.json` | 完全相同（10 步，相同 ID） |
| 脚本编号 | `scripts/01-33_*.py` | `scripts/01-33_*.py` | 相同编号体系 |
| 产物检查 | 有（required_outputs） | 有（required_outputs） | 完全相同 |
| 门控机制 | 有（gates） | 有（gates） | 完全相同 |

### 关键差异点

| 维度 | 项目模板 | CHARLS 样例 | 融合影响 |
|------|----------|-------------|----------|
| Runtime 实现 | 30+ auto_mode_*.py 脚本 | 1 个 pipeline.py（271 行） | 需要统一 |
| 复杂度 | 极高（P0-P18，50+ BDD 文件） | 极简（4 个核心文件） | 需要取舍 |
| 产品界面 | FastAPI + React（135KB 后端） | 静态 HTML（被毙） | React 保留，workbench 重建 |
| 状态管理 | JSON 文件 + headless state | JSON 文件 + pipeline_state | 可统一为 JSON |
| 证据系统 | 完善（claim register + integrity audit） | 缺失 | 需要移植 |
| 测试覆盖 | 1214 项测试 | 无 | 需要移植 |

## 融合方案

### 核心策略

**以 CHARLS 的 runtime/pipeline.py 为基础，吸收项目模板的丰富特性**。

理由：
1. CHARLS 版已跑通（11 步，全部 pass）
2. CHARLS 版极简（4 个核心文件，~500 行），易于理解和修改
3. 项目模板版过于复杂（30+ auto_mode_*.py，难以维护）
4. 两者共享相同的 workflow registry 格式（可直接复用）

### 具体融合步骤

#### Step 1: Runtime 统一（P0）

- 复制 CHARLS 的 `runtime/` 到项目模板
- 修改路径适配项目模板目录结构
- 修改状态文件路径为 `artifacts/pipeline_state.json`
- 新增 `scripts/runtime_runner.py` 统一入口
- 保留项目模板的 `auto_mode_*.py` 作为 legacy，但不作为主路径

#### Step 2: 跨题验证（P0）

- 用 CFPS 最低工资消费效应题目跑通 10 步 workflow
- 验证 runtime 不是 CHARLS 个例
- 样本已构造完成：60,754 条观测，31 省，DID 信号存在（-1.58%）

#### Step 3: 高质量工作台（P1）

- 调研 3 个参考设计（Linear、GitHub Projects、Notion timeline）
- 用 React + Tailwind 实现（与现有产品壳一致）
- 嵌入 `Product/web-react/src/components/Workbench.tsx`

#### Step 4: StatsPAI DID 适配器（P1）

- 提取 CHARLS 的 `scripts/05_event_study.py` + `scripts/06_table2.py` 核心逻辑
- 包装成通用 `runtime/adapters/did_adapter.py`
- 在 `runtime/pipeline.py` 中注册为 Step 5 的执行器

## Acceptance Criteria

### AC1: Runtime 统一

- [ ] `runtime/pipeline.py` 能读取 `workflows/registry.json` 的 10 步定义
- [ ] `runtime/cli.py` 支持 `--mode dry-run`，预演全部 10 步不执行
- [ ] `runtime/cli.py` 支持 `--mode execute`，真实执行 10 步
- [ ] `runtime/cli.py` 支持 `--resume`，从上次停止处继续
- [ ] `runtime/cli.py` 支持 `--status`，显示当前进度
- [ ] Human checkpoint 不可绕过——停下来等 yes
- [ ] 产物已存在时自动跳过（幂等）
- [ ] 失败即停，写 report，退出码非 0

### AC2: 跨题验证

- [ ] 用 CFPS 最低工资消费效应题目跑通 10 步 workflow
- [ ] 每步产出 required_outputs 中定义的产物
- [ ] 最终产出：`paper.pdf` + `tables/` + `figures/` + `repro_report.md`
- [ ] 运行记录写入 `artifacts/pipeline_report.md`
- [ ] 状态持久化到 `artifacts/pipeline_state.json`

### AC3: 高质量工作台

- [ ] 浏览器打开 workbench/index.html 能看到 10 步 workflow 卡片
- [ ] 每步卡片显示：状态图标、名称、目的、产物路径、human checkpoint、failure code
- [ ] 顶部 summary bar：流水线状态 / 完成数 / 失败次数
- [ ] 点击卡片展开详情（产物 + gate 命令 + 检查点）
- [ ] 响应式布局（桌面 + 移动端）
- [ ] 纯静态 HTML，零依赖，无需服务器

### AC4: StatsPAI DID 适配器

- [ ] `runtime/adapters/did_adapter.py` 能读取标准数据集（CSV/parquet）
- [ ] 自动跑事件研究图（平行趋势检验）
- [ ] 自动跑主回归（DID coefficient + 聚类稳健标准误）
- [ ] 自动跑异质性分析（按收入分位数）
- [ ] 产出：`tables/table2_did.csv` + `figures/event_study.png` + `model_log.md`

### AC5: 证据审计

- [ ] 每个 claim 自动绑定到真实表格/图表/运行 ID
- [ ] `evidence/claim_register.md` 自动更新
- [ ] `artifacts/integrity_audit.md` 自动生成
- [ ] 缺失证据时标记 `needs_evidence` 而非静默跳过

## Golden Journeys

### Journey 1: 新题目从零到论文（端到端）

```
用户输入: causal_question.yaml + 数据路径
  ↓
runtime/cli.py --mode execute
  ↓
Step 1/10: 选题与研究设计 → research_design.md ✅
Step 2/10: 文献检索与综述 → litreview/ ✅
Step 3/10: 论文阅读与拆解 → litreview/notes/ ✅
Step 4/10: 数据获取与清洗 → Data/Final/ ✅
Step 5/10: 统计分析与因果推断 → tables/ + figures/ ✅
Step 6/10: 论文写作 → paper.tex + paper.pdf ✅
Step 7/10: 论文修改与润色 → revision_plan.md ✅
Step 8/10: 引用管理与排版 → references.bib ✅
Step 9/10: 论文复现与可复现研究 → repro_report.md ✅
Step 10/10: 审稿回复与学术答辩 → response_matrix.md ✅
  ↓
输出: paper.pdf + 证据包 + 复现说明
```

**验收标准**：用户在终端跑一条命令，10 步全部 pass，产出 paper.pdf。

### Journey 2: 工作台可视化

```
用户双击 workbench/index.html
  ↓
浏览器打开，看到 10 步 workflow 卡片
  ↓
顶部 summary: 流水线状态 done, 11/11 步完成
  ↓
点击 Step 5 卡片 → 展开详情
  ↓
看到: 产物路径 tables/ + figures/ + model_log.md
      gate 命令: python3 scripts/05_event_study.py && python3 scripts/06_table2.py
      human checkpoint: 结果是否足以支撑主张
      failure codes: CAUSAL_PLACEBO_FAILS, CAUSAL_RESULT_OVERCLAIMED
```

**验收标准**：纯静态 HTML 直接打开，无服务器，交互流畅。

### Journey 3: 中断恢复

```
用户跑 runtime/cli.py --mode execute
  ↓
Step 5/10 卡在 human checkpoint（用户离开）
  ↓
用户关闭终端
  ↓
用户重新跑 runtime/cli.py --resume
  ↓
runtime 读取 pipeline_state.json
  ↓
跳过已完成的 Step 1-4，从 Step 5 继续
  ↓
用户确认 checkpoint → 继续 Step 6-10
```

**验收标准**：resume 后从正确的位置继续，不重复执行已完成步骤。

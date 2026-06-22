# Plan: 全自动论文机产品化实施计划

> 日期：2026-06-22
> 项目：实证论文项目模板 + StatspAI_跑通一次_CHARLS_DID
> 阶段：Design → Dev

## 用户故事

### Story 1: Runtime 统一（P0）

**作为** 开发者，
**我想要** 一套统一的 runtime 能读取 workflows/registry.json 并执行 10 步 workflow，
**以便** 跨题目复用，不用维护两套 runtime。

**任务**：
1. 复制 CHARLS 的 `runtime/` 到项目模板（pipeline.py, state.py, checkpoints.py, cli.py）
2. 修改路径适配项目模板目录结构
3. 修改状态文件路径为 `artifacts/pipeline_state.json`
4. 新增 `scripts/runtime_runner.py` 统一入口
5. 跑 `python3 runtime/cli.py --mode dry-run` 验证 10 步预演
6. 跑 `python3 runtime/cli.py --mode execute` 验证真实执行

**验收**：
- `runtime/cli.py --mode dry-run` 输出 10 步预演
- `runtime/cli.py --mode execute` 跑通 10 步
- 产物：`artifacts/pipeline_state.json` + `artifacts/pipeline_report.md`

---

### Story 2: 跨题验证（P0）

**作为** 用户，
**我想要** 用第二个题目（CFPS 最低工资消费效应）跑通 10 步 workflow，
**以便** 验证 runtime 不是 CHARLS 个例。

**任务**：
1. 复制 `runtime/` 到 `StatspAI_第二个样例_最低工资消费效应/`
2. 写 `scripts/03_descriptive_stats.py`（描述统计 + Table 1）
3. 写 `scripts/04_event_study.py`（事件研究图 + 平行趋势检验）
4. 写 `scripts/05_did_regression.py`（主回归 + 异质性 + 稳健性）
5. 写 `scripts/06_paper_writing.py`（论文写作 + LaTeX 编译）
6. 写 `scripts/07_revision.py`（审稿回复）
7. 写 `scripts/08_format_citation.py`（引用管理）
8. 写 `scripts/09_replication.py`（复现说明）
9. 写 `scripts/10_defense.py`（答辩准备）
10. 跑 `python3 runtime/cli.py --mode execute` 验证端到端

**验收**：
- 10 步全部 pass，状态 `done`
- 产物：`paper.pdf` + `tables/` + `figures/` + `repro_report.md`

---

### Story 3: 高质量工作台（P1）

**作为** 用户，
**我想要** 一个高质量的可视化工作台展示 10 步 workflow 状态，
**以便** 直观看到进度、产物、human checkpoint、failure code。

**任务**：
1. 调研 3 个参考设计（Linear、GitHub Projects、Notion timeline）
2. 设计工作台交互原型（Figma 或手绘）
3. 用 React + Tailwind 实现（与现有产品壳一致）
4. 关键交互：点击卡片展开详情、hover 动效、响应式布局
5. 嵌入 `Product/web-react/src/components/Workbench.tsx`
6. 浏览器验收（桌面 + 移动端）

**验收**：
- 浏览器打开 http://127.0.0.1:8765/workbench 看到 10 步卡片
- 点击卡片展开详情（产物 + gate + checkpoint + failure code）
- 响应式布局（桌面 + 390px 移动端）

---

### Story 4: StatsPAI DID 适配器（P1）

**作为** 开发者，
**我想要** 一个通用的 DID 适配器能自动跑事件研究 + 主回归 + 异质性，
**以便** 在 runtime 中接入 DID 方法。

**任务**：
1. 提取 CHARLS 的 `scripts/05_event_study.py` + `scripts/06_table2.py` 核心逻辑
2. 包装成 `runtime/adapters/did_adapter.py`
3. 输入标准数据集（CSV/parquet），输出 tables/figures/model_log
4. 在 `runtime/pipeline.py` 中注册为 Step 5 的执行器
5. 用 CFPS 最低工资数据验证

**验收**：
- `did_adapter.py` 读取 CSV 输出 `tables/table2_did.csv` + `figures/event_study.png`
- 事件研究图显示平行趋势
- 主回归 DID coefficient 显著（p < 0.05）

# Scope: 全自动论文机产品化

> 日期：2026-06-22
> 项目：实证论文项目模板 + StatspAI_跑通一次_CHARLS_DID
> 阶段：Design Phase 0

## Appetite

**2 周冲刺**（2026-06-22 → 2026-07-06）

目标：在 2 周内完成从"设计文档"到"可用产品"的最小闭环。

## In Scope

### 1. Runtime 统一（P0 — 第 1 周）

- 以 CHARLS 的 `runtime/pipeline.py` 为基础，重构为通用 orchestrator
- 兼容主仓库的 `workflows/registry.json`（10 步 workflow 定义）
- 支持 `--dry-run` / `--execute` / `--resume` / `--status` 四种模式
- Human checkpoint 不可绕过，失败即停，状态可恢复

### 2. 跨题验证（P0 — 第 1 周）

- 用第二个题目（最低工资消费效应，CFPS 数据）跑通 10 步 workflow
- 验证 runtime 不是 CHARLS 个例
- 产出：`artifacts/feasibility_report.md` + 完整运行记录

### 3. 高质量工作台（P1 — 第 2 周）

- 调研好的前端设计模式（线性 timeline + 卡片展开 + 状态指示）
- 重建 workbench，替代 CHARLS 的 1/100 分版本
- 纯静态 HTML，零依赖，直接浏览器打开
- 显示：10 步状态、human checkpoint、产物路径、failure code

### 4. StatsPAI 方法扩展（P1 — 第 2 周）

- 在 runtime 中接入 DID 方法（已有 CHARLS 脚本可复用）
- 把 `scripts/05_event_study.py` + `scripts/06_table2.py` 包装成通用 adapter
- 产出：`runtime/adapters/did_adapter.py`

## Out of Scope

- ❌ 不做完整云端部署（当前只做本地可运行版本）
- ❌ 不重写全部 UI（只做 workbench，React 产品壳保留不动）
- ❌ 不做任意题目通用 adapter 抽象（先跑通 DID，其他方法后续）
- ❌ 不把未经证据链支持的探索性草稿静默提升为正式论文
- ❌ 不做 IV / RDD / 合成控制（本轮只做 DID）
- ❌ 不做中文文献检索（CNKI 权限问题，后续解决）

## Risks

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| CFPS 数据字段不足 | 中 | 跨题验证失败 | 已确认 60,754 条观测可用，核心变量存在 |
| Runtime 重构破坏现有 P0-P18 | 低 | 主仓库测试失败 | 重构为独立 `runtime/` 目录，不碰现有代码 |
| 工作台设计再被用户评为低分 | 中 | 浪费时间 | 先调研 3 个参考设计，再做，不 guess |
| StatsPAI DID 适配器依赖 Stata | 中 | 需要 Stata 环境 | 先用 Python pandas/statsmodels 实现，Stata 版后续 |
| Ship auto 流程中断 | 低 | 设计文档不完整 | 本轮先完成 design artifacts，dev phase 下轮继续 |

## Open Questions

1. 第二个题目是否固定为"最低工资消费效应"？还是等 runtime 统一后再选？
2. 工作台是独立 HTML 还是嵌入 React 产品壳？
3. StatsPAI 的 DID 实现用 Python 还是 Stata？

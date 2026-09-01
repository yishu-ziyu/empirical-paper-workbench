# ADR 0010 — 一个网页产品

- **Status:** Accepted
- **Date:** 2026-08-16
- **Supersedes:** 已退役的「多仓多入口」工作区契约
- **Related:** ADR 0003（Facade / NodeResult）、ADR 0004（文献节点）、识别验真 / 稳健性节点

## Context

本决策作出时，工作区里并排放着三份东西：

| 本地 | 实际身份 |
|------|----------|
| `econpaper/` | GitHub `empirical-paper-workbench` 的 `main`。网页端。 |
| 旧 CLI checkout | 同一远程的长分支，现已删除。 |
| CHARLS DID 论文工作目录 | 第一阶段样例，现已删除；脱敏设计夹具留在产品仓。 |

旧契约把它们写成两套入口。结果是 Cursor 里三个根、两套身份。

不能并的是 **Git 历史**。能并的是 **产品身份**：只做一个网页产品。

## Decision

1. **唯一产品 = `econpaper/` 网页端。** 上传数据 → 设定方向 → 识别验真 → 文献 → 估计 / 设定表 → 稳健性 → 逐章写 → 导出。
2. **旧 CLI 只做一次性能力核对，不搬整仓：** 产品已覆盖的能力不重复迁移。
3. **CHARLS DID 降为 `fixtures/charls_did/`。** 只收脱敏研究说明，不收原始数据和 PDF。
4. **StatsPAI 是唯一保留的本地源码依赖。** 它位于 `dependencies/StatsPAI/`；识别、稳健性和代码导出为产品自有实现。
5. **核对结束后删除旧模板仓和无用论文目录。** 私有研究材料只在 `materials/` 中按明确价值保留。

## Non-Goals

- 不合并 Git 历史。
- 不把旧 CLI 门禁剧场、模板 React 壳搬进来。
- 不把 CHARLS 原始微观数据纳入 git。

## Consequences

- `set_direction` 写出 `main_specification`，识别 / 稳健 / 设定表可以直接用。
- `search_literature` 增加 `crossref` 源。pytest / `ECONPAPER_LLM=mock` 仍 mock；运行时最后一档为 `crossref`（paper-engine 文献批次取代本 ADR 原先的「默认 mock」）。无网或 Crossref 失败标 `mock_degraded`。
- Journey 统一 8 站，可介入 `{0, 2, 3, 5, 6}`。
- 开发只进 `econpaper/`。

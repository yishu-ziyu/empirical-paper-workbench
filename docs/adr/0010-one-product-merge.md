# ADR 0010 — 一个网页产品

- **Status:** Accepted
- **Date:** 2026-08-16
- **Supersedes:** 工作区 `项目入口.md` 的「两仓两坐法、仓库先别并」契约
- **Related:** ADR 0003（Facade / NodeResult）、ADR 0004（文献节点）、识别验真 / 稳健性节点

## Context

工作区里并排坐着三份东西：

| 本地 | 实际身份 |
|------|----------|
| `econpaper/` | GitHub `empirical-paper-workbench` 的 `main`。网页端。 |
| `实证论文项目模板/` | 同一远程的长分支。旧 CLI。 |
| `papers/StatspAI_跑通一次_CHARLS_DID/` | 第一阶段样例。无产品远程。 |

旧契约把它们写成两套入口。结果是 Cursor 里三个根、两套身份。

不能并的是 **Git 历史**。能并的是 **产品身份**：只做一个网页产品。

## Decision

1. **唯一产品 = `econpaper/` 网页端。** 上传数据 → 设定方向 → 识别验真 → 文献 → 估计 / 设定表 → 稳健性 → 逐章写 → 导出。
2. **从旧 CLI 只抽引擎，不搬整仓：** 研究方向规范化、设定表、Crossref 检索。
3. **CHARLS DID 降为 `fixtures/charls_did/`。** 只收研究说明，不收原始数据和 PDF。
4. **StatsPAI / stata-code / `_refs/AERS-ref` 仍与产品同级。** 它们是库。
5. **模板仓与 `papers/` 改为归档。** 可考古，不再当开发入口。

## Non-Goals

- 不合并 Git 历史。
- 不把旧 CLI 门禁剧场、模板 React 壳搬进来。
- 不把 CHARLS 原始微观数据纳入 git。

## Consequences

- `set_direction` 写出 `main_specification`，识别 / 稳健 / 设定表可以直接用。
- `search_literature` 增加 `crossref` 源。pytest / `ECONPAPER_LLM=mock` 仍 mock；运行时最后一档为 `crossref`（paper-engine 文献批次取代本 ADR 原先的「默认 mock」）。无网或 Crossref 失败标 `mock_degraded`。
- Journey 统一 8 站，可介入 `{0, 2, 3, 5, 6}`。
- 开发只进 `econpaper/`。

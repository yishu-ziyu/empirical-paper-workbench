# econpaper 文档

所有项目文档都在本目录。每个文件夹有一个 `README.md` 做目录；长文档拆成“概览 + 目录”加同名子文件夹里的分节文件。先读概览，按需再往下点。

写作和维护规则见 [文档约定](conventions.md)。

## 按问题找

| 我想知道 | 从这里开始 |
|---|---|
| 这个产品是什么、给谁用、核心流程 | [产品](product/README.md) → [核心产品契约](product/core-product-contract.md) |
| 某个功能现在应该怎么表现 | [规格](specs/README.md) → [当前前端交互基线](specs/frontend-interaction-current.md) |
| 某段后端/Agent 行为的冻结约束 | [契约](contracts/README.md) |
| 某个 HTTP / WebSocket 接口 | [API](api/README.md) |
| 为什么当初这样设计 | [架构决策 ADR](adr/README.md) |
| 视觉、交互、动效 | [设计](design/README.md) |
| 本地跑起来、依赖、离线评测 | [开发](dev/README.md) |
| 部署 | [部署](deployment/README.md) |
| 某项工作是怎么验收的 | [验收](acceptance/README.md) · [独立评审](reviews/README.md) |
| 过去的计划、诊断与开发日志 | [计划](plans/README.md) · [笔记](notes/README.md) · [仓库清理记录](cleanup/README.md) |

## 文件夹

| 文件夹 | 放什么 | 状态 |
|---|---|---|
| [product/](product/README.md) | 产品契约、业务流程、术语、用户手册、UX 待办 | 现行，随功能更新 |
| [specs/](specs/README.md) | 功能规格与交互基线 | 现行，随功能更新 |
| [contracts/](contracts/README.md) | 各切片冻结的行为契约（识别设计、找数据/文献、真实取数、数据补全等） | 现行，改行为时同步 |
| [api/](api/README.md) | HTTP 端点、WebSocket 协议、OpenAPI 规范 | 现行；`openapi.json` 由 `make gen-api` 生成 |
| [adr/](adr/README.md) | 架构决策记录 | 只追加；被取代时写新 ADR |
| [design/](design/README.md) | 设计稿、交互动效纪律、审阅原型 | 现行 + 历史稿 |
| [dev/](dev/README.md) | 本地运行、本地依赖、离线评测 | 现行 |
| [deployment/](deployment/README.md) | 部署手册与私有试用环境 | 现行 |
| [acceptance/](acceptance/README.md) | 验收契约、实施报告、独立验证报告及证据 | 历史记录，只追加 |
| [reviews/](reviews/README.md) | 独立评审结论 | 历史记录，只追加 |
| [plans/](plans/README.md) | 大任务的执行计划 | 历史记录 |
| [notes/](notes/README.md) | 开发日志、试用记录、定位诊断 | 历史记录 |
| [cleanup/](cleanup/README.md) | 2026-09 本地仓库清理的台账 | 历史记录 |

## 不在 docs 里的

- 仓库入口：根目录 [README.md](../README.md)；Agent 规则：[AGENTS.md](../AGENTS.md)。
- Agent 运行状态：`runtime/STATE.md` 与 `runtime/tasks/`（任务恢复用，不是文档）。
- Agent 学习记录：`agent-learning/`（去敏运行记录）。
- 组件自带说明：`frontend/README.md`、`eval/README.md`、`fixtures/*/README.md`，只讲本目录怎么用。

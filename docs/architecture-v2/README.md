# 架构重塑文档 v2 —— 索引

日期：2026-05-10

---

## 文档清单

| 文档 | 读者 | 内容 |
|------|------|------|
| [interaction-design.md](./interaction-design.md) | Kimi（前端设计） | 7 个页面的详细交互设计、组件规范、动效、响应式规则 |
| [technical-architecture.md](./technical-architecture.md) | Codex（后端实现） | 7 层架构详述、新增 7 个服务设计、数据模型、Agent 编排 |
| [api-contract-v2.md](./api-contract-v2.md) | Kimi + Codex | 新增 API 端点、请求/响应契约、错误码、测试契约 |
| [agent-orchestration.md](./agent-orchestration.md) | Codex | Agent 编排详细设计（待补充） |

## 阅读顺序

1. **Kimi**：先读 `interaction-design.md`，了解页面布局和交互需求；然后读 `api-contract-v2.md` 了解需要调用的端点
2. **Codex**：先读 `technical-architecture.md`，了解服务边界；然后读 `api-contract-v2.md` 了解具体端点契约

## 与现有文档的关系

| 现有文档 | 关系 |
|---------|------|
| `docs/empirical-research-os-architecture-2026-05-08.md` | v2 架构的上位文档，v2 是对其的细化和落地 |
| `docs/frontend-architecture-2026-05-08.md` | v2 交互设计的前置文档，v2 扩展了 7 个新页面 |
| `docs/product-api-contract.md` | v2 API 契约的前置文档，v2 在 `/api/v1/` 基础上扩展 |
| `docs/copaper-competitive-architecture-research-2026-05-10.md` | v2 的来源文档，调研结论在此落地 |

## 实现路线图

```
Phase A（当前）：信息架构重塑
├── 前端：研究总览页 + 旅程条 + Agent 控制台升级
├── 后端：新增 overview API + mock 数据 + 新路由
└── 文档：本文档集

Phase B：数据与研究设计闭环
├── dataset_service + cleaning_service
├── design_service
└── HITL gate 基础

Phase C：local Codex + StatsPAI 执行接入
├── execution_adapter
├── 替换 mock 执行
└── result object 标准化

Phase D：论文草稿与导出
├── draft_service
├── DOCX export 升级
└── replication pack

Phase E：多人多 Agent 治理
├── identity + permission 完整实现
├── cost ledger
└── approval history
```

## 关键决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 一阶导航 | 7 个研究阶段 | 映射用户研究旅程，CoPaper 验证 |
| 现有导航 | 保留为二级导航 | 不破坏现有功能，渐进迁移 |
| DAG 可视化 | Phase A 文本替代 | 降低 Phase A 复杂度 |
| 后端存储 | JSON 文件（Phase A-B） | 保持与现有系统一致，SQLite 后续引入 |
| Mock 数据 | 必须标记 evidence_level | 防止混淆，支持渐进替换 |
| Agent 架构 | Pipeline Roles + Dimension Agents | 融合 CoPaper 流水线 + 现有并行分析 |

# 契约

各开发切片冻结的后端/Agent 行为契约：命名对象、顺序约束、诚实性要求和验收条目。改相关行为时，同一改动里更新对应契约；契约文本仍是验收依据。

| 契约 | 管什么 | 主要代码 |
|---|---|---|
| [infer-design-contract.md](infer-design-contract.md) | 以题目为先推断研究设计：`session.design` 的提议与确认（DECIDE-6） | `backend/services/session_design.py`、`backend/routers/design.py` |
| [data-completion-contract.md](data-completion-contract.md) | 按题目补全数据、挂接数据集 | `backend/services/data_attach.py`、`backend/routers/attach.py` |
| [find-data-lit-contract.md](find-data-lit-contract.md) | 设计确认后找数据、找文献（DECIDE-7） | find-data / find-literature 节点与路由 |
| [real-fetch-contract.md](real-fetch-contract.md) | 真实取数：`source_kind`、诚实性、下载或链接策略（DECIDE-10 + DATA-RIGOR） | fetch 服务、`frontend/src/types/findDataHonesty.ts` |
| [bryce-tools-contract.md](bryce-tools-contract.md) | 接入的四个 Bryce 工具及其边界（DECIDE-8） | 估计、清洗、文献复用、离线评测 |
| [did-narrow-exception-contract.md](did-narrow-exception-contract.md) | DiD 窄例外：废弃目录里的 `allow_did` 令牌 | `agent/engine/did_spec.py` |

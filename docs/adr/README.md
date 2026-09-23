# 架构决策记录（ADR）

每条 ADR 记一个架构取舍：背景、决定、后果。只追加：推翻旧决定时写新 ADR，并在旧 ADR 顶部注明被哪条取代。编号 0005、0006 从未使用。

| ADR | 决定 | 状态 |
|---|---|---|
| [0001](0001-split-title-and-body-chapters-in-state.md) | state 中标题章与正文章分开存 | Accepted |
| [0002](0002-cleaning-pipeline-step-protocol.md) | 数据清洗管道统一 Step 协议 | Accepted |
| [0003](0003-agent-contract-facade-and-shared-shapes.md) | Agent 契约、Facade 边界与共享数据形状 | Accepted |
| [0004](0004-sakana-review-and-literature-nodes.md) | 自动评审节点与文献检索节点（Sakana 启发） | Draft |
| [0007](0007-hitl-review-integration.md) | 人工评审（HITL）接入 | Accepted |
| [0008](0008-multi-llm-routing.md) | 多 LLM 路由：评审与生成用不同模型 | Accepted |
| [0009](0009-citation-graph-and-references.md) | 文献引用图谱与参考文献自动生成 | Draft |
| [0010](0010-one-product-merge.md) | 只有一个网页产品，废弃多仓多入口 | Accepted |
| [0011](0011-apodex-literature-bypass.md) | Apodex 深搜只作可弃旁路，不作依赖 | — |
| [0012](0012-journey-presentation-layers.md) | 旅程呈现分用户动作层与引擎阶段层 | Accepted（决策点 4 另议） |
| [0013](0013-workbench-v2-truth-owner.md) | Workbench v2：研究状态唯一真相在后端 | Accepted |
| [0014](0014-workbench-v2-visual-phase.md) | Workbench v2 视觉：IA 重排、token 分域 | Accepted |
| [0015](0015-card-canonical-research-experience.md) | Card 规范研究体验：SpecificationRun、preview 边界、Claim Ledger | Accepted |

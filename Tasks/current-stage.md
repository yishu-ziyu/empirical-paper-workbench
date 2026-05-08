# 当前阶段

- 研究题目：待定
- 当前主线：Agent 集群式深度研究工作流设计与实现准备
- 下一步：
  - 按 `docs/agent-cluster-workflow-development-progress-2026-05-08.md` 增加 workflow schema 与 service
  - 在 `Product/state/workflows/` 落地 JSON 状态
  - 在 `Product/web/` 增加 Agent 集群列表、进度条与 hover 详情卡
  - 先用 mock 子任务跑通 10 维度并行研究闭环
  - 再接入真实数据源、文献源和 StatsPAI 方法设计
- 当前约束：
  - 原始数据不手改
  - 正文不直接从临时结果取数
  - 临时试验优先放 `Program/temp/`
  - mock 输出不得冒充真实研究证据
  - 第一版优先复用现有 FastAPI + 静态前端产品壳

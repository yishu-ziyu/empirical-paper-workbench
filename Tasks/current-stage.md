# 当前阶段

- 研究题目：待定
- 当前主线：Agent 集群式深度研究工作流 API 与前端完成动作已接通，第一执行 provider 选定为本地 Codex
- 下一步：
  - 为工作流增加 `events.jsonl` 事件流
  - 把 deterministic mock 子任务替换为显式 local Codex 执行步骤
  - 第一批 local Codex adapter 优先接入本地 source inventory、Zotero/PDF 文献池和 StatsPAI 方法设计
  - 启动本地产品服务并浏览器验证 Agent 集群 UI
- 当前约束：
  - 原始数据不手改
  - 正文不直接从临时结果取数
  - 临时试验优先放 `Program/temp/`
  - mock 输出不得冒充真实研究证据
  - 第一版优先复用现有 FastAPI + 静态前端产品壳

# Handoff: F4 - 前端集成测试

## 目标
为前端集成流程编写测试，覆盖 upload → sessionId → WebSocket → 章节生成的全链路。

## 背景
- 现有前端测试 20 个（组件级别），但缺少集成测试覆盖 App.tsx 的完整业务流程
- 需要 mock 后端 API 和 WebSocket 来测试集成场景

## 具体改动

### 1. 集成测试文件
创建 `frontend/src/__tests__/integration.test.tsx`，覆盖以下场景：

- **场景 A：上传文件创建 session**
  - mock `/upload` 端点返回 `{session_id: "test-123"}`
  - 渲染 App → 触发上传 → 验证 sessionId 传递到子组件

- **场景 B：WebSocket 连接和消息分发**
  - mock WebSocket
  - 渲染 App（sessionId 有效）→ 验证 WSClient 创建并连接
  - 发送 mock streaming_chunk → 验证 Editor 更新

- **场景 C：页面刷新后状态恢复**
  - mock localStorage 中有 sessionId
  - 渲染 App → 验证从 localStorage 恢复 sessionId
  - 验证 WebSocket 自动重连

### 2. Mock 工具
- 使用 `vi.mock()` mock `fetch` 或 `axios` 调用
- 使用 `vi.stubGlobal('WebSocket', MockWebSocket)`（参考 ws.test.ts 中的模式）

### 3. 运行测试
```bash
cd frontend && npm test
```

## 依赖
- 前置：F1（App.tsx 真实 sessionId）
- 前置：F2（localStorage 状态恢复）
- 前置：F3（WebSocket 全流程打通）

## 验收标准
- [ ] 场景 A 测试通过：upload → sessionId 传递
- [ ] 场景 B 测试通过：WebSocket 连接和消息分发
- [ ] 场景 C 测试通过：localStorage 恢复
- [ ] 所有现有测试仍然通过
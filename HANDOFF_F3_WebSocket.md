# Handoff: F3 - WebSocket 全流程打通

## 目标
将 ws.ts WebSocket 客户端集成到 App.tsx 中，实现后端到前端的实时通信。

## 背景
- ws.ts 已实现 WSClient 类，支持 onChunk / onStatus / onInterrupt / onError 回调
- 后端 ws.py 已实现 WebSocket 端点 `ws://localhost:8001/ws/{session_id}`
- 当前 App.tsx 中 AgentPanel 的 `connectionState` 硬编码为 `'disconnected'`
- App.tsx 尚未创建 WSClient 实例

## 具体改动

### 1. App.tsx
- 在 sessionId 变化时（从 F1 获取或 F2 恢复）创建 WSClient 实例
- 注册回调：onChunk → 更新 Editor 的 chunks 状态
- 注册回调：onStatus → 更新 AgentPanel 的 currentNode 和 connectionState
- 注册回调：onError → 显示错误提示
- 组件卸载时调用 `wsClient.close()`

### 2. ws.ts（无需修改，仅确认）
- 确认 WSClient 的 URL 格式：`ws://localhost:8001/ws/{sessionId}`
- 确认 WSClient 的消息类型与后端 ws.py 一致

### 3. 状态管理
- sessionId 从 null 变为有效值 → 创建 WSClient 并 connect()
- sessionId 变为 null → 关闭 WSClient
- 页面刷新（F2 localStorage 恢复）→ 恢复 sessionId 后重新 connect()

### 4. 测试
- 运行 `cd frontend && npm test` 确认现有测试全部通过
- 手动测试：启动后端和前端，上传文件，确认 WebSocket 连接建立

## 依赖
- 前置：F1（App.tsx 真实 sessionId）—— WebSocket 需要真实 sessionId 才能连接
- 前置：F2（localStorage 状态恢复）—— 页面刷新后需恢复 sessionId 才能重连 WebSocket
- 后置：F4（前端集成测试）—— 依赖 WebSocket 全流程打通后才可测试

## 验收标准
- [ ] App.tsx 在 sessionId 有效时创建 WSClient 并连接
- [ ] WebSocket 消息（streaming_chunk, status, error）正确分发到对应组件
- [ ] 组件卸载时关闭 WebSocket 连接
- [ ] 页面刷新后自动重连 WebSocket
- [ ] 现有测试全部通过
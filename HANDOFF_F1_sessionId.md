# Handoff: F1 - App.tsx 真实 sessionId

## 目标
替换 App.tsx 中硬编码的 `'demo-session'` 为 upload 端点返回的真实 sessionId。

## 背景
- 当前 App.tsx line 10: `const [sessionId] = useState('demo-session')`
- 后端 `/upload` 端点 POST multipart file 后返回 `{"session_id": "..."}`
- 前端已有 upload 组件逻辑（在 EdaSidebar 或其他组件中），但 App.tsx 未接收真实 sessionId

## 具体改动

### 1. App.tsx
- 将 `sessionId` 改为可变状态：`const [sessionId, setSessionId] = useState<string | null>(null)`
- 监听 upload 完成事件，从响应中提取 `session_id` 并调用 `setSessionId(sid)`
- 所有子组件（EdaSidebar, AgentPanel 等）的 `sessionId` prop 从真实值获取

### 2. 子组件适配
- EdaSidebar 等组件可能需要接收 `onSessionCreated` 回调
- 确保 upload 完成后 sessionId 能传递到所有需要它的子组件

### 3. 测试
- 运行 `cd frontend && npm test` 确认现有测试通过
- 更新 App.test.tsx 以覆盖新的 sessionId 逻辑

## 依赖
- 前置：无（独立任务）
- 后置：F2（localStorage 恢复）依赖本任务
- 后置：F3（WebSocket 全流程）依赖本任务

## 验收标准
- [ ] App.tsx 不再有硬编码 `'demo-session'`
- [ ] 上传文件后，sessionId 从 response 获取并传递到所有子组件
- [ ] 现有测试全部通过
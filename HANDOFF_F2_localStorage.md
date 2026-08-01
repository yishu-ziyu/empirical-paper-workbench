# Handoff: F2 - localStorage 状态恢复

## 目标
在 App.tsx 中添加 localStorage 读写逻辑，使页面刷新后能恢复 sessionId 和连接状态。

## 背景
- 当前 App.tsx 使用 `useState` 管理 sessionId，刷新后丢失
- 后端状态已通过 PostgresSaver 持久化（已完成）
- 前端只需恢复 sessionId 即可从后端重新加载状态

## 具体改动

### 1. App.tsx
- sessionId 变化时写入 localStorage: `localStorage.setItem('econpaper_session_id', sid)`
- 页面加载时从 localStorage 读取: `const saved = localStorage.getItem('econpaper_session_id')`
- 如果 localStorage 中有值，自动使用该 sessionId 连接后端获取状态
- 添加 `connectionState` 状态管理，从 localStorage 恢复时初始化为 'connecting' 或 'reconnecting'

### 2. 状态恢复流程
- 页面加载 → 检查 localStorage 中是否有 sessionId
- 有 → 调用后端恢复会话（如 `GET /sessions/{id}/state` 或类似端点）
- 无 → 显示空态（等待用户上传文件）
- 恢复成功后更新 `connectionState` 为 'connected'

### 3. 测试
- 运行 `cd frontend && npm test` 确认现有测试通过

## 依赖
- 前置：F1（App.tsx 真实 sessionId）—— 因为需要先替换硬编码，才能在 localStorage 中存真实值
- 后置：F3（WebSocket 全流程）—— WebSocket 连接需要从 localStorage 恢复的 sessionId

## 验收标准
- [ ] 上传文件后 sessionId 保存到 localStorage
- [ ] 页面刷新后自动从 localStorage 恢复 sessionId
- [ ] 恢复后自动连接后端获取状态
- [ ] 现有测试全部通过
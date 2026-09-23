# WebSocket 协议

> 上级：[econpaper API 文档](../README.md)


## 连接

```
ws://localhost:8000/sessions/{session_id}/stream
```

## 消息类型

| type | 方向 | 说明 |
|------|------|------|
| `status` | 服务端 → 客户端 | 节点状态更新（running / done） |
| `streaming_chunk` | 服务端 → 客户端 | 章节内容流式推送 |
| `interrupt` | 服务端 → 客户端 | 推送完整章节内容，触发前端 HITL 暂停 |
| `error` | 服务端 → 客户端 | 错误信息 |

## 消息时序

```
客户端 → [wss 连接]
服务端 ← {"type": "status", "node": "upload_data", "status": "running"}
服务端 ← {"type": "status", "node": "clean_data", "status": "running"}
服务端 ← {"type": "status", "node": "generate_title", "status": "running"}
服务端 ← {"type": "streaming_chunk", "chapter_id": "title", "chunk": "## 引"}
服务端 ← {"type": "streaming_chunk", "chapter_id": "title", "chunk": "言\n\n..."}
服务端 ← {"type": "status", "node": "generate_title", "status": "done"}
服务端 ← {"type": "interrupt", "chapter_id": "title", "content": "..."}
服务端 → [关闭连接]
```

## 客户端示例

```javascript
const ws = new WebSocket(`ws://localhost:8000/sessions/${sessionId}/stream`);
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'streaming_chunk') {
    // 追加到编辑器
  } else if (msg.type === 'status') {
    // 更新进度条
  } else if (msg.type === 'interrupt') {
    // 显示 HITL 暂停界面
  } else if (msg.type === 'error') {
    // 显示错误
  }
};
```

---

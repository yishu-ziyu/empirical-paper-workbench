# 传输层

> 上级：[创作台方案](README.md)

## 两条通道

| 方向 | 通道 | 用途 |
|---|---|---|
| 前端 → 后端 | HTTP POST，带 `Idempotency-Key` | 所有命令：发消息、回答询问、撤销、处理批注、手动改稿 |
| 后端 → 前端 | 一条会话级 SSE：`GET /sessions/{id}/events` | 助手的流式回复、工具进度、稿子改动、批注变化、光标意图 |

另外保留 `GET /sessions/{id}/snapshot`：首次打开和断线太久时取完整快照，之后只吃事件。

### 为什么是 SSE 而不是 WebSocket

- 现有的 `/runs/{id}/events` 已经是 SSE，带 `seq` 和 `Last-Event-ID` 断点续传（`backend/routers/run_execution.py`），可以直接扩展成会话级。
- 命令本来就需要幂等和鉴权，走普通 HTTP 更简单，也更好测。
- 现有的 WebSocket `/sessions/{id}/stream` 并不是真的流：它在图跑完之后把最终状态一次性分块推出去。创作台不再使用它。

## 事件目录

每条事件：`{ seq, type, at, session_id, turn_id?, payload }`。`seq` 在会话内单调递增，由后端在同一事务里分配。

| type | payload 要点 | 前端怎么用 |
|---|---|---|
| `turn.started` / `turn.completed` | turn_id | 输入框进入 / 退出忙碌 |
| `message.delta` | turn_id, text | 逐字追加到当前回复 |
| `tool.started` / `tool.finished` | tool_id, label, run_id?, summary | 工具卡转圈 / 显示结果 |
| `run.*` | 转发自现有 RunEvent（`run.accepted`、`run.progress`、`run.succeeded`、`run.failed`） | 工具卡进度 |
| `ask.opened` / `ask.answered` | ask_id, question, options | 询问卡；回答后留痕 |
| `cursor.intent` | target（语义 id）, action: move\|click\|select\|type, label | 驱动光标；只做表现，不改状态 |
| `change.applied` | change_id, ops[{block_id, version, after}] | 更新块内容，对应的光标“打字”播放完毕再落最终文字 |
| `change.reverted` | change_id, inverse_change_id | 撤销 |
| `note.updated` | note_id, status | 页边批注变色 |
| `evidence.revised` | evidence_id, revision | 重新计算哪些 Ref 过时 |

`cursor.intent` 总是出现在对应的 `change.applied` 之前。前端先播放光标，再应用改动；错过光标事件（例如刚重连）时直接应用改动，不补播。

## 断点续传与一致性

- 前端记住最后处理的 `seq`；重连时带 `Last-Event-ID`，后端从下一条开始补发。
- 缺口太大或事件已过保留期时，后端返回 `409`，前端改取快照。
- 每个 `change.applied` 都带块的新 `version`；前端发现版本跳号，就重取这个块。
- 同一会话的 SSE 连接数有上限（沿用 `_MAX_SSE_CONNECTIONS_PER_RUN` 的做法）。

## 命令

| 命令 | 路径（草案） | 说明 |
|---|---|---|
| 发消息 | `POST /sessions/{id}/turns` | body: text, quote?（引用的块）；返回 turn_id |
| 回答询问 | `POST /sessions/{id}/asks/{ask_id}` | body: option |
| 撤销改动 | `POST /sessions/{id}/changes/{change_id}/revert` | 生成反向 ChangeSet |
| 用户手改 | `POST /sessions/{id}/changes` | body: ops（带 base_version） |
| 处理批注 | `POST /sessions/{id}/notes/{note_id}/resolve` | 通常由助手发起，用户也可以手动标记 |

所有命令的响应只表示“已受理”，状态以随后的事件为准（沿用 `frontend/src/lib/confirmationCommands.ts` 的读回原则）。

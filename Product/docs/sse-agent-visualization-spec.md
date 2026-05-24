# SSE 实时推送 + Agent 工作可视化 技术执行文档

> 目标：让 Empirical OS 的 Journey 流水线具备 Copaper.ai 级别的实时 Agent 执行可视化体验。
> 核心约束：**所有数据必须来自真实运行，禁止模拟/假数据**。

---

## 1. 架构概述

```
┌─────────────────┐     SSE (text/event-stream)      ┌─────────────────┐
│  Backend        │ ◄──────────────────────────────── │  Frontend       │
│  orchestrator   │     event: stage.start             │  EventSource    │
│  _run_stage()   │ ──► event: stage.output            │  renderJourney()│
│  (sync code)    │ ──► event: stage.complete          │  Agent输出面板  │
│                 │ ──► event: checkpoint.pending      │                 │
└─────────────────┘                                    └─────────────────┘
         │                                                      │
         │  threading.Queue                                     │  DOM更新
         │  (全局 RUN_QUEUES)                                   │  (真实数据)
         ▼                                                      ▼
  FastAPI SSE endpoint                                  阶段轨道实时高亮
  /api/v1/projects/{pid}/runs/{rid}/stream              Agent输出打字机效果
```

**关键设计决策**：
- orchestrator.py 是同步顺序执行代码，不改为异步
- 使用 `threading.Queue` 作为同步/异步桥梁：orchestrator 往 Queue 放事件，FastAPI SSE 端点从 Queue 消费
- 每个 `run_id` 有独立的 Queue，存储在全局字典 `RUN_EVENT_QUEUES: dict[str, queue.Queue]` 中
- Queue 中的事件是极简 dict，序列化为 JSON 后通过 SSE 推送

---

## 2. 事件类型定义 (SSE Event Schema)

所有事件统一格式：

```json
{
  "event_id": "evt_001",
  "run_id": "run_20260522T120000Z_abc123",
  "timestamp": "2026-05-22T12:00:01Z",
  "type": "stage.start",
  "stage": "04_modeling",
  "agent_name": "ModelingAgent",
  "payload": { ... }
}
```

| type | 触发时机 | payload |
|------|---------|---------|
| `run.started` | run_workbench 开始执行 | `{ mode, user_goal }` |
| `stage.start` | _run_stage 即将执行 stage_func | `{ stage, agent_name, action }` |
| `stage.output` | 阶段执行过程中产生的实时输出 | `{ stage, chunk: "...", source: "llm" \| "statspai" \| "log" }` |
| `stage.complete` | _run_stage 的 stage_func 执行完毕 | `{ stage, status: "succeeded" \| "failed", wall_seconds }` |
| `checkpoint.pending` | HITL checkpoint 创建后 | `{ checkpoint_id, stage, title, description }` |
| `checkpoint.resolved` | 用户解决 checkpoint 后 | `{ checkpoint_id, status, user_feedback }` |
| `run.completed` | run_workbench 全部阶段执行完毕 | `{ status, artifacts_count }` |
| `run.failed` | run_workbench 异常终止 | `{ stage, error: "..." }` |

---

## 3. 后端变更

### 3.1 新增文件：`Product/backend/run_event_bus.py`

职责：全局事件总线，管理每个 run_id 的 Queue，提供 put / consume 接口。

```python
"""Run event bus — bridges sync orchestrator with async SSE."""
from __future__ import annotations

import json
import queue
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

# Global registry: run_id -> Queue
_RUN_QUEUES: dict[str, queue.Queue] = {}
_LOCK = threading.Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_queue(run_id: str) -> queue.Queue:
    """Get or create a Queue for the given run_id."""
    with _LOCK:
        if run_id not in _RUN_QUEUES:
            _RUN_QUEUES[run_id] = queue.Queue(maxsize=1000)
        return _RUN_QUEUES[run_id]


def drop_queue(run_id: str) -> None:
    """Remove a Queue after the run is finished."""
    with _LOCK:
        _RUN_QUEUES.pop(run_id, None)


def emit_event(run_id: str, event_type: str, stage: str = "", agent_name: str = "", payload: dict | None = None) -> None:
    """Emit an event to the run's queue. Called from sync orchestrator code."""
    q = ensure_queue(run_id)
    event = {
        "event_id": f"evt_{uuid.uuid4().hex[:8]}",
        "run_id": run_id,
        "timestamp": _utc_now(),
        "type": event_type,
        "stage": stage,
        "agent_name": agent_name,
        "payload": payload or {},
    }
    try:
        q.put_nowait(event)
    except queue.Full:
        # Drop oldest event to make room
        try:
            q.get_nowait()
            q.put_nowait(event)
        except queue.Empty:
            pass


def get_queue(run_id: str) -> queue.Queue | None:
    """Get the queue for a run_id, or None if not found."""
    with _LOCK:
        return _RUN_QUEUES.get(run_id)


def list_active_runs() -> list[str]:
    """Return all run_ids that currently have active queues."""
    with _LOCK:
        return list(_RUN_QUEUES.keys())
```

### 3.2 修改文件：`Product/backend/orchestrator.py`

**修改内容**：

1. **顶部导入**：
```python
from .run_event_bus import emit_event, drop_queue
```

2. **`_run_stage` 函数中插入事件发射**（在原有逻辑的 6 个关键节点）：

```python
def _run_stage(...):
    # ... 原有 identity/permission/capability/cost 逻辑不变 ...

    # ① 阶段开始
    emit_event(run_id, "stage.start", stage=stage, agent_name=agent_display_name,
               payload={"action": action, "capability_id": effective_cap_id})

    # 4. Start cost event
    event_id = cost_service.start_cost_event(...)

    # Execute stage with wall-clock timing
    start_ts = time.perf_counter()
    status = "succeeded"
    try:
        result = stage_func()

        # ② 阶段执行过程中（如果 stage_func 有产出，通过回调注入）
        # NOTE: 当前 stage_func 是闭包，无法直接拦截输出。
        # 对于 04_modeling，在 LLM 调用和 StatsPAI 调用后手动 emit

    except Exception as exc:
        status = "failed"
        # ③ 阶段失败
        emit_event(run_id, "stage.output", stage=stage, agent_name=agent_display_name,
                   payload={"source": "log", "chunk": f"Error: {exc}"})
        raise
    finally:
        wall_seconds = time.perf_counter() - start_ts
        cost_service.finish_cost_event(...)
        # ... git logging ...

    # ④ 阶段完成
    emit_event(run_id, "stage.complete", stage=stage, agent_name=agent_display_name,
               payload={"status": status, "wall_seconds": round(wall_seconds, 3)})

    # ── HITL checkpoint creation ───────────────────────────────────────────
    hitl_config = HITL_STAGES.get(stage)
    if hitl_config:
        checkpoint_id = f"checkpoint_{uuid.uuid4().hex[:12]}"
        # ... 原有 checkpoint 创建逻辑 ...
        save_checkpoint(repo_root, checkpoint.__dict__)

        # ⑤ checkpoint 创建事件
        emit_event(run_id, "checkpoint.pending", stage=stage, agent_name=agent_display_name,
                   payload={
                       "checkpoint_id": checkpoint_id,
                       "title": hitl_config["title"],
                       "description": hitl_config["description"],
                   })

    return result
```

3. **`run_workbench` 函数中插入事件发射**：

```python
def run_workbench(...):
    # ... 原有初始化逻辑 ...

    # ① Run 开始
    emit_event(run_id, "run.started", payload={"mode": mode, "user_goal": user_goal})

    try:
        # ... 8 个阶段的 _run_stage 调用 ...

        # ... manifest 写入 ...

        # ⑥ Run 完成
        emit_event(run_id, "run.completed", payload={"status": "completed", "artifacts_count": len(artifacts)})

        return manifest.to_dict()
    except Exception as exc:
        # ⑦ Run 失败
        emit_event(run_id, "run.failed", payload={"error": str(exc)})
        raise
    finally:
        # 延迟清理 queue，让 SSE 消费者有时间读取最后的事件
        # 使用 threading.Timer(60.0, drop_queue, args=(run_id,)) 延迟60秒清理
        pass
```

4. **`_call_llm_for_modeling` 调用后手动 emit**：

在 `_stage_04_modeling` 中，LLM 调用成功后：
```python
emit_event(run_id, "stage.output", stage="04_modeling", agent_name="ModelingAgent",
           payload={"source": "llm", "chunk": llm_report[:500] + "..." if len(llm_report) > 500 else llm_report})
```

StatsPAI 调用成功后：
```python
emit_event(run_id, "stage.output", stage="04_modeling", agent_name="ModelingAgent",
           payload={"source": "statspai", "chunk": f"StatsPAI backend: {backend_result.get('status', 'unknown')}"})
```

### 3.3 修改文件：`Product/app.py`

**新增导入**：
```python
from Product.backend.run_event_bus import get_queue, list_active_runs, ensure_queue
import asyncio
from fastapi.responses import StreamingResponse
```

**新增 SSE 路由**：

```python
@app.get("/api/v1/projects/{project_id}/runs/{run_id}/stream")
async def api_v1_run_event_stream(project_id: str, run_id: str):
    """Server-Sent Events endpoint for real-time run updates."""
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")

    q = ensure_queue(run_id)

    async def event_generator():
        """Async generator that bridges sync threading.Queue to async SSE."""
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'run_id': run_id, 'status': 'listening'}, ensure_ascii=False)}\n\n"

        while True:
            try:
                # Non-blocking get with timeout; use asyncio.to_thread to avoid blocking event loop
                event = await asyncio.wait_for(
                    asyncio.to_thread(q.get, timeout=1.0),
                    timeout=5.0
                )
                data = json.dumps(event, ensure_ascii=False)
                yield f"event: {event['type']}\ndata: {data}\n\n"

                # Stop if run is completed or failed
                if event["type"] in ("run.completed", "run.failed"):
                    break

            except asyncio.TimeoutError:
                # Send keep-alive comment to prevent connection timeout
                yield ":keep-alive\n\n"
            except Exception:
                break

        yield f"event: closed\ndata: {json.dumps({'run_id': run_id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
```

**新增 Active Runs 路由**（供前端知道当前有哪些 run 在活跃）：
```python
@app.get("/api/v1/projects/{project_id}/runs/active")
def api_v1_project_active_runs(project_id: str) -> dict:
    """Return active run IDs for this project."""
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")

    active_runs = list_active_runs()
    # Filter to runs belonging to this project (by checking run manifest paths)
    # Simplified: return all active, frontend filters by run_id
    return {"project_id": project_id, "active_runs": active_runs}
```

---

## 4. 前端变更

### 4.1 修改文件：`Product/web/assets/app.js`

**新增状态**：
```javascript
// SSE state
sseConnection: {
  eventSource: null,
  connected: false,
  runId: null,
  reconnectAttempts: 0,
},

// Agent output panel state
agentOutput: {
  visible: false,
  currentStage: null,
  currentAgent: null,
  lines: [],       // { timestamp, source, text }
  isTyping: false,
},
```

**新增 v2api 命名空间**：
```javascript
runs: {
  async stream(projectId, runId, onEvent) {
    const url = `/api/v1/projects/${projectId}/runs/${runId}/stream`;
    const es = new EventSource(url);

    es.addEventListener("connected", (e) => {
      onEvent({ type: "connected", data: JSON.parse(e.data) });
    });

    es.addEventListener("run.started", (e) => {
      onEvent({ type: "run.started", data: JSON.parse(e.data) });
    });

    es.addEventListener("stage.start", (e) => {
      onEvent({ type: "stage.start", data: JSON.parse(e.data) });
    });

    es.addEventListener("stage.output", (e) => {
      onEvent({ type: "stage.output", data: JSON.parse(e.data) });
    });

    es.addEventListener("stage.complete", (e) => {
      onEvent({ type: "stage.complete", data: JSON.parse(e.data) });
    });

    es.addEventListener("checkpoint.pending", (e) => {
      onEvent({ type: "checkpoint.pending", data: JSON.parse(e.data) });
    });

    es.addEventListener("run.completed", (e) => {
      onEvent({ type: "run.completed", data: JSON.parse(e.data) });
      es.close();
    });

    es.addEventListener("run.failed", (e) => {
      onEvent({ type: "run.failed", data: JSON.parse(e.data) });
      es.close();
    });

    es.addEventListener("closed", (e) => {
      onEvent({ type: "closed", data: JSON.parse(e.data) });
      es.close();
    });

    es.onerror = (err) => {
      onEvent({ type: "error", error: err });
      // Auto-reconnect with exponential backoff (max 5 attempts)
      es.close();
    };

    return es;
  },
},
```

**新增 SSE 管理函数**：
```javascript
function connectRunStream(runId) {
  disconnectRunStream();
  if (!state.selectedProjectId || !runId) return;

  state.sseConnection.runId = runId;
  state.sseConnection.connected = false;
  state.agentOutput.visible = true;
  state.agentOutput.lines = [];
  state.agentOutput.currentStage = null;
  state.agentOutput.currentAgent = null;

  const es = v2api.runs.stream(state.selectedProjectId, runId, (event) => {
    handleRunEvent(event);
  });

  state.sseConnection.eventSource = es;
}

function disconnectRunStream() {
  if (state.sseConnection.eventSource) {
    state.sseConnection.eventSource.close();
    state.sseConnection.eventSource = null;
  }
  state.sseConnection.connected = false;
  state.sseConnection.runId = null;
}

function handleRunEvent(event) {
  switch (event.type) {
    case "connected":
      state.sseConnection.connected = true;
      break;
    case "stage.start":
      state.agentOutput.currentStage = event.data.stage;
      state.agentOutput.currentAgent = event.data.agent_name;
      addAgentOutputLine(event.data.timestamp, "system",
        `▶ ${event.data.agent_name} 开始执行 ${stageNameCN(event.data.stage)}`);
      updateJourneyStageStatus(event.data.stage, "running");
      break;
    case "stage.output":
      addAgentOutputLine(event.data.timestamp, event.data.payload?.source || "log",
        event.data.payload?.chunk || "");
      break;
    case "stage.complete":
      const statusLabel = event.data.payload?.status === "succeeded" ? "完成" : "失败";
      addAgentOutputLine(event.data.timestamp, "system",
        `✓ ${event.data.agent_name} ${statusLabel} (${event.data.payload?.wall_seconds || 0}s)`);
      updateJourneyStageStatus(event.data.stage, event.data.payload?.status === "succeeded" ? "completed" : "failed");
      break;
    case "checkpoint.pending":
      addAgentOutputLine(event.data.timestamp, "system",
        `⏸ 检查点: ${event.data.payload?.title}`);
      updateJourneyStageStatus(event.data.stage, "pending_confirmation");
      // Trigger checkpoint modal via existing polling mechanism
      void pollCheckpoint();
      break;
    case "run.completed":
      addAgentOutputLine(event.data.timestamp, "system", "🏁 运行完成");
      disconnectRunStream();
      break;
    case "run.failed":
      addAgentOutputLine(event.data.timestamp, "system", `❌ 运行失败: ${event.data.payload?.error}`);
      disconnectRunStream();
      break;
    case "error":
      state.sseConnection.connected = false;
      break;
  }
  renderAgentOutputPanel();
}

function addAgentOutputLine(timestamp, source, text) {
  state.agentOutput.lines.push({
    timestamp: timestamp ? new Date(timestamp).toLocaleTimeString("zh-CN") : "",
    source,
    text,
  });
  // Keep max 200 lines
  if (state.agentOutput.lines.length > 200) {
    state.agentOutput.lines = state.agentOutput.lines.slice(-200);
  }
}

function stageNameCN(stageId) {
  const map = {
    "00_intake": "选题解析",
    "01_sources": "数据源发现",
    "02_literature": "文献综述",
    "03_strategy": "识别策略",
    "04_modeling": "基线估计",
    "05_results": "结果整理",
    "06_writing": "写作",
    "07_review": "审阅",
    "08_final": "导出",
  };
  return map[stageId] || stageId;
}

function updateJourneyStageStatus(stageId, status) {
  // Update state.overviewData.stage_summaries to reflect new status
  if (!state.overviewData) return;
  const summaries = state.overviewData.stage_summaries || [];
  const existing = summaries.find(s => s.stage_id === stageId);
  if (existing) {
    existing.status = status;
  } else {
    summaries.push({ stage_id: stageId, status });
  }
  renderJourney();
  renderJourneyBar();
}
```

**修改 `renderJourney` 中的 quick actions**：

在 "journey-actions" 区域，当有一个 active run 正在 streaming 时，显示 "查看实时输出" 按钮：
```javascript
const actions = document.getElementById("journey-actions");
if (actions) {
  const isStreaming = state.sseConnection.connected && state.sseConnection.runId;
  actions.innerHTML = `
    ${isStreaming ? `<button class="primary-button" data-journey-action="view-output">查看 Agent 实时输出</button>` : ""}
    ${primaryAction ? `<button class="primary-button" data-journey-action="primary">${escapeHtml(productTermLabel(primaryAction.action || "继续"))}</button>` : ""}
    <button class="ghost-button" data-journey-action="refresh">刷新状态</button>
    ${currentStageData?.status === "pending" ? `<button class="ghost-button" data-journey-action="checkpoint" style="color: #e67e22; border-color: #e67e22;">确认检查点</button>` : ""}
  `;
}
```

**新增 Agent 输出面板渲染函数**：
```javascript
function renderAgentOutputPanel() {
  const panel = document.getElementById("agent-output-panel");
  if (!panel) return;

  if (!state.agentOutput.visible) {
    panel.style.display = "none";
    return;
  }

  panel.style.display = "block";
  const linesHtml = state.agentOutput.lines.map(line => {
    const sourceClass = line.source === "llm" ? "is-llm"
      : line.source === "statspai" ? "is-statspai"
      : line.source === "system" ? "is-system"
      : "is-log";
    return `<div class="agent-output-line ${sourceClass}">
      <span class="agent-output-time">${escapeHtml(line.timestamp)}</span>
      <span class="agent-output-source">${escapeHtml(line.source)}</span>
      <span class="agent-output-text">${escapeHtml(line.text)}</span>
    </div>`;
  }).join("");

  panel.innerHTML = `
    <div class="agent-output-header">
      <strong>Agent 实时输出</strong>
      <span class="agent-output-status ${state.sseConnection.connected ? "is-connected" : "is-disconnected"}">
        ${state.sseConnection.connected ? "● 实时连接中" : "○ 已断开"}
      </span>
      <button class="ghost-button" data-close-agent-output>关闭</button>
    </div>
    <div class="agent-output-body">
      ${linesHtml}
    </div>
  `;

  // Auto-scroll to bottom
  const body = panel.querySelector(".agent-output-body");
  if (body) body.scrollTop = body.scrollHeight;
}
```

**事件委托中添加处理**：
```javascript
// In the existing event delegation switch statement, add:
case "view-output":
  state.agentOutput.visible = true;
  renderAgentOutputPanel();
  break;

// Add a global listener for close button:
document.addEventListener("click", (e) => {
  if (e.target.matches("[data-close-agent-output]")) {
    state.agentOutput.visible = false;
    renderAgentOutputPanel();
  }
});
```

**在 workbench run 启动后连接 SSE**：

找到触发 workbench run 的代码（搜索 `execute_workbench_run` 或 workbench run 创建逻辑），在 run 启动成功后连接 stream：
```javascript
// After workbench run is created successfully:
const runId = result.run_id;
if (runId) {
  connectRunStream(runId);
}
```

### 4.2 修改文件：`Product/web/assets/styles.css`

**新增 Agent 输出面板样式**（约 120 行）：

```css
/* Agent Output Panel */
.agent-output-panel {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 560px;
  max-width: calc(100vw - 48px);
  max-height: 420px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
  display: none;
  flex-direction: column;
  overflow: hidden;
  z-index: 200;
  font-family: "SF Mono", "Fira Code", "Cascadia Code", monospace;
  font-size: 13px;
}

.agent-output-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #1e293b;
  border-bottom: 1px solid #334155;
  color: #e2e8f0;
}

.agent-output-header strong {
  font-size: 14px;
  font-weight: 600;
}

.agent-output-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
}

.agent-output-status.is-connected {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.15);
}

.agent-output-status.is-disconnected {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.15);
}

.agent-output-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  line-height: 1.6;
}

.agent-output-line {
  display: flex;
  gap: 8px;
  padding: 2px 0;
  color: #cbd5e1;
}

.agent-output-time {
  color: #64748b;
  font-size: 11px;
  white-space: nowrap;
  flex-shrink: 0;
  width: 64px;
}

.agent-output-source {
  color: #94a3b8;
  font-size: 11px;
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
  width: 56px;
  text-align: right;
}

.agent-output-text {
  flex: 1;
  word-break: break-word;
}

.agent-output-line.is-llm .agent-output-source { color: #a78bfa; }
.agent-output-line.is-statspai .agent-output-source { color: #38bdf8; }
.agent-output-line.is-system .agent-output-source { color: #fbbf24; }
.agent-output-line.is-log .agent-output-source { color: #94a3b8; }

/* Journey stage running animation */
.journey-node.is-running .journey-node-dot {
  animation: journey-node-pulse 1.5s ease-in-out infinite;
  background: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
}

@keyframes journey-node-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

/* Journey stage status colors update */
.journey-node.is-running .journey-node-dot { background: #3b82f6; }
.journey-node.is-failed .journey-node-dot { background: #ef4444; }
.journey-node.is-pending .journey-node-dot { background: #f59e0b; }
```

### 4.3 修改文件：`Product/web/index.html`

在 `</body>` 结束前添加 Agent 输出面板 DOM：
```html
<!-- Agent Real-time Output Panel -->
<div id="agent-output-panel" class="agent-output-panel" style="display:none;">
  <div class="agent-output-header">
    <strong>Agent 实时输出</strong>
    <span class="agent-output-status is-disconnected">○ 未连接</span>
    <button class="ghost-button" data-close-agent-output>关闭</button>
  </div>
  <div class="agent-output-body">
    <p class="muted">等待运行开始...</p>
  </div>
</div>
```

同时更新版本号缓存戳：
```html
<script src="assets/app.js?v=20260522-sse-agent-viz"></script>
<link rel="stylesheet" href="assets/styles.css?v=20260522-sse-agent-viz" />
```

---

## 5. 文件修改清单

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `Product/backend/run_event_bus.py` | 新增 | 全局事件总线，threading.Queue 管理 |
| 2 | `Product/backend/orchestrator.py` | 修改 | 在 8 个关键节点插入 emit_event() |
| 3 | `Product/app.py` | 修改 | 新增 SSE StreamingResponse 路由 + active runs 路由 |
| 4 | `Product/web/assets/app.js` | 修改 | EventSource 客户端 + Agent 输出面板 + Journey 实时状态更新 |
| 5 | `Product/web/assets/styles.css` | 修改 | Agent 输出面板样式 + Journey running 动画 |
| 6 | `Product/web/index.html` | 修改 | Agent 输出面板 DOM + 缓存版本号更新 |

---

## 6. 执行顺序

1. **创建 `run_event_bus.py`** — 事件总线基础设施
2. **修改 `orchestrator.py`** — 在 _run_stage 和 run_workbench 中插入 emit_event 调用
3. **修改 `app.py`** — 新增 SSE 端点
4. **修改 `index.html`** — 添加 Agent 输出面板 DOM
5. **修改 `styles.css`** — 添加面板样式和动画
6. **修改 `app.js`** — EventSource 连接 + 事件处理 + 面板渲染
7. **启动后端验证** — 确保 SSE 端点返回 text/event-stream
8. **浏览器验收** — 启动一次 workbench run，观察 Journey 阶段实时高亮 + Agent 输出面板打字机效果

---

## 7. 验收标准

### 7.1 功能验收

- [ ] 启动 workbench run 后，浏览器 Network 面板能看到 `/stream` 请求，Type 为 `eventsource`
- [ ] Journey 轨道上的当前执行阶段节点显示蓝色脉冲动画（is-running）
- [ ] 阶段完成后，节点变为绿色（is-completed）
- [ ] Agent 输出面板自动弹出，显示各阶段的开始/输出/完成时间线
- [ ] LLM 调用输出在面板中标记为紫色（llm）
- [ ] StatsPAI 调用输出在面板中标记为蓝色（statspai）
- [ ] 检查点创建时，面板显示黄色暂停标记，同时弹出现有 checkpoint modal
- [ ] Run 全部完成后，面板显示 "运行完成"，SSE 连接自动关闭

### 7.2 非功能验收

- [ ] SSE 连接断开后能自动重连（指数退避，最多 5 次）
- [ ] 同时只能有一个 SSE 连接活跃（切换项目时断开旧连接）
- [ ] Agent 输出面板最多保留 200 行，超出后自动丢弃最旧的
- [ ] 整个实现不使用任何模拟/假数据

### 7.3 红线

- **禁止**在 EventSource 回调中伪造/模拟事件数据
- **禁止**在 Agent 输出面板中显示未经后端 emit 的文本
- **禁止**修改 _run_stage 的同步执行模型（不改 async）
- **禁止**引入新的 npm/pip 依赖（使用浏览器原生 EventSource）

---

## 8. 备注

- 当前 checkpoint 系统使用轮询（每5秒），SSE 推送 `checkpoint.pending` 事件后，前端仍保留轮询作为 fallback
- 如果 `asyncio.to_thread` 在 Python 3.8 中不可用，改用 `loop.run_in_executor(None, q.get, timeout)`
- `threading.Queue` 的 maxsize=1000 是防内存泄漏的安全阀，正常场景不会触及

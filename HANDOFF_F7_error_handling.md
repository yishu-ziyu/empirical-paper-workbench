# Handoff: F7 - 异常处理与降级 UX

## 目标
为 econpaper 前后端实现全局异常处理机制和降级 UX，确保任何环节出错时用户能清晰感知并采取行动。

## 背景
- 当前后端 facade.py 有 try/except 模式，但缺少全局异常处理中间件
- 前端 App.tsx 已有 uploadError 状态，但未覆盖全局
- 无 ErrorBoundary 组件（ErrorBoundary.tsx 不存在）
- 无统一的降级提示规范
- cleaning 模块已有降级日志（`stats_pai_used: false`），但前端无法展示

## 具体改动

### 1. 后端：全局异常处理中间件

在 `backend/main.py` 中添加 `@app.exception_handler`：
- `HTTPException` → 返回结构化 JSON `{error, detail, code}`
- `ValidationError` → 返回 422 含字段级错误
- `Exception` → 返回 500 含请求 ID（便于调试）
- 所有异常响应包含 `degraded: bool` 字段，标识是否发生了降级

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    request_id = str(uuid.uuid4())
    logger.error(f"Request {request_id} failed: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": request_id,
            "degraded": True,
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )
```

### 2. 后端：降级报告端点

添加 `GET /sessions/{id}/degradation` 端点，返回该 session 的降级记录：
```json
{
  "degradations": [
    {"node": "clean_data.outliers", "reason": "StatsPAI winsor() failed", "fallback": "pandas", "timestamp": "..."},
    {"node": "export_docx", "reason": "LaTeX not installed", "fallback": "pandoc", "timestamp": "..."}
  ]
}
```

在 facade.py 添加 `record_degradation(session_id, node, reason, fallback)` 方法，各节点在降级时调用。

### 3. 前端：ErrorBoundary 组件

创建 `frontend/src/components/ErrorBoundary.tsx`：
- 捕获子组件渲染错误
- 显示友好错误提示 + 重试按钮
- 记录错误到控制台
- 包裹 App.tsx 中所有主要区域（三栏各自独立 ErrorBoundary）

```tsx
interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}
```

### 4. 前端：全局错误提示

在 App.tsx 中添加：
- 全局 `error` 状态，接收 WebSocket `onError` 回调
- 统一的错误提示条（右上角 toast 风格，自动消失）
- 降级提示：当后端返回 `degraded: true` 时显示 "⚠ 降级" 标识
- 网络断开时提示 "连接已断开，正在重连..."

### 5. 前后端：降级可视化

- AgentPanel 显示降级状态（`degraded: true` 时显示黄色警告）
- Editor 顶部显示降级提示条（"⚠ 部分功能以降级模式运行"）
- 导出页面显示降级详情（"LaTeX 未安装，已使用 Pandoc 降级导出"）

### 6. 测试
- 后端测试：`cd agent && source .venv/bin/activate && python -m pytest tests/ -q`（357 passed）
- 后端新增测试：test_global_exception_handler, test_degradation_endpoint
- 前端测试：`cd frontend && npm test`（132 passed）
- 前端新增测试：ErrorBoundary 渲染/错误捕获/重试

## 依赖
- 前置：无（独立任务，涉及 frontend/ + backend/）
- 与其他任务无冲突

## 验收标准
- [ ] 后端全局异常处理中间件返回结构化 JSON + request_id
- [ ] 后端 `GET /sessions/{id}/degradation` 端点返回降级记录
- [ ] 前端 ErrorBoundary 组件捕获渲染错误并显示重试按钮
- [ ] 前端 WebSocket 断连时显示重连提示
- [ ] 后端返回 `degraded: true` 时前端显示 "⚠ 降级" 标识
- [ ] 所有现有后端测试（357 passed）仍然通过
- [ ] 所有现有前端测试（132 passed）仍然通过
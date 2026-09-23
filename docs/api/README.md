# econpaper API 文档

> 版本：0.1.0 | 基础 URL：`http://localhost:8000`

econpaper 后端 API 基于 FastAPI 构建，提供论文生成全流程的 REST + WebSocket 接口。

## 目录

1. [快速开始](reference/01-quickstart.md)
2. [端点一览](reference/02-endpoints.md)
3. [端点详情](reference/03-endpoint-details.md)
4. [WebSocket 协议](reference/04-websocket.md)
5. [认证](reference/05-auth.md)
6. [OpenAPI 规范](reference/06-openapi.md)
7. [通用错误格式](reference/07-errors.md)

## 相关

- [openapi.json](openapi.json)：OpenAPI 3.1 规范，由 `make gen-api` 从后端生成，`make test` 会检查它有没有落后于代码。不要手改。
- [prewrite-confirm.md](prewrite-confirm.md)：写作前估计确认（PREWRITE-PAUSE）的接口与状态说明。
- 改了 `backend/routers/` 或 `backend/schemas/`：同一改动里更新对应的 `reference/` 分节文件，并运行 `make gen-api`。


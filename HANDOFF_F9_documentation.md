# Handoff: F9 - 生产化文档

## 目标
为 econpaper 项目生成生产化文档，包括 API 文档（OpenAPI 导出 + 使用说明）和用户手册，方便开发者和最终用户使用。

## 背景
- 后端 FastAPI 自动生成 OpenAPI schema（`/openapi.json`），但未导出为静态文档
- 前端 `frontend/openapi.json` 已存在（可能是旧副本）
- ADR 文档在 `docs/adr/` 目录下（7 个 ADR 文件）
- 无用户手册、无 API 文档站、无部署说明
- 项目 README.md 存在但内容较简略

## 具体改动

### 1. API 文档（面向开发者）

#### 1.1 导出 OpenAPI 规范
- 启动后端 → 访问 `http://localhost:8001/openapi.json` → 下载并保存到 `docs/api/openapi.json`
- 使用 `redoc-cli` 或 `swagger-ui` 构建静态 HTML 文档站
- 文档站输出到 `docs/api/index.html`

#### 1.2 API 概览文档
在 `docs/api/README.md` 中：
- 列出所有 11 个 router 及其端点
- 每个端点说明：方法、路径、请求体、响应体、错误码
- 认证方式（当前无认证，标注 "TBD: 用户体系实施后添加"）
- WebSocket 协议说明（消息类型、格式、时序）
- 示例 curl 命令

#### 1.3 端点清单
| Router | 端点 | 方法 | 说明 |
|--------|------|------|------|
| eda | /sessions/{id}/eda | GET | EDA 报告 |
| sessions | /sessions/{id} | GET | 会话状态 |
| ws | /sessions/{id}/stream | WS | 实时流 |
| outline | /sessions/{id}/outline | POST | 生成大纲 |
| chapter | /sessions/{id}/chapter | POST | 生成章节 |
| sample | /sessions/{id}/sample | POST | 样本筛选 |
| charls | /sessions/{id}/charls/detect | GET | CHARLS 检测 |
| charls | /sessions/{id}/charls/confirm | POST | CHARLS 确认 |
| code_export | /sessions/{id}/code | GET | 代码导出 |
| doc_export | /sessions/{id}/export | POST | 文档导出 |
| progress | /sessions/{id}/progress | GET | 进度查询 |
| review | /sessions/{id}/review | GET | 评审信息 |
| review | /sessions/{id}/review/decision | POST | 提交评审决策 |

### 2. 用户手册（面向最终用户）

在 `docs/user-guide.md` 中：
- 产品简介：econpaper 是什么？
- 快速开始：上传 CSV → 生成论文的 5 分钟教程
- 功能导览：
  - 三栏布局说明（左：大纲导航 / 中：编辑器 / 右：Agent 状态）
  - 数据上传与清洗（8 子步骤）
  - 研究设计（方向设定 + 变量映射）
  - 章节生成与 HITL 评审
  - 导出（PDF/DOCX/代码）
- 常见问题 FAQ
- 技术支持与反馈渠道

### 3. 部署文档

在 `docs/deployment.md` 中：
- 环境要求（Python 3.12+, Node 18+, PostgreSQL 16+）
- 开发环境启动（`make dev`）
- 生产环境部署（Docker 待实施后补充）
- 环境变量说明表
- 数据库配置（PostgreSQL 连接 + 迁移）
- 故障排查指南

### 4. README 更新

更新 `README.md`：
- 项目简介和经济学家定位
- 快速开始命令（`make install && make dev`）
- 核心功能亮点
- 技术栈概览
- 文档链接（指向 docs/ 目录）

### 5. 测试
- 确认 `make dev` 仍然正常工作
- 确认 API 文档站可访问
- 无需修改代码，纯文档任务

## 依赖
- 前置：无（独立任务，只涉及 docs/ 目录 + README.md）
- 不影响其他任务

## 验收标准
- [ ] `docs/api/openapi.json` 包含所有 11 个 router 的端点定义
- [ ] `docs/api/README.md` 包含完整 API 概览（端点表 + 示例 + WebSocket 协议）
- [ ] `docs/user-guide.md` 包含完整用户手册（快速开始 + 功能导览 + FAQ）
- [ ] `docs/deployment.md` 包含部署说明（环境要求 + 启动命令 + 配置表）
- [ ] `README.md` 更新为更专业的项目介绍
- [ ] 所有文档使用中文撰写
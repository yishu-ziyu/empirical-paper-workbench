# econpaper 部署文档

> 版本：0.1.0 | 更新时间：2026-07-31

## 环境要求

| 组件 | 最低版本 | 备注 |
|------|----------|------|
| Python | 3.12+ | 3.10+ 也可，但推荐 3.12 |
| Node.js | 18+ | 前端所需 |
| PostgreSQL | 16+ | 生产环境必须（开发可跳过） |
| latexmk | 最新版 | 可选，PDF 导出需要 |
| pandoc | 2.0+ | 可选，Word 导出需要 |

**上游依赖**（需与 econpaper 同级目录）：

```
../StatsPAI/          — 因果推断主库
../_refs/AERS-ref/    — prompt/skill 库（不 pip install）
../stata-code/        — Python → Stata/R/EViews 代码翻译引擎
```

## 快速开始（开发环境）

### 1. 克隆仓库并安装依赖

```bash
cd econpaper
make install
```

`make install` 等价于依次执行：

```bash
# 前端
cd frontend && npm install

# 后端
cd backend && python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pip install -e ../StatsPAI
pip install -e ../stata-code

# Agent
cd agent && python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动开发服务器

```bash
make dev
```

并发启动：
- **前端**：Vite dev server，`http://localhost:5173`
- **后端**：FastAPI uvicorn（reload 模式），`http://localhost:8000`

### 3. 验证

```bash
# 后端健康检查
curl http://localhost:8000/health
# 期望：{"status":"ok"}

# Agent graph 冒烟测试
make smoke-agent

# 全栈一键验证
make verify
```

## 单独启动

```bash
# 只启动前端
make dev-frontend

# 只启动后端
make dev-backend
```

## 生产环境部署

### Docker 部署

econpaper 提供完整的 Docker Compose 编排，一键启动 PostgreSQL + 后端 + 前端。

#### 前置条件

- **Docker Engine** 24+（含 `docker compose` 插件）
- **Docker Compose** v2.20+

#### 快速启动

```bash
# 1. 从模板创建环境变量文件并编辑
cp .env.docker .env
# 编辑 .env：至少设置 LLM_API_KEY 和 JWT_SECRET_KEY

# 2. 构建并启动所有服务
make docker-up
# 等价于：docker compose up -d --build

# 3. 验证
curl http://localhost/health
# 期望：{"status":"ok"}

# 4. 访问
# 前端：http://localhost
# API 文档：http://localhost/docs
```

#### 常用命令

```bash
# 查看日志
make docker-logs

# 查看容器状态
make docker-ps

# 停止服务
make docker-down

# 清理所有数据（含数据库卷）
make docker-clean
```

#### 服务架构

```
用户 → Nginx (80)
        ├── /api/*   → backend:8000 (FastAPI)
        ├── /ws/*    → backend:8000 (WebSocket)
        ├── /health  → backend:8000
        └── /*       → 前端静态文件
backend → postgres:5432
```

#### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `false` | 调试模式 |
| `CORS_ORIGINS` | `http://localhost` | 允许的跨域来源 |
| `UPLOAD_DIR` | `/app/uploads` | 上传文件存储目录（持久卷） |
| `MAX_UPLOAD_SIZE_MB` | `50` | 上传文件大小限制 |
| `CHECKPOINT_DB_URL` | `postgresql://econpaper:econpaper_pass@postgres:5432/econpaper` | LangGraph checkpoint 连接 |
| `DATABASE_URL` | `postgresql+asyncpg://econpaper:econpaper_pass@postgres:5432/econpaper` | 用户认证数据库连接 |
| `JWT_SECRET_KEY` | 需自行设置 | JWT 签名密钥（生产环境必须修改） |
| `LLM_API_KEY` | 需自行设置 | LLM API 密钥 |
| `POSTGRES_PASSWORD` | `econpaper_pass` | PostgreSQL 密码（生产环境必须修改） |

#### 生产环境注意事项

1. **修改默认密码**：编辑 `.env` 中的 `JWT_SECRET_KEY` 和 `POSTGRES_PASSWORD`
2. **配置 CORS**：`CORS_ORIGINS=https://你的域名.com`
3. **设置 LLM**：填入 `LLM_API_KEY`
4. **HTTPS**：建议在 Nginx 前加反向代理（如 Caddy / Traefik）自动管理 TLS
5. **备份**：`pgdata` 卷包含数据库，定期备份：
   ```bash
   docker run --rm -v econpaper-pgdata:/source -v /backup:/dest alpine tar czf /dest/pgdata-$(date +%Y%m%d).tar.gz -C /source .
   ```

### 环境变量配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG` | `false` | 调试模式（开启后显示详细错误） |
| `CORS_ORIGINS` | `http://localhost:5173` | 允许的跨域来源（逗号分隔） |
| `UPLOAD_DIR` | `./uploads` | 上传文件存储目录 |
| `MAX_UPLOAD_SIZE_MB` | `50` | 上传文件大小限制（MB） |
| `CHECKPOINT_DB_URL` | `postgresql://mahaoxuan@localhost:5432/econpaper` | PostgreSQL 连接字符串 |
| `LLM_PROVIDER` | `openai` | LLM 提供商 |
| `LLM_API_KEY` | `""` | LLM API 密钥 |
| `LLM_MODEL` | `gpt-4o-mini` | LLM 模型名称 |
| `HTTPX_TIMEOUT_SECONDS` | `30.0` | HTTP 客户端超时时间（秒） |

### 生产环境 CORS 配置

```bash
# 生产环境必须指定具体域名，禁止使用 *
export CORS_ORIGINS="https://econpaper.your-domain.com"
```

## 数据库配置

### PostgreSQL 设置

1. 安装 PostgreSQL 16+

```bash
# macOS
brew install postgresql@16
brew services start postgresql@16
```

2. 创建数据库和用户

```bash
createdb econpaper
createuser mahaoxuan
```

3. 配置连接字符串

```bash
# 使用默认连接（peer auth）
export CHECKPOINT_DB_URL="postgresql://mahaoxuan@localhost:5432/econpaper"

# 或使用密码认证
export CHECKPOINT_DB_URL="postgresql://user:password@localhost:5432/econpaper"
```

### 数据库迁移

当前版本使用 PostgreSQL 的 LangGraph PostgresSaver 进行 checkpoint 持久化。数据库 schema 由 LangGraph 自动管理，无需手动迁移。

## 故障排查

### 后端无法启动

**问题**：`uvicorn` 启动时报错

**检查**：
```bash
# 确认 Python 版本
python3 --version  # 需要 ≥ 3.10

# 确认依赖已安装
cd backend && . .venv/bin/activate && pip list

# 确认端口未占用
lsof -i :8000
```

**解决**：重新安装依赖
```bash
make install-backend
```

### 前端无法启动

**问题**：`npm run dev` 报错

**检查**：
```bash
# 确认 Node 版本
node --version  # 需要 ≥ 18

# 确认依赖已安装
ls frontend/node_modules
```

**解决**：
```bash
make install-frontend
```

### 数据库连接失败

**问题**：启动后端时 PostgreSQL 连接错误

**检查**：
```bash
# 确认 PostgreSQL 正在运行
brew services list | grep postgresql

# 确认数据库存在
psql -l | grep econpaper

# 测试连接
psql -d econpaper
```

**解决**：
```bash
# 启动 PostgreSQL
brew services start postgresql@16

# 创建数据库
createdb econpaper
```

### PDF 导出失败

**问题**：导出 PDF 返回 503

**解决**：
```bash
# 安装 latexmk
brew install latexmk

# 确认 LaTeX 发行版已安装
which latexmk
```

### Word 导出失败

**问题**：导出 docx 返回 503

**解决**：
```bash
# 安装 pandoc
brew install pandoc

# 确认安装
which pandoc
```

### LLM 调用失败

**问题**：章节生成时 LLM 返回错误

**检查**：
```bash
# 确认 LLM_API_KEY 已设置
echo $LLM_API_KEY

# 确认网络连接正常
curl https://api.openai.com/v1/models
```

## 常用命令

| 命令 | 作用 |
|------|------|
| `make dev` | 并发起 frontend + backend |
| `make install` | 装齐所有依赖 |
| `make verify` | 三件套冒烟检查 |
| `make smoke-agent` | Agent graph 可 import 验证 |
| `make health` | 后端 /health 端点检查 |
| `make test` | 运行测试套件 |
| `make clean` | 清空依赖和缓存 |
| `make gen-api` | 导出 OpenAPI schema 并生成前端类型 |

## 目录结构

```
econpaper/
├── frontend/      # Vite + React 18 前端应用
├── backend/       # FastAPI + uvicorn 后端服务
├── agent/         # LangGraph graph 定义 + 节点实现
├── docs/          # 文档（spec、ADR、API 文档、用户手册、部署文档）
├── Makefile       # 开发命令入口
├── README.md      # 项目简介
├── conftest.py    # 全局测试配置
└── pytest.ini     # pytest 配置
```